# 01 - Google Drive Source Map

## Purpose
Google Drive is the source governance layer for the Super Agent.

The assistant must know where source files live, what is final, what is draft, what is client-ready and what requires verification.

## Core Rule
No client-facing output should be created from unknown source status.

## Recommended Drive Folder Structure

```text
PRIME / King Tamar /
  01_Source_of_Truth /
  02_Project_Materials /
  03_Final_Decks /
  04_Canva_Exports /
  05_Figma_Masters /
  06_Financial_Models /
  07_Images_and_Renders /
  08_Client_Ready /
  09_Archive /
  10_Working_Drafts /
```

## Folder Definitions

### 01_Source_of_Truth
Contains only approved and authoritative files.

Examples:
- Client Copy V6
- Sales Playbook V6
- approved project facts
- legal / commercial source summaries
- verified claim log

Rule:
Only this folder may override older materials.

### 02_Project_Materials
Contains raw project files.

Examples:
- brochures
- developer files
- floor plans
- renders
- price lists
- payment plans
- location materials

Rule:
Content here may be used, but facts should be checked before client use.

### 03_Final_Decks
Contains final or near-final presentations.

Examples:
- final investor deck
- meeting deck
- short deck
- webinar deck

Rule:
If a final deck conflicts with Source of Truth, Source of Truth wins.

### 04_Canva_Exports
Contains exported campaign assets.

Subfolders:
```text
Full Versions
Clean Versions
Stories
Feed Posts
Archive
```

### 05_Figma_Masters
Contains master slide systems and reusable design frames.

Examples:
- Light masters
- Dark masters
- Card system
- Benchmark boards
- trust slides

### 06_Financial_Models
Contains Excel / Sheets / simulations.

Examples:
- price model
- rental model
- investor simulation
- payment plan model

Rule:
Numbers from this folder require source and date context.

### 07_Images_and_Renders
Contains:
- project renders
- real photos
- city photos
- maps
- people photos
- logo files
- seal files

Rule:
Real people must not be altered in identity, face, age or expression.

### 08_Client_Ready
Contains only client-safe exports.

Rule:
No drafts. No unverified claims. No broken Hebrew.

### 09_Archive
Contains old files and replaced versions.

Rule:
Archive files are reference only, not source of truth.

### 10_Working_Drafts
Contains experiments and work in progress.

Rule:
Never treat draft materials as final.

## Source Status Labels
Every important file should be classified as:

```text
Source of Truth
Approved Template
Client Ready
Working Draft
Project Material
Archive
Unknown / Needs Review
```

## Assistant Behavior
When using Drive materials, the assistant must:
- identify the source folder
- classify the file status
- prefer Source of Truth over drafts
- mark missing data as requiring verification
- avoid mixing client copy with internal sales playbook
- never assume a file is final from title alone

## File Naming Convention

```text
project_layer_asset_version_status_date
```

Examples:
```text
king-tamar_client-copy_v6_source-of-truth_2026-04
king-tamar_investor-deck_v12_client-ready_2026-05
king-tamar_banner-income-4x5_v03_full_2026-05
king-tamar_banner-income-4x5_v03_clean_2026-05
```

## Drive QA Gate
Before any client-facing output, check:
- source file exists
- version is current
- data claim has source
- copy is approved or rewritten safely
- output is stored in correct folder

## Short Operating Rule

```text
Drive is not storage. Drive is source governance.
```
