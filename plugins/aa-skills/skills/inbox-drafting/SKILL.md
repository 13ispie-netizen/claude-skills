---
name: inbox-drafting
description: Draft replies to unread inbox emails from the last 24 hours in Erin's voice. Fetches headers, triages each thread, drafts replies for emails that need them, handles meeting requests by checking calendar and creating HOLD events, and presents all drafts in-chat for review with option to save to Gmail drafts. Use whenever Erin says "draft my inbox," "check my emails," "what needs a reply," or wants to process unread mail.
---

# Inbox Drafting Skill

## Purpose
Draft replies to unread inbox emails from the last 24 hours in Erin's voice. Present all drafts in-chat for review, with option to save each to Gmail drafts. Create calendar holds for any meeting confirmed.

---

## Workflow

### Step 1 — Fetch unread inbox
Call Gmail MCP: fetch unread threads from last 24h, headers only.
`query: is:unread newer_than:1d in:inbox -in:draft`

### Step 2 — Triage each thread
Classify each as one of:
- **draft** → needs a reply
- **skip** → automated notification (Google Pay, Google Docs @mention, newsletter, etc.)

Flag as **urgent** if any of the following apply:
- Legal matter
- Wetlands project
- Board member
- USC student (`.usc.edu` email)
- Columbia student (`.columbia.edu` email)
- Funder or major donor
- Explicit deadline stated in the email (within 48–72 hours)

Announce skipped threads in one line. Do not fetch their bodies.

### Step 3 — For each "draft" thread
Fetch the full thread. Read every message before drafting — never skim.

Then classify the email type:
- **Meeting request** → follow Meeting Request rules below
- **Standard reply** → follow Drafting rules below

### Step 4 — Present drafts
Show each draft with:
- Sender name + subject line as the header
- The specific message being replied to (quoted plaintext, no HTML)
- The draft copy
- ⚠️ ! flag if there is an action Erin must take before or after replying (e.g., sign a document, confirm something)

After all drafts: offer "save [name]" or "save all" to push to Gmail drafts.

---

## Meeting Request Rules

### Check availability
Call Google Calendar MCP. Check all four calendars: Executive Team, Erin A+A, Architecture + Advocacy, Personal.

### If they propose specific times
- Check calendar for conflicts during those windows
- If available AND times fall within preferred window (Wed/Thu 11am–3pm): accept
- If available but times fall outside preferred window: decline and offer 3 alternatives (see below)
- If urgent (see urgency list): accept if available, regardless of day/time

### If they ask for open availability
Offer 3 slots from Wed/Thu 11am–3pm for Erin to choose from. Do not commit to a time — present options.

### Urgency exception
Urgent emails get full flexibility: 9am–8pm, any day of the week.

Urgent = any of:
- Legal matter
- Wetlands project
- Board member request
- USC student (`.usc.edu`)
- Columbia student (`.columbia.edu`)
- Funder / major donor
- Explicitly stated deadline within 48–72 hours

### Duration defaults
- Intro / first call → 30 minutes
- Working session or unspecified → 1 hour
- Email specifies a time window → match it

### After confirming a time
Create a calendar HOLD on the **Executive Team calendar** (`office@architectureandadvocacy.org`):
- Title: `HOLD - [brief description]`
- Include in description: contact name, org, email, phone, any address from the email, and any action items (e.g., sign BSA before call)

---

## Drafting Rules

Apply all rules from Email HQ CLAUDE.md. Key reminders:

- Read the full thread before drafting
- Match greeting formality to the sender's email
- **Skip the greeting entirely** on short replies when the sender did not use one
- On active threads: drop re-warm, open with substance
- One-line and one-word replies are complete emails — do not pad
- `-E` is the default sign-off. Drop it on very quick one-liners
- Thank you goes at the end, not the opener

---

## Calendar IDs
- Executive Team: `office@architectureandadvocacy.org`
- Erin A+A: `erin@architectureandadvocacy.org`
- Architecture + Advocacy: `arch.advocacy@gmail.com`
- Personal: `c_d233bc8f16c7ffa2820874d82c82d5b516666aa855e3aed6adce273f23645443@group.calendar.google.com`
