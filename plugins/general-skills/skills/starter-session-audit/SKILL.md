---
name: starter-session-audit
description: "Simple end-of-session audit that scans for uncaptured corrections, preferences, and decisions, then proposes saving them to the right workspace file. Use this skill whenever you say 'audit this session,' 'session audit,' 'what did we miss,' or 'end of session check.' Works with any Cowork workspace that has a CLAUDE.md and MEMORY.md in the root folder."
---

# Starter Session Audit

A lightweight audit that runs at the end of any Cowork session. It catches things you told Cowork during the session that should be saved permanently so you never have to say them again.

## What This Skill Does

Two things, and only two things:

1. **Scans for uncaptured learnings.** Looks through the conversation for corrections you made, preferences you expressed, and decisions you stated that aren't already written in your workspace files.
2. **Proposes where to save each finding.** For each uncaptured learning, it tells you which file it belongs in, what section, and the exact wording. You approve or skip each one.

That's it. No file reorganization, no cleanup, no progress tracking. Just: "Did I learn anything this session that should be remembered?"

## Step 1: Discover Your Workspace

Find your workspace root dynamically. Look for a CLAUDE.md file in the mounted workspace folder. Read whatever workspace files exist. The audit adapts to your setup — it works whether you have one workstation or twenty.

Read these files if they exist:
1. Root CLAUDE.md (standing instructions)
2. Root MEMORY.md (accumulated context)
3. Any workstation CLAUDE.md and MEMORY.md files that were used during this session
4. Any project CLAUDE.md and MEMORY.md files that were used during this session
5. **Master voice-principles.md** at `00. Resources/voice-principles.md`
6. **Any HQ voice-principles.md files** that were referenced or used during this session — check each HQ folder that was active (e.g., `Email HQ/voice-principles.md`, `LinkedIn HQ/voice-principles.md`, etc.)

## Step 2: Scan the Conversation

Go through the entire conversation from top to bottom. Look for these five signal types:

### A. Corrections

You fixed something Cowork produced. Maybe you changed a word, rewrote a sentence, adjusted a format, or said "no, do it this way instead." Each correction reveals a rule that Cowork should follow next time.

**What to look for:** Moments where you edited, rejected, or rewrote Cowork's output. Ask: what underlying preference or rule drove the change?

**Example:** You changed "Best regards" to "Thanks" on an email draft. The underlying rule: "Sign off with 'Thanks' for internal contacts."

### B. Explicit Preferences

You stated a preference directly. Words like "always," "never," "I prefer," "from now on," "I like it when," or "don't do that."

**What to look for:** Direct instructions about how you want things done, even casual ones.

**Example:** "I prefer bullet points over numbered lists." "Don't use exclamation points in subject lines."

### C. Decisions

You made a decision that affects future work. Chose one option over another, set a deadline, established a rule for a project, or resolved an ambiguity.

**What to look for:** Choices that should be recorded so Cowork doesn't re-ask the same question later.

**Example:** "Let's go with the $5,000 savings target." "Cancel the gym membership, keep Spotify."

### D. New Context

You shared a fact about yourself, your work, or your world that Cowork didn't previously know. Contact details, schedules, relationships, project updates, or anything that changes how Cowork should approach future tasks.

**What to look for:** Information that would help Cowork in a future session if it remembered it.

**Example:** "My rent went up to $2,600 starting next month." "Sarah is my new manager."

### E. Voice and Style Corrections

You corrected, overrode, or clarified a writing rule — either during content drafting or explicitly (e.g., "never do X," "always write it as Y," "that word is banned"). These corrections must be routed to the right voice file.

**What to look for:**
- You changed a word, phrase, or format in a draft and the change implies a rule
- You contradicted or clarified something in voice-principles.md or an HQ voice file
- You approved or rejected a phrasing pattern for a specific audience or format
- You resolved a conflict between two existing voice rules

**Routing rule — apply in order:**
1. Does the correction apply only to one HQ's audience or format (e.g., email sign-offs, LinkedIn post hooks, grant narrative tone)? → Route to that **HQ's voice-principles.md**.
2. Does it apply universally across all writing? → Route to **master voice-principles.md** (`00. Resources/voice-principles.md`).
3. Does it prescribe behavior ("always," "never," "before doing X")? → Also add it to **root CLAUDE.md** under `## Rules` or `## Preferences`.
4. If you're unsure, flag it and ask Erin which file it belongs in before writing.

**Example:** Erin says "em-dashes should be `--`, not rewritten away." → Update the em-dash rule in root CLAUDE.md and the checklist item in master voice-principles.md.

**Example:** Erin says "never re-warm a reply in an active email thread." → Route to `Email HQ/voice-principles.md` under Tone adjustments.

## Step 3: Filter Against What's Already Saved

For each finding from Step 2, check whether it's already captured in the workspace files you loaded in Step 1. Skip anything that's already written down. Only surface genuinely new findings.

For voice corrections specifically: check both the master voice file AND the relevant HQ voice file before concluding something is uncaptured. A rule may already exist in one but not the other.

## Step 4: Present Findings

Present each finding in this format:

```
**[Number]. [What happened]**

- **The rule/fact:** [Exact wording to save, written as a clear instruction or statement]
- **Where it goes:** [File path and section name]
- **Why:** [One sentence on why this matters for future sessions]
```

Group findings into two categories:

**Recommend (apply unless you object):** Clear-cut findings where the right action is obvious.

**Your call:** Findings where there's a judgment call or where you might want to phrase the rule differently.

If there are no findings, say so: "Clean session. Nothing new to capture." Don't manufacture findings.

## Step 5: Apply Approved Changes

After you approve (all, some, or none), write the approved changes to the appropriate files. For each change, confirm what was written and where.

**Important:** Never write changes without approval. Always present findings first and wait.
