---
name: sync-newsletter-contacts
description: Before a newsletter, pull new people out of the "'@@new" Google Contacts group onto the bottom of the "Mailing List (Peripheral Supporters)" Google Sheet, then push all unsynced sheet rows into Squarespace as marketing contacts. Use when the user says things like "sync my contacts", "upload new contacts to Squarespace", "add new people before the newsletter", or "pull my new contacts onto the mailing list".
---

# Sync newsletter contacts → sheet → Squarespace

Two phases, run back to back:

- **Phase A — Contacts → Sheet.** Read the `'@@new` Google Contacts group (the review queue the
  "Auto-tag New Contacts" routine fills), drop anyone already on the sheet, and append the rest to
  the bottom of the mailing-list sheet with `Synced` left blank.
- **Phase B — Sheet → Squarespace.** Push every row with a blank `Synced` (the Phase A additions
  plus anything Erin typed in by hand) into Squarespace as a marketing-opted-in contact, then mark
  those rows `yes`.

At the end, **remind Erin to remove the added people from `'@@new` by hand.** This skill never
writes to Google Contacts — Contacts access is strictly read-only.

## Fixed facts

**Google Contacts**
- Source group: **`'@@new`** = `contactGroups/441b27ff0d2a083f` (47 members as of 2026-07-30).
- Read-only. Do not add, edit, remove, or un-group anything in Google Contacts.

**The sheet**
- **Spreadsheet ID:** `1yoUxdOqCVKhNRa_TECL5CKrj7l7sl-oQ4POBVAyNDTQ`
- **Tab (worksheet) title:** `Mailing List (Peripheral Supporters)` (sheetId/gid `1983332372`)
- **Header is on row 2, not row 1.** Row 1 is a spacer (`do not copy this row` in col J). Data
  starts on **row 3**. Data currently ends around row 954 (~951 emails).
- **Columns:** A `email` · B `First name` · C `Last name` · D `Company` · E `Job Title` ·
  F `Pronouns` · G `Location` · H `Category` · I `A+A Point Person` ·
  **J `Synced`** (the tracking column this skill manages)
- **Verify the layout before every run.** Columns have been inserted before (`Synced` moved
  G → J). Read `A1:L8` first, confirm which column header is `Synced`, and use THAT column
  throughout — never blindly write to a fixed letter, or you may clobber real data.
- **Synced rows are marked `yes`** (not a date). Match that convention.
- Only email + first/last name transfer to Squarespace. Company, Job Title, Pronouns, Location,
  Category, Point Person do **not** — Squarespace's Create Contact has no field for them. The
  sheet stays the master record for segmentation.

## Access paths

Two ways in. Pick by environment:

- **Claude Code / any terminal (preferred, faster):** the `gws` CLI for both Contacts and Sheets.
  Note `gws` prints a `Using keyring backend: keyring` line to stdout — strip it (`grep -v keyring`)
  before piping into a JSON parser.
- **Chat / Cowork (no terminal):** **Zapier MCP** raw requests (Google Sheets + Squarespace
  Commerce are connected), or the Google connectors.

Squarespace has **no** `gws` equivalent — Phase B always goes through Zapier MCP.

### API quirks (learned; follow these to avoid failures)

- Zapier Sheets: use `_zap_raw_request` on `selected_api` `GoogleSheetsV2CLIAPI`
  (read = `execute_zapier_read_action`, write = `execute_zapier_write_action`).
- `fail_on_errors` **must be passed as the string `"true"`** (not boolean), or the tool stalls.
- In request **URLs**, the tab title must be URL-encoded and single-quoted:
  `%27Mailing%20List%20%28Peripheral%20Supporters%29%27` then `%21` for `!`.
  In JSON **bodies**, use the plain quoted form: `'Mailing List (Peripheral Supporters)'!A1`.
- For Squarespace `create_contact` (`selected_api` `SquarespaceCLIAPI`), pass
  `acceptsMarketing: true` and tell the action to execute without asking follow-ups.
- **Keep `instructions` and `output` text neutral and factual** for `create_contact`. Do NOT use
  words like "error", "reject", "fail", or "placeholder" — this connector is LLM-mediated and will
  sometimes *echo such wording back as a fake result* instead of calling the API. Describe only
  the successful action you want.
- The `.` (single period) last-name placeholder **is accepted** by Squarespace (verified).
- A genuine duplicate returns a tool **error** whose message contains `already exists`. That is a
  SUCCESS case — count it as synced and mark the row.
- Google People `people:batchGet` caps at 200 resource names per call; chunk at 50.

---

### 0. Confirm the sheet layout (always, before anything else)

Read `A1:L8` and confirm which column header is `Synced`. Use that column for the rest of the run.
Columns have been inserted into this sheet before.

```bash
gws sheets spreadsheets values get --params '{"spreadsheetId":"1yoUxdOqCVKhNRa_TECL5CKrj7l7sl-oQ4POBVAyNDTQ","range":"'"'"'Mailing List (Peripheral Supporters)'"'"'!A1:L8"}'
```

# Phase A — pull `'@@new` onto the sheet

### 1. Read the `'@@new` group members

```bash
gws people contactGroups get \
  --params '{"resourceName":"contactGroups/441b27ff0d2a083f","maxMembers":500}'
```
Returns `memberCount` and `memberResourceNames` (`people/c…`).

Then hydrate them in chunks of 50:
```bash
gws people people getBatchGet --params '{"resourceNames":["people/c…","people/c…"],
  "personFields":"names,emailAddresses,organizations,addresses,memberships,biographies"}'
```

Zapier equivalent — raw GET on `selected_api` `GoogleContactsCLIAPI` (or any raw-request action
that reaches Google):
`https://people.googleapis.com/v1/contactGroups/441b27ff0d2a083f?maxMembers=500`
then `https://people.googleapis.com/v1/people:batchGet?resourceNames=…&resourceNames=…&personFields=names,emailAddresses,organizations,addresses,memberships,biographies`

### 2. Map each contact to a sheet row

| Sheet column | Source on the Google Contact |
|---|---|
| A `email` | primary `emailAddresses[].value` (the one with `metadata.primary: true`, else the first) |
| B `First name` | `names[0].givenName`, credential suffixes stripped. **Leave BLANK if the contact has no name** — do not put the email local-part in the sheet (that's a Phase B / Squarespace-only fallback). |
| C `Last name` | `names[0].familyName`, credential suffixes stripped. Blank if absent (Phase B substitutes a placeholder). |
| D `Company` | `organizations[0].name` |
| E `Job Title` | `organizations[0].title` (append `, <department>` only if the title alone is meaningless) |
| F `Pronouns` | parse a `Pronouns: …` line out of `biographies[0].value` — the auto-tagger stores them there. Blank if absent. |
| G `Location` | from `addresses[0]`: `City, ST` (`city` + `region`). Blank if there's no address — do not guess from the org. |
| H `Category` | the contact's category group name(s), verbatim (table below). Blank if none matches. |
| I `A+A Point Person` | always **`Erin`** |
| J `Synced` | **leave blank** — Phase B fills it |

**Category group → sheet Category value.** As of 2026-07-30 the sheet uses the **Google Contacts
group names verbatim** — there is no translation layer, so write the group name exactly as it
appears. Column H was backfilled from Contacts on that date (247 of 951 rows filled); a blank is
still completely normal for anyone not in a category group. Never invent a value.

| Google Contacts group | Sheet `Category` |
|---|---|
| AEC Firm (`56b866188a20d8b7`) | `AEC Firm` |
| Community-Based Non-Profit (`12a592488880e312`) | `Community-Based Non-Profit` |
| Non-profit: other (`1d87800c8f4021ff`) | `Non-profit: other` |
| Gov't (`5e1e6c01098dcb01`) | `Gov't` |
| Developer (`406ebafe0fce041f`) | `Developer` |
| Foundation (`944616a8c6072b2`) | `Foundation` |
| family foundation (`53b811ba0f8d272d`) | `family foundation` |
| Event Venue (`25ba767509d554a2`) | `Event Venue` |
| Real-Estate PR (`6c58a71d8919a864`) | `Real-Estate PR` |
| no category group at all | *(blank)* |

**A contact in two or more category groups gets all of them**, comma-space separated and
alphabetical — e.g. `AEC Firm, Non-profit: other`. Do not pick a winner and do not leave it blank.

Column H carries a **non-strict dropdown** (`ONE_OF_LIST`, `strict: false`, `showCustomUi: true`)
over the nine group names plus two legacy values, `Student/Volunteer` and `Other`. Non-strict is
deliberate: Google Sheets has no native multi-select dropdown, so the list has to *warn* rather than
*reject* or the comma-joined multi-category cells would be blocked. If you ever re-set this
validation, keep `strict: false`.

Ignore the `'@Level 1–4`, roster, event, and campaign groups — they carry no Category meaning.
`Student/Volunteer` and `Other` are legacy sheet-only values with no Contacts equivalent; never
auto-assign them, and don't overwrite them if a row already has one.

**Strip credential suffixes from names.** Google Contacts routinely has them jammed into the
`familyName` field (`"Chan, AIA, Leed AP"`), which then reads as the person's surname on a
newsletter. Remove them from BOTH name fields before writing:

> AIA · FAIA · Assoc. AIA · NOMA · AICP · ASLA · FASLA · LEED / LEED AP (+ BD+C, ND, ID+C) ·
> NCARB · PE · RA · PLA · Ph.D. · PsyD · EdD · MD · DDS · JD · Esq. · CPA · MBA · MPA · MPH ·
> MSW · LCSW · RN · CFA · CFRE · PMP · MArch · MUP

Match case-insensitively on a word boundary, then clean up orphaned commas and double spaces.
Only strip from this known list — **leave unrecognized trailing tokens alone** rather than
guessing (`"Larson CAN"` stays as-is; a real surname must never be truncated). Do not strip
anything from `Company` or `Job Title` — credentials belong there.

**Skip and report separately:** any `'@@new` member with **no email address** — there's nothing to
put on a mailing list. Do not fabricate one.

### 3. Dedupe against the sheet

Read the existing sheet emails:
```bash
gws sheets spreadsheets values get --params '{"spreadsheetId":"1yoUxdOqCVKhNRa_TECL5CKrj7l7sl-oQ4POBVAyNDTQ","range":"'"'"'Mailing List (Peripheral Supporters)'"'"'!A3:J5000"}'
```
Compare **case-insensitively and trimmed** — the sheet contains trailing-space emails
(`"glh2116@columbia.edu "`) and ~9 duplicate addresses already. Drop any `'@@new` contact whose
email already appears anywhere in column A, whether that row is synced or not. Also dedupe within
the `'@@new` batch itself.

### 4. Append the new rows

Per Erin's instruction, **add all of them automatically** — no per-contact confirmation. Append to
the bottom in ONE call:

```bash
gws sheets spreadsheets values append \
  --params '{"spreadsheetId":"1yoUxdOqCVKhNRa_TECL5CKrj7l7sl-oQ4POBVAyNDTQ","range":"'"'"'Mailing List (Peripheral Supporters)'"'"'!A3","valueInputOption":"USER_ENTERED","insertDataOption":"INSERT_ROWS"}' \
  --json '{"values":[["email","First","Last","Company","Job Title","Pronouns","Location","Category","Erin",""]]}'
```
Zapier equivalent: POST
`…/values/%27Mailing%20List%20%28Peripheral%20Supporters%29%27%21A3:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS`.

Send **exactly 10 cells per row** (A–J, empty string for blanks) so nothing lands in the wrong
column. Then confirm from the response's `updates.updatedRange` which rows were written, and carry
those row numbers into Phase B. If `Synced` is not column J on this run, reorder the cells to match
the layout you confirmed in step 0.

Note how many were appended and at which rows, then **continue straight into Phase B without
pausing.** Erin's instruction (2026-07-30): do not stop for a go-ahead between phases. Run the
whole thing end to end and report once at the finish.

---

# Phase B — push the sheet into Squarespace

### 5. Re-read the sheet and find the unsynced rows

Read `A3:J5000` again (post-append). A row is **to-add** when BOTH:
- Column A (`email`) is present and contains `@`, AND
- The `Synced` column (currently J, index 9) is blank.

Each returned row maps to **actual sheet row = array index + 3**. Trailing empty cells are trimmed,
so a row may come back shorter than 10 fields — treat a missing index 9 as blank. Skip rows whose
column A isn't an email, and rows already marked `yes` / `pre-existing` / dated. The full range
often exceeds the tool's token cap and gets saved to a file — parse it with a script, not inline.

This set = the Phase A additions **+** anything Erin added by hand since the last run.

### 6. Proceed — do not wait for confirmation

**Run straight through.** Do not pause to ask permission before writing to Squarespace; Erin does
not want a checkpoint mid-run. If there's nothing to add, report "nothing new to sync" and skip to
step 9. Anything questionable (garbled names, contacts with no name, people who look like vendors
rather than newsletter audience) gets **synced anyway and flagged in the step 9 report** — she'd
rather clean up afterward than answer questions mid-run. Adding a wrong person to a mailing list is
reversible; blocking the run is the bigger cost.

### 7. Create each contact in Squarespace

For each confirmed row, call `create_contact` (`SquarespaceCLIAPI`) with:
- `email` = column A (trimmed)
- `firstName` = column B, or if blank, the part of the email before `@`
- `lastName` = column C, or if blank, `.`
- `locale` = `en-US`
- `acceptsMarketing` = `true`

Treat an "already exists" response as **success**. Track the sheet row number of every success.
The same email can appear on more than one row — create the contact once, but mark **every**
matching row synced.

### 8. Mark synced rows

**Re-read the sheet first and match by EMAIL, not by cached row number.** Erin edits this sheet
while the skill is running — during the 2026-07-30 run a row was deleted mid-run and every row
below it shifted up by one, which would have marked the wrong people. Re-read `A1:L5000`,
re-confirm the `Synced` column index from the header, then map each successful email to its
*current* row. An email that has vanished from the sheet was deleted deliberately — skip it,
don't re-add it.

Write `yes` into the `Synced` column for every successful row, in ONE batched write to
`values:batchUpdate` (POST, `fail_on_errors` `"true"`):
```json
{"valueInputOption":"USER_ENTERED",
 "data":[{"range":"'Mailing List (Peripheral Supporters)'!J<row>","values":[["yes"]]}, ...]}
```
Use whichever column step 0 confirmed is `Synced`, and match the existing `yes` marker.

### 9. Report — and hand back the `'@@new` cleanup

Summarize:
1. **Pulled from `'@@new`:** N appended to the sheet (rows X–Y), N skipped as already on the sheet,
   N skipped for having no email address.
2. **Squarespace:** N contacts added, N already present, and any errors with the offending email.
3. **⚠ Manual step for Erin — remove these people from `'@@new`.** This skill does not touch
   Google Contacts. List each person appended in Phase A as a name hyperlinked to their contact
   (`https://contacts.google.com/person/<id>`, where `<id>` is the `resourceName` minus the
   `people/` prefix), and link the group itself so she can clear it in one pass. Say plainly that
   until she removes them, they'll be re-checked (and correctly skipped as duplicates) on the next
   run — so nothing breaks if she forgets, the queue just keeps growing.

Then remind her the new people will be included next time she sends to marketing contacts.

## Notes

- Safe to re-run anytime. Phase A dedupes on email, Phase B skips already-synced rows.
- To re-sync someone (or backfill a `pre-existing` row), clear their `Synced` cell first.
- To re-pull someone from `'@@new`, delete their sheet row (or they'll dedupe out).
- If Squarespace ever rejects the `.` last-name placeholder, reuse the first name as the last name.
- Squarespace has no API for targeting a specific named mailing list — Create Contact only adds to
  the Contacts address book with the marketing opt-in, which is why the sheet holds segmentation.
