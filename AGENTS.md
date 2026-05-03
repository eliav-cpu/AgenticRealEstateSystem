# AGENTS.md — PRIME / King Tamar Operating Rules

## Purpose
This repository is the master operating layer for PRIME / King Tamar. Every agent, GPT, Codex session, NotebookLM workflow, image workflow, slide workflow, Excel workflow or automation must load this file first.

## Core Rule
Do not build a warehouse of tools. Build a production line.

## Production Line
Every task must move through this sequence:

```text
request -> source/DNA extraction -> prompt refinement -> prompt compression -> output -> QA -> final deliverable
```

No task should stop at critique. Audit first, then produce a usable prompt, layout, copy, file, checklist or workflow.

## Source of Truth Hierarchy
1. `docs/source-of-truth/King_Tamar_Client_Copy_V6.md` — client-facing slide screen copy only.
2. `docs/source-of-truth/King_Tamar_Sales_Playbook_V6.md` — internal salesperson guide only.
3. `KING-TAMAR-DNA-OPERATING-MODEL.md` — master production and DNA rules.
4. `KING-TAMAR-SYNC-MANIFEST.md` — cross-chat and cross-repo synchronization manifest.
5. `docs/source-of-truth/PRIME_Visual_DNA.md` — visual and brand system.

If an older prompt, old slide, old wording or previous chat conflicts with the V6 source files, the V6 files win.

## Mandatory Separation Rule
Client Copy V6 goes into the client slide.
Sales Playbook V6 stays in the internal guide.

Never put the following on client-facing slides:
- salesperson scripts
- long explanations
- psychology
- objection handling
- internal notes
- source-validation notes
- team training
- legal/commercial verification comments

## Screen Copy Rule
Client slide copy must be:
- Hebrew-first
- RTL
- right-aligned
- short
- premium
- clear in 3 seconds
- investor-facing
- value/proof/action oriented

The slide structure is normally:
- decision headline
- short subtitle
- 3–4 concise cards
- optional message line only if it adds real screen value
- IMAGE_EDIT_PROMPT

## Sales Playbook Rule
Sales Playbook content may include:
- what the salesperson says
- meeting flow
- questions
- objections
- Excel transition
- apartment selection
- reservation language
- allowed/forbidden wording
- customer agreement steps

This content must not be merged into the slide screen.

## Language Rule
Use simple, modern, premium, classic Hebrew for Israeli investors.
Avoid heavy consultant language, including:
- פוזיציה
- סקייל
- סטייל
- מיקרו־לוקיישן
- מערכת החלטה
- overly advisory or research-style titles

Do not start headlines with negative constructions such as:
- לא עוד
- לא רק
- לא מתחילים
- לא קונים

## Commercial Safety Rule
Never invent numbers, legal claims, financial claims, market facts, regulatory statements, delivery certainty or guaranteed returns.

Forbidden language:
- תשואה מובטחת
- עליית ערך ודאית
- ללא סיכון
- רווח בטוח
- כסף קל
- PRIME מבטיחה תשואה

Preferred language:
- צפי
- פוטנציאל
- תרחיש עבודה
- לפי חומרי הפרויקט
- בכפוף לבדיקה
- דורש אימות
- בדיקה באקסל לפי יחידה

Every numeric, financial, regulatory or commercial claim must be source-checked before client use. If no source exists, mark: `דורש אימות`.

## Visual DNA Rule
All PRIME / King Tamar visual outputs must follow:
- RTL Hebrew
- Heebo-style typography
- zero typography errors
- large clear headings
- no fake Hebrew letters
- no smeared text
- no generic Canva look
- no loud blue
- Champagne only as a restrained accent
- do not alter faces of real people

Official colors:
- PRIME Navy `#0F1E3A`
- Deep Blue `#2F63C8`
- CTA Blue `#4D8DF7`
- White `#FFFFFF`
- Cloud `#FAFAFB`
- Mist Gray `#F3F4F6`
- Graphite `#111827`
- Steel Gray `#6B7280`
- Champagne Sand `#D6C7A1`

## Dual Colorway Rule
For every strategic slide, prepare or specify two matched versions:
1. Light: white/cloud/mist base, navy typography, controlled blue/champagne accents.
2. Dark: navy/graphite base, white typography, restrained champagne accents.

Both versions must keep the same structure, hierarchy, order and message. Only the color atmosphere changes.

## Uploaded Slide Workflow
When a King Tamar slide is uploaded for the new variation:
1. Identify what the slide is and where it belongs in the approved 16-slide flow.
2. Provide exactly two headline options:
   - סיפורי־יוקרתי
   - ברור־מכירתי
3. Choose the recommended client-facing headline.
4. Correct the existing slide copy according to Client Copy V6.
5. Ask how to continue: Light / Dark / Hybrid, with text / clean version.
6. Do not decide alone whether to keep or remove all existing small text; ask the user.
7. Titles are always strengthened and reorganized.
8. Every final slide should have:
   - version with title/text
   - clean version without final title/text but with the same layout zones

## Fast-Lane Defaults
When the user asks to move fast:
- use existing source files first
- reuse approved wording
- do not re-explain the full framework
- produce copy/prompt/layout immediately
- run a short QA checklist before delivery
- only ask a question when it blocks execution

## Final QA Before Delivery
Before delivering anything, verify:
- Is this Client Copy or Sales Playbook?
- Is it RTL Hebrew?
- Is the headline clear in 3 seconds?
- Are there any invented claims?
- Are numbers marked with sources or `דורש אימות`?
- Does it fit PRIME / King Tamar DNA?
- Is the output useful immediately?

## Enforcement Line
שים לב: שני מסמכי V6 הם מקור האמת. Client Copy V6 קובע מה נכנס לשקף. Sales Playbook V6 קובע מה המשווק אומר. אין לערבב בין מסך לבין מדריך פנימי.
