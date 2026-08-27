# Design tokens: the `boardroom` theme

This file covers the default `boardroom` theme only. For the `tufte` theme
(or any other), see `themes.md` — each theme's own tokens live as CSS
custom properties at the top of its `pdf.css`, which is the citable
source once a theme exists; this file predates the multi-theme system
and documents the original reverse-engineering in full.

Reverse-engineered from a 2025 consulting-firm lead-magnet PDF (reference kept private) by
rendering sample pages to PNG and sampling pixels + `pdffonts`/`pypdf`
mediabox. All values already live in `assets/pdf.css` / `assets/epub.css`
as CSS custom properties — this file is the citable source of truth when
a value needs to change or be checked.

## Geometry

- Interior trim: **US Letter, 612×792pt** (8.5×11in).
- Cover trim: **600×900pt** (8.333×12.5in) — a distinct, smaller custom
  trim, not the same page size as the interior.
- Interior margins: top 54pt, right 54pt, bottom 54pt, **left 162pt**
  (2.25in) — the wide left rail is the signature layout trait. Text
  column width = 396pt (5.5in).
- Cover padding: ~90pt top, 60pt sides/bottom.

## Color

| Token | Hex | Use |
|---|---|---|
| `--c-navy` | `#012169` | Part label, Section (h3) heading, links |
| `--c-green` | `#188038` | Chapter (h2) heading |
| `--c-ink` | `#1a1a1a` | Body text |
| `--c-meta` | `#808080` | Running header/footer, page number |
| `--c-cover-bg` | `#2a1642` | Cover background (deep aubergine) |
| `--c-cover-fg` | `#fffbf7` | Cover title (warm off-white) |
| `--c-cover-accent` | `#c89e80` | Cover subtitle (muted gold/tan) |

Note: TOC entries (Part + Chapter + Section) all render navy for scan-
ability; the green chapter accent only appears on the actual chapter-
opener heading in body flow. `pdf.css`'s `#TOC` rules already encode this.

## Type

- Sans (headings, body, UI): `Fira Sans` (Regular/SemiBold/Bold), falling
  back to system sans. Confirmed via `pdffonts` on the source PDF.
- Serif (cover title/subtitle only): `Times New Roman`, falling back to
  `Liberation Serif`/Georgia — also confirmed via `pdffonts`. Zero-
  dependency by default; see `scripts/fetch_fonts.py` to swap in an
  embedded open-license alternative for pixel-exact cross-host rendering.
- Cover title ≈64pt/1.12 line-height; subtitle ≈22pt.
- Chapter (h2) 22pt/700; Section (h3) 15pt/700; Part label (h1) 13pt/700;
  body 10.5pt/1.55 line-height.

## Recurring patterns

- **Definition paragraph**: `**Term:** sentence.` — bold lead-in, no
  special markup beyond standard bold.
- **Checklist**: pandoc task list (`- [ ] **Label:** text`) styled as an
  empty square box (not a native checkbox glyph) + bold label.
- **Statement/promo page**: a full page of large bold black sans text,
  breaking on phrase boundaries, plus a smaller CTA line — still carries
  the normal running header/footer chrome (it is not a bleed page).
- **Chapter pagination**: every chapter starts a fresh page, and the Part
  label always appears directly above it, repeated per-chapter. See
  `content-model.md` for why only `h1` (not `h2`) carries the page break.
