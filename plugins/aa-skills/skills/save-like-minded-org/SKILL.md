---
name: save-like-minded-org
description: Add an organization to Erin's "National Like-Minded Orgs" Google Sheet from the org's own website, filling the row with only publicly available info in the org's own language. Use whenever Erin shares an org website and says "add this to my like-minded orgs sheet", "save this org", "add this organization to the sheet", or similar. Always use this skill when the goal is capturing a peer/partner organization into that tracker.
---

# Save Like-Minded Org

Adds one organization as a new row in Erin's **National Like-Minded Orgs** sheet, pulling every
public field from the org's own website and pasting the org's own language — never synthesized.

## Fixed facts about the sheet

- **Spreadsheet ID:** `1jAIN7lrNd-BskvdLgnf2wafjsPjPUYQ-srlx7vztnA0`
- **Tab title:** `National Like-Minded Orgs` (gid `1686205038`). A second tab, `Chicago grassroots orgs`, exists — do NOT use it unless Erin says so.
- **Header is on row 1. Data starts on row 2.**
- **Columns** (A–N):
  - A `Organization`  — **hyperlink** the name to the org website (see below)
  - B `Organization Description`  — the org's OWN language, verbatim (see below)
  - C `Location`
  - D `Contact Person`  — founder / ED / president / co-founders (see below)
  - E `Contact Role`
  - F `Contact Email`
  - G `Contact phone`
  - H `Headquarters Address`
  - I `A+A Point Person`  — internal, leave blank
  - J `Status`  — internal, leave blank
  - K `Last Contact Date`  — internal, leave blank
  - L `Meeting Notes link`  — internal, leave blank
  - M `Proposed Poject Description`  — internal, leave blank
  - N `notes`  — internal, leave blank
- **Verify the header row before every run** (`A1:N1`) in case columns shift.

## Inputs

- **The org's website URL.** If Erin didn't give it, ask — never guess it, and never pull from
  any other site. All facts come from the org's own website only (their homepage / About /
  Contact / Team pages are fine; other websites are NOT).

## Rules for each field

### Organization (col A) — hyperlinked
Write the org name as a live hyperlink to its website using a formula, with
`valueInputOption: USER_ENTERED`:
```
=HYPERLINK("https://example.org/","Org Name")
```

### Organization Description (col B) — their own words, concise
- **Copy/paste the org's OWN language. Do NOT synthesize or paraphrase.**
- Prefer the **concise tagline / homepage hero** version that plainly says what they DO over a
  long "about" paragraph full of fluff. Pick the shortest verbatim wording that actually
  describes their work.

### Contact Person (col D) + Contact Role (col E)
- Use the **founder, Executive Director, President, CEO, or similar top leader.**
- **If there are two or more co-founders / co-leaders, list ALL of them**, separated by `; `.
- Role should reflect what the site actually says (e.g. "Co-Founders", "Executive Director").
  If the site only says the studio/org is "led by" people without a formal title, note that
  honestly to Erin rather than inventing a title.

### Everything else
- Fill Location, Email, Phone, Headquarters Address **only if publicly listed** on the site.
- Leave a field blank if the site doesn't publish it — do not infer.
- Leave the internal columns (I–N) blank.

## Steps

1. Get the org website URL from Erin (ask if missing).
2. Read the sheet header (`A1:N1`) to confirm the column layout hasn't changed.
3. Fetch the org's website — homepage plus About / Contact / Team pages on the SAME domain as
   needed. Extract description (verbatim), location, leadership + roles, email, phone, address.
4. Find the next empty row: read column A, next row = count of non-empty A cells + 1.
5. Write the row:
   - First write A with the `=HYPERLINK(...)` formula using `valueInputOption: USER_ENTERED`.
   - Write B–H with `valueInputOption: RAW`.
   (Two writes are fine — or one USER_ENTERED write for the whole row.)
6. Reply to Erin with a short summary of what was filled, flag anything the site didn't publish
   (blank cells) and any honesty caveats (e.g. no formal leadership title), and **always include
   the clickable link back to the sheet.**

## Tooling — gws CLI

Use the `gws` CLI (already installed and authed). Note: gws prints a `Using keyring backend:`
line to stderr — pipe through `grep -v 'keyring backend'` when parsing JSON.

Read header:
```
gws sheets spreadsheets values get \
  --params '{"spreadsheetId":"1jAIN7lrNd-BskvdLgnf2wafjsPjPUYQ-srlx7vztnA0","range":"National Like-Minded Orgs!A1:N1"}' \
  --format json 2>/dev/null | grep -v 'keyring backend'
```

Find next empty row (count col A):
```
gws sheets spreadsheets values get \
  --params '{"spreadsheetId":"1jAIN7lrNd-BskvdLgnf2wafjsPjPUYQ-srlx7vztnA0","range":"National Like-Minded Orgs!A:A"}' \
  --format json 2>/dev/null | grep -v 'keyring backend'
```

Write a row (adjust the row number, e.g. `A45`):
```
gws sheets spreadsheets values update \
  --params '{"spreadsheetId":"1jAIN7lrNd-BskvdLgnf2wafjsPjPUYQ-srlx7vztnA0","range":"National Like-Minded Orgs!A45:H45","valueInputOption":"USER_ENTERED"}' \
  --json '{"range":"National Like-Minded Orgs!A45:H45","majorDimension":"ROWS","values":[[
    "=HYPERLINK(\"https://example.org/\",\"Org Name\")",
    "<verbatim concise description>",
    "<location>",
    "<Person A; Person B>",
    "<role>",
    "<email>",
    "<phone>",
    "<address>"
  ]]}' 2>/dev/null | grep -v 'keyring backend'
```
Leave a value as `""` for anything not publicly listed.

Sheet link to return to Erin:
`https://docs.google.com/spreadsheets/d/1jAIN7lrNd-BskvdLgnf2wafjsPjPUYQ-srlx7vztnA0/edit?gid=1686205038#gid=1686205038`
