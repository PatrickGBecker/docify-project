# docify_tool/scanner.py

import os
import json

# Roughly 3–4 chars per token; 350k chars ~ < 120k tokens -> safe margin
MAX_TOTAL_CHARS = 350_000
MAX_FILE_CHARS = 8_000  # max chars per file to include in context


def read_notebook_source(file_path):
    """Read Jupyter notebook and return concatenated code + markdown cells."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        code_cells = "\n".join(
            "".join(cell["source"])
            for cell in nb.get("cells", [])
            if cell.get("cell_type") == "code"
        )
        markdown_cells = "\n".join(
            "".join(cell["source"])
            for cell in nb.get("cells", [])
            if cell.get("cell_type") == "markdown"
        )
        return code_cells + "\n" + markdown_cells
    except Exception as e:
        return f"[Error reading notebook: {e}]"


def get_project_context(root_dir, ignore_dirs=None, ignore_exts=None):
    """
    Walks through a directory, gets file structure and truncated content,
    returns a formatted string including notes about ignored files/directories.
    """
    ignore_dirs = set(ignore_dirs or [])
    ignore_exts = set(ignore_exts or [])
    full_context: list[str] = []
    total_chars = 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Track ignored dirs
        ignored_dirs_in_path = [d for d in dirnames if d in ignore_dirs]
        for d in ignored_dirs_in_path:
            line = f"--- Ignored directory: {os.path.join(dirpath, d)} ---\n"
            full_context.append(line)
            total_chars += len(line)

        # Prevent walking into ignored dirs
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]

        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(file_path, root_dir)

            # Track ignored files
            if any(filename.endswith(ext) for ext in ignore_exts):
                line = f"--- Ignored file: {relative_path} ---\n"
                full_context.append(line)
                total_chars += len(line)
                continue

            header = f"--- File: {relative_path} ---\n"
            if total_chars + len(header) > MAX_TOTAL_CHARS:
                full_context.append(
                    "\n[...project context truncated: remaining files omitted...]\n"
                )
                return "".join(full_context)

            full_context.append(header)
            total_chars += len(header)

            try:
                if filename.endswith(".ipynb"):
                    content = read_notebook_source(file_path)
                else:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                        content = file.read()
            except Exception as e:
                content = f"[Error reading file: {e}]"

            # Per-file truncation
            if len(content) > MAX_FILE_CHARS:
                content = (
                    content[:MAX_FILE_CHARS]
                    + "\n\n[...file truncated for Docify-AI context...]\n"
                )

            # Check overall cap
            if total_chars + len(content) > MAX_TOTAL_CHARS:
                remaining = MAX_TOTAL_CHARS - total_chars
                if remaining > 0:
                    full_context.append(content[:remaining])
                full_context.append(
                    "\n\n[...project context truncated: size limit reached...]\n"
                )
                return "".join(full_context)

            full_context.append(content)
            full_context.append("\n\n")
            total_chars += len(content) + 2  # +2 for the added "\n\n"

    return "".join(full_context)

    