# QA Checklist

The model is ready for client proposal only when every relevant check is OK.

## Required checks

1. Selected unit exists in DATA_UNITS.
2. Selected unit appears in AVAILABLE_UNITS.
3. Sum of combined payments equals total deal price.
4. Sum of client display percentages equals 100 percent.
5. Sum of shell payments equals adjusted shell price.
6. Sum of finish payments equals finish full price.
7. Sum of parking payments equals adjusted parking price.
8. Client proposal shows one total deal price.
9. Client proposal shows one combined payment schedule.
10. No internal margin or internal split is visible to the client.
11. No formula errors appear in the active sheets.

## Active sheets for error scan

- SIMULATOR
- ENGINE
- CLIENT_PROPOSAL
- QA
- QA_MATRIX
- PAYMENT_MODEL
- DATA_UNITS
- AVAILABLE_UNITS

## Red flags

Do not send a proposal if any of these appear:

- #REF
- #VALUE
- #NAME
- #DIV/0
- #N/A
- Total percent different from 100 percent
- Total payments different from total deal price
- Unit not found
