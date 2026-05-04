# 04 - GitHub QA Automation Spec

## Purpose
GitHub is the operating brain and quality gate for the Super Agent.

This file defines the QA automation layer that should run before content is treated as client-ready.

## Core Rule
A file can exist in the repo without being client-ready. Client-ready status requires QA.

## QA Categories

### 1. Commercial Safety QA
Flag risky words:
- guaranteed
- zero risk
- certain return
- guaranteed return
- certain appreciation
- no competition

Hebrew terms to flag:
- מובטח
- ודאי
- ללא סיכון
- תשואה מובטחת
- עליית ערך ודאית
- אין תחרות

### 2. Data Claim QA
Flag claims requiring verification:
- yield
- price
- appreciation
- delivery date
- bank guarantee
- tax claim
- residency / permit claim
- legal claim
- market ranking
- rental forecast

### 3. Hebrew RTL QA
Flag:
- broken Hebrew
- mixed direction issues
- left aligned Hebrew notes
- unclear typography instructions
- missing RTL requirement in visual prompts

### 4. Source Governance QA
Check whether important files mention:
- source basis
- status
- version
- verification requirement
- final / draft classification

### 5. Visual Production QA
Check whether visual tasks include:
- full version
- clean version when relevant
- Light / Dark version when strategic
- Canva or Figma handoff when needed
- QA checklist

## Recommended GitHub Actions

### Action 1 - Text Safety Check
Runs on markdown files.

Checks:
- forbidden words
- risky claims
- missing verification tags

### Action 2 - Structure Check
Runs on key folders.

Checks that required files exist:
```text
visual-production-system/00-auto-pilot-router.md
visual-production-system/README.md
super-agent/README.md
super-agent/SUPER-AGENT-CONNECTION-CHECKLIST.md
```

### Action 3 - Prompt QA Check
Runs on prompt banks.

Checks:
- no final-heavy Hebrew instruction for image model when avoidable
- includes clean version rules
- includes RTL rules
- includes no invented data rule

## Suggested Labels

```text
qa-pass
qa-needs-review
source-needed
client-ready
working-draft
visual-system
hebrew-rtl
commercial-risk
```

## Manual QA Output

```text
QA Status: Pass / Needs Review / Failed
Risk Level: Low / Medium / High
Files Checked:
Issues Found:
Required Fixes:
Client Ready: Yes / No
```

## Future Automation Files
Suggested later:

```text
.github/workflows/super-agent-qa.yml
scripts/qa/forbidden_words_check.py
scripts/qa/source_status_check.py
scripts/qa/prompt_structure_check.py
```

## Rule
GitHub should not only store the system. It should protect the system.
