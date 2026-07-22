---
name: flight-to-calendar
description: >
  Add airline flights to Erin's personal calendar from a screenshot, confirmation email, or pasted itinerary. Always asks for Erin's current timezone before creating events, then converts all times to that timezone before passing to the calendar API. Trigger whenever Erin shares a flight itinerary and wants it added to her calendar — even if she just says "add this flight" or "put this on my calendar."
---

# Flight to Calendar

Adds airline flights to Erin's personal calendar with correct timezone handling.

---

## Critical rule: the calendar API stores everything as UTC and displays in the device's local timezone

Do NOT pass times with foreign offsets (e.g. `-05:00` for Chicago) and expect the calendar to display them correctly in local time. It won't. Convert every time to Erin's **current device timezone** before creating or updating events — no exceptions.

---

## Step 1 — Ask for current timezone

Before doing anything else, ask:

*"What timezone is your device currently set to?"*

Wait for the answer. Do not proceed until confirmed.

Common answers: PT (UTC-7 standard, UTC-8 daylight), ET (UTC-5 standard, UTC-4 daylight), CT (UTC-6 standard, UTC-5 daylight).

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

| Airport | Timezone | Standard offset | Daylight offset |
|---|---|---|---|
| LAX, SFO, SEA, PDX | PT | UTC-8 | UTC-7 |
| DEN, SLC, PHX | MT | UTC-7 | UTC-6 |
| ORD, MDW, DFW, IAH | CT | UTC-6 | UTC-5 |
| ATL, MIA, JFK, LGA, EWR, BOS, DCA, IAD | ET | UTC-5 | UTC-4 |

Note: The US observes daylight saving time from the second Sunday in March through the first Sunday in November. During that window, use the daylight offset column.

---

## Step 3 — Convert all times to Erin's current device timezone

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

Use `event_create_v1`. Pass **all times using Erin's current device timezone offset only** — no mixed offsets.

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

## Step 6 — Confirm creation

After events are created, confirm in chat:

```
Added:
✈ LAX → ORD | Delta DL0967 — Thu Jul 16, 7:40am–11:46am PT
✈ ORD → LAX | Delta DL1556 — Mon Jul 20, 5:29am–10:00am PT
```

Note any fields that were TBD (gates, seats) so Erin knows to check Delta closer to departure.

---

## Standing rules

- **Always ask for current device timezone first.** Never assume PT even if Erin is based in LA -- she travels.
- **Never pass mixed timezone offsets to the calendar API.** Convert everything to device timezone before creating events.
- **Always confirm converted times before creating.** Show the math (e.g. "1:46pm CT = 11:46am PT") so Erin can catch errors.
- **Personal calendar only** unless Erin specifies otherwise.
- **Never fabricate flight details.** If something is unclear in the screenshot, ask.
- **Gates are almost always TBD** at booking -- note this in the description and flag it to Erin.
