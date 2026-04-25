# PPT Master Visual Assessment for PRIME / King Tamar

Status: Working
Date: 2026-04-25
Scope: Assess whether `eliav-cpu/ppt-master` can improve PRIME / King Tamar presentation visual output

## Executive conclusion

`ppt-master` can improve the production layer significantly, but it is not enough by itself to solve the final visual quality gap.

The correct use is not to rely on its existing templates as-is. The correct use is to create a dedicated PRIME / King Tamar template inside `ppt-master` and feed it the locked Brand Presentation DNA.

## Why it helps

1. It generates editable PowerPoint objects, not flat screenshots.
2. It uses an SVG-first pipeline, which is good for precise layout control.
3. It supports reusable layout templates.
4. It has a strict strategist-to-executor workflow.
5. It has existing consulting, finance and executive templates that can inspire structure.

## Why it does not solve everything

1. The project itself states that generated PPTX is a design draft, not a final polished product.
2. Existing templates do not match PRIME DNA exactly.
3. The final result still depends on our design spec, taste, typography, spacing and slide master rules.
4. Without a custom PRIME template, output may look generic consulting or tech-business rather than PRIME.

## Recommended approach

Create a new global template in `ppt-master`:

Template ID: `prime_invest_platinum`
Display name: `PRIME Invest Platinum`
Category: `brand`
Canvas: `ppt169`
Tone: institutional, premium, calm, data-driven, human, private-banking standard
Theme: hybrid - Authority Dark, Strategic Light Board, Premium Photo Narrative

## Required master slides

1. Cover
2. Chapter divider
3. Strategic Light Board
4. KPI Grid
5. Trust Split Screen
6. Location Board
7. Comparison Board
8. Process / Timeline
9. FAQ / Risk Board
10. CTA / Excel Transition

## Decision

Use `ppt-master` as the execution engine, not as the brand brain.

The brand brain remains:
`brand-presentation-os/`

The visual execution engine can become:
`ppt-master/skills/ppt-master/templates/layouts/prime_invest_platinum/`

## Next step

Build one PRIME custom template with 4-5 SVG master files first. Then generate one King Tamar master slide from it. Only after the master slide reaches the desired standard should a full deck be produced.
