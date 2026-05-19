# Latest Workbook Review - 2026-05-19

Reviewed workbook:

`סימולטור קינג תמר  _ סופי 17.05.26.xlsx`

Output workbook:

`סימולטור_קינג_תמר_סופי_17.05.26_SYNC_READY.xlsx`

## What was identified

The workbook already includes an advanced operating structure:

- Hebrew King Tamar simulator
- EXCELDOR SIMULATOR / ENGINE / PAYMENT_MODEL / QA structure
- DATA_UNITS and AVAILABLE_UNITS
- client proposal layers
- media mapping sheets
- sales screen
- system map

The latest user-built changes significantly improve the workbook by adding sales and media operation layers:

- `מפת מערכת`
- `גלריית מכירה`
- `מיפוי תמונות 3D`
- `מיפוי מדיה להצעות`
- `מדיה לפי דירה`
- `מסך מכירה`

These layers move the workbook closer to a real internal operating system, not just a price calculator.

## What was added in the SYNC_READY workbook

### 1. ONLINE_STATUS_SYNC

A new sheet was added with the Google Sheets link for online sales-status reporting.

The online sheet is explicitly defined as a sales-status synchronization layer only.

It must not pull prices, update apartment pricing, or calculate deals.

### 2. SALES_STATUS_SCHEMA

A structured data schema was added for the Google Sheet status layer.

Recommended fields include:

- UnitKey
- Project
- Floor
- Flat
- SalesStatus
- SoldDate
- ReservedDate
- Agent
- Advisor
- ClientStatus
- IsraelSide
- OverseasSide
- OurSide
- LastAction
- LastUpdated
- Notes

### 3. EXCELDOR_IMPROVEMENT_PLAN

A roadmap sheet was added with priorities:

- Online status sync
- Unit source of truth
- Media engine cleanup
- Proposal architecture decision
- Exchange-rate stability
- QA visibility
- Version control
- SaaS readiness

### 4. SIMULATOR link block

A visible block was added in the SIMULATOR sheet with the online-status Google Sheet link and a clear warning that the link is for sales status only.

### 5. Sales screen link block

A compact online-status block was added to `מסך מכירה`.

### 6. System map update

`מפת מערכת` was updated with the new online sync and status schema layers.

## Important warning

The workbook still contains legacy formula/media risks that were not force-fixed in this pass:

- possible #NAME? errors in exchange-rate formulas if the environment does not support WEBSERVICE/FILTERXML
- possible #VALUE! errors in legacy image cells or image references

These were not overwritten because the requested task was to study the latest workbook, add online status synchronization, and propose improvements without disrupting the working simulator.

## Sales status sync rule

The Google Sheet should store only sales status and workflow actions:

- sold / not sold / reserved / in process / cancelled / blocked
- sold date
- reserved date
- agent
- advisor / marketer
- client status
- Israel side
- overseas side
- our side
- last action
- last updated
- notes

It should not store or calculate prices.

## Recommended next fix

Add mandatory dropdown-based unit selection in SIMULATOR from AVAILABLE_UNITS to prevent typing invalid flats.
