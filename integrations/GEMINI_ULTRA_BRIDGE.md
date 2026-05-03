# Gemini Ultra Bridge — PRIME / King Tamar

## Purpose
Gemini Ultra is used as the external research and source-verification engine for PRIME / King Tamar.

It does not control final slide copy. It does not replace Client Copy V6 or Sales Playbook V6.

## Gemini Role
Use Gemini for:
- Deep Research
- external source discovery
- Tbilisi / Georgia market research
- tourism and urban-development context
- regulatory source checks
- competitor and benchmark checks
- source summaries
- source-log preparation
- Google / NotebookLM workflows

## Output Back To ChatGPT
Gemini must return structured research only, not final slide copy.

Required output format:

```markdown
# Gemini Research Output

## Topic

## Research Question

## Executive Summary

## Verified Sources
| Claim | Source | Date | Link | Confidence | Notes |
|---|---|---|---|---|---|

## Claims Suitable For Client Use

## Claims For Internal Use Only

## Data Requiring Verification

## Risks / Caveats

## Suggested Slide Use

## Suggested Source-Log Entry
```

## Gemini Prompt — Copy/Paste

```text
פעל כמנוע מחקר חיצוני עבור PRIME / King Tamar.

התפקיד שלך הוא לא לכתוב מצגת, לא לייצר קופי מסך ולא להחליף את Client Copy V6.

המטרה שלך:
לאתר מקורות אמינים, לסכם עובדות, להפריד בין נתון מאומת לבין טענה שיווקית, וליצור Source Log מסודר לשימוש בהמשך.

הקשר:
King Tamar by Archi הוא פרויקט מגורים פרימיום בטביליסי, בגאורגיה. העבודה מתבצעת עבור PRIME Invest. השפה מול לקוח ישראלי חייבת להיות פשוטה, יוקרתית, ברורה ולא מבטיחה תוצאה.

חוקי עבודה:
1. אל תמציא נתונים.
2. כל מספר חייב מקור.
3. סמן כל דבר לא מאומת כ־דורש אימות.
4. הפרד בין מקור רשמי, מקור שוק, הערכה, מסקנה ונתון חסר.
5. אל תכתוב סליידים סופיים.
6. החזר מחקר מסודר בלבד.
7. אם יש סתירה בין מקורות, הצג אותה.
8. אל תשתמש בשפה של הבטחת תשואה, ודאות או ללא סיכון.

פורמט הפלט:
# Gemini Research Output
## Topic
## Research Question
## Executive Summary
## Verified Sources table: Claim | Source | Date | Link | Confidence | Notes
## Claims Suitable For Client Use
## Claims For Internal Use Only
## Data Requiring Verification
## Risks / Caveats
## Suggested Slide Use
## Suggested Source-Log Entry
```

## Operating Rule
Gemini produces sources. ChatGPT converts verified sources into slide copy, prompts, QA and final deliverables.
