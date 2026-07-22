---
name: board-premeeting-email
description: Draft a pre-meeting email to the A+A board of directors from the agenda. Use this skill whenever Erin asks to convert, draft, write, or send a board meeting email — even if she just says "write the board email" or "convert this agenda." Always use this skill when a board agenda is present and the goal is an outgoing email to the board. Also use when she asks to update or refine a previous board email draft.
---

# A+A Board Pre-Meeting Email

Draft a pre-meeting email to Architecture + Advocacy's board of directors, sent 5-7 days before the meeting.

---

## Before You Draft

Ask Erin these questions if the answers aren't already in the conversation:

1. What is the energy or headline of this meeting? (milestone, routine, heavy decisions?)
2. What does the board need to know that isn't on the agenda?
3. What does the board need to deliver at this meeting — and how prepared are they?

Do NOT draft until you have enough context to answer these. If the agenda is the only input, flag any gaps with [NOTE: ...] rather than inventing information.

---

## Key Facts

- **Meeting time:** 5:30 PT / 8:30 ET on Zoom (always, unless Erin specifies otherwise)
- **Date:** Encoded in the agenda filename as YYMMDD. Parse it and convert to readable format (e.g., "Thursday, May 28").
- **Erin recuses herself** from ED hiring/compensation discussions. Always note this with a brief FYI when relevant.
- **Guests** must always be named in pre-meeting emails if present on the agenda.

---

## Email Structure

Follow this order. Skip sections with no relevant content — do not pad.

### 1. INTRO (1-2 sentences)
- First sentence: frame the meeting's purpose. Lead with milestone energy if applicable.
- Second sentence: logistics — "Don't forget: [Weekday], [Month] [Day] at 5:30 PT / 8:30 ET on Zoom."

### 2. HOMEWORK / ACTION ITEMS
- Only include if board members must do something BEFORE the meeting.
- Header: "YOUR HOMEWORK (before [day]):"
- Numbered list. One concrete action per item.
- Name any linked documents by title — Erin will attach or hyperlink them.

### 3. KEY DECISIONS + DISCUSSION TOPICS
- Header: "Key Decisions:" or "What we'll cover:"
- 2-4 items max, framed as decisions or questions — not a play-by-play of the schedule.
- Hyperlink the full agenda where natural: "(full agenda)"
- Note any recusals with a brief FYI.

### 4. ADDITIONAL CONTEXT (optional)
- Forward-looking notes, disclosures, logistics the board should know but doesn't need to act on.
- 1-3 sentences max. Do not pad.

### 5. SIGN-OFF
- "Cheers!" for milestone or celebratory meetings
- "-E" for routine or informational meetings
- Always end with: "As always, let me know if you have any questions."
- Use one sign-off only — not both.

---

## Voice Rules

These apply to every email. No exceptions.

- **No em dashes** when another punctuation mark will serve
- **No vague filler:** never use "exciting," "interesting," "remarkable," or similar adjectives
- **One idea per line** — short sentences, line breaks between thoughts
- **The ask appears within the first 3 lines**
- Address board as "Hi A+A Board," or "Hi All,"
- Use "FYI" naturally for secondary disclosures
- No emojis in the body text (parenthetical asides with personality are fine)
- No jargon or corporate-speak — write for a smart generalist at an 8th-grade reading level
- Total email: under 300 words unless the agenda is unusually complex

---

## What NOT to Do

- Do not invent information not in the agenda — flag gaps with [NOTE: ...]
- Do not summarize the entire agenda — extract only what the board needs to prepare and decide
- Do not paste large blocks of legal or policy text inline — reference the document by name and note it's attached
- Do not include process details, internal task-force mechanics, or anything the board doesn't need to act on before the meeting
- Do not use both "Cheers!" and "-E" — pick one

---

## Progressive Updates

This skill is a living document. Whenever Erin states a clear rule — something to always do, never do, or do differently — update this SKILL.md immediately, before responding.

**Triggers for an update:**
- "always do X" / "never do X"
- "don't [do thing] anymore"
- "from now on, [rule]"
- A correction that implies a standing rule (e.g., correcting the meeting time, flagging a recurring mistake)
- Approval of a final email that contains a new pattern not yet in the skill

**How to update:**
1. Identify the clearest home for the rule (Key Facts, Voice Rules, What NOT to Do, Flags, etc.)
2. Edit this SKILL.md using str_replace before drafting any response
3. Repackage the .skill file and present it to Erin silently — no need to announce the update unless it changes something meaningful she should know about

Do not ask for permission to update. If Erin defines a rule, update the skill.

---

## Flags to Always Check

Before presenting a draft, verify:
- [ ] Is the secretary nominee name filled in (if there's an election)?
- [ ] Are all guest names included if guests appear on the agenda?
- [ ] Are all linked documents named so Erin knows what to attach?
- [ ] Is the meeting time correct (5:30 PT / 8:30 ET)?
- [ ] Does the ask appear in the first 3 lines?
- [ ] Is there a sign-off conflict (both "Cheers!" and "-E")?
