---
name: book-publisher
description: "Build designed PDF+EPUB books/lead magnets from Markdown: swappable themes, checklists, cover page, sidenotes."
---

# Book Publisher

Turns a single Markdown manuscript into a professionally designed PDF and
EPUB via a swappable **theme** system — each theme reproduces a real
reference design (a PDF someone liked, a web page someone liked) rather
than a generic default look. One manuscript, any theme, no edits needed
between them.

## When to use

Any request to produce a polished ebook, lead magnet, guide, or report as
a downloadable PDF and/or EPUB — not a one-off text answer, and not a
plain unstyled document (use the `docx`/`pdf` skills for those instead).
Also use this when the user points at a PDF or web page and says "I like
this look, use it for our book(s)" — that's a request to add a new theme
(see "Adding a theme" below), not a one-off styling hack.

## Themes

- `boardroom` (default) — corporate lead-magnet look: colored Part/Chapter/
  Section headings, wide left margin, full-bleed color cover.
- `tufte` — monochrome academic/print look adapted from Tufte CSS: serif
  throughout, sidenotes in a right-margin rail, restrained paper-white
  cover.
- `jianghu` — translated-novel look: digest trim, first-line-indent body
  paragraphs, centered chapter openers, real bottom-of-page footnotes,
  a gold-rule frontmatter "plate", roman-numeral front matter that
  resets to Arabic 1 at Chapter 1.

Full details, tokens, and how each was derived: `references/themes.md`.

## Workflow

1. **Read `references/content-model.md`** for the Markdown conventions
   (heading levels = Part/Chapter/Section, the "repeat the Part heading
   before every Chapter" pagination rule, checklist/definition/sidenote
   syntax, front-matter fields).
2. Write the manuscript as one `.md` file — start from
   `assets/example-book.md` (a working, buildable reference covering
   every pattern, theme-agnostic) rather than from scratch.
3. **First time on a host**: `python3 scripts/check_deps.py`, then
   `brew install pandoc` (or apt/dnf) and `uv tool install weasyprint` if
   either is missing. Details and the macOS dylib gotcha are in
   `references/cli-workflow.md`.
4. Build: `python3 scripts/build_book.py manuscript.md --out dist --theme boardroom`.
   Produces `dist/<name>.pdf`, `dist/<name>.epub`, and
   `dist/preview/page-NN.png` for the first few pages.
5. **Always view the preview PNGs** before calling the book done — CSS
   paged-media output has real failure modes (overflow, bad breaks,
   color mistakes, running header/footer bleeding onto the cover) that
   only show up rendered, and only sometimes only show up past page 1.
6. Iterate on the theme's CSS or the manuscript, rebuild, re-check.

## Facing pages (print/duplex)

Default output is single-sided: every page uses the same fixed margins,
correct for reading one page at a time on a screen (which is what both
current themes' source references are). If the book is actually going
to be printed and bound double-sided, add `--facing-pages`: margins and
running header/footer mirror between odd (recto/right) and even
(verso/left) pages, and chapters start on a recto page (inserting a
blank verso if needed) instead of wherever they happen to fall. EPUB is
reflowable and unaffected either way. Per-theme mechanics, and a real
CSS limitation (sidenote rails can't fully alternate sides — documented
rather than silently wrong) are in each theme's `facing-pages.css`.

## Adding a theme (new reference design)

Don't guess a look from memory — derive it the same way the two existing
themes were built: fetch the actual PDF/page, sample real pixel colors
and read the real CSS/fonts, then translate to WeasyPrint paged media.
Full step-by-step and the WeasyPrint gotchas already hit (cover-page
header/footer bleed, page-canvas background not covering margins, flex
mis-sizing checklists) are in `references/themes.md` — read it before
starting so those bugs aren't re-introduced.

## To change an existing theme

All tokens (colors, fonts, page geometry, type scale) are CSS custom
properties at the top of each `assets/themes/<name>/pdf.css`. Edit tokens
first; only touch individual selectors for structural changes.

Fonts default to a zero-dependency system stack per theme (already
renders correctly on any host). Run `scripts/fetch_fonts.py` only if
pixel-exact, fully self-contained typography is required (embeds Fira
Sans, OFL-licensed); wire it in with `--extra-css assets/fonts.css`.

## Files

- `assets/themes/<name>/{pdf.css,epub.css,facing-pages.css}` — the design
  systems (`facing-pages.css` only applies with `--facing-pages`).
- `assets/template.pdf.html5` — Pandoc HTML template (cover/front-
  matter/TOC wrapper) shared by every theme, feeding WeasyPrint.
- `assets/example-book.md` — copy-and-edit starter manuscript.
- `scripts/build_book.py` — the only command needed to produce output.
- `scripts/check_deps.py`, `scripts/fetch_fonts.py` — setup helpers.
