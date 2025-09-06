#!/usr/bin/env python3
import os
import sys
import fnmatch
import shutil
import argparse


EXACT_NAMES = {
    "prompt",
    "libft_malloc_x86_64.so",
    "xml-prompt",
    "README.md",
    "copy_content.fish",
    "ftree_tokens.py",
    "check_multiboot.py",
    "output.txt",
    "test_malloc",
    "test_free",
    "test_threads",
    ".gdbinit",
    "save",
    ".gitignore",
    "LICENSE",
}

GLOB_NAMES = {
    "*.fish",
    "*.iso",
    "*.png",
    "*.o",
    "*.d",
    "*.log",
    "*.bin",
    "*out*",
    "*uml",
    "*clang*",
    "*flowchart*",
}

EXCLUDE_DIRS = {
    ".git", ".github", "objs", "venv", "build",
    "images", "iso", "migrate", "sounds", ".zig-cache", "zig-out",
}

REL_PATH_PREFIXES = {
    os.path.join("srcs", "database"),
}


def should_exclude(full_path, rel_path):
    base = os.path.basename(full_path)
    if base in EXACT_NAMES:
        return True
    for pat in GLOB_NAMES:
        if fnmatch.fnmatch(base, pat):
            return True
    parts = rel_path.split(os.sep)
    if any(p in EXCLUDE_DIRS for p in parts):
        return True
    for prefix in REL_PATH_PREFIXES:
        if rel_path.startswith(prefix + os.sep):
            return True
    return False


def dump_tree(folder_path, output_path="output.txt"):
    folder_path = os.path.abspath(folder_path)
    cwd = os.getcwd()

    if os.path.exists(output_path):
        os.remove(output_path)

    with open(output_path, "wb") as out:
        for root, dirs, files in os.walk(folder_path, topdown=True):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            rel_root = os.path.relpath(root, folder_path)
            if rel_root in REL_PATH_PREFIXES or any(
                rel_root.startswith(p + os.sep) for p in REL_PATH_PREFIXES
            ):
                dirs[:] = []
                continue

            for fname in sorted(files):
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, cwd)
                if not rel.startswith(os.curdir + os.sep):
                    rel = os.curdir + os.sep + rel

                if should_exclude(full, os.path.relpath(full, folder_path)):
                    continue

                header = f"### {rel} ###\n".encode("utf-8")
                out.write(header)

                try:
                    with open(full, "rb") as src:
                        shutil.copyfileobj(src, out, 16 * 1024)
                except Exception as e:
                    msg = f"\n<!-- could not read file: {e} -->\n".encode("utf-8")
                    out.write(msg)

                out.write(b"\n")

    print(f"All files have been copied to {output_path}.")


def main():
    parser = argparse.ArgumentParser(
        description="Recursively dump all files under a folder into a single output file."
    )
    # Manual usage check so missing folder arg exits with code 1 and prints Usage: to stdout
    if len(sys.argv) < 2:
        prog = os.path.basename(sys.argv[0])
        print(f"Usage: {prog} [-o OUTPUT] folder")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Recursively dump all files under a folder into a single output file."
    )
    parser.add_argument(
        "folder",
        help="Path to the folder whose files you want to copy"
    )
    parser.add_argument(
        "-o", "--output",
        default="output.txt",
        help="Output file path (default: output.txt)"
    )
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print(f"Error: The folder '{args.folder}' does not exist.")
        sys.exit(1)

    dump_tree(args.folder, args.output)


if __name__ == "__main__":
    main()
