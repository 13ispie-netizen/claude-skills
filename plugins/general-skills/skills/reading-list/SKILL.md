---
name: reading-list
description: >
  Add books, articles, podcasts, or videos to Erin's Notion reading list (the Read/Review/Research Tasks database). Trigger whenever Erin shares a book title, a photo or screenshot of a book list, a reading recommendation, or a link and says "add this to my reading list", "add these books", "save this to read later", "put this on my reading list", or similar. Always use this skill when the goal is getting something into the reading list — even if she just drops a photo of book covers with no instruction.
---

# Reading List

Adds items to Erin's Notion reading list, researched and tagged, in one batched write.

**Token discipline:** Never call `notion-fetch` on the reading database — the schema below is complete and the fetch costs ~20k tokens. Never search Notion for the database. Go straight to Step 1.

---

## The Database

Everything lives in **Read/Review/Research Tasks**.

- Data source ID: `111c9a33-bd41-81f6-88ac-000b876e0047`
- Create rows with `notion-create-pages`, parent type `data_source_id`

Properties to set (exact names and values — the emoji prefixes on Priority are real and required):

| Property | Type | Value |
|---|---|---|
| `Tasks` | title | The full title of the book/article/etc. |
| `Author` | text | From web research |
| `Format` | select | One of: `Book`, `Audiobook`, `Article`, `Podcast`, `Youtube`, `Online Course`, `Textbook` |
| `Priority` | select | One of: `VERY HIGH`, `🚨HIGH`, `🧀 Medium`, `🧊 Low` |
| `Project` | relation | Array with one category page URL (see Step 2) |
| `Notes` | text | Where Erin heard about it (see Step 3) |
| `Link` | url | Only if research surfaced a real canonical URL — never invent one |

Leave `Done` unset. It defaults to Not Done.

The old **"Books to Read"** database is archived and merged into this one. Never write there.

---

## Step 1 — Extract and Research

Pull every title out of what Erin shared (photo, screenshot, list, link, or plain text).

Then **web search each title** to fill in:
- **Author** — full name as published
- **Format** — a book is `Book` unless the title is clearly a podcast, article, video, or course

Rules:
- One search per title. Don't over-research — author and format are all that's needed.
- If a search comes back ambiguous or empty, leave the field blank and flag it in Step 4. Never guess an author.
- Run the searches in parallel.

---

## Step 2 — Get the Category List

The `Project` relation is Erin's reading category (Fiction, Leadership, Racial Justice + Economics, etc.), not an A+A work project.

Pull the live list with one cheap SQL call — never `fetch` the category database:

```
notion-query-data-sources
  mode: sql
  data_source_urls: ["collection://17ac9a33-bd41-8154-89d2-000b906dead2"]
  query: SELECT "Name", url FROM "collection://17ac9a33-bd41-8154-89d2-000b906dead2" ORDER BY "Name"
```

Use the returned `url` values for the relation.

---

## Step 3 — Ask (always, in one call)

Use a single `AskUserQuestion` call with only the questions that are actually open:

1. **Category** — ask whenever the right category is not obvious, and whenever a batch could plausibly land in more than one. Offer the 2–3 closest existing categories, plus a proposed new category if nothing fits well. Never guess silently.
2. **Priority** — ask every time Erin hasn't already said a level. Offer `🚨HIGH`, `🧀 Medium`, `🧊 Low`. Never default to a level on her behalf, and never assume "high priority" means VERY HIGH.
3. **"Where did you hear of this?"** — ask every time, no exceptions. Offer a few plausible sources (a person, a newsletter, a conference, the website it came from) and let her type her own. Her answer goes verbatim into `Notes`.

One source answer covers the whole batch when the items came from one place (one photo, one page, one recommendation). Ask per item only when the items clearly came from different places.

If Erin already gave a category or priority in her message, don't re-ask it.

---

## Step 4 — Write

Create **all rows in a single `notion-create-pages` call**, with every property set at once — including Priority. Never create first and patch properties afterward; that's one call per row and it wastes tokens.

Then confirm in a short message: how many items, which category, which priority, and any field left blank because research came up empty.

---

## Standing Rules

- Never leave `Project` blank. If unsure, ask (Step 3).
- Priority values carry emoji prefixes. `🚨HIGH` is not `HIGH`, and it is not `VERY HIGH`.
- Don't fabricate authors, links, or publication details. Blank and flagged beats wrong.
- Erin's reading list is personal — nothing here routes to an A+A workstation.

---

## Progressive Updates

Any time Erin corrects behavior or states a preference during a reading-list session, say what the skill change would be and ask before editing this file. Once she approves, that one approval covers the whole ship: edit, commit, push, repackage, and report the commit hash in the same response.
