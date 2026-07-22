---
name: daily-planner
description: >
  Build Erin's interactive hour-by-hour plan for tomorrow — pulling calendar events and task CSV, then sequencing them into a prioritized day view with founder-specific heuristics applied. Trigger whenever Erin says "plan tomorrow", "daily planner", "build my day", "what should I do tomorrow", or "evening planning session." Always use this skill at the end of the day when the goal is building tomorrow's schedule.
---

# Daily Planner

Erin's evening planning session. Runs in four phases. Total output: an in-chat structured schedule + an interactive HTML day-view artifact.

---

## Phase 1 — Pull Tomorrow's Calendar

Pull events from **all four calendars** for tomorrow's date:
- **Executive Team** (`office@architectureandadvocacy.org`)
- **Erin A+A** (`erin@architectureandadvocacy.org`)
- **Architecture + Advocacy** (`arch.advocacy@gmail.com`)
- **Personal** (`c_d233bc8f16c7ffa2820874d82c82d5b516666aa855e3aed6adce273f23645443@group.calendar.google.com`)

Also check the **Travel calendar** (`c_dc3945dd34cbf3886d7ffdd519b702f2b688bdfbccf588f761671538171ebf07@group.calendar.google.com`) for any travel blocks — if a travel event is present, flag as a **travel day** and apply the travel-day override (see Phase 4).

For each event, extract:
- Title, start time, end time, duration
- Attendees (names + emails if available)
- Video/location link

**Timezone:** Always display times in ET when Erin is on the East Coast. Check the Personal calendar for flight/hotel events to infer timezone.

**Deduplicate** events that appear across multiple calendars — same title + overlapping time = one event.

Identify all **gaps between events**. Classify each gap:
- ≥ 90 min → **Deep work eligible**
- 30–89 min → **Operational task eligible**
- < 30 min → **Buffer only** (do not schedule tasks here)

Flag:
- Back-to-back meetings with zero buffer
- Any event before 9:00am (early constraint)
- Total meeting time — if > 4 hours, mark as **meeting-heavy day**
- Travel blocks → flag as **travel day** (see Phase 4 override)

---

## Phase 2 — Pull Tasks

**The Notion MCP cannot query filtered database rows.** Do not attempt to fetch or query Notion databases directly — it will return only schema, not task records.

Instead, use this approach in order:

### Option A — CSV in Cowork Playground (preferred)
Check if a file matching `A+A Tasks*.csv` exists in the Cowork Playground folder. If found, read it and filter for:
- `Done` field ≠ `Done`
- `Assignee` contains `Architecture + Advocacy`

Sort by `Due Date` ascending (overdue first, then upcoming, then undated).

### Option B — CSV uploaded this session
If Erin has uploaded a CSV during this session, use that.

### Option C — Manual input
If no CSV is available, ask:
*"Can you export your task list from Notion (My Tasks page → Export → CSV) and drop it in the Cowork Playground folder? Or paste your top priorities for tomorrow and I'll slot them in."*

Do not attempt to query Notion databases. Do not repeat the attempt if it fails.

### Task databases (for reference only)
- A+A Tasks: `c879a434-1557-4d0b-bf09-af690bb10fe4`
- Executive Tasks: `6441cdf5-9891-4cec-a49a-b6403dc5af7a`
- Wetlands Tasks: `354c9a33-bd41-80e9-903a-c4618daca525`
- My Tasks page: `0799c0a2-0156-402f-9a01-67d7e58ed9eb`

### Presenting tasks
Bucket results into:
1. **Overdue** — due date before tomorrow, not done
2. **Due tomorrow** — due date = tomorrow, not done
3. **Due this week** — due within 7 days, not done
4. **Undated high-priority** — no due date, status = `1. FIRST` or `2. MUST DO`

Do not surface low-priority undated tasks unless the day is light. Present rollovers (overdue) separately and ask Erin which to schedule, defer, or drop — never auto-schedule them.

---

## Phase 3 — Monthly Goals (Manual Input)

Ask for monthly goals or focus areas if not already provided:
*"Any monthly goals or focus areas to factor in? Paste them here or skip."*

Treat as soft constraints — lenses for evaluating whether the plan is directionally right, not hard task assignments.

---

## Phase 4 — Build the Plan

### Standing recurring blocks (apply every day)

These are always included unless Erin explicitly skips them:

| Block | Timing | Size | Notes |
|---|---|---|---|
| **Meeting prep** | Start of day, before first meeting | 15 min | Only if there are meetings that day |
| **LinkedIn post** | Morning | 15–30 min | Daily goal (3–5x/week); drafts usually exist, just polish + schedule |
| **Learning block** | End of day | 30 min | Current focus: Coursera PM course. Place on plane/transit if traveling |

**Day-of-week overrides:**
- **Monday:** Reserve 2–3 hrs morning for LinkedIn content planning for the week (replaces single post block)
- **Friday:** Reserve 3 hrs morning for project review (in addition to or replacing deep work block)

### Travel day override
If the Travel calendar shows a travel block tomorrow:
- Cap scheduled tasks at 3 maximum
- Protect the morning block (9am–lunch) for founder-only / deep work
- Leave afternoon as buffer/flex — travel days need it
- Place the learning block on the plane

### Step 4a: Classify every task

| Type | Definition | Label |
|---|---|---|
| **Founder-only** | Fundraising, donor outreach, board relations, hiring, strategic partnerships, funder research | `[FOUNDER ONLY]` |
| **Deep work** | Writing, strategy, design, anything requiring 60+ min of uninterrupted focus | `[DEEP WORK]` |
| **Operational** | Admin, logistics, internal coordination, scheduling | `[OPS]` |
| **Reactive** | Replies, turnarounds, requests from others, quick tasks < 20 min | `[REACTIVE]` |
| **Deferred** | Status = Waiting, no clear next action, blocked | `[DEFER]` — do not schedule |

### Step 4b: Apply prioritization rules

**Rule 1 — Protect the morning.**
The first available 90–120 min block at or after 9:00am goes to Founder-only or Deep Work tasks — no exceptions.

**Rule 2 — Sequence by energy.**
- Morning → Founder-only / Deep work
- Midday → Meetings + communication tasks
- Afternoon → Operational + Admin
- End of day → Learning block, then Reactive

**Rule 3 — Fit tasks to gap size.**
- Deep work eligible gaps (≥ 90 min) → Founder-only or Deep Work only
- Operational eligible gaps (30–89 min) → OPS or REACTIVE
- Buffer gaps (< 30 min) → leave empty; label as "Buffer"
- Never schedule deep work after 3:00pm

**Rule 4 — Meeting-heavy day override.**
If total meeting time > 4 hours, cap scheduled tasks at 3. Label: *"Meeting-heavy — light task day."*

**Rule 5 — Always leave one buffer block.**
Reserve at least one 30-min gap mid-afternoon, labeled "Overflow / Flex."

**Rule 6 — Rollover handling.**
Present rollover candidates separately. Erin chooses: reschedule, defer, or drop. Never auto-schedule.

### Step 4c: Apply founder health checks

**Reactive crowding check:**
If reactive/operational task time > 50% of total scheduled task time → warn:
*"Founder-only work is underrepresented. Consider deferring [task] to protect time for [high-ROI task]."*

**Zero founder-only check:**
If no Founder-only task is scheduled → warn:
*"No founder-only work scheduled. Is there a fundraising, board, or hiring task that belongs in the morning block?"*

---

## Phase 5 — Output

### 5a: In-chat structured schedule

Present the plan as a flat chronological list. One line per block:

```
9:00–9:15    [OPS]            Meeting prep — [meeting name]
9:15–9:30    [FOUNDER ONLY]   LinkedIn post — polish + schedule
9:30–11:30   [FOUNDER ONLY]   Board meeting prep: raises/review + succession plan
11:30–12:00  [BUFFER]         Overflow / Flex
12:00–1:00   [MEETING]        Funder intro — Maya Torres
1:00–2:00    [OPS]            Reply backlog
2:00–2:30    [BUFFER]         Overflow / Flex
End of day   [LEARNING]       Coursera PM course — 30 min
```

List flagged warnings below under **Flags + Checks**.

Ask: *"Does this look right? Any tasks to swap, defer, or add before I render the day view?"*

Wait for confirmation before rendering.

### 5b: Interactive HTML day view

After Erin confirms, render using `mcp__visualize__show_widget` (read `mcp__visualize__read_me` first).

**Color coding:**
- Teal green → Founder-only / Deep work
- Warm amber → Meetings
- Purple → Ops
- Coral → Personal
- Blue → Learning
- Light gray → Buffer / Travel

Show: time label, task type tag, task name, sub-tasks if batched. Include a legend. All times in ET (or local timezone if traveling).

---

## Standing Rules

- **Never attempt to query Notion databases directly for task rows.** The MCP returns schema only. Use CSV export instead.
- **Never auto-schedule rollover tasks.** Always present and confirm.
- **Never fill the morning block with OPS or REACTIVE tasks.**
- **Always confirm the draft schedule** before rendering the artifact.
- **Duration estimates (if not in CSV):** 30 min for OPS/REACTIVE, 60 min for DEEP WORK, 90 min for FOUNDER ONLY.
- **Travel days:** cap at 3 tasks, protect morning, learning block goes on the plane.

---

## A+A Context

Erin is Co-Founder and Executive Director of Architecture + Advocacy — a design-justice nonprofit with chapters in South LA and Flatbush, Brooklyn. High-ROI founder activities: fundraising, funder relationships, board governance, strategic hiring, and major partnership development. These always take priority over operational and reactive work. The goal of this skill is to protect that time, not just fill the calendar.

Never say "marginalized" or "low-income."
