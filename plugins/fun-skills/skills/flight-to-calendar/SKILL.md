---
name: flight-to-calendar
description: >
  Add airline flights to Erin's personal calendar from a screenshot, confirmation email, or pasted itinerary. Always asks for Erin's current timezone before creating events, shows converted times for confirmation, then pins each event to its departure airport's timezone. Trigger whenever Erin shares a flight itinerary and wants it added to her calendar — even if she just says "add this flight" or "put this on my calendar."
---

# Flight to Calendar

Adds airline flights to Erin's personal calendar with correct timezone handling.

---

## Critical rule: each event is pinned to its departure airport's timezone

Google Calendar shows events in the viewer's timezone, but an event's own `timeZone` field controls what Erin sees when she opens it. The API allows **one** timezone per event (no separate start/end zones), so:

- Set `timeZone` to the **departure airport's** IANA zone (see table below).
- Pass `startTime` and `endTime` in that **same zone's offset**: departure as printed, arrival converted into the departure zone. The `timeZone` field overrides offsets, so a mismatched offset shifts the event.
- Never omit `timeZone`. Erin's Personal calendar defaults to `America/New_York`, so an event without a zone silently lands in Eastern.

Erin's device timezone is still used to **show her** the converted times for confirmation (Step 4).

---

## Step 1 — Ask for current timezone

Before doing anything else, ask:

*"What timezone is your device currently set to?"*

Wait for the answer. Do not proceed until confirmed.

Common answers: PT (UTC-8 standard, UTC-7 daylight), MT (UTC-7 standard, UTC-6 daylight), CT (UTC-6 standard, UTC-5 daylight), ET (UTC-5 standard, UTC-4 daylight).

---

## Step 2 — Extract flight data

From the screenshot, email, or pasted text, extract for each flight:

| Field | Notes |
|---|---|
| Route | Origin → Destination (e.g. LAX → ORD) |
| Date | Day + date (e.g. Thu Jul 16) |
| Departure time | As shown, plus the airport's local timezone |
| Arrival time | As shown, plus the airport's local timezone |
| Flight number | e.g. DL0967 |
| Aircraft | e.g. Boeing 737-800 |
| Stops | Nonstop or layover details |
| Terminal | Departure and arrival terminals if shown |
| Cabin class | e.g. Delta Main (X) |

### Timezone reference for major US airports

| Airport | Timezone | IANA zone (`timeZone`) | Standard offset | Daylight offset |
|---|---|---|---|---|
| LAX, SFO, SEA, PDX | PT | America/Los_Angeles | UTC-8 | UTC-7 |
| DEN, SLC, BZN | MT | America/Denver | UTC-7 | UTC-6 |
| PHX | MST (no DST) | America/Phoenix | UTC-7 | UTC-7 |
| ORD, MDW, DFW, IAH | CT | America/Chicago | UTC-6 | UTC-5 |
| ATL, MIA, JFK, LGA, EWR, BOS, DCA, IAD | ET | America/New_York | UTC-5 | UTC-4 |

For an airport not listed, look up its IANA zone; don't guess.

Note: The US observes daylight saving time from the second Sunday in March through the first Sunday in November. During that window, use the daylight offset column.

---

## Step 3 — Convert times to Erin's device timezone (for confirmation)

For each departure and arrival time:

1. Identify the airport's local timezone (see table above)
2. Calculate the UTC offset for that timezone (accounting for daylight saving)
3. Calculate the UTC offset for Erin's current device timezone
4. Apply the difference to convert the time

**Example:**
- Erin's device: PT (UTC-7, daylight saving active in July)
- ORD departure: 7:29am CT (UTC-5 in July) → 7:29am - 2hrs = **5:29am PT**
- LAX arrival: 10:00am PT → already in device timezone, **no change needed**

Always show Erin the converted times before creating events so she can confirm.

---

## Step 4 — Confirm before creating

Present a summary table for confirmation:

```
Flight 1: LAX → ORD | Thu Jul 16 | DL0967
  Departs: 7:40am PT (LAX T3)
  Arrives: 11:46am PT [= 1:46pm CT] (ORD T5)

Flight 2: ORD → LAX | Mon Jul 20 | DL1556
  Departs: 5:29am PT [= 7:29am CT] (ORD T5)
  Arrives: 10:00am PT (LAX T3)
```

Ask: *"Does this look right before I add to your calendar?"*

Wait for confirmation.

---

## Step 5 — Create calendar events

Use the Google Calendar `create_event` tool. Per flight:

- `calendarId`: `c_d233bc8f16c7ffa2820874d82c82d5b516666aa855e3aed6adce273f23645443@group.calendar.google.com` (Personal; skip `list_calendars`)
- `timeZone`: departure airport's IANA zone
- `startTime` / `endTime`: both in the departure zone's offset

**Example:** SLC → JFK, departs 5:10pm MT, arrives 11:40pm ET (= 9:40pm MT), October:
`timeZone: America/Denver`, `startTime: 2026-10-03T17:10:00-06:00`, `endTime: 2026-10-03T21:40:00-06:00`

Create all flights in parallel.

### Event format

**Title:** `✈ [ORIGIN] → [DESTINATION] | [Airline] [Flight#]`
Example: `✈ LAX → ORD | Delta DL0967`

**Description template:**
```
[Airline] [Flight#] | [Aircraft] | [Nonstop or # stops]
Departs: [local time] from [Airport] Terminal [#] (Gate TBD)
Arrives: [local time] at [Airport] Terminal [#] (Gate TBD)
Flight duration: ~[Xh Xm]
Cabin: [class]
```

**Location:** `[Origin Airport] Terminal [#] → [Destination Airport] Terminal [#]`

**Calendar:** Personal calendar (default -- do not add to A+A work calendars unless Erin specifies)

---

## Step 6 — Verify and confirm

Check each returned `start`/`end` against the approved times (the API may echo them in the calendar's default zone, so convert before comparing). If anything is off, fix it with `update_event` before reporting. Then confirm in chat, in Erin's device timezone:

```
Added:
✈ LAX → ORD | Delta DL0967 — Thu Jul 16, 7:40am–11:46am PT
✈ ORD → LAX | Delta DL1556 — Mon Jul 20, 5:29am–10:00am PT
```

Note any fields that were TBD (gates, seats) so Erin knows to check Delta closer to departure.

---

## Standing rules

- **Always ask for current device timezone first.** Never assume PT even if Erin is based in LA -- she travels.
- **One zone per event: the departure airport's.** Set `timeZone` and use that same offset for start and end. Never omit `timeZone`.
- **Always confirm converted times before creating.** Show the math (e.g. "1:46pm CT = 11:46am PT") so Erin can catch errors.
- **Personal calendar only** unless Erin specifies otherwise.
- **Never fabricate flight details.** If something is unclear in the screenshot, ask.
- **Gates are almost always TBD** at booking -- note this in the description and flag it to Erin.
