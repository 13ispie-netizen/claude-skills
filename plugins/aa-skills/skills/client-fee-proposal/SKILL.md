---
name: client-fee-proposal
description: "Add a client-facing 'Client Fee Proposal' tab to an A+A fee worksheet: live-linked to the internal Fee Worksheet, showing phase and sub-task totals (not sub-sub tasks), billing rates, phase summary, sub-consultants, billed hard costs, and the fee summary, formatted like the Wetlands client service fee proposal. Use whenever Erin says 'make the client-facing bill', 'client fee proposal', 'the version the client sees', 'detailed proposal for the client', or wants to share a budget built with proposal-to-budget."
---

# Client Fee Proposal

Turns an internal fee worksheet (built with `proposal-to-budget`) into the tab the client sees, in the same spreadsheet.

## Run

```
python3 scripts/build_client_tab.py <spreadsheetId>
```

- Creates the tab `Client Fee Proposal` (second tab) if it doesn't exist.
- If the tab exists, the script compares it to what it would write. **Any difference stops the script** and prints the rows: Erin may have hand-edited it, or the Fee Worksheet gained/lost sub-tasks. Show her the differences; rerun with `--force` only after she approves. When she edited the tab, fold her change into the script's standard (e.g., she removed the Qty column, so it is no longer shown) instead of overwriting it.
- Requires the `gws` CLI. The Fee Worksheet must follow the proposal-to-budget layout (labels: Phase Summary, Effort Analysis, `x.0` phases, indented `x.n` sub-tasks, `x.n.m` sub-sub tasks, Subtotal (All Phases), Sub-consultants, Hard Costs /, Fee Summary, Total Proposed Fee).

## What the client sees (top to bottom)

1. Project, Client, Fee Proposal From (Architecture + Advocacy, PO Box 18205, Los Angeles, CA 90018), Date Prepared. Product Line and Client Target Budget stay internal.
2. Billing Rates.
3. Phase Summary.
4. Services: phase rows + sub-task totals only. Columns: ED Hrs, PM Hrs, Amb Hrs, Total Hrs, Fee (role hours summed from sub-sub tasks x staff count). No Qty, no Menu ID, no notes, no Variables.
5. Sub-consultants (name + fee; internal notes hidden).
6. Hard Costs (billed amount, incl. markup).
7. Fee Summary, mirrored line for line. **Contingency appears only here**, never as a column.

Every cell is a formula pointing at the Fee Worksheet, so edits to hours, rates, Variables, staff counts, and existing rows flow through. A new sub-task needs a rerun to appear.

## Formatting (Wetlands client-tab precedent; no filled header bars)

- Public Sans throughout, gridlines hidden.
- Labels: Public Sans 10, salmon `#f49f7c`. Values: bold `#36354d` 12-14pt.
- Section titles: Public Sans 12 bold. Column headers: Public Sans 10, grey `#999999`, white background.
- Phase rows: `#efefef`, 11pt bold. Sub-task rows: white, 10pt, **not bold**.
- Total rows (Phase Summary total, Total Service Fee): `#cccccc`, bold, top rule. Section subtotals: `#efefef` bold.
- Total Proposed Fee: salmon block with white 18pt bold label; amount 15pt bold salmon.

## Before sending

Check the PDF export (the client tab starts at the page containing "Fee Proposal From"). In chat, flag anything client-visible that looks internal or wrong: typos in Fee Worksheet labels, empty hard-cost lines, internal planning columns. Fix the Fee Worksheet label, not the client tab, so the link stays live.
