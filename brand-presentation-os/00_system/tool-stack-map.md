# PRIME / King Tamar / ex-el - Tool Stack Map

Status: Working
Owner: PRIME Invest
Purpose: Define the role of every connected tool in the Brand & Presentation Operating System

## Core rule

Every tool must have one clear job.

The system should not become a collection of disconnected tools. It must work as a pipeline:

Source -> Research -> Governance -> Brand Language -> Visual System -> Slide Generation -> QA -> Distribution -> Improvement

## Stack map

### 1. MegaParse

Role: Source ingestion and parsing

Use for:

- extracting text from PDF, PPTX, DOCX, XLSX and CSV
- preserving tables, headers, footers and document structure
- preparing clean Markdown before NotebookLM or GPT work
- creating a first source-log draft

Do not use for:

- visual design
- final copywriting
- final claims

### 2. NotebookLM

Role: Research, synthesis and source-based thinking

Use for:

- analyzing source packs
- extracting thesis
- building FAQ
- comparing documents
- preparing presentation logic
- identifying missing data

Do not use for:

- final visual output
- unsupported assumptions
- client-ready claims without governance

### 3. GitHub

Role: System of record and version control

Use for:

- Brand DNA
- Presentation DNA
- approved copy
- prompts
- project folders
- source logs
- governance rules
- version history

### 4. Figma

Role: Visual Source of Truth

Use for:

- slide master design
- component system
- colors, typography and spacing
- card systems
- trust rings and circular motifs
- visual proof before full deck production

### 5. PPTAgent

Role: Reference-based deck generation lab

Use for:

- learning from reference decks
- generating structured drafts
- testing slide logic
- creating alternatives for one approved slide type

Do not use as final authority.

### 6. ppt-master

Role: SVG-to-PPTX and template execution engine

Use for:

- PRIME custom template generation
- SVG-first layout control
- production of editable PowerPoint drafts

### 7. Office PowerPoint MCP

Role: PowerPoint editing and polish layer

Use for:

- reading existing PPTX files
- extracting slide text
- editing titles, shapes, images and tables
- applying production cleanup

### 8. ShapeCrawler / PptxGenJS

Role: Programmatic PPTX manipulation

Use for:

- deterministic slide generation
- structured PPTX edits
- template-driven production
- server-side generation inside ex-el

### 9. docxtemplater / unioffice

Role: Document and proposal production

Use for:

- proposal documents
- investor reports
- Word templates
- Excel-based outputs
- templated PPTX / DOCX production at scale

### 10. Playwright

Role: Visual QA and screenshot testing

Use for:

- capturing slide previews
- comparing generated output to reference masters
- checking spacing, overflow and visual consistency
- building a visual QA loop

### 11. Canva / Google Slides

Role: Distribution and collaborative editing

Use for:

- sharing drafts
- team editing
- client-facing preview versions
- social and campaign assets

## Final production pipeline

1. Upload source materials
2. Parse with MegaParse
3. Analyze with NotebookLM
4. Save findings and source-log in GitHub
5. Build approved copy and slide outline
6. Design or update master in Figma
7. Generate draft with PPTAgent / ppt-master
8. Edit and polish with PowerPoint MCP / ShapeCrawler / PptxGenJS
9. Run Visual QA
10. Export to Canva / Google Slides / PPTX / PDF
11. Save learnings back to GitHub

## Governance rule

A tool output is never automatically client-ready.

Every output must pass:

- source governance
- brand voice linter
- visual QA checklist
- project-specific review
