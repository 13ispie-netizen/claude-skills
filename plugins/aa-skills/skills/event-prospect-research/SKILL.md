---
name: event-prospect-research
description: >
  Build an A+A prospect research table from an event. Trigger this skill whenever Erin
  drops a link to an event (conference, summit, gala, convening, festival, forum) and wants
  to know who to connect with -- or says "prospect research," "who should I meet,"
  "build my prospect table," or pastes an event URL with a list of names. The skill confirms
  the event, researches each named person, and outputs a sorted, honestly-sourced prospect
  table -- including recent articles and podcasts -- saved as a CSV to the local CRM HQ folder.
---

# Event Prospect Research

Turn an event + a list of names into a ranked, sourced prospect table for Architecture + Advocacy (A+A). The single most important rule: **never fabricate a URL, fact, quote, role, article, or podcast.** Erin relies on this being trustworthy. Honest gaps beat confident guesses.

## When this runs

Erin drops a link to an event and wants to know who to meet on behalf of A+A. She may paste the names herself, or ask you to pull the speaker/attendee list from the event page.

## About A+A (use for alignment scoring)

A+A is a 501(c)(3) design-justice nonprofit (founded 2022) combining architectural expertise, community organizing, youth leadership, and in-house design-to-build capacity to give residents in underserved neighborhoods real power over what gets built around them. Chapters: South LA and Flatbush, Brooklyn. Budget ~$172K, transitioning from all-volunteer to staff-led. Core vocabulary: Spatial Justice, Community-Led Design, design-build, emerging professionals, underserved. A+A works at the intersection of spatial justice, land use, and community power over the built environment. Never use "marginalized," "low-income," or "full stop."

Targets usually fall into three buckets: (1) people leading spatial-justice / land-use / community-equity work, (2) funders (foundation staff, program officers, philanthropic leaders), (3) potential board members with real giving or convening capacity ("could pack a room / write a real check").

## Process

1. **Confirm the event.** Fetch the link. Identify event name, host org, dates, and location. State them back to Erin in one line so she can correct a wrong guess.
2. **Get the names.** If Erin pasted a list, dedupe it (people are often listed twice) and confirm the count. If she didn't, offer to pull the speaker/attendee list from the event page -- but only list names that actually appear there.
3. **Ask scope once** if the list is long or the ask is ambiguous (e.g., "articles/podcasts for everyone, or just the top-priority rows?"). Flag it if this will be a large, high-token research pass before you start (Erin's standing rule).
4. **Research each person** with web search -- multiple passes for funders and less-public figures. Parallelize across people where possible.
5. **Score, sort, and write** the table (columns below), sorted by Urgency Rank (column F) descending.
6. **Save the CSV to CRM HQ** locally (see Output), deliver it, and show the table + a short Confidence & Gaps note in chat.

## Columns (exact)

| Col | Content |
|-----|---------|
| A. Name | Person's name, hyperlinked to their **verified** LinkedIn profile. |
| B. Current Org | Current employer, hyperlinked to the org's official website. |
| C. Current Role | Current title. |
| D. Notable Accomplishments / Other Roles | Board seats, prior positions, awards, publications, affiliations -- whatever shows weight and reach. |
| E. Mission Alignment with A+A | 2-4 sentences: where their work intersects spatial justice / land use / community-led design, and how tight the fit is. Be specific and honest -- if alignment is thin or tangential, say so. |
| F. Urgency Rank (1-5) | How urgently to prioritize them: 5 = drop everything, 1 = nice-to-have. Base on alignment strength AND capacity to help A+A (funding, board potential, policy influence, network). Add a 3-6 word justification in parentheses. |
| G. Opening Line | A specific, human opening line framed around what THAT PERSON cares about / is working on -- never around A+A's needs. Reference something concrete from their work. |
| Recent Articles (last ~year) | Articles they authored in roughly the last 12 months, as "Title (Publication, Date): URL," separated by " || ". If an item is a feature/interview about them rather than their byline, label it as such. If none, write "None found in the last year" and optionally note the closest out-of-window item. |
| Recent Podcasts (last ~year) | Podcasts they hosted or guested on in roughly the last 12 months. **Podcast links must be Spotify links** (open.spotify.com). Same "Title (Show, Date): URL" format, " || " separated. If none, say so, and you may note the most recent out-of-window episode, labeled. |

## Sourcing rules (NON-NEGOTIABLE)

- Only include a URL that was actually returned by a web search or fetch. Never construct, guess, or pattern-match LinkedIn slugs or company URLs from memory.
- If you cannot verify a person's LinkedIn via search, leave the name un-hyperlinked and put "LinkedIn unverified -- search manually" in column A. Same logic for org URLs in column B.
- If you can't confirm which person a common name refers to, give the top candidate plus a clear flag rather than guessing.
- Do not fabricate accomplishments, roles, quotes, or affiliations. If a field is unknown after searching, write "Not found."
- Distinguish confirmed facts from inference. If E or F leans on assumption, note it.
- Verify dates before calling an article or podcast "recent." Search engines surface old pieces under recent-looking queries -- confirm the publication/episode date and say so if it falls just outside the window.
- For podcasts, resolve to the Spotify URL specifically (search "<name> <show> Spotify" or open the show/episode on open.spotify.com). Do not substitute Apple/Newsweek/other links.

## Scoring guidance (Column F)

- **5** -- Mission twin or top-tier funder/gateway: host-org leadership working directly on spatial justice/land use, or a funder with real grantmaking authority over relevant programs.
- **4** -- Strong: tight topical fit at senior level, or a funder-connector / big convener with board potential.
- **3** -- Solid/adjacent: real thematic kinship (youth leadership, community/economic justice, land/place) or high prestige with a plausible board/ally angle.
- **2** -- Tangential: little direct mission fit; value is reach, amplification, or network.
- **1** -- Icon/nice-to-have: inspirational or symbolic, little capacity to move A+A forward.

Weight both alignment AND capacity. When a high score rests mostly on capacity rather than mission fit (e.g., a major funder whose topic is only adjacent), say so plainly in column E.

## Output

- Save the table as a CSV to the local **CRM HQ** folder: `/Users/erinlight/Documents/Cowork Playground/CRM HQ/`. ("HQ" always means a local folder, reached via the device bridge -- never Google Drive or Notion.) Name it `<EventName>_Prospects.csv`.
- Split LinkedIn and org URLs into their own columns in the CSV (Name, LinkedIn URL, Current Org, Org URL, ...) so nothing is lost in a flat file. Keep the Urgency Justification as its own column next to the rank.
- Deliver the CSV to Erin, then also show the table in chat (rendered with hyperlinks) and a short **Confidence & Gaps** note: which rows are least certain, and which URLs/facts she should verify herself before relying on them.
- Do not put caveats or "verify this" language inside the deliverable body beyond what belongs in the honest E/F cells; surface process caveats to Erin in chat.

## Notes

- "Last ~year" means roughly the trailing 12 months from today. If the strongest item is a month or two outside that, include it but label the date so Erin can judge.
- Offer to widen the window (e.g., to two years) or to research the "Not yet researched" rows in a follow-up pass.
- Voice: no em dashes (use `--`), no emojis, economy over eloquence.
