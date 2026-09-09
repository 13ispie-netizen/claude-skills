---
name: grants-sync
description: >
  Sync A+A's "START HERE: A+A Grant Status" Google Sheet into the Grants database in Notion.
  Use whenever Erin says "sync the grants", "grants sync", "update the grants tracker",
  "pull the sheet into Notion", "push new grants to Notion", or asks why Notion and the grant
  sheet disagree. The sheet is the source of truth for grant data; Notion owns Priority and the
  planning columns. Always use this skill when the goal is reconciling those two documents.
---

# Grants Sync

Pushes edits and new grants from the **FUTURE LOOKING** tab of the Grant Status Google Sheet into
the **Grants** database in Notion. Never runs the other direction.

## The two documents

| | ID |
| :--- | :--- |
| Google Sheet | `1UrHVT6g9lloJSiagXrrFl1WYy7ttySoccbqZ3Ps79vQ` |
| Tab | `FUTURE LOOKING` (gid `1671174031`), columns A-Y |
| Notion database | `3d6c9a33bd4180cfb9d6cde298e8f896` |
| Notion data source | `collection://3d6c9a33-bd41-805f-8005-000bbcc937e5` |

Full column-to-property mapping: `reference/field-map.md`. Read it before writing anything.

## Hard rules

1. **Hyperlinks live in cell metadata, not cell text.** A CSV or values-only export silently drops
   them -- that is exactly how the original import lost every grant and org link. You must read the
   sheet through the Sheets API with a field mask that includes `hyperlink`. `scripts/fetch_sheet.py`
   does this. Never substitute a CSV export.

2. **Notion-owned columns. Never overwrite from the sheet:**
   - `Prioirity` (checkbox) -- see the Priority rule below
   - `Work Month` (select) -- derived; the sync recalculates it only when `Revisit` changes
   - `Work Window` (formula) -- read-only, never written

3. **Priority is additive, never subtractive.** Erin marks priority in *both* places: a highlighted
   row in the sheet and the checkbox in Notion. So:
   - Row highlighted in the sheet and unchecked in Notion → tick it.
   - Row not highlighted → **leave Notion alone.** Never untick.

   A "highlighted row" means 10 or more of the 25 cells in columns A-Y carry a non-white background.
   Single tinted cells are stray formatting, not a highlight, and must be ignored.

4. **Re-read Notion immediately before writing.** Per root CLAUDE.md. Someone may have edited a row
   since the last sync. The plan step does this; do not skip it and reuse an earlier read.

5. **Conflicts are flagged, not overwritten.** If a field changed in Notion since the last sync *and*
   the sheet also changed it, the sync reports it and leaves Notion as-is. Erin decides.

6. **Removals are archived** -- Erin approved automatic archiving. Still list every row to be archived
   in the run summary before applying, so nothing disappears unannounced. Archive only; never
   hard-delete.

## Workflow

### 1. Pull the sheet
```
python3 scripts/fetch_sheet.py --out <scratch>/sheet_rows.json
```
Requires the `gws` CLI (Claude Code). **If `gws` is unavailable** (e.g. Cowork), stop and tell Erin:
the Google Drive connector cannot read cell hyperlinks or fill colors, so a sync there would
re-create the original bug. Offer to run it in Claude Code instead.

### 2. Load the last-sync snapshot
`Grants HQ/Grants HQ Resources/grants-sync-state.json`, written by the previous run. Holds each
Notion page id, its match key, and the field values as of that sync. If it is missing, this is a
first run: every sheet row is compared against Notion directly and every match is recorded.

### 3. Read Notion
Run **one** SQL query via `notion-query-data-sources`, not per-page fetches. Select only the page
`url` plus the synced properties (see field-map). Save the result to `<scratch>/notion_rows.json`.

**Token discipline:** on a run *with* a snapshot, only query rows whose sheet-side values changed
plus any unmatched rows. If nothing changed in the sheet, no Notion read is needed at all -- say so
and stop.

*Fallback:* `notion-query-data-sources` has a workspace usage limit. If it returns a usage-limit
error, fall back to `notion-fetch` on the specific page ids that need checking, and tell Erin the
limit was hit.

### 4. Build the plan
```
python3 scripts/build_plan.py --sheet <scratch>/sheet_rows.json \
  --notion <scratch>/notion_rows.json --state <state.json> --out <scratch>/plan.json
```
Prints a compact summary: counts of updates, new grants, conflicts, archives, priority ticks. Do not
dump `plan.json` into the conversation.

### 5. Present and confirm
Show Erin a short table: what will change, what is new, what conflicts, what will be archived.
Wait for approval before any write.

### 6. Apply
- Updates: `notion-update-page` with `update_properties`, batching independent calls in one message.
- New grants: `notion-create-pages` into the data source.
- Archives: `notion-update-page` with `in_trash`.
- Recompute `Work Month` for any row whose `Revisit` changed. If its month option does not exist yet,
  add it with `notion-update-data-source` first.

### 7. Save state
Write the new snapshot back to `grants-sync-state.json`, then report what changed in plain language.

## Gotchas learned the hard way

- **Notion property names contain runs of spaces.** `Grant Name` and `Organization` both have long
  internal padding. Copy them verbatim from `reference/field-map.md`; a near-miss silently no-ops.
- **Row order does not match.** The original import scrambled it, and every row shares the same
  `createdTime`, so ordering cannot be used to match. Match on normalized grant name + org name.
- **Notion page ids from `substr(url,25)` lose the leading character.** Prepend it back before use.
- **A board cannot group by a formula**, and the view DSL has no month granularity for date grouping.
  That is why `Work Month` is a maintained select rather than a formula.
- **Guard junk org values.** Some sheet rows have dollar amounts or bare URLs in the Organization
  column from column drift. Never write those as an org name; report them instead.
