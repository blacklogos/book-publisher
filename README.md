# Book Publisher

Turn one Markdown file into a designed PDF and EPUB book. An agent skill for Claude Code, Codex, and any agent that reads skill folders.

Landing page: https://bookpublisher.cc4.marketing

## What you get

- Real book structure from plain headings: `#` Part, `##` Chapter, `###` Section, YAML front matter for title and author
- Cover page, table of contents, roman-numeral front matter that restarts at Chapter 1, running headers
- Checklists, definition boxes, and sidenotes written as ordinary Markdown
- Four themes reproducing real reference designs: `boardroom` (corporate lead magnet, default), `tufte` (monochrome academic, margin sidenotes), `jianghu` (translated-novel look, real footnotes), `haibara` (business-guide look in the spirit of the HBR Guide series: serif body, sans chapter openers, real Contents page)
- `--facing-pages` for duplex print: mirrored margins, chapters open on a right-hand page
- Every build renders preview PNGs so layout bugs are caught before shipping

## Install

```sh
git clone https://github.com/blacklogos/book-publisher ~/.claude/skills/book-publisher
```

Or download the [latest release zip](https://github.com/blacklogos/book-publisher/releases/latest/download/book-publisher.zip), unzip, and copy the `book-publisher` folder into your skills directory.

One-time dependencies (pandoc + weasyprint):

```sh
python3 scripts/check_deps.py
```

It prints exact install commands for your OS.

## Use with an agent

Install, open a new session, and describe the book:

> Turn my notes in drafts/pricing-guide.md into a lead magnet PDF.

> Write a 5-chapter beginner's guide to sourdough and build it as a book. Tufte theme.

The agent reads SKILL.md, writes the manuscript, builds, and checks the rendered previews.

## Use by hand

```sh
python3 scripts/build_book.py assets/example-book.md --out out
open out/example-book.pdf
```

Try `--theme tufte` or `--theme jianghu` on the same command. To write your own book, copy `assets/example-book.md` and replace the words; every supported pattern is in there working. Full conventions: `references/content-model.md`.

## Add a theme

Found a PDF or page whose look you love? `references/themes.md` documents the process used to build the four included themes: sample the real colors, read the real fonts, translate to CSS paged media, plus the WeasyPrint pitfalls already solved.

## License

MIT. Bundled fonts (Fraunces, Be Vietnam Pro) are under the SIL Open Font License. The `tufte` theme adapts [Tufte CSS](https://github.com/edwardtufte/tufte-css) (MIT).
