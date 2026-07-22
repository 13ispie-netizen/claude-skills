---
name: task-capture
description: >
  Take free-form meeting action items and add them to Notion with project assignment and due dates. Trigger whenever Erin pastes action items from a meeting and wants them captured in Notion — even if she just says "add these to Notion", "capture these tasks", or "log these action items." Always use this skill when the goal is turning meeting output into Notion tasks.
---

# Task Capture

Takes free-form action items and creates structured Notion tasks with project assignment. Always pauses for confirmation before writing anything.

---

## Step 1 — Parse

Read the pasted text and extract every action item. For each, pull out:
- **Task name** — clean, specific, verb-first
- **Due date** — explicit ("tomorrow", "June 15") or implied ("ASAP", "end of week"); flag if none found
- **Project hint** — any project, topic, or context keyword mentioned near the task

Do not ask any questions yet. Proceed directly to Step 2.

---

## Step 2 — Collect Project Hints

Count the number of unique project assignments needed across all tasks.

**If 4 or fewer unique projects:** Search Notion automatically (data source ID: `54eba13d-b4c0-412f-8ec4-d1cf8f8a1fcd`) — one search per unique project hint. Pick the best match. If two plausible matches exist, flag both in the table. If no match, flag as **"New project?"**

**If 5 or more unique projects:** Pause before searching. Present the task list and ask:
> "I found [N] tasks that need project assignments. To keep this fast, can you give me a project name for each? I'll match them without searching."

Then use the provided names to search — one search per unique name only.

---

## Step 3 — Present Confirmation Table

Output a single table. Wait for Erin to approve or edit before creating anything.

| # | Task | Due Date | Project | Priority | Notes |
|---|------|----------|---------|----------|-------|
| 1 | [task name] | [date or —] | [project name] | [suggested] | [flag if uncertain] |
| 2 | ... | ... | ... | ... | ... |

**Priority suggestions** — infer from effort and urgency:
- Urgent + complex → `1. FIRST`
- Must do today/tomorrow → `2. MUST DO`
- Longer task, no hard deadline → `3. Low`
- 10 minutes or less → `4. 10 minute task`
- Can do anywhere, anytime → `5. Quick/Anywhere`

At the bottom of the table, note any tasks flagged for new project creation and ask Erin what project they belong to.

Wait for Erin to confirm, correct, or edit the table before proceeding.

---

## Step 4 — Handle New Projects (if any)

If any tasks need a new project:

1. Ask for:
   - Project name
   - **Team Responsible** — always prompt with these exact options: NY Chapter, LA Chapter, Board, Executive Team, Grants Working Group, Fundraising, Business Development/Marketing, Finances
   - Due date for the project (if known)

2. Create the project in Notion (data source ID: `54eba13d-b4c0-412f-8ec4-d1cf8f8a1fcd`):
   - Always apply the **"project template"** template — search for it by name first
   - Always set Team Responsible before creating

---

## Step 5 — Create Tasks

Create each confirmed task in the A+A Tasks Notion database:
- Data source ID: `7ec52d40-050f-4f14-942e-3ee85f2935cb`
- **Assignee:** Architecture + Advocacy (user ID: `7af60168-882b-4253-ad8e-b327439b3237`) — ALWAYS set on every task. Non-negotiable.
- **Done status:** use exact values only: `1. FIRST`, `2. MUST DO`, `3. Low`, `4. 10 minute task`, `5. Quick/Anywhere`, `Not Done`, `Waiting`, `Done`
- **Due date:** set if provided

**Linking to projects:**
- Find the matching project page in Notion by name
- Update the **project page's** "Tasks" relation property to include the new task ID
- Do NOT update the rollup field on the task — it's read-only
- One `update_properties` call per task URL — never comma-separated

Confirm completion with a brief summary: how many tasks created, which projects they were linked to.

---

## Progressive Updates

Any time Erin corrects behavior, states a preference, or says "always" / "never" / "don't do that" during a task-capture session:

1. Update this SKILL.md immediately — add the rule to the relevant step, or create a new rule under a "Standing Rules" section at the bottom.
2. Repackage the `.skill` file and save it to `/Users/erin/Documents/Cowork Playground/Skills/task-capture.skill`.
3. Present the updated `.skill` file using `mcp__cowork__present_files` so Erin can reinstall it.

Do this inline — don't wait until the end of the session.
