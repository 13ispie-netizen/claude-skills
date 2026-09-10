# Annual Calendar: layout reference

## Tabs

| | |
| :--- | :--- |
| Spreadsheet | `1UrHVT6g9lloJSiagXrrFl1WYy7ttySoccbqZ3Ps79vQ` |
| Source | `FUTURE LOOKING` |
| Target | `Annual Calendar`, sheetId `398998318` |
| Backup written on `--apply` | `Annual Calendar (pre-sync YYMMDD)` |

## Grid

- **A** Project/category, **B** Done?, **C** Person, **D onward** one column per month.
- Window: **July 2026 → September 2027**, 15 months, columns **D:R**. Set by `WINDOW` in the script.
- Row 1: month headers (`JULY 2026`), bold, grey.
- Row 2: semester banners, merged across their month groups.
- Row 3 onward: one row per grant, grouped by category.

Banners mirror the academic pattern Erin used originally: SUMMER BREAK (Jul-Aug 26),
FALL SEMESTER (Sep-Nov 26), FINALS (Dec 26), Q1: Spring (Jan-Mar 27), FINALS (May 27),
SUMMER BREAK (Jun-Aug 27), FALL SEMESTER (Sep 27).

## Source columns

Resolved **by header text**, never by index — these have moved before.

| Field | Header contains |
| :--- | :--- |
| due | `DUE/Date` |
| revisit | `Revisit` |
| name | `Grant Name` |
| org | `Organization` + `Link their` |
| amount | `Amount` |
| 2nd round start | `Second Round Start` |
| 2nd round due | `Second Round Due` |

## Palette

Taken from Erin's pre-rebuild tab. Rows alternate darker, lighter, darker within each category.

| Category | Darker | Lighter |
| :--- | :--- | :--- |
| LA Projects | `#FFF2CC` | `#FFF8E2` |
| NY Projects | `#EAD1DC` | `#F4E8ED` |
| Capacity/General | `#D9EAD3` | `#ECF6E8` |
| Fellowship | `#D9D2E9` | `#E4E1EC` |
| Conferences | `#C9DAF8` | `#E4EDFB` |
| Uncategorized | `#D9D9D9` | `#EFEFEF` |

`NY Projects` lighter and both `Conferences` shades were derived by blending toward white; the rest
are Erin's originals. `Conferences` and `Fellowship` are categories this workflow added.

## Cell text

```
<Grant name>
(<amount>)              <- only when Amount (Range) is filled
check back reminder     <- only when there is no usable due date
```

Second-round cells read `<Grant name> (2nd Round)` and follow the same reminder rule against the
Second Round Due column.

## Order of operations when rebuilding

The sequence matters; getting it wrong leaves stray formatting behind.

1. Unmerge the whole grid area.
2. Clear values, fills and bold.
3. Clear **all** borders across the area.
4. Write headers and banners, re-merge banners.
5. Write grant rows, merge spans, apply row fills, bold the category labels.
6. Apply every grant border **last**.

Step 6 is last on purpose: clearing a border in step 3 or unmerging in step 1 removes the line
shared with an adjacent cell, so any border applied earlier can be silently destroyed.
