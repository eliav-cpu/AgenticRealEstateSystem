# 07 - Figma Master Slide System

## Current EXEL authority — V1.1 (2026-10-31)

Read [the canonical EXEL skill](https://github.com/eliav-cpu/AgenticRealEstateSystem/blob/main/skills/exel-institutional-royal-slides/SKILL.md) and [the integration rules](https://github.com/eliav-cpu/AgenticRealEstateSystem/blob/main/docs/EXEL_VISUAL_AUTHORITY_V1_1.md) first. They override conflicting legacy brand/palette/ratio, forced components, automatic Light/Dark and repair instructions below. PRIME is historical context, not active EXEL branding. For **PALETTE_ONLY**, lock layout, copy, images, faces, logos, icons and editable text; change colors only. Project facts and flow remain project-specific. Prior versions are retained in Git history at `2481857`.

## Purpose
This file defines the Figma layer for building precise, reusable, premium slide systems.

Figma is the preferred layer for:
- master slide design
- reusable card systems
- Light / Dark variants
- exact spacing
- typography control
- design tokens
- components
- investor presentation boards

## Core Rule
Figma is the control room. Canva is the fast campaign floor.

Use Figma when the asset must become a reusable visual system, not just a one-time graphic.

## Master Slide Production Flow

```text
1. Define slide role
2. Define screen copy
3. Choose master layout
4. Apply PRIME color mode
5. Build card hierarchy
6. Add image / visual layer
7. Add Hebrew live text
8. Create Light version
9. Create Dark version
10. Export full and clean versions
```

## Required Master Layouts

### 1. Cover Master
Use for opening slides.

Structure:
- large Hebrew title
- short subtitle
- premium project image or architectural render
- small brand lockup
- subtle circular trust motif

### 2. Strategic Light Board
Use for data, logic, benchmarks and decision slides.

Structure:
- light background
- large right-aligned headline
- 3-4 cards
- thin blue / champagne lines
- optional map, chart, table or image
- bottom message line

### 3. Authority Dark
Use for trust, leadership, closing and high-importance moments.

Structure:
- Institutional Navy background
- white typography
- restrained champagne detail
- strong portrait / project image
- minimal cards
- premium private-banking feel

### 4. Premium Photo Narrative
Use for city, lifestyle, project and atmosphere.

Structure:
- large real image
- controlled navy overlay
- right-side or bottom card cluster
- short text only
- emotional but disciplined tone

### 5. Benchmark Board
Use for King Tamar vs King David or comparable reference logic.

Structure:
- two comparison zones
- neutral benchmark language
- no aggressive competitor attack
- clear investor interpretation
- final message line explaining what the benchmark helps evaluate

### 6. Excel Transition Board
Use before simulator / numbers.

Structure:
- decision headline
- 3-step bridge from story to numbers
- visual cue toward Excel
- CTA-style bottom line

## Component Families

### KPI Card
Use for numbers and metrics.

Fields:
- label
- main number
- short explanation
- source / verification status if needed

### Trust Card
Use for people, companies and process anchors.

Fields:
- trust anchor
- role
- why it matters

### Decision Card
Use for investor decision points.

Fields:
- decision factor
- value
- proof / next check

### Process Card
Use for customer journey.

Fields:
- step number
- action
- result

### Comparison Card
Use for benchmark slides.

Fields:
- item
- what it shows
- investor interpretation

## Figma Design Tokens

### Colors
```text
Institutional Navy #0A1E3F
EXEL Blue #0066FF
Silver Gray #D8DADD
Pearl Gray #F3F4F5
Pure White #FFFFFF
Royal Champagne #B7A47D
Supporting Graphite #394452
```

### Typography
```text
Hebrew font: Heebo
H1: Heebo ExtraBold / Bold
H2: Heebo Bold
Body: Heebo Regular / Medium
Labels: Heebo Medium
```

### Spacing Logic
Use consistent spacing:
- outer margins: generous
- card padding: medium-large
- card gaps: consistent
- no cramped text
- no overloaded walls of text

## Light / Dark Pair Rule
Every strategic master should support:

### Light
- White / Pearl Gray / Mist background
- Navy headline
- Graphite body
- blue micro accents
- champagne micro detail

### Dark
- Institutional Navy background
- White text
- champagne micro accents
- EXEL Blue active marks
- same layout as Light

## Hebrew Handling In Figma
All Hebrew text must be:
- live text
- right aligned
- RTL
- sharp
- using Heebo
- not embedded as flattened image text

## Clean Version In Figma
For each important slide create:

### Full Version
Includes:
- final Hebrew copy
- cards
- CTA / message line
- image / visual layer

### Clean Version
Includes:
- background
- image areas
- card placeholders
- icon areas
- frame lines
- no final text

## Figma QA Checklist
Before export:
- Is the hierarchy readable in 3 seconds?
- Is Hebrew live and sharp?
- Are all cards aligned?
- Are Light and Dark versions structurally identical?
- Are colors within PRIME DNA?
- Is Champagne subtle, not dominant?
- Is there enough whitespace?
- Is the slide investor-grade, not decorative?

## Recommended Naming

```text
KT_Master_Cover_Light_v01
KT_Master_Cover_Dark_v01
KT_BenchmarkBoard_Light_v01
KT_BenchmarkBoard_Dark_v01
KT_Banner_4x5_Light_v01
KT_Banner_4x5_Clean_v01
```

## Figma Handoff Prompt

```text
Build a premium Hebrew RTL Figma slide system for PRIME / King Tamar. Use Heebo, right alignment, PRIME colors, clean cards, institutional whitespace, subtle circular trust motifs and matched Light/Dark variants. All Hebrew must be live text, not image text. Create both full copy and clean placeholder versions.
```
