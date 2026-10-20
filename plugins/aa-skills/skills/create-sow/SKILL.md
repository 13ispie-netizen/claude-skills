---
name: create-sow
description: "Write an A+A scope of work / fee-for-service scope proposal as a branded Google Doc, built from A+A's six standard phases and the Services Module Menu. Use whenever Erin says 'create a SOW', 'write a scope proposal', 'draft a proposal from this outline', 'fee for service proposal', or shares an outline/brainstorm for client work (engagement sub-consulting for a design firm or agency, or a community-backed strategic plan for a community organization)."
---

# Create SOW

Turns an outline or project notes into A+A's **Fee for Service Proposal**: a Google Doc in A+A's proposal format, branded with the A+A document template, using standard phases and module language.

## Sources of truth (Contracted Work shared drive)

| File | ID | Use |
|---|---|---|
| 261019_A+A Services_Module Menu Template | `1BGMVRlzLF8FK9Pjvj_92DS_X2cTdmOLcTSwxrlZ-cMA` | Phases, modules, ready SOW language + deliverables, SOW Language tab (exclusions, acceptance) |
| 261019_Billing_Fee Worksheet Template | `1N6jxj5KE_ZhVsl4AAAl5_4zxZ14zE2hR5xp927Ze8R0` | Fees + hours; its **Rules** tab is the master list of standing rules |

Read the menu's Module Menu (cols A-I) and SOW Language tabs plus the fee worksheet's Rules tab once per run. They override anything below if they differ.

## Step 0: ask first (one round, multiple choice where possible)

1. Product line: Engagement Sub-consultant (client = design firm/agency) or Community-Backed Strategic Plan (client = community org, A+A leads with sub-consultants)
2. Fee: numbers known, or phase breakdown with blank $
3. Terms: include payment/reimbursable/rate sections, or leave out for now
4. Start date, or leave blank
5. Destination folder: default is the folder the outline lives in. Check its sharing first (step 6).

## Step 1: map the outline to the six phases

Every proposal uses all six, in order. Task numbers 1.0-6.0 match phase numbers; add-ons nest inside the phase they serve.

1. **Discover + Plan**: client goals, site research/history, interviews, detailed work plan + schedule, decision-power framework, evaluation metrics (baseline for Phase 6).
2. **Community Organizing**: canvassing, outreach to community-based orgs/schools/partners, stakeholder power map + contact list, focus-group recruitment beyond the client's own members, coalition building. **Never cut; scale down.** Architects skip this phase; A+A makes it explicit. If the outline has no on-the-ground organizing, add it and flag that to Erin.
3. **Engage**: formats from the menu (focus groups, pop-ups, workshops, block parties, open houses, virtual meetings, surveys). One block per engagement round.
4. **Synthesize + Draft**: coding, findings, draft plan, draft presented back to the community. List **sub-consultant coordination** explicitly.
5. **Final + Launch**: revisions, final branded deliverable, pitch materials, public report-back/activation/launch. List **sub-consultant coordination** explicitly.
6. **Evaluate**: participant survey, engagement metrics vs. neighborhood demographics, "you said, we did" report-back, debrief.

Use the module's menu language as the starting point, then tailor it to the project.

## Step 2: standing rules (also on the fee worksheet's Rules tab)

- **PM inside every phase**, as its last numbered item, never a standalone task: up to [N] 1-hour virtual meetings with Client (every other week) + emails and phone calls as needed. N = ROUNDUP(phase weeks / 2).
- Virtual meetings = 1 hr. In-person meetings carry 1 hr drive time each way (pricing only; don't write it in the doc).
- **Deliverables are always a lettered list** (a, b, c), nested under the activity that produces them.
- Every count is a cap: "up to X".
- Third person: "Architecture + Advocacy will...". Define (The Project), (Client), (Project Team), (the Site) in the Overview.
- Formal contract language ("relinquish", not "give up" / "part with"). No em dashes.
- Comparison matrices (e.g., pathways x requirements x research x deliverables) may be a table with bullets in cells. Everything else is lists.
- Default sections: A. Overview, B. Scope, C. Scope Exclusions, D. Compensation, E. Acceptance. Add terms/rates only if Erin says so.

## Step 3: write the HTML

Fill `reference/skeleton.html`. Task line format: `<p><b>N.0 Phase Name (Months x-y)</b> | narrative. This includes:</p>` then an `<ol>` of activities. Lettered lists use `<ol style="list-style-type:lower-alpha">` (Docs import keeps it). Run a negative-parallelism pass on the prose before upload.

## Step 4: create the Google Doc

Name: `YYMMDD_[Project]_Scope Proposal_draft1`. Replace `[LOGO_IMG]` with `<img src="data:image/png;base64,..." width="72" height="72">` from `00. Resources/A+A+Logos-03.png`.

- With `gws` (Claude Code): `gws drive files create --params '{"supportsAllDrives":true}' --json '{"name":"...","mimeType":"application/vnd.google-apps.document","parents":["FOLDER_ID"]}' --upload file.html --upload-content-type text/html`
- Without `gws` (Cowork): Drive connector `create_file` with `contentMimeType: text/html` and `parentId`. Styling in step 5 then needs the Docs connector or gws; if neither exists, say so and deliver unstyled.

## Step 5: brand it (one pass)

```
gws docs documents get --params '{"documentId":"ID"}' > doc.json
python3 scripts/style_gdoc.py doc.json batch.json
gws docs documents batchUpdate --params '{"documentId":"ID"}' --json "$(cat batch.json)"
```
The script applies the aa-document-template fonts and colors (Public Sans Black/ExtraLight/ExtraBold headings, Nunito body, #36354d / #f5a17d, rule under the subtitle) and styles tables (shaded header, 10pt cells, tight bullet indents). Then tell Erin to click the logo and set **Wrap text**; the API can't.

Gotchas:
- Docs only keeps weights 800/900 when `bold` is true (the script handles it).
- Files in shared drives need `supportsAllDrives: true` on Drive calls, or you get "File not found".
- Style from a fresh read taken right after the import, in one batch with the revision guard. Piecemeal styling has moved the inline logo into the title.
- **Re-importing HTML replaces the whole doc.** Before any re-import, re-read the live doc and diff its text against your last version. If Erin edited, fold her edits into the HTML first or edit in place instead.

## Step 6: verify and report

- Export PDF and look at page 1 (and any table page).
- Check sharing: `gws drive permissions list` with `supportsAllDrives`. If the doc inherits a large shared drive (students, volunteers, personal Gmail), tell Erin who can open it and recommend a restricted folder. Never change sharing without asking.
- Log the doc link in the owning HQ's MEMORY.md Reference Links table.
- In chat (never in the doc), list every gap you filled or assumption you made.
