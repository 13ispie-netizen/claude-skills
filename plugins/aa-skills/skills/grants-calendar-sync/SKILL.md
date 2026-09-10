---
name: grants-calendar-sync
description: >
  Rebuild the "Annual Calendar" tab of A+A's Grant Status Google Sheet from the "FUTURE LOOKING"
  tab, as a month-by-month view of the highlighted (priority) grants. Use whenever Erin says
  "sync the calendar", "grants calendar sync", "update the annual calendar", "rebuild the grant
  calendar", "I updated FUTURE LOOKING", or asks why the calendar and the grant list disagree.
  Google Sheets only -- this skill has nothing to do with Notion.
---

# Grants Calendar Sync

One direction only: **FUTURE LOOKING → Annual Calendar**, both tabs of the same spreadsheet
(`1UrHVT6g9lloJSiagXrrFl1WYy7ttySoccbqZ3Ps79vQ`). The calendar is a rebuilt artifact; never
hand-edit it and expect the edit to survive a sync.

## Run it

```
python3 scripts/build_calendar.py            # dry run: prints the placement table, writes nothing
python3 scripts/build_calendar.py --apply    # duplicates the tab as backup, then rebuilds
```

Always dry-run first, show Erin the placement table, and get a yes before `--apply`.
`--apply` duplicates the tab to `Annual Calendar (pre-sync YYMMDD)` before touching anything.

Requires the `gws` CLI. Without it, stop and say so: the Google Drive connector cannot read cell
fill colors, and priority *is* the fill color, so a sync without `gws` would silently drop every
priority grant.

## What lands on the calendar

- Every **highlighted** row in FUTURE LOOKING. Highlighted means **10 or more of the 25 cells in
  columns A-Y have a non-white fill**. That threshold is not arbitrary: tinted-cell counts are
  sharply bimodal (most rows 0-3, highlighted rows 11-25). A few stray tinted cells is not a
  highlight.
- Plus anything in `ALWAYS_KEEP` (currently Graham Foundation), which Erin wants shown even when
  it isn't highlighted.

## Placement rules

A grant occupies the months from its **Revisit** date to its **DUE/Date**.

| Situation | Result |
| :--- | :--- |
| Revisit + a later due date | merged span, revisit month → due month |
| **Due date falls on day 1-7 of a month** | **span stops at the previous month** |
| No due date, or `rolling` | one month cell, and `check back reminder` appended to the text |
| Due date on/before the revisit (stale) | one month cell, **no** reminder -- it has a date, just an old one |
| Second Round Start / Second Round Due filled | a second cell or span on the same row, labelled `(2nd Round)`, same rules |

Grants whose revisit falls outside the window are reported, never silently dropped.

## Formatting

- **Column A** carries the category label on the first row of each group, bold. Everything in
  D:R is unbolded.
- **Row fill** is the category color, alternating darker/lighter down the rows. Palette is Erin's
  own, lifted from the original tab -- see `reference/rules.md`.
- **Borders**: every cell containing a grant gets a thin solid black outline on all four sides,
  merged or single. Borders are applied last, after all clearing, because clearing a border on one
  row also wipes the shared edge of its neighbour.

## Editable reference files

- `reference/categories.json` -- grant name → category. Anything missing lands in **Uncategorized**
  and is listed in the run output for Erin to assign. Never guess silently.
- `reference/labels.json` -- display-name overrides for rows whose Grant Name cell is blank or holds
  junk (e.g. the Durfee row, where an amount ended up in the Organization column).
- Window, palette, banners and `ALWAYS_KEEP` are constants at the top of the script.

## Things that have actually gone wrong

- **FUTURE LOOKING's columns move.** "Second Round Start date" and "Second Round Due" once sat where
  "Report due" and "Reporting Required" used to be, and "Preliminary Proposal Due" was deleted
  outright. The script resolves every column **by header text, not position**, and exits if a header
  is missing. Never reintroduce fixed indexes.
- **Hidden columns.** D:J were hidden from a previous layout, so the rebuilt calendar appeared to
  start in February. After a sync, check that no month column is hidden.
- **Clearing borders wipes shared edges.** A cell's bottom edge is its neighbour's top edge. Do all
  clearing first and apply every border at the end.
- **Text due dates.** `June 6`, `Feb 25th`, `August 29` are real values. Year-less dates resolve to
  the first occurrence on or after the revisit date.
- **The sheet changes constantly.** Re-read it immediately before every run; don't reuse an earlier
  read. Row numbers shift and highlights get added and removed between runs.

## Report back in chat, not in the sheet

After a run, tell Erin: new grants added, grants whose dates moved, anything Uncategorized, anything
outside the window, and any `stale-due` rows (a due date already in the past). Per the
no-caveats rule, none of that commentary goes into the spreadsheet.
