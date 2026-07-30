---
name: end-of-day
description: >
  Run Erin's end-of-day workflow — pull today's meetings from all four A+A calendars plus Fathom and the Cowork Playground, slim any raw transcripts, build meeting notes with the meeting-notes skill, upload them to the right Google Drive folder, update CRM contact logs for external 1:1s, draft thank-you emails into Gmail drafts, capture to-dos as Notion tasks with project links, and mark the end-of-day backstop Done. Trigger whenever Erin says "end of day", "EOD routine", "wrap up today", "run my end of day", or "let's close out the day." Always use this skill when the intent is wrapping up the workday — even if she just says "can you do my EOD?" or "run the workflow."
---

# End-of-Day Workflow

Erin's structured close-of-day routine. Run all seven phases in order, pausing for confirmation at each phase gate.

---

## Phase 1 — Identify Today's Meetings

Pull today's calendar events from all four A+A calendars:
- **Executive Team** calendar
- **Erin A+A** calendar
- **Architecture + Advocacy** calendar
- **Personal** calendar (contains travel and personal appointments that affect work windows)

Then check these two sources for today's transcripts or notes and match them to calendar events by title or time:

- **Fathom** (`mcp__c03aadc8...list_meetings`) — Fathom sometimes processes recordings the following day; if a meeting isn't found, search by title with a 2-day window. Read the **summary** (`get_meeting_summary`), not the full transcript, unless a detail is missing. Keep the recording URL — Phase 4 needs it.
- **Cowork Playground** — the local vault at `/Users/erin/Documents/Cowork Playground/`, the ONLY local folder to search. List files modified today and report the filenames:

  ```bash
  cd "/Users/erin/Documents/Cowork Playground" && find . -newermt "$(date +%Y-%m-%d) 00:00" -type f -not -path "*/.*"
  ```

**Do not open any transcript found there yet.** These are RAW dual-channel exports — thousands of lines, ~72k tokens each. Slim every one first (see below).

If a note already exists in the Playground for a meeting, flag it: another automation may have put it there, and Phase 2 could duplicate it. Ask whether to write alongside it or replace it.

### Slim every transcript before reading it

**Mandatory. No exceptions.** For each transcript found in the Cowork Playground, run the **slim-transcript** skill before anything reads the file:

```bash
python3 <slim-transcript skill dir>/slim_transcript.py "<transcript path>"
```

This writes `<name>_slim.md` beside the original and leaves the original untouched. Cuts a 46-minute call from ~72k tokens to ~28k. **From this point on, the slim file is the transcript** — Phases 2, 4 and 6 all read the slim file. Never read the raw original; `grep` it only to recover a specific quote.

Two outputs of that run must be acted on, not skimmed past:

- **Proper-noun audit.** It lists names present in the original but missing from the slim file. Anything substantive means real content was lost — grep the original and restore it by hand before writing notes.
- **Attribution warning.** If it reports every speaker label is `Unknown`, the transcript cannot tell you who said what. Take attendees from the calendar invite, never assign action-item ownership from the transcript, and confirm owners with Erin in Phase 6.

Delete the `_slim.md` files at the end of the run, or ask — don't leave near-duplicates in the Playground.

### Present the list

Present a numbered list of confirmed meetings. For each, note:
- Meeting title
- Time
- Type: **1:1** or **Group**, and **internal** or **external**
- Whether notes/transcript were found (and in which tool)

Wait for Erin to confirm or correct the list before proceeding.

---

## Phase 2 — Create Meeting Note Docs

For each confirmed meeting with notes, run the **`aa-skills:meeting-notes`** skill. That skill owns the document structure (Meeting Details, Executive Summary, Action Items, Decisions Made, Key Discussion Topics, Timeline & Next Steps, Reference Materials) and A+A branding via **`aa-skills:aa-document-template`**. Do not hand-roll a different format here.

**Source material:**
- Playground transcripts → the **slim file from Phase 1**, never the raw original.
- Fathom-only meetings → the Fathom summary.
- **If no transcript or notes exist: do NOT create the doc at all.**

**Filename** (YYMMDD = meeting date; the same name is used in Drive, no renaming on upload):

- **1:1 meetings** → `YYMMDD_Lastname, Firstname_Organization_meeting-notes.docx`
  e.g. `260729_Wyllie, Meagan_Independent_meeting-notes.docx`
  The date sorts; the name is how Erin browses. Ask for the person's org if the transcript doesn't give it.
- **Group meetings** → `YYMMDD_[descriptive-name]_meeting-notes.docx`

**Where to build it:** notes are **Drive-only** (see Phase 3). Build to a scratch location, not into an HQ folder. There is no local copy of meeting notes.

**Internal meetings (all @architectureandadvocacy.org attendees):** Skip Phases 4 and 5 entirely.

---

## Phase 3 — Upload Notes to Google Drive

Meeting notes live in Google Drive only. Route each doc with this decision tree, **in order** — the first match wins:

1. **Project-related** (1:1 or group) → that project's Drive folder. **A project relation supersedes the 1:1 folder.** Always ask which folder; there is no default.
2. **External 1:1, not project-related** → **"1:1 Notes_Erin"**, folder `1Nmp0tb0TxKJ28axXqUD_kRaqAfaAetoV` (its own shared drive).
3. **Group or internal, not project-related** → ask. For community/partner outreach meetings, suggest **"25-26 Community Partner Outreach"**, folder `1yplER9ldBWeiY9phj-s7ubKp6UrzEwyW` (parent "02. LA Community Partners" `1Q6zinSc7Bm8rezCYeBwkkmL0m4idMr3F`, LA Chapter Programs shared drive). **Fiscal-year rollover:** A+A's fiscal year ends at the end of August. Once FY26-27 begins, create "26-27 … Outreach" in the same parent and use that instead.

Filenames carry over from Phase 2 unchanged — 1:1s are `YYMMDD_Lastname, Firstname_Organization_meeting-notes.docx`, group notes are `YYMMDD_[descriptive-name]_meeting-notes.docx`.

**Capture the Drive file URL for every upload.** Phase 4 needs it for the contact-log hyperlink.

Confirm the destination with Erin before uploading — every time, even when it seems obvious.

---

## Phase 4 — Update CRM Contact Log (external 1:1s only)

**Skip this phase for group meetings and internal A+A meetings.**

Two parts, both driven by the **meeting notes doc** from Phase 2 — not the raw transcript.

### 4a — Profile data

Use the **`aa-skills:crm-extractor`** skill to pull structured profile data from the meeting notes (falling back to the slim transcript or Fathom summary for detail) and update the contact's record.

### 4b — Contact Log row

Check each attendee against the **existing** CRM profiles in the profiles Drive folder (`1aaj3JQ372IYMh7pRmNY5B5tSeKU_dGDS`). If an attendee has a profile, append a row to that profile's **Contact Log**. **Only update profiles that already exist — never create a new profile in this step.**

**Matching (email first, then name):**
1. List the .docx files in the profiles folder.
2. Match the attendee's **email** to the profile's **Email** field (read the profile to get it). If no email match, fall back to matching the attendee **name** against the filename (`Lastname, Firstname_Category.docx`).
3. If neither matches, skip that attendee — do not create anything.

**Row values** (the Contact Log is the last table in the profile; five columns — Date, Format, Name, Description / Notes, Notes Link):
- **Date:** meeting date (MM/DD/YYYY)
- **Format:** `email`, `phone call`, `in-person meeting`, `zoom meeting`, or `event` (infer from the calendar event; if ambiguous use `meeting`)
- **Name:** who the profile subject met with — default `Erin`
- **Description / Notes:** one concise sentence on the meeting's purpose
- **Notes Link:** **two hyperlinks** — a `Notes` link to the Drive URL captured in Phase 3, and a `Fathom` link to the recording URL from Phase 1. Include whichever exist; leave the cell blank if neither does.

**How to edit the .docx:** download the profile from Drive, open with **python-docx**, select the last table (the Contact Log), `add_row()`, set the five cell values (both links as real hyperlinks), save, and re-upload **replacing the same file** (same file ID) via `gws drive files update --upload`. Never create a new file — that duplicates the profile.

Present a summary of which profiles were updated, and which attendees had no existing profile, before moving on.

---

## Phase 5 — Draft Thank-You Emails (external 1:1s only)

**Skip this phase for group meetings and internal A+A meetings.**

For each external 1:1, use the **`aa-skills:thank-you-email`** skill to draft a follow-up. Subject line is always **"Thank you!"**.

Present each draft to Erin for review, then **save it to the Gmail drafts box** (`mcp__claude_ai_Gmail__create_draft`). Do not send.

---

## Phase 6 — Capture To-Dos in Notion

**Step 6a — Extract to-dos**

Scan all of today's meeting notes for action items and to-dos. Present the full list to Erin for review and correction before proceeding. Then ask: "Are there any additional to-dos to add?"

**Step 6b — Confirm task details**

For each task, confirm:
1. **Due date** (if not clear from notes)
2. **Which Notion project** it belongs to — always ask, even if it seems obvious. This is required.
3. **Priority** — Erin will specify; if not, infer from effort (see status values below)

If a task requires a **new project**, ask for:
- Project name
- **Team Responsible** — always prompt with these exact options: NY Chapter, LA Chapter, Board, Executive Team, Grants Working Group, Fundraising, Business Development/Marketing, Finances
- Due date for the project (if known)

**Step 6c — Create new projects (if needed)**

Create new projects in the **Projects** Notion database:
- Data source ID: `54eba13d-b4c0-412f-8ec4-d1cf8f8a1fcd`
- Always apply the **"project template"** template (use `template_id` parameter) — search for it by name first
- Always set **"Team Responsible"** — never create a project without it
- Set due date if provided

**Step 6d — Create Notion tasks**

Create each task in the **A+A Tasks** Notion database:
- Data source ID: `7ec52d40-050f-4f14-942e-3ee85f2935cb`
- **Assignee:** Architecture + Advocacy (user ID: `7af60168-882b-4253-ad8e-b327439b3237`) — ALWAYS set this on every task. This is non-negotiable. Pass the bare UUID directly as the "Assignee" property value.
- **Done status:** use the valid values below
- **Project relation:** Find the matching project page in Notion by name, then update the **project page's** "Tasks" relation property to include the new task ID. Do NOT try to update the rollup field on the task itself — it's read-only. Each task URL must be added individually (one per update call).

**Valid Done field options:** `1. FIRST`, `2. MUST DO`, `3. Low`, `4. 10 minute task`, `5. Quick/Anywhere`, `Not Done`, `Waiting`, `Done`

---

## Phase 7 — Mark the End-of-Day Backstop Complete

As the final step, mark today's **"End of Day"** marker task **Done** in the **A+A Tasks** Notion database (data source `7ec52d40-050f-4f14-942e-3ee85f2935cb`). This is a daily recurring weekday task, linked to the **Project Management** project (`2abc9a33-bd41-80e1-984f-d70740a8c18e`), assigned to Architecture + Advocacy.

- Find the task titled `End of Day` whose **Due Date** is today, and set its **Done** status to `Done`.
- Why: an automated 8pm-weekday cloud routine ("End of Day Backstop") checks this marker first. If it's Done, the backstop skips (no duplicate summary email, no duplicate tasks). If Erin's manual EOD does not mark it Done, the backstop will run at 8pm and do it for her.

---

## Notes + Standing Rules

- Always check **both Fathom and the Cowork Playground** — notes may live in either place.
- **Cowork Playground is the only local folder to touch.** Never search elsewhere on Erin's filesystem.
- **Every Playground transcript gets slimmed before it is read.** Run slim-transcript in Phase 1; all later phases read the slim file. Reading a raw dual-channel export costs ~72k tokens and is never justified.
- **Never infer who said what from an unattributed transcript.** These exports label every speaker `Unknown`. Attendees come from the calendar invite; action-item owners get confirmed with Erin.
- Never create a doc for a meeting with no notes or transcript.
- **Meeting notes are Drive-only.** No local HQ copy. Confirm the Drive destination with Erin before every upload, and remember that a project relation beats the 1:1 folder.
- Use `aa-skills:meeting-notes` for the doc — never a hand-rolled format.
- Always ask for the **project relation** when capturing Notion tasks — required every time.
- Phases 4 and 5 apply to external 1:1 meetings only. Skip for internal A+A meetings and all group meetings.
- The Notion "Parent Project" field is a read-only rollup. To link a task to a project, update the **project page's** Tasks relation, not the task directly.
- When adding multiple tasks to one project, make one `update_properties` call per task URL — the API does not accept comma-separated URLs.
- New projects always require: template applied + Team Responsible set before creation.
