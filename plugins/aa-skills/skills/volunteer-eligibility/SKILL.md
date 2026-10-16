---
name: volunteer-eligibility
description: >
  Refresh A+A's volunteer paperwork tracker Google Sheet: check off waivers, code of conduct,
  mandated reporter certificates, dues, entrance survey and cleared-to-drive from the semester's
  Drive upload folders and form responses, read unlabeled payment screenshots, add rows for anyone
  with a folder but no row, and remind Erin to check Zelle since the last refresh. Use whenever
  Erin says "volunteer eligibility", "refresh the eligibility sheet", "update the volunteer
  tracker", "who's eligible for ICA / wetlands", "check volunteer paperwork", or "new semester"
  for this tracker.
---

# Volunteer Eligibility

Links for the current semester live in `reference/config.json` (tracker, uploads folder, last
semester's folder, entrance survey responses, vehicle form responses). The ICA / Wetlands
eligibility formulas live in the sheet itself; this skill never edits them.

## Run it (three steps)

1. **Dry run** (writes nothing, downloads only unreviewed generic images):
   ```
   python3 scripts/refresh.py
   ```
2. **Read each image** in `images_to_review` (open the `path` with the image reader). For each one
   that shows a payment, survey confirmation, vehicle form or woodshop sticker, note
   `"Full Name=key"`. Keys: `dues`, `survey`, `vehicle`, `woodshop`. Skip images that show nothing
   relevant; they still get marked reviewed so they never come back.
3. **Apply**:
   ```
   python3 scripts/refresh.py --apply --extra "Violet Hong=dues" "Kiera Hegarty=dues"
   ```
   This checks the boxes, adds rows for new folders, and logs the run on the **Refresh Log** tab
   (date, count, rows added, reviewed image IDs).

Apply directly after reading images; no extra confirmation round needed. The script only turns
boxes on and never touches N/A cells, so it cannot undo Erin's manual edits.

## Report to Erin (keep it short)

- **First line, always:** the `zelle_reminder` text, e.g. "Check Zelle for dues payments received
  since 2026-10-16." The date is the last Refresh Log entry.
- Boxes checked, grouped by column. Name the people.
- New rows added. These come from folder names, so email and phone are blank.
- Anything in `unsorted_non_images`, and images that showed nothing usable, each with a link.
- `tracker_columns_not_found`: just mention it, since Erin removes or renames columns on purpose.
  Only flag it if a core column (waiver, code of conduct, dues) is missing.
- Re-read the eligibility columns and name who is newly ICA / Wetlands eligible.

## How matching works (for judgment calls)

- People are matched to `FA26 First Last` folders by name: 2+ shared name words, or every folder
  word in the tracker name. Same for last semester's folder, used **only** for mandated reporter
  certificates (they're good for a year).
- File names decide the box: "Volunteer Waiver", "Strategy Team Waiver", "Code of Conduct",
  "certificate/mandated" (mandated reporter), "dues/paypal/venmo/zelle/payment/membership" (dues).
  Scholarship or "waived" files are **not** dues; mention them instead.
- Entrance survey: matched by email or name, including people who typed their last name in the
  email box.
- Cleared to drive: vehicle form rows with column A = TRUE, matched by signature or legal name.
  **Never repeat license numbers or birthdays** from that sheet anywhere.

## New semester

When Erin says "new semester", ask for the new tracker, uploads folder, and form links. Then show
the `config.json` change and get her approval before saving it (skill-edit rule). The old
semester's uploads folder becomes `last_semester_folder_id`.

## Requirements

Needs the `gws` CLI (Claude Code). In Cowork or anywhere without `gws`, say so and stop. The Drive
connector can list files and read responses for a read-only report, but it cannot check boxes in
the sheet.
