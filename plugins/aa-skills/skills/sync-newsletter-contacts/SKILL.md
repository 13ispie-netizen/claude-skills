---
name: sync-newsletter-contacts
description: Push new contacts from the "Mailing List (Peripheral Supporters)" Google Sheet into Squarespace as marketing contacts. Run this before sending a newsletter to make sure recently-added people will receive it. Use when the user says things like "sync my contacts", "upload new contacts to Squarespace", or "add new people before the newsletter".
---

# Sync newsletter contacts → Squarespace

Adds **only new rows** from the contacts Google Sheet into Squarespace as marketing-opted-in
contacts, so they're included when the user sends to "everyone who accepts marketing." Tracks
what's already been synced using a `Synced` column in the sheet, so it never double-adds.

All actions go through the **Zapier MCP** (Google Sheets + Squarespace Commerce are already
connected). No other credentials needed.

## Fixed facts about the sheet

- **Spreadsheet ID:** `1yoUxdOqCVKhNRa_TECL5CKrj7l7sl-oQ4POBVAyNDTQ`
- **Tab (worksheet) title:** `Mailing List (Peripheral Supporters)` (sheetId/gid `1983332372`)
- **Header is on row 2, not row 1.** Row 1 is a spacer (`do not copy this row`). Data starts
  on **row 3**.
- **Columns:** A `email` · B `First name` · C `Last name` · D `Company` · E `Job Title` ·
  F `Pronouns` · G `Location` · H `Category` · I `A+A Point Person` ·
  **J `Synced`** (the tracking column this skill manages)
- **Verify the layout before every run.** Columns have been inserted before (the Synced column
  moved from G → J, and more may be added). Read `A1:L8` first, confirm which column header is
  `Synced`, and use THAT column throughout — never blindly write to a fixed letter, or you may
  clobber real data (e.g. Location).
- **Synced rows are marked `yes`** (not a date). Match that convention when marking new rows.
- Only email + first/last name transfer to Squarespace. Everything else (Company, Job Title,
  Pronouns, Location, Category, Point Person) does **not** — Squarespace's Create Contact has no
  field for them. The sheet stays the master record.

### API quirks (learned; follow these to avoid failures)

- Use the **raw Sheets API** via Zapier action `_zap_raw_request` on `selected_api`
  `GoogleSheetsV2CLIAPI` (read = `execute_zapier_read_action`, write = `execute_zapier_write_action`).
- `fail_on_errors` **must be passed as the string `"true"`** (not boolean), or the tool stalls
  asking for it.
- In request **URLs**, the tab title must be URL-encoded and single-quoted:
  `%27Mailing%20List%20%28Peripheral%20Supporters%29%27` then `%21` for `!`.
  In JSON **bodies**, use the plain quoted form: `'Mailing List (Peripheral Supporters)'!A1`.
- For Squarespace `create_contact` (`selected_api` `SquarespaceCLIAPI`), pass
  `acceptsMarketing: true` and tell the action to execute without asking follow-ups (it
  sometimes asks to confirm the marketing flag — just re-run with the same params).
- **Keep `instructions` and `output` text neutral and factual** for `create_contact`. Do NOT
  use words like "error", "reject", "fail", or "placeholder" in them — this connector is
  LLM-mediated and will sometimes *echo such wording back as a fake result* instead of calling
  the API. Describe only the successful action you want.
- The `.` (single period) last-name placeholder **is accepted** by Squarespace (verified).
- A genuine duplicate returns a tool **error** whose message contains `already exists`. That is
  a SUCCESS case (the person is already in Squarespace) — count it as synced and mark the row.

## Steps

### 1. Read the sheet
First confirm the layout with a small GET to `…!A1%3AL8` and check which column header is
`Synced` (currently J). Then read all data rows (from **row 3**) through the Synced column with
a raw GET, e.g.:
```
https://sheets.googleapis.com/v4/spreadsheets/1yoUxdOqCVKhNRa_TECL5CKrj7l7sl-oQ4POBVAyNDTQ/values/%27Mailing%20List%20%28Peripheral%20Supporters%29%27%21A3%3AJ5000
```
Each returned row maps to **actual sheet row = array index + 3** (rows 1–2 are spacer + header).
Note: trailing empty cells are trimmed, so a row may come back shorter than the full column count.
The full range often exceeds the tool's token cap and gets saved to a file — parse it with a
script rather than reading it inline.

### 2. Find the new rows
A row is **to-add** when BOTH:
- Column A (`email`) is present and looks like an email (contains `@`), AND
- The `Synced` column (currently J, index 9) is blank.

Skip rows whose column A is not an email (e.g. stray first-name-only rows) and rows already
marked `yes` / `pre-existing` / dated.

### 3. Show the user and confirm
List the to-add contacts (email + name) and how many there are. **Wait for confirmation**
before writing anything to Squarespace. If none, report "nothing new to sync" and stop.

### 4. Create each contact in Squarespace
For each confirmed row, call `create_contact` (`SquarespaceCLIAPI`) with:
- `email` = column A
- `firstName` = column B, or if blank, the part of the email before `@`
- `lastName` = column C, or if blank, `.` (placeholder — Squarespace requires a last name)
- `locale` = `en-US`
- `acceptsMarketing` = `true`

Treat an "already exists" response as **success** (they're already in Squarespace).
Track the sheet row number of every success.

### 5. Mark synced rows
Write `yes` into the `Synced` column (currently J) for every successful row, in ONE batched
write to `values:batchUpdate` (method POST, `fail_on_errors` `"true"`):
```json
{"valueInputOption":"USER_ENTERED",
 "data":[{"range":"'Mailing List (Peripheral Supporters)'!J<row>","values":[["yes"]]}, ...]}
```
(Use whichever column the step-1 check confirmed is `Synced`, and match the existing marker —
`yes` today.)

### 6. Report
Summarize: N contacts added, N already-present, and any errors (with the offending email).
Remind the user the new people will be included next time they send to marketing contacts.

## Notes
- Safe to re-run anytime; already-synced rows are skipped.
- To re-sync someone (or backfill a `pre-existing` row), clear their `Synced` cell first.
- If Squarespace ever rejects the `.` last-name placeholder, fall back to reusing the first
  name as the last name.
- The same email can appear on more than one row. Create the contact once, but mark **every**
  matching row synced.
