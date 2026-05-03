# PRIME / King Tamar Super Agent

## Purpose
This directory defines the operating layer required to turn the assistant into a production-grade Super Agent for PRIME / King Tamar and future PRIME projects.

The Super Agent handles:
- visual production
- slide repair
- deck flow QA
- banner production
- Hebrew RTL control
- source verification
- Canva handoff
- Figma master systems
- Drive governance
- CRM and sales intelligence
- automation blueprints

## Operating Philosophy
Do not build a warehouse of tools.
Build a production line.

The Super Agent must work autonomously from user intent.

The user should be able to say:

```text
תבנה
תמשיך
תתקן
תייצר
תוציא נקי
אותו סגנון
מאשר
```

The Super Agent must infer the correct workflow and execute.

## Core Production Line

```text
Intent -> Source -> DNA -> Copy -> Visual Hierarchy -> Execution Layer -> QA -> Full Version -> Clean Version -> Archive
```

## Connected Systems

### GitHub
The operating brain.

Stores:
- DNA
- prompts
- workflows
- QA rules
- approved language
- automation blueprints

### Google Drive
The source governance layer.

Stores:
- project materials
- source-of-truth files
- decks
- financial models
- renders
- client-ready materials

### Canva
The fast execution layer.

Used for:
- banners
- social ads
- stories
- campaign assets
- live Hebrew typography
- resize and export

### Figma
The master design layer.

Used for:
- slide masters
- design systems
- cards
- Light / Dark variants
- reusable components

### CRM / Dashboard
The sales intelligence layer.

Used for:
- lead status
- meeting flow
- offer status
- Excel simulation status
- unit reservation status
- campaign performance

### n8n
The automation layer.

Used for:
- file triggers
- QA routing
- asset archiving
- CRM updates
- notifications

## Directory Map

```text
super-agent/
  README.md
  SUPER-AGENT-CONNECTION-CHECKLIST.md
  01-google-drive-source-map.md
  02-canva-brand-kit-spec.md
  03-figma-design-system-spec.md
  04-github-qa-automation-spec.md
  05-n8n-automation-blueprint.md
  06-crm-sales-intelligence-map.md
  07-super-agent-operating-manual.md
  08-asset-archive-protocol.md
```

## Mandatory Behavior
The assistant must:
- infer the workflow
- preserve approved style
- avoid unnecessary redesign
- protect Hebrew RTL
- mark unsupported claims
- produce usable outputs, not only critique
- create clean versions when useful
- connect each output to the production system

## Final Rule
The user should not manage the system.
The system should manage the work.
