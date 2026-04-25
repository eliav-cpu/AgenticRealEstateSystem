# Repo Connection Priority Matrix

Status: Working
Date: 2026-04-25
Scope: PRIME / King Tamar / ex-el / Brand Presentation OS

## Executive decision

Do not connect everything.

The correct strategy is to connect only repositories that add a distinct production layer.

## Connect now

1. PPTAgent
Role: reference-based deck generation lab
Priority: Critical
Reason: best candidate for learning from reference decks and generating structured drafts

2. ppt-master
Role: visual template engine / SVG-to-PPTX
Priority: Critical
Reason: best candidate for PRIME custom slide-master production

3. awesome-notebookLM-prompts
Role: prompt architecture for NotebookLM / Kael style work
Priority: High
Reason: improves prompt discipline and design-spec writing

4. MegaParse
Role: source ingestion / document parsing
Priority: High
Reason: parses PDFs, PPTX, DOCX, XLSX, tables, images and document structure before synthesis

5. Office-PowerPoint-MCP-Server
Role: live PPTX editing and polish layer
Priority: High
Reason: useful after generation for extracting, editing and improving PowerPoint files

6. ShapeCrawler
Role: deterministic .NET PPTX manipulation
Priority: High
Reason: strong server-side PPTX read / create / modify library, no Office required

7. docxtemplater
Role: template-based DOCX/PPTX document generation
Priority: High
Reason: strong for replacing placeholders, loops and conditions in DOCX/PPTX templates

## Connect later / optional

8. unioffice
Role: Go backend for DOCX/XLSX/PPTX production
Priority: Medium-High
Reason: valuable for ex-el backend generation, but commercial license and not first visual layer

9. docx4j
Role: Java OpenXML manipulation
Priority: Medium
Reason: powerful but overlaps with unioffice/docxtemplater/ShapeCrawler unless Java stack is chosen

10. PowerPointLabs
Role: inspiration / manual PowerPoint add-in patterns
Priority: Medium
Reason: useful for visual ideas and interactive PowerPoint operations, but not core automation

11. Microsoft Architecture PPTX Icons
Role: icon reference library for architecture diagrams
Priority: Low-Medium
Reason: useful only for system/tech diagrams; not core PRIME real-estate deck identity

12. Open XML Package Editor Power Tool
Role: OOXML inspection and debugging
Priority: Low-Medium
Reason: useful for developers debugging PPTX internals, not a production generator

13. Claper
Role: interactive audience presentation layer
Priority: Low
Reason: useful only if PRIME wants live interactive webinars, polls or audience feedback

## Do not connect now

14. PHPPresentation
Reason: useful only if PRIME runs a PHP backend; overlaps with stronger current options

15. PowerPoint-Generator-Python-Project
Reason: generic GPT presentation generator, weaker than PPTAgent and ppt-master for our needs

16. Some-Many-Books
Reason: unrelated and too broad; not relevant to PRIME presentation production stack

17. powerpoint
Reason: ambiguous repository name; exact repo must be identified before decision

## Recommended final stack

1. MegaParse - parse raw materials
2. NotebookLM prompts - research and synthesis
3. brand-presentation-os - governance, DNA, approved copy
4. PPTAgent - reference-based draft generation
5. ppt-master - PRIME visual template / SVG production
6. ShapeCrawler or Office MCP - PPTX manipulation and polish
7. docxtemplater - proposal / report / template outputs
8. unioffice - future ex-el production backend if license is approved

## Rule

Connect for capability, not curiosity.

Every connected repo must have one unique job in the operating system.
