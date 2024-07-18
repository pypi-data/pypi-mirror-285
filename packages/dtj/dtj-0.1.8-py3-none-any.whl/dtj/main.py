import json
import os
import argparse
from rich import print as rich_print
import pyperclip
import fnmatch

def list_files(directory, include_patterns, exclude_patterns, recursive):
    """Recursively list files in the directory with specified filename glob patterns."""
    file_structure = {}

    for root, dirs, files in os.walk(directory):
        if not recursive:
            dirs[:] = []

        relative_path = os.path.relpath(root, directory)
        file_list = []

        for file in files:
            if include_patterns and not any(fnmatch.fnmatch(file, pat) for pat in include_patterns):
                continue
            if exclude_patterns and any(fnmatch.fnmatch(file, pat) for pat in exclude_patterns):
                continue
            file_list.append(os.path.join(root, file))

        if file_list:
            if relative_path == '.':
                relative_path = os.path.basename(directory)

            file_structure[relative_path] = file_list

    return file_structure

def process_single_file(file_path):
    """Process a single file and return its content in JSON format."""
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return {"filename": os.path.basename(file_path), "content": content}
    except Exception as e:
        rich_print(f"[bold yellow]Warning:[/bold yellow] Could not read file [bold cyan]{file_path}[/bold cyan]: [bold red]{e}[/bold red]")
        return None

def read_file_contents(file_structure, directory):
    output = {os.path.basename(directory): {}}
    
    for path, files in file_structure.items():
        current_dir = output[os.path.basename(directory)]

        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                nested_path = os.path.relpath(file_path, directory).replace(os.sep, '/')
                dirs = nested_path.split('/')[:-1]
                file_name = os.path.basename(file_path)

                target_dir = current_dir
                for d in dirs:
                    target_dir = target_dir.setdefault(d, {})

                target_dir[file_name] = content
            except Exception as e:
                rich_print(f"[bold yellow]Warning:[/bold yellow] Could not read file [bold cyan]{file_path}[/bold cyan]: [bold red]{e}[/bold red]")

    return output


def main():
    parser = argparse.ArgumentParser(description="Process and print the contents of a directory or a single file in JSON format.")
    parser.add_argument(
        'target', 
        nargs='?', 
        default=os.getcwd(), 
        type=str, 
        help="Target directory. Defaults to the current directory if not specified. Outputs to the terminal unless otherwise specified."
    )
    parser.add_argument('-t', '--target-file', type=str, help="Target a single file. This option outputs the content of the file in JSON format to the terminal.")
    parser.add_argument('-i', '--include', type=str, nargs='+', help="Include patterns for files. Use fnmatch-style patterns like '*.py', 'data*', '?file.txt'.")
    parser.add_argument('-e', '--exclude', type=str, nargs='+', help="Exclude patterns for files. Use fnmatch-style patterns like '*.xml', 'temp*'.")
    parser.add_argument('-o', '--output-file', type=str, help="Specify an output file for the JSON data. If not provided, data will be printed to the terminal.")
    parser.add_argument('-r', '--recursive', action='store_true', help="Enable recursive search in directories. Not applicable with --target-file.")
    parser.add_argument('-c', '--clipboard', action='store_true', help="Copy the JSON output to the clipboard.")

    args = parser.parse_args()

    if args.target_file:
        data = process_single_file(args.target_file)
        if data is None:
            return
    else:
        if args.include and args.exclude:
            print("[Error] -i/--include and -e/--exclude cannot be used together. Please specify only one.")
            return
        file_structure = list_files(args.target, args.include, args.exclude, args.recursive)
        data = read_file_contents(file_structure, args.target)

    json_data = json.dumps(data, indent=4)

    if args.clipboard:
        pyperclip.copy(json_data)
        print("[Output has been copied to the clipboard.]")
    elif args.output_file:
        with open(args.output_file, 'w') as file:
            file.write(json_data)
    else:
        print(json_data)

if __name__ == "__main__":
    main()