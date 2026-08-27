#!/usr/bin/env python3
"""Verify/report the two hard dependencies for book-publisher: pandoc + weasyprint.
Run before scripts/build_book.py on a new host (fresh Codex/agy sandbox, new machine)."""
import platform
import shutil
import sys

OK = "\033[32mok\033[0m"
MISSING = "\033[31mmissing\033[0m"


def check(name, hint):
    found = shutil.which(name) is not None
    print(f"  {name:12s} {OK if found else MISSING}")
    if not found:
        print(f"    -> {hint}")
    return found


def main():
    system = platform.system()
    print(f"Host: {system}")
    pandoc_ok = check("pandoc", "brew install pandoc   (Linux: apt/dnf install pandoc)")
    weasy_ok = check("weasyprint", "uv tool install weasyprint")

    if system == "Darwin":
        print(
            "  macOS note: WeasyPrint needs Homebrew's pango/cairo/gdk-pixbuf/glib.\n"
            "    If `weasyprint` errors with 'cannot load library libgobject-2.0-0',\n"
            "    export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH\n"
            "    (or /usr/local/lib on Intel Macs). scripts/build_book.py sets this\n"
            "    automatically; only needed if calling `weasyprint` directly."
        )
    elif system == "Linux":
        print(
            "  Linux note: apt install weasyprint-deps via\n"
            "    sudo apt install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0\n"
            "    (most distros already ship these for other GTK-based tools)."
        )

    if not (pandoc_ok and weasy_ok):
        sys.exit(1)
    print("All dependencies present.")


if __name__ == "__main__":
    main()
