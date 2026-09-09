---
name: internal-newsletter
description: "Draft A+A's internal volunteer newsletter as a Google Doc, pulling from board minutes, the board deck, the Fathom board check-in, Slack, the A+A calendar, and the volunteer roster sheets. Use whenever Erin says 'internal newsletter', 'volunteer newsletter', 'draft the newsletter', 'monthly newsletter', or asks for the member/volunteer update. Always use this skill when the audience is A+A volunteers and the output is the recurring internal newsletter."
---

# A+A Internal Newsletter

Build the monthly volunteer newsletter as a Google Doc. Audience is college-age A+A volunteers. Voice is Erin's: short, warm, fun, direct.

**Google Doc destination:** see `reference/sources.md`.
**File name:** `YYMMDD_A+A Internal Newsletter` (today's date).
**Project home:** `A+A Marketing HQ/Internal Newsletter/`. Every issue gets its own subfolder there named `YYMMDD_internal newsletter`. Create it first and keep the issue's working files (email HTML, resized images, notes) in it.

## Before drafting

1. Read `reference/sources.md` for all IDs, column maps, and channel IDs.
2. Read `00. Resources/voice-principles.md` in the workspace root. Match it.
3. Re-read every source live. Never reuse a prior month's pull.

## Token discipline

This workflow touches a lot of sources. Keep it cheap:

- **Fathom:** use `get_meeting_summary`. Never pull the transcript.
- **Board deck:** only open it if the minutes leave project updates thin. The minutes plus the Fathom summary usually cover Wins.
- **Slack:** `response_format: "concise"`, `limit: 20`. Check the newest message date first. If the newest post is older than 30 days, skip that section and stop reading.
- **Sheets:** `batchGet` only the named columns. Never read whole sheets.
- **Photos:** use Slack avatars. Web searches for volunteer photos reliably fail; do not run them.

## Sections, in this exact order

Do not add, rename, or reorder sections. Sections with no content are dropped entirely (see Hard rules).

### 1. Opening note from Erin
One or two sentences. Fun, energetic, welcoming. Include a joke that lands with architecture students.
**Never mention the board, board meetings, or board decisions in the opening.**

### 2. Get Involved!
Events from the A+A calendar in the next 30 days, in three subsections in this order: **NY**, **LA**, **A+A-Wide**.

- Hyperlink the **event title** to its calendar `htmlLink`. If Erin supplies an RSVP form link, use that instead.
- Format: `**[Title](link)** | Day, Date, Time | Location or "Virtual". One-line description.`
- A+A-Wide items are virtual/all-org. Give both PT and ET.
- **Exclude conferences that are not in NY or LA.** They can still appear under Wins.
- End the section, every time, with exactly:
  `Want everything in one place? [Subscribe to the A+A-wide Google Calendar](https://calendar.google.com/calendar/u/0?cid=YXJjaC5hZHZvY2FjeUBnbWFpbC5jb20).`

**Timezone trap:** the A+A calendar returns offsets in `America/Denver` regardless of the event's own `timeZone` field. Convert from the UTC offset, not the label, or every time will be wrong.

### 3. Project Updates
One block per active project. Header format:
`[Project Name] | [Program Type] | [City]`

- **Maximum 3 bullets** per project.
- Only what a general volunteer cares about. Skip budget, cash flow, governance, and anything board-only.

### 4. Wins
Grants, awards, RFPs won, speaking engagements, org milestones.
- **Never include funding amounts for grants.** Name the funder and the award, nothing more.

### 5. Birthdays This Month
Cross-reference all three roster sources (see `reference/sources.md`) and include only people who pass their source's filter. Add each person's Slack avatar.
End the section, every time, with exactly:
`Is it your birthday but you don't see yourself here? Make sure you've taken the [volunteer entrance survey](https://docs.google.com/forms/d/e/1FAIpQLScJdM3tj149jdse8WCM1ZpHRfKGoXbpPx1gmlyttp68gAGsbg/viewform?usp=dialog)`

If someone has no Slack avatar, leave them photo-free in the doc and give Erin their LinkedIn URL in chat instead.

### 6. Member Wins
From the `#kudos` channel. End, every time, with exactly:
`Don't forget to send your wins in #kudos!`

### 7. Resources
Internships, scholarships, jobs, networking events from the two resource channels.

### 8. Inspo from Other Orgs
From `#inspo`.

## Freshness rule (Resources and Inspo)

Never include an item unless its channel has messages from the last 30 days. Then check each item individually and drop anything whose deadline, application date, or event date has already passed. If nothing survives, omit the section under the empty-section rule.

## Hard rules

- **No caveats in the doc.** Never write "verify," "check this," "TBD," or any hedge into the deliverable. Surface every uncertainty to Erin in chat.
- **No em dashes.** Use commas, colons, or periods.
- **Empty sections get cut, not filled.** If a section has no qualifying content, leave it out of the doc entirely, heading and standing closing line included. Never pad with a placeholder note, an apology, or stretched-for old content. Inspo is the usual casualty. Say what you dropped in chat instead.
- Same when a source is unreachable: omit the section from the doc and flag the gap to Erin in chat. Never invent content.
- Sections that survive always keep their exact standing closing line.
- Run a negative-parallelism pass before publishing (see voice-principles.md).

## Writing the doc

Create as Google Doc from Markdown so headings, links, and images convert. See `reference/sources.md` for the two working methods and the multipart gotcha.

**Revisions:** edit the existing doc in place, same file ID and link. Only create a new dated file on a new day or for a major rewrite. When unsure, ask.

## Worked example

The September 2026 issue is the reference implementation:
`https://docs.google.com/document/d/1ZP_sT_kPg7cpM7yYIZFl4SMRCuxLk3zD7OuUploDuFE/edit`

**Re-read it live at the start of every run.** Erin edits it after publishing, and those edits are the current house style. Do not work from a remembered version of it.

Conventions it establishes, beyond the rules above:

- **Get Involved covers deadlines, not just events.** Application and RSVP due dates get their own line (`USC Student Applications Due | Tues, Sept 22, 11:59 PM PT`).
- **Every A+A-Wide item says why a volunteer would care.** Not `A+A Board Check-In | Virtual.` but `A+A Board Check-In | Virtual. Listen in or give comments on our annual budget.`
- **Event descriptions carry real context** about the partner and the community, not just logistics.
- **Project bullets describe what volunteers will make or do.** Erin cut contract mechanics and replaced them with the actual deliverable, e.g. high-school students designing a mobile shaded check-in kiosk.
- **Status claims stay literal.** She corrected "the Tool Library is open" to "is getting ready to open." Check the state of a thing before asserting it.

## Handing off to the email

The Google Doc is the deliverable for this skill. Stop here.

When Erin asks for the email version, that is a separate skill: **`newsletter-to-email`**. Do not build the email inside this workflow.

## Report back in chat

- Doc name and link
- Sections you dropped for having no content, and why
- Birthday conflicts across the three roster sources, and how you resolved them
- Anything you dropped and why
