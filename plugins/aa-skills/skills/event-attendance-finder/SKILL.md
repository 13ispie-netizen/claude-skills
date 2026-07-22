---
name: event-attendance-finder
description: "Use this skill whenever the user wants to find upcoming public events a specific named person is likely to attend, is asked to build a prospect's event calendar, or wants to know where someone will be so they can meet them. Triggers on requests like \"find events [name] will be at\", \"where is [name] speaking\", \"build me an event list for [person]\", \"what's [person] attending\", or any donor/board/partner outreach research where the goal is to intercept a person at a public event. Often paired with a LinkedIn URL or a name plus a role. This skill confirms identity FIRST, runs multi-category web research, and returns a strict, honest events table with no fabricated events or URLs."
---

# Event Attendance Finder

Find upcoming public events a specific person is likely to attend, for outreach and relationship-building. Execute the steps in order. The identity gate in Step 1 is mandatory and comes before any event search.

Non-negotiable honesty rules apply throughout (see bottom). Never invent events, dates, or URLs.

---

## STEP 0: SET THE WINDOW

State the exact date range at the very top of the answer, using today's actual date.

- Default window is the next 4 months unless the user specifies otherwise.
- Write it plainly. Ex: "Date range: [today] to [today + 4 months]."

---

## STEP 1: IDENTITY CONFIRMATION -- DO THIS FIRST

Common names produce wrong matches. Do not search for a single event until identity is confirmed.

1. If given a LinkedIn URL, treat it as context only. LinkedIn blocks automated access. Do not claim to have read the profile. Use it only to infer name, role, company, location so open-web searches are accurate.
2. Search the open web to establish: current company/org, current role, and location.
3. Report the identifying details found and a confidence level: High, Medium, or Cannot confirm.

Gate:
- **Cannot confirm** -- say so, show the candidates found so the user can disambiguate, and STOP. Do not guess. Ask the user for one disambiguating detail (company, role, city, or a non-LinkedIn link).
- **High or Medium** -- proceed to Step 2, and list the confirmed current affiliations that will become search targets.

A single disambiguating detail from the user (ex: "President, [Foundation]") is usually enough to restart cleanly. Re-run identity confirmation once you have it.

---

## STEP 2: MULTI-CATEGORY SEARCH

Run multiple distinct searches. Vary the terms. Search each affiliated organization separately rather than combining them into one query. Cover all four categories:

1. Events the person has publicly posted about attending -- talks, panels, speaking slots.
2. News, press releases, interviews stating the person will be somewhere.
3. Events the person's own company or foundation is hosting or sponsoring.
4. Events hosted by any board, nonprofit, commission, university, or volunteer org the person is affiliated with. Pull the affiliation list from Step 1 and search each one.

Search guidance:
- Include the year, and the target window, in queries.
- Look for recurring patterns (annual galas, lecture series the person moderates, standing commission meetings). Note the typical month for each -- it may fall outside the window.
- Keep going until searches stop returning anything new. A stable "nothing new" result across several distinct queries is itself a valid finding.

---

## STEP 3: PRESENT THE TABLE

Output one table, sorted by date, earliest first, with exactly these columns:

| Date | Event (hyperlinked) | Host Organization | Location |
|------|--------------------|--------------------|----------|

Column rules:
- **Date:** the event date or date range. If there is no confirmed date, say so plainly in the cell (ex: "No confirmed date in window") rather than inventing one.
- **Event (hyperlinked):** the event name, hyperlinked to its registration page or the exact source page where it was found. Only use URLs actually returned in search results. If there is no valid URL, use plain text and write "no source URL" in that cell.
- **Host Organization:** who is hosting or organizing.
- **Location:** city / venue / virtual.

If zero confirmed in-window events are found:
- Say so directly. Do not pad the confirmed table with speculation.
- Then, if useful, provide a clearly separate table or list labeled "Leads / recurring patterns (inference, not confirmed)" with real source URLs, each flagged as unconfirmed. Keep confirmed facts and inference visibly separate.

---

## STEP 4: CLOSE WITH GAPS AND VERIFICATION

- State what is missing and why (ex: no public forward calendar, LinkedIn feed inaccessible).
- Give the highest-yield next steps to find more (ex: the person's own LinkedIn feed, a specific org's events page, or ask the user to name a suspected event/org to search directly).
- Add the standing caveat: event plans change; verify every finding against a primary registration or announcement page before relying on it.

---

## HONESTY RULES (NON-NEGOTIABLE)

- Do not invent events, dates, hosts, sources, or quotes.
- Only cite URLs returned in searches. Never fabricate or guess a URL.
- Never claim to have read a LinkedIn profile or any login-walled page.
- Distinguish confirmed facts from inference in every part of the output.
- If identity cannot be confirmed, stop at Step 1 rather than researching the wrong person.
- If there is not enough to answer well, say what is missing instead of filling the gap with speculation.

---

## NOTES

- This is research output, not a file. Do not save a document unless the user explicitly asks.
- A recurring role (annual lecture, standing commission seat) is a lead, not a confirmed event, until a specific in-window date is found.
- Funders and behind-the-scenes executives often have thin public forward calendars and announce appearances only after the fact. A sparse result is normal and should be reported honestly, not inflated.
