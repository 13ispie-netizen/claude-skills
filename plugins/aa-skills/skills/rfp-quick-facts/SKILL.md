---
name: rfp-quick-facts
description: "Read an RFP/RFSQ in full and produce A+A's one-page 'Project Quick Facts' intake doc in Google Docs. Use whenever Erin shares an RFP, RFSQ, or solicitation (PDF/folder) and wants it summarized into the quick-facts sheet, says 'make a quick facts', 'RFP intake', 'fill out the quick facts template', or drops RFP documents into a project folder. Always use this skill when the goal is turning an RFP into A+A's scannable go/no-go intake doc."
---

# RFP Quick Facts

Turns an RFP/RFSQ into A+A's **Project Quick Facts** doc: a single two-column Google Docs table a board member can read in 5 minutes or less to make a go/no-go call.

The output is always a copy of the master template, filled and formatted in A+A brand style.

---

## KEY RESOURCES

- **Master template (Google Doc):** `1pbk38wUwLXUMOGD--5tGxsD60tj6VNc0ti4SaDK9Z6o` ("Project Quick Facts Template"). Two-column table: left = field labels (bold Public Sans), right = values (fill these).
- **A+A insurance holdings sheet:** `1O5y0sMzD1NBvxJ3EDZV0AoJ2nUeNhlv9` — always re-read live (holdings change) to confirm which insurance requirements A+A already meets.
- **A+A submission contact:** Erin Light, Co-Founder + CEO, office@architectureandadvocacy.org.
- **Fill mechanics (Google Docs API):** see `reference/fill-google-doc.md` — load it before editing the doc.

---

## WORKFLOW

### 1. Copy the template
Copy the master template into the RFP's Drive folder (or the folder Erin names). Name it `YYMMDD_[Project Short Name]_Project Quick Facts`. Use `gws drive files copy` or the Drive `copy_file` tool (set `supportsAllDrives` for shared drives).

### 2. Read the RFP in FULL
Read every page of the solicitation plus all appendices/forms — no skimming, including fine print, exclusions, and the Master Agreement terms.
- **Large PDFs (roughly 30+ pages): delegate the read to a subagent** so the full document stays out of the main context. Tell it to read the whole PDF in 20-page chunks with the Read tool, watch for **highlighted passages** (Erin highlights the parts relevant to A+A's scope), read the appendix .docx/.xlsx (`textutil -convert txt` / `openpyxl`), and return the field values below — verbatim where marked [VERBATIM].
- If no subagent is available, read it directly.

### 3. Fill the fields
Fill the right column of each row per the table below. Follow the CONVENTIONS.

| Field | How to fill |
|---|---|
| Project Name | Short official title + solicitation number. |
| Short Description | Plain-language, **two short sentences max**, what the RFP is actually seeking. |
| Organization Issuing | Issuing agency/department. |
| Project Address | Project location. **Blank if not listed.** |
| A+A Point Person | Usually Erin (whoever is completing it). |
| Contract Amount | Total/pool value. `N/A` if none (e.g., as-needed/on-call agreements). |
| A+A Proposed Fee | **Leave blank** (A+A's number, decided later). |
| Scope of Work Relevant to A+A | [VERBATIM] Copy the exact bullet points of services A+A would provide — usually the Community Engagement / outreach items. Render as bullets. |
| Due Date | Deadline (date + time + timezone). If rolling, note "rolling through [term end date]". |
| Award Notification Date | Date awards announced. `Not specified` if absent. |
| Contract Term | Start date - end date. |
| Partner Orgs | Who A+A is applying with. Blank if none/unknown. |
| Required Qualifications | Minimum mandatory requirements to submit. Bullets. |
| Optional Certifications + Benefits | A+A's LA County **Social Enterprise (SE)** certification and what it earns (prompt payment, bid preference). Note if it applies to work-order bids rather than this submission. |
| Insurance Requirements | [VERBATIM] Copy required coverage types + limits as **checkboxes**, grouped by category with sub-limits indented. Check each against the holdings sheet and tag `(held)`, `(NOT held)`, or `(GAP: ...)`. |
| Point Person | The RFP's listed contact + contact info. Keep the `Contacted?` checkbox. |
| Submission Documents | [VERBATIM] Copy the required-submittals list / TOC as bullets. |
| RFP Submission | Two checkboxes, Digital and Print. Fill the accepted method(s) with their instructions (email/portal/format/limits). Leave the non-accepted method unchecked with **no explanation**. |
| Conflicts of Interest | A+A's or its board's conflicts. **Usually blank.** |
| Contract "Red Flags" | Onerous/high-risk terms for a small nonprofit: indemnification, IP assignment, insurance burden, termination-for-convenience, liquidated damages, payment timing, records/audit, non-negotiable terms, etc. Bullets, one line each. |
| Draft Application | Hyperlink to the draft if one exists. Else blank. |
| Questions | Up to 3 sharp questions A+A might ask the review panel before submitting. |

### 4. Format + brand
Apply real bullets/checkboxes and A+A's body font per `reference/fill-google-doc.md`. All value text = **Nunito 11pt, color #36354d**. Labels stay bold Public Sans.

### 5. Hand off
Give Erin the doc link. Then, **in chat only** (never in the doc), surface: unknowns (e.g., missing submission time), insurance gaps, and the biggest go/no-go risks.

---

## CONVENTIONS (non-negotiable)

- **5-minute read.** Terse. No explanatory tails, no "Note —" context lines. State the fact, stop.
- **Blank when not listed.** If the RFP doesn't give a value, leave it blank. Use `N/A` or `Not specified` only where that is genuinely the answer.
- **Sentence counts are literal.** When a field says "two sentences," write two real short sentences. Never pad with em dashes, semicolons, or parentheticals to cram in more.
- **No em dashes.** Write `--` only if truly unavoidable.
- **No emojis.**
- **No caveats in the doc.** Verify/confirm/hedge language and risk flags go to Erin in chat, not into the deliverable.
- **Never guess.** Only fill what the RFP states or Erin confirms.

---

## NOTES

- This skill edits Google Docs via the `gws` CLI (Claude Code). If `gws` is unavailable, use whatever Google Docs editing tools the environment provides; the checkbox/bullet/font mechanics still apply. Degrade gracefully and tell Erin what could not be done.
- **The Google Docs API cannot set a checkbox's checked state.** Leave boxes unchecked and tell Erin to tick the applicable ones (one click each).
