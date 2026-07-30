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
  - H `Conference Location`
  - I `Estimated Cost/revenue`
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
- **There is no longer a `Payment to Speaker` column.** It was merged into
  `Estimated Cost/revenue` (I) on July 30, 2026 — one signed column, see below.
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

### Dates (B, C, D, Q, R)
- `Due Date` = the application deadline. The application doc filename often encodes it as
  `YYMMDD_` — confirm rather than assume.
- `Conference Date` = format as `MM/DD - MM/DD/YYYY` for multi-day, `MM/DD/YY` for single-day.
- Leave `Second Round Due`, `Award Notification Date`, and `Important Reporting Dates` **blank if
  not published**. Check the conference site AND the application form itself — Google Forms often
  state the notification date when the website doesn't. If the form is sign-in restricted
  (`FAIpQLS` links return 401 to any fetch), ask Erin what it says rather than estimating.
- **Month-only dates: write them as text.** If a conference publishes only "November 2026" for
  notification, `USER_ENTERED` coerces that to `11/1/26` — a day nobody published. Write the
  month as a text string with `valueInputOption: RAW` instead, and read it back to confirm it
  didn't get coerced.

### Conference Name (E) + Organization (F) — hyperlinked
Write both as live hyperlink formulas with `valueInputOption: USER_ENTERED`:
```
=HYPERLINK("https://www.example.org/conference","ACD49: Enduring Optimism")
```

### Submitted Title (G)
The **exact** session/proposal title as submitted. Verbatim from the application doc.

### Conference Location (H)
City and state/country of the conference, in the conference's own framing
(`Philadelphia, PA`, `Bozeman, Montana`). Blank if the venue isn't announced yet.

Location is also the sanity check on the cost formula below — the formula assumes airfare, so a
conference within driving or train distance of the speakers means the number is too high. Flag it.

### Estimated Cost/revenue (I) — a SIGNED, LIVE FORMULA, never a typed number
One signed column carries both directions (it absorbed the old `Payment to Speaker` column):

- **Unpaid opportunity (almost always):** the cost formula, **negative** — money A+A spends.
- **Conference pays the speaker:** that honorarium as a **positive** number, typed in directly.
  Only when the opportunity explicitly states speakers are paid.

Never leave it blank, and never write an unsigned cost — a positive value means A+A gets paid.

The math the formula implements (then negates):
```
Estimated Cost = ($500 x presenters)            <- air travel, per presenter
               + ($100 x presenters x days)     <- per diem, per person per day
               + ($300 x (days + 1))            <- one hotel room, one extra night
```
- `presenters` = count of comma-separated first names in column J.
- `days` = conference length from column D (`end date - start date + 1`; a single date = 1 day).
- The room is billed for **days + 1** nights (arrive the night before), one room total — not one
  room per presenter.

Paste this into I for the new row (adjust the row number), with
`valueInputOption: USER_ENTERED`. Note the leading `-` on the result:
```
=IFERROR(LET(d,TRIM(D2),n,IF(TRIM(J2)="",0,COUNTA(SPLIT(J2,","))),e,IF(ISNUMBER(SEARCH("-",d)),TRIM(REGEXEXTRACT(d,"-\s*(.+)$")),d),s,IF(ISNUMBER(SEARCH("-",d)),TRIM(REGEXEXTRACT(d,"^([^-]+)")),d),y,REGEXEXTRACT(e,"(\d{2,4})$"),sf,IF(REGEXMATCH(s,"^\d+[/-]\d+[/-]\d+$"),s,s&"/"&y),days,DATEVALUE(e)-DATEVALUE(sf)+1,IF(OR(d="",n=0),"",-(n*500+n*100*days+300*(days+1)))),"")
```

It handles `10/02 - 10/03/2026`, `11/1/26 - 11/3/26` (start date missing its year), and single
dates like `05/27/26`. Blank date or blank speakers returns blank; junk in the date column
(e.g. a conference name) falls through to blank rather than `#VALUE!`.

Format the cell as currency (`$#,##0`) after writing, or the result shows as a bare `-1200`:
```
{"repeatCell":{"range":{"sheetId":0,"startRowIndex":1,"endRowIndex":2,"startColumnIndex":8,"endColumnIndex":9},
 "cell":{"userEnteredFormat":{"numberFormat":{"type":"CURRENCY","pattern":"$#,##0"}}},
 "fields":"userEnteredFormat.numberFormat"}}
```
Use the plain `$#,##0` pattern — it renders negatives as `-$4,200`. **Do not add red or
parenthesis negative formatting** unless Erin asks; it isn't the column's convention.

If `repeatCell` silently doesn't take on a cell, use `updateCells` with the same range and
`fields: "userEnteredFormat.numberFormat"` — that works where repeatCell occasionally won't.

Notes:
- Sanity-check the result. `"Erin, Bee, etc."` in column J counts as **3** presenters — flag
  junk entries rather than trusting the number.
- If Erin gives real numbers (an actual flight quote, a comped room, a local event with no
  airfare), hardcode hers instead and tell her you replaced the formula on that row. Keep the
  sign convention when you do.
- **Rows predating July 30, 2026 still hold unsigned positive costs** (e.g. ACD49 `$1,600`,
  ACSA113 `$2,800`), so the column mixes conventions and won't sum meaningfully yet. Don't
  silently rewrite those historical rows; offer to flip them and let Erin decide.

### A+A Speakers (J) + A+A Point Person (P)
- Speakers = first names of everyone presenting, comma-separated (`Erin, Abri`), taken from the
  application's presenter + additional-presenter fields.
- **The comma-separated count drives the Estimated Cost formula** — keep it clean first names
  only, no "etc." or trailing commas.
- Point Person = whoever is responsible for submitting.

### Google Drive Folder (K)
Hyperlink to the opportunity's Drive folder. If there's no folder yet, hyperlink the application
doc itself and flag to Erin that a proper folder may be wanted.

### Quick Description (L) — the CONFERENCE, not our submission
- **Under 3 sentences.** Honor that limit literally; no padding with semicolons or em dashes.
- Describe the **conference itself** — its theme, host, and what it's about. Our session title
  belongs in the Submitted Title column, not here.
- **Lead with the category we submitted under** (e.g. "Submitted under: Practitioner Project
  (10-15 min presentation + 10 min discussion).") — that context is worth keeping.

### Primary Audience (M)
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
5. Write the full row into row 2 with `valueInputOption: USER_ENTERED` so the hyperlinks and the
   Estimated Cost/revenue formula resolve. Apply currency formatting to that cell.
6. **Read row 2 back and verify** — confirm each value landed under the header it belongs to, that
   no value was truncated or shifted, and that Estimated Cost/revenue computed a sane number with
   the **right sign** rather than blank or `#VALUE!`.
7. Reply to Erin with a short table of what was filled, an explicit list of what was left blank
   and why, and **always include the clickable link back to the sheet.**

## Watch-outs

- **Column drift mid-task.** Erin edits the sheet's structure while you work — she has both added
  a column (`Conference Location`) and merged two away (`Payment to Speaker`) mid-task. Everything
  to the right shifts. Re-read the header (`A1:V1`) and re-verify every cell you wrote before
  declaring done.
  - Sheets **moves existing cells with the insert/delete and auto-retargets formula references**,
    so the cost formula keeps working — but read it back with
    `valueRenderOption: FORMULA` to confirm it now points at the new speaker column, not a
    stale one.
  - Number formatting follows the cell too, but re-check it rather than assuming.
- **Commas survive fine, but verify anyway.** Read the row back after writing; a value like
  `Erin, Abri` landing as `Erin,` means something went wrong upstream.

## Tooling — gws CLI

Use the `gws` CLI (installed and authed). It prints a `Using keyring backend:` line to stderr —
pipe through `tail -n +2` or `grep -v 'keyring backend'` when parsing JSON.

Read the header (go past T so a newly added column shows up):
```
gws sheets +read --spreadsheet 1jXtPAZmpNpPwUTeU_nwbsPhz833uFFT93Pm74o4uflg \
  --range 'CURRENT!A1:V1' --format csv 2>/dev/null | grep -v 'keyring backend'
```

Read a formula back to confirm its references after a column shift:
```
gws sheets spreadsheets values get \
  --params '{"spreadsheetId":"1jXtPAZmpNpPwUTeU_nwbsPhz833uFFT93Pm74o4uflg","range":"CURRENT!I2","valueRenderOption":"FORMULA"}' \
  2>/dev/null | grep -v 'keyring backend'
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
