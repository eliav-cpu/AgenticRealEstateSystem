# 06 - Canva Handoff

## Current EXEL authority — V1.1 (2026-10-31)

Read [the canonical EXEL skill](https://github.com/eliav-cpu/AgenticRealEstateSystem/blob/main/skills/exel-institutional-royal-slides/SKILL.md) and [the integration rules](https://github.com/eliav-cpu/AgenticRealEstateSystem/blob/main/docs/EXEL_VISUAL_AUTHORITY_V1_1.md) first. They override conflicting legacy brand/palette/ratio, forced components, automatic Light/Dark and repair instructions below. PRIME is historical context, not active EXEL branding. For **PALETTE_ONLY**, lock layout, copy, images, faces, logos, icons and editable text; change colors only. Project facts and flow remain project-specific. Prior versions are retained in Git history at `2481857`.

## Purpose
This file defines how to move from idea, prompt, image or slide direction into an editable Canva asset.

Canva is the preferred execution layer for:
- Facebook banners
- Instagram posts
- stories
- campaign creatives
- quick client-facing visuals
- editable Hebrew layouts
- resizing assets into multiple formats

## Core Rule
Use Canva for final Hebrew typography and editable campaign assets.

For Hebrew-heavy visuals, do not rely on image-model text. Generate the visual background or composition first, then add Hebrew as live text in Canva.

## Canva Production Flow

```text
1. Define asset type
2. Define ratio
3. Define copy
4. Define visual hierarchy
5. Create or import design
6. Add live Hebrew typography
7. Apply PRIME colors
8. Run mobile readability QA
9. Export full version
10. Export clean version
```

## Supported Asset Ratios

### Facebook / Instagram Feed
```text
4:5 vertical
1080 x 1350
```

### Story / Reel Cover
```text
9:16 vertical
1080 x 1920
```

### Presentation Slide
```text
16:9 horizontal
1920 x 1080
```

### Square Post
```text
1:1 square
1080 x 1080
```

## Canva Text Rules

### Hebrew Typography
- Use Heebo when available.
- Align all Hebrew text to the right.
- Keep titles large and readable on mobile.
- Avoid long paragraphs.
- Use no more than 3 font weights in one asset.
- Keep line spacing generous.

### Text Hierarchy
Recommended banner hierarchy:

```text
1. Main number or main claim
2. Value sentence
3. Proof / trust point
4. Logo or seal
5. CTA
```

Recommended slide hierarchy:

```text
1. Decision headline
2. Short subtitle
3. 3-4 cards
4. Bottom message line
```

## PRIME Canva Color Rules

Use:
- Institutional Navy `#0A1E3F`
- EXEL Blue `#0066FF`
- Silver Gray `#D8DADD`
- Pearl Gray `#F3F4F5`
- Pure White `#FFFFFF`
- Royal Champagne `#B7A47D`
- Supporting Graphite `#394452`

Avoid:
- neon blue
- shiny gold
- loud gradients
- aggressive red unless required for warning
- generic Canva template colors

## Banner Handoff Template

Use this when preparing a banner for Canva:

```text
Asset type:
Ratio:
Campaign:
Audience:
Main headline:
Supporting line:
Value points:
CTA:
Logo placement:
Seal placement:
Image direction:
Background direction:
Color system:
Typography rules:
Clean version needed: yes/no
```

## Example - Real Estate Lead Banner

```text
Asset type: Facebook / Instagram feed banner
Ratio: 4:5
Campaign: King Tamar investor lead generation
Audience: Israeli investors
Main headline: כ-60,000 ש״ח בשנה
Supporting line: הכנסה צפויה מנכס פרימיום בטביליסי, בירת גאורגיה
Value points:
- החל מהון עצמי של כ-100,000 ש״ח
- אפשרות למימון בנקאי בערבות בנקאית
- בדיקת התאמה אישית לפני החלטה
CTA: בדוק התאמה להשקעה
Logo placement: bottom area, small and controlled
Seal placement: under logo, diagonal and elegant
Image direction: real project image, slightly lower, not dominant over headline
Background direction: clean premium light background
Color system: Institutional Navy, White, Pearl Gray, controlled EXEL Blue, subtle Champagne
Typography rules: Heebo, RTL, sharp, large headline, mobile-readable
Clean version needed: yes
```

## Existing Banner Repair Instruction

```text
Keep the same banner design, same color palette and same overall composition. Do not redesign from scratch. Apply only the requested changes: text correction, hierarchy, font size, logo placement, seal placement, CTA and minor image crop. Preserve the original premium direction.
```

## Canva QA Checklist

Before export, check:
- Is the main headline dominant?
- Is the CTA visible on mobile?
- Is Hebrew right-aligned?
- Is the logo controlled and not oversized?
- Is the seal elegant and not misleading?
- Are value points short?
- Is there enough whitespace?
- Is the asset not too busy?
- Is there a clean version?

## Clean Version Rule
Every important Canva creative should have a clean version:
- same background
- same image position
- same empty card areas
- same logo area if needed
- no final text or only neutral placeholders

## Final Export Naming
Use this naming format:

```text
project_asset_campaign_ratio_version_date
```

Example:
```text
king-tamar_banner_leadgen_4x5_light_v01
king-tamar_banner_leadgen_4x5_clean_v01
```
