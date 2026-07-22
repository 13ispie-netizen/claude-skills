---
name: crm-extractor
description: "Extract structured CRM profile data from meeting transcripts and export as a Google Docs–compatible .docx file with a photo and formatted table. Use this skill whenever the user uploads or pastes a meeting transcript and wants to update a person's CRM record, contact profile, or people database. Trigger on phrases like \"update the profile,\" \"extract from this transcript,\" \"fill in the CRM,\" \"meeting notes,\" or any time a transcript is provided alongside a request to capture information about a person. Always use this skill when a transcript is present and the goal is structured data extraction — even if the user just says \"here's my notes from a call.\""
---

# CRM Extractor Skill

Extract structured profile data from meeting transcripts and output a Google Sheets–compatible CSV using the exact A+A CRM field schema.

## Core Principles

- **Accuracy over completeness.** Only extract what is explicitly stated.
- **Never infer, assume, paraphrase, or hallucinate.** If it wasn't said, leave the field blank.
- **Preserve proper nouns exactly as spoken**, even if imperfect.
- **All work history must be captured** — do not drop prior roles because details are incomplete.
- If an organization name is unknown, record the role and set org as "name not recalled."
- Missing dates are acceptable.

---

## Input

The user will provide a transcript as either:
- An uploaded file (PDF, .txt, .docx, etc.)
- Pasted text directly in the chat

Read the full transcript before extracting. Do not start filling fields until you have processed the complete input.

### Ask before generating
Pronouns, Adjectives to Describe, or (when applicable) Event Name for the contact log entry is unknown. 

ask all missing questions in one message before producing the file. Do not generate the document until you have the answers.

When asking for pronouns, also include the best public URL where a photo of the person can be found (e.g. their firm's website, a press page, or a profile page). Format it as a direct link and note that the user can download the photo from there and drop it into chat for embedding. Example: "I also found a photo of her at [ora.la/practice](https://www.ora.la/practice) — you can download it from there and drop it here and I'll embed it in the doc."

---

## Web Research

After extracting from the transcript, search Google and LinkedIn to fill in fields the transcript left blank. Use the person's name plus their organization or title as the search query.

### Identity Verification (required before using any web result)

You must be confident the search result is the same person before using any data from it. Confirm by matching at least **two independent identifiers** from the transcript against the search result — e.g., name + org, name + title, name + city. If you cannot confirm two identifiers, do not use that result.

- If confident: fill blank fields with web-sourced data. Mark each web-sourced value with a trailing ` [web]` so the user knows the source.
- If not confident: leave fields blank. Do not guess.
- Never overwrite a value that came from the transcript with a web result.

### Email and Phone from Gmail

Search Gmail for the person's name to find any emails exchanged with them. Use `Gmail:search_threads` with their name as the query. **Retrieve the 5 most recent threads only.** Scan results for:
- Their email address (in From/To fields)
- Their phone number (in signatures or message body)

Apply the same identity verification standard — confirm it's the same person before using any data. Mark values found this way with a trailing ` [gmail]`.

**Add each thread to the Contact Log** as a single row: Date (from thread), Format = `email`, Name = the other party (default: Erin), Description = subject line only. One row per thread — do not create multiple rows for replies within the same chain.

### Calendar Meetings

Search all three A+A calendars for recent meetings where the contact was an attendee:
- **A+A Executive Team**
- **Architecture + Advocacy**
- **Erin A+A**

Use `Google Calendar:list_events` for each calendar with a lookback of up to **2 years** from today. Scan results for events where the contact's name or email appears in the attendee list.

For each match, add a row to the Contact Log:
- **Date:** event date
- **Format:** `in-person meeting` or `zoom meeting` — infer from event title/location if possible; if ambiguous, use `meeting`
- **Name:** the contact's name
- **Description:** event title

---

## Field Schema (exact order — do not add, remove, rename, or reorder)

Output every field, in this exact order, whether or not it has a value. Blank values are output as empty (nothing after the comma).

### Basic Background Info
1. Name, including nickname
2. Pronouns
3. Last Updated (date the profile was created or last updated — always populate with today's date)
4. LinkedIn URL
4. Prefix
5. Suffix
6. Organization Name
7. Organization Title
8. Organization main purpose
9. Email
10. Phone
11. Home Address
12. Preferred Method for Receiving Updates
13. Birthday
14. Birthplace
15. Race/Ethnicity/Nationality
16. How did they find A+A?
17. Relationship to Anyone in A+A
18. Wealth Indicators + Source (salary, company shares, real estate, family inheritance, etc.)

### Personal Life
17. Hobbies/Passions
18. Marital Status + Partner Name
19. Partner's Education, Occupation, Hobbies, etc.
20. Wedding Anniversary
21. Sexual Orientation + Openness
22. Religion
23. Vacation Habits
24. Children, if any, names and ages, and occupation/hobbies, etc.
25. Siblings + Birth Order
26. Outstanding Physical Conditions, Including medical history
27. Heritage
28. Sensitive topics not to be discussed with
29. Opinions of Drinking, Smoking, Drugs, Etc.
30. Favorite Food, Lunch + Dinner Spots
31. Kind of Car(s)
32. Who are they anxious to impress?
33. Adjectives to describe
34. Most Proud Personal Achievements
35. Short-term personal goals
36. Long-range personal goals

### Professional Life
37. Employment History (Company, Location, Dates, Title)
38. Education
39. Extracurricular College Activities
40. Military Service + Discharge Rank
41. Attitude Towards Current Company
42. Major Business Competitors
43. Immediate Business Objective
44. Long-range business objective
45. Professional or Trade Associations
46. Mentors

### Giving Background
47. Process for making donations, including other decision-makers
48. Current Board Position(s)
49. Past Board Position(s)
50. Giving History (A+A + others)
51. Volunteering
52. Top advocacy and philanthropic issues
53. Reasons for supporting A+A

---

## Work History Rules

Field 36 (Employment History) must capture ALL roles mentioned across time:
- Format each role as: `Company Name | Title | Location | Dates`
- If multiple roles exist, separate them with a semicolon: `Role 1; Role 2; Role 3`
- If org name unknown: `name not recalled | Title | Location | Dates`
- Missing dates or location: leave that segment blank but keep the delimiters
- Do NOT drop a role because some details are missing

---

## Output Format

Produce a `.docx` file (Google Docs–compatible) using the `docx` npm library.

- File name: `Lastname, Firstname_[Category].docx`
  - Parse name from field 1. If only one name known, use what's available.
  - **Category** must be one of: `individual donor`, `professional`, `corporate donor`, `client`, `institutional donor`
  - If the user provided the category in their message, use it. If not, ask before generating:
    > "What category is this person? (individual donor / professional / corporate donor / client / institutional donor)"
  - Ask this alongside any other pre-generation questions (pronouns, format, etc.) — never ask in a separate message.
- **Output ONLY the file — no explanations, no commentary**
- Save to `/mnt/user-data/outputs/` and use `present_files` to deliver it

### Document structure

1. **Photo** (if confirmed via web research): embed at top, centered, ~1.5 inches tall. Use `ImageRun` with the downloaded file. If no confirmed photo, skip this block entirely.
2. **Name** as a bold Heading 1, centered, immediately below the photo.
3. **Profile table**: two-column table spanning the full content width (9360 DXA for US Letter with 1" margins).
   - Column 1 (field name): 3500 DXA, light gray shading (`F2F2F2`), bold text
   - Column 2 (value): 5860 DXA, white background
   - All cells: `ShadingType.CLEAR`, `BorderStyle.SINGLE` borders (`CCCCCC`), cell margins `{ top: 80, bottom: 80, left: 120, right: 120 }`
   - Output every field as a row, whether or not it has a value
   - Group rows under section header rows (bold, full-width, dark background `2E4057`, white text) for: Basic Background Info, Personal Life, Professional Life, Giving Background
   - Do NOT include Photo URL as a table row — it is rendered as an image, not text

### docx generation rules (from docx skill)
- Install: `npm install -g docx`
- Always set page size explicitly: US Letter `{ width: 12240, height: 15840 }` with 1" margins
- Tables need dual widths: `columnWidths` on the table AND `width` on each cell, both in DXA
- `WidthType.DXA` only — never `WidthType.PERCENTAGE` (breaks in Google Docs)
- `ShadingType.CLEAR` — never `SOLID`
- Validate after creation: `python scripts/office/validate.py`

---

## Contact Log

Add a Contact Log table at the bottom of the document, after the profile table. Leave one blank line between them.

### Table structure
Four columns:
- **Date** — 1200 DXA
- **Format** — 1700 DXA
- **Name** — 1700 DXA
- **Description / Notes** — 4760 DXA

Column widths must sum to 9360 DXA. Use the same border and cell margin style as the profile table. Header row: dark navy (`2E4057`) background, white bold text.

### Filling in the log entry

**Date:** Use the date of the current conversation unless the user states they met the person on a different day.

**Format:** Must be one of: `email`, `phone call`, `in-person meeting`, `zoom meeting`, `event`. Do not infer or assume. If the user has not explicitly stated the format, stop and ask before generating the document:
> "What was the format of this meeting? (email / phone call / in-person meeting / zoom meeting / event)"

**Name:** The name of the person Erin met with (i.e., the subject of the profile). Always populate this from the profile being created.

**Description:** Write one concise sentence summarizing the purpose of the meeting, inferred from the transcript. Do not quote the transcript.

**Special case — event:** If the format is `event`, stop and ask the user for the event name before generating:
> "What event was this? I'll use that as the description."
Then set the description to the event name (e.g., "ULI 2026 Annual Conference").

---

---

## Progressive Updates

After every interaction, scan the conversation for any clear behavioral rule the user has defined — something they explicitly said to always do, never do, or handle a specific way going forward. These can come as corrections, instructions, or preferences stated mid-conversation.

When you detect one:
1. Append it to the **User-Defined Rules** section at the bottom of this SKILL.md (copy the file to `/tmp/crm-extractor/` first if it hasn't been already).
2. Repackage the skill: `python -m scripts.package_skill /tmp/crm-extractor`
3. Present the `.skill` file immediately using `present_files` — no confirmation prompt.

Rules should be written as short, imperative statements. Examples:
- "Always include LinkedIn URL as a separate field after Email."
- "Never leave Employment History blank if a current org is known."
- "Format dates as MM/YYYY."

---

## Document Generation Scaffold

```javascript
const fs = require('fs');
const path = require('path');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        ImageRun, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, VerticalAlign } = require('docx');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

function sectionHeaderRow(label) {
  return new TableRow({ children: [
    new TableCell({
      columnSpan: 2,
      borders,
      shading: { fill: "2E4057", type: ShadingType.CLEAR },
      margins: cellMargins,
      children: [new Paragraph({ children: [new TextRun({ text: label, bold: true, color: "FFFFFF", size: 24 })] })]
    })
  ]});
}

function dataRow(field, value) {
  return new TableRow({ children: [
    new TableCell({
      width: { size: 3500, type: WidthType.DXA },
      borders, margins: cellMargins,
      shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
      children: [new Paragraph({ children: [new TextRun({ text: field, bold: true, size: 20 })] })]
    }),
    new TableCell({
      width: { size: 5860, type: WidthType.DXA },
      borders, margins: cellMargins,
      shading: { fill: "FFFFFF", type: ShadingType.CLEAR },
      children: [new Paragraph({ children: [new TextRun({ text: value || "", size: 20 })] })]
    })
  ]});
}

// Build rows — replace placeholder strings with extracted values
const rows = [
  sectionHeaderRow("Basic Background Info"),
  dataRow("Name including nickname", ""),
  dataRow("Pronouns", ""),
  dataRow("LinkedIn URL", ""),
  // ... all fields in schema order, grouped by section
  // Personal Life includes: Sexual Orientation + Openness (after Wedding Anniversary)
  // Giving Background includes: Volunteering (after Giving History), Top advocacy and philanthropic issues
];

const children = [];

// Photo block (only if confirmed photo was downloaded)
// const photoBytes = fs.readFileSync('/tmp/Lastname_Firstname_photo.jpg');
// children.push(new Paragraph({ alignment: AlignmentType.CENTER, children: [
//   new ImageRun({ data: photoBytes, transformation: { width: 108, height: 108 }, type: "jpg" })
// ]}));

children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: "FULL NAME HERE", bold: true })] }));

children.push(new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [3500, 5860],
  rows
}));

// Spacer
children.push(new Paragraph({ children: [] }));

// Contact log table
const logBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const logBorders = { top: logBorder, bottom: logBorder, left: logBorder, right: logBorder };

function logHeaderCell(text, width) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, borders: logBorders, margins: cellMargins,
    shading: { fill: "2E4057", type: ShadingType.CLEAR },
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", size: 20 })] })]
  });
}
function logDataCell(text, width) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, borders: logBorders, margins: cellMargins,
    shading: { fill: "FFFFFF", type: ShadingType.CLEAR },
    children: [new Paragraph({ children: [new TextRun({ text: text || "", size: 20 })] })]
  });
}

children.push(new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [1500, 2000, 5860],
  rows: [
    new TableRow({ children: [
      logHeaderCell("Date", 1500),
      logHeaderCell("Format", 2000),
      logHeaderCell("Description / Notes", 5860),
    ]}),
    new TableRow({ children: [
      logDataCell("MEETING_DATE", 1500),
      logDataCell("MEETING_FORMAT", 2000),
      logDataCell("MEETING_DESCRIPTION", 5860),
    ]})
  ]
}));

const doc = new Document({
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children
  }]
});

// Replace LASTNAME, FIRSTNAME and CATEGORY with extracted values
Packer.toBuffer(doc).then(buf => fs.writeFileSync('/mnt/user-data/outputs/LASTNAME, FIRSTNAME_CATEGORY.docx', buf));
```

---

## User-Defined Rules

_(Rules are appended here automatically as the user defines them during sessions.)_

- Never populate "Attitude Towards Current Company" or "Adjectives to Describe" from web research or inference. Leave both blank always — these can only come from direct conversation.

- Always ask for the person's pronouns before generating the document. Include them in the Pronouns field.
- Never list A+A or Architecture + Advocacy under Organization Name — that field is for paid jobs only. Exception: if the user explicitly states the person is paid by A+A. Instead, capture their A+A role under "Relationship to Anyone in A+A" or "How did they find A+A?"
- Always add a "Last Updated" row immediately after Pronouns in the profile table. Populate it with today's date (the date the document is being created).
- Contact Log table has four columns: Date (1200 DXA), Format (1700 DXA), Name (1700 DXA), Description / Notes (4760 DXA). The Name column contains who the profile subject met with — default is "Erin" unless stated otherwise.
- When the user says to specify a person's title or role more precisely, update the Organization Title field in the document accordingly.
- Add an "A+A Point Person" row immediately below LinkedIn URL in the profile table. Default value is "Erin" unless stated otherwise.
- When asking for pronouns, include a direct link to the best public URL where the person's photo can be found, and invite the user to download it and drop it into chat for embedding.
- Always search Gmail (Gmail:search_threads) for the person's name during profile creation to find their email address and phone number from past correspondence. Mark values found this way with [gmail].
- Always ask for "Adjectives to Describe" in the same pre-generation message as pronouns. Never skip this question.