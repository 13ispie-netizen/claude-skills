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

## Step 2: Get the PUBLIC recording link

**Always link the public share view of the Fathom recording, never the internal one.** Recipients are volunteers and community members without Fathom accounts -- an internal link locks them out.

- Public share links look like `https://fathom.video/share/<token>` (including the `/share/h/`, `/share/i/`, `/share/p/`, `/share/u/` variants).
- Internal links look like `https://fathom.video/calls/<id>`. **Never put one of these in the email.**

The Fathom MCP tools only return `/calls/` URLs -- they cannot generate a share link. So if Erin hasn't pasted a `/share/` URL, ask her for it: in Fathom, open the recording, click **Share**, enable public/anyone-with-the-link access, and copy that URL.

If a `/calls/` link is all you have, do not silently use it. Draft the email with an obvious placeholder and tell her what's missing.

## Step 2b: Ask for any other missing links

Also check whether the user has provided:
- A slides link (Canva, Google Slides, etc.)
- Any collaborative board used in the meeting (Figma, Miro) -- link it if referenced in a highlight

If either is missing, ask. Don't invent them. If the user says to skip one, omit that line from the email.

## Step 3: Draft the email

Output the email directly in the chat. Never save it as a file unless Erin explicitly asks.

Follow this exact structure:

---

Hi A+A-ers,

Missed the [Meeting Name]? [Live ask -- do this now!](link) and [Watch the recording!](share-link)

**Highlights:**

* **[What we did]:** one-sentence summary
* **[What you contributed]:** one-sentence summary

Key themes (see screenshots below):
* short theme, stated as A+A's shared position
* short theme
* short theme

**Action Items**

* **[The ask]:** what it is, who's already in, who to contact
* **[The ask]:** brief description

**[Project] Next Steps**

* **[Stage or season]:** what happens
* **[Stage or season]:** what happens

-E

---

**Lead with the live ask, not the recap.** If there's a still-open input window -- a Figma or Miro board taking stickies, a survey, a signup -- that goes in the very first line alongside the recording link. The recap's first job is pulling people back in, not summarizing the past.

**Action Items before the timeline.** What someone can do this week outranks what happens next spring. When listing a group to join, name who's already signed up -- it's social proof and it makes joining feel easy.

**Point to visuals.** If the meeting produced a board, deck, or whiteboard, screenshot the themes and reference them ("see screenshots below") instead of writing prose summaries of each one.

## Voice and formatting rules

These matter -- Erin has a specific style and will notice if you deviate.

**Tone:** Warm, personal, direct. Like a friend running a nonprofit. Genuine enthusiasm, never stiff or corporate.

**Length:** Short. Each highlight bullet should be one sentence. Sub-bullets are optional and only for things that genuinely add value (a stat, a link, a deadline). If in doubt, cut it.

**Bold formatting:**
- Section headers are bold: `**Highlights:**`, `**Next Steps:**`
- The topic label before the colon in every bullet is bold: `**Leadership Transition:**`

**Sentences:** Short. If a sentence runs over 25 words, split it.

**Em-dashes:** Use `--` (double hyphen), not `—`.

**Links:** The recording link must always be a public Fathom `/share/` URL, never a `/calls/` URL.

**Sign-off:** Always `-E`. Never "Best," "Warmly," or "Sincerely."

**Greeting:** `Hi A+A-ers,` for volunteers and chapter members. `Hi A+A Community,` for a wider list.

**Energy:** Use exclamation points. Erin's real emails have several. A recap with zero exclamation points reads flat and corporate.

**Avoid:**
- Q&A format or interview-style recaps
- Long explanations of what happened -- just the key takeaway
- Corporate phrases: "synergy," "circle back," "leverage"
- Throat-clearing: "I hope this finds you well"
- Emojis (unless Erin specifically asks)

## Report themes, not who said what

This is the single biggest failure mode. A recap is **not** meeting minutes.

Do NOT attribute ideas to individuals: "Bhavana raised...", "Ambika pushed to...", "Serena connected it back to...". Naming who said what turns a rallying email into a transcript summary and makes people who didn't speak feel like spectators.

Instead, synthesize each theme into A+A's collective position, written in first-person plural:

- Bad: *"Ambika pushed to flip the dynamic: what if we're the ones learning from community members?"*
- Good: *"we want to learn as much from community members as they learn from us!"*

The only place names belong is Action Items -- who to contact, and who has already signed up.

## AI tells to cut

Erin will spot these immediately. Scan your draft for every one before sending:

- **Discussion-shape narration:** "The conversation centered on...", "The room kept returning to...", "was the throughline", "connected it back to". Say the substance, delete the framing.
- **Rhetorical questions to the reader:** "Did residents find jobs? Did their kids get into school?", "What would it take to amplify that?" Never pose a question you then answer.
- **Punchy fragment as verdict:** a short declarative dropped after a longer sentence for effect ("Nobody tracks it."). Cut it.
- **"Not just X, but Y"** constructions and other neat antitheses.
- **Grand abstraction as a closer:** "The vision is A+A as the bridge, even when the outcome isn't a design-build."
- **Hedging tail clauses:** "...even when...", "...at least in part...", "...though it remains to be seen..."
- **Proof-of-concept / business-speak framing** applied to volunteer work.

Plain statements of what A+A wants, with energy, beat all of it.

## What to highlight

Scan the transcript for:
- **Announcements** (new hires, new projects, funding wins)
- **Project updates** (what each chapter/team shipped or completed)
- **Data or outcomes** (survey results, attendance numbers, impact stats)
- **Upcoming events or deadlines** (next meeting, workshops, applications)
- **Opportunities for volunteers** (ways to get involved, funds available)

Skip internal discussion, process debates, side conversations, and anything that doesn't affect volunteers or isn't actionable for them.

## Gold standard example

This is a real Erin-approved recap (strategic plan kickoff, July 2026). Match this voice, length, and structure.

```
Hi A+A-ers,

Missed the bi-coastal bonding? [Add stickies on Figma](figma-link) over the next week to have your voice heard! and [Watch the recording!](https://fathom.video/share/...)

**Highlights:**

* **We kicked off our 3-year strategic plan:** If A+A is wildly successful three years from now, what does that future look like, and what do we need to get there?
* **You brainstormed our impact on three audiences:** Young professionals, community members, and the architecture industry

Key themes (see screenshots below):
* we want to learn as much from community members as they learn from us!
* It's not just about the final build; architecture and design are part of the community-organizing ecosystem
* interest in exploring data, research and ethnography to elevate the intangible aspects of community that often get erased
* A+A being a platform for volunteers to "know where they land" and build both hard and soft skills
* Changing how architecture is practiced in the industry

**Action Items**

* **Sign up to join the small group:** A team will meet monthly (remote) over the next year to dive deeper into strategic planning topics and write the plan itself.
  * Members so far: Kianna, Reily, Susana, Eva, Ayesha, Ambika, Abri, Erin
  * Reach out to Erin/Abri to be involved
* **Leadership development funds:** Our fiscal year ends in a month. Use it to buy books, courses, events. Use your bill.com account or reach out to me or Reily!

**Strategic Plan Next Steps**

* **Small group meets:** to synthesize yesterday's meeting into outcomes the chapters can derive their goals from!
* **This fall:** Each chapter and the board writes a mini-plan based on the outcomes we identified.
* **Winter:** Share + align mini-plans
* **Spring:** Feedback on draft strategic plan iterations
* **Next summer:** Final plan published.

-E
```

Note what this example does: no individual attribution in the themes, themes written as A+A's collective position, the live Figma ask before the recording link, action items ahead of the timeline, named members as social proof, and real exclamation points.

The example above is a good length target. If your draft is significantly longer, cut it.
