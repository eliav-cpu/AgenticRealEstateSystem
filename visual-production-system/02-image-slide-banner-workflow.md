# 02 - Image / Slide / Banner Workflow

## Universal Workflow
Every visual asset follows this sequence:

```text
1. Identify asset type
2. Identify source basis
3. Define commercial role
4. Rewrite screen copy
5. Define layout hierarchy
6. Generate or edit visual
7. Run visual QA
8. Run Hebrew RTL QA
9. Produce final version
10. Produce clean version
```

## Asset Types

### Presentation Slide
Purpose:
- build investor trust
- explain a decision point
- move the client toward Excel, unit selection or reservation

Structure:
- decision headline
- short subtitle
- 3-4 cards
- one bottom message line
- clean visual hierarchy

### Banner / Social Ad
Purpose:
- stop the scroll
- create immediate value perception
- make one promise clear without exaggeration
- push to one CTA

Structure:
- one dominant headline
- one short supporting line
- 2-3 value points maximum
- logo / seal / CTA
- strong vertical or square composition

### Clean Version
Purpose:
- editable template
- future text replacement
- design reuse

Structure:
- same background
- same card zones
- same frames, lines and image areas
- no final text or only placeholder labels

## Workflow For Existing Slide Improvement

When user uploads a slide:

### Step 1 - Diagnose
Check:
- what slide this is
- what role it plays in the deck
- whether it matches the approved flow
- whether the headline is a decision headline
- whether text is readable and premium
- whether Hebrew is correct
- whether claims require verification

### Step 2 - Preserve
Identify what should stay:
- image
- composition
- colors
- card logic
- icon language
- hierarchy
- premium feeling

### Step 3 - Refine
Suggest 3-5 focused refinements:
- enlarge small text
- shorten copy
- increase whitespace
- strengthen card contrast
- soften loud color
- correct RTL
- remove logo only if requested
- preserve existing style if user liked it

### Step 4 - Production Prompt
Return a direct production prompt:

```text
Preserve the current design direction. Do not rebuild the slide. Improve only typography clarity, card emphasis, RTL alignment and the requested copy changes. Keep the same color language, same composition and same premium clean style.
```

## Workflow For Banner Improvement

When user asks to fix an existing banner:

### Hard Rule
Do not redesign the banner unless the user explicitly asks.

Default instruction:

```text
Keep the exact same banner concept, background, color palette and composition. Apply only the requested changes to text, hierarchy, sizing, logo placement, seal placement and minor image crop. Do not introduce a new style.
```

### Banner QA
Check:
- is the main number/title the largest element?
- is the CTA clear?
- is the logo not overpowering the offer?
- is the seal tasteful and not misleading?
- does the Hebrew read correctly?
- is the asset readable on mobile?

## Workflow For New Image Generation

Use when creating a new image or visual concept.

### Prompt Structure

```text
Asset type:
Audience:
Commercial goal:
Main message:
Copy to include:
Visual style:
Composition:
Colors:
Typography handling:
RTL instruction:
Do not include:
Output ratio:
Clean version required:
```

### Typography Handling
Use one of two modes:

#### Mode A - Text Included
Use only for short, simple Hebrew.

Instruction:
```text
Hebrew text must be crisp, readable, right-aligned and fully RTL. No fake letters, no distorted characters, no blurry text.
```

#### Mode B - No Final Hebrew Text
Preferred for client-ready work.

Instruction:
```text
Create the visual design without final Hebrew typography. Keep clean empty text zones and card areas so the Hebrew copy can be added later in Canva or Figma as live text.
```

## Slide Copy Compression Rule
Before visual generation, compress copy into:
- headline: 5-9 words
- subtitle: 1 short sentence
- cards: 3-4 cards, each 1-2 lines
- bottom line: 1 sentence only

## Light / Dark Variant Rule
For strategic slides:
- create Light and Dark versions
- same layout
- same hierarchy
- same copy
- same card logic
- different atmosphere only

### Light Version
- White / Cloud / Mist base
- Navy heading
- Graphite body
- CTA Blue accents
- Champagne micro-accent

### Dark Version
- PRIME Navy base
- White typography
- Champagne micro-accent
- Deep Blue active accent
- premium private-banking feeling

## Image Model Prompt Guardrails
Always include:

```text
Avoid generic Canva template feeling.
Avoid neon blue.
Avoid shiny gold.
Avoid excessive decoration.
Avoid fake Hebrew letters.
Avoid distorted faces.
Avoid changing real people identity.
```

## Final QA Checklist
Before approving any visual:
- Can the user understand it in 3 seconds?
- Is the main value obvious?
- Is the hierarchy strong?
- Is the Hebrew clean?
- Is it premium but not over-designed?
- Is there a clear action or next step?
- Is the design reusable?
- Is there a clean version?

## Final Response Format For A Slide Or Banner

```text
1. Asset identified:
2. Role in funnel/deck:
3. What to preserve:
4. What to improve:
5. Corrected copy:
6. Production prompt:
7. Clean version instruction:
8. QA notes:
```
