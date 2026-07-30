---
name: end-of-day
description: >
  Run Erin's end-of-day workflow — pull today's meetings from all four A+A calendars, create meeting note docs and save them to the HQ matching each meeting's topic (confirm destination every time), update the CRM for external 1:1s, draft thank-you emails for external 1:1s, and capture to-dos as Notion tasks with project links. Trigger whenever Erin says "end of day", "EOD routine", "wrap up today", "run my end of day", or "let's close out the day." Always use this skill when the intent is wrapping up the workday — even if she just says "can you do my EOD?" or "run the workflow."
---

# End-of-Day Workflow

Erin's structured close-of-day routine. Run all six phases in order, pausing for confirmation at each phase gate.

---

## Phase 1 — Identify Today's Meetings

Pull today's calendar events from all four A+A calendars:
- **Executive Team** calendar
- **Erin A+A** calendar
- **Architecture + Advocacy** calendar
- **Personal** calendar (contains travel and personal appointments that affect work windows)

Then check these two sources for today's transcripts or notes and match them to calendar events by title or time:

- **Fathom** (`mcp__c03aadc8...list_meetings`) — Fathom sometimes processes recordings the following day; if a meeting isn't found, search by title with a 2-day window. Read the **summary** (`get_meeting_summary`), not the full transcript, unless a detail is missing.
- **Cowork Playground** — the local vault at `/Users/erin/Documents/Cowork Playground/`, the ONLY local folder to search. List files modified today (`find . -newermt "<today> 00:00" -type f`) and report the filenames; open one only if it's actually a meeting note. These files are often RAW two-speaker transcripts (`[Said]`/`[Heard]` lines duplicated, thousands of lines, 40k+ tokens) — never read one whole. Grep for the specific section you need.

If a note already exists in the Playground for a meeting, flag it: another automation may have put it there, and Phase 2 could duplicate it. Ask whether to write alongside it or replace it.

Present a numbered list of confirmed meetings. For each, note:
- Meeting title
- Time
- Type: **1:1** or **Group**
- Whether notes/transcript were found (and in which tool)

Wait for Erin to confirm or correct the list before proceeding.

---

## Phase 2 — Create Meeting Note Docs

For each confirmed meeting with notes, create a `.docx` file using the **docx** skill.

**Naming convention:**
- 1:1: `YYMMDD_Erin x [Name]_[short description].docx`
- Group: `YYMMDD_[Group or Topic]_[short description].docx`

**Doc contents:**
- Title (H1): meeting name
- Meta rows (bold label + plain value): Date, Time, Attendees, Meeting Type
- If Fathom recording(s) exist: add a "Fathom Recording: [View]" hyperlink row for each
- Horizontal rule divider
- H2 sections for each topic covered, with bullet points
- Final H2 "Next Steps": one bullet per action item with owner and due date if known
- If no transcript or notes exist: do NOT create the doc at all.

**Save location:** Meeting notes are stored in the HQ that corresponds to the meeting's topic — there is no standalone Meeting Notes HQ (retired 2026-07-09). **Always ask Erin to confirm the destination HQ before saving any meeting note**, even when the topic seems obvious. Save into that HQ's root unless Erin specifies a subfolder. Do NOT upload to Google Drive unless Erin explicitly asks.

**Internal meetings (all @architectureandadvocacy.org attendees):** Skip Phases 3 and 4 entirely.

---

## Phase 3 — Update CRM Contact Log (1:1s only, external meetings only)

**Skip this phase for group meetings and internal A+A meetings.**

For each external 1:1, use the **crm-extractor** skill to pull structured profile data from the meeting transcript (or the Fathom summary if the transcript is unavailable) and update the contact's record.

---

## Phase 4 — Draft Thank-You Emails (1:1s only, external meetings only)

**Skip this phase for group meetings and internal A+A meetings.**

For each external 1:1, use the **thank-you-email** skill to draft a follow-up. Present the draft to Erin for review before sending.

---

## Phase 4.5 — Log Meetings to Existing CRM Profile Contact Logs

**Applies to ALL of today's meetings (1:1 and group, internal or external) — not limited to external 1:1s.**

For every meeting today, check each attendee against the **existing** CRM profiles in the profiles Drive folder (`1aaj3JQ372IYMh7pRmNY5B5tSeKU_dGDS`). If an attendee has a profile there, append a row to that profile's **Contact Log** table. **Only update profiles that already exist — never create a new profile in this step.**

**Matching (email first, then name):**
1. List the .docx files in the profiles folder.
2. For each meeting attendee, first match the attendee's **email** to the profile's **Email** field (read the profile's contents to get it). If no email match, fall back to matching the attendee **name** to the profile filename (`Lastname, Firstname_Category.docx`).
3. If neither matches an existing profile, skip that attendee (do not create anything).

**Appending the Contact Log row** (the Contact Log is the last table in the profile; it has five columns — Date, Format, Name, Description / Notes, Notes Link):
- **Date:** meeting date (MM/DD/YYYY)
- **Format:** `email`, `phone call`, `in-person meeting`, `zoom meeting`, or `event` (infer from the calendar event; if ambiguous use `meeting`)
- **Name:** who the profile subject met with — default `Erin`
- **Description / Notes:** one concise sentence on the meeting's purpose
- **Notes Link:** a clickable `Notes` hyperlink to the meeting-notes doc created in Phase 2. **If no notes doc exists for that meeting, leave this cell blank.**

**How to edit the .docx (manual run):** download the profile from Drive, open it with **python-docx**, select the last table (the Contact Log), `add_row()`, set the five cell values (add the Notes Link as a real hyperlink), save, and re-upload to Drive **replacing the same file** (same file ID) via the `gws drive files update --upload` flow. Do not create a new file — that would duplicate the profile.

Present a summary of which profiles you updated (and which attendees had no existing profile) before moving on.

---

## Phase 5 — Capture To-Dos in Notion

**Step 5a — Extract to-dos**

Scan all meeting notes from today for action items and to-dos. Present the full list to Erin for review and correction before proceeding. Then ask: "Are there any additional to-dos to add?"

**Step 5b — Confirm task details**

For each task, confirm:
1. **Due date** (if not clear from notes)
2. **Which Notion project** it belongs to — always ask, even if it seems obvious. This is required.
3. **Priority** — Erin will specify; if not, infer from effort (see status values below)

If a task requires a **new project**, ask for:
- Project name
- **Team Responsible** — always prompt with these exact options: NY Chapter, LA Chapter, Board, Executive Team, Grants Working Group, Fundraising, Business Development/Marketing, Finances
- Due date for the project (if known)

**Step 5c — Create new projects (if needed)**

Create new projects in the **Projects** Notion database:
- Data source ID: `54eba13d-b4c0-412f-8ec4-d1cf8f8a1fcd`
- Always apply the **"project template"** template (use `template_id` parameter) — search for it by name first
- Always set **"Team Responsible"** — never create a project without it
- Set due date if provided

**Step 5d — Create Notion tasks**

Create each task in the **A+A Tasks** Notion database:
- Data source ID: `7ec52d40-050f-4f14-942e-3ee85f2935cb`
- **Assignee:** Architecture + Advocacy (user ID: `7af60168-882b-4253-ad8e-b327439b3237`) — ALWAYS set this on every task. This is non-negotiable. Pass the bare UUID directly as the "Assignee" property value.
- **Done status:** use the valid values below
- **Project relation:** Find the matching project page in Notion by name, then update the **project page's** "Tasks" relation property to include the new task ID. Do NOT try to update the rollup field on the task itself — it's read-only. Each task URL must be added individually (one per update call).

**Valid Done field options:** `1. FIRST`, `2. MUST DO`, `3. Low`, `4. 10 minute task`, `5. Quick/Anywhere`, `Not Done`, `Waiting`, `Done`

---

## Phase 6 — Mark the End-of-Day Backstop Complete

As the final step, mark today's **"End of Day"** marker task **Done** in the **A+A Tasks** Notion database (data source `7ec52d40-050f-4f14-942e-3ee85f2935cb`). This is a daily recurring weekday task, linked to the **Project Management** project (`2abc9a33-bd41-80e1-984f-d70740a8c18e`), assigned to Architecture + Advocacy.

- Find the task titled `End of Day` whose **Due Date** is today, and set its **Done** status to `Done`.
- Why: an automated 8pm-weekday cloud routine ("End of Day Backstop") checks this marker first. If it's Done, the backstop skips (no duplicate summary email, no duplicate tasks). If Erin's manual EOD does not mark it Done, the backstop will run at 8pm and do it for her.

---

## Notes + Standing Rules

- Always check **both Fathom and the Cowork Playground** — notes may live in either place.
- **Cowork Playground is the only local folder to touch.** Never search elsewhere on Erin's filesystem.
- Never create a doc for a meeting with no notes or transcript.
- Meeting notes are saved to the HQ matching the meeting's topic, never a standalone Meeting Notes HQ. Always confirm the destination HQ with Erin before saving. Not Google Drive unless Erin explicitly asks.
- Always ask for the **project relation** when capturing Notion tasks — required every time.
- Phases 3 and 4 apply to external 1:1 meetings only. Skip for internal A+A meetings and all group meetings.
- The Notion "Parent Project" field is a read-only rollup. To link a task to a project, update the **project page's** Tasks relation, not the task directly.
- When adding multiple tasks to one project, make one `update_properties` call per task URL — the API does not accept comma-separated URLs.
- New projects always require: template applied + Team Responsible set before creation.
