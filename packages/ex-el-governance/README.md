# ex-el-governance

Governance layer for ex-el.

This package is responsible for deciding:

- what counts as a reliable source
- what is only a working draft
- what can be used for client-facing output
- how confidence is calculated
- what next action is required before an output can be trusted

## Core responsibilities

1. Classify source material
2. Score confidence
3. Detect conflicts between sources
4. Block unsafe client-output generation when source basis is weak
5. Promote strong material into reusable knowledge

## Expected inputs

- CRM records
- spreadsheets and simulations
- Drive documents and decks
- emails and commercial threads
- approved templates and clause banks

## Expected outputs

For every governed artifact:

- source summary
- confidence level
- output classification
- blocking issues
- recommended next action
- reusable knowledge recommendation

## Rule of the system

No client-facing financial, legal, or commercial wording should be generated without a visible source basis.
