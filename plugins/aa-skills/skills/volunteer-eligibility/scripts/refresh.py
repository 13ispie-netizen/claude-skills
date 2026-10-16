#!/usr/bin/env python3
"""Refresh A+A's volunteer paperwork tracker from Drive uploads + form responses.

Dry run (default): reads everything, prints the plan, downloads unsorted images
for Claude to look at. Writes nothing.
  python3 refresh.py [--out DIR]

Apply: writes the plan, plus any extra boxes Claude found in images, then logs
the run on the Refresh Log tab.
  python3 refresh.py --apply [--extra "Full Name=dues" ...]

Rules: boxes only ever go from unchecked to checked; N/A cells are never touched;
columns are found by header text, so Erin can reorder or rename them freely.
"""
import argparse, datetime, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.environ.get("VE_CONFIG") or os.path.join(HERE, "..", "reference", "config.json")))

# requirement key -> header keyword (lowercase substring of the tracker header)
COLS = {
    "waiver": "volunteer waiver", "coc": "code of conduct", "survey": "entrance survey",
    "st_waiver": "strategy team waiver", "mrt": "mandated reporter", "dues": "dues",
    "vehicle": "vehicle use", "tool": "tool use", "woodshop": "woodshop",
    "drive": "cleared to drive", "scholarship": "scholarship", "returning": "returning volunteer",
}
# requirement key -> filename keywords
FILE_RULES = [
    ("st_waiver", ["strategy team waiver"]),
    ("waiver", ["volunteer waiver"]),
    ("coc", ["code of conduct"]),
    ("mrt", ["mandated", "certificate", "praesidium"]),
    ("vehicle", ["vehicle"]),
    ("tool", ["tool use"]),
    ("woodshop", ["woodshop", "sticker"]),
    ("survey", ["survey"]),
    ("dues", ["dues", "paypal", "venmo", "zelle", "payment", "t-shirt", "tshirt", "membership", "transaction", "receipt"]),
]
IGNORE = ["scholarship", "waived", "delete"]
IMAGE_KEYS = ("dues", "survey", "vehicle", "woodshop")  # what a generic image could prove


def gws(*args, cwd=None):
    r = subprocess.run(["gws", *args], capture_output=True, text=True, cwd=cwd)
    if r.returncode:
        sys.exit(f"gws failed: {' '.join(args[:3])}\n{r.stdout[-600:]}{r.stderr[-300:]}")
    return json.loads(r.stdout) if r.stdout.strip().startswith("{") else {}


def values(sid, rng, render="FORMATTED_VALUE"):
    return gws("sheets", "spreadsheets", "values", "get", "--params",
               json.dumps({"spreadsheetId": sid, "range": rng, "valueRenderOption": render})).get("values", [])


def ls(fid):
    out, tok = [], None
    while True:
        p = {"q": f"'{fid}' in parents and trashed=false", "pageSize": 1000,
             "fields": "nextPageToken,files(id,name,mimeType,webViewLink)",
             "supportsAllDrives": True, "includeItemsFromAllDrives": True}
        if tok: p["pageToken"] = tok
        d = gws("drive", "files", "list", "--params", json.dumps(p))
        out += d.get("files", []); tok = d.get("nextPageToken")
        if not tok: return out


def folders(fid):
    """{person folder name: [files]} -- files nested deeper are flattened into the person."""
    res = {}
    def walk(f_id, top):
        for f in ls(f_id):
            if f["mimeType"].endswith(".folder"): walk(f["id"], top)
            else: res.setdefault(top, []).append(f)
    for f in ls(fid):
        if f["mimeType"].endswith(".folder"): res.setdefault(f["name"], []); walk(f["id"], f["name"])
    return res


norm = lambda s: " ".join(re.sub(r"[^a-z\- ]", " ", s.lower()).split())
folder_person = lambda k: norm(re.sub(r"^\s*(FA|SP|SU)\d+\s*", "", k))


def same_person(name, folder):
    a, b = set(norm(name).split()), set(folder_person(folder).split())
    return bool(b) and (len(a & b) >= 2 or (len(b) >= 2 and b <= a))


def classify(fname):
    n = fname.lower()
    if any(k in n for k in IGNORE): return "ignore"
    for key, kws in FILE_RULES:
        if any(k in n for k in kws): return key
    return None


def col_letter(i):
    s = ""
    i += 1
    while i: i, r = divmod(i - 1, 26); s = chr(65 + r) + s
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--extra", nargs="*", default=[], help='"Full Name=key" from image review')
    ap.add_argument("--out", default=os.path.join(__import__("tempfile").gettempdir(), "volunteer-eligibility-images"))
    a = ap.parse_args()
    today = datetime.date.today().isoformat()

    meta = gws("sheets", "spreadsheets", "get", "--params", json.dumps(
        {"spreadsheetId": CFG["tracker_id"], "fields": "sheets.properties(sheetId,title),sheets.conditionalFormats"}))
    tab = meta["sheets"][0]["properties"]; T = tab["title"]
    allrows = values(CFG["tracker_id"], f"'{T}'!A1:AZ1000")
    H = next(n for n, r in enumerate(allrows[:10]) if r and "name" in r[0].lower())  # header row (0-based); rows above it are notes
    rows = allrows[H:]
    hdr = [h.lower() for h in rows[0]]
    col = {}
    for k, kw in COLS.items():
        hit = [i for i, h in enumerate(hdr) if kw in h]
        if hit: col[k] = hit[0]
    missing_cols = [k for k in COLS if k not in col]
    people = [(i, (r + [""] * len(hdr))) for i, r in enumerate(rows[1:], H + 2) if r and r[0].strip()]
    cell = lambda r, k: r[col[k]] if k in col else ""

    # last refresh date (for the Zelle reminder)
    log_tabs = [s["properties"]["title"] for s in meta["sheets"]]
    last, reviewed = None, set()
    if CFG["log_tab"] in log_tabs:
        lg = values(CFG["tracker_id"], f"'{CFG['log_tab']}'!A2:E1000")
        last = lg[-1][0] if lg else None
        reviewed = {x.strip() for r in lg if len(r) > 4 for x in r[4].split(",") if x.strip()}

    cur, prev = folders(CFG["uploads_folder_id"]), folders(CFG["last_semester_folder_id"])
    survey = values(CFG["survey_sheet_id"], "A1:AZ1000")
    sh = [h.lower() for h in survey[0]]
    s_email = [i for i, h in enumerate(sh) if "email" in h]
    s_name = [i for i, h in enumerate(sh) if "name" in h]
    s_keys = set()
    for r in survey[1:]:
        r = r + [""] * len(sh)
        s_keys |= {r[i].strip().lower() for i in s_email if r[i].strip()}
        s_keys |= {norm(r[i]) for i in s_name if r[i].strip()}
        s_keys |= {norm(" ".join(r[i] for i in s_name + s_email[:1]))}  # first + last typed in the wrong boxes
    veh = values(CFG["vehicle_sheet_id"], "A1:AZ1000")
    vh = [h.lower() for h in veh[0]]
    v_name = [i for i, h in enumerate(vh) if "name" in h or "signature" in h or "typing my name" in h]
    cleared = {norm(r[i]) for r in veh[1:] if r and r[0] == "TRUE" for i in v_name if i < len(r) and r[i].strip()}

    plan, images, unknown, matched = {}, [], [], set()   # plan: (row, key) -> person name
    def want(i, r, k, why):
        if k in col and cell(r, k) not in ("TRUE", "N/A"): plan[(i, k)] = (r[0], why)

    for i, r in people:
        name = r[0]
        fs = [k for k in cur if same_person(name, k)]; matched |= set(fs)
        files = [f for k in fs for f in cur[k]]
        for f in files:
            c = classify(f["name"])
            if c and c != "ignore": want(i, r, c, f["name"])
            elif c is None:
                if f["mimeType"].startswith("image/") and f["id"] not in reviewed and any(k in col and cell(r, k) not in ("TRUE", "N/A") for k in IMAGE_KEYS):
                    images.append({"person": name, "file": f["name"], "id": f["id"], "link": f.get("webViewLink", "")})
                elif not f["mimeType"].startswith("image/"):
                    unknown.append(f"{name}: {f['name']}")
        if not any(classify(f["name"]) == "mrt" for f in files):
            if any(classify(f["name"]) == "mrt" for k in prev if same_person(name, k) for f in prev[k]):
                want(i, r, "mrt", "last semester's folder")
        if r[1].strip().lower() in s_keys or norm(name) in s_keys: want(i, r, "survey", "survey responses")
        if norm(name) in cleared: want(i, r, "drive", "vehicle form, column A")

    new_people = []
    for k, files in cur.items():
        if k in matched: continue
        nm = " ".join(w.capitalize() if w.islower() else w for w in re.sub(r"^\s*(FA|SP|SU)\d+\s*", "", k).replace(",", " ").split())
        keys = sorted({classify(f["name"]) for f in files} - {None, "ignore"})
        new_people.append({"name": nm, "keys": keys, "folder": k})

    for e in a.extra:
        nm, _, k = e.partition("=")
        hit = [(i, r) for i, r in people if norm(r[0]) == norm(nm)]
        if hit and k in col: want(hit[0][0], hit[0][1], k, "image review")
        else: print(f"! could not apply --extra {e}")

    # downloads for Claude to read (dry run only)
    if images and not a.apply:
        os.makedirs(a.out, exist_ok=True)
        for n, im in enumerate(images):
            ext = os.path.splitext(im["file"])[1] or ".png"
            im["path"] = os.path.join(a.out, f"{n:02d}_{norm(im['person']).replace(' ', '_')}{ext.lower()}")
            gws("drive", "files", "get", "--params", json.dumps({"fileId": im["id"], "alt": "media", "supportsAllDrives": True}),
                "--output", os.path.basename(im["path"]), cwd=a.out)

    by_key = {}
    for (i, k), (nm, why) in sorted(plan.items()):
        by_key.setdefault(rows[0][col[k]], []).append(nm)
    report = {
        "mode": "APPLY" if a.apply else "DRY RUN",
        "zelle_reminder": f"Check Zelle for dues payments received since {last or 'the start of the semester (no earlier refresh logged)'}.",
        "boxes_to_check": by_key, "box_count": len(plan),
        "new_people": new_people,
        "images_to_review": [{k: im.get(k) for k in ("person", "file", "path", "link")} for im in images] if not a.apply else len(images),
        "unsorted_non_images": unknown,
        "tracker_columns_not_found": [COLS[k] for k in missing_cols],
    }

    if a.apply:
        data = [{"range": f"'{T}'!{col_letter(col[k])}{i}", "values": [[True]]} for (i, k) in plan]
        if data:
            gws("sheets", "spreadsheets", "values", "batchUpdate", "--params", json.dumps({"spreadsheetId": CFG["tracker_id"]}),
                "--json", json.dumps({"valueInputOption": "USER_ENTERED", "data": data}))
        if new_people: add_rows(T, tab["sheetId"], rows, people, col, new_people, H)
        log(today, len(plan), new_people, [im["id"] for im in images], log_tabs)
    print(json.dumps(report, indent=1))


def add_rows(T, sid, rows, people, col, new_people, H):
    """Append rows: copy the first data row (formulas, checkboxes, formats), then write name + reset boxes."""
    last = max(i for i, _ in people); width = len(rows[0]); first = H + 2
    tpl = values(CFG["tracker_id"], f"'{T}'!A{first}:{col_letter(width - 1)}{first}", "FORMULA")[0]
    reqs = [{"insertDimension": {"range": {"sheetId": sid, "dimension": "ROWS", "startIndex": last, "endIndex": last + len(new_people)}, "inheritFromBefore": True}},
            {"copyPaste": {"source": {"sheetId": sid, "startRowIndex": first - 1, "endRowIndex": first, "startColumnIndex": 0, "endColumnIndex": width},
                           "destination": {"sheetId": sid, "startRowIndex": last, "endRowIndex": last + len(new_people), "startColumnIndex": 0, "endColumnIndex": width},
                           "pasteType": "PASTE_NORMAL"}}]
    # the template row may be a strategy-team row with N/A (no checkbox) in a waiver column; re-add checkboxes
    for k, c in col.items():
        dv = {"range": {"sheetId": sid, "startRowIndex": last, "endRowIndex": last + len(new_people), "startColumnIndex": c, "endColumnIndex": c + 1}}
        if k != "st_waiver": dv["rule"] = {"condition": {"type": "BOOLEAN"}}   # no rule = plain cell for the N/A
        reqs.append({"setDataValidation": dv})
    gws("sheets", "spreadsheets", "batchUpdate", "--params", json.dumps({"spreadsheetId": CFG["tracker_id"]}), "--json", json.dumps({"requests": reqs}))
    out = []
    for n, p in enumerate(new_people):
        rn = last + 1 + n; row = []
        for c, v in enumerate(tpl):
            if isinstance(v, str) and v.startswith("="): row.append(None)        # copyPaste already shifted the formula
            elif c == 0: row.append(p["name"])
            elif c in (1, 2): row.append("")
            elif "st_waiver" in col and c == col["st_waiver"]: row.append("N/A")
            elif c in col.values(): row.append(c in {col[k] for k in p["keys"] if k in col})
            else: row.append("")
        out.append({"range": f"'{T}'!A{rn}", "values": [row]})
    gws("sheets", "spreadsheets", "values", "batchUpdate", "--params", json.dumps({"spreadsheetId": CFG["tracker_id"]}),
        "--json", json.dumps({"valueInputOption": "USER_ENTERED", "data": out}))


def log(today, n, new_people, image_ids, tabs):
    if CFG["log_tab"] not in tabs:
        gws("sheets", "spreadsheets", "batchUpdate", "--params", json.dumps({"spreadsheetId": CFG["tracker_id"]}),
            "--json", json.dumps({"requests": [{"addSheet": {"properties": {"title": CFG["log_tab"]}}}]}))
        gws("sheets", "spreadsheets", "values", "update", "--params", json.dumps(
            {"spreadsheetId": CFG["tracker_id"], "range": f"'{CFG['log_tab']}'!A1", "valueInputOption": "RAW"}),
            "--json", json.dumps({"values": [["Refreshed on", "Boxes checked", "Rows added", "Notes", "Images reviewed (file IDs)"]]}))
    gws("sheets", "spreadsheets", "values", "append", "--params", json.dumps(
        {"spreadsheetId": CFG["tracker_id"], "range": f"'{CFG['log_tab']}'!A1", "valueInputOption": "RAW", "insertDataOption": "INSERT_ROWS"}),
        "--json", json.dumps({"values": [[today, n, ", ".join(p["name"] for p in new_people), "Next run: check Zelle from this date", ",".join(image_ids)]]}))


if __name__ == "__main__":
    main()
