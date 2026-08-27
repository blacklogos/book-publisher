# Changelog

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
