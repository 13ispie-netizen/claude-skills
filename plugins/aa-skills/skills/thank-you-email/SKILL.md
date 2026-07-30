---
name: thank-you-email
description: Write a thank-you follow-up email after a meeting using Erin's exact template. Use this skill whenever the user asks to write a thank you email, follow-up email, post-meeting email, or any email expressing gratitude after connecting with someone — even if they just say "write a thank you to [name]" or "follow up with [name] after our meeting." Always use this skill for any post-meeting outreach.
---

# Thank-You Follow-Up Email

Write a warm, specific, templated thank-you email after a meeting. Follow the structure below exactly — no deviation.

## Intake

When this skill is triggered, immediately ask the user for all of the following variables in a single message before writing anything:

1. **First name** of the person
2. **When you met** — compute this, don't ask blindly. See "Choosing the time phrase" below.
3. **The specific thing you want to mention** from the conversation
4. **Any follow-up to-dos** (optional)
5. **Any next meeting request** (optional)
6. **Any P.S. item** — a personal remark, shared experience, or warm send-off (optional)

Do not write the email until you have received all inputs.

---

## Choosing the time phrase

Sentence 1 is always "You were such a joy to talk with **[time phrase]**." The phrase depends on the gap between the meeting date and the date the email will actually be **sent** — not the date the draft is written. Drafts written at the end of the day are usually sent the next morning, so compute against the send date.

The phrase includes its own preposition. Drop it in verbatim — do not add "on".

| Gap between meeting and send | Phrase (use exactly) |
| :--- | :--- |
| Same day | `today` |
| 1 day (met yesterday, sending this morning) | `yesterday` |
| 2–6 days, same week | `on Wednesday` (the actual weekday) |
| 7–13 days | `last Wednesday` (the actual weekday) |
| 14+ days | `a couple of weeks ago` |

Verify the day rather than assuming:

```bash
date -j -f "%Y-%m-%d" "2026-07-29" "+%A"   # -> Wednesday
```

**Never say "yesterday" for a same-day send, and never name a weekday when "yesterday" is accurate** — naming the day when it was yesterday reads as though Erin had to look it up. If the send date is genuinely unclear, ask whether it goes out now or in the morning; a one-day shift changes the wording.

---

## Email Template

Use this structure exactly. Write in Erin's voice: warm, direct, genuine, unhurried.

---

Hi [Name],

You were such a joy to talk with [time phrase]. [Specific sentence beginning with "Your" — reference a concrete detail, insight, project, story, or opinion they shared.] I'm so glad we got to connect. It seems like we have a lot in common. Thank you for taking the time to meet with me.

[PARAGRAPH 2 — only if follow-up items exist]
I'm looking forward to [follow-up item(s)].

[PARAGRAPH 3 — only if another meeting needs to be scheduled]
[Note about scheduling the next meeting. Keep it light and warm, one or two sentences. No P.S. label — just a plain paragraph.]

[PARAGRAPH 4 — only if a personal remark exists]
P.S. [Personal remark: something social or personal that references a shared experience or a kind wish tied to something mentioned in conversation.]

-E

---

## Rules

- **Paragraph 1 is always present.** Paragraphs 2, 3, and 4 are conditional.
- The time phrase follows the table in "Choosing the time phrase" -- compute it from the SEND date, not the drafting date. An end-of-day draft sent next morning says "yesterday", not the weekday name.
- Sentence 2 must begin with **"Your"** and reference something specific from the conversation. Keep it short and simple — one clean sentence, no jargon, no complex clauses.
- Sentences 3 and 4 are **fixed phrases** — do not rephrase them.
- Paragraph 2 always starts with "I'm looking forward to" — do not vary this.
- Paragraph 3 (next meeting) is a plain paragraph with no label — no P.S., no prefix. Light and warm, one or two sentences.
- Paragraph 4 (personal remark) starts with "P.S." — include the periods.
- Signature is always "-E" — nothing else.
- No subject line unless the user asks for one.
- No em dashes. No emojis.

---

## Example

**Inputs:**
- Name: Jordan
- Met: Thursday; email being sent the next morning -> time phrase is "yesterday"
- Talking point: Jordan is building a community land trust in Detroit and mentioned it started from a personal experience losing their childhood home
- Follow-up: Send her the ExpandLA Coalition overview
- Next meeting: Want to reconnect in a few weeks
- Personal remark: She mentioned she's going to her family reunion this weekend

**Output:**

Hi Jordan,

You were such a joy to talk with yesterday. Your work building a community land trust in Detroit is really moving. I'm so glad we got to connect. It seems like we have a lot in common. Thank you for taking the time to meet with me.

I'm looking forward to sending over the ExpandLA Coalition overview for you to take a look at.

Let's find time to reconnect in the next few weeks. I'd love to keep this going.

P.S. Hope the family reunion this weekend is everything. Enjoy every second of it.

-E
