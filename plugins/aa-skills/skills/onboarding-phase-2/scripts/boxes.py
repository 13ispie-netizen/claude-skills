"""Typed checkboxes for the onboarding checklist (Google's Docs API can't tick native ones).

Usage:
  boxes.py convert --doc ID              turn native checkbox bullets into "☐ " text (indent kept)
  boxes.py tick --doc ID --item TEXT ... change "☐" to "☑" on each line that starts with TEXT

Prints JSON: converted count, or ticked lines plus any items not found.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import gws  # noqa: E402

OPEN, DONE = "☐", "☑"


def get(doc_id):
    return gws(["docs", "documents", "get"], params={"documentId": doc_id})


def paras(d):
    for el in d["body"]["content"]:
        if "paragraph" in el:
            p = el["paragraph"]
            text = "".join(r.get("textRun", {}).get("content", "") for r in p["elements"])
            yield el["startIndex"], el["endIndex"], p, text


def is_checkbox(d, p):
    b = p.get("bullet")
    if not b:
        return False
    lvl = d["lists"][b["listId"]]["listProperties"]["nestingLevels"][b.get("nestingLevel", 0)]
    return lvl.get("glyphType", "GLYPH_TYPE_UNSPECIFIED") == "GLYPH_TYPE_UNSPECIFIED" and not lvl.get("glyphSymbol")


def indent(d, p):
    """Where the bullet's text starts: the paragraph's own indent, else its list level's."""
    own = p.get("paragraphStyle", {}).get("indentStart", {}).get("magnitude")
    if own is not None or "bullet" not in p:
        return own or 0
    b = p["bullet"]
    lvl = d["lists"][b["listId"]]["listProperties"]["nestingLevels"][b.get("nestingLevel", 0)]
    return lvl.get("indentStart", {}).get("magnitude", 0)


def batch(doc_id, reqs):
    if reqs:
        gws(["docs", "documents", "batchUpdate"], params={"documentId": doc_id}, body={"requests": reqs})


def convert(doc_id):
    d = get(doc_id)
    targets = [(s, e, indent(d, p)) for s, e, p, t in paras(d) if is_checkbox(d, p) and t.strip()]
    # Drop the bullet but keep the line exactly where it sat (indices don't move).
    reqs = []
    for s, e, ind in targets:
        rng = {"startIndex": s, "endIndex": e}
        reqs += [{"deleteParagraphBullets": {"range": rng}},
                 {"updateParagraphStyle": {"range": rng, "fields": "indentStart,indentFirstLine",
                                           "paragraphStyle": {"indentStart": {"magnitude": ind, "unit": "PT"},
                                                              "indentFirstLine": {"magnitude": ind, "unit": "PT"}}}}]
    reqs += [{"insertText": {"location": {"index": s}, "text": OPEN + " "}}
             for s, _, _ in sorted(targets, reverse=True)]
    batch(doc_id, reqs)
    return {"converted": len(targets)}


def tick(doc_id, items):
    d = get(doc_id)
    starts, ticked, found = [], [], set()
    for s, _, _, t in paras(d):
        if not t.startswith(OPEN):
            continue
        body = t[1:].strip().lower()
        hit = next((i for i in items if body.startswith(i.strip().lower())), None)
        if hit:
            found.add(hit)
            ticked.append(t[1:].strip())
            starts.append(s)
    reqs = []
    for s in sorted(starts, reverse=True):
        reqs += [{"deleteContentRange": {"range": {"startIndex": s, "endIndex": s + 1}}},
                 {"insertText": {"location": {"index": s}, "text": DONE}}]
    batch(doc_id, reqs)
    return {"ticked": ticked, "not_found": [i for i in items if i not in found]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["convert", "tick"])
    ap.add_argument("--doc", required=True)
    ap.add_argument("--item", action="append", default=[])
    a = ap.parse_args()
    out = convert(a.doc) if a.action == "convert" else tick(a.doc, a.item)
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
