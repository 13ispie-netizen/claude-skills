---
name: end-of-day
description: >
  Run Erin's end-of-day workflow — pull today's meetings from all four A+A calendars, create meeting note docs and save them to the HQ matching each meeting's topic (confirm destination every time), update the CRM for external 1:1s, draft thank-you emails for external 1:1s, and capture to-dos as Notion tasks with project links. Trigger whenever Erin says "end of day", "EOD routine", "wrap up today", "run my end of day", or "let's close out the day." Always use this skill when the intent is wrapping up the workday — even if she just says "can you do my EOD?" or "run the workflow."
---

# End-of-Day Workflow

Erin's structured close-of-day routine. Run all five phases in order, pausing for confirmation at each phase gate.

---

## Phase 1 — Identify Today's Meetings

Pull today's calendar events from all four A+A calendars:
- **Executive Team** calendar
- **Erin A+A** calendar
- **Architecture + Advocacy** calendar
- **Personal** calendar (contains travel and personal appointments that affect work windows)

Also check **Fathom** (`mcp__c03aadc8...list_meetings`) and **Granola** (`mcp__5254d818...list_meetings`) for any meeting transcripts or notes from today — match them to calendar events by title or time. Note: Fathom sometimes processes recordings the following day — if a meeting isn't found, search by title with a 2-day window. Granola full transcripts require a paid tier; if the transcript is unavailable, work from the Granola summary.

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
- If Granola notes exist: add a "Granola Notes: [View in Granola]" hyperlink row
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

For each external 1:1, use the **crm-extractor** skill to pull structured profile data from the meeting transcript (or Granola summary if the transcript is unavailable) and update the contact's record.

---

## Phase 4 — Draft Thank-You Emails (1:1s only, external meetings only)

**Skip this phase for group meetings and internal A+A meetings.**

For each external 1:1, use the **thank-you-email** skill to draft a follow-up. Present the draft to Erin for review before sending.

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

## Notes + Standing Rules

- Always check **both Fathom and Granola** — notes may live in either tool.
- Never create a doc for a meeting with no notes or transcript.
- Meeting notes are saved to the HQ matching the meeting's topic, never a standalone Meeting Notes HQ. Always confirm the destination HQ with Erin before saving. Not Google Drive unless Erin explicitly asks.
- Always ask for the **project relation** when capturing Notion tasks — required every time.
- Phases 3 and 4 apply to external 1:1 meetings only. Skip for internal A+A meetings and all group meetings.
- The Notion "Parent Project" field is a read-only rollup. To link a task to a project, update the **project page's** Tasks relation, not the task directly.
- When adding multiple tasks to one project, make one `update_properties` call per task URL — the API does not accept comma-separated URLs.
- New projects always require: template applied + Team Responsible set before creation.
