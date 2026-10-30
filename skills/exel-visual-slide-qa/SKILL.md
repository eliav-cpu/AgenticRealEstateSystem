---
name: exel-visual-slide-qa
description: Controlled visual refinement of existing EXEL/PRIME/Wyndham/King Tamar slides; preserve layouts, approved photographs, identities and truthful Hebrew.
---
# EXEL Visual Slide OS — v1.0 (corrective layer)
Parent: EXEL Strategic Questioning & Execution OS. Load project-specific source of truth and current user's most recent design preference first.

## Intent classifier
- REPAIR: user's image exists and asks improve/sharpen/fix. Default: PRESERVE layout, images, number of sections, major proportions, identity, approved logo and style. Change only specified flaws. Never redesign.
- REDESIGN: only when user explicitly asks for a new layout, new style or total rebuilding.
- GENERATE: new slide from approved copy/visual references.
- TEXT_ONLY: modify copy in an editable text layer; no image regeneration unless asked.

## Design restraint rules
- If user says classic, clean, simpler, too many details: REDUCE. Remove extra lines, badges, cards, icons, decorative airport motifs and extra slogans.
- Never add an icon grid, fourth panel, bottom decorative banner, more captions or new promises merely to fill space.
- Never enforce 3–4 cards universally: executive portraits may use no cards; hero may use one sentence.
- Never enforce two colorways unless requested or a specific approved workflow requires both.
- For an existing slide, first preserve the image/layout and ensure the repair is visibly incremental.
- Do not replace real project renderings with generated alternatives and do not change the face of a real person. Use original supplied photo as a fixed asset; if it cannot be faithfully preserved, deliver a text/layout-only instruction rather than synthetic identity.
- Do not fabricate visual endorsements, logos, actual interiors or project facilities.

## Hebrew and source integrity
- Hebrew is RTL/right aligned, Heebo when rendered in an editable deterministic layer.
- Image AI is a visual layer, never a reliable final Hebrew typography engine. Prefer image/background without letters + editable overlay.
- Compare final on-screen copy character-by-character with approved copy. Do not silently modify product claims or names.
- Claims not grounded in user-approved materials require verification, and must not be introduced as factual benefits.
- Source facts, product names, photographs and licensing are project-specific. King Tamar V6 rules do not govern Wyndham unless explicitly adopted for that project.

## Visual review gates (hard fail)
1. PRESERVATION: approved portrait/architecture/logo unaltered; layout drift limited to requested scope.
2. COMPOSITION: one focal point; balanced photo-to-copy ratio; sufficient whitespace.
3. REDUCTION: each visual element must justify its existence; remove ornamental clutter.
4. RTL: no reversed ordering, awkward English/Hebrew crossover or left aligned Hebrew.
5. TEXT: precise, legible, no artificial glyphs, overflow or invented slogans.
6. PROOF: no unsupported promises, project photos falsely presented as actual, or false labels.
7. DELIVERY: explain exactly what changed and what remains unverified. Do not claim full QA from visual inspection alone.

## Default Wyndham executive-profile layout
16:9, classic navy-and-white. Header with existing logos and short right-aligned section heading. Left ~55% original approved architectural montage (1 large visual plus up to 2 secondary photos); right ~45% original portrait, name/title, one short proof-led statement. No icon-grid, no gratuitous bottom ribbon, no invented spa/airport imagery. Footer: only one brief verified line if needed.

## Prompt sent to any image model
"Edit the existing slide, not create a different presentation. Preserve all supplied logos, photos and executive face as-is; keep original photographic content. Classic premium corporate navy-white look, restrained accents, whitespace, large readable headline and no decorative icon grid. Do not add facts, amenities, alternate renderings or text not in approved copy. If Hebrew rendering is unreliable, leave clean text zones for a separate editable RTL layer."

## Acceptance test
For any change, record:
- Mode REPAIR/REDESIGN/GENERATE/TEXT_ONLY.
- LOCKED elements.
- Allowed changes.
- Screenshot comparison result (if available).
- Copy/proof flags.
- Status: verified / partially verified / requires human review.


## Mandatory RTL composition gate — user-approved Wyndham reference
RTL is a **spatial reading system**, not just CSS direction or right alignment.
- Header logos must be arranged from RIGHT to LEFT in the exact approved sequence: X-only EXEL mark, D.Group mark, Wyndham Garden. Never substitute a full oversized EXEL wordmark.
- Preserve the original photo grid and its reading order. For the Wyndham facilities montage, start with the project tile on the right in reading order, followed by spa, lobby and restaurant according to the approved reference. Each caption is right aligned within its own tile.
- Treat the Hebrew title, subtitles, captions, footer and all labels as separate RTL regions; test each independently.
- English brand names and mixed strings must be isolated with Unicode bidi handling, not visually reversed.
- Never add panel borders, blue underlines, separators, footer ornaments, extra cards or background geometry unless specifically present in the approved reference or requested.
- For this slide: preserve original project rendering, spa, lobby, restaurant, and original portrait; avoid invented amenities and replacement images.
- Before image generation, write a COMPOSITION CONTRACT: exact regions, right-to-left order, locked assets, editable text zones, and allowed modifications.
- If a generated image violates even one locked region, mark QA_FAILED and do not present it as the finished slide.
- The screenshot must be compared against the original side by side at equal scale; assess direction, logos, tile order, borders, captions and text legibility.
