# Daily King Tamar Production Workflow

## Purpose
A fast daily operating flow for PRIME / King Tamar production across ChatGPT, Gemini, Claude, GitHub, visual tools and Excel.

## Daily Rule
Work as a production line, not as scattered chats.

```text
intake -> source check -> copy -> visual -> QA -> final asset -> reusable knowledge
```

## 10-Minute Daily Startup

### 1. Activate DNA
Use this command in every active chat/tool:

```text
פעל לפי King Tamar DNA: אפס טעויות טיפוגרפיה, RTL עברית, שני וריאנטים זהים Light/Dark, אין המצאת נתונים, אין הבטחות תשואה, וכל תוצר עובר QA לפני מסירה.
```

### 2. Select Workstream
Choose one:
- Slide repair
- New slide production
- Source verification
- Gemini research
- Claude playbook polish
- Excel / simulator correction
- Banner / image asset
- QA / proofreading

### 3. Open GitHub Issue
Use the relevant template:
- `slide-production.yml`
- `source-verification.yml`

### 4. Attach Source Basis
Every issue must define:
- which V6 source controls it
- whether it is client screen copy or sales playbook material
- which data requires verification
- what final output is needed

## Slide Repair Fast Lane

When a slide is uploaded:

1. Identify the slide role in the 16-slide flow.
2. Provide two title options:
   - סיפורי־יוקרתי
   - ברור־מכירתי
3. Choose one recommended title.
4. Correct screen copy using Client Copy V6.
5. Ask user for Light / Dark / Hybrid and text / clean version.
6. Produce IMAGE_EDIT_PROMPT.
7. Run QA.
8. Save reusable copy/prompt when strong.

## Gemini Research Fast Lane

Use Gemini only for external source work.

Input to Gemini:
```text
Topic:
Research question:
Required source type:
Target use:
Return Source Log only. Do not write client slide copy.
```

Output from Gemini must return:
- verified sources
- client-safe claims
- internal-only claims
- claims requiring verification
- source-log entry

## Claude Polish Fast Lane

Use Claude for internal depth only.

Input to Claude:
```text
Task:
Source basis:
Target internal document:
Preserve:
Improve:
Forbidden:
```

Claude output must return:
- revised internal guide text
- conflicts with screen copy
- claims requiring verification
- suggested Sales Playbook updates
- QA notes

## ChatGPT Final Production Lane

ChatGPT receives Gemini/Claude outputs and produces:
- final screen copy
- IMAGE_EDIT_PROMPT
- QA summary
- source flags
- next production action

## File Discipline

Store outputs in:

```text
outputs/gemini/
outputs/claude/
outputs/final/
outputs/slides/
outputs/source-log/
```

Store reusable prompts in:

```text
prompts/
```

Store QA standards in:

```text
qa/
```

## Done Definition
A task is complete only when:
- source layer is identified
- screen/internal separation is respected
- Hebrew RTL is correct
- no invented claims exist
- unverified data is marked `דורש אימות`
- visual prompt follows PRIME DNA
- output is ready for immediate use

## Daily Closing
At the end of each working block, save strong outputs as:
- approved copy
- prompt template
- source-log entry
- QA note
- FAQ answer
- slide example

## One-Line Operating Law
Every good output becomes reusable infrastructure.
