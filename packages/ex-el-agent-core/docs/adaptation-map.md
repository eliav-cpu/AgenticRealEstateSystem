# Adaptation map: Ori CLI to ex-el

## Take as-is or nearly as-is

### Persistent memory pattern
Keep the concept, not the exact implementation.
Reason: ex-el needs continuity across sessions, projects, templates, and decisions.

### Warm context refresh
Keep.
Reason: critical for preserving current strategic state after compaction.

### Multi-model slotting
Keep.
Reason: ex-el has clearly separable workloads: reasoning, cheap summarization, batch classification, and primary interaction.

### Phase-gated tools
Keep.
Reason: business workspaces are noisier than coding workspaces. Token discipline matters even more.

### Compaction discipline
Keep.
Reason: long-running operational sessions will otherwise degrade quickly.

## Adapt heavily

### REPL body
Adapt from codebase REPL to workspace execution body.
New purpose:
- rank sources
- normalize spreadsheet and CRM state
- compute scenario deltas
- compare assumptions and outputs
- detect missing data and confidence gaps

### Structural graph
Adapt from code dependency graph to workspace graph.
New nodes:
- project
- client
- proposal
- unit
- spreadsheet
- sheet
- assumption set
- clause
- email thread
- meeting
- task

### Judgment tools
Adapt from code duplication and convention detection to business-pattern detection.
New operations:
- duplicate proposal logic detection
- conflicting assumptions detection
- approved language consistency scoring
- source-of-truth conflict detection
- proposal placement suggestion

## Do not carry over directly

### Code-first abstractions
Do not let codebase semantics dominate the design.
ex-el is a business operating layer first.

### Identity language from Ori
Do not reuse naming, ritual, or philosophical branding.
ex-el needs its own institutional voice.

### Pure terminal-first UX assumption
Do not anchor the product in CLI-only workflows.
Use service-core architecture that can back web UI, automation, and internal operators.

## ex-el native additions required

### Source governance
Every output should know:
- source summary
- confidence level
- classification
- recommended next action
- reusable knowledge decision

### Proposal intelligence
The core should support:
- unit and inventory search
- payment-plan reasoning
- pricing and delta computation
- proposal assembly
- scenario comparison

### CRM awareness
The core should understand:
- lead stage
- SLA timers
- event timestamps
- meeting outcomes
- stalled deal alerts
- next best action

### Reusable knowledge capture
The core should promote strong material into:
- template
- FAQ
- clause bank
- approved phrasing
- playbook

## Target architecture outcome

A workspace-native agent kernel that can reason across code, spreadsheets, CRM, documents, and commercial communication as one operational surface.
