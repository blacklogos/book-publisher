# Themes

`assets/themes/<name>/{pdf.css,epub.css}` are fully self-contained design
systems. `template.pdf.html5` (the cover/front-matter/TOC/content shell)
and every manuscript convention in `content-model.md` are shared across
all of them — a manuscript never needs to change to switch themes.

```
scripts/build_book.py manuscript.md --theme tufte
```

## Available themes

- **boardroom** (default) — corporate lead-magnet look reverse-engineered
  from a consulting-firm lead-magnet PDF (reference kept private). Wide left margin, three-tier
  colored headings (navy Part, green Chapter, navy Section), full-bleed
  color cover. See `design-tokens.md` for its exact values.
- **tufte** — monochrome academic/print look adapted from Tufte CSS
  (Dave Liepmann, MIT license, github.com/edwardtufte/tufte-css), the
  design behind https://luhmann.surge.sh/learning-how-to-read. Serif
  throughout, restrained paper-white cover, sidenotes in a right-margin
  rail instead of colored headings. Tokens live at the top of
  `themes/tufte/pdf.css`.
- **jianghu** — translated-novel look reverse-engineered from a
  Vietnamese-translated Chinese wuxia/xianxia sample ("Minh Hải Cấm
  Địa", gioithieusach.com, 2026). Digest trim (5.5x8.5in, not the other
  two themes' shared US Letter), first-line-indent body paragraphs with
  no inter-paragraph gap, centered uppercase chapter openers with
  generous top whitespace, a gold-double-rule "plate" for the
  frontmatter/character-list page, real bottom-of-page footnotes for
  in-story glossary terms, and roman-numeral front-matter pagination
  that resets to Arabic 1 at Chapter 1. Tokens live at the top of
  `themes/jianghu/pdf.css`. See "Real per-page footnotes and
  roman-numeral front matter" below for the two WeasyPrint mechanisms
  this theme introduced, reusable by any future theme.

## Illustrated covers and inline images

Both themes support a generated-art cover and inline illustrations, shipped
after building a real book (a Vietnamese Zettelkasten guide) with them.

**Cover.** Set `cover-image: "/absolute/path/to/art.png"` in the
manuscript's YAML front matter (see `content-model.md`). Mechanism: the
pandoc template only adds an inline `--cover-image` custom property to
the `<section class="cover">` element when the field is present, and each
theme's `.cover[style]` rule (which only matches when that attribute
exists) layers a paper/plum-tinted gradient over the art so the cover
title/subtitle/logo text stays legible. A book that doesn't set
`cover-image` renders byte-for-byte the same solid-color cover as before,
this is strictly additive. Both themes are verified by real render (see
below) — including a real WeasyPrint bug caught and fixed in the
process: `var()` cannot carry a `url()` value reliably (`background-image:
linear-gradient(...), var(--x)` where `--x: url(...)` silently drops the
image with "Relative URI reference without a base URI: None", even for
an absolute path, reproduced both from an inline style and an external
stylesheet), so the tint is a `::before` overlay instead of a second
`background-image` layer, and `.cover-title`/`.cover-subtitle` needed
`position: relative` added or the overlay painted over the text instead
of behind it (positioned z-index:auto elements paint after non-positioned
in-flow siblings regardless of source order). If a new theme adds
`cover-image` support, copy this exact mechanism, not the more obvious
two-layer `background-image` approach — that one looks correct and
builds without error, it just silently loses the image.

Portrait art at or near the 600x900pt cover box (2:3 aspect, e.g.
1024x1536px) crops cleanest; anything drastically off-aspect will
crop from the center via `background-size: cover`.

**Inline illustrations/placeholders.** Standard Markdown
`![alt](/absolute/path.png)` now works in the manuscript body — both
themes cap images to the content-column width automatically (added to
`pdf.css`/`epub.css` as part of this; previously *no* theme constrained
image size, so a native-resolution PNG would render at native pixel size
and bleed off the page — a real bug, not a hypothetical, hit building the
Zettelkasten book). See `content-model.md`'s "Recurring patterns" for the
placeholder-image convention.

**Generating the art (gen-image skill).** Neither theme's illustrations
are photorealistic or brand-flat — they're monochrome ink engravings,
which is what makes them sit naturally on a print page instead of looking
like a pasted-in web graphic. Style string used for both the tufte cover
and its chapter illustration (works for boardroom too, though not yet
tried there):

> Monochrome academic engraving style, ink on cream paper #fffff8, fine
> crosshatch line work like a 19th-century book plate or Tufte-CSS
> aesthetic, sepia-black ink #111111 only, no color, no gradients,
> restrained and scholarly, generous whitespace, NOT photorealistic,
> NOT 3D, NOT cartoonish, NOT modern flat-vector.

Invocation (see the `gen-image` skill for the full contract):
```bash
gen-image.sh --name "cover-art" \
  --scene "an old wooden card-catalog drawer, pulled slightly open, \
rows of index cards standing upright inside, three-quarter angle" \
  --style "<the style string above>" \
  --aspect "2:3 portrait" \
  --out path/to/images/
```
One metaphor per image, same restraint principle as `gen-image`'s other
styles (see its `references/styles.md`): a single clear scene, not a
busy collage. For a book-specific bug/concept illustration, describe the
*metaphor* (e.g. "a librarian whose lantern only lights the first
shelf, everything else fades to black") rather than a literal screenshot
or diagram — that's what separates an illustration from a UI mockup.

For a placeholder standing in for an asset that isn't ready yet (a real
screenshot, say), don't spend an AI generation on it — a plain
deterministic graphic (bordered box, one simple line icon, a caption)
made with Pillow/PIL is faster, has no text-rendering risk, and reads
unambiguously as "placeholder" rather than as a low-effort illustration.

## Real per-page footnotes and roman-numeral front matter

Both introduced by the `jianghu` theme, verified by real render before
being written into its `pdf.css`, and available to any theme:

**Bottom-of-page footnotes.** WeasyPrint fully implements the CSS GCPM
`float: footnote` feature — a footnote written inline at its point of
reference gets pulled to the bottom of whichever page it lands on and
numbered automatically, real pagination-aware footnotes, not endnotes.
Pandoc's own `[^1]` footnote syntax won't drive this (it emits the
definition in one `<section class="footnotes">` block at the end of the
document, nowhere near the per-page reference point `float: footnote`
needs), so — same reasoning as the existing hand-authored sidenote
convention — write it as raw HTML right at the word being annotated:
```html
word<span class="footnote">Note text.</span>
```
CSS (see `themes/jianghu/pdf.css` for the full version with borders):
```css
.footnote { float: footnote; }
::footnote-call { content: counter(footnote); vertical-align: super; font-size: 0.68em; }
::footnote-marker { content: counter(footnote) ". "; }
@page { @footnote { border-top: 0.75pt solid gray; padding-top: 6pt; margin-top: 10pt; } }
```
A theme with no `.footnote` rule (e.g. `boardroom`) just renders the note
text as a stray inline run if a `jianghu`-authored manuscript is built
under it — harmless, same asymmetry already accepted for sidenotes.

**Roman-numeral front matter, resetting to Arabic 1 at Chapter 1.**
`counter-reset: page N` (the special CSS Paged Media page counter) is
silently ignored when set on a normal body/DOM element — confirmed
empirically, not documented clearly upstream. WeasyPrint only honors it
inside an `@page` rule. The working pattern is a named page per side of
the split:
```css
section.frontmatter, section.statement, #TOC { page: frontmatter; }
@page frontmatter { @bottom-right { content: counter(page, lower-roman); } }
article.content > h1:first-of-type { page: mainmatter; }
@page mainmatter { counter-reset: page 1; @bottom-right { content: counter(page); } }
```
`h1:first-of-type` is what makes this safe to reuse even though
`content-model.md` requires the Part `h1` to repeat before every
Chapter: `:first-of-type` only ever matches the literal first h1 among
its siblings, so later chapters' repeated `h1`s fall through to the
plain (Arabic) `@page` rule and just keep incrementing. `#TOC` needs
its own `page: frontmatter` too — it renders inside `article.content`
but *before* the first real `h1` (see `template.pdf.html5`), so without
it the TOC page displays an Arabic number one page early even though
the counter *value* is still correct once Chapter 1 resets it. And
`section.statement`/`section.frontmatter` (tag+class) deliberately
don't match a *mid-book* `::: statement :::` fenced div, which pandoc
compiles to `<div class="statement">` nested inside `article.content`
— a different tag, a different ancestor, so it's naturally excluded and
keeps normal Arabic numbering.

Each named `@page` rule needs its own full geometry (`size`, `margin`,
etc.) restated — a named page does not inherit unset properties from
the plain `@page` rule, it falls back to UA defaults instead. Forgetting
this silently loses the theme's margins on exactly the pages using the
override (found while building `jianghu`: the cover page's `@page cover`
rule already does this for the same reason; the frontmatter/mainmatter
split is the same pattern applied to counter formatting instead of
zero-margin geometry). `--facing-pages` interacts with this the same way
`tufte`'s sidenote rail does — real limitation, documented in
`themes/jianghu/facing-pages.css`, not silently wrong: a named page's
own unconditional `margin` outranks a plain `@page :left`/`:right`
override in the page-selector cascade, so the frontmatter/first-chapter
pages keep single-sided margins even when facing pages is on; every
other page mirrors correctly.

## Adding a new theme

1. Copy an existing `themes/<name>/` directory as a starting point.
2. Re-derive colors/fonts/spacing from the actual reference (screenshot
   pixel-sample it, or read the source CSS if it's a web page) rather
   than guessing — see the git history of the tufte theme for the
   pattern: fetch the page, read its CSS, sample cover colors, then
   translate to WeasyPrint paged media.
3. Keep the same class contract the template emits: `.cover`,
   `.cover-title`, `.cover-subtitle`, `.cover-logo`, `.frontmatter`,
   `.statement`, `#TOC`, `article.content`, `h1`/`h2`/`h3`/`h4`,
   `ul.task-list`. A theme is just CSS against these; no template edits.
4. `h1`/`h2`/`h3` are Part/Chapter/Section *semantically*, not
   necessarily in that visual size order — remap sizes to whatever the
   reference's actual visual hierarchy implies (tufte puts the biggest
   treatment on h2/Chapter, not h1/Part, because that's what a reader
   scans for; boardroom does the same via color instead of size).
5. Build the shared `assets/example-book.md` with the new theme and
   check every preview page, not just the cover — the real bugs so far
   have all been in @page mechanics (running header/footer bleeding
   onto the cover, page-canvas background not reaching the margin area)
   that only show up once you look at more than one page.

## Known WeasyPrint gotchas (apply to every theme)

- `@page cover { margin: 0; }` does not, by itself, stop a *different*
  `@page { @bottom-right { content: ... } }` rule from painting into
  that now-zero-size margin box. Explicitly set `content: none` on each
  margin box for the cover page.
- A theme's page background must be set via `background` on the `@page`
  rule itself to cover the margin area too — `html`/`body` background
  only fills the content box, leaving a visible seam at the page edges
  on any non-white theme.
- Flexbox (`display: flex`) mis-sizes anonymous items created from mixed
  element+text content (e.g. a checkbox `<input>` followed by inline
  text) — labels wrap early and content jumps beside instead of after.
  Use `float: left` + `overflow: hidden` (hanging indent) instead;
  that's what both themes' `ul.task-list` styling does.
- CSS custom properties (`var(--x)`) work; percentage-based negative
  margins for sidenote-style rails do not translate from a fluid web
  layout to a fixed print page — the percentage resolves against the
  wrong containing block. Reserve real `@page margin` space and float
  into it with fixed `pt` values instead.
- Don't trust a classic "book" serif stack (Palatino especially) with
  non-Latin diacritics before checking. macOS's actual `Palatino.ttc`
  mispositions Vietnamese combining tone marks (verified by rendering
  the same sentence through Palatino vs. Georgia vs. Times New Roman —
  only Palatino garbled it). Georgia and Times New Roman both shape
  Vietnamese correctly and are close enough in feel to substitute
  without changing a theme's character; put them first in the font
  stack and treat Palatino as a low-priority fallback, not the primary
  choice, whenever a manuscript might be non-English.
- `hyphens: auto` mis-breaks real Vietnamese words — confirmed by
  rendering the same paragraph with and without it (a footnote column
  under `jianghu` split "tiểu thuyết" mid-word only when `auto` was on).
  Dictionary-based hyphenation isn't Vietnamese-aware. Don't set
  `hyphens: auto` on a manuscript that might be Vietnamese; the CSS
  default (`manual`, only breaking at literal soft hyphens) is safe and
  is what every current theme relies on implicitly by simply not setting
  the property.
- An `<img>` with no CSS renders at its native pixel size, not scaled to
  the page. A real illustration or screenshot is routinely 2-4x wider
  than a ~360pt content column, so it silently bleeds off the page edge
  (or, worse, gets clipped mid-image with no error). Both themes now
  cap `article.content img` to `max-width: 100%; height: auto` — if a
  new theme is added, carry that rule over, it isn't optional.
