#!/usr/bin/env python3
"""
Slim a bloated meeting transcript without loading it into an LLM context.

Two modes:
  safe (default)  -- strip structural scaffolding only. Every word of speech survives.
  --aggressive    -- additionally drop echo-channel blocks that add nothing new,
                     and collapse ASR stutters.

Always prints before/after stats and a proper-noun audit. Never overwrites the input.

Usage:
  python3 slim_transcript.py INPUT.md
  python3 slim_transcript.py INPUT.md --aggressive
  python3 slim_transcript.py INPUT.md --aggressive --merge --strip-times
  python3 slim_transcript.py INPUT.md --out /path/to/output.md
"""

import argparse
import os
import re
import sys
from collections import defaultdict

# ---------------------------------------------------------------- parsing

BLOCK_RE = re.compile(r"^Source:\s*\[(?P<ch>[^\]]+)\]\s*$")
SPEAKER_RE = re.compile(r"^Speaker:\s*(?P<who>.*)$")
TIME_RE = re.compile(r"^Timestamp:\s*(?P<ts>\S+)")
RULE_RE = re.compile(r"^-{5,}\s*$")
SLIM_LINE_RE = re.compile(r"^(?P<ch>[A-Z]\*?) (?P<t>\d\d:\d\d) (?P<tx>.*)$")


def parse(path):
    """Return (preamble_lines, [ [channel, hh:mm, text], ... ], speaker_names)."""
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

            # already-slim files can be re-processed
            m = SLIM_LINE_RE.match(line)
            if m and ch is None and not line.startswith("Source:"):
                flush()
                rows.append([m.group("ch"), m.group("t"), m.group("tx")])
                ch = m.group("ch")
                continue

            m = BLOCK_RE.match(line)
            if m:
                flush()
                ch = m.group("ch")[0].upper()  # "Said" -> S, "Heard" -> H
                continue
            m = SPEAKER_RE.match(line)
            if m:
                who = m.group("who").strip()
                if who and who.lower() != "unknown":
                    speakers.add(who)
                continue
            m = TIME_RE.match(line)
            if m:
                ts = m.group("ts")
                hm = re.search(r"T(\d\d:\d\d)", ts) or re.search(r"\b(\d\d:\d\d)\b", ts)
                t = hm.group(1) if hm else t
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


# ---------------------------------------------------------------- helpers

STOP = set("the and for that with this you your not but are was were have has had".split())


def toks(s):
    return {w for w in re.findall(r"[a-z']+", s.lower()) if len(w) > 2 and w not in STOP}


def destutter(s):
    # "for for us" -> "for us"; "what what is" -> "what is"
    return re.sub(r"\b(\w+)( \1\b)+", r"\1", s, flags=re.I)


def proper_nouns(text):
    """Capitalised words that are not sentence-initial artefacts we care little about."""
    return set(re.findall(r"\b[A-Z][a-zA-Z]{2,}", text))


def near_index(rows, primary):
    by_min = defaultdict(list)
    for ch, t, tx in rows:
        if ch == primary:
            by_min[t].append(toks(tx))
    return by_min


def window(by_min, t, span=2):
    m = re.match(r"(\d\d):(\d\d)", t)
    if not m:
        return []
    hh, mm = int(m.group(1)), int(m.group(2))
    out = []
    for d in range(-span, span + 1):
        m2, h2 = mm + d, hh
        if m2 < 0:
            m2 += 60
            h2 -= 1
        if m2 > 59:
            m2 -= 60
            h2 += 1
        out += by_min.get(f"{h2:02d}:{m2:02d}", [])
    return out


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--out")
    ap.add_argument("--aggressive", action="store_true",
                    help="drop echo-channel blocks that add no unique content; de-stutter")
    ap.add_argument("--merge", action="store_true",
                    help="merge consecutive same-channel lines in the same minute "
                         "(smaller, but harder for a human to read)")
    ap.add_argument("--strip-times", action="store_true",
                    help="remove the HH:MM markers entirely")
    ap.add_argument("--span", type=int, default=2,
                    help="minutes either side to search for echoed content (default 2)")
    args = ap.parse_args()

    src = args.input
    if not os.path.exists(src):
        sys.exit(f"no such file: {src}")

    out = args.out or re.sub(r"(\.[a-z]+)$", "", src) + (
        "_slim2.md" if args.aggressive else "_slim.md")
    if os.path.abspath(out) == os.path.abspath(src):
        sys.exit("refusing to overwrite the input file")

    pre, rows, speakers = parse(src)
    if not rows:
        sys.exit("no transcript blocks recognised -- is this the expected [Said]/[Heard] format?")

    counts = defaultdict(int)
    for ch, _, _ in rows:
        counts[ch] += 1
    primary = max(counts, key=counts.get)

    kept, dropped = [], 0
    if args.aggressive and len(counts) > 1:
        by_min = near_index(rows, primary)
        for ch, t, tx in rows:
            if ch == primary:
                kept.append([ch, t, tx])
                continue
            tk = toks(tx)
            covered = set()
            for other in window(by_min, t, args.span):
                covered |= (tk & other)
            uniq = tk - covered
            # A SINGLE unique word is enough when it looks like a proper noun.
            # Rare names are exactly what must not be lost -- a >=2 threshold
            # silently drops them.
            props = {w.lower() for w in proper_nouns(tx)}
            if len(uniq) >= 2 or (uniq & props):
                kept.append([ch + "*", t, tx])
            else:
                dropped += 1
    else:
        kept = [list(r) for r in rows]

    if args.aggressive:
        for r in kept:
            r[2] = destutter(r[2])

    if args.merge:
        merged = []
        for ch, t, tx in kept:
            if merged and merged[-1][0] == ch and merged[-1][1] == t:
                merged[-1][2] += " " + tx
            else:
                merged.append([ch, t, tx])
        kept = merged

    with open(out, "w", encoding="utf-8") as fh:
        for line in pre:
            fh.write(line + "\n")
        if args.aggressive and dropped:
            fh.write(f"# {primary} = primary channel | *-suffixed = secondary channel, "
                     f"kept only where it adds unique content\n")
        for ch, t, tx in kept:
            fh.write(f"{ch} {tx}\n" if args.strip_times else f"{ch} {t} {tx}\n")

    # ------------------------------------------------------------ audit
    o_bytes, n_bytes = os.path.getsize(src), os.path.getsize(out)
    o_text = open(src, encoding="utf-8", errors="replace").read()
    n_text = open(out, encoding="utf-8", errors="replace").read()
    o_lines, n_lines = o_text.count("\n"), n_text.count("\n")

    print(f"input : {src}")
    print(f"output: {out}")
    print(f"mode  : {'AGGRESSIVE' if args.aggressive else 'safe'}"
          f"{' +merge' if args.merge else ''}{' +strip-times' if args.strip_times else ''}")
    print()
    print(f"lines: {o_lines:,} -> {n_lines:,}   ({100 - 100 * n_lines // max(1, o_lines)}% fewer)")
    print(f"bytes: {o_bytes:,} -> {n_bytes:,}   ({100 - 100 * n_bytes // max(1, o_bytes)}% smaller)")
    print(f"blocks: {len(rows):,} -> {len(kept):,}")
    if args.aggressive:
        print(f"echo blocks dropped: {dropped}")
    if not speakers:
        print("\nWARNING: every speaker label was 'Unknown' -- no attribution is available.")
        print("Do NOT assign action-item ownership from this transcript without confirming.")

    lost = sorted(proper_nouns(o_text) - proper_nouns(n_text))
    ignore = {"Source", "Speaker", "Timestamp", "Unknown", "Said", "Heard"}
    lost = [w for w in lost if w not in ignore]
    print(f"\nproper nouns in input but MISSING from output: {len(lost)}")
    if lost:
        print("  " + ", ".join(lost))
        print("  ^ review these. Most are sentence-initial common words, but a real")
        print("    name or product here means content was lost -- re-run without --aggressive.")


if __name__ == "__main__":
    main()
