---
name: board-deck-update
description: Update A+A's monthly board deck (.pptx in Drive) -- find or create the deck from the template, link it in the agenda, refresh Upcoming Board Events from the calendar, swap the grants and conference tracker screenshots, build the fundraising thermometer from QuickBooks, and write project update slides. Use whenever Erin says "update the board deck", "this month's board deck", "board slides", "refresh the deck", or names any one of these slides.
---

# Board Deck Update

Erin may ask for the whole deck or one section. Do only the sections she names. If she says she already did a section, skip it.

## Fixed links

| Item | ID |
| :--- | :--- |
| Board meetings parent folder | `1bemQltpMkHIlZhPPaL_U9kTUeO0qNJho` |
| Deck template (`YYMMDD_Board Deck`, .pptx) | `1oUEJP8ZG8VsAATlh0H1syqlpPT65CwIB` |
| Grants tracker (Sheet) | `1UrHVT6g9lloJSiagXrrFl1WYy7ttySoccbqZ3Ps79vQ` |
| Conference tracker (Sheet, tab `CURRENT`) | `1jXtPAZmpNpPwUTeU_nwbsPhz833uFFT93Pm74o4uflg` |
| Board calendar invitee | `aa-board@architectureandadvocacy.org` |

Folder layout: parent → `FY YY-YY` fiscal-year folder (FY runs Sept 1 to Aug 31) → `YYMMDD` meeting folder → `YYMMDD_Board Deck.pptx` + `YYMMDD_Board Agenda` (Google Doc).

## How to edit the deck

The deck is a **.pptx stored in Drive**, not native Slides, so the Slides API can't edit it. Use the `gws` CLI + python-pptx:

1. Download: `gws drive files get --params '{"fileId":ID,"alt":"media","supportsAllDrives":true}' --output deck.pptx`
2. Edit locally (python-pptx; bundled `scripts/swap_image.py` for pictures).
3. **Right before upload**, re-check `md5Checksum` against the downloaded copy. If it changed, Erin edited it: re-download and redo the edit on the fresh copy.
4. Upload in place: `gws drive files update --params '{"fileId":ID,"supportsAllDrives":true}' --upload deck_updated.pptx`
5. Tell Erin to keep the deck closed (or reload it) while you're editing, so neither overwrites the other.

Batch all slide edits for one turn into a single download/upload when possible.

## 0. Find or create the deck

- Look in the FY folder for the meeting's `YYMMDD` folder. Create it if missing (meeting date = next "A+A Board Check-In" event).
- No deck in it → copy the template into it as `YYMMDD_Board Deck`.
- The agenda doc should be in the folder. In its **Resources** section, hyperlink the words "slide deck" to the deck (re-read the doc right before editing).
- Update the cover's `MM.DD.YY` placeholder to the meeting date.

## 1. Upcoming Board Events slide

- `list_events` from today through 3 months out, `fullText` = the board email.
- **Keep only events where the board email is actually in `attendees`.** Full-text search also returns events that just mention it (e.g. Bi-Coastal Bonding meetings). Drop those.
- Title starts with `[optional` (e.g. `[optional]`, `[optional board invite]`) → **Optional** heading. Everything else → **Mandatory**.
- Format each line `Sat 11/21 Event name`, with the prefix stripped. Keep any lines Erin already wrote (like "3 tickets remaining!").

## 2. Grants + Conference tracker screenshots

1. Send Erin both edit links and **stop. Wait for her to say she updated them.**
2. Count the rows and columns visible in the slide's current image, accounting for the picture's crop (python-pptx `crop_*`). The new image must have exactly the same number.
3. Pull grid data:
   `gws sheets spreadsheets get --params '{"spreadsheetId":ID,"ranges":["TAB!A1:<lastcol>40"],"includeGridData":true,"fields":"sheets(data(rowMetadata(pixelSize,hiddenByFilter,hiddenByUser),columnMetadata(pixelSize),rowData(values(formattedValue,hyperlink,textFormatRuns,effectiveFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,wrapStrategy)))))"}' > grid.json`
4. Render: `python scripts/render_table.py grid.json table.png NROWS NCOLS`. This respects the sheet's current filter (hidden rows skipped). Look at the PNG before inserting it.
5. Swap: `python scripts/swap_image.py deck.pptx deck_updated.pptx "Conferences/Thought" table.png` (grants slide title: `GRANTS`).
6. Tell Erin what changed in the rows (e.g. status flips, new amounts). Also tell her it's a rebuilt table, not a true screenshot (Google blocks range export from here).

## 3. Finance: fundraising thermometer (FUNDRAISING slide)

This is **fundraising, not revenue.** Goals live in `Fundraising HQ/MEMORY.md` (FY27: $56,832 by Dec 31, $92,329 by Mar 31, $64,215 by Aug 31; per-period, not cumulative). Use the current period's goal.

1. QuickBooks P&L, FY start → today. QBO counts invoices as income when **sent**, not paid.
2. Unpaid invoices: the AR/unpaid report only covers invoices dated through today. **Also pull invoices dated after today** to catch future-dated pledges.
3. **Received** = P&L income − unpaid invoices − anything that isn't fundraising (investment income, fee-for-service such as Sasaki/Wetlands, and anything else Erin has excluded). List what you excluded, with amounts.
4. **Pledged** = unpaid fundraising invoices, itemized by name and amount. Last time Erin left out Sasaki and California Arts Council. Ask about any invoice where it's unclear whether it's a gift or payment for services.
5. **Still to raise** = goal − received − pledged. % of goal = (received + pledged) / goal, rounded to a whole number for the headline.
6. Fill `assets/thermometer_template.html` placeholders: `{{PCT}}`, `{{PCT_TOTAL_EXACT}}` = (received + pledged)/goal × 100 to 2 decimals, `{{PCT_RECEIVED_EXACT}}`, `{{RECEIVED}}`, `{{PLEDGED}}`, `{{STILL}}`, `{{GOAL}}`, `{{GOAL_DATE}}`. Show exact dollars with cents where they exist.
   - Design rules from Erin: **no eyebrow/subheader above the headline, no gray caption lines under the amounts.**
7. Render to PNG at 1920×1080 with headless Brave or Chrome (`--headless=new --screenshot=out.png --window-size=1920,1080 file://...`). If neither browser is available, say so and stop.
8. Save `YYMMDD_FY27 Fundraising_Thermometer.html` + `.png` to `Finance + Bookkeeping HQ/`. Insert with `swap_image.py ... "FUNDRAISING" thermo.png --add` (or without `--add` if a picture is already there).
9. Show the math (P&L total, each subtraction, each pledge) to Erin in chat before inserting.

## 4. Project update slides

For each project Erin names (e.g. South LA Wetlands, Inner-City Arts Design-Build), fill the project slide template: short update bullets, Budget / Schedule / Overall status, Kudos/Quote, photos.

- **Never invent facts, numbers, quotes, or statuses.** Use only what Erin gives you or what's in sources she points to. If a field is missing, ask her. Don't fill it with a guess.
- Ask Erin where this month's photos are (Drive folder or files). Don't pick photos yourself without her saying which source to use.
- Keep any text Erin already wrote on the slide. Only fill what's empty or what she asks to change.

## Report back

Bullets only: which slides changed, what changed in the data, and any open questions at the top.
