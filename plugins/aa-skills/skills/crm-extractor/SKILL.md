---
name: crm-extractor
description: "Extract structured CRM profile data from meeting transcripts and store it in Google Drive as a native Google Doc with a photo and formatted tables. Use this skill whenever the user uploads or pastes a meeting transcript and wants to update a person's CRM record, contact profile, or people database. Trigger on phrases like \"update the profile,\" \"extract from this transcript,\" \"fill in the CRM,\" \"meeting notes,\" or any time a transcript is provided alongside a request to capture information about a person. Always use this skill when a transcript is present and the goal is structured data extraction — even if the user just says \"here's my notes from a call.\""
---

# CRM Extractor Skill

Extract structured profile data from meeting transcripts and store a native Google Doc profile in the CRM folder, using the exact A+A CRM field schema.

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

### Conversation-Only Fields (never web-source or infer)

These fields may ONLY come from the transcript or direct conversation with Erin. Never fill them from a web search, LinkedIn, Gmail, or Calendar, and never infer them — leave blank if not explicitly stated:
- Attitude Towards Current Company
- Adjectives to describe
- Sexual Orientation + Openness
- Religion
- Outstanding Physical Conditions / Medical History

(Marital Status + Partner Name is NOT on this list — it can be filled from web research like other fields.)

### Media Mentions (News Articles & Podcasts)

For every profile, search for news articles, podcast episodes, panels, or interviews where the person is quoted or speaking. Use queries like `"[Name]" interview`, `"[Name]" podcast`, `"[Name]" news`, and `"[Name]" [Organization]`.

Apply the same Identity Verification standard below before using any result.

- Format each confirmed result as `Outlet/Podcast Name: "Title" | URL`. Separate multiple entries with a semicolon, same convention as Employment History.
- Render each entry as a clickable hyperlink in the document — link text is the outlet/title, not the raw URL (see Document Generation Scaffold).
- Mark this field ` [web]` like other web-sourced fields.
- If no confirmed mentions are found, leave the field blank. Do not include unconfirmed or ambiguous matches.
- This field applies to every profile going forward, including profiles created before this field existed. When revising an old profile that predates it, add the row and run this search even if nothing else in the profile is being updated.

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

**This list and `CRM_Profile_Template.docx` must never drift.** Any add, remove, rename, or reorder here must be made to the template's table in the same edit, and vice versa. After editing either, run:
```
python3 "~/claude-skills/plugins/aa-skills/skills/crm-extractor/scripts/check_schema_sync.py"
```
Do not consider a schema change done until this reports everything in sync.

### Basic Background Info
1. Name, including nickname
2. Pronouns
3. Last Updated (date the profile was created or last updated — always populate with today's date)
4. LinkedIn URL
5. A+A Point Person (default: Erin, unless stated otherwise)
6. Media Mentions + Links (news articles, podcasts, interviews, etc. where they are quoted or speaking — rendered as clickable hyperlinks; see Web Research and Document Generation Scaffold)
7. Prefix
8. Suffix
9. Organization Name
10. Organization Title
11. Organization main purpose
12. Email
13. Phone
14. Home Address
15. Preferred Method for Receiving Updates
16. Birthday
17. Birthplace
18. Race/Ethnicity/Nationality
19. How did they find A+A?
20. Relationship to Anyone in A+A
21. Wealth Indicators + Source (salary, company shares, real estate, family inheritance, etc.)

### Personal Life
22. Hobbies/Passions
23. Marital Status + Partner Name
24. Partner's Education, Occupation, Hobbies, etc.
25. Wedding Anniversary
26. Sexual Orientation + Openness
27. Religion
28. Vacation Habits
29. Children (names, ages, occupation/hobbies)
30. Siblings + Birth Order
31. Outstanding Physical Conditions / Medical History
32. Heritage
33. Sensitive Topics Not to Be Discussed
34. Opinions on Drinking, Smoking, Drugs, Etc.
35. Favorite Food, Lunch + Dinner Spots
36. Kind of Car(s)
37. Who are they anxious to impress?
38. Adjectives to describe
39. Most Proud Personal Achievements
40. Short-term personal goals
41. Long-range personal goals

### Professional Life
42. Employment History (bulleted, reverse-chronological — see List Field Formatting Rules)
43. Education (bulleted, reverse-chronological — see List Field Formatting Rules)
44. Extracurricular College Activities
45. Military Service + Discharge Rank
46. Attitude Towards Current Company
47. Major Business Competitors
48. Immediate Business Objective
49. Long-range business objective
50. Professional or Trade Associations (bulleted, reverse-chronological — see List Field Formatting Rules)
51. Mentors

### Giving Background
52. Process for Making Donations (incl. other decision-makers)
53. Current Board Position(s) (bulleted, reverse-chronological — see List Field Formatting Rules)
54. Past Board Position(s) (bulleted, reverse-chronological — see List Field Formatting Rules)
55. Giving History (A+A + others)
56. Volunteering (bulleted, reverse-chronological — see List Field Formatting Rules)
57. Top advocacy and philanthropic issues
58. Reasons for supporting A+A

---

## List Field Formatting Rules

These fields must be rendered as **bulleted lists, most recent entry first**: Employment History, Education, Professional or Trade Associations, Current Board Position(s), Past Board Position(s), Volunteering.

Each entry follows this exact format:
```
- Company/Organization | Role | City (start year - end year)
```
- Use "present" instead of an end year for an ongoing role: `(2022 - present)`
- If the org name is unknown: `- name not recalled | Role | City (start year - end year)`
- If a segment is missing (role, city, or dates), drop that segment and its surrounding delimiter rather than leaving it blank — e.g. `- Company | Role (2019 - 2021)` with no city known.
- Do NOT drop an entry because some details are missing — capture every entry mentioned across time.
- Order entries most recent to oldest. If an entry is ongoing (no end date), it sorts first.
- In the underlying field value, separate entries with a semicolon (`Entry 1; Entry 2; Entry 3`) — the semicolons are converted to separate bullet lines when rendered in the document (see `bulletedListRow` in the Document Generation Scaffold).

---

## Completeness Check (required before generating)

Before generating the document, go through all 58 fields in the Field Schema **in order, one by one**. For each field, confirm it is in one of these states:
- Filled from the transcript
- Filled from web/Gmail/Calendar research and tagged `[web]` or `[gmail]`
- Deliberately blank because it was never stated anywhere available

Do not generate the document until every field has been touched this way. A field you haven't consciously checked is not the same as a field that's genuinely blank — if you can't place a field in one of the three states above, go back and research or ask before moving on.

---

## Output Format

Build a `.docx` with the `docx` npm library, then **store it in Drive as a native Google Doc** (see "Storing the profile in Drive" below). The .docx is an intermediate, not the deliverable.

Why native Google Docs rather than a stored .docx:

- **A stored .docx can be silently corrupted in transit.** Two profiles were found damaged this way (2026-06-01 and 2026-07-28); one had `word/document.xml` destroyed and was unrecoverable, because a stored .docx keeps only a single Drive revision. A native Doc has no zip to corrupt and real revision history.
- **Contact Log appends become one `documents batchUpdate` call**, instead of download → python-docx edit → re-upload to the same file ID.
- **Links open in the browser.** A `drive.google.com/file/d/<id>/view` link on a stored .docx triggers a download instead.

Tradeoff: Google Docs substitutes the exact A+A faces (`Public Sans Black`/`ExtraLight`). Acceptable for an internal CRM record. Keep .docx for external deliverables.

- File name: `Lastname, Firstname_[Category]` (no extension on the Google Doc)
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
   - **Always hyperlink the LinkedIn URL and the Organization Name** value cells. Render each as an `ExternalHyperlink` (blue `0563C1`, underlined). For LinkedIn, the link points at the profile URL (display the URL, or "LinkedIn"). For Organization Name, link the company name to the organization's website (use a real, verified URL from research; if no URL is known, leave it as plain text — never invent one). If a value carries a `[web]`/`[gmail]` source tag, keep that tag as plain text after the hyperlink.
   - **Media Mentions + Links** renders as one or more `ExternalHyperlink`s in the same blue `0563C1`/underlined style, one per confirmed mention — not plain text. See Document Generation Scaffold.

### docx generation rules (from docx skill)
- Install: `npm install -g docx`
- Always set page size explicitly: US Letter `{ width: 12240, height: 15840 }` with 1" margins
- Tables need dual widths: `columnWidths` on the table AND `width` on each cell, both in DXA
- `WidthType.DXA` only — never `WidthType.PERCENTAGE` (breaks in Google Docs)
- `ShadingType.CLEAR` — never `SOLID`
- Validate after creation: `python scripts/office/validate.py`

---

## Storing the profile in Drive

Upload as a **native Google Doc**, into the CRM profiles folder `1aaj3JQ372IYMh7pRmNY5B5tSeKU_dGDS`.

That folder is a **Shared Drive**, so every call must pass `supportsAllDrives`. Omitting it returns `404 File not found: <valid ID>`, which reads like a bad ID or a broken upload and has caused real misdiagnosis.

Two-step conversion, verified working and cheap (no base64 through a tool call):

```bash
# 1. upload the .docx as a temp file
gws drive files create --params '{"supportsAllDrives":true}' \
  --json '{"name":"__tmp_src","parents":["1aaj3JQ372IYMh7pRmNY5B5tSeKU_dGDS"]}' \
  --upload "Lastname, Firstname_category.docx" \
  --upload-content-type "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

# 2. copy it to a native Google Doc, then trash the temp
gws drive files copy --params '{"fileId":"TMP_ID","supportsAllDrives":true}' \
  --json '{"name":"Lastname, Firstname_category","mimeType":"application/vnd.google-apps.document","parents":["1aaj3JQ372IYMh7pRmNY5B5tSeKU_dGDS"]}'
gws drive files update --params '{"fileId":"TMP_ID","supportsAllDrives":true}' --json '{"trashed":true}'
```

Conversion preserves the profile table, the five-column Contact Log, and `ExternalHyperlink` links. MCP `Google_Drive__create_file` with `base64Content` and conversion left on also works, but costs several thousand tokens of inlined base64 — prefer the gws path.

**Verify before reporting done.** Export the new Doc back to .docx and confirm it opens, both tables are present with the expected dimensions, and hyperlinks survived:

```bash
gws drive files export --params '{"fileId":"NEW_ID","mimeType":"application/vnd.openxmlformats-officedocument.wordprocessingml.document","supportsAllDrives":true}' -o check.docx
```

**Updating an existing profile:** edit the Google Doc in place with `gws docs documents batchUpdate`. Never replace a profile with a new file when one already exists — that duplicates the record. If an existing profile turns out to be corrupt and unrecoverable, say so and ask before rebuilding.

---

## Linking the profile into the person's Google Contact

Whenever you create a profile for the **first time**, paste its link into that person's Google Contact so the CRM record is reachable from the address book. Do this immediately after the profile is stored and verified.

**The only edit you may make to an existing contact is appending the single `CRM profile:` line to its notes.** Never change a name, email, phone, company, job title, address, group membership, or any existing note text. Never delete or rewrite notes — append only.

1. **Find the contact.** Zapier Google Contacts Find Contact, `search_by: "email"`, the profile subject's email. No email on file → search `search_by: "name"` with the full name. Confirm the returned record's email or name actually matches the person; Find Contact returns a nearest match and will happily hand back someone else. No genuine match → skip silently and note it in your output.
2. **Read current notes and etag.** People API GET `https://people.googleapis.com/v1/people/<ID>?personFields=names,emailAddresses,biographies,metadata`. Keep the `etag` — `updateContact` rejects a write without the current one.
3. **Idempotency.** If the notes already contain a line starting `CRM profile:`, leave the contact untouched. Do not add a second link, and do not "refresh" an existing one.
4. **Append one line.** New notes value = existing notes text, then a newline, then exactly:

   ```
   CRM profile: https://docs.google.com/document/d/<FILE_ID>/edit
   ```

   Preserve the existing text byte-for-byte above that line, including blank lines. If notes were empty, the link line is the whole value.
5. **Write it.** PATCH `https://people.googleapis.com/v1/people/<ID>:updateContact?updatePersonFields=biographies`, body `{"etag":"<ETAG>","biographies":[{"value":"<FULL NOTES>","contentType":"TEXT_PLAIN"}]}`. A 400 about the etag means the contact changed under you — re-read and retry once, then give up and report.
6. **Report it.** Say which contact got a link, and name anyone who was skipped and why (no contact found, ambiguous match, link already present).

Existing profiles get the same treatment when you happen to touch them: if a contact has no `CRM profile:` line and a profile exists for them in `1aaj3JQ372IYMh7pRmNY5B5tSeKU_dGDS`, append it. Match profiles by filename (`Lastname, Firstname_[Category]`) and use the file's `webViewLink`.

---

## Contact Log

Add a Contact Log table at the bottom of the document, after the profile table. Leave one blank line between them.

### Table structure
Five columns:
- **Date** — 1100 DXA
- **Format** — 1500 DXA
- **Name** — 1500 DXA
- **Description / Notes** — 3560 DXA
- **Notes Link** — 1700 DXA

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

**Notes Link:** A clickable hyperlink to any meeting-notes document created from that meeting (e.g., the .docx/Google Doc produced by the meeting-notes skill). Render it as an `ExternalHyperlink` with link text `Notes` pointing at the doc's URL. If no notes document exists for that row, leave the cell blank. When notes for a logged meeting are created later, add or update this link. Never invent a URL — only use a real, known document link.

---

---

## Progressive Updates

This skill's master copy lives in the `claude-skills` GitHub repo (single source of truth across Claude Code, Cowork, and claude.ai Capabilities). Never edit a cached or installed copy directly — always land changes in the repo master first.

After every interaction, scan the conversation for any clear behavioral rule the user has defined — something they explicitly said to always do, never do, or handle a specific way going forward. These can come as corrections, instructions, or preferences stated mid-conversation.

When you detect one, first classify it — do not default to appending it at the bottom and moving on:

**A. Structural** — it adds, removes, renames, or reorders a profile field, a Contact Log column, or a document-structure element (it changes what a row/column IS, not just how it gets filled in).
1. Merge it directly into the Field Schema / Document structure / Contact Log section it affects, in the repo master, renumbering as needed. Do NOT park it in User-Defined Rules — that section is prose at the bottom of the file and structural changes left there get missed later (this happened before: "A+A Point Person" existed only as a User-Defined Rule for months while the canonical Field Schema list never had it).
2. Update `CRM_Profile_Template.docx` to match in the same pass.
3. Run `scripts/check_schema_sync.py` (in this skill's folder) and confirm it reports everything in sync.
4. Commit and push the repo, then rebuild the Claude Code plugin cache.
5. Copy the file to `/tmp/crm-extractor/` (if not already done), repackage with `python -m scripts.package_skill /tmp/crm-extractor`, and present the `.skill` file via `present_files` for manual re-upload to claude.ai Capabilities — no confirmation prompt.

**B. Behavioral** — it governs how to act (sourcing rules, tone, sequencing, when to ask) without changing the schema itself.
1. Append it to the **User-Defined Rules** section at the bottom of this SKILL.md, in the repo master (copy the file to `/tmp/crm-extractor/` first if it hasn't been already).
2. Commit and push the repo, then rebuild the Claude Code plugin cache.
3. Repackage the skill: `python -m scripts.package_skill /tmp/crm-extractor`
4. Present the `.skill` file immediately using `present_files` — no confirmation prompt.

Rules should be written as short, imperative statements. Examples:
- Structural: "Add a 'Referral Source' row right after How did they find A+A?" → goes into Field Schema + template, never just a footnote.
- Behavioral: "Always include LinkedIn URL as a separate field after Email." / "Format dates as MM/YYYY."

---

## Document Generation Scaffold

```javascript
const fs = require('fs');
const path = require('path');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        ImageRun, ExternalHyperlink, AlignmentType, HeadingLevel, BorderStyle, WidthType,
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

// Hyperlinked value row — use for LinkedIn URL and Organization Name.
// linkText is what shows; url is where it points; trailing is optional plain text (e.g. a " [web]" source tag).
function linkedDataRow(field, linkText, url, trailing) {
  const valueChildren = url
    ? [new ExternalHyperlink({ link: url, children: [new TextRun({ text: linkText, size: 20, color: "0563C1", underline: {} })] })]
    : [new TextRun({ text: linkText || "", size: 20 })];
  if (trailing) valueChildren.push(new TextRun({ text: trailing, size: 20 }));
  return new TableRow({ children: [
    new TableCell({
      width: { size: 3500, type: WidthType.DXA }, borders, margins: cellMargins,
      shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
      children: [new Paragraph({ children: [new TextRun({ text: field, bold: true, size: 20 })] })]
    }),
    new TableCell({
      width: { size: 5860, type: WidthType.DXA }, borders, margins: cellMargins,
      shading: { fill: "FFFFFF", type: ShadingType.CLEAR },
      children: [new Paragraph({ children: valueChildren })]
    })
  ]});
}

// Parses "Outlet: \"Title\" | https://url ; Outlet2: \"Title2\" | https://url2"
function parseLinkEntries(value) {
  return (value || "").split(";").map(s => s.trim()).filter(Boolean).map(entry => {
    const [label, url] = entry.split("|").map(s => s.trim());
    return { label: label || url, url };
  });
}

// Same layout as dataRow, but renders the value as one or more clickable hyperlinks
// (blue 0563C1, underlined — same style as linkedDataRow). Use for Media Mentions + Links.
function mediaMentionsRow(field, value) {
  const links = parseLinkEntries(value);
  const valueParagraphs = links.length
    ? links.map(({ label, url }) => new Paragraph({
        children: [new ExternalHyperlink({
          link: url,
          children: [new TextRun({ text: label, size: 20, color: "0563C1", underline: {} })]
        })]
      }))
    : [new Paragraph({ children: [new TextRun({ text: "", size: 20 })] })];

  return new TableRow({ children: [
    new TableCell({
      width: { size: 3500, type: WidthType.DXA }, borders, margins: cellMargins,
      shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
      children: [new Paragraph({ children: [new TextRun({ text: field, bold: true, size: 20 })] })]
    }),
    new TableCell({
      width: { size: 5860, type: WidthType.DXA }, borders, margins: cellMargins,
      shading: { fill: "FFFFFF", type: ShadingType.CLEAR },
      children: valueParagraphs
    })
  ]});
}

// Same layout as dataRow, but renders the value as a bulleted list, one bullet per
// semicolon-separated entry — most recent first. Use for Employment History, Education,
// Professional or Trade Associations, Current/Past Board Position(s), and Volunteering.
function bulletedListRow(field, value) {
  const entries = (value || "").split(";").map(s => s.trim()).filter(Boolean);
  const valueParagraphs = entries.length
    ? entries.map(entry => new Paragraph({
        bullet: { level: 0 },
        children: [new TextRun({ text: entry, size: 20 })]
      }))
    : [new Paragraph({ children: [new TextRun({ text: "", size: 20 })] })];

  return new TableRow({ children: [
    new TableCell({
      width: { size: 3500, type: WidthType.DXA }, borders, margins: cellMargins,
      shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
      children: [new Paragraph({ children: [new TextRun({ text: field, bold: true, size: 20 })] })]
    }),
    new TableCell({
      width: { size: 5860, type: WidthType.DXA }, borders, margins: cellMargins,
      shading: { fill: "FFFFFF", type: ShadingType.CLEAR },
      children: valueParagraphs
    })
  ]});
}

// Build rows — replace placeholder strings with extracted values.
// Use linkedDataRow for LinkedIn URL and Organization Name, e.g.:
//   linkedDataRow("LinkedIn URL", "https://www.linkedin.com/in/...", "https://www.linkedin.com/in/...", " [web]")
//   linkedDataRow("Organization Name", "Pratt Institute", "https://www.pratt.edu/")
// Use mediaMentionsRow for Media Mentions + Links, e.g.:
//   mediaMentionsRow("Media Mentions + Links", "NPR: \"Fresh Air\" | https://npr.org/... [web]")
// Use bulletedListRow for Employment History, Education, Professional or Trade Associations,
// Current Board Position(s), Past Board Position(s), and Volunteering, e.g.:
//   bulletedListRow("Employment History", "Acme Co | Director | Los Angeles (2022 - present); Beta Inc | Manager | Chicago (2018 - 2022)")
const rows = [
  sectionHeaderRow("Basic Background Info"),
  dataRow("Name including nickname", ""),
  dataRow("Pronouns", ""),
  dataRow("LinkedIn URL", ""),
  dataRow("A+A Point Person", "Erin"),
  mediaMentionsRow("Media Mentions + Links", ""),
  // ... all fields in schema order, grouped by section
  // Personal Life includes: Sexual Orientation + Openness (after Wedding Anniversary)
  // Professional Life: use bulletedListRow for Employment History, Education, Professional or Trade Associations
  // Giving Background: use bulletedListRow for Current Board Position(s), Past Board Position(s), Volunteering (after Giving History), then Top advocacy and philanthropic issues
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
// Notes Link cell: clickable "Notes" hyperlink, or blank if no notes doc exists.
function logLinkCell(url, width) {
  const child = url
    ? new ExternalHyperlink({ link: url, children: [new TextRun({ text: "Notes", size: 20, style: "Hyperlink", color: "0563C1", underline: {} })] })
    : new TextRun({ text: "", size: 20 });
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, borders: logBorders, margins: cellMargins,
    shading: { fill: "FFFFFF", type: ShadingType.CLEAR },
    children: [new Paragraph({ children: [child] })]
  });
}

const logCols = [1100, 1500, 1500, 3560, 1700];
children.push(new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: logCols,
  rows: [
    new TableRow({ children: [
      logHeaderCell("Date", logCols[0]),
      logHeaderCell("Format", logCols[1]),
      logHeaderCell("Name", logCols[2]),
      logHeaderCell("Description / Notes", logCols[3]),
      logHeaderCell("Notes Link", logCols[4]),
    ]}),
    new TableRow({ children: [
      logDataCell("MEETING_DATE", logCols[0]),
      logDataCell("MEETING_FORMAT", logCols[1]),
      logDataCell("MEETING_NAME", logCols[2]),
      logDataCell("MEETING_DESCRIPTION", logCols[3]),
      logLinkCell("NOTES_DOC_URL_OR_NULL", logCols[4]),
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
- Contact Log table has **five** columns — see "Table structure" above for the authoritative widths (Date 1100, Format 1500, Name 1500, Description / Notes 3560, Notes Link 1700; sum 9360 DXA). The Name column contains who the profile subject met with — default is "Erin" unless stated otherwise. **If you open an existing profile whose log has only four columns, add the fifth ("Notes Link") rather than working around its absence** — older files predate the current template.
- When the user says to specify a person's title or role more precisely, update the Organization Title field in the document accordingly.
- Add an "A+A Point Person" row immediately below LinkedIn URL in the profile table. Default value is "Erin" unless stated otherwise.
- When asking for pronouns, include a direct link to the best public URL where the person's photo can be found, and invite the user to download it and drop it into chat for embedding.
- Always search Gmail (Gmail:search_threads) for the person's name during profile creation to find their email address and phone number from past correspondence. Mark values found this way with [gmail].
- Always ask for "Adjectives to Describe" in the same pre-generation message as pronouns. Never skip this question.
- Contact Log table has FIVE columns: Date (1100 DXA), Format (1500 DXA), Name (1500 DXA), Description / Notes (3560 DXA), Notes Link (1700 DXA). The Notes Link column holds a clickable "Notes" hyperlink to any meeting-notes document created from that meeting; leave blank if none exists, and add/update it when notes are later created.
- Always hyperlink the LinkedIn URL value and the Organization Name value in the profile table (blue, underlined). Link the org name to the organization's real website; never invent a URL — if none is known, leave it as plain text.
- Render Employment History, Education, Professional or Trade Associations, Current Board Position(s), Past Board Position(s), and Volunteering as bulleted lists, most recent first, in the format `Company/Organization | Role | City (start year - end year)` — see List Field Formatting Rules and `bulletedListRow` in the Document Generation Scaffold.