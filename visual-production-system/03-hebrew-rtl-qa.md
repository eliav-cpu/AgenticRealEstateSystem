# 03 - Hebrew RTL QA

## Purpose
This file defines the Hebrew and RTL quality gate for every slide, banner, image and visual asset.

A visual asset with broken Hebrew is not client-ready, even if the design looks beautiful.

## Core Rule
Hebrew is not decoration. Hebrew is the trust layer.

## Mandatory Checks

### 1. RTL Direction
Check that:
- all Hebrew text flows right to left
- sentences are right-aligned
- punctuation sits naturally
- mixed Hebrew / English does not break the line
- numbers are readable in the correct order

### 2. Typography Clarity
Check that:
- text is sharp
- letters are not smeared
- letters are not fake or AI-distorted
- font weight is consistent
- hierarchy is clear
- small text is still readable on mobile and in meeting-room view

### 3. Hebrew Spelling
Check for:
- missing letters
- wrong final letters
- accidental English characters
- duplicated words
- broken words
- awkward phrasing
- incorrect professional terms

### 4. Commercial Safety
Flag or replace absolute language:

Avoid:
- מובטח
- ודאי
- ללא סיכון
- תשואה מובטחת
- עליית ערך ודאית
- אין תחרות
- שקט נפשי מלא
- ביקוש מטורף

Prefer:
- צפי
- פוטנציאל
- תזה
- Benchmark
- בדיקה מסודרת
- בכפוף לבדיקה
- לפי חומרי הפרויקט
- סימולציה אישית
- דורש אימות

### 5. Data Verification
Mark as requiring verification when the asset includes:
- price
- yield
- appreciation
- delivery date
- legal claim
- banking claim
- permit / residency claim
- tax claim
- market ranking
- occupancy
- rent forecast
- comparison to competitors

Use:
```text
דורש אימות
```

Do not invent missing data.

## Hebrew Slide Copy Standard

### Good Slide Copy
- short
- sharp
- premium
- readable in 3 seconds
- focused on value and decision
- no long educational paragraphs

### Weak Slide Copy
- too explanatory
- too legalistic
- too generic
- too many claims
- too much text
- no investor action

## Recommended Structure

```text
כותרת החלטה
כותרת משנה קצרה
3-4 כרטיסים
שורת מסר תחתונה
```

## Common Fix Patterns

### Long Title -> Decision Title
Before:
```text
מידע כללי על סביבת הפרויקט והיתרונות למשקיעים
```
After:
```text
כתובת שמחברת ביקוש, נגישות ופוטנציאל
```

### Weak CTA -> Clear CTA
Before:
```text
לפרטים נוספים
```
After:
```text
בדיקת התאמה להשקעה
```

### Risky Claim -> Safe Claim
Before:
```text
תשואה מובטחת של 12%
```
After:
```text
צפי תשואה לפי סימולציה אישית
```

### Heavy Consultant Language -> Client Language
Before:
```text
מיקרו־לוקיישן אסטרטגי עם פוזיציה אורבנית
```
After:
```text
כתובת מרכזית על ציר ביקוש חזק
```

## Mixed Hebrew / English Rule
English is allowed only for:
- brand names
- product names
- international professional terms when needed

Examples:
- PRIME
- King Tamar
- Archi
- Benchmark
- Excel

Do not overload Hebrew headlines with English.

## QA Output Template

```text
Hebrew QA Result:
- RTL: Pass / Fix needed
- Spelling: Pass / Fix needed
- Typography: Pass / Fix needed
- Commercial safety: Pass / Fix needed
- Data verification: Pass / Requires verification
- Final status: Client-ready / Needs correction
```

## Zero-Tolerance Failure Cases
The asset fails if it contains:
- broken Hebrew
- blurry Hebrew
- reversed sentence order
- misspelled headline
- invented financial number
- guaranteed return language
- distorted real person identity
- unreadable CTA

## Recommended Production Instruction
Use this instruction when sending to an image or design model:

```text
All Hebrew must be clean, sharp, fully RTL and right-aligned. If perfect Hebrew typography cannot be guaranteed, create the visual without final text and leave clean text zones for Canva/Figma live typography.
```
