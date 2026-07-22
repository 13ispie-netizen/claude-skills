---
name: grant-application-template
description: "Fill out A+A's internal grant application template for a new grant opportunity. Use whenever Erin says 'fill out the grant template', 'start a new grant application', 'set up a grant folder', or shares a grant URL and wants to begin the internal process. Always use this skill when the goal is populating A+A's internal grant overview doc -- not just researching a grant."
---

# Grant Application Template

This skill walks through filling out A+A's internal grant application template for a new opportunity. It creates the project folder, copies the template, and fills it out section by section with Erin.

---

## BEFORE YOU START

1. Read `Grants HQ/MEMORY.md` to load active pipeline context.
2. Confirm the template source file exists at: `Grants HQ/Grants HQ Resources/Grant Applicaiton Template 2.docx`
3. Confirm or create the project folder: `Grants HQ/YYMMDD_[Grant Name]/`
4. Copy the template into the project folder and name it using the application deadline: `YYMMDD_[Grant Name].docx` (e.g., `260717_Claude Corps Fellow.docx`)

---

## STEP 1: GATHER GRANT INFO

If the user provides a URL:
- Fetch the page with `web_fetch`. If client-rendered, escalate to Claude in Chrome.
- Look for a PDF version of the application and fetch it -- PDFs contain the full question list.
- Extract: grant name, funder organization, application link, deadline, award amount, contact info, eligibility requirements, reporting requirements, matching requirements, payment method.

If the page is behind a login or inaccessible, ask Erin to paste the key details.

---

## STEP 2: FILL THE GRANT OVERVIEW TABLE

Fill these fields in col 2 of the template table using what you found. Leave blank if unknown -- never guess.

| Field | Instructions |
|---|---|
| Grant Name | Full official name |
| Organization | Funder name |
| Grant Application Link | Direct URL to the application |
| Grant Application G-Drive Folders | **Always leave blank** -- Erin fills this |
| Application Deadline | Full date + time + timezone if available |
| Grant Amount | Full award description (e.g., "Fully-funded fellow salary + $10,000 implementation grant") |
| Funder Contact Info | Name, title, email, phone, address if listed. Mark TBD if not found. |
| Award Notification Date | Date winners announced. Search funder site if not listed. |
| Quick Description of Award | What the grant funds -- use funder's own language |
| Grant Use Restrictions | Any restrictions on how funds may be used |
| Quick Description of Org | **Describe the FUNDER** (mission, focus, type of org) -- NOT A+A |
| A+A Contact (Submission) | Name/Title: Erin Light / Co-Founder + CEO; Email: office@architectureandadvocacy.org |
| Grant Amount Requesting | What A+A is asking for |
| Expected Grant Use | How A+A plans to use the funding -- draft from Erin's direction |

---

## STEP 3: SPECIAL CONSIDERATIONS

These are plain-text checkboxes `[ ]` / `[x]`. Work through each one based on what you know about the grant. Do not guess -- ask Erin if unsure.

The six conditions that would require board approval:
1. Funding is from a public government agency
2. Does not cover any overhead costs
3. Applying jointly with an organization A+A has not worked with before
4. It is a matching grant
5. Payment is through reimbursement
6. Proposed use does not fall under an existing A+A program (Architecture Workshop, Design-Build, Community Organizing Event, Advocacy Campaign, Leadership Development)

Check `[x]` for any that apply. If any are checked → **flag that board approval is required** before Erin proceeds.

---

## STEP 4: GO/NO-GO FIELDS

Walk through each go/no-go field **one at a time**. Ask Erin for her input on anything you cannot confirm from research.

### Checkbox rules
- Every line in the right column (col 2) must have a `[ ]` or `[x]` checkbox prefix.
- Every row label in the left column (col 0) must start with `[ ]`.
- **If any box in col 2 is checked `[x]`, check the col 0 label too `[x]`.** This means the criterion has been verified.

### Eligibility row
Replace the generic A+A boilerplate with only the eligibility requirements this specific grant asks for. Delete the rest -- they live in the master template in Grants HQ Resources for reference.

### Fields to complete

| Row | How to fill |
|---|---|
| Funding areas | Check all that apply from A+A's work |
| A+A applied before? | Yes/No -- check MEMORY.md |
| Geographic Area | Check NY and/or LA based on which chapters are relevant |
| Target Population | Check all that apply based on who A+A serves through this grant |
| Eligibility requirements | List only what THIS grant requires; checkbox each one |
| Has made grants to similar orgs? | Research funder's 990s or past grantee lists. List findings. |
| Know orgs that received grants? | Ask Erin |
| Grant award sufficient? | Yes/No based on award vs. program cost |
| Covers overhead? | Yes/No |
| Accepts unsolicited proposals? | Yes/No |
| Staffed? Contacted? | Yes/No -- note if contact has been made |
| Conflicts of interest? | Ask Erin |
| Payment method | Check the applicable option(s); use "Other" if none fit |
| Reporting requirements | List all reporting obligations |
| Matching requirements | List or mark "None" |

---

## STEP 5: FINALIZE

1. Save the completed `.docx` to the project folder.
2. Update `Grants HQ/MEMORY.md` -- add a row to the Active Pipeline table with: funder, program, ask, stage (Prospecting), deadline.
3. Update the project folder's `MEMORY.md` -- set status, deadline, and log that the template was completed.
4. Present the file using `mcp__cowork__present_files`.

---

## NOTES

- Never pre-fill answers by guessing. Only fill what you can confirm from the grant materials or from Erin directly.
- All cell 2 entries should be our working answers. Col 1 in the original template is reference content -- do not delete it from the master template in Grants HQ Resources.
- The template file lives at `Grants HQ/Grants HQ Resources/Grant Applicaiton Template 2.docx` (note the typo in the filename -- do not rename it).
- Use python-docx to read and write the .docx file. Never use the Read tool on a .docx binary.
- When writing multi-line content to a cell, use `cell.add_paragraph()` for each line after the first.
