---
name: slim-transcript
description: >
  Shrink a bloated meeting transcript before reading it, cutting a 46-minute call from ~72k tokens to ~28k. Use whenever a raw transcript file needs to be read, quoted, or turned into notes — especially `[Said]`/`[Heard]` dual-channel exports padded with `Source:` / `Speaker: Unknown` / `Timestamp:` lines and `-----` divider rules. Trigger on "slim this transcript", "this transcript is huge", "clean up this transcript", "make this cheaper to read", or any time a transcript over ~500 lines is about to be opened.
---

# Slim a Transcript

Raw transcript exports are the most expensive thing you can read. A 46-minute
call runs 2,663 lines and 108 KB, and it tokenises about 2.5x worse than normal
prose because hyphen rules and ISO timestamps split into many tokens each.

Run the bundled script first. It works in the shell, so **the transcript never
enters context** — you pay for the summary statistics, not the content.

```bash
python3 slim_transcript.py "<transcript>"
python3 slim_transcript.py "<transcript>" --out "<somewhere else>.md"
```

It writes a new file beside the input (`..._slim.md`) and refuses to overwrite
the original. Then read the slim file instead.

---

## What it does

One pass, five transforms, no options to choose between:

1. **Strips scaffolding** — `Source:` lines, `Speaker: Unknown` lines (zero
   information when every value is identical), `-----` dividers, blank padding.
   On a real file that is 39% of the bytes before a single word is touched.
2. **Compresses timestamps** — `2026-07-29T16:02:19-07:00` becomes `16:02`, which
   keeps the ability to cite a moment for almost nothing.
3. **Drops echo blocks** — dual-channel exports record the same audio twice. On a
   real call, 98.6% of secondary-channel blocks were ≥80% covered by nearby
   primary-channel blocks, and only 2.7% of their content words were unique. The
   redundant ones go; the ones that add something are kept and marked `H*`.
4. **De-stutters** — `for for us` becomes `for us`.
5. **Merges by minute** — consecutive same-channel lines in one minute join into
   one line.

Typical result: **2,663 lines → 82, and 108 KB → 43 KB (60% smaller).**

---

## Read the audit before trusting the output

Every run prints a proper-noun diff: names present in the input but missing from
the output. **Do not skip it.**

Expect around a dozen entries, most of them sentence-initial common words
(`Before`, `Otherwise`, `Sounds`). But a real name or product in that list means
content was genuinely lost. In testing, the echo-dedup dropped the name of a
"**Kudos**" channel a participant recommended by name — it kept the idea and lost
the label.

When something substantive appears in that list, grep the original for it and
restore it by hand:

```bash
grep -o ".\{80\}Kudos.\{80\}" "<original>"
```

---

## Heed the attribution warning

If the run prints:

```
WARNING: every speaker label was 'Unknown' -- no attribution is available.
```

the transcript cannot tell you who said what. This matters more than the file size:

- **Never** assign action-item ownership from an unattributed transcript.
- **Never** state that a named person said something specific.
- Take attendees from the calendar invite, and confirm who owns each follow-up
  before finalising any notes.

---

## Hard rules

- **Never overwrite the original.** The script enforces this; don't work around it.
- **Never leave clutter.** Delete the slim file once notes are produced, or ask.
  Several near-duplicate transcripts in one folder is worse than one big one.
- **Report measured numbers, not estimates.** `wc -l` and `wc -c` are free. Do not
  guess a token count and present it as fact.
- Use this rather than hand-rolling `sed`/`awk` per transcript, so the audit and
  the attribution warning always run.

---

## Why the echo threshold is what it is

A secondary block is kept if it contributes **≥2 unique content words, OR ≥1
unique word that looks like a proper noun.**

That second clause exists because a `>= 2` threshold alone silently dropped
`ChatGPT` and `Katie` — each contributed exactly one unique word. Rare proper
nouns are single words by definition, which is exactly why they are worth keeping
and exactly why a naive word count discards them. Do not collapse this back into
a single count.
