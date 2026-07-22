---
name: volunteer-meeting-recap
description: >
  Draft a concise volunteer recap email from a Fathom meeting transcript. Use
  this skill whenever Erin asks to send a meeting recap, summary, or update to
  volunteers, the community, or any non-staff audience after a meeting. Triggers
  on phrases like "write a recap", "send a summary to volunteers", "turn this
  into an email for the team", "write up the meeting", or when a Fathom link or
  transcript is present and the goal is an outgoing email. Always use this skill
  when the audience is volunteers, community members, or chapter members --
  even if Erin just says "write the email" or "send a recap."
---

# Volunteer Meeting Recap Skill

You are drafting a post-meeting email for A+A's volunteer community. The goal is a short, energetic update that makes people who missed the meeting feel caught up and people who attended feel celebrated -- without making anyone read a wall of text.

## Step 1: Get the transcript

If a Fathom meeting link or recording ID is not already in context, fetch the most recent meeting using the Fathom MCP tool (`list_meetings` with `include_summary: true`), then pull the full transcript with `get_meeting_transcript`. If the user pastes a transcript directly, use that.

## Step 2: Ask for any missing links (if not provided)

Before drafting, check whether the user has provided:
- A recording link (Fathom share URL)
- A slides link (Canva, Google Slides, etc.)

If either is missing, ask. Don't invent them. If the user says to skip one, omit that line from the email.

## Step 3: Draft the email

Output the email directly in the chat. Never save it as a file unless Erin explicitly asks.

Follow this exact structure:

---

Hi [Audience],

Missed the [Meeting Name]? [Watch the recording!](recording-link)

Want to look at the projects in more detail? [Review the slides](slides-link)

**Highlights:**

* **[Topic Name]:** one-sentence summary of what happened or was announced
  * sub-bullet for a key detail, stat, or follow-up (only if it adds real value)
* **[Topic Name]:** one-sentence summary
  * sub-bullet if needed

**Next Steps:**

* **[Action or date]:** brief description
* **[Action or date]:** brief description

-E

---

## Voice and formatting rules

These matter -- Erin has a specific style and will notice if you deviate.

**Tone:** Warm, personal, direct. Like a friend running a nonprofit. Genuine enthusiasm, never stiff or corporate.

**Length:** Short. Each highlight bullet should be one sentence. Sub-bullets are optional and only for things that genuinely add value (a stat, a link, a deadline). If in doubt, cut it.

**Bold formatting:**
- Section headers are bold: `**Highlights:**`, `**Next Steps:**`
- The topic label before the colon in every bullet is bold: `**Leadership Transition:**`

**Sentences:** Short. If a sentence runs over 25 words, split it.

**Em-dashes:** Use `--` (double hyphen), not `—`.

**Sign-off:** Always `-E`. Never "Best," "Warmly," or "Sincerely."

**Greeting:** `Hi [Audience],` is the default. For the A+A community, "Hi A+A Community," works well.

**Avoid:**
- Q&A format or interview-style recaps
- Long explanations of what happened -- just the key takeaway
- Corporate phrases: "synergy," "circle back," "leverage"
- Throat-clearing: "I hope this finds you well"
- Emojis (unless Erin specifically asks)

## What to highlight

Scan the transcript for:
- **Announcements** (new hires, new projects, funding wins)
- **Project updates** (what each chapter/team shipped or completed)
- **Data or outcomes** (survey results, attendance numbers, impact stats)
- **Upcoming events or deadlines** (next meeting, workshops, applications)
- **Opportunities for volunteers** (ways to get involved, funds available)

Skip internal discussion, process debates, side conversations, and anything that doesn't affect volunteers or isn't actionable for them.

## Example output

```
Hi A+A Community,

Missed the first-ever BiCoastal Bonding meeting? [Watch the recording!](https://fathom.video/share/...)

Want to look at the projects in more detail? [Review the slides](https://canva.com/...)

**Highlights:**

* **Leadership Transition:** Erin Light is A+A's first full-time Executive Director.
* **New Engagement Project @ South LA Wetlands:** A+A will collect community visions for the park restoration over the next 2 years -- volunteer opportunities expected to start in the fall.
* **LA Design-Build Success:** The LA chapter's ICA drum kit project engaged high schoolers in a full design-build cycle.
  * 8/8 students rated it 5 stars in the spring survey!
* **NY Tool Library Launch:** The NY chapter launched the Flatbush Mixtape Tool Library, a multi-year project built around a "solidarity economy" model.
  * Plans to host "Repair Cafes" where community members can come learn to use the tools.

**Next Steps:**

* **Save the date -- July 28, 5:30 PT / 8:30 ET:** Next BiCoastal Bonding meeting + 2027--2030 strategic plan kickoff.
* **Leadership Development Funds are available:** Use them for books, courses, or events this summer -- reach out to Erin.

-E
```

The example above is a good length target. If your draft is significantly longer, cut it.
