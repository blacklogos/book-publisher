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
        # --wrap=none: pandoc's default 72-column wrapping also applies to
        # the template's inline <style>, so a running-title longer than
        # ~60 chars got a raw newline inside its CSS string. An unescaped
        # newline ends the string as a "bad string" token, which dropped
        # that @top-right rule *and* mangled the @bottom-left/@bottom-right
        # declarations after it — no running head, brand or folio on any
        # page, silently. Found on a Vietnamese title in 2026-09.
        "--wrap=none",
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
    dedupe_toc_parts(html_tmp)
    run(["weasyprint", str(html_tmp), str(pdf_out)], env=weasyprint_env())
    html_tmp.unlink()
    return pdf_out


def dedupe_toc_parts(html_path: Path) -> None:
    """Merge consecutive top-level TOC entries with identical link text.

    content-model.md requires the `# Part` heading to be repeated before
    every `## Chapter` (only h1 breaks the page), so pandoc's --toc lists
    "Part II" once per chapter. A printed contents page shows each Part
    once with its chapters nested under it; this folds the repeats and
    moves their chapter <li>s under the first occurrence. Pandoc's nav
    fragment is well-formed XHTML, so a strict XML parse is safe."""
    import re
    import xml.etree.ElementTree as ET
    html = html_path.read_text(encoding="utf-8")
    m = re.search(r'(<nav id="TOC"[^>]*>)(.*?)(</nav>)', html, flags=re.S)
    if not m:
        return
    try:
        root = ET.fromstring("<root>" + m.group(2) + "</root>")
    except ET.ParseError:
        return  # leave the TOC untouched rather than risk a broken build
    top = root.find("ul")
    if top is None:
        return
    merged, prev_text, prev_li = [], None, None
    for li in list(top):
        a = li.find("a")
        text = "".join(a.itertext()).strip() if a is not None else None
        sub = li.find("ul")
        if text is not None and text == prev_text and prev_li is not None:
            target = prev_li.find("ul")
            if target is None:
                target = ET.SubElement(prev_li, "ul")
            if sub is not None:
                for child in list(sub):
                    target.append(child)
            continue
        merged.append(li)
        prev_text, prev_li = text, li
    for li in list(top):
        top.remove(li)
    for li in merged:
        top.append(li)
    inner = "".join(ET.tostring(child, encoding="unicode", method="html") for child in root)
    html_path.write_text(html[: m.start(2)] + inner + html[m.end(2):], encoding="utf-8")


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
    validate_epub_xhtml(epub_out)
    return epub_out


def validate_epub_xhtml(epub: Path) -> None:
    """Fail the build if any XHTML inside the EPUB is not well-formed XML.

    Pandoc copies raw HTML through verbatim, so a hand-authored sidenote
    written as `<input ...>` (fine in HTML5, and WeasyPrint renders it)
    produces "Opening and ending tag mismatch: input and p" in every
    XHTML-strict reader (Apple Books, Calibre). Raw void elements must be
    self-closed: `<input ... />`, `<img ... />`, `<br />`."""
    import subprocess, tempfile, zipfile
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(epub) as z:
            names = [n for n in z.namelist() if n.endswith((".xhtml", ".html"))]
            z.extractall(tmp, names)
        bad = []
        for n in names:
            r = subprocess.run(["xmllint", "--noout", str(Path(tmp) / n)], capture_output=True, text=True)
            if r.returncode != 0:
                bad.append(f"{n}: {r.stderr.strip().splitlines()[0]}")
    if bad:
        sys.exit("EPUB XHTML is not well-formed (self-close raw <input>/<img>/<br> in the manuscript):\n  " + "\n  ".join(bad))
    print(f"EPUB XHTML well-formed ({len(names)} files)")


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
