---
name: exel-institutional-royal-slides
description: EXEL נדל״ן presentation design standard for institutional, trustworthy, restrained premium RTL slides; governs visual creation and repair, including X Magazine and X Mobile derivatives.
version: 1.0-draft
status: proposed-for-owner-approval
---
# EXEL Institutional Royal — Presentation Design Skill

## 1. Brand identity
EXEL נדל״ן | חוכמת הנדל״ן. Brand promise language: רואים את כל העסקה. Never use PRIME Invest as active branding. Never imply EXEL is a bank, regulated financial institution, or guaranteed investment provider. Aim for institutional-grade visual trust, not imitation of a bank's legal status.

## 2. Visual north star
Royal restraint; institutional authority; truthfulness; clarity; stability; premium editorial precision. Strong typography and spacing carry the prestige. No AI-looking glow, futuristic corridors, floating marble pedestals, shiny metallic gradients, excess glassmorphism, invented architectural images, decorative crowns, or gratuitous badges.

## 3. Palette / design tokens
- Institutional Navy #0A1E3F — headings, selective header, high-contrast text.
- Pure White #FFFFFF — main paper/card surface.
- Pearl Gray #F3F4F5 — calm neutral page background.
- Silver Gray #D8DADD — hairline separators, quiet surfaces.
- Royal Champagne #B7A47D — 1px/2px rules, rare single accent, restrained icon treatment; matte, never glossy gold.
- EXEL Blue #0066FF — brand/action color, one focal emphasis per slide maximum.
- Supporting graphite #394452 — secondary text when necessary.
Color distribution for light information slides: white/pearl 70–85%, navy/graphite 10–25%, silver/champagne/blue combined 3–8%. These are recommended ranges, not pixel quotas. Large project photography is exempt from area calculation.
Do not use Champagne and vivid blue as competing focal accents. Choose one accent per slide; other may be near-invisible or absent. Silver is not chrome.

## 4. Typography and RTL
Hebrew font Heebo; H1 Bold 30–42 pt for 16:9; subtitle Medium 18–24 pt; card titles Medium/Bold 16–22 pt; body Regular 14–20 pt; footnotes >=10 pt when physically readable. Exact sizes adapt to content and device. Right-align Hebrew text; use true bidi isolation for English brands, prices, dates, %, €, $, phone numbers and mixed scripts. RTL governs component order, step direction, arrow direction, charts and reading flow, not only paragraph alignment. Do not ask image generators to render final Hebrew: generate/edit photographic/background layers separately and overlay editable Heebo typography via PPTX, Figma or Adobe.

## 5. Grid and composition
16:9 master, consistent 12-column grid, safe margins 4–6% of width, baseline spacing multiples of 8px (or equivalent). Choose one visual anchor, one primary message, one supporting region. Preserve existing source slide composition unless user explicitly requests a rebuild. Do not add panels, frames, badges, circles or footer ribbons without a functional reason. Cards are optional, not mandatory. Light shadows only when necessary. No synthetic 3D.
Modes:
- Editorial Light (default): white/pearl dominant, navy text, thin silver rules.
- Hybrid Photo (project/people): original licensed photograph or developer rendering + clean white/pearl text area, minimal navy.
- Executive Dark (rare): navy cover/section divider, white text, a single champagne accent.
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
5. Choose palette mode and ONE accent color.
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
"Produce a premium institutional EXEL real-estate investor slide, 16:9, with [approved content]. Mode [Editorial Light/Hybrid Photo/Executive Dark]. Preserve [locked images/logos/layout]. Use matte EXEL Navy #0A1E3F, White #FFFFFF, Pearl #F3F4F5, Silver #D8DADD, Royal Champagne #B7A47D sparingly and EXEL Blue #0066FF only for one active emphasis. Formal editorial grid, calm premium white space, no AI-glow, no shiny gold, no floating pedestals, no decorative clutter. Reserve clean zones for editable Heebo Hebrew RTL overlay. Do not invent claims, change actual faces, or fabricate project renderings."

## 11. Acceptance standard
An institutional slide should look credible without its logo. The strongest feature must be the clarity and integrity of the information, not a decorative effect. Verify real render output; a written skill is not proof of deployment.
