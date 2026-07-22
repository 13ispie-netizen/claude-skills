---
name: clear-and-concise
description: Edit written output to be clear, concise, and direct. Use this skill whenever the user asks to edit, tighten, rewrite, or clean up their writing. Also trigger when the user says things like "make this clearer," "shorten this," "simplify this," "cut the fluff," "make it punchier," or pastes text and asks for an edit. Apply this skill to emails, bios, posts, product copy, blog drafts, or any prose that needs tightening. Always use this skill when editing is the goal, even if the user just says "can you clean this up?" or "how does this read?"
---

# Clear and Concise Editing

Edit the user's text without losing their tone. Apply all rules below.

## Rules

**Length**
- Keep the output under 150 words unless the user sets a different limit.
- Every word earns its place. Cut anything that restates what the previous sentence implied.

**Word choice**
- Use simple, common words. Prefer short words over formal ones (use "use" not "utilize," "show" not "demonstrate").
- Cut adjectives unless they change meaning.
- Turn two-word phrases into one word where possible ("in order to" → "to").
- No vague emotional words like "interesting," "exciting," or "important."

**Banned phrases**
- No AI giveaway phrases: "dive into," "unleash," "game-changing," "delve," "navigate," "landscape," "robust," "leverage," "unlock."
- No em dashes. Use a period, comma, or parentheses instead.

**Sentence structure**
- One subject, one verb per sentence. Split sentences with multiple clauses.
- Use simple present tense ("the app saves time," not "the app is saving time").
- No declarative clause followed by a colon that introduces an explanatory clause. (Wrong: "There is one reason: it works." Right: "It works.")
- No corrective redefinitions. (Wrong: "This isn't just a tool — it's a system." Cut it.)
- No metadiscursive setups. (Wrong: "Let me explain why this matters." Just explain it.)

## Output format

Return the edited text only. No preamble, no explanation, no "here's your edited version." Just the text.

If the user asks why you made a change, then explain. Otherwise, stay silent and deliver the edit.

## Progressive updates

After every edit session, scan the conversation for new rules the user has stated clearly — things like "never do X," "always do Y," or corrections they gave to your output. If you find any, add them to the relevant section of this SKILL.md before the conversation ends. Use the str_replace tool to edit the file directly. Do not ask permission. Do not announce the update unless the user asks. Just do it silently.

A rule qualifies if:
- The user stated it explicitly ("don't use passive voice," "keep sentences under 15 words")
- The user corrected the same pattern twice — treat the second correction as a rule

Do not add rules from vague preferences or one-off requests that won't apply again.
