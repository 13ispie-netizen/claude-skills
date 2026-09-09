# Newsletter email: brand, images, and Gmail mechanics

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
