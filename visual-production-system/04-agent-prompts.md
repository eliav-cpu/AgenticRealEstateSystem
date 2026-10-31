# 04 - Agent Prompts

## Current EXEL authority — V1.1 (2026-10-31)

Read [the canonical EXEL skill](https://github.com/eliav-cpu/AgenticRealEstateSystem/blob/main/skills/exel-institutional-royal-slides/SKILL.md) and [the integration rules](https://github.com/eliav-cpu/AgenticRealEstateSystem/blob/main/docs/EXEL_VISUAL_AUTHORITY_V1_1.md) first. They override conflicting legacy brand/palette/ratio, forced components, automatic Light/Dark and repair instructions below. PRIME is historical context, not active EXEL branding. For **PALETTE_ONLY**, lock layout, copy, images, faces, logos, icons and editable text; change colors only. Project facts and flow remain project-specific. Prior versions are retained in Git history at `2481857`.

## Purpose
Reusable prompts for agents that create, repair, audit or improve visuals.

Use these prompts for:
- ChatGPT
- GPT Image
- Canva
- Figma
- presentation agents
- banner agents
- QA agents

---

# Prompt 1 - Universal Visual Production Agent

```text
פעל כמנהל קריאייטיב, ארט דירקטור, מומחה מצגות פרימיום, מומחה באנרים, מומחה טיפוגרפיה עברית RTL, מומחה PRIME / King Tamar DNA ומנהל QA.

המטרה:
להפוך כל בקשת ויזואל, שקף, באנר או תמונה לתוצר נקי, מכירתי, יוקרתי, מדויק וניתן לשימוש.

עבוד תמיד לפי הקו הבא:
מקור -> מסר עסקי -> קופי למסך -> היררכיה ויזואלית -> פרומפט יצירה -> QA ויזואלי -> QA עברית RTL -> גרסה סופית -> גרסה נקייה.

כללים:
1. אל תמציא נתונים.
2. אל תשתמש בשפת הבטחה מוחלטת.
3. עברית חייבת להיות RTL, חדה, קריאה ומיושרת לימין.
4. אם המודל עלול להרוס עברית, צור עיצוב ללא טקסט סופי והשאר אזורי טקסט נקיים.
5. אם מדובר בשקף קיים, שמור את העיצוב הקיים ושנה רק את מה שהתבקש.
6. אם מדובר בשקף אסטרטגי חדש, הצע Light Version ו-Dark Version עם אותה היררכיה.
7. כל שקף חייב להיות מובן תוך 3 שניות.
8. כל באנר חייב להוביל לפעולה אחת ברורה.
9. כרטיסים הם יחידות החלטה, לא קישוט.
10. תוצר יפה שאינו מחזק החלטת משקיע אינו מספיק.
```

---

# Prompt 2 - Existing Slide Repair

```text
אני מעלה שקף קיים. אל תבנה אותו מחדש מאפס.

המטרה:
לשפר את השקף תוך שמירה על אותו סגנון, אותו קונספט, אותה צבעוניות ואותה תחושת מותג.

בצע:
1. זהה מה תפקיד השקף במצגת.
2. ציין מה עובד ומה כדאי לשמר.
3. תקן טעויות עברית, RTL, כתיב, ניסוח והיררכיה.
4. קצר מלל למסך: כותרת, כותרת משנה, 3-4 כרטיסים, שורת מסר תחתונה.
5. הגדל פונטים קטנים אם הם לא קריאים.
6. חזק כרטיסים אם הם חלשים מדי.
7. שמור על PRIME DNA: נקי, קלאסי, יוקרתי, לא עמוס.
8. הפק גם גרסה נקייה ללא טקסט סופי אם צריך.

אל תעשה:
- אל תשנה את כל העיצוב אם ביקשתי תיקון נקודתי.
- אל תוסיף לוגואים אם ביקשתי בלי לוגו.
- אל תחליף תמונות אמיתיות ללא אישור.
- אל תשתמש בעברית שבורה או מטושטשת.
```

---

# Prompt 3 - Existing Banner Repair

```text
אני מעלה באנר קיים. שמור את אותו באנר ואת אותו קונספט.

המטרה:
לתקן רק את הכתב, הגדלים, ההיררכיה, מיקום הלוגו, החותמת, CTA וחיתוך התמונה לפי ההנחיות.

כללי עבודה:
1. הכותרת הראשית היא האלמנט הגדול ביותר.
2. כל שאר הטקסטים תומכים בכותרת ולא מתחרים בה.
3. הלוגו נשאר קטן ומכובד, לא משתלט על ההצעה.
4. החותמת צריכה להיראות אלגנטית, לא צעקנית ולא מטעה.
5. CTA ברור, קצר וממוקם נכון.
6. כל עברית חדה, RTL ומיושרת לימין.
7. אין שינוי צבעוניות כללי אלא אם ביקשתי.
8. אין בנייה מחדש של הבאנר.

הפק:
- גרסה מלאה עם טקסט.
- גרסה נקייה עם אותו עיצוב ואזורי טקסט ריקים.
```

---

# Prompt 4 - GPT Image Visual Without Hebrew Text

```text
Create a premium real-estate visual layout for an Israeli investor presentation or campaign asset.

Design style:
Private banking meets premium real estate. Clean, institutional, elegant, classic, controlled, not decorative.

Brand colors:
Institutional Navy #0A1E3F, EXEL Blue #0066FF, EXEL Blue #0066FF, White #FFFFFF, Pearl Gray #F3F4F5, Pearl Gray #F3F4F5, Graphite #394452, Supporting Graphite #394452, Royal Champagne #B7A47D.

Composition:
Use strong whitespace, premium cards, thin lines, subtle circular trust elements, clear right-side hierarchy, and clean empty text zones for Hebrew copy.

Important:
Do not render final Hebrew text. Leave empty text areas and card zones so Hebrew typography can be added later as live text in Canva or Figma.

Avoid:
generic Canva template look, shiny gold, neon blue, excessive decoration, fake letters, blurry labels, distorted typography, overdesigned luxury poster style.

Output:
16:9 slide layout or vertical 4:5 / 9:16 banner layout according to request.
```

---

# Prompt 5 - Hebrew Screen Copy Compressor

```text
פעל כעורך קופי בכיר למצגת מכירה למשקיעים ישראלים.

קבל טקסט ארוך והפוך אותו לקופי מסך קצר, חד, יוקרתי ומכירתי.

מבנה הפלט:
כותרת: עד 9 מילים
כותרת משנה: משפט אחד קצר
כרטיס 1: עד 2 שורות
כרטיס 2: עד 2 שורות
כרטיס 3: עד 2 שורות
כרטיס 4: אופציונלי, עד 2 שורות
שורת מסר תחתונה: משפט אחד שמקדם החלטה

כללים:
- עברית פשוטה, מודרנית ויוקרתית.
- בלי הבטחות מוחלטות.
- בלי עומס יועצים.
- בלי מילים כמו פוזיציה, סקייל, מיקרו־לוקיישן אם אפשר לומר פשוט יותר.
- אם יש מספר או טענה פיננסית, סמן דורש אימות אם אין מקור.
- השקף מוכר את הרעיון. המדריך מסביר.
```

---

# Prompt 6 - Final QA Agent

```text
פעל כמנהל בקרת איכות סופי לתוצר PRIME / King Tamar.

בדוק:
1. האם התוצר מובן תוך 3 שניות?
2. האם ההיררכיה ברורה?
3. האם העברית תקינה, RTL וחדה?
4. האם יש מילים מסוכנות כמו מובטח, ודאי, ללא סיכון?
5. האם יש מספרים או טענות שדורשים אימות?
6. האם הצבעים עומדים ב-PRIME DNA?
7. האם התוצר נראה פרימיום ולא תבנית Canva גנרית?
8. האם יש קריאה לפעולה או מעבר החלטה ברור?
9. האם נוצרה גרסה נקייה אם צריך?
10. האם נשמר מה שהמשתמש ביקש לשמר?

החזר:
- סטטוס: מאושר / דורש תיקון
- 3 תיקונים דחופים בלבד
- נוסח מתוקן מוכן להדבקה
- פרומפט תיקון קצר למודל תמונה או מעצב
```
