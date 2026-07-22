---
name: flyer-to-calendar
description: Parse a community event flyer (image or text) and create a Google Calendar event from it. Use this skill whenever the user shares a flyer, poster, event announcement, or any image/text describing a community event and wants it added to their calendar. Trigger on phrases like "add this to my calendar," "create an event from this," "put this on my calendar," or when an event flyer is shared without explicit instruction — the intent is almost always to capture it. Always use this skill when a flyer or event image is present.
compatibility: "MCPs: Google Calendar (https://gcal.mcp.claude.com/mcp). Tools: web_search, image input (for flyer images)."
---

# Flyer to Calendar

Parse a community event flyer and create a Google Calendar event — no guessing, no hallucinating.

---

## Step 1: Extract fields

From the flyer (image or text), extract all events present. A flyer may contain one event or many.

For each event, extract:

| Field | Notes |
|---|---|
| **Title** | Exact event name as written |
| **Date** | Full date including year if present |
| **Time** | Start time; end time if listed |
| **Location** | Full address if available; venue name + city at minimum |

If multiple events are found, process all of them — unless the user's prompt specifies otherwise (e.g., "just add the first one").

Do not infer, estimate, or fill in any field not present in the flyer.

---

## Step 2: Check for missing or ambiguous fields

Before doing anything else, check all four required fields for each event.

If **any** are missing or ambiguous:
- Stop
- Ask the user — **one question per missing field**, in order: title → date → time → location
- Do not proceed until all fields across all events are confirmed

---

## Step 3: Look up the timezone

Use web search to find the IANA timezone for the event's location.

Examples:
- Los Angeles, CA → `America/Los_Angeles`
- Brooklyn, NY → `America/New_York`
- Chicago, IL → `America/Chicago`

Use the timezone of the **event's location**, not the user's local timezone.

---

## Step 4: Select the target calendar

Default calendar by event type:
- Community events, org events, flyers from outside orgs → **Community Events** (`c_f4d038c9061270258c7e0ff3cbea223a0813676cde0fb343241f8097bbb0eccb@group.calendar.google.com`)
- If the user specifies a different calendar by name, use `list_calendars` to find the correct ID before proceeding.

**Important:** Only use Google Calendar IDs (email-style or `c_...@group.calendar.google.com` format). Never use iCloud-style UUIDs (e.g. `73DE07A0-...`) — these will always fail via the Google Calendar MCP.

If a calendar ID returns a 404 error:
1. Call `list_calendars`
2. Show the user the available calendars
3. Ask which one to use before retrying

---

## Step 5: Create the Google Calendar event(s)

Use the Google Calendar MCP to create each event. If there are multiple events, create them one by one.

Required fields per event:
- **Title**: from the flyer
- **Start time**: ISO 8601 in the event's local timezone (e.g., `2026-05-10T14:00:00-07:00`)
- **End time**: if listed on flyer; otherwise omit or set to 1 hour after start
- **Location**: full address or venue + city
- **Description**: any additional details from the flyer (speakers, registration links, cost, etc.)

After creating all events, confirm how many were added and list their titles and dates.

---

## Rules

- Never hallucinate details not on the flyer
- Never convert timezone to user's local time — always use event location's timezone
- Never combine multiple missing-field questions into one ask
- If the flyer is blurry, cropped, or unreadable, say so and ask the user to provide the details manually
- Never use iCloud-style calendar IDs — Google Calendar MCP does not support them

---

## Progressive Updates

During any conversation using this skill, watch for moments where the user defines a clear behavioral rule — something they want Claude to always do, never do, or handle differently going forward. These can be explicit ("always do X") or implicit (a correction they make that clearly reflects a standing preference).

When you detect one:
1. Apply it immediately in the current response
2. Append it to the **User-Defined Rules** section at the bottom of this SKILL.md
3. Repackage the skill using `python -m scripts.package_skill /tmp/flyer-to-calendar`
4. Present the `.skill` file to the user for reinstall — no confirmation prompt

Do not ask permission. Just update, repackage, and present.

---

## User-Defined Rules

- If a flyer contains multiple events, create all of them automatically unless the user's prompt says otherwise.
- For community event flyers, default to the Community Events calendar (ID: `c_f4d038c9061270258c7e0ff3cbea223a0813676cde0fb343241f8097bbb0eccb@group.calendar.google.com`).
- Never use iCloud-style calendar IDs (e.g. UUIDs like `73DE07A0-...`). These always fail via the Google Calendar MCP.
- If a calendar ID returns a 404, call `list_calendars` and ask the user to confirm which calendar to use before proceeding.
- When a ticket purchase link is available (e.g., from Eventbrite or similar), include it as the first line of the event description/notes, before any other details.
