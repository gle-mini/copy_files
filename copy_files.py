#!/usr/bin/env python3
import os
import sys
import fnmatch
import shutil

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
}

GLOB_NAMES = {
    "*.fish",
    "*.iso",
    "*.png",
    "*.o",
    "*.d",
    "*.py",
    "*.log",
    "*.bin",
    "*out*",
    "*uml",
    "*clang*",
    "*flowchart*",
}

EXCLUDE_DIRS = {
    ".git", ".github", "objs", "venv", "build",
    "images", "iso", "migrate", "sounds",
}

REL_PATH_PREFIXES = {
    os.path.join("srcs", "database"),
}


def should_exclude(full_path, rel_path):
    base = os.path.basename(full_path)
    # exact filename
    if base in EXACT_NAMES:
        return True
    # glob patterns on basename
    for pat in GLOB_NAMES:
        if fnmatch.fnmatch(base, pat):
            return True
    # excluded sub‑directory
    parts = rel_path.split(os.sep)
    if any(p in EXCLUDE_DIRS for p in parts):
        return True
    # specific relative‑path prefixes
    for prefix in REL_PATH_PREFIXES:
        if rel_path.startswith(prefix + os.sep):
            return True
    return False


def dump_tree(folder_path, output_path="output.txt"):
    folder_path = os.path.abspath(folder_path)
    cwd = os.getcwd()

    # remove old output
    if os.path.exists(output_path):
        os.remove(output_path)

    with open(output_path, "wb") as out:
        for root, dirs, files in os.walk(folder_path, topdown=True):
            # prune unwanted directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            rel_root = os.path.relpath(root, folder_path)
            # skip entire srcs/database subtree
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

                # header
                header = f"### {rel} ###\n".encode("utf-8")
                out.write(header)

                # raw copy
                try:
                    with open(full, "rb") as src:
                        shutil.copyfileobj(src, out, 16 * 1024)
                except Exception as e:
                    msg = f"\n<!-- could not read file: {e} -->\n".encode("utf-8")
                    out.write(msg)

                out.write(b"\n")  # separate files

    print(f"All files have been copied to {output_path}.")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <folder_path>")
        sys.exit(1)

    folder = sys.argv[1]
    if not os.path.isdir(folder):
        print(f"Error: The folder '{folder}' does not exist.")
        sys.exit(1)

    dump_tree(folder)


if __name__ == "__main__":
    main()

