#!/usr/bin/env python3
"""Diff the sheet against Notion and emit a write plan.

Three-way compare per field:
    snapshot = value at last sync
    sheet    = value now in the Google Sheet
    notion   = value now in Notion

    sheet == snapshot                  -> nothing to do
    sheet != snapshot, notion == snap  -> clean update
    sheet != snapshot, notion != snap  -> CONFLICT, report and leave Notion alone

Priority is additive only. Work Month / Work Window are never written from the sheet.
"""

import argparse
import json
import os
import re
import unicodedata
from datetime import datetime

# Verbatim Notion property names. The space runs are real -- do not retype.
P_TITLE = "Grant Name                              (Link Website)"
P_ORG_URL = "Organization                (Link their website)"
P_ORG_NAME = "Organization Name"
P_APP_URL = "Application URL"
P_PRIORITY = "Prioirity"
P_WORK_MONTH = "Work Month"

# col index -> (notion property, kind)
FIELDS = {
    0:  ("DUE/Date", "date"),
    1:  ("Application Type", "select"),
    2:  ("Revisit", "date"),
    3:  ("Notificaiton Date (est.)", "text"),
    5:  ("Use", "select"),
    7:  ("Amount (Range)", "text"),
    8:  ("Matching", "select"),
    9:  ("Google Drive Folder", "url"),
    10: ("Quick Description", "text"),
    11: ("Grant Start Date", "date"),
    12: ("Grant end date", "date"),
    13: ("Report due", "date"),
    14: ("Reporting Required", "text"),
    15: ("Similar Groups Funded", "text"),
    16: ("Contact Person", "email"),
    17: ("Contacted?", "text"),
    18: ("A+A Point Person (responsible for submitting)", "text"),
    19: ("Preliminary Proposal Due", "date"),
    20: ("Second Round Due", "date"),
    21: ("Award Notification Date", "text"),
    22: ("Important Reporting Dates", "select"),
    23: ("Prioirty (1-5)", "text"),
    24: ("Funds Recieved?", "select"),
}

NEVER_WRITE = {P_PRIORITY, P_WORK_MONTH, "Work Window"}

JUNK_ORG = re.compile(r"^\$|^[\d,.\s\-$]+$")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DATE_FORMATS = ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d", "%m-%d-%Y", "%b %d, %Y")


def norm(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", str(s)).replace("’", "'")
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def to_iso(v):
    if not v:
        return None
    v = str(v).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(v, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def esc(t):
    return str(t).replace("[", "\\[").replace("]", "\\]")


def clean(v):
    """Normalize a value for comparison: None and '' are the same thing."""
    return (v or "").strip()


def sheet_values(row):
    """Derive the full set of Notion-bound values for one sheet row."""
    cells = row["cells"]
    out, notes = {}, []

    name = clean(cells[4])
    org = clean(cells[6])
    org_is_url = org.startswith("http")
    org_is_junk = bool(org) and bool(JUNK_ORG.match(org))

    if org_is_junk:
        notes.append(f"row {row['sheet_row']}: org cell looks like an amount ({org!r}); skipped")

    # Title falls back to the org name when the grant name is blank.
    out[P_TITLE] = name or ("" if (org_is_url or org_is_junk) else org)

    if row.get("name_link"):
        out[P_APP_URL] = row["name_link"]
    if row.get("org_link"):
        out[P_ORG_URL] = row["org_link"]

    if org and not org_is_url and not org_is_junk:
        out[P_ORG_NAME] = f"[{esc(org)}]({row['org_link']})" if row.get("org_link") else org
    elif org_is_url:
        notes.append(
            f"row {row['sheet_row']}: org cell is a bare URL, no name to carry over; "
            "derive from the domain or report"
        )

    for idx, (prop, kind) in FIELDS.items():
        raw = clean(cells[idx]) if idx < len(cells) else ""
        if not raw:
            continue
        if kind == "date":
            iso = to_iso(raw)
            if iso:
                out[prop] = iso
            else:
                notes.append(f"row {row['sheet_row']}: {prop} = {raw!r} is not a date; skipped")
        elif kind == "email":
            if EMAIL.match(raw):
                out[prop] = raw
            else:
                notes.append(f"row {row['sheet_row']}: {prop} = {raw!r} is not an email; skipped")
        else:
            out[prop] = raw

    return out, notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True)
    ap.add_argument("--notion", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    sheet = json.load(open(args.sheet))["rows"]
    notion = json.load(open(args.notion))
    state = json.load(open(args.state)) if os.path.exists(args.state) else {"rows": {}}
    snapshots = state.get("rows", {})

    # Match key: normalized grant name + normalized org name.
    # Row order and createdTime are useless -- the original import scrambled both.
    def key_of(name, org):
        o = org or ""
        if o.startswith("https://"):
            o = o[8:]
        elif o.startswith("http://"):
            o = o[7:]
        return f"{norm(name)}|{norm(o)}"

    by_key, dupes = {}, []
    for r in notion:
        k = key_of(r.get("name"), r.get("org_name") or r.get("org_url"))
        if k in by_key:
            dupes.append(k)
        by_key.setdefault(k, r)

    updates, creates, conflicts, prio, notes = [], [], [], [], []
    matched_ids = set()

    for row in sheet:
        vals, n = sheet_values(row)
        notes.extend(n)
        k = key_of(vals.get(P_TITLE), vals.get(P_ORG_NAME) or vals.get(P_ORG_URL))
        target = by_key.get(k)

        if not target:
            creates.append({"sheet_row": row["sheet_row"], "props": vals,
                            "highlighted": row["highlighted"]})
            continue

        pid = target["id"]
        matched_ids.add(pid)
        snap = snapshots.get(pid, {}).get("fields", {})
        changed = {}

        for prop, new in vals.items():
            if prop in NEVER_WRITE:
                continue
            old_snap = clean(snap.get(prop))
            cur = clean(target.get("props", {}).get(prop))
            new = clean(new)
            if new == old_snap:
                continue  # sheet didn't change this field
            if cur != old_snap and cur != new:
                conflicts.append({
                    "id": pid, "title": vals.get(P_TITLE), "prop": prop,
                    "sheet": new, "notion": cur, "last_sync": old_snap,
                })
                continue
            if cur != new:
                changed[prop] = new

        if changed:
            updates.append({"id": pid, "title": vals.get(P_TITLE), "props": changed})

        # Priority: additive only, never unticked.
        if row["highlighted"] and clean(target.get("props", {}).get(P_PRIORITY)) != "__YES__":
            prio.append({"id": pid, "title": vals.get(P_TITLE)})

    archives = [
        {"id": pid, "title": s.get("fields", {}).get(P_TITLE, "(untitled)")}
        for pid, s in snapshots.items()
        if pid not in matched_ids
    ]

    plan = {"updates": updates, "creates": creates, "conflicts": conflicts,
            "priority": prio, "archives": archives, "notes": notes,
            "duplicate_keys": dupes}
    with open(args.out, "w") as f:
        json.dump(plan, f, indent=1)

    print(f"updates      : {len(updates)}")
    print(f"new grants   : {len(creates)}")
    print(f"priority tick: {len(prio)}")
    print(f"conflicts    : {len(conflicts)}   (reported, not written)")
    print(f"to archive   : {len(archives)}")
    if dupes:
        print(f"WARNING: {len(dupes)} duplicate match key(s); first match used")
    for x in notes[:15]:
        print("  note:", x)
    if len(notes) > 15:
        print(f"  ... and {len(notes) - 15} more notes in the plan file")


if __name__ == "__main__":
    main()
