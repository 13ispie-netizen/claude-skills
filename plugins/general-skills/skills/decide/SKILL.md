---
name: decide
description: "Decision Memo + Contrarian Check. Use whenever your_name says /decide, asks \"should I stop using X\", \"should I hire Y\", \"I'm torn between A and B\", or otherwise frames a founder-level decision they're stuck on. Runs an interview, structures the options with explicit assumptions, dispatches an opus-powered contrarian pass to find holes and second-order effects, and produces a saved decision memo with a clear recommendation and reversibility rating. Trigger this even when your_name doesn't say \"decide\" explicitly, whenever they're wrestling with a course of action and would benefit from a structured think rather than a Slack debate."
---


# /decide — Decision Memo + Contrarian Check

Help your_name make better, faster decisions by structuring the thinking, red-teaming the logic, and producing a saved memo to revisit.

The skill orchestrates three subagent passes:

| Pass | Model | Purpose |
|------|-------|---------|
| Structurer | sonnet | Organize the interview into a clean draft memo (context, options, assumptions, pros/cons) |
| Contrarian | opus | Red-team the logic, surface hidden assumptions, name second-order effects |
| Synthesizer | opus | Weigh structure vs contrarian pass, recommend, name reversibility and kill criteria |

The interview happens in the main session. Subagents handle the heavy thinking.

## Step 1: Run the interview

Ask one question at a time. Wait for the answer before moving on.

1. What's the decision? One sentence.
2. What are the options on the table?
3. Why now? What's forcing the decision?
4. What's the decision window?
5. Who's affected? (your_name, team, customers, revenue, brand)
6. What's your gut leaning? Capture verbatim.
7. What would have to be true for your leaning to be wrong?

If the user gives all answers in one message, skip the questions you have. Echo back a one-paragraph summary and ask for confirmation before dispatching subagents.

## Step 2: Pass 1 — Structurer (sonnet subagent)

Dispatch with the Agent tool, `subagent_type: general-purpose`, `model: sonnet`. Give it the interview transcript and the memo template. It returns Context, Decision Framing, and Options sections only (with explicit assumptions, pros, cons per option). Direct tone. No em-dashes.

## Step 3: Pass 2 — Contrarian (opus subagent)

Dispatch with the Agent tool, `subagent_type: general-purpose`, `model: opus`. Give it the structured memo and your_name's stated leaning.

Look for: holes in logic, hidden assumptions, second-order effects (6-12 months out), motivated reasoning, what would flip the decision. Return a numbered list of 4-7 sharp critiques. End with the strongest single argument for the option your_name is NOT leaning toward.

## Step 4: Pass 3 — Synthesizer (opus subagent)

Dispatch with the Agent tool, `subagent_type: general-purpose`, `model: opus`. Give it the structured memo plus the contrarian critique.

Produce a Recommendation section with:
- Pick: which option you recommend
- Why: 2-4 sentences referencing the memo and contrarian pass
- Reversibility: one-way door or two-way door, with explanation
- Kill criteria: specific, observable, time-bound ("I'd reverse this if {X} happens within {Y timeframe}")

Be willing to disagree with the user's leaning if the contrarian pass made a stronger case.

## Step 5: Assemble and save

Stitch the three outputs together using `references/memo-template.md`:
1. Header (decision title, date, reversibility)
2. Context + Decision Framing + Options
3. Contrarian Pass
4. Recommendation

Filename: `Decision-{slug}-{YYYY-MM-DD}.md`
Save to: `vault_path/Decisions/{filename}`

## Step 6: Report back

Post in chat:
- Decision memo saved: path
- TL;DR: pick, reversibility, kill criteria (one-liner)

Don't repeat the full memo in chat.

## Style rules (apply throughout, including subagent prompts)

- No em-dashes — use periods, commas, or restructure (hard rule)
- Direct, conversational. No hedging.
- Specific over general. "Revenue drops 15% in Q3" beats "things go badly"
- Bullet over paragraph when listing
- Don't sycophantize. The point is better thinking, not validation.

## When NOT to use this skill

- Pure information lookups
- Already-decided actions where the user wants execution
- Tasks that fit a more specific skill (`/today`, `/follow-up`, `/newsletter`, etc.)