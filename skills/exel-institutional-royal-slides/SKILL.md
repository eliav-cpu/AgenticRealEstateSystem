---
name: exel-institutional-royal-slides
description: EXEL נדל״ן presentation design standard for institutional, trustworthy, restrained premium RTL slides; governs visual creation and repair, including X Magazine and X Mobile derivatives.
version: 1.1
status: approved-palette-2026-10-31
---
# EXEL Institutional Royal — Presentation Design Skill

## 1. Brand identity
EXEL נדל״ן | חוכמת הנדל״ן. Brand promise language: רואים את כל העסקה. Never use PRIME Invest as active branding. Never imply EXEL is a bank, regulated financial institution, or guaranteed investment provider. Aim for institutional-grade visual trust, not imitation of a bank's legal status.

## 2. Visual north star
Royal restraint; institutional authority; truthfulness; clarity; stability; premium editorial precision. Strong typography and spacing carry the prestige. No AI-looking glow, futuristic corridors, floating marble pedestals, shiny metallic gradients, excess glassmorphism, invented architectural images, decorative crowns, or gratuitous badges.

## 3. APPROVED palette — EXEL Modern Institutional Luxury V1.1 (owner-approved 2026-10-31)
This palette supersedes the earlier Institutional Royal color defaults for ALL new EXEL presentation work. Do not silently revert to an older champagne-dominant variant.
- Institutional Navy #0A1E3F — authoritative headlines, restrained header zones, important typography.
- EXEL Blue #0066FF — deliberate visible brand tone in unified line icons, one or two thin focal rules, or a single geometric transition. Not an entire glowing background.
- Silver Gray #D8DADD — restrained borders, separators, matte structural accents.
- Pearl Gray #F3F4F5 — quiet neutral backgrounds and supporting surfaces.
- Pure White #FFFFFF — cards, whitespace, content clarity.
- Royal Champagne #B7A47D — tiny warm accent only (typically <=2% of non-photographic visual area); matte, optional, never competing with blue.
- Supporting Graphite #394452 — secondary readable text.
Suggested *visual balance* for non-photographic design surfaces: Navy 24%, Blue 12%, Silver 18%, Pearl 24%, White 20%, Champagne 2%. These are conceptual proportions, not pixel quotas; image areas are excluded. Prioritize readability and restraint over exact ratios.
Blue must have a perceptible but controlled presence. Use a consistent blue icon family, not alternating gold and blue icons within one row. Champagne is warmth, not a second primary accent.
Reference direction: the final owner-approved Wyndham Garden lobby slide with a blue EXEL header tone, cool silver/white cards, calm blue line icons, a restrained blue edge, and a nearly imperceptible champagne touch.
Avoid: saturated blue gradients, excessive dark backgrounds, champagne frames on every card, glossy gold, AI glow, heavy 3D effects, excessive ornaments.
## 4. Typography and RTL
Hebrew font Heebo; H1 Bold 30–42 pt for 16:9; subtitle Medium 18–24 pt; card titles Medium/Bold 16–22 pt; body Regular 14–20 pt; footnotes >=10 pt when physically readable. Exact sizes adapt to content and device. Right-align Hebrew text; use true bidi isolation for English brands, prices, dates, %, €, $, phone numbers and mixed scripts. RTL governs component order, step direction, arrow direction, charts and reading flow, not only paragraph alignment. Do not ask image generators to render final Hebrew: generate/edit photographic/background layers separately and overlay editable Heebo typography via PPTX, Figma or Adobe.

## 5. Grid and composition
16:9 master, consistent 12-column grid, safe margins 4–6% of width, baseline spacing multiples of 8px (or equivalent). Choose one visual anchor, one primary message, one supporting region. Preserve existing source slide composition unless user explicitly requests a rebuild. Do not add panels, frames, badges, circles or footer ribbons without a functional reason. Cards are optional, not mandatory. Light shadows only when necessary. No synthetic 3D.
Modes:
- Editorial Light (default): white/pearl dominant, navy text, thin silver rules.
- Hybrid Photo (project/people): original licensed photograph or developer rendering + clean white/pearl text area, minimal navy.
- Executive Dark (rare): navy cover/section divider, white text, a restrained blue or optional champagne accent.
Do not generate multiple modes automatically unless asked.

## 6. Slide categories
- Executive / person: authentic approved portrait, short name and role, one verifiable trust statement.
- Architecture / project: one large original project rendering, short proof-led text; never invent hotel facades or amenities.
- Data / financial: editable tables, navy header, silver separators, no decorative backgrounds; verified numbers only.
- Process: 3–5 ordered stages, right-to-left; avoid unrelated icons.
- Editorial / X Magazine: large image, article hierarchy, evidence captions, controlled white space.
- X Mobile: vertical, large Hebrew typography, single message per screen, tap-friendly content, no tiny footnotes.
- Decision / CTA: one clear action, non-coercive, verifiable terms.

## 7. Image provenance
Never alter a real person's face or create a synthetic likeness as an official portrait. Do not replace approved official project renderings with AI alternatives. Record asset source, permission and whether it is a rendering, photograph or illustration. Generated imagery is illustration only and must not be misrepresented as documentary evidence.

## 8. Production workflow
1. Identify brand/project and current source of truth.
2. Classify REPAIR, REFINE, REBUILD, GENERATE or MULTI-OUTPUT.
3. Extract exact approved text and claims; mark unverified claims privately for QA.
4. Write composition contract: fixed elements, editable elements, reading order, image provenance.
5. Choose palette mode; EXEL Blue is the controlled principal accent, champagne only a tiny optional secondary warmth.
6. Build background/visual assets; overlay controlled Hebrew typography.
7. Export editable PPTX plus PNG preview; optional clean background without final text when requested.
8. Check at 100% and mobile size, compare to source and verify all content.
9. Present as DRAFT until QA and owner approval; never claim published/approved automatically.

## 9. Hard QA gates
- Correct EXEL identity, no PRIME branding.
- True RTL reading order and mixed-language correctness.
- Sharp, legible editable Hebrew; no smeared letters or clipping.
- No unsupported financial, regulatory, project or occupancy figures.
- No invented real-person portraits or project photographs.
- No unjustified glow, metallic effect, cards, borders or gradients.
- Color discipline, generous white space, one focal message.
- Distinguish verified facts, forecasts and illustrations.
- Any hard gate failure = QA_FAILED regardless of aesthetics.

## 10. Model prompt template
"Produce a premium institutional EXEL real-estate investor slide, 16:9, with [approved content]. Mode [Editorial Light/Hybrid Photo/Executive Dark]. Preserve [locked images/logos/layout]. Use matte EXEL Navy #0A1E3F, White #FFFFFF, Pearl #F3F4F5, Silver #D8DADD, EXEL Blue #0066FF as the controlled visible accent and Royal Champagne #B7A47D only as an optional tiny matte warmth detail. Formal editorial grid, calm premium white space, no AI-glow, no shiny gold, no floating pedestals, no decorative clutter. Reserve clean zones for editable Heebo Hebrew RTL overlay. Do not invent claims, change actual faces, or fabricate project renderings."

## 11. Acceptance standard
An institutional slide should look credible without its logo. The strongest feature must be the clarity and integrity of the information, not a decorative effect. Verify real render output; a written skill is not proof of deployment.
