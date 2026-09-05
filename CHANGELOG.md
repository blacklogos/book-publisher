# Changelog

## v0.2.0 — 2026-09-06

### New features
- New `haibara` theme: business-guide look reverse-engineered from the HBR Guide series (372x642pt trim, serif body with first-line indents, light + bold sans chapter openers, running head top-outer, folio bottom-outer, roman-numeral front matter, a Contents page with real page numbers)
- Contents page now folds repeated Part headings: each Part appears once with its chapters nested under it

### Fixes
- `--wrap=none` on the pandoc call: a running-title longer than ~60 chars used to break a CSS string mid-declaration and silently drop the running head, footer brand, and page numbers from every page
- Tufte theme refinements (pdf, epub, and facing-pages CSS)

### Docs
- QA workflow expanded: which pages to rasterize beyond the default three previews, and a contact-sheet pass for books over ~40 pages

## v0.1.0 — 2026-08-27

Initial public release.

### New features
- Build designed PDF + EPUB from a single Markdown manuscript (pandoc + WeasyPrint pipeline, Python stdlib glue)
- Three themes reproducing real reference designs: boardroom (corporate lead magnet, default), tufte (monochrome academic with margin sidenotes), jianghu (translated-novel look with real footnotes)
- Book structure from plain headings: Part/Chapter/Section, YAML front matter, cover page, TOC, roman-numeral front matter restarting at Chapter 1
- Checklists, definition boxes, and sidenotes as ordinary Markdown
- --facing-pages duplex mode: mirrored margins, recto chapter openers
- Automatic preview PNG rendering for layout QA
- check_deps.py setup helper and fetch_fonts.py for self-contained typography
- Working example manuscript covering every supported pattern
