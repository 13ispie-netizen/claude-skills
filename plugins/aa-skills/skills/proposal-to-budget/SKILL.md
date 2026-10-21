---
name: proposal-to-budget
description: "Turn an A+A scope proposal (SOW) into a fee worksheet / budget in Google Sheets: copy the Billing Fee Worksheet template, mirror the proposal's numbered phases, sub-tasks and sub-sub tasks, seed hours from a precedent budget (default: South LA Wetlands draft 6), and apply A+A's Rules, Variables, project-management, staffing and hard-cost conventions. Use whenever Erin says 'make a budget from this proposal', 'turn the SOW into a bill/fee worksheet', 'price this proposal', 'build the fee worksheet', or shares a scope proposal and asks for hours or fees."
---

# Proposal to Budget

Produces a fee worksheet whose rows match the proposal line for line, so the SOW's compensation section can be filled straight from it.

## Sources (Contracted Work shared drive)

| File | ID |
|---|---|
| 261019_Billing_Fee Worksheet Template | `1N6jxj5KE_ZhVsl4AAAl5_4zxZ14zE2hR5xp927Ze8R0` (tab `Fee Worksheet` sheetId 996518806; tab `Rules` sheetId 1) |
| 260928_South LA Wetlands Budget_draft 6 (default hours precedent) | `1wktVWitF5zwwJGwMoc4O4Js8AuqzL3mqSiTkARNE1l0`, numbered tabs only (01, 02, 04, 05 x2, 06-09) |
| 260912_South LA Wetlands_Scope Proposal_draft 6.3 (structure example) | `1yFSWKahZjoETHZboCeyJ3PBIPLA3ETduu3CbSsIDnBw` |
| Worked example | `reference/example_makers_hub_spec.py` |

The template's **Rules** tab is the source of truth for standards. Read it every run.

## Step 0: ask (one round)

1. Proposal link (Google Doc).
2. Precedent budget: Wetlands draft 6, or another.
3. Phase lengths in months.
4. Destination folder. Default: Contracted Work › current FY folder. Check sharing before saving: budgets hold rates.

## Step 1: read the proposal in full and map its hierarchy

- Phase = `x.0` heading. Sub-task = each enumerated item under it (`x.1, x.2`). Sub-sub task = each nested item (`x.1.1`). Number rows exactly as the proposal does.
- **Charrettes, focus groups, and engagement meetings always get sub-sub tasks** (design activities, agenda, outreach/coordination, reminders, attend, drive time, compile results), even when the proposal lists them as one line.
- Each phase ends with a **Project Management** sub-task holding three rows: Schedule + Coordination (first phase: ED 5 hrs kickoff), Client Meetings (Qty = ROUNDUP(weeks x PM meetings/week); 1 hr each, ED + PM), Emails + Phone Calls (Qty = weeks; ED 1 + PM 1 hr/week).

## Step 2: Variables vs Rules

- **Variables** (top of Fee Worksheet): project-specific counts and lengths only. Examples: PM meetings per week, number of focus groups, members per event, interviews, session lengths, Ambassadors, launch events.
- **Rules** (Rules tab, Standard values E:G): how to calculate hours or costs for a task on any project. Examples: drive time per trip, virtual meeting length, report sizes (short 5 PM + 1 ED, longer 10 + 2, intense 20 + 3; revisions separate), follow-ups, hard-cost unit costs, markup.
- A cell that uses either one links to it (`=$B$23`, `=Rules!$F$2`). Never hard-code a number that has a Variable or Rule.

## Step 3: hours

- Columns: Qty, then **one hours-per-unit column per staff role** (ED, PM, Amb). Row Total = Qty x hours x Number of Staff. Fee = that x rate, summed across roles. A blank Qty counts as 1; Qty 0 = not included. **Qty formulas must start with `=`**, or they read as text and count as 0.
- **Per-person hours only.** The precedent's "# of staff" / multiplier columns (e.g., Wetlands coordinator x2, x1.5; ambassadors x4-5) are headcount. Headcount goes in the **Number of Staff** row, never as `2*` inside an hours cell.
- Wetlands Workshop Coordinator hours map to PM. Wetlands "Attend 4 hr" = session + drive: use the session-length Variable plus drive time from Rules.
- In-person tasks add drive time (Rules) per person attending. Report-type deliverables use the Rules report sizes.
- A task with no precedent and no Rule stays **blank**, with the note "New task; no precedent. Fill in hours."
- Every row's Notes column cites its basis (precedent tab, line, and any adjustment).

## Step 4: hard costs

Columns B:D are editable inputs: **B Qty** (events / trips / sets) x **C Per event** (people / miles; blank = 1) x **D Unit cost** (linked to Rules). G = Cost, H = Billed (cost + markup from Rules, 15%). Column I states the math in words. Seed from the precedent's reimbursement rates (Wetlands: food $15/person, gift cards $25/person, printing $50/meeting, supplies $50/event, mileage 20 mi x $0.70/trip). Leave interpreters, DJ, videographer, rentals out unless Erin asks.

## Step 5: build

1. Copy the template: `gws drive files copy --params '{"fileId":"<template>","supportsAllDrives":true}' --json '{"name":"YYMMDD_[Project]_Fee Worksheet_draft1","parents":["<folder>"]}'`.
2. Write a spec in the format of `reference/example_makers_hub_spec.py` and run it. `scripts/feebuild.py` writes the whole Fee Worksheet tab, its formatting, and the Rules standards block.
3. Verify: read the Phase Summary back, toggle one Variable and one Number of Staff value, confirm the totals move, then restore them.

Requires the `gws` CLI (Claude Code). Without it (Cowork), build with the Sheets connector by the same layout, or tell Erin which step needs gws.

## Editing an existing budget (most requests)

- **Run `scripts/check_edits.py <spec> <sheetId>` as its own step.** If it reports any difference, Erin has edited the sheet: **never rebuild**. Edit in place (insert rows, rewrite only the targeted cells), finding rows by label right before writing, since rows move while she works.
- Never delete or overwrite her rows or values without asking. If a formula she touched is broken (e.g., #REF!, stray characters), flag it with the fix and ask.

## Report back

Lead with the Phase Summary totals (hours by role, fee) and the hard-cost total, then show the math for anything new, list blank tasks, list assumptions (staffing, session length, attendance), and flag mismatches with the proposal (numbering gaps, months that don't add up). Caveats go in chat, never in the sheet.
