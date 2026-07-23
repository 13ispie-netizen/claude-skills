# Filling the Quick Facts Google Doc (Docs API mechanics)

The template is a two-column table. You fill the **right (value) cell** of each row. All edits go through `gws docs documents batchUpdate` on the copied doc. Work in phases and always compute indices from a **fresh** `gws docs documents get`.

Save fetched JSON to a temp file, strip any leading non-JSON line (e.g. "Using keyring backend: keyring") before `json.loads`, i.e. `raw[raw.index("{"):]`.

## Locating value cells
Walk `body.content` -> `table.tableRows` -> `tableCells`. Cell 0 is the label (match its text to find the row), cell 1 is the value cell. For each value cell collect its paragraphs with `startIndex`/`endIndex` and text.

## Phase 1 — insert text (one batchUpdate)
- For each field, insert its text at the value cell's first-paragraph `startIndex`. Multi-line content: join lines with `\n` (creates one paragraph per line).
- Compute every insert from the SAME fetch, then **sort requests by index descending** and send in one batch — higher-index inserts don't shift lower indices.
- Appending inside an existing paragraph (e.g. the pre-placed `Digital` / `Print` checkbox lines): insert at `paragraph.endIndex - 1` (before the paragraph mark) so it stays one paragraph and keeps its bullet.
- Replacing a whole cell: `deleteContentRange` `[firstStart, lastEnd - 1]` (keeps the cell's final paragraph mark, required), then insert new text at `firstStart`. To blank a cell, delete only.

## Phase 2 — formatting (re-fetch first, then one batchUpdate)
Locate paragraphs by exact text (robust against index shifts), then:
- **Bullets:** `createParagraphBullets` with `bulletPreset: "BULLET_DISC_CIRCLE_SQUARE"` over `[firstItemStart, lastItemEnd]`. Applies to every paragraph the range touches, so keep header lines outside the range.
- **Checkboxes:** same call with `bulletPreset: "BULLET_CHECKBOX"` (insurance, and the Point Person / RFP Submission boxes).
- **Inherited-bullet cleanup:** inserting lines *before* an existing bulleted paragraph makes the new lines inherit that bullet. Strip with `deleteParagraphBullets` over their range (this is how the Point Person contact lines are un-bulleted while the `Contacted?` checkbox below stays a checkbox).
- **Indent sub-items:** literal leading tabs are NOT consumed into nesting by this API. Instead: delete the tab characters, then `updateParagraphStyle` with `indentStart`/`indentFirstLine` (parent categories ~36 PT, indented sub-limits ~54 PT), `fields: "indentStart,indentFirstLine"`.
- **Text cleanups:** `replaceAllText` needs no indices. Scrub em dashes doc-wide by replacing `" — "` (space, U+2014, space) with `"; "`.

## Phase 3 — brand font
Apply A+A body font to every value cell's text via `updateTextStyle` over `[firstStart, lastEnd - 1]`:
```
textStyle: {
  weightedFontFamily: { fontFamily: "Nunito" },
  fontSize: { magnitude: 11, unit: "PT" },
  foregroundColor: { color: { rgbColor: { red: 54/255, green: 53/255, blue: 77/255 } } }  // #36354d
}
fields: "weightedFontFamily,fontSize,foregroundColor"
```
Skip empty cells. Leave label cells alone (they stay bold Public Sans).

## Gotchas
- **Checked state:** the Docs API cannot check a checklist box. Leave unchecked; tell Erin to click the applicable ones.
- A table cell must always retain at least one paragraph — never delete its final paragraph mark.
- Verify at the end: re-fetch and confirm each value cell, that checkbox lists have `glyphType: "GLYPH_TYPE_UNSPECIFIED"`, that no literal `\t` remain, and that no em dashes remain.
