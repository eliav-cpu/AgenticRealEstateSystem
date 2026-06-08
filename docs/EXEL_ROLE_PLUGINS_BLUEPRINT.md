# EXEL Role Plugins Blueprint

## Status
Working Draft / Reusable Architecture Reference

## Purpose
This document captures the reusable architecture idea learned from OpenAI's `role-specific-plugins` repository and adapts it as a strategic blueprint for EXEL.

EXEL should not be structured only by tools such as CRM, Drive, spreadsheets, WhatsApp, or email. It should be structured by professional operating roles.

## Core Naming
Recommended system name:

**EXEL Role Plugins Blueprint**

Hebrew working name:

**תשתית תוספי התפקידים של EXEL**

## Strategic Principle
EXEL becomes a role-based real-estate operating system: each professional function has its own plugin, skills, workflow logic, source bindings, reusable assets, and governance rules.

## Proposed EXEL Role Plugins

### 1. EXEL Sales Agent
Responsible for lead handling, meeting preparation, follow-up, objection handling, pipeline review, proposal readiness, and sales-team guidance.

### 2. EXEL Deal Architect Agent
Responsible for deal analysis, contract review support, risk mapping, commercial structure, investor suitability, pricing logic, and decision support.

### 3. EXEL Analytics Agent
Responsible for Excel models, investment simulators, KPI dashboards, data validation, scenario analysis, source mapping, and QA checks.

### 4. EXEL Investor Presentation Agent
Responsible for investor decks, slide narratives, project storytelling, visual QA, meeting flow, and transition from presentation to simulator.

### 5. EXEL Marketing Agent
Responsible for landing pages, ads, banners, social responses, campaign copy, lead magnets, brand language, and funnel messaging.

### 6. EXEL Legal Translation Agent
Responsible for legal translation, clause explanation, bilingual agreement review, source-grounded wording, and legal-risk highlighting.

### 7. EXEL Client Journey Agent
Responsible for CRM stage logic, task triggers, WhatsApp/email sequences, emotional tagging, next actions, and handover between team members.

## Folder Concept
A future implementation can follow this pattern:

```text
plugins/
  exel-sales/
  exel-deal-architect/
  exel-analytics/
  exel-investor-presentation/
  exel-marketing/
  exel-legal-translation/
  exel-client-journey/
```

Each plugin should eventually include:

```text
.codex-plugin/plugin.json
.app.json
skills/
assets/
README.md
source-rules.md
governance.md
```

## Commercial Use
This blueprint supports EXEL's positioning as:

**פלטפורמה לבחינה, השבחה ושיווק עסקאות נדל״ן נבחרות**

Official slogan:

**נדל״ן שנבדק**

## Next Action
Use this as the architecture layer for building EXEL's internal AI operating system and future role-specific assistants.
