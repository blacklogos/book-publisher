#!/usr/bin/env python3
"""Build a designed PDF + EPUB from a book-publisher Markdown manuscript.

Pipeline:
  markdown --(pandoc + template.pdf.html5 + theme pdf.css)--> html --(weasyprint)--> pdf
  markdown --(pandoc + theme epub.css)--> epub, cover image rasterized from PDF p.1

Usage:
  scripts/build_book.py manuscript.md [--out dist] [--formats pdf,epub] [--theme boardroom]

`template.pdf.html5` (cover/front-matter/TOC shell) is shared across themes;
only assets/themes/<name>/{pdf.css,epub.css} change. See references/themes.md
for the list and how to add a new one.

Only stdlib is used here; PDF rasterization (for the epub cover + QA preview)
is delegated to `uv run --with pypdfium2 --with pillow` so this script has no
install-time dependency of its own beyond pandoc + weasyprint on PATH.
"""
import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"
THEMES = ASSETS / "themes"


def run(cmd, **kw):
    print("$", " ".join(str(c) for c in cmd))
    env = kw.pop("env", None)
    subprocess.run(cmd, check=True, env=env, **kw)


def weasyprint_env():
    """WeasyPrint on macOS/Homebrew needs libgobject etc. on the dylib path
    (Homebrew's `libgobject-2.0.0.dylib` isn't found by WeasyPrint's default
    search names). No-op on Linux, where apt/dnf installs land on the
    standard loader path."""
    import os
    env = os.environ.copy()
    if platform.system() == "Darwin":
        brew_lib = shutil.which("brew")
        prefix = "/opt/homebrew" if brew_lib else "/usr/local"
        env["DYLD_LIBRARY_PATH"] = prefix + "/lib:" + env.get("DYLD_LIBRARY_PATH", "")
    return env


def check_deps():
    missing = [t for t in ("pandoc", "weasyprint") if not shutil.which(t)]
    if missing:
        sys.exit(
            f"Missing tools: {', '.join(missing)}. Run scripts/check_deps.py "
            "for install commands, then retry."
        )


def theme_dir(theme: str) -> Path:
    path = THEMES / theme
    if not (path / "pdf.css").exists():
        available = ", ".join(sorted(p.name for p in THEMES.iterdir() if p.is_dir()))
        sys.exit(f"Unknown theme '{theme}'. Available: {available}")
    return path


def build_pdf(md: Path, out: Path, theme: Path, extra_css: Path | None, facing_pages: bool) -> Path:
    html_tmp = out / (md.stem + ".pdf-source.html")
    pdf_out = out / (md.stem + ".pdf")
    cmd = [
        "pandoc", str(md),
        "-f", "markdown+task_lists+fenced_divs+yaml_metadata_block+raw_html",
        "-t", "html5",
        "--template", str(ASSETS / "template.pdf.html5"),
        "--toc", "--toc-depth=3",
        "-V", f"pdf-css={theme / 'pdf.css'}",
        "-o", str(html_tmp),
    ]
    if facing_pages:
        cmd += ["-V", "facing-pages=true"]
        facing_css = theme / "facing-pages.css"
        if not facing_css.exists():
            sys.exit(f"--facing-pages requested but {facing_css} doesn't exist for this theme.")
        cmd += ["--css", str(facing_css)]
    theme_fonts = theme / "fonts.css"
    if theme_fonts.exists():
        # auto-opt-in once scripts/fetch_fonts.py has been run for this
        # theme (currently only boardroom has one) — no --extra-css needed.
        # Absent, the theme's pdf.css falls back to its system-font stack.
        cmd += ["--css", str(theme_fonts)]
    if extra_css:
        cmd += ["--css", str(extra_css)]
    run(cmd)
    run(["weasyprint", str(html_tmp), str(pdf_out)], env=weasyprint_env())
    html_tmp.unlink()
    return pdf_out


def build_epub(md: Path, out: Path, theme: Path, cover: Path | None, extra_css: Path | None) -> Path:
    epub_out = out / (md.stem + ".epub")
    cmd = [
        "pandoc", str(md),
        "-f", "markdown+task_lists+fenced_divs+yaml_metadata_block+raw_html",
        "-t", "epub3",
        "--css", str(theme / "epub.css"),
        "-o", str(epub_out),
    ]
    theme_fonts = theme / "fonts.css"
    if theme_fonts.exists():
        cmd += ["--css", str(theme_fonts)]  # see build_pdf
    if extra_css:
        cmd += ["--css", str(extra_css)]
    if cover and cover.exists():
        cmd += ["--epub-cover-image", str(cover)]
    run(cmd)
    return epub_out


def make_cover_and_preview(pdf: Path, out: Path, pages: int = 3):
    """Rasterize page 1 (epub cover) and the first N pages (QA preview)."""
    preview_dir = out / "preview"
    preview_dir.mkdir(exist_ok=True)
    script = f"""
import pypdfium2 as pdfium
pdf = pdfium.PdfDocument(r"{pdf}")
n = min({pages}, len(pdf))
for i in range(n):
    bitmap = pdf[i].render(scale=150/72)
    img = bitmap.to_pil()
    path = r"{preview_dir}" + f"/page-{{i+1:02d}}.png"
    img.save(path)
    if i == 0:
        img.save(r"{out}/cover.png")
print(f"Rendered {{n}} preview pages")
"""
    run(["uv", "run", "--with", "pypdfium2", "--with", "pillow", "python3", "-c", script])
    return out / "cover.png"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manuscript", type=Path)
    ap.add_argument("--out", type=Path, default=Path("dist"))
    ap.add_argument("--formats", default="pdf,epub")
    ap.add_argument("--theme", default="boardroom", help="assets/themes/<name>/ to use")
    ap.add_argument(
        "--extra-css", type=Path, default=None,
        help="Extra stylesheet layered on top, e.g. assets/fonts.css from fetch_fonts.py",
    )
    ap.add_argument(
        "--facing-pages", action="store_true",
        help="Mirror margins/header-footer for odd(right)/even(left) pages and start "
             "chapters on a recto page — for a book meant to be printed and bound "
             "double-sided. Off by default: most PDFs from this skill are read on a "
             "screen one page at a time, where a fixed single-sided layout is correct. "
             "PDF only, no effect on --formats epub (reflowable, no facing pages).",
    )
    args = ap.parse_args()

    check_deps()
    theme = theme_dir(args.theme)
    args.out.mkdir(parents=True, exist_ok=True)
    formats = set(args.formats.split(","))

    pdf_path = None
    if "pdf" in formats:
        pdf_path = build_pdf(args.manuscript, args.out, theme, args.extra_css, args.facing_pages)
        print(f"PDF  -> {pdf_path}")

    cover = None
    if pdf_path:
        cover = make_cover_and_preview(pdf_path, args.out)
        print(f"QA preview PNGs -> {args.out / 'preview'}")

    if "epub" in formats:
        epub_path = build_epub(args.manuscript, args.out, theme, cover, args.extra_css)
        print(f"EPUB -> {epub_path}")


if __name__ == "__main__":
    main()
