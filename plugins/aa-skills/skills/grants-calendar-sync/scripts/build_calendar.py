#!/usr/bin/env python3
"""Rebuild the Annual Calendar tab from the FUTURE LOOKING tab.

Default is a dry run: prints the placement table and writes the payload, but
changes nothing. Pass --apply to back up the tab and write.

    python3 build_calendar.py                 # preview
    python3 build_calendar.py --apply         # back up + rebuild

Reads through the Sheets API with a field mask that keeps fill colors, because
priority is expressed as a highlighted row and a values-only read loses it.
"""

import argparse, json, os, re, subprocess, sys
from datetime import date

SID = "1UrHVT6g9lloJSiagXrrFl1WYy7ttySoccbqZ3Ps79vQ"
SRC_TAB = "FUTURE LOOKING"
CAL_TAB = "Annual Calendar"
CAL_SHEET_ID = 398998318

# Calendar window. Column D holds WINDOW[0]; one column per month after that.
WINDOW = [(2026, m) for m in range(7, 13)] + [(2027, m) for m in range(1, 10)]
C0 = 3                      # column D
FIRST_WEEK = 7              # due on/before this day of month -> don't merge into it
HIGHLIGHT_MIN = 10          # tinted cells (of 25) that make a row "highlighted"

# Kept on the calendar even when not highlighted.
ALWAYS_KEEP = ["Graham Foundation - Organization Grant"]

CATEGORY_ORDER = ["LA Projects", "NY Projects", "Capacity/General",
                  "Fellowship", "Conferences", "Uncategorized"]
PALETTE = {                        # (darker, lighter) -- from Erin's original tab
    "LA Projects":      ("#FFF2CC", "#FFF8E2"),
    "NY Projects":      ("#EAD1DC", "#F4E8ED"),
    "Capacity/General": ("#D9EAD3", "#ECF6E8"),
    "Fellowship":       ("#D9D2E9", "#E4E1EC"),
    "Conferences":      ("#C9DAF8", "#E4EDFB"),
    "Uncategorized":    ("#D9D9D9", "#EFEFEF"),
}
BANNERS = [("SUMMER BREAK", (2026, 7), (2026, 8)), ("FALL SEMESTER", (2026, 9), (2026, 11)),
           ("FINALS", (2026, 12), (2026, 12)), ("Q1: Spring", (2027, 1), (2027, 3)),
           ("FINALS", (2027, 5), (2027, 5)), ("SUMMER BREAK", (2027, 6), (2027, 8)),
           ("FALL SEMESTER", (2027, 9), (2027, 9))]
MONTH_NAMES = ["", "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY",
               "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
MON3 = {n[:3].upper(): i for i, n in enumerate(MONTH_NAMES) if n}
HERE = os.path.dirname(os.path.abspath(__file__))
CATS_FILE = os.path.join(HERE, "..", "reference", "categories.json")
LABELS_FILE = os.path.join(HERE, "..", "reference", "labels.json")
SCHEMA_FILE = os.path.join(HERE, "..", "reference", "schema.json")

# set from CLI in main()
ACCEPT_SCHEMA = False
APPLY = False

BLACK = {"style": "SOLID", "colorStyle": {"rgbColor": {"red": 0, "green": 0, "blue": 0}}}


# ---------- sheets io ----------
def gws(verb, params, body=None):
    cmd = ["gws", "sheets", "spreadsheets", verb, "--params", json.dumps(params)]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    except FileNotFoundError:
        sys.exit("ERROR: the `gws` CLI is required (row fill colors and hyperlinks "
                 "cannot be read without it). Run this in Claude Code.")
    except subprocess.CalledProcessError as e:
        sys.exit(f"ERROR: gws {verb} failed: {e.stderr.strip()}")
    i = out.find("{")
    return json.loads(out[i:]) if i >= 0 else {}


def col_of(ym):
    return C0 + WINDOW.index(ym) if ym in WINDOW else None


def parse_date(s, after=None):
    """'10/05/2026', '9/30/25', 'June 6', 'Feb 25th', 'November 30, 2026' -> (y,m,d).

    Year-less values resolve to the first occurrence on/after `after`.
    'rolling' and blanks return None.
    """
    s = (s or "").strip()
    if not s or s.lower() in ("rolling", "false", "n/a", "tbd"):
        return None
    m = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})$", s)
    if m:
        mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        y += 2000 if y < 100 else 0
        return (y, mo, d)
    m = re.match(r"^([A-Za-z]{3,9})\.?\s+(\d{1,2})", s)
    if m and m.group(1)[:3].upper() in MON3:
        mo, d = MON3[m.group(1)[:3].upper()], int(m.group(2))
        yr = re.search(r"(20\d{2})", s)
        if yr:
            return (int(yr.group(1)), mo, d)
        if after:
            y = after[0] if mo >= after[1] else after[0] + 1
            return (y, mo, d)
    return None


def preflight(hdr, IX):
    """Re-read the source structure before doing anything else.

    Hard-stops when a column the calendar depends on has vanished. Otherwise
    reports any drift (added / removed / moved / renamed headers) against the
    last-accepted snapshot in reference/schema.json, so a silent restructure
    can never quietly produce a wrong calendar.
    """
    missing = [k for k, v in IX.items() if v is None]
    if missing:
        sys.exit(
            f"STRUCTURE CHANGED -- cannot continue.\n"
            f"These fields no longer resolve to a column in '{SRC_TAB}': {missing}\n"
            f"Current headers: {hdr}\n"
            f"Fix the header text in the sheet, or update the `find(...)` terms in this script.")

    old = {}
    if os.path.exists(SCHEMA_FILE):
        old = json.load(open(SCHEMA_FILE))
    prev = old.get("headers")
    if prev is None:
        print(f"schema: no baseline recorded; snapshotting {len(hdr)} columns")
        _write_schema(hdr, IX)
        return

    if prev == hdr:
        print(f"schema: unchanged ({len(hdr)} columns)")
        return

    prev_ix = {h: i for i, h in enumerate(prev) if h}
    cur_ix = {h: i for i, h in enumerate(hdr) if h}
    added = [h for h in cur_ix if h not in prev_ix]
    removed = [h for h in prev_ix if h not in cur_ix]
    moved = [(h, prev_ix[h], cur_ix[h]) for h in cur_ix
             if h in prev_ix and prev_ix[h] != cur_ix[h]]

    def L(i):
        return chr(65 + i) if i < 26 else "A" + chr(65 + i - 26)
    print("\n*** COLUMN STRUCTURE CHANGED in FUTURE LOOKING ***")
    for h in removed:
        print(f"    removed : {L(prev_ix[h])}  {h!r}")
    for h in added:
        print(f"    added   : {L(cur_ix[h])}  {h!r}")
    for h, a, b in moved:
        print(f"    moved   : {L(a)} -> {L(b)}  {h!r}")
    print("    all fields the calendar needs still resolve, so placement is safe.")

    if APPLY and not ACCEPT_SCHEMA:
        sys.exit("\nRefusing to --apply over an unreviewed structure change.\n"
                 "Show Erin the diff above. Re-run with --accept-schema once she confirms.")
    if ACCEPT_SCHEMA:
        _write_schema(hdr, IX)
        print("    baseline updated.")
    else:
        print("    (dry run -- baseline not updated)")


def _write_schema(hdr, IX):
    json.dump({"headers": hdr, "resolved": IX, "recorded": date.today().isoformat()},
              open(SCHEMA_FILE, "w"), indent=2)


def read_source():
    d = gws("get", {"spreadsheetId": SID, "ranges": [f"{SRC_TAB}!A1:Z400"],
                    "fields": "sheets.data.rowData.values(formattedValue,"
                              "effectiveFormat.backgroundColorStyle.rgbColor)"})
    grid = d["sheets"][0]["data"][0].get("rowData", [])
    hdr = [(v.get("formattedValue") or "").strip() for v in grid[0].get("values", [])]

    # Map by header text, never by fixed index -- these columns have moved before.
    def find(*prefixes):
        for i, h in enumerate(hdr):
            hl = h.lower()
            if all(p.lower() in hl for p in prefixes):
                return i
        return None
    IX = {"due": find("due/date"), "revisit": find("revisit"),
          "name": find("grant name"), "org": find("organization", "link their"),
          "amount": find("amount"), "r2s": find("second round start"),
          "r2d": find("second round due")}
    preflight(hdr, IX)

    def fv(v, i):
        return ((v[i].get("formattedValue") if i is not None and i < len(v) else None) or "").strip()

    def tinted(v, i):
        if i >= len(v):
            return False
        c = v[i].get("effectiveFormat", {}).get("backgroundColorStyle", {}).get("rgbColor", {})
        return bool(c) and tuple(round(c.get(k, 0), 3) for k in ("red", "green", "blue")) != (1., 1., 1.)

    rows = []
    for n, r in enumerate(grid[1:], start=2):
        v = r.get("values", [])
        if not any(x.get("formattedValue") for x in v):
            continue
        rows.append({"row": n,
                     "hl": sum(1 for i in range(25) if tinted(v, i)) >= HIGHLIGHT_MIN,
                     **{k: fv(v, i) for k, i in IX.items()}})
    return rows, IX


# ---------- planning ----------
_LABELS = json.load(open(LABELS_FILE)) if os.path.exists(LABELS_FILE) else {}


def label_of(g):
    """Display name. labels.json overrides rows whose Grant Name cell is blank
    or holds junk (e.g. an amount landed in the Organization column)."""
    raw = g["name"] or g["org"] or f"(row {g['row']})"
    return _LABELS.get(raw, raw)


def span_for(start, due):
    """-> (start_col, end_col, reminder?) applying Erin's rules."""
    cs = col_of((start[0], start[1]))
    if cs is None:
        return None, None, False
    ce = cs
    reminder = due is None
    if due and (due[0], due[1], due[2]) > (start[0], start[1], start[2]):
        if due[2] <= FIRST_WEEK:                      # first-week due: stop before that month
            prev = (due[0], due[1] - 1) if due[1] > 1 else (due[0] - 1, 12)
            c = col_of(prev)
        else:
            c = col_of((due[0], due[1]))
        if c is not None and c > cs:
            ce = c
    return cs, ce, reminder


def build():
    src, _ = read_source()
    cats = json.load(open(CATS_FILE)) if os.path.exists(CATS_FILE) else {}
    keep = [g for g in src if g["hl"] or any(k.lower() in label_of(g).lower() for k in ALWAYS_KEEP)]

    planned, outside, unknown = [], [], []
    for g in keep:
        rv = parse_date(g["revisit"])
        if not rv:
            outside.append((label_of(g), f"unparseable revisit {g['revisit']!r}"))
            continue
        if col_of((rv[0], rv[1])) is None:
            outside.append((label_of(g), f"revisit {g['revisit']} outside window"))
            continue
        du = parse_date(g["due"], rv)
        cs, ce, rem = span_for(rv, du)
        stale = bool(du and (du[0], du[1], du[2]) <= (rv[0], rv[1], rv[2]))
        cat = cats.get(label_of(g))
        if not cat:
            cat = "Uncategorized"
            unknown.append(label_of(g))
        # second round
        r2 = None
        r2s = parse_date(g["r2s"])
        if r2s and col_of((r2s[0], r2s[1])) is not None:
            r2d = parse_date(g["r2d"], r2s)
            a, b, r2rem = span_for(r2s, r2d)
            r2 = (a, b, r2rem)
        planned.append({"g": g, "cat": cat, "label": label_of(g), "cs": cs, "ce": ce,
                        "reminder": rem, "stale": stale, "r2": r2,
                        "amount": g["amount"].strip()})

    planned.sort(key=lambda p: (CATEGORY_ORDER.index(p["cat"]) if p["cat"] in CATEGORY_ORDER
                                else len(CATEGORY_ORDER), p["cs"]))
    return planned, outside, unknown


# ---------- rendering ----------
def rgb(h):
    h = h.lstrip("#")
    return {k: int(h[i:i + 2], 16) / 255 for k, i in (("red", 0), ("green", 2), ("blue", 4))}


def txt(s):
    return {"userEnteredValue": {"stringValue": s}} if s else {}


def rng(r0, r1, c0, c1):
    return {"sheetId": CAL_SHEET_ID, "startRowIndex": r0, "endRowIndex": r1,
            "startColumnIndex": c0, "endColumnIndex": c1}


def render(planned):
    reqs, report = [], []
    last = C0 + len(WINDOW)
    # wipe the grid area (values, fills, bold, borders, merges)
    reqs.append({"unmergeCells": {"range": rng(2, 60, 0, 31)}})
    reqs.append({"repeatCell": {"range": rng(2, 60, 0, 31),
                 "cell": {"userEnteredFormat": {
                     "backgroundColorStyle": {"rgbColor": rgb("#FFFFFF")},
                     "textFormat": {"bold": False}}},
                 "fields": "userEnteredValue,userEnteredFormat.backgroundColorStyle,"
                           "userEnteredFormat.textFormat.bold"}})
    reqs.append({"updateBorders": {"range": rng(2, 60, 0, 31), **{k: {"style": "NONE"}
                 for k in ("top", "bottom", "left", "right",
                           "innerHorizontal", "innerVertical")}}})
    # header + banners
    reqs.append({"updateCells": {"start": {"sheetId": CAL_SHEET_ID, "rowIndex": 0, "columnIndex": C0},
                 "rows": [{"values": [txt(f"{MONTH_NAMES[m]} {y}") for y, m in WINDOW]}],
                 "fields": "userEnteredValue"}})
    brow = [{} for _ in WINDOW]
    for lab, s, e in BANNERS:
        cs, ce = col_of(s), col_of(e)
        if cs is None or ce is None:
            continue
        brow[cs - C0] = txt(lab)
        if ce > cs:
            reqs.append({"mergeCells": {"range": rng(1, 2, cs, ce + 1), "mergeType": "MERGE_ALL"}})
    reqs.append({"updateCells": {"start": {"sheetId": CAL_SHEET_ID, "rowIndex": 1, "columnIndex": C0},
                 "rows": [{"values": brow}], "fields": "userEnteredValue"}})

    row, cat, idx = 3, None, 0
    borders = []
    for p in planned:
        if p["cat"] != cat:
            cat, idx = p["cat"], 0
        text = p["label"]
        if p["amount"]:
            text += f"\n({p['amount']})"
        if p["reminder"]:
            text += "\ncheck back reminder"
        vals = [txt(cat if idx == 0 else ""), {}, {}] + [{} for _ in WINDOW]
        vals[3 + (p["cs"] - C0)] = txt(text)
        borders.append((row, p["cs"], p["ce"]))
        if p["ce"] > p["cs"]:
            reqs.append({"mergeCells": {"range": rng(row - 1, row, p["cs"], p["ce"] + 1),
                                        "mergeType": "MERGE_ALL"}})
        if p["r2"]:
            a, b, rem2 = p["r2"]
            t2 = p["label"] + " (2nd Round)" + ("\ncheck back reminder" if rem2 else "")
            vals[3 + (a - C0)] = txt(t2)
            borders.append((row, a, b))
            if b > a:
                reqs.append({"mergeCells": {"range": rng(row - 1, row, a, b + 1),
                                            "mergeType": "MERGE_ALL"}})
        reqs.append({"updateCells": {"start": {"sheetId": CAL_SHEET_ID, "rowIndex": row - 1,
                                               "columnIndex": 0},
                     "rows": [{"values": vals}], "fields": "userEnteredValue"}})
        shade = PALETTE.get(cat, PALETTE["Uncategorized"])[idx % 2]
        reqs.append({"repeatCell": {"range": rng(row - 1, row, 0, last),
                     "cell": {"userEnteredFormat": {
                         "backgroundColorStyle": {"rgbColor": rgb(shade)},
                         "textFormat": {"bold": False}}},
                     "fields": "userEnteredFormat.backgroundColorStyle,"
                               "userEnteredFormat.textFormat.bold"}})
        if idx == 0:
            reqs.append({"repeatCell": {"range": rng(row - 1, row, 0, 1),
                         "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                         "fields": "userEnteredFormat.textFormat.bold"}})
        report.append((row, cat if idx == 0 else "", p["label"], p["cs"], p["ce"], p["r2"],
                       p["reminder"], p["stale"]))
        idx += 1
        row += 1

    # borders last, so nothing clears a shared edge afterwards
    for r, a, b in borders:
        reqs.append({"updateBorders": {"range": rng(r - 1, r, a, b + 1),
                                       "top": BLACK, "bottom": BLACK,
                                       "left": BLACK, "right": BLACK}})
    return reqs, report, row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--payload", default="calendar_payload.json")
    ap.add_argument("--accept-schema", action="store_true",
                    help="acknowledge a reported column-structure change and update the baseline")
    a = ap.parse_args()
    global ACCEPT_SCHEMA, APPLY
    ACCEPT_SCHEMA, APPLY = a.accept_schema, a.apply

    planned, outside, unknown = build()
    reqs, report, endrow = render(planned)
    json.dump({"requests": reqs}, open(a.payload, "w"))

    def L(i):
        return chr(65 + i)
    print(f"grants: {len(planned)}   requests: {len(reqs)}\n")
    print(f"{'row':>4} {'category':17} {'grant':42} {'1st':7} {'2nd':7} flags")
    for r, c, lab, cs, ce, r2, rem, stale in report:
        s1 = L(cs) + ("" if ce == cs else f":{L(ce)}")
        s2 = "" if not r2 else L(r2[0]) + ("" if r2[1] == r2[0] else f":{L(r2[1])}")
        fl = ",".join(f for f, on in (("reminder", rem), ("stale-due", stale)) if on)
        print(f"{r:>4} {c[:17]:17} {lab[:42]:42} {s1:7} {s2:7} {fl}")
    if unknown:
        print("\nNEEDS A CATEGORY (parked in 'Uncategorized' -- add to reference/categories.json):")
        for u in unknown:
            print("   ", u)
    if outside:
        print("\nNOT PLACED:")
        for lab, why in outside:
            print(f"    {lab} -- {why}")

    if not a.apply:
        print(f"\nDry run. Payload written to {a.payload}. Re-run with --apply to write.")
        return
    stamp = date.today().strftime("%y%m%d")
    gws("batchUpdate", {"spreadsheetId": SID},
        {"requests": [{"duplicateSheet": {"sourceSheetId": CAL_SHEET_ID,
                                          "newSheetName": f"{CAL_TAB} (pre-sync {stamp})"}}]})
    print(f"backed up to '{CAL_TAB} (pre-sync {stamp})'")
    gws("batchUpdate", {"spreadsheetId": SID}, {"requests": reqs})
    print("calendar rebuilt")


if __name__ == "__main__":
    main()
