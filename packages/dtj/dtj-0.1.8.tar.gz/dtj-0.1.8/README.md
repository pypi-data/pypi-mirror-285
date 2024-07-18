
# DTJ (Directory-to-JSON)

## Overview
DTJ (Directory-to-JSON) is a Python command-line tool, particularly useful for quickly generating and sharing representations of directory structures and their contents in a structured and token-efficient manner, making it ideal for interactions with language models like ChatGPT.

## Example output
```bash
dtj
```

```json
{
  "my_project": {
    "__init__.py": "",
    "main.py": "# Main application file\nimport app\n\napp.run()",
    "app.py": "# App module\n\ndef run():\n    print('Running the app')",
    "utils": {
      "helper.py": "# Utility functions\n\ndef helper():\n    return 'Helper function'"
    }
  }
}
```

### Features
- Convert directory contents to JSON format.
- Include or exclude files using patterns (supports fnmatch style, e.g., `*.py`, `data*`).
- Recursive directory parsing.
- Options for output: printing to console, saving to a file, or copying to the clipboard.

### Updates
- new JSON format **reduces token usage ~30%**

## Installation

```bash
pip install dtj
```

## Usage

Run DTJ from the command line with the following options:

```bash
dtj <target-directory> [options]
```

If no target directory is specified, DTJ will default to the current working directory.

Options:
- `-t` or `--target-file`: Target a single file. This option is mutually exclusive with `-i`, `-e`, and `-r`.
- `-i` or `--include`: Patterns to include files. Enclose patterns in quotes to avoid shell expansion (e.g., `'*.py'`, `'data*'`).
- `-e` or `--exclude`: Patterns to exclude files. Enclose patterns in quotes to avoid shell expansion (e.g., `'*.xml'`, `'temp*'`).
- `-o` or `--output-file`: Set the output JSON file name.
- `-r` or `--recursive`: Enable recursive search in directories. Not valid when targeting a single file.
- `-p` or `--print`: Print the output using rich formatting.
- `-c` or `--clipboard`: Copy the output to the clipboard.

## Example
simple
```bash
dtj
```

Generates an output.json with the content

advanced
```bash
dtj myfolder -i '*.py' '*.html' -o output.json -r
```

This command will parse all `.py` and `.html` files in `myfolder` recursively and save the JSON output to `output.json`.

## Using it alongside [gptwc](https://github.com/lwneal/gptwc)

```bash
dtj | gptwc
```
outputs the token count
`1337`

## Authors

- Adrian Galilea - *Initial work*

## Acknowledgments

- Hat tip to ChatGPT for assistance with project setup and documentation.
