---
name: wetlands-invoice
description: Build the monthly South LA Wetlands invoice to Sasaki. Copies last month's invoice workbook in Drive, swaps in the new month's QuickBooks time export, freezes the prior invoice as a plain-text tab, rolls the live tabs forward to the next invoice number, and links Previously Billed off the frozen tab. Use whenever Erin says "build the wetlands invoice", "next Sasaki invoice", "invoice 002", "monthly wetlands billing", or hands over a Timesheet Detail by Employee export for this project.
---

# South LA Wetlands Monthly Invoice

Builds invoice N from invoice N-1. The workbook is self-referential: every month's file contains a frozen copy of the prior invoice, which is what feeds the Previously Billed column.

## Fixed references

| Thing | Value |
| :-- | :-- |
| Drive folder (invoices) | `1SF5SBI8FBiwgarggWnpJLcah4zYIuzOd` |
| Remapped budget workbook | `1pKFTq7FVusnLHjUtAcq1bDVgx1j7mnbMOxAnZGjth-Q` |
| Contract amounts + sub-tasks | `reference/task-map.md` (read this, not the budget workbook) |
| File naming | `YYMMDD_Sasaki_South LA Wetlands_invoice{NNN}` |
| Invoice number cell | `INV-{NNN}!A8` = `Sasaki-Wetlands-{NNN}` |

Use the `gws` CLI where available (`gws sheets spreadsheets ...`). In Cowork, use the Google Sheets/Drive connector instead. Never read this workbook with Drive's `read_file_content` -- it dumps all seven tabs and is the single most expensive call in the whole job. Read named ranges with `valueRenderOption: FORMULA`.

## Inputs

Ask for both before starting:

1. **The month being billed** (e.g. September 2026) and the invoice number.
2. **The QuickBooks time export** (`Timesheet Detail by Employee.xlsx`). Erin either attaches it or drops it in a dated invoice folder under `South LA Wetlands HQ/` (e.g. `261015 Invoice/`). Check the folder first; ask if it isn't there.

## Order of operations

**Step 3 must happen before step 4.** The duplicated tab is flattened to values while it still points at the *old* Sheet1. Replace Sheet1 first and you freeze the new month's numbers into the archive, which silently corrupts Previously Billed and every invoice after it.

### 1. Copy the workbook

Find the most recently modified spreadsheet in the invoice folder. Copy it in place, named for today's date and the new invoice number.

```
gws drive files list --params '{"q":"'\''1SF5SBI8FBiwgarggWnpJLcah4zYIuzOd'\'' in parents and trashed=false","orderBy":"modifiedTime desc","fields":"files(id,name)"}'
gws drive files copy --params '{"fileId":"<SOURCE_ID>"}' --json '{"name":"<NEW_NAME>","parents":["1SF5SBI8FBiwgarggWnpJLcah4zYIuzOd"]}'
```

Work in the copy from here on. Never edit the prior month's file.

### 2. Read the layout

Pull `INV-{prev}!A14:I60` with `valueRenderOption: FORMULA` and note the actual row numbers for: each section header, each deliverable row, each sub-task row, each Hard Costs row, the Sub-Total row, the Total Contract Amount row, and the INVOICE TOTAL row.

Do not assume row numbers carry over from last month -- rows get added as new tasks pick up hours. Do not read this tab as CSV; blank rows collapse and every row number you derive will be wrong.

### 3. Freeze the prior invoice

`duplicateSheet` the live `INV-{prev}` tab, name the copy `invoice {prev}` (lowercase, space, zero-padded -- e.g. `invoice 001`), then flatten it with a `copyPaste` of the whole tab onto itself using `pasteType: PASTE_VALUES`.

Verify the flattened tab holds numbers, not formulas, before going any further.

### 4. Swap in the new time export

Read the .xlsx locally (openpyxl) and write it over `Sheet1`. Clear `Sheet1` first, then write from A1 so a shorter month can't leave last month's rows stranded at the bottom.

Column layout, unchanged from QuickBooks: B date, F duration, I description, J Product/Service (carries the task number), K Billable Y/N, N Billable Total. Data starts at row 7.

### 5. Roll the tabs forward

`updateSheetProperties` to rename `INV-{prev}` to `INV-{NNN}` and `ACTIVITIES-{prev}` to `ACTIVITIES-{NNN}`. ACTIVITIES gets no frozen duplicate -- it describes work performed, not money owed.

### 6. Link Previously Billed

On every **sub-task row and Hard Costs row** of the live invoice, set column H to the frozen tab's column G:

```
H{row}  =  ='invoice {prev}'!G{row}
```

Column G on the prior invoice is Total Fee Earned to Date, so this makes each month cumulative. Leave the deliverable (parent) rows alone -- their H stays `=SUM(H{first child}:H{last child})`.

### 7. Update the header block

| Cell | Value |
| :-- | :-- |
| `A8` | `Sasaki-Wetlands-{NNN}` |
| `C8` | Issue date. **Check the year** -- the template has shipped with a stale one. |
| `A11` | Services through, e.g. `September 1 -  September 30` |
| `A43` (INVOICE TOTAL row) | `Sasaki-Wetlands-{NNN}` |

### 8. Add rows for tasks that are new this month

Scan `Sheet1` column J for every billable tag whose deliverable number has no row yet. For each one, look it up in `reference/task-map.md` and add a block matching the pattern already in the workbook:

```
   | 05. Community Outreach and Public Participation      <- Appendix C task name, only if the task is new
5.01 | A work plan detailing the community outreach...    | $21,841.88 | =G/E | =SUM(children) | =SUM(children) | =G-H
5.01.A | Meetings + Project Management                    |            |      | =H+I | ='invoice N-1'!G | SUMIFS
5.01.B | Presentation of Results                          |            |      | =H+I | ='invoice N-1'!G | SUMIFS
     | Hard Costs                                         |            |      | =H+I | ='invoice N-1'!G | 0
```

Rules that govern this:

- A task appears only when it has billable time this month **or** was billed previously. Never pre-populate future tasks.
- Deliverable numbers and contract amounts come from **Appendix C**. Sub-task names come from the **detailed fee proposal**. The two disagree on some numbering -- `reference/task-map.md` records which.
- Task numbers carry the leading zero, the client's convention: `5.01`, `5.01.A`, not `5.1.A`.
- Hard Costs always sits last in its block.
- Copy formatting onto new rows from the equivalent rows in the 01 block (`copyPaste` with `PASTE_FORMAT`).

Formulas for the new rows:

```
INV        I{row} = =SUMIFS(Sheet1!$N$7:$N, Sheet1!$K$7:$K, "yes", Sheet1!$J$7:$J, "*"&$A{row}&"*")
ACTIVITIES E{row} = =IFERROR(TEXTJOIN(CHAR(10), TRUE, FILTER(Sheet1!$I$7:$I, Sheet1!$K$7:$K="yes", ISNUMBER(SEARCH($A{row}, Sheet1!$J$7:$J)))), "")
```

Ranges stay open-ended (`$N$7:$N`, not `$N$7:$N$31`) so any number of time entries works without maintenance. If you find a bounded range left over from an earlier month, open it up.

The `IFERROR` matters: without it a sub-task with no hours renders `#N/A` on a tab that goes to the client.

### 9. Mirror onto ACTIVITIES

Same rows, same numbers, same order as the invoice tab, so the two read side by side. No contract amounts, no Hard Costs rows.

### 10. Verify before handing it over

Run all four. Report any failure rather than quietly fixing it.

1. **Total ties out.** INVOICE TOTAL must equal `=SUMIF(Sheet1!K7:K,"yes",Sheet1!N7:N)`. If it doesn't, the gap is time tagged to something no row matches -- name the offending entries and their tags. This is a real recurring failure: `SEARCH` on ACTIVITIES matches loosely, `SUMIFS` on INV only honors `*` and `?`, so a tag like `5.01 A work plan...` shows up as described work on one tab and $0.00 on the other. Do not ship an invoice with that gap unexplained.
2. **No `#REF!` or `#N/A` anywhere** on INV or ACTIVITIES.
3. **The frozen tab is values, not formulas.**
4. **Row heights: 24px is the floor.** Auto-fit squeezes single-line rows to 20px, which breaks against the rest of the table. Grow rows past 24px to fit wrapped content in column E, never shrink below it.

Then present the link and state the invoice total, the billable total from the time export, and confirm they match.

## Guardrails

- The workbook carries leftover tabs from an earlier client project (`EXP`, `MILES`, `BUDGET`). Leave them alone unless asked. There are no hard-cost expenses on this project yet.
- Before clearing or overwriting any block you didn't just create, ask -- describe what's going in plain language and confirm the replacement is ready.
- Erin often has the sheet open while you work. Re-read any range immediately before writing to it, even if you read it earlier in the same session.
