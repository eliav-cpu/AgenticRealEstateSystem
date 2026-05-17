# Payment Engine V18 Spec

Workspace: Excelator Prime Invest King Tamar

## Current artifact

`עופר_נבו_EXCELDOR_V18_BEST_PRO.xlsx`

## Core logic

The client sees one total deal price and one combined payment schedule.

Internally the model splits the deal into:

1. Shell
2. Finishing
3. Parking
4. Combined client display
5. QA checks

## Formula architecture

### Total deal price

```text
Total deal price = adjusted shell price + finish full price + adjusted parking price
```

### Adjusted shell price

```text
Adjusted shell price = shell base price * selected payment model multiplier
```

### Finish price

```text
Finish full price = internal sqm * finish price per sqm
```

Finish is not distributed by the shell payment model. It is split into two fixed apartment-based payments:

```text
Finish first payment = finish full price * finish upfront percent
Finish final payment = finish full price - finish first payment
```

### Parking price

```text
Adjusted parking price = parking quantity * 25000 * selected payment model multiplier
```

Parking is distributed according to the same shell percentage schedule.

### Stage payment

```text
Combined stage payment = shell stage payment + finish stage payment + parking stage payment
```

### Client display percent

```text
Client display percent = combined stage payment / total deal price
```

## Required workbook layers

1. SIMULATOR - agent input and client-facing numbers
2. ENGINE - single source of truth for calculations
3. CLIENT_PROPOSAL - clean client proposal
4. QA - selected scenario validation
5. QA_MATRIX - static regression scenarios
6. PAYMENT_MODEL - clean model percentages and multipliers
7. DATA_UNITS - source unit data
8. LISTS - dropdown lists and service fee mapping

## QA rules

The model is valid only when all checks are OK:

- sum of combined payments equals total deal price
- sum of display percentages equals 100 percent
- sum of shell payments equals adjusted shell price
- sum of finish payments equals finish full price
- sum of parking payments equals adjusted parking price
- selected unit exists in DATA_UNITS

## Default validated scenario

King Tamar / floor 7 / flat 9 / option 3 / with finish / without parking

Expected total deal price:

```text
201,687.74 USD
```

Status: V18 working model.
