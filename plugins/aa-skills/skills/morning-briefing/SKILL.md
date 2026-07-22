---
name: morning-briefing
description: >
  Run Erin's daily morning briefing — fetch today's calendar events across all three A+A calendars, research each meeting (Gmail context, CRM profiles, org web research where needed), and output a structured in-chat briefing with attendee context and a sharp Opening Line for each meeting. Trigger whenever Erin says "morning briefing", "prep me for today", "what's on my calendar", "run the briefing", "brief me", or any variation of wanting to know what's happening today and how to show up prepared. Always use this skill when the intent is meeting preparation for today's schedule — even if she just says "what do I have today."
---

# Morning Briefing

Erin's daily meeting prep, run in-chat. The goal: she reads this once and walks into every meeting already knowing what matters.

---

## Step 1: Fetch today's calendar

Pull events from all three calendars:
- **Executive team**
- **Architecture + Advocacy**
- **Erin A+A**

Use today's date (from system context). Deduplicate events that appear across multiple calendars. Ignore all-day events (holidays, OOO blocks) unless they're relevant to a meeting.

For each event, note:
- Title, time, duration
- All attendees (names + emails)
- Video/location link if present
- Any linked agenda docs

---

## Step 2: For each event, research context

Work through events in chronological order. For each one, run the research appropriate to the meeting type (see rules below), then move to the next.

### Research rules

**Gmail search** — always, for every meeting. Search for threads involving the key attendees or the meeting topic. Look for: prior conversations, outstanding asks, context that would be awkward to forget.

**CRM profile lookup (Google Drive)** — only for 1:1 meetings (Erin + one other person, no one else). Search Drive for a profile file matching the attendee's name. If found, note the file link. If not found, skip silently.

**Web research** — only if the attendee is external AND Erin doesn't clearly know them (see below). Do a quick org lookup to understand what they do and what they care about.

### How to tell if Erin knows someone

Treat someone as known — skip web research — if ANY of these are true:
- Their email is @architectureandadvocacy.org, @usc.edu, or @columbia.edu
- They appear in multiple Gmail threads over several months
- It's a 1:1 meeting (Erin + one other person) — **1:1 always overrides this rule**: always do CRM lookup for 1:1s regardless of domain or familiarity

---

## Step 3: Write the briefing

Output everything in-chat. One section per meeting, in chronological order.

### Format for each meeting

```
**[TIME] | [MEETING TITLE]** | [meeting type: 1:1 / Phone call / Team meeting / etc.]
*[CRM profile link if found] | Attendees: Erin, [name(s)]*

[One-line bio: role, org, relationship to Erin/A+A. For group meetings, describe the group.]

- **[Month Year]:** [Most recent prior interaction]
- **[Month Year]:** [Next most recent]

Likely agenda: [1–2 sentences grounded in Gmail/Drive research.]

Smart questions:
1. "[Strategic, relational, or forward-looking — something Erin would actually ask]"
2. "[Another strong one]"
3. "[Third, if a strong one exists]"

**Opening line:** [One sentence. Specific, warm, direct. Sounds like Erin.]
```

### Rules

- Bio is always one sentence: who they are, where they work, how they connect to Erin or A+A.
- Prior interactions: 2 bullets max, most recent first.
- Likely agenda: 1–2 sentences of inference grounded in Gmail/Drive research.
- Smart questions: aim for 3; use 2 if a third strong one doesn't exist. Skip entirely for large group meetings.
- Opening line is always one sentence — warm, direct, personal. Not a pitch.
- For group meetings: skip individual bios, describe the group, omit Smart Questions.
- If no context is available, say so briefly and move on. Don't pad.
- End the full briefing with one sentence on the highest-leverage meeting and why.

### Progressive updates

Every time Erin corrects the format or says "always do X" / "never do Y" during a briefing session, update this SKILL.md immediately to reflect the new rule. This file is the source of truth for briefing behavior.

---

## A+A context

Erin is Co-Founder/CEO of Architecture + Advocacy, a design-justice nonprofit with chapters in South LA and Flatbush, Brooklyn. Use her frame when writing: community power, spatial justice, design-build, emerging professionals. Never say "marginalized" or "low-income."

Opening lines should sound like her: warm, direct, a little personal. Not a pitch. The thing she'd actually say.
