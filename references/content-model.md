# Markdown authoring conventions

The manuscript is one Pandoc-flavored Markdown file. `assets/example-book.md`
is a working, buildable reference — copy it as a starting point. It is
theme-agnostic: the same file builds under any `--theme` (see
`themes.md`) without edits.

## YAML front matter (all optional except `title`)

```yaml
title: Book Title
subtitle: Optional subtitle
running-title: "Book Title: Optional subtitle"   # top-right header text
footer-brand: "PUBLISHER NAME"                   # bottom-left footer text
footer-cta: "yourdomain.com | "                  # bottom-right, before page #
publisher-name: "PUBLISHER NAME"                 # small wordmark on cover
cover-image: "/absolute/path/to/art.png"         # optional illustrated cover,
                                                   # both themes — see themes.md
copyright: |                                     # raw markdown, becomes the
  Copyright text as one or more paragraphs.       # copyright/front-matter page
promo: |                                         # raw markdown, becomes a
  Big bold statement.                             # full-page promo/CTA — see
                                                   # design-tokens.md "statement"
  Smaller follow-up line.
```

`copyright` and `promo` are plain markdown block scalars — Pandoc parses
them as real paragraphs, not literal strings, so normal `**bold**` etc.
works inside them.

## Heading levels are semantic, not just visual

- `# Part N. Title` → Part label (h1)
- `## Chapter N. Title` → Chapter heading (h2)
- `### N.M Section Title` → Section heading (h3)
- `#### Minor heading` → rarely needed (h4)

**Every `## Chapter` must be immediately preceded by its `# Part` heading**,
even if it repeats the same Part text as the previous chapter. Only `h1`
carries `page-break-before: always` in `pdf.css` — this is deliberate: if
both h1 and h2 forced breaks, a part's 2nd+ chapter (already preceded by
h1) would get a spurious blank page. Repeating the h1 is what starts each
chapter on its own fresh page without that side effect. See
`design-tokens.md` for the rationale in one place.

## Recurring patterns

- Definition/glossary line: `**Term:** definition sentence.`
- Checklist: standard Pandoc task list syntax —
  `- [ ] **Label:** description.` (requires `+task_lists` when invoking
  pandoc; `scripts/build_book.py` already passes it).
- Full-page statement/CTA: use the `promo` front-matter field (one per
  book, rendered right after the copyright page) — for a statement page
  *mid-book*, use a fenced div instead: `::: statement` ... `:::`
  (requires `+fenced_divs`, also already enabled).
- Sidenote/margin note (rendered only by themes that define a margin
  rail, e.g. `tufte` — see `themes.md`): hand-authored raw HTML right at
  the point being annotated, matching upstream Tufte CSS's own
  convention (there's no lighter Markdown syntax for this upstream
  either):
  ```html
  word<label for="sn-1" class="margin-toggle sidenote-number"></label><input type="checkbox" id="sn-1" class="margin-toggle"><span class="sidenote">Note text.</span>
  ```
  Each note needs a unique `id`/`for` pair. Themes without a margin rail
  (e.g. `boardroom`) hide `.sidenote`/`.marginnote`/`.margin-toggle` cleanly
  rather than rendering them broken — the note's content is simply lost
  in those themes, which is expected, not a bug.
- End-of-chapter framed lesson box (journal-narrative + boxed-takeaway
  format, e.g. `jianghu`'s reference book — see `themes.md`): a fenced
  div, `::: lesson-box ... :::`, same mechanism as `::: statement :::`
  but inline in the chapter flow — it does not force a page break, so
  it's for a short takeaway paragraph at the natural end of a chapter,
  not a dedicated full page. Themes without a `.lesson-box` rule render
  it as a plain unstyled paragraph, same graceful-fallback pattern as
  `.statement`/`.sidenote`.
- Footnote (rendered as a real bottom-of-page note by themes that
  define `.footnote`, e.g. `jianghu` — see `themes.md`; themes without
  one, e.g. `boardroom`, just render the text as a plain inline run):
  hand-authored raw HTML at the point of reference, same pattern as the
  sidenote convention above — there's no lighter Markdown syntax for
  this either, and Pandoc's own `[^1]` footnote syntax won't drive a
  per-page float (it emits definitions in one block at the document's
  end, see `themes.md` for why that doesn't work here):
  ```html
  word<span class="footnote">Note text.</span>
  ```
- Dialogue in a translated-fiction manuscript: start the line with an
  em dash `—`, not a hyphen `-`. Two independent reasons converge on the
  same fix: it's the correct Vietnamese-translated-fiction typographic
  convention, and a line starting with `- ` (hyphen + space) is Markdown
  bullet-list syntax — Pandoc will silently turn a whole page of dialogue
  into a bulleted list instead of paragraphs if written with a plain
  hyphen.
- Inline illustration or screenshot: standard Markdown image syntax,
  `![alt text](/absolute/path/to/image.png)`. Use an absolute filesystem
  path, not one relative to the manuscript — the intermediate HTML pandoc
  writes lives in `--out`, not next to the manuscript, so a
  manuscript-relative path silently resolves to the wrong directory
  (`<out>/<manuscript-dir>/image.png`, which doesn't exist) and the image
  drops. Both themes cap images to the content-column width
  automatically (`article.content img` in each `pdf.css`/`epub.css`); no
  per-image sizing needed in the manuscript. For a placeholder standing
  in for an asset that doesn't exist yet, put the image inside a
  blockquote with a short caption line rather than leaving bare marker
  text — a reader should see "this is intentionally a placeholder," not
  raw TODO-style brackets:
  ```markdown
  > ![Ảnh chụp màn hình sẽ cập nhật](/absolute/path/to/placeholder.png)
  >
  > **[CẦN SCREENSHOT THẬT]** what the real screenshot needs to show.
  ```

## What NOT to hand-author

- The cover page, copyright/front-matter page, and table of contents are
  all generated from front matter + `--toc` — don't write them as body
  Markdown.
