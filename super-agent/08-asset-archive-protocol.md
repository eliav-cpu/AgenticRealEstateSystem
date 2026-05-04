# 08 - Asset Archive Protocol

## Purpose
This protocol defines how final assets, clean versions, drafts and campaign outputs should be archived.

## Core Rule
If an asset is not named, classified and archived, it is not part of the system.

## Asset Types

```text
Slide
Deck
Banner
Story
Square Post
Clean Template
Figma Master
Canva Design
Image Background
Client PDF
Excel Visual
```

## Version Types

```text
Full
Clean
Draft
Client Ready
Source
Archive
```

## Naming Convention

```text
project_asset_campaign_ratio_version_status_date
```

Examples:
```text
king-tamar_banner_income-60k_4x5_v01_full_2026-05
king-tamar_banner_income-60k_4x5_v01_clean_2026-05
king-tamar_slide_king-david-benchmark_16x9_v03_client-ready_2026-05
king-tamar_figma_master_trust-triangle_16x9_v02_source_2026-05
```

## Required Archive Fields
For each asset, log:

```text
Asset ID
Project
Asset Type
Campaign
Ratio
Version
Status
Source Basis
QA Status
Created By
Approved By
Drive Link
Canva Link
Figma Link
GitHub Reference
Date Created
Date Approved
Notes
```

## Status Definitions

### Draft
Work in progress.
Not for client use.

### Working Draft
Can be reviewed internally.
Requires QA before client use.

### Client Ready
Approved for client or campaign use.
Must pass QA.

### Clean Template
Reusable design without final text.

### Source
Authoritative source file.

### Archive
Old or replaced asset.
Reference only.

## Archive Folder Map

```text
04_Canva_Exports /
  Full Versions /
  Clean Versions /
  Stories /
  Feed Posts /
  Archive /

05_Figma_Masters /
  Source Masters /
  Exported PNG /
  Clean Templates /

08_Client_Ready /
  Slides /
  Decks /
  Banners /
  PDF /

09_Archive /
  Old Versions /
  Replaced /
  Experiments /
```

## QA Before Archive
Before marking client-ready:
- Hebrew RTL pass
- commercial safety pass
- source status known
- no unsupported claim
- full and clean versions exist where needed
- correct folder
- correct naming

## Assistant Behavior
When producing or reviewing an asset, the assistant should recommend:
- final filename
- status
- archive location
- missing QA if any
- whether it should become a reusable template

## Rule
The archive is not storage. It is operational memory.
