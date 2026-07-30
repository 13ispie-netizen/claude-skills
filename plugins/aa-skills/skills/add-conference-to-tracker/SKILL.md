---
name: add-conference-to-tracker
description: Add a conference, speaking opportunity, or session application to A+A's Conference Tracker Google Sheet as a new top-line row, pulling details from the application doc plus the conference's own website. Use whenever Erin shares a conference application, session proposal, speaking submission, or conference URL and says "add this to the conference tracker", "add my [X] application", "track this conference", or similar. Always use this skill when the goal is logging a conference/speaking opportunity into that tracker.
---

# Add Conference to Tracker

Adds one conference or speaking opportunity as a **new row on the TOP line** of A+A's Conference
Tracker, filling every column from (1) the application doc Erin submitted and (2) the
conference's own website — never inventing values.

## Fixed facts about the sheet

- **Spreadsheet ID:** `1jXtPAZmpNpPwUTeU_nwbsPhz833uFFT93Pm74o4uflg`
- **Tab title:** `CURRENT` (sheetId `0`). A second tab, `RESEARCH/FUTURE LOOKING`, exists — do NOT
  use it unless Erin says so.
- **Header is on row 1. New entries go on row 2** — insert a blank row above the existing data.
  Never append to the bottom.
- **Columns (as of July 30, 2026, A–T):**
  - A `Status`
  - B `Due Date`
  - C `Award Notification Date`
  - D `Conference Date`
  - E `Conference or Event Name` — **hyperlink** to the conference website
  - F `Organization` — **hyperlink** to the org website
  - G `Submitted Title`
  - H `Estimated Cost`
  - I `Payment to Speaker`
  - J `A+A Speakers`
  - K `Google Drive Folder`
  - L `Quick Description`
  - M `Primary Audience`
  - N `Contact Person`
  - O `Contacted?`
  - P `A+A Point Person (responsible for submitting)`
  - Q `Second Round Due`
  - R `Important Reporting Dates`
  - S `Prioirty (1-5)`
  - T `Funds Recieved?`
- **Verify the header row before every run** (`A1:T1`). Columns get added — the letters above are
  a snapshot, not a guarantee. Map values by header NAME, not by position, and re-read the header
  again after any write if Erin edits the sheet mid-task.

## Inputs

- **The application doc** (usually a Google Doc link) — the source for submitted title, speakers,
  point person, and the category submitted under.
- **The conference URL** — the source for conference dates, location, host, and theme. If Erin
  didn't give it, find it by searching the conference name; if the site is ambiguous, ask.

## Rules for each field

### Status (A)
`Pending` for a submitted-but-undecided application. `Awarded` / `Lost` only when Erin says so.

### Dates (B, C, P, Q, R)
- `Due Date` = the application deadline. The application doc filename often encodes it as
  `YYMMDD_` — confirm rather than assume.
- `Conference Date` = format as `MM/DD - MM/DD/YYYY` for multi-day, `MM/DD/YY` for single-day.
- Leave `Second Round Due`, `Award Notification Date`, and `Important Reporting Dates` **blank if
  not published**. Check the conference site AND the application form itself — Google Forms often
  state the notification date when the website doesn't. If the form is sign-in restricted
  (`FAIpQLS` links return 401 to any fetch), ask Erin what it says rather than estimating.

### Conference Name (D) + Organization (E) — hyperlinked
Write both as live hyperlink formulas with `valueInputOption: USER_ENTERED`:
```
=HYPERLINK("https://www.example.org/conference","ACD49: Enduring Optimism")
```

### Submitted Title (F)
The **exact** session/proposal title as submitted. Verbatim from the application doc.

### Estimated Cost (G) — always calculate it
Use A+A's standard travel formula:

```
Estimated Cost = ($500 x number of presenters)        <- air travel
               + ($300 x number of conference days)   <- one hotel room per day
               + ($100 x presenters x days)           <- per person per day
```

Example: 2 presenters, 2-day conference =
`(500 x 2) + (300 x 2) + (100 x 2 x 2)` = `$1,000 + $600 + $400` = **$2,000**.

Notes:
- One room total per day, not one per presenter.
- If the conference dates aren't known yet, don't guess the day count — leave blank and tell Erin
  what's missing.
- If Erin gives real numbers (an actual flight quote, a comped room, a local conference with no
  airfare), use hers instead and say which line you overrode.

### Payment to Speaker (H)
**`$0` unless the opportunity explicitly says speakers are paid.** Do not leave blank — $0 is the
real answer for almost every conference A+A applies to.

### A+A Speakers (I) + A+A Point Person (O)
- Speakers = first names of everyone presenting, comma-separated (`Erin, Abri`), taken from the
  application's presenter + additional-presenter fields.
- Point Person = whoever is responsible for submitting.

### Google Drive Folder (J)
Hyperlink to the opportunity's Drive folder. If there's no folder yet, hyperlink the application
doc itself and flag to Erin that a proper folder may be wanted.

### Quick Description (K) — the CONFERENCE, not our submission
- **Under 3 sentences.** Honor that limit literally; no padding with semicolons or em dashes.
- Describe the **conference itself** — its theme, host, and what it's about. Our session title
  belongs in column F, not here.
- **Lead with the category we submitted under** (e.g. "Submitted under: Practitioner Project
  (10-15 min presentation + 10 min discussion).") — that context is worth keeping.

### Primary Audience (L)
Who attends, in the conference's own framing (e.g. "Community designers, planners, architects,
landscape architects, allied practitioners/students").

### Everything else
- `Contact Person` / `Contacted?` — fill only if the application names a contact; otherwise blank.
- `Prioirty (1-5)` — leave blank unless Erin says.
- `Funds Recieved?` — `FALSE` for a new entry.
- **Blank, not explained.** If a value isn't published anywhere, leave the cell empty and mention
  it in the reply — never write "TBD", "N/A", or a guess into the sheet.

## Steps

1. Read the application doc and the conference website. Search the web for conference dates,
   location, host, and theme if the doc doesn't carry them.
2. Read the header row (`A1:T1`) and confirm the column layout. Build the row by header name.
3. Check whether a stub/placeholder row already exists for this same opportunity (a near-empty
   row with a matching due date) — flag it to Erin rather than silently deleting it.
4. Insert a blank row at the top (`insertDimension`, `startIndex: 1`, `endIndex: 2`,
   `inheritFromBefore: false`).
5. Write the full row into row 2 with `valueInputOption: USER_ENTERED` so the hyperlinks resolve.
6. **Read row 2 back and verify** — confirm each value landed under the header it belongs to, and
   that no value was truncated or shifted.
7. Reply to Erin with a short table of what was filled, an explicit list of what was left blank
   and why, and **always include the clickable link back to the sheet.**

## Watch-outs

- **Column drift mid-task.** If Erin adds a column while you're working, everything to its right
  shifts and your earlier writes are now in the wrong cells. Re-read the header and re-verify
  every cell you wrote before declaring done.
- **Commas survive fine, but verify anyway.** Read the row back after writing; a value like
  `Erin, Abri` landing as `Erin,` means something went wrong upstream.

## Tooling — gws CLI

Use the `gws` CLI (installed and authed). It prints a `Using keyring backend:` line to stderr —
pipe through `tail -n +2` or `grep -v 'keyring backend'` when parsing JSON.

Read the header:
```
gws sheets +read --spreadsheet 1jXtPAZmpNpPwUTeU_nwbsPhz833uFFT93Pm74o4uflg \
  --range 'CURRENT!A1:T1' --format csv 2>/dev/null | grep -v 'keyring backend'
```

Read an application Google Doc (note: `--params`, not `--document-id`):
```
gws docs documents get --params '{"documentId":"<DOC_ID>"}' 2>/dev/null | grep -v 'keyring backend'
```

Insert the blank top row:
```
gws sheets spreadsheets batchUpdate \
  --params '{"spreadsheetId":"1jXtPAZmpNpPwUTeU_nwbsPhz833uFFT93Pm74o4uflg"}' \
  --json '{"requests":[{"insertDimension":{"range":{"sheetId":0,"dimension":"ROWS","startIndex":1,"endIndex":2},"inheritFromBefore":false}}]}' \
  2>/dev/null | grep -v 'keyring backend'
```

Write the row (write the JSON body to a file first — long descriptions and quoted hyperlink
formulas are painful to inline in a shell command):
```
gws sheets spreadsheets values update \
  --params '{"spreadsheetId":"1jXtPAZmpNpPwUTeU_nwbsPhz833uFFT93Pm74o4uflg","range":"CURRENT!A2:T2","valueInputOption":"USER_ENTERED"}' \
  --json "$(cat row.json)" 2>/dev/null | grep -v 'keyring backend'
```

Patch individual cells:
```
gws sheets spreadsheets values batchUpdate \
  --params '{"spreadsheetId":"1jXtPAZmpNpPwUTeU_nwbsPhz833uFFT93Pm74o4uflg"}' \
  --json '{"valueInputOption":"RAW","data":[{"range":"CURRENT!F2","values":[["<title>"]]}]}' \
  2>/dev/null | grep -v 'keyring backend'
```

Sheet link to return to Erin:
`https://docs.google.com/spreadsheets/d/1jXtPAZmpNpPwUTeU_nwbsPhz833uFFT93Pm74o4uflg/edit?gid=0#gid=0`
