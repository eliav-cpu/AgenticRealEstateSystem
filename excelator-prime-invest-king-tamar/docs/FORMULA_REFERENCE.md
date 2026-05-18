# Formula Reference

## Total deal price

Total deal price = adjusted shell price + active finish price + adjusted parking price

## Adjusted shell price

Adjusted shell price = shell base price * selected payment model multiplier

## Active finish price

If finish is selected, finish full price is included. If finish is not selected, finish price is zero.

## Finish split

Finish is not distributed by the shell payment model.

Finish first payment = finish full price * finish upfront percent

Finish final payment = finish full price - finish first payment

## Parking price

Adjusted parking price = parking quantity * 25000 * selected payment model multiplier

Parking is distributed by the same shell payment schedule.

## Stage payment

Shell stage payment = adjusted shell price * shell stage percent

Finish stage payment:
- signing stage = finish first payment
- delivery stage = finish final payment
- middle stage = 0

Parking stage payment = adjusted parking price * shell stage percent

Combined stage payment = shell stage payment + finish stage payment + parking stage payment

## Client display percent

Client display percent = combined stage payment / total deal price

This is the only percentage that should be shown to the client.
