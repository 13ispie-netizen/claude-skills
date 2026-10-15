---
name: invoice-documentation
description: Build the proof-of-work package for a Sasaki / South LA Wetlands invoice. Creates the per-invoice documentation folder in Drive, copies every doc linked in the invoice as a frozen "[for invoice YYMMDD]" snapshot, shortcuts linked folders, relinks the invoice to the copies, PDFs Kianna's weekly recap emails into a "YYMMDD weekly reports" subfolder, and drafts the invoice email to Sasaki. Use whenever Erin says "invoice documentation", "document the invoice", "back up the invoice", "prove our billing", "send the Sasaki invoice", or shares a finished wetlands invoice sheet and wants it documented. Run after the wetlands-invoice skill has built the invoice.
---

# Invoice Documentation (Sasaki / South LA Wetlands)

Turns a finished invoice workbook into a package Sasaki can audit: every link in the invoice points to a frozen copy, and the weekly recaps sit alongside.

## Fixed references

| Thing | Value |
| :-- | :-- |
| Parent documentation folder | `1imoTrwsgC8zJIck2e3aMAcRdNHpFEpcf` |
| Per-invoice folder name | `YYMMDD_sasaki invoice_documentation` (YYMMDD = invoice file-name prefix) |
| Copy name | `[for invoice YYMMDD] <original name>` |
| Recap subfolder | `YYMMDD weekly reports`, inside the per-invoice folder |
| Recap sender | `kianna@architectureandadvocacy.org`; subject contains "Week of" or "weekly" |
| Recap window | the invoice's "Services through" cell (e.g. "August 1 - October 12") |
| Email draft | Subject `{Month} Invoice`; To Accounts Payable, Cc Megan Vogt, Bcc Finance (constants at the top of the script) |

## Link rules

- Linked Google Docs, Sheets and Drive files (PDF, .docx, .xlsx): copy into the folder, then relink the invoice cell to the copy. Each copy records its original's ID, so next month's run (whose links point at this month's copies) copies the live original again with a clean name.
- Linked Drive folders: add a shortcut in the folder; the invoice link stays on the live folder.
- External links (Smartsheet, websites): leave as-is.

## Run it (Claude Code, `gws` available)

One call does everything and is safe to re-run (reuses existing folders, copies, PDFs; won't duplicate the draft):

```
python3 scripts/invoice_docs.py --invoice <spreadsheetId>
```

Flags: `--skip docs,recaps,draft` to run part of it; `--start/--end YYYY-MM-DD` if the period cell won't parse; `--stamp YYMMDD` if the file name has no date prefix. Output is a JSON report. PDF rendering needs a Chromium browser (Chrome, Brave, Edge) installed.

Don't read the workbook or the emails yourself first; the script does it. Only open things the report flags.

## Report to Erin

From the JSON report, tell Erin in a few lines: folder link, files copied, shortcuts added, links left external, recap PDFs (and which recap-like emails were skipped, e.g. meeting recaps), and that the draft is in Gmail. Remind her to attach the invoice PDF to the draft before sending. Also surface:
- `warnings` verbatim (stale shortcuts, attachments not captured, missing recaps).
- Any gap in recap coverage (e.g. first recap weeks after the period start).
- Two different labels in the invoice pointing at the same doc; it may be a wrong link.

Never remove a stale shortcut or a copy without asking Erin first.

## Cowork fallback (no `gws`)

Use the Google Drive, Sheets and Gmail connectors to do the same steps by hand: read the invoice cells' `textFormatRuns` links, Drive `copy_file` each file into the folder with the prefixed name, rewrite each cell with `updateCells` (fields `userEnteredValue,textFormatRuns`, re-reading the cell right before writing), and create the Gmail draft from the template text in `scripts/invoice_docs.py` (`draft()`). If there's no way to render PDFs, list the recap emails for Erin and skip that step. If the Sheets connector is missing, stop and ask; don't build a separate file.
