import argparse
import os
import sys
import json
import logging

import pyperclip
from rich import print as rich_print

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dtj.file_utils import (
        generate_file_structure,
        get_gitignore_spec,
        read_file_contents,
    )
except ImportError:
    from file_utils import (
        generate_file_structure,
        get_gitignore_spec,
        read_file_contents,
    )


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Generate a JSON file from a directory's contents."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=os.getcwd(),
        type=str,
        help="Target directory. Defaults to the current directory if not specified.",
    )
    parser.add_argument(
        "-i",
        "--include",
        type=str,
        nargs="+",
        help="File patterns to include (e.g., *.py, *.html).",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        type=str,
        nargs="+",
        help="File patterns to exclude (e.g., *.xml).",
    )
    parser.add_argument("-o", "--output-file", type=str, help="Output JSON file name.")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively search in directories.",
    )
    parser.add_argument(
        "-p", "--print", action="store_true", help="Print the output using rich."
    )
    parser.add_argument(
        "-c",
        "--clipboard",
        action="store_true",
        help="Copy the output to the clipboard.",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and directories.",
    )
    parser.add_argument(
        "--include-global-gitignore",
        action="store_true",
        help="Include the global .gitignore file.",
    )
    parser.add_argument(
        "--exclude-local-gitignore",
        action="store_true",
        help="Exclude the local .gitignore file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run to see which files would match without generating output.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.include and args.exclude:
        rich_print(
            "[bold red][Error][/bold red] -i/--include and -e/--exclude cannot be used together. Please specify only one."
        )
        return

    target_dir = os.path.abspath(args.target)
    logging.debug(f"Target directory: {target_dir}")
    logging.debug(f"Current working directory: {os.getcwd()}")

    gitignore_spec = get_gitignore_spec(
        target_dir, args.include_global_gitignore, args.exclude_local_gitignore
    )

    file_structure = generate_file_structure(
        target_dir,
        args.include,
        args.exclude,
        args.recursive,
        args.include_hidden,
        gitignore_spec,
    )

    if args.dry_run:
        rich_print(f"[bold cyan]Dry run: The following files would match:[/bold cyan]")
        for path, files in file_structure.items():
            for file in files:
                rich_print(f"{os.path.join(path, file)}")
        return

    data = read_file_contents(file_structure, target_dir)
    json_data = json.dumps(data, indent=4)

    if args.clipboard:
        try:
            pyperclip.copy(json_data)
            rich_print(
                "[bold green]Output successfully copied to clipboard.[/bold green]"
            )
        except pyperclip.PyperclipException as e:
            rich_print(
                f"[bold yellow]Warning: Could not copy to clipboard. {str(e)}[/bold yellow]"
            )
            rich_print("[bold yellow]Printing to console instead:[/bold yellow]")
            rich_print(json_data)
    elif args.output_file:
        with open(args.output_file, "w") as file:
            file.write(json_data)
        rich_print(f"[bold green]Output saved to {args.output_file}[/bold green]")
    elif args.print:
        rich_print(json_data)
    else:
        print(json_data)


if __name__ == "__main__":
    main()
