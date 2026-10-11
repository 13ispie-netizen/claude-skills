---
name: onboarding-phase-2
description: "Run phase 2 of A+A employee onboarding once Erin has received and approved every signed phase 1 form: set up the employee's Drive folder and state-specific checklist, file the signed forms, pre-fill the DE 34 (CA) or PFL deduction notice (NY), and draft the posters email. SSN-safe: raw forms only pass through bundled scripts, so Claude never sees Social Security numbers. Use when Erin says 'run onboarding phase 2', 'onboarding step 2', 'their paperwork is in', 'file [name]'s onboarding docs', or similar."
---

# Onboarding Phase 2

**Starts when:** Erin has received every signed phase 1 form and confirmed they're correct. (Phase 1 isn't built yet.)

## SSN rule (hard)

Never open, read, download, or print an employee form yourself: no Read on PDFs, no Drive `read_file_content`/`download_file_content`, no Gmail attachment fetches. Every form goes through `scripts/`, which redact SSNs and report only "match" / "MISMATCH". The `ssn-guard` hook (general-skills) enforces this while the skill runs. If a script says a form is scanned, unreadable, or not a PDF, tell Erin to check it herself. Never fall back to reading it.

**Requires** the `gws` CLI and local Python (Claude Code on Erin's Mac). If `gws` is missing (e.g. Cowork), stop and tell Erin to run this in Claude Code. Don't try another route to the forms.

Run scripts as `python3 "<this skill's dir>/scripts/<script>.py" ...`. Every script prints short JSON.

## Key IDs (A+A shared drive: always `supportsAllDrives`)

- Employee folders parent: `1A6MK_7KCAnrRH54p72xhTM6TLRWX-edq`
- Master checklist: `1YdnWPbwk8JLwS1d4S17qjGCIKma0DpUBRLa5eBaJ9DI` (hard-coded in `checklist.py`)
- Workplace posters: https://drive.google.com/drive/u/1/folders/19vofA960x1fpXax9jEMo-1qRwD54JItB
- Blank DE 34 + 2026 PFL notice: bundled in `assets/`

## Steps

1. **Ask once** (single AskUserQuestion): employee's state (CA/NY) if Erin didn't say, how close she is with them, and the tone (brief + admin vs. warm). The audience is always the new employee.
2. **Find threads.** `search_threads` (metadata/snippets only) for the thread where the employee sent the signed forms, plus the signed offer letter thread if it's separate. Note the latest message id in the forms thread. If the employee shared a Drive folder link instead of attaching the forms, note that link (from the snippet) too.
3. **Folder.** Find `Last, First` under the parent, or create it with gws.
4. **Checklist.** `checklist.py --folder F --name "Last, First" --state CA|NY` (add `--doc ID` if a copy already exists in the folder). It copies the live master, so Erin's edits there carry into every new copy. Report the removed lines.
   - State-only lines are cut by pattern: a line that starts with "NY"/"CA" or contains "(NY)"/"(CA)" (see `REMOVE` in `checklist.py`). If the master still has native checkboxes, run `boxes.py convert --doc MASTER` once first so Claude can tick them.
5. **Forms.** `fetch_forms.py --folder F --thread T1 [--thread T2] [--drive-folder LINK]`. This copies the latest copy of every attachment and every file in the shared folder and returns redacted fields plus `ssn_check`. Compare name, address, city, ZIP, and dates across forms yourself. Get the start date, hourly rate, and weekly hours from the offer letter text (for a range, use the median); if the text didn't come through, ask Erin. Then read the employee's checklist copy and compare the forms against every item to collect for their state: any that's missing goes in the email.
6. **State form.**
   - **CA:** `fill_forms.py de34 --folder F --name "Last, First" --first .. --mi .. --last .. --street-num .. --street-name .. [--unit ..] --city .. --state .. --zip .. --start MMDDYY`. If ZIPs disagree, use the one that matches the city and flag it.
   - **NY, no PFL waiver among the forms:** `fill_forms.py pfl --folder F --name "Last, First" --employee "First Last" --rate R --hours H`. Keep the `local_path` for step 7.
7. **Email.** Write the body to a temp .txt file, then run `make_draft.py --reply-to LATEST_MSG_ID --to first@architectureandadvocacy.org --body-file body.txt [--attach PFL_LOCAL_PATH]`. This also turns off the guard lock. Body:
   - **First lines:** every missing form and every discrepancy (ZIP, name, address, SSN mismatch, ITIN warning), asking them to fix that form and resend. Say they're good to go *only* if nothing's off. For an SSN mismatch, name the forms only, never the number.
   - The posters link. CA: name the three EDD brochures in that folder (DE 2515 Disability Insurance, DE 2511 Paid Family Leave, DE 2320 For Your Benefit). NY + PFL: mention the attached deduction notice.
   - Erin's voice, short, no em dashes, signed "Erin".
8. **Tick the checklist.** `boxes.py tick --doc CHECKLIST --item "W-4" --item ...` for every form filed, the SSN check if it matched, and the PFL deduction calculator if used. Items only drafted (notices, posters) stay open until Erin sends.
9. **Report to Erin** (under 150 words): what was ticked and what's still open, folder link, checklist lines removed, forms filed (and any skipped older copies), SSN check result, discrepancies, the DE 34/PFL file, and a draft link. Remind her the DE 34 still needs the FEIN and CA employer account # and is due within 20 days of the start date. Always end by reminding her to fill out and sign the employer section (Section 2) of the I-9.

If anything fails mid-run, delete `~/.claude/onboarding-phase2.lock` only after confirming no raw forms remain in `~/.cache` (the scripts clean up after themselves).
