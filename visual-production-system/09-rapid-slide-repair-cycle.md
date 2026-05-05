# 09 - Rapid Slide Repair Cycle

## Purpose
This file defines the mandatory fast repair cycle for every PRIME / King Tamar slide uploaded by the user.

The user should not need to provide instructions. The assistant must identify the slide, preserve the original concept, repair it quickly and return a precise correction package.

## Core Rule
Every uploaded slide must return fast with a clear correction cycle:

```text
Identify -> Flow Position -> Preserve -> Repair -> 2 Headlines -> Final Copy -> Execution Prompt -> Clean Version -> QA
```

## Mandatory Fast Cycle

### 1. Identify The Asset
Classify the uploaded item:
- slide
- banner
- story
- social post
- deck page
- clean template
- appendix

### 2. Assign Flow Position
Every slide must be placed in the sales flow:

```text
הבנה -> אמון -> מיקום -> מוצר -> מספרים -> אקסל -> בחירת יחידה -> שמירה / סגירה
```

If the slide does not belong in the core flow, classify it as:
- appendix
- internal guide
- archive
- delete / remove from client deck

### 3. Preserve Original Concept
By default, preserve:
- design concept
- color palette
- building / project image
- real people images
- logos
- card structure
- visual mood
- existing premium direction

Do not rebuild unless the user clearly asks.

### 4. Repair Automatically
Fix:
- spelling
- Hebrew phrasing
- RTL
- right alignment
- text hierarchy
- title strength
- small unreadable text
- card order
- icon/text direction
- visual clutter
- weak sales message
- risky commercial language

### 5. Mandatory Two Headlines
For every slide, provide at least two headline options:

```text
כותרת א׳ - סיפורי / יוקרתי
כותרת ב׳ - ברור / מכירתי
כותרת מומלצת למסך
```

The headline must:
- be understood in 3 seconds
- speak to the client
- move the investor toward the next stage
- avoid heavy consultant language
- avoid negative framing
- avoid guarantees

### 6. Client-Safe Long-Term Value Rule
The business message may communicate long-term value potential, but must not promise guaranteed profit.

Avoid:
```text
מי שקונה כאן מרוויח לכל החיים
רווח לכל החיים
תשואה מובטחת
עליית ערך ודאית
כסף בטוח
```

Preferred language:
```text
נכס שנבנה להחזקה ארוכת טווח
פוטנציאל ערך ותזרים לאורך שנים
החלטה שיכולה לשרת את ההון לשנים קדימה
בודקים היום נכס שיכול לעבוד לאורך זמן
הזדמנות שמתחילה בבחירה נכונה ונבדקת במספרים
```

### 7. Final Screen Copy
Return copy in this structure:

```text
כותרת מומלצת:
כותרת משנה:
Card 1:
Card 2:
Card 3:
Card 4 optional:
שורת מסר תחתונה:
```

Keep it short. Screen copy is not a sales script.

### 8. Execution Prompt
Return a precise prompt for execution:
- preserve design
- fix copy
- fix RTL
- fix title
- improve hierarchy
- keep brand colors
- do not change image/logo/building
- produce full and clean versions

### 9. Clean Version
For every important slide, define a clean version:
- same design
- same card zones
- same image areas
- no final Hebrew text
- ready for future reuse

### 10. QA Gate
Every slide must pass:
- Hebrew RTL
- right alignment
- spelling
- title strength
- sales flow fit
- mobile / meeting readability
- no risky guarantee language
- data verification marker if needed
- PRIME visual DNA

## Response Format For Every Uploaded Slide

```text
1. זיהוי המשימה
2. מיקום בפלואו
3. מה לשמר
4. מה לתקן מיד
5. שתי כותרות לבחירה
6. כותרת מומלצת
7. קופי מסך מתוקן
8. הנחיית ביצוע קצרה
9. גרסה נקייה
10. QA קצר
```

## Speed Rule
Do not delay with over-analysis. Return the correction package quickly.

The first response should be actionable.

## Integration With Corrected Flow Pack V2
This cycle must follow the corrected sales flow:

```text
הבנה -> אמון -> מיקום -> מוצר -> מספרים -> אקסל -> שמירה
```

The recommended live meeting deck is 28-32 slides with appendices after closing.

## Final Rule
The slide is not repaired when it looks nicer.
The slide is repaired when it sells the next step clearly, safely and cleanly.
