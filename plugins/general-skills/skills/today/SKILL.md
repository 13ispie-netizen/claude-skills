---
name: today
description: "Generate Erin's daily plan from vault tasks, calendar, email, and Slack. Use this whenever your_name says /today, \"what's on my plate today\", \"what should I focus on\", or asks about today's schedule or priorities."
---

# /today — Daily Planning

Generate today's plan from vault contents, calendar, email, and Slack.

## Steps

1. Check if `plans_folder/YYMMDD.md` exists for today — if so, read it first
2. Find tasks by due date using grep (never glob all tasks):
   - Grep for `due: YYMMDD` (today's date) in `tasks_folder/inbox/` and `tasks_folder/active/` -> Due Today
   - Grep for dates before today in same folders -> Overdue
   - Grep for `status: blocked` -> Blocked
   - If no tasks found for today/overdue, grep for dates through end of week
   - If still none, grep to find the next earliest due date
   - Skip `tasks_folder/done/` and `tasks_folder/ideas/`
3. Read only the matching task files
4. Grep `projects_folder/` for `status: active`, read those files for next actions
5. Pull today's calendar from your calendars (see Calendar section)
6. Check priority email (see Email section)
7. Check Slack (see Slack section)
8. (Optional) Run `git log --since="midnight" --grep="cos:" --oneline` for today's activity if you version-control your vault
9. Create or update `plans_folder/YYYY-MM-DD.md`

## Task Discovery (grep-first approach)

All tasks have `due: YYMMDD` in frontmatter. Use grep to find relevant tasks efficiently. Always substitute the real current date. Only read files returned by grep; never glob and read all task files.

## Calendar

Pull events from these calendars for today (timeMin = start of day, timeMax = end of day, timeZone = `notion_database_label`):

- Executive Internal
- Architecture + Advocacy
- Personal
- Erin A+A

Use `gcal_list_events` for each. Combine into one chronological list. Add or remove rows to match the calendars you actually use.

## Email

Search Gmail for priority unread emails:
- `is:unread newer_than:1d` with maxResults of 10
- Highlight emails from key people 
- Show sender, subject, and one-line preview for each
- Don't read full bodies unless asked

## Slack

Check these channels and DMs for recent messages (last 24 hours) needing your attention. Use `slack_read_channel` with limit of 10.

- All A+A
- grants
- board
- Direct messages

### Direct Messages

| Person | User ID |
|---|---|
| teammate_name | teammate_name-id |
| teammate_email | teammate_email-id |

For Slack Connect DMs (external partners): use `slack_search_public_and_private` with query `from:Their Name` filtered to `after:` yesterday's Unix timestamp, channel_types `im`, limit 5.

What to surface: messages mentioning you, questions, anything from teammates needing a response, bug reports in product channels. Keep it brief: sender, channel, one-line summary.

## Update Behavior

When the daily plan file already exists:
- Keep any `[x]` completed items
- Keep any manually added items
- Add new tasks from vault not already present
- Refresh Calendar, Email, Slack, Recent Activity sections
- Preserve custom sections

## Output Format

Write to `plans_folder/YYYY-MM-DD.md`:

- type: daily-plan
- date: YYYY-MM-DD
- ## Calendar (HH:MM — Event (calendar source))
- ## Needs Response ([Slack] / [Email])
- ## Due Today
- ## Overdue
- ## Blocked
- ## Active Projects (Project Name — next action)
- ## Recent Activity (from git log, if applicable)