# Tool Role Matrix — PRIME / King Tamar

## Purpose
This file prevents tool overlap. Every system has a narrow role, source layer and output format.

## Master Rule
Do not let every system do everything.
Each tool must serve one part of the production line.

```text
Gemini -> sources
Claude -> internal depth and long-form polish
ChatGPT -> production coordination, final copy, QA, GitHub
Image/Canva tools -> visual execution only
Excel -> decision validation
GitHub -> operating memory and source control
```

## Tool Roles

| Tool | Primary Role | Allowed Output | Not Allowed |
|---|---|---|---|
| ChatGPT | Production manager, DNA keeper, final copy, QA, GitHub implementation | prompts, slide copy, QA, protocols, final structure | inventing data, ignoring V6 source hierarchy |
| Gemini Ultra | research and external source discovery | source log, source table, summaries, caveats | final slide copy, final sales language, unsupported claims |
| Claude | long-form writing and internal playbook polish | Sales Playbook sections, FAQ, objections, scripts, consistency review | uncontrolled slide copy, mixing internal guide into screen copy |
| Canva / Image tools | visual execution | design variations, visual layouts, clean/text versions | inventing content, changing strategy, changing real faces |
| Excel / Simulator | unit-level decision validation | price, payment track, finishing, cash-flow scenario, comparison | replacing the deck story, guaranteeing outcomes |
| GitHub | operating memory and source control | source files, prompts, QA, workflows, issues, templates | being a dumping ground without structure |

## Gemini Input Format
Send Gemini research tasks only.

```text
Research topic:
Research question:
Market / project context:
Required source types:
Date range:
Output format: Source Log table + verified claims + claims requiring verification.
```

## Gemini Output Format

```markdown
# Gemini Research Output
## Topic
## Research Question
## Executive Summary
## Verified Sources
## Claims Suitable For Client Use
## Claims For Internal Use Only
## Data Requiring Verification
## Risks / Caveats
## Suggested Slide Use
## Suggested Source-Log Entry
```

## Claude Input Format
Send Claude long internal-writing tasks only.

```text
Task:
Source basis:
Target document:
Tone:
What to preserve:
What to improve:
Forbidden content:
Output format:
```

## Claude Output Format

```markdown
# Claude Output
## Task
## Source Basis Used
## Main Improvements
## Revised Internal Text
## Screen Copy Conflicts Found
## Claims Requiring Verification
## Suggested Updates To Sales Playbook
## Suggested Updates To Client Copy, if any
## QA Notes
```

## ChatGPT Output Format
ChatGPT converts all inputs into production-ready artifacts:

```markdown
## Source basis
## Slide/category identification
## Recommended screen copy
## IMAGE_EDIT_PROMPT
## QA checklist
## Data requiring verification
## Next action
```

## No-Overlap Rule
If two tools produce conflicting outputs:
1. V6 source files win.
2. Source Log wins on data.
3. Client Copy V6 wins on screen copy.
4. Sales Playbook V6 wins on internal talk track.
5. ChatGPT resolves the final production decision.

## Fast Lane Rule
For speed, use the tool only where it is strongest:
- Need sources? Gemini.
- Need internal guide depth? Claude.
- Need final slide production? ChatGPT.
- Need visual execution? Canva/Image model.
- Need financial decision? Excel.
