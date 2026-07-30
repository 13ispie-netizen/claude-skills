---
name: slim-transcript
description: >
  Shrink a bloated meeting transcript before reading it, so a 46-minute call costs ~5k tokens instead of ~72k. Use whenever a raw transcript file needs to be read, quoted, or turned into notes — especially `[Said]`/`[Heard]` dual-channel exports full of `Source:` / `Speaker: Unknown` / `Timestamp:` scaffolding and divider rules. Trigger on "slim this transcript", "this transcript is huge", "clean up this transcript", "make this cheaper to read", or any time a transcript over ~500 lines is about to be opened. Also read this BEFORE reading any raw transcript, to check whether a summary already exists that makes reading it unnecessary.
---

# Slim a Transcript

Raw transcript exports are the single most expensive thing you can read. They are
also usually the wrong thing to read. Work through this in order.

---

## Step 0 — Check whether you need the transcript at all

**Do this first, every time.** List the sibling files:

```bash
ls -la "$(dirname "<transcript>")" | grep -i "$(basename "<transcript>" .md | cut -c1-20)"
```

If a `*_summary.md`, `*_summary with chapters.md`, or a Fathom/Granola summary
exists, **read that instead**. A summary is typically 2 KB against the
transcript's 108 KB — around 98% cheaper — and it has already stripped filler
and consolidated repeated points.

The transcript is worth opening only when you need an exact quote, a specific
number, or a detail the summary omitted. In that case prefer `grep` over reading:

```bash
grep -o ".\{80\}<term>.\{80\}" "<transcript>"
```

Only if you genuinely must read the body end to end, continue.

---

## Step 1 — Slim it

The bundled script does the work in the shell, so **the file never enters
context**. Cost is the summary statistics, not the content.

```bash
python3 slim_transcript.py "<transcript>"              # safe mode (default)
python3 slim_transcript.py "<transcript>" --aggressive # smaller, slightly lossy
```

It writes a new file beside the input (`_slim.md` / `_slim2.md`) and refuses to
overwrite the original.

### Safe mode — use this by default

Removes only scaffolding: `Source:` lines, `Speaker: Unknown` lines (zero
information when every value is identical), divider rules, blank padding. Full
ISO timestamps compress to `HH:MM`, which keeps the ability to cite a moment for
almost nothing. **Every word of speech survives.**

Typical result: **86% fewer lines, ~37% smaller.**

### Aggressive mode — only when you accept lossiness

Adds two transforms:

- **Echo-channel dedup.** Dual-channel exports render the same audio twice. On a
  real 46-minute call, 98.6% of `[Heard]` blocks were ≥80% covered by nearby
  `[Said]` blocks, and only 2.7% of their content words were unique. Blocks that
  add nothing are dropped; blocks that add something are kept and marked `H*`.
- **De-stutter.** ASR repeats: `for for us` → `for us`.

Typical result: **90% fewer lines, ~59% smaller.**

Optional flags:

- `--merge` — merge consecutive same-channel lines within a minute. Smaller, but
  it blends both speakers into one wall of text and is **noticeably worse to
  read**. Leave off unless you only care about token count.
- `--strip-times` — drop `HH:MM` entirely. You lose the ability to cite a moment.
- `--span N` — minutes either side to search for echoed content (default 2).

---

## Step 2 — Read the audit before trusting the output

The script prints a proper-noun diff: names present in the input but missing
from the output. **Do not skip this.**

Safe mode should report `0`. Aggressive mode reports around a dozen, and most
are sentence-initial common words (`Before`, `Otherwise`, `Sounds`). But a real
name or product in that list means content was genuinely lost — in testing,
aggressive mode dropped the name of a "**Kudos**" channel that a participant
recommended by name, keeping the idea but losing the label.

If the list contains anything substantive, re-run without `--aggressive`.

---

## Step 3 — Heed the attribution warning

If the script prints:

```
WARNING: every speaker label was 'Unknown' -- no attribution is available.
```

then the transcript cannot tell you who said what. This matters enormously:

- **Never** assign action-item ownership from an unattributed transcript.
- **Never** state that a named person said something specific.
- Ask who attended and who owns each follow-up before finalising any notes.

Attribute from the calendar invite and confirm with the user instead.

---

## Hard rules

- **Never read a raw transcript whole when a summary exists.** Check first.
- **Never overwrite the original.** The script enforces this; don't work around it.
- **Never leave clutter.** Delete intermediate slim files once notes are produced,
  or ask. Three near-duplicate transcripts in one folder is worse than one big one.
- **Report measured numbers, not estimates.** `wc -l` / `wc -c` are free. Do not
  guess at a token count and present it as fact.
- Prefer this over hand-rolling `sed`/`awk` per transcript, so the audit and the
  attribution warning always run.

---

## Why the thresholds are what they are

The echo-dedup keeps a secondary block if it contributes **≥2 unique content
words, OR ≥1 unique word that looks like a proper noun.**

That second clause exists because a `>= 2` threshold alone silently dropped
`ChatGPT` and `Katie` — each contributed exactly one unique word. Rare proper
nouns are single words by definition, which is precisely why they are worth
keeping and precisely why a naive word-count threshold discards them. Do not
"simplify" this back to a single count.
