# unioffice Assessment for PRIME / ex-el / King Tamar

Status: Working
Date: 2026-04-25
Repository reviewed: unidoc/unioffice

## Executive decision

unioffice is useful for PRIME, but as a production backend library, not as an AI design or research layer.

It should be considered for document generation infrastructure when ex-el needs to create or edit DOCX, XLSX and PPTX files programmatically at scale.

## What it is

unioffice is a Go library for creating and editing Office Open XML documents:

- DOCX
- XLSX
- PPTX

It is focused on compatibility and performance, not on AI reasoning or visual creativity.

## Best use for PRIME / ex-el

Use unioffice for:

1. Generating investor proposal documents
2. Creating DOCX reports from approved templates
3. Filling Word templates with client/project data
4. Creating Excel workbooks or extracting structured spreadsheet data
5. Creating PowerPoint drafts from strict templates
6. Producing high-volume standardized outputs
7. Backend generation where Go performance and deterministic output matter

## PPTX relevance

For PowerPoint, unioffice currently appears strongest for:

- creating presentations from templates
- text boxes
- shapes
- image insertion

It is not a full design agent and should not be expected to produce premium PRIME slide logic on its own.

## XLSX relevance

For Excel, unioffice is potentially valuable:

- read / write / edit spreadsheets
- formatting and conditional formatting
- validation rules
- formatted cell values
- formula evaluation
- embedded images
- charts

This may be especially relevant for ex-el, proposal engines and investor dashboards.

## DOCX relevance

For Word, unioffice is relevant for:

- reports
- contracts summaries
- proposal letters
- client-ready documentation
- templates with form fields
- headers, footers, TOC and images

## Important limitation

unioffice is commercial software and requires a license key.

This makes it a strategic production decision, not a casual open-source dependency.

## Relationship with the PRIME tool stack

Recommended stack:

1. `MegaParse` - parse and ingest documents
2. `NotebookLM templates` - research and synthesis
3. `brand-presentation-os` - brand rules, governance and approved copy
4. `PPTAgent` - reference-based slide generation lab
5. `ppt-master` - controlled visual master generation
6. `Office-PowerPoint-MCP-Server` - PowerPoint editing and polish
7. `unioffice` - backend Office document generation at scale

## Decision

Worth keeping in the architecture.

Do not use it as the first visual solution for King Tamar decks.
Use it later as the deterministic backend for ex-el outputs, proposal packs, DOCX reports, XLSX files and templated PPTX production.
