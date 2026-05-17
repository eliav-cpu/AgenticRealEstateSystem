# Excelator Prime Invest King Tamar

This folder is the organized GitHub workspace for the King Tamar Excel simulator, internal payment engine, client proposal, QA rules, and control panel.

## Current working files

- Main Excel working model: `עופר_נבו_EXCELDOR_V20_UNIT_SELECTOR_FIXED.xlsx`
- Control panel workbook: `EXCELDOR_CONTROL_PANEL_V1.xlsx`

## Goal

Build one reliable operating model for the sales team:

- one client-facing deal price
- one client-facing payment schedule
- internal split between shell, finishing, and parking
- clean QA checks that close to 100 percent
- stable unit selection from an available-units table
- future migration path to Google Sheets or an internal SaaS tool

## Core payment rule

The client display percentage must be calculated only from the total combined deal price.

Client display percent = combined stage payment / total deal price

Combined stage payment = shell payment + finishing payment + parking payment

## Workbook layers

1. SIMULATOR - agent input and display
2. ENGINE - single source of truth for calculations
3. CLIENT_PROPOSAL - client-facing proposal
4. QA - selected-scenario validation
5. QA_MATRIX - regression checks
6. PAYMENT_MODEL - payment stages, shell percentages, multipliers
7. DATA_UNITS - source unit data
8. AVAILABLE_UNITS - valid selectable units
9. CONTROL PANEL - workflow, QA, formulas, version log

## Folder structure

- `docs/CONTROL_PANEL_GUIDE.md`
- `docs/WORKFLOW.md`
- `docs/FORMULA_REFERENCE.md`
- `docs/QA_CHECKLIST.md`
- `docs/VERSION_LOG.md`
- `artifacts/MANIFEST.md`
- `artifacts/base64/` backup copies of workbook files encoded as base64 text

## Status

V20 is the current working model. The control panel is V1.
