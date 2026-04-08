# ex-el-agent-core

A distilled adaptation of the strongest architectural ideas from Ori CLI, rebuilt for the ex-el operating model.

This package is not a clone of Ori CLI.
It is a selective extraction of reusable patterns:

- persistent agent memory
- repo and workspace structural mapping
- phase-gated tool exposure
- multi-model routing
- execution body for computational reasoning
- project-local memory
- context compaction and warm context refresh

## What this package is for

ex-el needs an agent core that can sit between fragmented sources of truth:

- CRM status and workflow
- spreadsheets for pricing, models, assumptions, simulations, and proposals
- Drive files for contracts, docs, decks, and approved outputs
- email and WhatsApp style context for objections, emotional signals, and live deal motion

The goal is not to create a generic coding assistant.
The goal is to create an operational intelligence layer for real estate, investment, proposal, and workflow systems.

## What we kept from Ori CLI

### 1. Persistent memory
A durable memory layer that survives sessions and carries forward identity, decisions, project context, and reusable patterns.

### 2. Execution body
A persistent execution surface where the agent can compute, inspect structure, run ranking logic, and work on normalized workspace state without wasting turns narrating every micro-step.

### 3. Structural mapping
A graph-oriented view of the workspace so the agent can understand which artifacts are central, which are dependent, and where new logic belongs.

### 4. Phase-gated tools
A lean tool set by default, widened only when needed, to reduce noise and token drag.

### 5. Multi-model slots
Dedicated models for primary interaction, heavy reasoning, cheap synthesis, and batch or sub-agent work.

### 6. Warm context
A compact continuity layer injected into every turn so the agent preserves identity and current priorities even after compaction.

## What we changed for ex-el

### 1. Workspace-first instead of repo-first
Ori is optimized for codebases. ex-el must reason across business artifacts, not just source code.

### 2. Spreadsheet and proposal intelligence
The central object is not only code. It is also:
- inventory
- unit pricing
- payment models
- assumptions
- proposal outputs
- scenario engines
- dashboards

### 3. Governance and certainty
ex-el must classify source quality and output confidence before generating client-facing content.

### 4. Commercial workflow awareness
The system must understand lead stage, meeting stage, proposal state, objections, blockers, and next actions.

### 5. Memory taxonomy aligned to operations
Memory should be split into:
- institutional memory
- project memory
- client-pattern memory
- approved language and clause bank
- temporary operational state

## Package layout

```text
packages/ex-el-agent-core/
├── docs/
│   └── adaptation-map.md
├── src/
│   ├── agent/
│   │   ├── core.ts
│   │   ├── memory.ts
│   │   └── repo-map.ts
│   ├── config.ts
│   ├── index.ts
│   └── types.ts
├── package.json
└── tsconfig.json
```

## Recommended next layer

After this core, the next modules should be built outside this package:

1. `ex-el-connectors`
   - CRM adapter
   - Google Sheets adapter
   - Drive adapter
   - Gmail adapter
   - WhatsApp ingestion layer

2. `ex-el-governance`
   - source classification
   - confidence scoring
   - client-output guardrails

3. `ex-el-proposal-engine`
   - unit selection
   - payment model engine
   - proposal document generation
   - scenario pack generation

4. `ex-el-workspace-api`
   - normalized entities
   - search surface
   - event bus
   - audit logging

## Status

This is a distilled architectural starter, not a finished application.
It is designed to become the kernel for a larger ex-el platform.
