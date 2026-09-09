# Field map: FUTURE LOOKING tab → Notion Grants database

Property names are reproduced **verbatim**, including internal runs of spaces. Copy, do not retype.

| Col | Idx | Sheet header | Notion property | Type | Notes |
| :-- | :-- | :--- | :--- | :--- | :--- |
| A | 0 | DUE/Date | `DUE/Date` | date | |
| B | 1 | Application Type | `Application Type` | select | |
| C | 2 | Revisit | `Revisit` | date | drives `Work Month` |
| D | 3 | Notificaiton Date (est.) | `Notificaiton Date (est.)` | text | free text, not a date |
| E | 4 | Grant Name (Link Website) | `Grant Name                              (Link Website)` | title | **cell text → title** |
| E | 4 | *(its hyperlink)* | `Application URL` | url | **cell hyperlink → this** |
| F | 5 | Use | `Use` | select | |
| G | 6 | Organization (Link their website) | `Organization Name` | text | **name as linked text** |
| G | 6 | *(its hyperlink)* | `Organization                (Link their website)` | url | **cell hyperlink → this** |
| H | 7 | Amount (Range) | `Amount (Range)` | text | |
| I | 8 | Matching | `Matching` | select | |
| J | 9 | Google Drive Folder | `Google Drive Folder` | url | |
| K | 10 | Quick Description | `Quick Description` | text | |
| L | 11 | Grant Start Date | `Grant Start Date` | date | |
| M | 12 | Grant end date | `Grant end date` | date | |
| N | 13 | Report due | `Report due` | date | |
| O | 14 | Reporting Required | `Reporting Required` | text | |
| P | 15 | Similar Groups Funded | `Similar Groups Funded` | text | |
| Q | 16 | Contact Person | `Contact Person` | email | must be a valid address or skip |
| R | 17 | Contacted? | `Contacted?` | text | |
| S | 18 | A+A Point Person | `A+A Point Person (responsible for submitting)` | text | |
| T | 19 | Preliminary Proposal Due | `Preliminary Proposal Due` | date | |
| U | 20 | Second Round Due | `Second Round Due` | date | |
| V | 21 | Award Notification Date | `Award Notification Date` | text | |
| W | 22 | Important Reporting Dates | `Important Reporting Dates` | select | |
| X | 23 | Prioirty (1-5) | `Prioirty (1-5)` | text | note the typo, both sides |
| Y | 24 | Funds Recieved? | `Funds Recieved?` | select | note the typo, both sides |

## Row highlight → Priority

Not a column. Derived from cell fill across columns A-Y.

- Highlighted = 10 or more of the 25 cells have a non-white background.
- Highlighted → set `Prioirity` to `__YES__`.
- Not highlighted → **leave `Prioirity` untouched.** Never set `__NO__`.

## Notion-owned, never written from the sheet

| Property | Type | Why |
| :--- | :--- | :--- |
| `Prioirity` | checkbox | additive only, see above |
| `Work Month` | select | derived from `Revisit`; recalculated only when Revisit changes |
| `Work Window` | formula | read-only |

## The two link columns, restated

This is the thing the original CSV import broke, so it is worth being explicit.

A single sheet cell carries **two** pieces of information: its visible text and its hyperlink. Each
maps to a different Notion property.

- Grant Name cell → text becomes the page **title**; hyperlink becomes **Application URL**.
- Organization cell → text becomes **Organization Name**, written as markdown `[name](url)` so it
  renders as a clickable name; hyperlink also becomes the plain **Organization (Link their website)**
  URL property.

If the Organization cell's *text* is itself a URL, there is no name to carry over. Derive the
organization name from the domain, and if it cannot be determined confidently, report the row rather
than guessing.

## Date parsing

Sheet dates arrive as `MM/DD/YYYY`, `M/D/YY`, or occasionally free text like `Rolling` or
`Fall 2026`. Convert what parses to ISO `YYYY-MM-DD`. Anything that does not parse must not be
written to a date property; report it instead.

## Select options

`Application Type`, `Use`, `Matching`, `Important Reporting Dates`, and `Funds Recieved?` are select
properties. Writing an option that does not exist fails. Add missing options with
`notion-update-data-source` (`ALTER COLUMN ... SET SELECT(...)`) before writing the row.
