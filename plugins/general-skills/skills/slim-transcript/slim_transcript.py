#!/usr/bin/env python3
"""
Slim a bloated meeting transcript without loading it into an LLM context.

Does all of the following in one pass:
  1. strips scaffolding    -- Source: / Speaker: Unknown / Timestamp: lines, ----- dividers, blank padding
  2. compresses timestamps -- 2026-07-29T16:02:19-07:00  ->  16:02
  3. drops echo blocks     -- dual-channel exports record the same audio twice; the
                              secondary channel is kept ONLY where it adds something new
  4. de-stutters           -- "for for us" -> "for us"
  5. merges by minute      -- consecutive same-channel lines in one minute become one line

Then audits itself: reports any proper noun present in the input but missing from
the output, and warns if the transcript has no speaker attribution.

Never overwrites the input.

Usage:
  python3 slim_transcript.py INPUT.md
  python3 slim_transcript.py INPUT.md --out /path/to/output.md
"""

import argparse
import os
import re
import sys
from collections import defaultdict

BLOCK_RE = re.compile(r"^Source:\s*\[(?P<ch>[^\]]+)\]\s*$")
SPEAKER_RE = re.compile(r"^Speaker:\s*(?P<who>.*)$")
TIME_RE = re.compile(r"^Timestamp:\s*(?P<ts>\S+)")
RULE_RE = re.compile(r"^-{5,}\s*$")

STOP = set("the and for that with this you your not but are was were have has had".split())

# minutes either side to search when deciding whether a block is an echo
SPAN = 2


def parse(path):
    """Return (preamble_lines, [[channel, 'HH:MM', text], ...], speaker_names)."""
    pre, rows, speakers = [], [], set()
    ch = t = None
    buf = []

    def flush():
        nonlocal buf
        if ch is not None and buf:
            text = " ".join(s.strip() for s in buf if s.strip())
            if text:
                rows.append([ch, t or "--:--", text])
        buf = []

    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            m = BLOCK_RE.match(line)
            if m:
                flush()
                ch = m.group("ch")[0].upper()   # "Said" -> S, "Heard" -> H
                continue
            m = SPEAKER_RE.match(line)
            if m:
                who = m.group("who").strip()
                if who and who.lower() != "unknown":
                    speakers.add(who)
                continue
            m = TIME_RE.match(line)
            if m:
                hm = re.search(r"T(\d\d:\d\d)", m.group("ts")) or \
                     re.search(r"\b(\d\d:\d\d)\b", m.group("ts"))
                if hm:
                    t = hm.group(1)
                continue
            if RULE_RE.match(line):
                flush()
                continue
            if not line.strip():
                continue
            if ch is None:
                pre.append(line)
            else:
                buf.append(line)
    flush()
    return pre, rows, speakers


def toks(s):
    return {w for w in re.findall(r"[a-z']+", s.lower()) if len(w) > 2 and w not in STOP}


def proper_nouns(text):
    return set(re.findall(r"\b[A-Z][a-zA-Z]{2,}", text))


def window(by_min, t):
    m = re.match(r"(\d\d):(\d\d)", t)
    if not m:
        return []
    hh, mm = int(m.group(1)), int(m.group(2))
    out = []
    for d in range(-SPAN, SPAN + 1):
        m2, h2 = mm + d, hh
        if m2 < 0:
            m2 += 60
            h2 -= 1
        if m2 > 59:
            m2 -= 60
            h2 += 1
        out += by_min.get(f"{h2:02d}:{m2:02d}", [])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--out")
    args = ap.parse_args()

    src = args.input
    if not os.path.exists(src):
        sys.exit(f"no such file: {src}")

    out = args.out or re.sub(r"(\.[a-z]+)$", "", src) + "_slim.md"
    if os.path.abspath(out) == os.path.abspath(src):
        sys.exit("refusing to overwrite the input file")

    pre, rows, speakers = parse(src)
    if not rows:
        sys.exit("no transcript blocks recognised -- is this the expected "
                 "[Said]/[Heard] format?")

    # ---- identify the primary channel (the one with the most blocks)
    counts = defaultdict(int)
    for ch, _, _ in rows:
        counts[ch] += 1
    primary = max(counts, key=counts.get)

    # ---- drop echo blocks from the secondary channel
    kept, dropped = [], 0
    if len(counts) > 1:
        by_min = defaultdict(list)
        for ch, t, tx in rows:
            if ch == primary:
                by_min[t].append(toks(tx))

        for ch, t, tx in rows:
            if ch == primary:
                kept.append([ch, t, tx])
                continue
            tk = toks(tx)
            covered = set()
            for other in window(by_min, t):
                covered |= (tk & other)
            uniq = tk - covered
            # A SINGLE unique word is enough when it looks like a proper noun.
            # Rare names are exactly what must not be lost -- a >=2 threshold
            # silently drops them. Do not "simplify" this to one count.
            props = {w.lower() for w in proper_nouns(tx)}
            if len(uniq) >= 2 or (uniq & props):
                kept.append([ch + "*", t, tx])
            else:
                dropped += 1
    else:
        kept = [list(r) for r in rows]

    # ---- de-stutter
    for r in kept:
        r[2] = re.sub(r"\b(\w+)( \1\b)+", r"\1", r[2], flags=re.I)

    # ---- merge consecutive same-channel lines within a minute
    merged = []
    for ch, t, tx in kept:
        if merged and merged[-1][0] == ch and merged[-1][1] == t:
            merged[-1][2] += " " + tx
        else:
            merged.append([ch, t, tx])

    with open(out, "w", encoding="utf-8") as fh:
        for line in pre:
            fh.write(line + "\n")
        if dropped:
            fh.write(f"# {primary} = primary channel | *-suffixed = secondary channel, "
                     f"kept only where it adds unique content\n")
        for ch, t, tx in merged:
            fh.write(f"{ch} {t} {tx}\n")

    # ---------------------------------------------------------- audit
    o_bytes, n_bytes = os.path.getsize(src), os.path.getsize(out)
    o_text = open(src, encoding="utf-8", errors="replace").read()
    n_text = open(out, encoding="utf-8", errors="replace").read()
    o_lines, n_lines = o_text.count("\n"), n_text.count("\n")

    print(f"input : {src}")
    print(f"output: {out}")
    print()
    print(f"lines : {o_lines:,} -> {n_lines:,}   ({100 - 100 * n_lines // max(1, o_lines)}% fewer)")
    print(f"bytes : {o_bytes:,} -> {n_bytes:,}   ({100 - 100 * n_bytes // max(1, o_bytes)}% smaller)")
    print(f"blocks: {len(rows):,} -> {len(merged):,}   (echo blocks dropped: {dropped})")

    if not speakers:
        print("\nWARNING: every speaker label was 'Unknown' -- no attribution is available.")
        print("Do NOT assign action-item ownership from this transcript without confirming.")

    ignore = {"Source", "Speaker", "Timestamp", "Unknown", "Said", "Heard"}
    lost = [w for w in sorted(proper_nouns(o_text) - proper_nouns(n_text)) if w not in ignore]
    print(f"\nproper nouns in input but MISSING from output: {len(lost)}")
    if lost:
        print("  " + ", ".join(lost))
        print("  ^ REVIEW THESE. Most are sentence-initial common words, but a real")
        print("    name or product here means real content was lost. Grep the original")
        print("    for it and add it back by hand before writing anything up.")


if __name__ == "__main__":
    main()
