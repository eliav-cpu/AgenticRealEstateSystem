# Recovery and Safe Sync Plan - 2026-05-19

## Decision

The prior SYNC_READY workbook should not be used as the production workbook.

A safe original-copy restore was created:

`סימולטור_קינג_תמר_סופי_17.05.26_RESTORED_ORIGINAL.xlsx`

## Correct architecture

Do not inject online sync logic into the main simulator workbook at this stage.

Use a companion control workbook instead:

`EXCELDOR_ONLINE_STATUS_SYNC_COMPANION_V1.xlsx`

## Why

The main workbook contains active formulas, media mappings, proposal sheets, and legacy structures. Direct workbook editing can damage formulas, media references, sheet links, or workbook state.

## Online status sync scope

The Google Sheet is for sales status only:

- Available / Reserved / In Process / Sold / Cancelled / Blocked
- Sold date
- Reserved date
- Agent
- Advisor
- Client status
- Israel side
- Overseas side
- Our side
- Last action
- Last updated
- Notes

The Google Sheet must not:

- pull prices
- calculate deals
- overwrite apartment pricing
- update financial terms
- replace the pricing simulator

## Next safe step

1. Work from the restored original workbook.
2. Keep the online sync as a companion document.
3. Build future sync only through a controlled UnitKey layer.
4. Add any sync integration only after a full formula and media audit.
