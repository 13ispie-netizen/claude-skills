---
name: newsletter-to-email
description: "Convert a finished A+A newsletter Google Doc into a branded HTML email saved as a Gmail draft, with photos embedded inline and no horizontal lines. Use whenever Erin says 'turn the newsletter into an email', 'make the email version', 'convert the doc to HTML', 'put it in my drafts', or asks for the email of an issue she has finished editing. Always use this skill when the input is a newsletter Google Doc and the output is an email."
---

# Newsletter Doc to branded email

Turn a finished newsletter Google Doc into an HTML email in Erin's Gmail drafts.

The Doc is the source of truth. This skill renders it. It never writes new copy, never reorders sections, and never fixes typos. If something in the Doc looks wrong, say so in chat and render it as written.

Mechanics, brand values, and the known failure modes live in `reference/email-build.md`. Load it before building.

## Required warning, every single run

Print this in chat verbatim, in bold caps, on its own line, every time this skill runs. Put it at the top of the response that delivers the draft, not buried at the end. No exceptions, no paraphrasing, no softening:

**MAKE ALL EDITS IN THE GOOGLE DOC, NOT IN GMAIL. EDITING THE DRAFT IN GMAIL DELETES THE PHOTOS.**

Why it exists: Erin lost two sends to the whole volunteer list on 2026-09-09 because editing the draft in Gmail strips every inline image attachment and replaces the references with private `mail.google.com` viewer URLs. Those render for her and are broken for every recipient, so the damage is invisible until after it ships. She has decided all copy changes happen in the Google Doc instead.

If she says she edited the draft in Gmail anyway, do not let her send it. Re-attach the photos and rebuild first.

## Before you start

**Ask whether the Doc is final.** Erin often keeps editing after publishing. Building from a half-edited Doc wastes the whole pass.

**Ask her to close the Gmail draft if one is already open.** This matters more than it sounds. See the desync warning below.

## Workflow

1. **Re-read the Doc live.** Never work from a remembered version or a local copy. Pull headings, bullets, bold runs, links, and inline image ids fresh.
2. **Pull the photos.** Google Doc image URLs expire and the Doc is usually too large for Drive's export. Fetch each `contentUri` directly, then resize. See the reference.
3. **Build the HTML** to the brand rules below.
4. **Create or update the Gmail draft** with the photos attached inline.
5. **Verify before reporting.** Re-read the draft from the server and confirm the image count, that every `cid:` reference resolves to a real attachment, and that no horizontal lines survived.
6. **Save the HTML and the resized images** into that issue's folder under `A+A Marketing HQ/Internal Newsletter/YYMMDD_internal newsletter/`.

## Brand rules for email

Navy `#282739` background, white body copy, Public Sans with an `Arial, Helvetica, sans-serif` fallback. Section accents rotate: pink `#f5a17d` for Get Involved and Birthdays, green `#2fa690` for Project Updates and Kudos, yellow `#f4bf5f` for Wins and Resources.

**No horizontal lines anywhere.** No full-width dividers between sections and no short accent bars under headings. Erin ruled both out for email on 2026-09-09. The accent bar in the carousel spec is for Instagram slides only and does not carry over. Sections are separated by whitespace.

**No gradient glow circles.** Radial gradients do not render in Outlook.

Layout is a 600px table with fully inline styles. Photos are inline CID attachments, never hotlinked and never base64 data URIs.

"Architecture + Advocacy" in the masthead is pink `#f5a17d`.

## The Gmail desync trap

Every draft update assigns a new message id. A compose window Erin already has open is still bound to the old id, so it shows stale content or renders completely blank, and saving from that window overwrites the good version.

So: ask her to close the draft before you write to it, and tell her to reopen it from the Drafts list rather than trusting an open window. If she reports the draft looks blank or unchanged, re-read it from the server before assuming anything is broken. It usually is not.

Editing in Gmail also strips inline photos and the `<style>` block. Whenever Erin has edited the draft by hand, expect to re-attach all photos and restore the stylesheet.

## Report back in chat

- The required warning above, first, in bold caps
- The draft subject and that it is in her drafts
- Confirmation that photos are attached and verified
- Any typo or content problem you noticed and deliberately left alone
- That she should close and reopen the draft to see it
