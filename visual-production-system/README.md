# PRIME / King Tamar Visual Production System

## Current EXEL authority — V1.1 (2026-10-31)

Read [the canonical EXEL skill](https://github.com/eliav-cpu/AgenticRealEstateSystem/blob/main/skills/exel-institutional-royal-slides/SKILL.md) and [the integration rules](https://github.com/eliav-cpu/AgenticRealEstateSystem/blob/main/docs/EXEL_VISUAL_AUTHORITY_V1_1.md) first. They override conflicting legacy brand/palette/ratio, forced components, automatic Light/Dark and repair instructions below. PRIME is historical context, not active EXEL branding. For **PALETTE_ONLY**, lock layout, copy, images, faces, logos, icons and editable text; change colors only. Project facts and flow remain project-specific. Prior versions are retained in Git history at `2481857`.

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
- autonomous task routing

## Core Principle
Do not build a warehouse of tools. Build a production line.

The production line is:

```text
Source / DNA -> Prompt Builder -> Image / Layout Generation -> Visual QA -> Hebrew RTL QA -> Final Output -> Clean Version -> Reusable Template
```

## Auto Pilot Rule
The user should not need to paste production instructions every time.

The assistant must infer the correct production mode from the user request, uploaded asset and active project context.

If the user says:

```text
תבנה
תמשיך
תייצר
תקן
תשפר
אותו דבר
תוציא נקי
מאשר
כן
```

The assistant must classify the task and continue automatically.

Default routing:
- uploaded slide -> Existing Slide Repair Mode
- uploaded banner -> Existing Banner Repair Mode
- new banner request -> Banner Creation Mode
- new slide request -> New Slide Creation Mode
- full deck request -> Deck Audit / Flow Repair Mode
- Canva request -> Canva Handoff Mode
- Figma request -> Figma Master System Mode
- image request -> Image Generation Prompt Mode

The active router file is:

```text
00-auto-pilot-router.md
```

## Why This System Exists
The current pain points are clear:
- generated Hebrew becomes blurry, reversed or broken
- slides look visually nice but miss investor decision logic
- banners change too much instead of applying targeted corrections
- Light / Dark versions drift away from the same structure
- visual outputs become decorative instead of commercial
- prompts are not always compressed into clear model instructions
- the user should not manually operate the workflow each time

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
- Institutional Navy `#0A1E3F`
- EXEL Blue `#0066FF`
- Silver Gray `#D8DADD`
- Pearl Gray `#F3F4F5`
- Pure White `#FFFFFF`
- Royal Champagne `#B7A47D`
- Supporting Graphite `#394452`

Default ratio:
```text
70% light base / 20% navy or graphite / 10% blue or champagne accent
```

## Folder Map

```text
visual-production-system/
  00-auto-pilot-router.md
  README.md
  01-setup-map.md
  02-image-slide-banner-workflow.md
  03-hebrew-rtl-qa.md
  04-agent-prompts.md
  05-tool-connection-map.md
  06-canva-handoff.md
  07-figma-master-slide-system.md
  08-banner-template-bank.md
```

## Operating Rule
For Hebrew-heavy outputs, prefer this method:

```text
Generate visual/background first -> add Hebrew text in Canva/Figma/Slides as controlled live text
```

This avoids fake Hebrew typography and keeps the final asset professional.

## Short Internal Operating Command
The assistant should silently operate by this rule:

```text
פעל לפי Visual Production System Auto Pilot: זהה לבד את סוג המשימה, בחר את מצב העבודה הנכון, שמור מה שעובד, תקן מה שצריך, הגן על עברית RTL, אל תמציא נתונים, אל תשנה עיצוב קיים מעבר למה שהתבקש, והפק גרסה מלאה וגרסה נקייה כשזה רלוונטי.
```

## Final Operating Line
The user should not operate the system.
The assistant should operate the system for the user.
