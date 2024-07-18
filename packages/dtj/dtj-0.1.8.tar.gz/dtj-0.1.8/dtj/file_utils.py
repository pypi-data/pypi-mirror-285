import fnmatch
import os
import logging
from typing import Dict, List, Optional

import pathspec


def get_gitignore_spec(
    directory: str, include_global_gitignore: bool, exclude_local_gitignore: bool
) -> pathspec.PathSpec:
    gitignore_file = os.path.join(directory, ".gitignore")
    global_gitignore = os.path.expanduser("~/.gitignore")

    spec_lines = []

    if include_global_gitignore and os.path.exists(global_gitignore):
        with open(global_gitignore, "r") as f:
            lines = f.readlines()
            spec_lines.extend(lines)
        logging.debug(f"Loaded {len(lines)} lines from global .gitignore")

    if not exclude_local_gitignore and os.path.exists(gitignore_file):
        with open(gitignore_file, "r") as f:
            lines = f.readlines()
            spec_lines.extend(lines)
        logging.debug(f"Loaded {len(lines)} lines from local .gitignore")

    if not spec_lines:
        logging.debug("No gitignore lines loaded.")

    return pathspec.PathSpec.from_lines("gitwildmatch", spec_lines)


def is_binary_extension(file_name: str) -> bool:
    """Check if a file likely has a binary extension."""
    binary_extensions = {
        ".exe",
        ".dll",
        ".so",
        ".bin",
        ".dat",
        ".class",
        ".pyc",
        ".pyo",
        ".o",
        ".a",
        ".lib",
        ".img",
        ".iso",
        ".tar",
        ".gz",
        ".zip",
        ".rar",
        ".7z",
        ".bz2",
        ".xz",
        ".mp3",
        ".mp4",
        ".avi",
        ".mov",
        ".flv",
        ".mkv",
        ".wav",
        ".flac",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".ico",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".iso",
        ".dmg",
        ".pkg",
        ".deb",
        ".rpm",
        ".msi",
        ".apk",
        ".ipa",
    }
    return any(file_name.lower().endswith(ext) for ext in binary_extensions)


def should_include_file(
    file_path: str,
    gitignore_spec: pathspec.PathSpec,
    include_hidden: bool,
    include_patterns: Optional[List[str]],
    exclude_patterns: Optional[List[str]],
) -> bool:
    file_name = os.path.basename(file_path)

    if not include_hidden and file_name.startswith("."):
        logging.debug(f"Excluding hidden file: {file_path}")
        return False

    if gitignore_spec.match_file(file_path):
        logging.debug(f"Excluding file based on gitignore: {file_path}")
        return False

    if is_binary_extension(file_name):
        logging.debug(f"Excluding binary file: {file_path}")
        return False

    if include_patterns and not any(
        fnmatch.fnmatch(file_name, pat) for pat in include_patterns
    ):
        logging.debug(f"File {file_path} does not match include patterns")
        return False

    if exclude_patterns and any(
        fnmatch.fnmatch(file_name, pat) for pat in exclude_patterns
    ):
        logging.debug(f"File {file_path} matches exclude patterns")
        return False

    logging.debug(f"Including file: {file_path}")
    return True


def generate_file_structure(
    directory: str,
    include_patterns: Optional[List[str]],
    exclude_patterns: Optional[List[str]],
    recursive: bool,
    include_hidden: bool,
    gitignore_spec: pathspec.PathSpec,
) -> Dict[str, List[str]]:
    file_structure = {}

    for root, dirs, files in os.walk(directory):
        # Apply gitignore filtering to directories
        if not include_hidden:
            dirs[:] = [d for d in dirs if not d.startswith(".")]

        dirs[:] = [
            d
            for d in dirs
            if not gitignore_spec.match_file(
                os.path.relpath(os.path.join(root, d), directory)
            )
        ]

        if not recursive and root != directory:
            break

        relative_path = os.path.relpath(root, directory)
        file_list = []

        for file in files:
            file_path = os.path.join(root, file)
            rel_file_path = os.path.relpath(file_path, directory)

            if should_include_file(
                rel_file_path,
                gitignore_spec,
                include_hidden,
                include_patterns,
                exclude_patterns,
            ):
                file_list.append(rel_file_path)

        if file_list:
            if relative_path == ".":
                relative_path = ""  # Use empty string to denote the root directory
            file_structure[relative_path] = file_list
            logging.debug(
                f"Added files from {relative_path if relative_path else 'root'}: {file_list}"
            )

    return file_structure


def read_file_contents(
    file_structure: Dict[str, List[str]], directory: str
) -> Dict[str, Dict]:
    output = {os.path.basename(directory): {}}

    for path, files in file_structure.items():
        current_dir = output[os.path.basename(directory)]

        for file_path in files:
            full_file_path = os.path.join(directory, file_path)
            try:
                with open(full_file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                nested_path = os.path.relpath(file_path, directory).replace(os.sep, "/")
                dirs = nested_path.split("/")[:-1]
                file_name = os.path.basename(full_file_path)

                target_dir = current_dir
                for d in dirs:
                    target_dir = target_dir.setdefault(d, {})

                target_dir[file_name] = content
                logging.debug(f"Read file: {full_file_path}")
            except Exception as e:
                logging.warning(f"Warning: Could not read file {full_file_path}: {e}")

    return output
