# 05 - Tool Connection Map

## Purpose
This file defines how the production system connects to the available tools.

The goal is not to use every tool.
The goal is to use the right tool at the right stage.

## Tool Matrix

| Stage | Primary Tool | Secondary Tool | Output |
|---|---|---|---|
| Source collection | Google Drive | GitHub | source files, decks, docs |
| DNA / rules | GitHub | ChatGPT | reusable rules |
| Copy correction | ChatGPT | Google Docs | approved text |
| Visual concept | GPT Image | Figma | visual direction |
| Layout system | Figma | Canva | editable master layout |
| Banner execution | Canva | GPT Image | campaign asset |
| Final Hebrew typography | Canva / Figma | Google Slides | live RTL text |
| QA | ChatGPT | GitHub checklist | approval or correction |
| Archive | GitHub / Drive | Canva | final source and export |

## Recommended Connection Logic

### GitHub First
Use GitHub before creative generation when the task depends on:
- PRIME DNA
- King Tamar rules
- approved language
- workflows
- prompt libraries
- QA checklists

### Google Drive First
Use Google Drive before creative generation when the task depends on:
- uploaded decks
- source project documents
- price lists
- sales materials
- existing presentations
- client files

### Canva First
Use Canva when the task is:
- social post
- banner
- story creative
- editable design
- resize
- brand template
- campaign asset

### Figma First
Use Figma when the task is:
- design system
- master slide layout
- reusable components
- exact layout control
- premium slide system
- comparison board
- card system

### GPT Image First
Use GPT Image when the task is:
- fast creative idea
- background generation
- visual direction
- atmospheric composition
- image edit
- concept variation

## Important Hebrew Rule
For Hebrew-heavy client assets:

```text
GPT Image creates the background and layout.
Canva / Figma creates the final Hebrew typography.
```

This prevents broken Hebrew and keeps control.

## Recommended Operating Modes

### Mode 1 - Quick Banner
Use when speed matters.

```text
Prompt -> GPT Image visual -> Canva final text -> QA -> export
```

### Mode 2 - Client Presentation Slide
Use when quality matters.

```text
Source -> copy compression -> Figma / Canva layout -> GPT Image only for visuals -> Hebrew live text -> QA -> clean version
```

### Mode 3 - Existing Asset Fix
Use when user liked the direction and wants a correction.

```text
Audit existing asset -> preserve style -> targeted prompt -> generate corrected version -> QA -> clean version
```

### Mode 4 - Reusable Template
Use when asset type repeats.

```text
Define template -> create Light / Dark master -> create placeholder version -> save copy rules -> save QA rules -> reuse
```

## Default Decision Rule

```text
If the asset contains important Hebrew: do not trust image text.
If the asset is mostly visual: GPT Image is acceptable.
If the asset must stay editable: use Canva or Figma.
If the asset is part of a system: document it in GitHub.
```

## Current Priority
Build the following reusable systems first:
1. King Tamar slide repair agent
2. banner repair agent
3. Hebrew RTL QA agent
4. GPT Image clean-layout prompt bank
5. Canva/Figma handoff templates
6. Light/Dark slide master rules

## Next Files To Add Later

```text
06-canva-handoff.md
07-figma-master-slide-system.md
08-banner-template-bank.md
09-slide-repair-checklist.md
10-clean-version-rules.md
```
