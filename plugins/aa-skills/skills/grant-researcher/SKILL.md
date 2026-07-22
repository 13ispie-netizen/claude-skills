---
name: grant-researcher
description: "Use this skill whenever the user provides a URL to a grant, fellowship, award, conference application, or LOI opportunity and wants it researched and formatted. Triggers on any message containing a URL alongside words like \"grant\", \"fellowship\", \"award\", \"funding\", \"application\", \"LOI\", \"opportunity\", or \"deadline\". Also trigger when the user says things like \"look up this grant\", \"add this to my tracker\", \"research this funding\", or pastes a link and asks what it's about in a funding context. This skill performs multi-round web research, extracts structured grant data, presents it as a formatted table for confirmation, then outputs a tab-separated row ready to paste into Google Sheets."
---

---
name: grant-researcher
description: >
  Use this skill whenever the user provides a URL to a grant, fellowship, award, conference application, or LOI opportunity and wants it researched and formatted. Triggers on any message containing a URL alongside words like "grant", "fellowship", "award", "funding", "application", "LOI", "opportunity", or "deadline". Also trigger when the user says things like "look up this grant", "add this to my tracker", "research this funding", or pastes a link and asks what it's about in a funding context. This skill performs eligibility screening first, then multi-round web research, extracts structured grant data, and presents it as a formatted table for confirmation.
---

# Grant Researcher

When the user provides a URL to a grant, fellowship, award, conference application, or LOI, execute the following steps in order.

---

## STEP 0: ELIGIBILITY CHECK — DO THIS FIRST

Before researching any fields, check whether A+A meets the grant's eligibility requirements.

Read the grant page and extract all eligibility criteria. Then evaluate each one against what you know about A+A:

- 501(c)(3) under IRS sections 509(a)(1) and 170(b)(1)(A)(vi)
- 1 staff member
- Revenue ~$120,000/year
- Founded June 2022
- Based in Los Angeles, CA and NYC (Flatbush, Brooklyn)
- "Flatbush" is a program location, not a legally separate chapter or affiliate
- Focus: spatial justice, community-led design, youth leadership, design-build

For each requirement, mark it:
- ✅ Pass
- ❌ Fail — **stop here**, tell the user A+A does not meet this requirement, explain why, and ask how they'd like to proceed
- ⚠️ Unclear — flag it, suggest language to verify (e.g., "Worth confirming with [contact] whether [specific question]"), and continue with research

Present the eligibility check as a table before proceeding to Step 1.

Only continue to Step 1 if there are no hard ❌ failures, or the user explicitly instructs you to proceed anyway.

---

## STEP 1: RESEARCH

Perform **two rounds** of research before filling any fields.

### Round 1 — The provided URL
Load and read the grant page directly. Extract every field you can from that page alone.

### Round 2 — The funder's broader site and history
- Navigate to the funder's main website (the root domain)
- Look for: past grantees/awardees lists, previous cycle deadlines, notification timelines, reporting requirements, contact information, grant guidelines PDFs
- Search web history for past cycles to infer missing dates (see Due Date rules below)
- Use the **Kindora MCP** to search the funder's 990 filings for organizations they have previously funded — use this specifically to populate **Similar Groups Funded**

Only use web search when the grant page or funder site is missing information — do not search unnecessarily.

---

## STEP 2: FILL THE FIELDS

Apply these rules for each field:

| Field | Instructions |
|---|---|
| **Due Date** | Find the application deadline. If not listed, search web history of past cycles and return the **1st of the same month next year** (e.g., if historically due April 14 → return April 1, 2027) |
| **Application Type** | Choose one: `Application` or `LOI` |
| **Revisit Date** | Exactly 2 months before the Due Date. May fall in a future year — calculate carefully. |
| **Notification Date** | Date grant winners will be announced. Search funder site and past cycles if not on the page. |
| **Grant Name** | Full official name, hyperlinked to the provided URL |
| **Use** | Choose one: `Project Restricted`, `Unrestricted`, `Individual`, `Fellowship`, `Capacity`, `Award`, or `Conference` |
| **Organization** | Funder's full organization name, hyperlinked to their homepage |
| **Amount** | Dollar amount or range (e.g., `$5,000–$10,000`). Search if not listed. |
| **Matching** | Choose one: `Matching` or `Non-Matching` |
| **Google Drive Folder** | Leave blank |
| **Quick Description** | Pull directly from the funder's own grant page copy, lightly edited for length. Do not paraphrase from scratch. Preserve the funder's language and framing. |
| **Grant Start Date** | When the funded project/activity may begin |
| **Grant End Date** | When the funded project/activity must conclude |
| **Report Due** | Reporting deadline(s) after grant period ends |
| **Similar Groups Funded** | See rules below — return exactly 3, each hyperlinked to their website |
| **Contact Person** | Name and email address if listed anywhere on the funder's website |

### Similar Groups Funded — Selection Rules

Pull candidates from the funder's 990s (via Kindora MCP), past grantee lists on their site, and web search. Return exactly **3 organizations**, each hyperlinked to their own website.

Prioritize organizations that meet as many of these criteria as possible, in order of priority:
1. Located in **NY or LA metropolitan areas**
2. Focus on any of: architecture, urban planning, placemaking, public art, urban revival, youth leadership, civic engagement, innovative approaches, youth arts
3. **Social-justice and systems-change oriented**

If no past grantees are findable, leave the field blank rather than fabricating.

---

## STEP 3: PRESENT AS A TABLE

Present all findings as a **formatted markdown table** with fields as columns and one populated data row beneath — not fields as rows.

Leave any unfound fields blank.

Then ask:
> **"Does this look correct? Please confirm."**

---

## Notes

- Never fabricate data. If a field cannot be found after both research rounds, leave it blank.
- If the URL is behind a login wall or is otherwise inaccessible, tell the user and ask for the grant guidelines as a pasted text or uploaded PDF.
- If the funder has multiple grant programs, confirm with the user which program the URL refers to before proceeding.