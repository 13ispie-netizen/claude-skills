---
name: power-map
description: "Build a stakeholder/power map graphic (freeform overlapping category circles, organizations as budget-sized squares, connector lines for partners/parent orgs/shared projects) from an Excel spreadsheet. Use whenever Erin asks for a power map, stakeholder map, org ecosystem map, or landscape map built from a spreadsheet of organizations. Column names and category taxonomy vary per spreadsheet -- always confirm the mapping first, never assume it matches a previous map."
---

# Power Map Builder

Turns a spreadsheet of organizations into a stakeholder map: translucent overlapping
circles per category, each organization as a square sized by a chosen metric
(usually budget, log scale), connected by lines for partnerships, parent-org
relationships, and shared projects.

This is a **visual/graphic deliverable**, not a document. Output is a single SVG file.

## Step 0 -- Clarify the mapping (always, every time)

**Never reuse a previous map's column layout or category taxonomy.** Column
letters and header names change spreadsheet to spreadsheet. Before touching the
file, read the header row only (not the full data) and ask Erin, in one batch
via `AskUserQuestion` where the answers are genuinely ambiguous:

1. **Which column is the organization name** (becomes the square's label)?
2. **Which column is the category/grouping column**, and what are the exact
   category values that should become circles? Specifically ask:
   - Should any categories be **nested sub-groups** inside a larger circle
     (drawn ~25% size, like "Architects that get it" inside "Designers who get
     it")? Which parent do they nest under?
   - Should any categories be **merged** into another (e.g. a rare category
     folded into a bigger one)?
   - Should any categories/rows be **ignored** entirely?
   - Can an org list more than one category (comma-separated)? Confirm the
     separator.
3. **Which column drives square size** (budget, headcount, revenue, etc.)?
   Confirm it's the intended column -- don't assume "budget" is where the brief
   says it is; skim actual header names first (a past run found the brief's
   named column was wrong and the real budget data was elsewhere).
4. **Which column(s) drive connector lines?** Common patterns:
   - A "notable partners" style column -> curved solid lines.
   - A "parent org" column -> curved solid lines.
   - Paired "project lead" / "project participant" columns -> dashed lines,
     clustered by category (see Step 4). If a shared project could span dozens
     of orgs, flag the likely visual density to Erin *before* building and ask
     how to handle it (see Step 4).
5. Confirm the **output file name and destination folder** (same folder the
   source spreadsheet came from, named `YYMMDD_project_descriptive-name.svg`).

If anything about category values or partner-name matching is ambiguous once
the file is actually open (typos, categories not in the agreed taxonomy, stray
non-org text in a partners column), **stop and ask** rather than guessing --
this has come up in almost every real run (typo'd org names, a category not on
the agreed list, location strings mixed into a partners column).

## Step 1 -- Read the data in full

Read the whole sheet (not a sample) with `openpyxl`, `data_only=True`. Print
the header row and a handful of raw values from the columns identified in Step
0 before writing any placement logic, to sanity-check the mapping.

## Step 2 -- Load `power_map_template.py` and fill in CONFIG

This skill folder bundles `power_map_template.py`, the reusable engine built
and hardened across several rounds of real feedback. **Do not rewrite this
logic from scratch.** Copy it to the working output folder and edit only the
`CONFIG` block at the top:

- `SOURCE_XLSX`, `SHEET_NAME`, `HEADER_ROW`
- `COL_NAME`, `COL_CATEGORY`, `COL_PARTNERS`, `COL_PARENT`, `COL_PROJ_LEAD`,
  `COL_PROJ_PART` (0-indexed; set project columns to `None` if unused),
  `COL_BUDGET`
- `CATEGORY_ALIASES` -- map every raw category string variant to a canonical
  name; map anything to ignore to `'IGNORE'`; map merges to the target category
- `MANUAL_ALIASES` -- leave empty on the first run, then fill in after reading
  the "DROPPED" printout (see Step 3)
- `OUTPUT_SVG_PATH`, `CAPTION_TEXT`
- The `CIRCLES` dict -- one entry per top-level category with a hand-placed
  `cx, cy, r, color` and `parent=None`; nested sub-groups get `parent='Parent
  Category Name'`. Colors should draw from the brand skill (see Step 5) --
  reconcile a small brand palette against however many categories exist by
  using lighter/darker tints of the same core colors, not arbitrary hues.

The engine underneath (do not re-derive this by reasoning through placements
token-by-token -- it's a deterministic script, run it and look at the result):

- Parses categories per org, resolves aliases, drops `IGNORE` rows.
- Matches partner/parent name references back to real Column-A org names
  (exact match, then parenthetical-stripped match, then `MANUAL_ALIASES`).
  Anything still unmatched is dropped and printed -- never silently invented.
- For shared projects (lead/participant columns): groups an org's projects by
  its *primary category*, forming one cluster per (project, category) pair.
  Clusters are physically packed together inside their category circle and
  connected internally with a star pattern to an anchor org (the listed
  project lead if present, else the highest-budget member). One line then
  bridges each pair of category-clusters for the same project. This avoids
  the "hub-and-spoke to one org across the whole canvas" mess that makes
  large shared projects unreadable -- if a project spans a huge number of
  orgs, this is still the right approach; just size-check the result visually.
- Square size: log scale on the chosen metric; label font size scales with
  square size (never below 8pt).
- Placement is a Vogel/Fermat spiral search that **never accepts a colliding
  spot** -- it keeps expanding outward until it finds free space, which is
  what guarantees zero overlapping squares. Circles that can't fit their
  members **grow** to contain them (particularly small nested sub-group
  circles). Placement and growth **iterate together** until stable, because
  growing one circle can push into a neighboring circle's territory.
- Single-category orgs are constrained to never land inside a *different*
  category's circle (a real crossover) -- only inside their own circle or a
  parent/child of it. Multi-category orgs are placed in the actual geometric
  overlap between their circles (using the parent circle if one category is a
  nested sub-group, since the sub-circle itself may not reach the other
  category).
- Partner/parent-org lines render as curved (quadratic bezier) solid lines.
  Project cluster lines render as straight dashed lines. This distinction
  matters -- don't collapse them into one line style.
- The canvas viewBox is computed from the final (possibly grown) circle and
  square extents, so nothing is clipped.
- Category labels anchor to the top of that category's *actual placed
  content*, not the raw circle geometry -- otherwise a grown circle's
  geometric top can land under an unrelated neighbor's boxes.

## Step 3 -- First dry run, then fix names

Run the script. Read the printed "DROPPED" list of unmatched partner/parent
references. For each one, decide: real org with a typo/variant name (add to
`MANUAL_ALIASES` and re-run), a location string or non-org text (leave
dropped), or a genuinely missing org (leave dropped, mention it in the
wrap-up). Don't guess matches silently.

## Step 4 -- Flag anything that will be visually dense

If a shared project links an unusually large number of orgs, or a category
has far more members than others, say so *before* finalizing and offer the
tradeoff (e.g. cluster-and-bridge per Step 2 vs. dropping project lines
entirely vs. a different visual treatment). This has mattered in practice --
a naive hub-and-spoke rendering of one 40-org project looked like a hairball.

## Step 5 -- Brand styling

Read the org's brand-guidelines skill (e.g. `aa-brand-guidlines`) before
finalizing colors/typography, and reconcile the brand's accent palette with
however many category circles exist (tints/shades of the same core colors
rather than arbitrary hues).

## Step 6 -- Verify before presenting

Do not skip this -- overlap and crossover bugs are easy to introduce and easy
to miss by eye alone:

1. Programmatic check: every org from the source column appears exactly once;
   every square's size is monotonic with its metric; every org sits in the
   circle(s) implied by its category; every resolved partner/parent/project
   relationship has a corresponding line; **zero pairs of squares overlap**
   (compare actual `box_w`/`box_h` bounding boxes, not just the size used for
   placement); **zero single-category orgs fall inside a foreign circle**.
2. Visual check: render the SVG to PNG (`cairosvg`) at high resolution and
   `Read` it back, including cropped zooms into the densest clusters -- overlap
   bugs hide at full-canvas zoom.
3. Confirm the full canvas is visible (viewBox contains every grown circle and
   every square) -- growth can push content off the original canvas bounds.

## Step 7 -- Save and present

Save as `YYMMDD_project_descriptive-name.svg` in the same folder the source
spreadsheet came from (not the temp scratch folder). Present with
`mcp__cowork__present_files`. List the file's exact location. Do not write
extra script files into the deliverable folder -- keep working scripts in
scratch space and only copy the final SVG over.

## Token-efficiency notes

- All the placement math belongs in the Python script, run via bash -- never
  reason through where each square should land turn-by-turn. That's slow and
  expensive at 50-100+ orgs.
- Iterate on the *script*, not on individual squares: when something looks
  wrong (overlap, hidden label, clipped canvas), find the root cause in the
  algorithm and fix it once, rather than nudging individual coordinates by
  hand.
- Only re-render to PNG and re-`Read` when you've made a change likely to
  matter -- not after every tiny tweak.
