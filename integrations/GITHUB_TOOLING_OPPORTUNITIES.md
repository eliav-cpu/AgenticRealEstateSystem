# GitHub Tooling Opportunities — PRIME / King Tamar

## Purpose
This document captures external GitHub tooling that can improve PRIME / King Tamar production: Hebrew RTL, text correction, visual QA, slide generation, image rendering and deck automation.

## Status
Working Draft | Tooling Research | Not yet adopted into production

## Core Finding
The strongest improvement is not one magic repository. It is a controlled pipeline that combines:

1. deterministic slide generation
2. controlled Hebrew text layer
3. visual screenshot QA
4. Hebrew OCR / typo detection
5. image/background generation separated from final Hebrew typography

## Recommended Stack

### 1. PptxGenJS — deterministic PPTX generation
Potential use:
- Generate editable PowerPoint slides from structured JSON.
- Keep final Hebrew as editable text rather than generated image text.
- Enforce layout positions, card systems, fonts, colors and 16:9 sizing.

Role in PRIME pipeline:
- Use after Client Copy V6 is approved.
- Build actual slide templates with editable Heebo text.
- Avoid AI-generated Hebrew typography errors.

Adoption priority: High.

### 2. Marp / Markdown-to-PPTX tooling
Potential use:
- Fast text-to-deck workflows from Markdown.
- Useful for internal decks, playbooks and simple structured presentations.

Role in PRIME pipeline:
- Good for internal training and first-pass outlines.
- Not ideal as final premium visual layer unless heavily customized.

Adoption priority: Medium.

### 3. Playwright visual regression / screenshot comparison
Potential use:
- Render slides or HTML slide previews.
- Compare current slide vs approved baseline.
- Detect layout drift, overflow, alignment shifts and visual inconsistency.

Role in PRIME pipeline:
- Use as automated visual QA gate.
- Compare Light/Dark variants for structure consistency.
- Flag when a generated slide is visually different from approved DNA.

Adoption priority: High.

### 4. Hebrew OCR with Tesseract / tesseract.js
Potential use:
- Extract Hebrew text from generated slide images.
- Detect whether image text is readable or broken.
- Compare OCR output against approved slide copy.

Role in PRIME pipeline:
- Use only as QA assistance, not as the main reading layer.
- Detect major text failures after image generation.

Adoption priority: Medium-High.

### 5. Hebrew spell checking / Hspell
Potential use:
- Run Hebrew spelling checks on slide copy before final rendering.
- Catch obvious typos before image or PPT generation.

Role in PRIME pipeline:
- Add to pre-generation text QA.
- Combine with manual PRIME language QA.

Adoption priority: Medium.

### 6. resvg-js / SVG rendering
Potential use:
- Generate crisp PNGs from SVG/HTML-like layout systems.
- Keep layout deterministic.
- Create high-resolution visual assets with controlled typography zones.

Role in PRIME pipeline:
- Useful for banners, cards, thumbnails and clean text-safe image layers.
- Best when combined with a controlled font/text layout engine.

Adoption priority: Medium.

## Recommended Production Architecture

```text
Client Copy V6
  -> JSON slide schema
  -> Hebrew text QA
  -> deterministic template renderer
  -> PPTX editable slide OR SVG/PNG visual
  -> screenshot QA
  -> OCR / text comparison QA
  -> final asset
```

## New Modules To Build In Our Repo

### 1. `tools/slide-schema/`
Defines a structured JSON format for every slide:
- slide_id
- role
- headline
- subtitle
- cards
- message_line
- source_flags
- visual_mode
- colorway

### 2. `tools/hebrew-qa/`
Checks:
- RTL markers
- forbidden words
- risky commercial language
- typo candidates
- line length
- text density

### 3. `tools/pptx-renderer/`
Uses PptxGenJS or equivalent to create editable slides from the schema.

### 4. `tools/visual-regression/`
Uses screenshot comparison to compare generated output to approved baselines.

### 5. `tools/ocr-qa/`
Uses OCR to compare rendered slide text against approved copy.

## Key Rule
Do not let image generation write final Hebrew text.
Use image generation for background, architecture, mood, cards and visual composition.
Use deterministic text rendering for final Hebrew.

## Recommended Next Step
Build the first internal MVP:

```text
Slide JSON -> Hebrew QA -> PPTXGenJS editable slide -> screenshot QA
```

This will improve speed and reduce typography failures more than any prompt alone.

## Tooling Decision
Adopt conceptually now:
- PptxGenJS style editable slide generation
- Playwright visual QA
- Hebrew OCR QA
- Hspell-style spelling check
- SVG/PNG rendering for banners

Do not adopt blindly:
- random AI presentation generators
- small unmaintained presentation repos
- tools that create non-editable Hebrew text
- tools that cannot preserve RTL
