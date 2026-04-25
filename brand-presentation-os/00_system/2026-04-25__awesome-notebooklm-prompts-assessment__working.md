# Awesome NotebookLM Prompts Assessment

Status: Working
Date: 2026-04-25
Repository reviewed: serenakeyitan/awesome-notebookLM-prompts

## Executive decision

This repository is useful for PRIME, but not as a code tool.

It should be used as a prompt-pattern library for NotebookLM / Kael style generation and design-spec writing.

## What it gives us

1. Strong prompt structures for visual slide generation
2. Style definitions that include tone, palette, typography and layout rules
3. Useful language around one slide = one message
4. Useful layout families such as sharp minimalism, premium mockup, editorial business and grid-based design
5. A reminder that prompts should define design constraints, not just content

## What to take for PRIME

Take these patterns:

- strict design definition blocks
- prohibited output rules
- cover slide rules
- one slide = one message
- large headline hierarchy
- negative space discipline
- strict grid language
- premium mockup logic
- sharp-edged minimalism
- slide layout cataloging

## What not to take

Do not copy the pop, manga, street, neon or sports styles into PRIME.

These are visually strong, but too far from PRIME's institutional premium language.

## Best PRIME adaptation

Create a new prompt file:

`04_prompts/notebooklm/prime-invest-platinum-slide-style.md`

It should combine:

- PRIME color system
- Heebo typography
- Authority Dark / Strategic Light Board / Premium Photo Narrative
- Card System
- circular trust language
- one slide = one decision
- strict RTL Hebrew rules

## Relationship to other tools

Recommended stack:

1. `brand-presentation-os` - source of truth and DNA
2. `awesome-notebookLM-prompts` - prompt inspiration and design-spec syntax
3. `ppt-master` - visual SVG to PPTX execution engine
4. `Office-PowerPoint-MCP-Server` - PPTX editing and polish layer

## Decision

Use it.

Not by connecting it as infrastructure, but by extracting prompt architecture and creating PRIME-specific NotebookLM prompt templates.
