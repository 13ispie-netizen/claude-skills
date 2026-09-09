# Internal Newsletter: sources, IDs, and column maps

Load this only when actually running the newsletter workflow.

## Destination

Newsletter folder: `1s2-tWdxCqNft_E7dCITZreP61XxI2TE_`
File name: `YYMMDD_A+A Internal Newsletter`

## Calendar

A+A calendar ID: `arch.advocacy@gmail.com`
Public subscribe link: `https://calendar.google.com/calendar/u/0?cid=YXJjaC5hZHZvY2FjeUBnbWFpbC5jb20`

Pull all events for the next 30 days, `orderBy: startTime`. Use each event's `htmlLink` for the title hyperlink.

**Timezone trap:** this calendar reports offsets in `America/Denver` even when an event's own `timeZone` says Los_Angeles or New_York. Convert from the UTC offset in `start.dateTime`, not from the label. Cross-check against the `recurringEventId` suffix (e.g. `_20260923T003000Z`), which is true UTC.

Sort events into NY, LA, or A+A-Wide (virtual/all-org). Drop conferences outside NY and LA.

## Board sources

Board meetings root: `1bemQltpMkHIlZhPPaL_U9kTUeO0qNJho`
Inside it, fiscal-year folders (`FY 26-27`, `FY 25-26`), each holding `YYMMDD` meeting subfolders. Use the most recent dated subfolder. It contains the minutes doc, the agenda, and the board deck.

Fathom: search `A+A Board Check-In`, `recorded_by: "anyone"`. Use `get_meeting_summary` on the newest hit. Never pull the transcript.

Read order: minutes → Fathom summary → deck only if project updates are still thin.

## Slack channels

| Purpose | Channel | ID |
| :-- | :-- | :-- |
| Member Wins | `#kudos` | `C0BUQA8B64U` |
| Resources | `#job-and-scholarship-opportunitiess` | `C0AT0DWDHV2` |
| Resources | `#la-community-and-networking-events` | `C0AUA75BRFH` |
| Inspo | `#inspo` | `C07JZDSB4CQ` |

Read with `response_format: "concise"`, `limit: 20`. Check the newest timestamp before reading further.

Volunteer photos: `slack_search_users` returns a `Profile Pic` URL. Swap `_original.png` for `_192.png` for a doc-friendly size. These are public CDN URLs and embed via Markdown `![name](url)`.

## Roster sources for Birthdays

Include a person only if they pass their source's filter. Cross-reference all three and dedupe by name.

**1. Volunteer Entrance Survey** — `1_3a0-SWXteovcSWXbRx7snz5zVSlU95RUpcwvtWcY88`, tab `Form Responses 1`
Columns: `M` Full Name, `Q` Chapter, `S` Expected Grad Year, `U` Birthday
Filter: expected grad year has not passed (assume May graduation).

**2. Master Volunteer List** — `13lHlzVnPsiFG_sEci-T89pNM1GAlEO81s8oXBL94qlo`, tab `Sheet1`, **header on row 4, data from row 5**
Columns: `D` Full Name, `K` Chapter, `L` Cohort Year, `N` Expected Grad Year, `Q` Birthday
Filter: cohort year matches the current academic year. Confirm the year with Erin, since this column is updated manually and lags.

**3. Grad Exit Survey** — `18SouV8Sv_91-AYVt-A2zpssNB7bWnEgJklUKs4BQlos`, tab `Form Responses 1`
Columns: `I` Full Name, `O` Chapter, `R` Grad Year, `U` Birthday, `Z` "stay involved"
Filter: column `Z` contains "yes".

Entrance survey form (for the closing line): `https://docs.google.com/forms/d/e/1FAIpQLScJdM3tj149jdse8WCM1ZpHRfKGoXbpPx1gmlyttp68gAGsbg/viewform?usp=dialog`

## Reading the sheets

The Google Drive MCP connector returns "Requested entity was not found" for all three roster sheets. Fall back in this order:

1. `gws` CLI (Claude Code on Erin's Mac): `gws sheets spreadsheets values batchGet --params '{"spreadsheetId":"...","ranges":["Sheet1!D5:D400", ...]}'`
2. Any other authenticated Sheets tool available in the environment.
3. Ask Erin to export the sheet to the workspace folder.

Request only the named columns. Never read whole sheets.

## Creating and updating the Google Doc

**With the Drive MCP connector (Cowork):** `create_file` with `contentMimeType: "text/markdown"` and `parentId` set to the newsletter folder. Markdown headings, links, and images all convert. This tool cannot rewrite an existing doc's body.

**With the `gws` CLI (Claude Code):** creates and edits in place.

```
gws drive files update \
  --params '{"fileId":"<id>","uploadType":"multipart","supportsAllDrives":true}' \
  --upload newsletter.md --upload-content-type text/markdown
```

**Gotcha:** `uploadType: "media"` writes the raw multipart envelope into the doc as literal text and destroys it. Always use `multipart`.

After any write, verify before reporting:

```
gws docs documents get --params '{"documentId":"<id>"}'
```

Confirm headings exist, `inlineObjects` matches the number of photos, and no `gws_boundary` text is present.

## Converting the Doc to an HTML email

### Brand style for email

Navy `#282739` background, white body text, Public Sans with an `Arial, Helvetica, sans-serif` fallback (webfonts do not load in Outlook). Section accents rotate: salmon `#f5a17d` for Get Involved and Birthdays, green `#2fa690` for Project Updates and Kudos, yellow `#f4bf5f` for Wins and Resources. Each `<h2>` gets a 56x3px accent bar beneath it.

Email departs from the carousel spec in three ways: no gradient glow circles (radial gradients do not render in Outlook), **no accent bars under headers** (Erin ruled these out for email on 2026-09-09), and layout is 600px table-based with fully inline styles.

No horizontal rules of any kind. No full-width dividers between sections, no short bars under headings. Sections are separated by whitespace only.

### Images

Google Doc `contentUri` values expire, so never hotlink them. Also, `drive.files.export` on a Doc with photos fails with `exportSizeLimitExceeded`.

Working method:
1. Pull each `contentUri` from the Docs API response and fetch it with a plain HTTP GET. No auth needed.
2. Resize before sending. Project photos: `sips -s format jpeg -s formatOptions 72 -Z 1120`. Avatars: `-s formatOptions 80 -Z 240`. This took one issue from 11MB to 1.3MB.
3. Embed as inline CID attachments in `multipart/related`, referenced as `cid:<id>`. Never as base64 data URIs, which Gmail strips.

### Creating the draft

Build the MIME locally with Python's `EmailMessage`: `multipart/alternative` holding a plain-text fallback plus a `multipart/related` HTML part with the images attached via `add_related(..., cid="<id>")`.

```
gws gmail users drafts create \
  --params '{"userId":"me","uploadType":"multipart"}' \
  --upload draft.eml --upload-content-type message/rfc822
```

**Gotchas:**
- `uploadType: "media"` is rejected with "Media type multipart/related is not supported." Use `multipart`, same as the Drive update call.
- Never route the message through a tool argument as base64. A 1.8MB MIME becomes ~2.4MB of tokens. Always upload from a file.
- `gws auth export` returns a refresh token whose direct refresh against `oauth2.googleapis.com` returns 401. Do not build a manual curl path; use the `gws` subcommands.

Verify before reporting, with `gws gmail users drafts get --params '{"userId":"me","id":"<id>","format":"full"}'`. Confirm every `image/jpeg` part carries a `Content-ID` matching a `cid:` reference in the HTML.
