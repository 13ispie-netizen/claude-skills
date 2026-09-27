"""Copy the master onboarding checklist into the employee folder and cut the other state's items.

Usage: checklist.py --folder ID --name "Last, First" --state CA|NY [--doc EXISTING_DOC_ID]

Pass --doc if the employee already has a checklist copy; otherwise the master is copied.
Prints JSON with the doc id and every line removed, so Claude can report it.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import gws  # noqa: E402

MASTER = "1YdnWPbwk8JLwS1d4S17qjGCIKma0DpUBRLa5eBaJ9DI"  # "Employee On-Boarding Checklist [dupliacte me!]"

# (pattern, remove nested children too?)
REMOVE = {
    "CA": [  # CA employee: drop NY items
        (r"\bNY version\b", True),
        (r"\(NY\)", True),
        (r"^Different for NY\b", True),
        (r"^NY:", True),
        (r"^If NY employee\b", True),
        (r"^NY$", True),
    ],
    "NY": [  # NY employee: drop CA items
        (r"^CA Employee.s Withholding", False),
        (r"\bDE 34\b", False),
        (r"Calsavers", True),
        (r"^CA$", True),
        (r"^CA \(double-check", True),
        (r"^Notice to Employee$", True),
    ],
}


def paragraphs(doc_id):
    d = gws(["docs", "documents", "get"], params={"documentId": doc_id})
    out = []
    for el in d["body"]["content"]:
        p = el.get("paragraph")
        if not p:
            continue
        text = "".join(r.get("textRun", {}).get("content", "") for r in p["elements"]).strip()
        level = p["bullet"].get("nestingLevel", 0) if "bullet" in p else -1
        out.append((el["startIndex"], el["endIndex"], level, text))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--state", required=True, choices=["CA", "NY"])
    ap.add_argument("--doc")
    ap.add_argument("--dry-run", action="store_true", help="list what would be removed; change nothing")
    a = ap.parse_args()

    doc_id = a.doc or gws(["drive", "files", "copy"],
                          params={"fileId": MASTER, "supportsAllDrives": True},
                          body={"name": f"Employee On-Boarding Checklist_{a.name}", "parents": [a.folder]})["id"]

    paras = paragraphs(doc_id)
    ranges, removed, i = [], [], 0
    while i < len(paras):
        start, end, level, text = paras[i]
        rule = next((kids for pat, kids in REMOVE[a.state] if re.search(pat, text)), None)
        if rule is None:
            i += 1
            continue
        removed.append(text)
        j = i + 1
        if rule and level >= 0:
            while j < len(paras) and paras[j][2] > level:
                removed.append(paras[j][3])
                end = paras[j][1]
                j += 1
        ranges.append((start, end))
        i = j

    if ranges and not a.dry_run:
        reqs = [{"deleteContentRange": {"range": {"startIndex": s, "endIndex": e}}}
                for s, e in sorted(ranges, reverse=True)]
        gws(["docs", "documents", "batchUpdate"], params={"documentId": doc_id}, body={"requests": reqs})
    print(json.dumps({"doc_id": doc_id, "url": f"https://docs.google.com/document/d/{doc_id}/edit",
                      "removed": removed}, indent=1))


if __name__ == "__main__":
    main()
