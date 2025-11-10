# docify_tool/cli.py
import argparse
from docify_tool.generators.readme import generate_readme

def main():
    p = argparse.ArgumentParser("docify")
    p.add_argument("--path", required=True, help="Project path to analyze")
    p.add_argument("--output", help="Where to write README.md")
    p.add_argument("--client", help="openai/gemini", default=None)
    p.add_argument("--ignore-dirs", nargs="*", default=[])
    p.add_argument("--ignore-exts", nargs="*", default=[])
    # No --template flag; we always use the built-in default template.

    args = p.parse_args()
    generate_readme(
        path=args.path,
        output=args.output,
        client=args.client,
        ignore_dirs=args.ignore_dirs,
        ignore_exts=args.ignore_exts,
    )

if __name__ == "__main__":
    main()
