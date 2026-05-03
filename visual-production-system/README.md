# PRIME / King Tamar Visual Production System

## Purpose
This folder defines the production line for creating, auditing and improving visual assets for PRIME / King Tamar and related real-estate brands.

It covers:
- investor presentation slides
- Facebook / Instagram banners
- vertical story creatives
- clean slide templates
- image-generation prompts
- Hebrew / RTL QA
- visual quality checks
- Canva / Figma handoff logic

## Core Principle
Do not build a warehouse of tools. Build a production line.

The production line is:

```text
Source / DNA -> Prompt Builder -> Image / Layout Generation -> Visual QA -> Hebrew RTL QA -> Final Output -> Clean Version -> Reusable Template
```

## Why This System Exists
The current pain points are clear:
- generated Hebrew becomes blurry, reversed or broken
- slides look visually nice but miss investor decision logic
- banners change too much instead of applying targeted corrections
- Light / Dark versions drift away from the same structure
- visual outputs become decorative instead of commercial
- prompts are not always compressed into clear model instructions

This system solves that by separating every asset into six layers:
1. Source basis
2. Business message
3. Screen copy
4. Visual hierarchy
5. Hebrew / RTL QA
6. Final production prompt

## Mandatory Output Standard
Every client-facing visual must pass these gates:
- Hebrew text is live, readable and right-aligned when possible
- no broken RTL
- no blurry generated typography
- no invented data
- no guaranteed-return language
- no random decorative luxury
- PRIME colors only
- cards are used as decision units
- the slide or banner is understood within 3 seconds

## Active Brand Rules
Use the active King Tamar sync manifest and DNA system as the source of truth.

Main visual rules:
- Heebo typography
- PRIME Navy #0F1E3A
- Deep Blue #2F63C8
- CTA Blue #4D8DF7
- White #FFFFFF
- Cloud #FAFAFB
- Mist Gray #F3F4F6
- Graphite #111827
- Steel Gray #6B7280
- Champagne Sand #D6C7A1

Default ratio:
```text
70% light base / 20% navy or graphite / 10% blue or champagne accent
```

## Folder Map

```text
visual-production-system/
  README.md
  01-setup-map.md
  02-image-slide-banner-workflow.md
  03-hebrew-rtl-qa.md
  04-agent-prompts.md
  05-tool-connection-map.md
```

## Operating Rule
For Hebrew-heavy outputs, prefer this method:

```text
Generate visual/background first -> add Hebrew text in Canva/Figma/Slides as controlled live text
```

This avoids fake Hebrew typography and keeps the final asset professional.

## Short Command
Use this command in any working chat:

```text
פעל לפי Visual Production System: מקור -> מסר -> פרומפט -> יצירה -> QA ויזואלי -> QA עברית RTL -> גרסה סופית -> גרסה נקייה. אל תמציא נתונים. אל תשבור עברית. אל תשנה עיצוב קיים מעבר למה שהתבקש.
```
