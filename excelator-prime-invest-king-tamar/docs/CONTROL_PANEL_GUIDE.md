# Control Panel Guide

File: EXCELDOR_CONTROL_PANEL_V1.xlsx

## Purpose

This workbook is the operating guide for the King Tamar Excel system. It is not the pricing simulator itself. It explains how the sales team should work with the model and how management should validate every proposal.

## Sheets

1. Control dashboard - current file, version, status, workflow.
2. Work procedure - operational rules for agents and managers.
3. Sheet map - what each workbook sheet does and what can or cannot be edited.
4. QA - required checks before sending a client proposal.
5. Formula reference - the core business logic and formula patterns.
6. Version log - history of active model versions.

## Working rule

Agents should work only in SIMULATOR in the main Excel model. The internal engine and model sheets are not agent-editable layers.

## Client-facing rule

The client should see one total deal price and one payment schedule. The internal split between shell, finishing, and parking should remain behind the scenes.

## Before sending any proposal

1. Open the current Excel model in Excel Desktop.
2. Set formulas to Automatic Calculation.
3. Select a valid unit from AVAILABLE_UNITS.
4. Select option 1, option 2, or option 3.
5. Select with finish or without finish.
6. Select parking status and parking quantity.
7. Check QA.
8. Export proposal only if all QA checks are OK.
