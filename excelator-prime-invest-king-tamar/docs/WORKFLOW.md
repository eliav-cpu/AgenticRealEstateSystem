# Workflow

## Daily operating flow

1. Open the latest approved workbook in Excel Desktop.
2. Use the SIMULATOR sheet only.
3. Select project.
4. Select unit only from AVAILABLE_UNITS.
5. Select payment option.
6. Select with finish or without finish.
7. Select parking status and quantity.
8. Review combined payment schedule.
9. Open QA.
10. Send proposal only if QA is OK.

## No-edit zones

Do not edit formulas in:

- ENGINE
- PAYMENT_MODEL
- CLIENT_PROPOSAL calculation cells
- QA
- QA_MATRIX

## Editable zones

Agents may edit only approved input cells in SIMULATOR.

Managers may update:

- DATA_UNITS
- PAYMENT_MODEL
- text blocks in CLIENT_PROPOSAL

Only after QA.

## Version control rule

Every structural change must be saved as a new version and documented in VERSION_LOG.
