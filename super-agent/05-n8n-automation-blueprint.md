# 05 - n8n Automation Blueprint

## Purpose
n8n is the automation layer for the Super Agent.

It connects Drive, GitHub, Canva, CRM, email, sheets and notifications into one production system.

## Core Rule
Automation should move assets through the production line without the user manually managing every step.

## Recommended Workflows

### Workflow 1 - New Drive File Intake
Trigger:
- new file added to Google Drive project folder

Actions:
1. identify file type
2. classify source status
3. create GitHub issue if review is needed
4. notify user or team
5. route to correct folder if needed

### Workflow 2 - New Slide QA
Trigger:
- new deck or slide file uploaded

Actions:
1. extract text if possible
2. run Hebrew RTL QA
3. flag risky claims
4. mark data requiring verification
5. create QA summary

### Workflow 3 - Banner Production Archive
Trigger:
- new Canva export added

Actions:
1. detect full or clean version
2. rename using naming convention
3. store in Drive archive
4. log asset in production sheet
5. mark campaign and version

### Workflow 4 - GitHub QA Notification
Trigger:
- new commit in visual-production-system or super-agent

Actions:
1. check changed files
2. run QA checklist
3. notify if key files changed
4. open issue for missing pieces

### Workflow 5 - CRM Lead To Asset Flow
Trigger:
- lead moves to meeting scheduled / offer sent / simulation needed

Actions:
1. identify project and lead stage
2. select relevant deck or asset
3. prepare follow-up copy
4. log action
5. notify sales owner

### Workflow 6 - Client Ready Export Gate
Trigger:
- asset marked client-ready

Actions:
1. confirm source status
2. confirm QA pass
3. confirm no risky claims
4. confirm final and clean versions exist where required
5. move to Client Ready folder

## Required Credentials
Set in n8n credentials only, never inside prompts:
- Google Drive
- GitHub
- Canva if supported
- CRM
- Gmail / email
- Google Sheets
- OpenAI API if used

## Suggested Data Sheet
Create a production tracking sheet with columns:

```text
Asset ID
Project
Asset Type
Campaign
Version
Full / Clean
Source Status
QA Status
Owner
Drive Link
Canva Link
Figma Link
GitHub Reference
Date Created
Date Approved
Notes
```

## Priority Automations
Start with:
1. Drive file intake
2. Banner archive
3. GitHub QA notification
4. Client-ready export gate

Then add CRM and advanced OpenAI API workflows.

## Assistant Behavior
When designing n8n workflows, the assistant should provide:
- trigger
- nodes
- conditions
- data fields
- failure cases
- naming convention
- expected output

## Rule
n8n is not the brain. n8n is the conveyor belt.
