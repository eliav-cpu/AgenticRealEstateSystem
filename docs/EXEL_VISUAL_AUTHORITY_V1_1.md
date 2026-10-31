# EXEL visual authority and integration — V1.1

Status: Review — repository synchronization proposal, not a deployment certificate.
Source: owner instruction of 2026-10-31 and [canonical skill](../skills/exel-institutional-royal-slides/SKILL.md), verified at commit `2481857de2fc95f0fd700f4baeec3c2ce47f51e8`, original blob `5698c35f29828b87ff3d8c418ec6ea3db4b0dede`.

## Authority and scope
The canonical skill governs EXEL identity, color and visual restraint across presentation, visual, repair, image-edit, editorial/X Magazine, mobile/X Mobile and QA workflows. Workflow documents retain their format and source discipline, not their superseded visual defaults. Active brand: **EXEL נדל״ן | חוכמת הנדל״ן**. PRIME references in historical content are not active branding. Do not imply EXEL is a bank, regulated financial institution or guaranteed-return provider.

## Approved tokens
- Institutional Navy `#0A1E3F`
- EXEL Blue `#0066FF`
- Silver Gray `#D8DADD`
- Pearl Gray `#F3F4F5`
- Pure White `#FFFFFF`
- Royal Champagne `#B7A47D`
- Supporting Graphite `#394452`

Conceptual balance, excluding photographs: navy 24%, blue 12%, silver 18%, pearl 24%, white 20%, champagne 2%. Not a pixel quota. This replaces 70/20/10 and every older palette. Blue is visible but controlled; champagne is tiny, matte and optional. Use light balanced surfaces, navy titles and uniform blue icons. Do not recolor photographs or faces to satisfy ratios.

## Conflict resolution
- Editorial Light/Hybrid Photo are source-led defaults. Executive Dark is exceptional, never an automatically required second version. Historical dark masters remain references, not mandatory output.
- Cards, rings, seals, badges, lines and footers are optional according to source/content. Older mandatory motifs/card counts/QA points do not authorize adding decoration. No shiny gold, glow, heavy effects or fabricated imagery.
- For an existing slide, use the composition contract and [current QA skill](../skills/exel-visual-slide-qa/SKILL.md). Never silently redesign or remove approved icons.
- **PALETTE_ONLY:** lock composition, wording, reading order, images, people, logos, icons, proportions and text editability. Only specified colors change; no automatic copy correction, two-headline output, icon deletion, photo replacement or geometry changes. An old instruction to preserve colors does not cancel explicit owner recoloring authorization. Log out-of-scope issues instead of changing them.
- Use Heebo and true RTL including ordering; image model handles visual layers and a controlled PPT/typography layer handles final editable text. Preserve original project photos and real faces.
- King Tamar source copy, facts and 16-slide/other project flow do not apply to Wyndham unless explicitly adopted. Preserve approved project truth; this migration is not approval of any historical commercial claim.
- Historical approved repairs, dated assessments, source logs and copy banks remain untouched. Do not copy their legacy palette, branding or decorations into new EXEL work.

## Workflow mapping
| Requested function | Existing repository implementation |
|---|---|
| EXEL Presentation OS | `brand-presentation-os/`, `docs/PRESENTATION_PRODUCTION_PROTOCOL.md`, investor-presentation plugin README |
| EXEL Visual OS | `visual-production-system/README.md`, `00-auto-pilot-router.md` |
| EXEL Slide Repair | `visual-production-system/09-rapid-slide-repair-cycle.md`, corrective QA skill |
| EXEL Image Edit | `visual-production-system/02-image-slide-banner-workflow.md`, `04-agent-prompts.md` |
| X Magazine / X Mobile | Canonical skill section 6; banner/mobile workflow derivatives. No standalone SKILL.md found. |
| EXEL Visual QA | `skills/exel-visual-slide-qa/SKILL.md`, brand visual QA checklist |

Only two SKILL.md files exist in the checked complete repository tree. Named workflow coverage does not prove separate installed skills exist or were updated.

## Release and verification
Retain revisions through Git history; propose changes on an isolated branch/draft PR. Do not merge, deploy or claim system-wide synchronization without approval and independent checks of external runtimes/repos/templates. For the Wyndham trial: compare source vs recolored slide at equal scale, test color tokens and contrast, verify unchanged text/icons/assets/positions and editable PPT text, then obtain owner approval before wider rollout. No visual pilot result is asserted by this documentation change.
