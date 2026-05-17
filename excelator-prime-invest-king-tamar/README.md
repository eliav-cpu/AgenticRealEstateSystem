# Excelator Prime Invest King Tamar

This folder is the GitHub workspace for the King Tamar Excel simulator, internal payment engine, client proposal, and QA rules.

## Goal

Build one reliable operating model for the sales team:

- one client-facing deal price
- one client-facing payment schedule
- internal split between shell, finishing, and parking
- clean QA checks that close to 100 percent
- future migration path to Google Sheets or an internal SaaS tool

## Core payment rule

The client display percentage must be calculated only from the total combined deal price.

Client display percent = combined stage payment / total deal price

Combined stage payment = shell stage payment + finishing stage payment + parking stage payment

## Current Excel artifact

Current working artifact name:

`עופר_נבו_EXCELDOR_V13_FINAL_WORKING.xlsx`

## Workbook layers

1. EXCELDOR_PAYMENT_MODEL - clean payment model and multipliers
2. EXCELDOR_ENGINE_V10 - internal engine with shell, finish, parking and combined payment
3. EXCELDOR_SIMULATOR_V10 - agent-facing simulator
4. EXCELDOR_CLIENT_PROPOSAL_V10 - client proposal
5. QA_PAYMENT_V10 - validation checks
6. EXCELDOR_CHANGELOG - change history

## Status

Working Draft. QA closes correctly across the tested combinations of option 1, option 2, option 3, with finish, without finish, with parking, and without parking.
