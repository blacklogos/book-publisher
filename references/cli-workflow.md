# Cross-agent CLI workflow

Everything here is plain shell + Python stdlib — no Claude-only features
(no subagents, no slash commands). Works identically from Claude Code,
Codex, agy (Antigravity CLI), or a bare terminal inside cmux.

## One-time setup on a new host

```bash
python3 scripts/check_deps.py     # reports pandoc/weasyprint status + fixes
brew install pandoc               # macOS; apt/dnf install pandoc on Linux
uv tool install weasyprint        # installs the `weasyprint` CLI via uv
```

`uv` follows this user's global rule (uv for all new Python, never pip/
venv/poetry). `build_book.py` itself has zero install-time dependencies —
it shells out to `pandoc`/`weasyprint` and uses `uv run --with pypdfium2
--with pillow` on demand for rasterization, so nothing needs a persistent
venv.

**macOS-only gotcha**: WeasyPrint's dynamic loader looks for
`libgobject-2.0-0` under a name Homebrew doesn't use, and fails with
`OSError: cannot load library 'libgobject-2.0-0'` unless
`DYLD_LIBRARY_PATH` includes Homebrew's `lib` dir. `build_book.py` sets
this automatically; only relevant if invoking `weasyprint` directly.

## Build a book

```bash
python3 scripts/build_book.py path/to/manuscript.md --out dist --theme boardroom
# writes dist/<name>.pdf, dist/<name>.epub, dist/cover.png,
# dist/preview/page-NN.png (first 3 pages, for visual QA)
```

`--formats pdf` or `--formats epub` builds just one target. `--theme`
defaults to `boardroom`; see `themes.md` for the full list. Add
`--facing-pages` for a book that will actually be printed and bound
double-sided (mirrors margins/header-footer odd vs even, starts
chapters on a recto page); leave it off for screen-read PDFs, which is
the common case and the default.

## QA loop (any agent)

1. Run the build.
2. Read `dist/preview/page-01.png` (and any other page you touched) —
   every agent in this toolchain can view images, so this is the fast
   feedback loop instead of guessing from CSS alone.
3. Edit `assets/pdf.css` / the manuscript, rebuild, re-check.

To preview a page range beyond the default 3, rasterize directly:

```bash
uv run --with pypdfium2 --with pillow python3 -c '
import pypdfium2 as pdfium
pdf = pdfium.PdfDocument("dist/<name>.pdf")
for i in range(len(pdf)):
    pdf[i].render(scale=150/72).to_pil().save(f"dist/preview/page-{i+1:02d}.png")
'
```

## cmux / parallel agents

Each book (or each chapter, for a long manuscript) can be drafted by a
separate cmux pane/agent as its own `.md` file; concatenate before running
`build_book.py`, since Pandoc needs one input file per format pass. Keep
front matter (title/copyright/promo) in a small `_meta.md` header file and
`cat _meta.md chapters/*.md > manuscript.md` before building.
