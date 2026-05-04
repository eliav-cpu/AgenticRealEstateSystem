# 06 - CRM Sales Intelligence Map

## Purpose
The CRM layer turns the Super Agent from a production assistant into a commercial operating system.

The agent should understand not only what to create, but why the asset is needed in the sales journey.

## Core Rule
Every visual, slide, banner or message should support a funnel stage.

## Required CRM Entities

### Lead
Fields:
```text
Lead ID
Name
Phone
Email
Source
Campaign
Project
Owner
Created Date
Lead Quality Score
Current Stage
Next Action
Last Contact Date
```

### Meeting
Fields:
```text
Meeting Scheduled
Meeting Date
Meeting Held
Meeting Type
Meeting Outcome
No-show / Cancel Reason
Participants
Follow-up Needed
```

### Offer / Simulation
Fields:
```text
Simulation Sent
Excel Model Used
Unit Type
Payment Track
Expected Scenario
Offer Sent Date
Questions Raised
Objections
```

### Deal
Fields:
```text
Deal Status
Closed Won / Lost
Lost Reason
Reservation Status
Unit Reserved
Deposit Status
Contract Status
```

## Recommended Funnel Stages

```text
Lead Created
First Contact Attempt
Call Scheduled
Call Held
Meeting Scheduled
Meeting Held
Simulation Needed
Simulation Sent
Unit Selection
Reservation Discussion
Reservation Paid
Contract Process
Closed Won
Closed Lost
```

## Asset Mapping By Stage

### Lead Created
Recommended assets:
- short banner
- WhatsApp intro text
- trust mini-card

### Call Scheduled
Recommended assets:
- short project overview
- meeting prep message

### Meeting Held
Recommended assets:
- investor deck
- location slide
- trust slide
- benchmark slide

### Simulation Needed
Recommended assets:
- Excel transition slide
- personal simulation explanation
- payment track card

### Unit Selection
Recommended assets:
- unit mix slide
- availability check message
- unit comparison table

### Reservation Discussion
Recommended assets:
- reservation steps
- process timeline
- next action message

### Closed Lost
Recommended assets:
- lost reason tag
- nurture content
- retargeting audience signal

## CRM To Creative Feedback Loop
The Super Agent should learn which assets support which stage.

Track:
- which banner created the lead
- which deck was shown
- which slide caused questions
- which objection repeated
- which CTA converted
- which follow-up message worked

## Required Lost Reasons

```text
Budget
Timing
Trust
Location concern
Yield concern
Financing concern
Family decision
Legal concern
Needs more comparison
No response
Not relevant
Other
```

## Required Objection Tags

```text
Georgia risk
Developer trust
Yield credibility
Exit strategy
Financing
Tax
Legal process
Unit availability
Delivery date
Management
Resale
Currency
```

## Assistant Behavior
When a user asks for an asset, the assistant should infer:
- funnel stage
- audience temperature
- required CTA
- likely objection
- best asset type
- whether source verification is needed

## Rule
Creative output must serve the sales pipeline, not only look good.
