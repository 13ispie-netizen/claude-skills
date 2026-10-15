#!/usr/bin/env python3
"""Build the documentation package for a Sasaki / South LA Wetlands invoice.

One command does the whole job (run with --help for flags):
  python3 invoice_docs.py --invoice <spreadsheetId>

Steps: find/create the per-invoice folder, copy every linked Drive file into it
as "[for invoice YYMMDD] <name>", add shortcuts for linked folders, leave external
links alone, relink the invoice cells to the copies, PDF the weekly recap emails
into a "YYMMDD weekly reports" subfolder, and create the Gmail draft.
Each step is idempotent: re-running reuses copies/folders that already exist.
Requires the `gws` CLI. Prints a JSON report on stdout.
"""
import argparse, base64, html, json, os, re, shutil, subprocess, sys, tempfile
from datetime import date
from email.message import EmailMessage

PARENT = "1imoTrwsgC8zJIck2e3aMAcRdNHpFEpcf"  # Sasaki invoice documentation (parent)
RECAP_FROM = "kianna@architectureandadvocacy.org"
DRAFT_TO = "Accounts Payable <accountspayable@sasaki.com>"
DRAFT_CC = "Megan Vogt <mvogt@sasaki.com>"
DRAFT_BCC = "Finance A+A <finance@architectureandadvocacy.org>"
PREFIX_RE = re.compile(r"^(\[for invoice \d{6}\]\s*)+")
FOLDER_MIME = "application/vnd.google-apps.folder"
SHORTCUT_MIME = "application/vnd.google-apps.shortcut"
MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], 1)}
BROWSERS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "chromium", "chromium-browser",
]
report = {"copied": [], "reused": [], "shortcuts": [], "external": [], "relinked": 0,
          "recaps": [], "skipped_emails": [], "warnings": []}


def gws(*args, body=None, upload=None, cwd=None):
    cmd = ["gws", *args[:-1], "--params", json.dumps(args[-1])]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    if upload:  # gws only accepts a bare filename for --upload, so run from its folder
        cwd, name = os.path.split(upload)
        cmd += ["--upload", name, "--upload-content-type", "application/pdf"]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    out = r.stdout.strip()
    try:
        data = json.loads(out) if out else {}
    except json.JSONDecodeError:
        sys.exit(f"gws returned non-JSON for {args[:3]}: {out[:300]} {r.stderr[-300:]}")
    if isinstance(data, dict) and "error" in data:
        sys.exit(f"gws error on {args[:3]}: {data['error']}")
    return data


def list_children(folder):
    q = f"'{folder}' in parents and trashed=false"
    return gws("drive", "files", "list", {"q": q, "fields": "files(id,name,mimeType,shortcutDetails)",
               "pageSize": 1000, "supportsAllDrives": True, "includeItemsFromAllDrives": True}).get("files", [])


def ensure_folder(parent, name):
    for f in list_children(parent):
        if f["name"] == name and f["mimeType"] == FOLDER_MIME:
            return f["id"], False
    f = gws("drive", "files", "create", {"supportsAllDrives": True, "fields": "id"},
            body={"name": name, "mimeType": FOLDER_MIME, "parents": [parent]})
    return f["id"], True


def file_id(url):
    if not re.search(r"(docs|drive)\.google\.com", url):
        return None
    m = re.search(r"/(?:d|folders)/([\w-]{20,})", url) or re.search(r"[?&]id=([\w-]{20,})", url)
    return m.group(1) if m else None


def view_url(f):
    return f.get("webViewLink", "").split("?")[0] or f"https://drive.google.com/open?id={f['id']}"


# ---------- invoice metadata ----------
def invoice_meta(sid, tab):
    meta = gws("sheets", "spreadsheets", "get", {"spreadsheetId": sid,
               "fields": "properties.title,sheets.properties.sheetId,sheets.properties.title"})
    title = meta["properties"]["title"]
    tabs = {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta["sheets"]}
    tab = tab or next((t for t in tabs if t.startswith("INV")), None)
    if tab not in tabs:
        sys.exit(f"Invoice tab not found; tabs are {list(tabs)}")
    vals = gws("sheets", "spreadsheets", "values", "get",
               {"spreadsheetId": sid, "range": f"'{tab}'!A1:H14"}).get("values", [])
    flat = {}
    for r, row in enumerate(vals):
        for c, v in enumerate(row):
            flat[v.strip().lower()] = (r, c)
    def below(label):
        if label not in flat:
            return ""
        r, c = flat[label]
        try:
            return vals[r + 1][c]
        except IndexError:
            return ""
    return title, tabs, tab, below("issue date"), below("services through")


def parse_period(text, issue_year):
    found = re.findall(r"([A-Za-z]+)\.?\s+(\d{1,2})", text)
    found = [(MONTHS[m.lower()], int(d)) for m, d in found if m.lower() in MONTHS]
    if len(found) < 2:
        return None, None
    (m1, d1), (m2, d2) = found[0], found[-1]
    y1 = issue_year - 1 if m1 > m2 else issue_year
    return date(y1, m1, d1), date(issue_year, m2, d2)


# ---------- links ----------
def scan_links(sid):
    grid = gws("sheets", "spreadsheets", "get", {"spreadsheetId": sid, "includeGridData": True,
               "fields": "sheets(properties(sheetId,title),data(startRow,startColumn,rowData(values(userEnteredValue,hyperlink,textFormatRuns))))"})
    cells = []
    for sh in grid["sheets"]:
        for blk in sh.get("data", []):
            r0, c0 = blk.get("startRow", 0), blk.get("startColumn", 0)
            for ri, row in enumerate(blk.get("rowData", [])):
                for ci, c in enumerate(row.get("values", [])):
                    urls = [r["format"]["link"]["uri"] for r in c.get("textFormatRuns", []) or []
                            if r.get("format", {}).get("link", {}).get("uri")]
                    if c.get("hyperlink"):
                        urls.append(c["hyperlink"])
                    f = c.get("userEnteredValue", {}).get("formulaValue", "")
                    urls += re.findall(r'HYPERLINK\(\s*"([^"]+)"', f, re.I)
                    if urls:
                        cells.append({"sheetId": sh["properties"]["sheetId"], "row": r0 + ri,
                                      "col": c0 + ci, "urls": sorted(set(urls))})
    return cells


def build_copies(cells, folder, prefix):
    existing = {f["name"]: f for f in list_children(folder)}
    in_folder = {f["id"] for f in existing.values()}
    mapping, seen = {}, set()
    for cell in cells:
        for url in cell["urls"]:
            fid = file_id(url)
            if not fid:
                report["external"].append(url) if url not in report["external"] else None
                continue
            if fid in seen or fid in in_folder:
                continue
            seen.add(fid)
            src = gws("drive", "files", "get", {"fileId": fid, "fields": "id,name,mimeType,appProperties",
                      "supportsAllDrives": True})
            root = (src.get("appProperties") or {}).get("invoiceSourceId")
            if root and root != fid:  # link points at an earlier invoice's frozen copy: go back to the live original
                src = gws("drive", "files", "get", {"fileId": root, "fields": "id,name,mimeType",
                          "supportsAllDrives": True})
            elif PREFIX_RE.match(src["name"]):
                report["warnings"].append(f"{src['name']} is an earlier invoice's copy with no link to its original; copied the snapshot")
            name = prefix + PREFIX_RE.sub("", src["name"])
            if src["mimeType"] == FOLDER_MIME:
                if name not in existing:
                    gws("drive", "files", "create", {"supportsAllDrives": True, "fields": "id"},
                        body={"name": name, "mimeType": SHORTCUT_MIME, "parents": [folder],
                              "shortcutDetails": {"targetId": fid}})
                report["shortcuts"].append(src["name"])
                continue  # folder links stay pointed at the live folder
            if name in existing:
                f = gws("drive", "files", "get", {"fileId": existing[name]["id"],
                        "fields": "id,webViewLink", "supportsAllDrives": True})
                report["reused"].append(name)
            else:
                f = gws("drive", "files", "copy", {"fileId": fid, "supportsAllDrives": True,
                        "fields": "id,webViewLink"}, body={"name": name, "parents": [folder],
                              "appProperties": {"invoiceSourceId": src["id"]}})
                report["copied"].append(name)
            mapping[fid] = view_url(f)
    # shortcuts in the folder whose target is no longer linked anywhere
    linked = {file_id(u) for c in cells for u in c["urls"]}
    for f in existing.values():
        if f["mimeType"] == SHORTCUT_MIME and f.get("shortcutDetails", {}).get("targetId") not in linked:
            report["warnings"].append(f"Shortcut no longer linked in the invoice: {f['name']} (ask Erin before removing)")
    return mapping


def relink(sid, cells, mapping):
    if not mapping:
        return
    def swap(u):
        fid = file_id(u)
        return mapping.get(fid, u) if fid else u
    reqs = []
    for cell in cells:
        if not any(file_id(u) in mapping for u in cell["urls"]):
            continue
        # fresh read of this one cell right before writing
        a1 = f"R{cell['row'] + 1}C{cell['col'] + 1}"
        g = gws("sheets", "spreadsheets", "get", {"spreadsheetId": sid, "includeGridData": True,
                "ranges": [f"'{title_by_id[cell['sheetId']]}'!{a1}"],
                "fields": "sheets(data(rowData(values(userEnteredValue,hyperlink,textFormatRuns))))"})
        c = g["sheets"][0]["data"][0]["rowData"][0]["values"][0]
        uev, runs, n = c.get("userEnteredValue", {}), c.get("textFormatRuns"), 0
        if "formulaValue" in uev:
            new = re.sub(r'(HYPERLINK\(\s*")([^"]+)', lambda m: m.group(1) + swap(m.group(2)), uev["formulaValue"], flags=re.I)
            n += new != uev["formulaValue"]
            uev = {"formulaValue": new}
        if runs:
            for r in runs:
                link = r.get("format", {}).get("link", {})
                if link.get("uri") and swap(link["uri"]) != link["uri"]:
                    link["uri"] = swap(link["uri"]); n += 1
        elif c.get("hyperlink") and "formulaValue" not in uev and swap(c["hyperlink"]) != c["hyperlink"]:
            runs = [{"startIndex": 0, "format": {"link": {"uri": swap(c["hyperlink"])}}}]; n += 1
        if not n:
            continue
        val, fields = {"userEnteredValue": uev}, "userEnteredValue"
        if runs:
            val["textFormatRuns"] = runs; fields += ",textFormatRuns"
        reqs.append({"updateCells": {"rows": [{"values": [val]}], "fields": fields,
                     "start": {"sheetId": cell["sheetId"], "rowIndex": cell["row"], "columnIndex": cell["col"]}}})
        report["relinked"] += n
    if reqs:
        gws("sheets", "spreadsheets", "batchUpdate", {"spreadsheetId": sid}, body={"requests": reqs})
    # verify
    left = [u for c in scan_links(sid) for u in c["urls"] if file_id(u) in mapping]
    if left:
        report["warnings"].append(f"Links still pointing at originals: {left}")


# ---------- weekly recap PDFs ----------
def find_browser():
    for b in BROWSERS:
        if os.path.exists(b) or shutil.which(b):
            return shutil.which(b) or b
    return None


def recap_name(subject, prefix):
    s = re.sub(r"^((re|fwd?|fw):\s*)+", "", subject, flags=re.I).strip()
    m = re.search(r"(\d{1,2}/\d{1,2})\s*-\s*(\d{1,2}/\d{1,2})", s)
    if m:
        s = s.replace(m.group(0), f"{m.group(1)} to {m.group(2)}")
    return prefix + s.replace("/", "-") + ".pdf"


def recaps(start, end, folder, stamp, prefix, sender):
    q = (f"from:{sender} after:{start:%Y/%m/%d} before:{date.fromordinal(end.toordinal() + 1):%Y/%m/%d} "
         '(subject:recap OR subject:"week of" OR subject:weekly)')
    ids, tok = [], None
    while True:
        p = {"userId": "me", "q": q, "maxResults": 100}
        if tok:
            p["pageToken"] = tok
        r = gws("gmail", "users", "messages", "list", p)
        ids += [m["id"] for m in r.get("messages", [])]
        tok = r.get("nextPageToken")
        if not tok:
            break
    msgs = []
    for mid in ids:
        d = gws("gmail", "users", "messages", "get", {"userId": "me", "id": mid, "format": "full"})
        h = {x["name"]: x["value"] for x in d["payload"]["headers"]}
        subj = h.get("Subject", "")
        if re.search(r"week of|weekly", subj, re.I):
            msgs.append((d, h))
        else:
            report["skipped_emails"].append(f"{h.get('Date', '')[:16]} | {subj}")
    if not msgs:
        report["warnings"].append(f"No weekly recaps from {sender} between {start} and {end}")
        return None
    browser = find_browser()
    if not browser:
        report["warnings"].append("No Chromium browser found for PDF rendering; recaps not converted")
        return None
    sub, _ = ensure_folder(folder, f"{stamp} weekly reports")
    have = {f["name"] for f in list_children(sub)}
    tmp = tempfile.mkdtemp()
    for d, h in sorted(msgs, key=lambda x: int(x[0]["internalDate"])):
        name = recap_name(h.get("Subject", ""), prefix)
        report["recaps"].append(name)
        if name in have:
            continue
        parts, att = {"text/html": None, "text/plain": None}, []
        def walk(p):
            b = p.get("body", {})
            if p.get("filename"):
                att.append(p["filename"])
            elif p.get("mimeType") in parts and parts[p["mimeType"]] is None and b.get("data"):
                parts[p["mimeType"]] = base64.urlsafe_b64decode(b["data"]).decode("utf-8", "replace")
            for c in p.get("parts", []) or []:
                walk(c)
        walk(d["payload"])
        body = parts["text/html"] or f'<pre style="white-space:pre-wrap">{html.escape(parts["text/plain"] or "")}</pre>'
        rows = "".join(f'<tr><td style="color:#666;padding-right:12px">{k}</td><td>{html.escape(h[k])}</td></tr>'
                       for k in ["From", "To", "Cc", "Date", "Subject"] if h.get(k))
        if att:
            rows += f'<tr><td style="color:#666">Attachments</td><td>{html.escape(", ".join(att))}</td></tr>'
            report["warnings"].append(f"{name}: email had attachments not included in the PDF: {att}")
        page = (f'<html><head><meta charset="utf-8"><style>body{{font-family:Arial,sans-serif;font-size:12px;margin:32px}}</style></head>'
                f'<body><h2 style="font-size:16px">{html.escape(h.get("Subject", ""))}</h2>'
                f'<table style="font-size:12px;margin-bottom:16px">{rows}</table><hr>{body}</body></html>')
        hp, pp = os.path.join(tmp, d["id"] + ".html"), os.path.join(tmp, d["id"] + ".pdf")
        open(hp, "w").write(page)
        subprocess.run([browser, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={pp}", "file://" + hp], capture_output=True, timeout=120)
        if not os.path.exists(pp):
            report["warnings"].append(f"PDF render failed for {name}")
            continue
        gws("drive", "files", "create", {"supportsAllDrives": True, "fields": "id"},
            body={"name": name, "parents": [sub]}, upload=pp)
    return sub


# ---------- email draft ----------
def draft(month, folder):
    url = f"https://drive.google.com/drive/folders/{folder}"
    subject = f"{month} Invoice"
    existing = gws("gmail", "users", "drafts", "list", {"userId": "me", "q": f'subject:"{subject}"', "maxResults": 10})
    if existing.get("drafts"):
        report["warnings"].append(f'A draft titled "{subject}" already exists; did not create another')
        return
    text = (f"Hi Sasaki Team,\n\nPlease find Architecture + Advocacy's {month} Invoice attached. "
            f"You can access all of our documentation here <{url}>.\n\n"
            "You should have also received a payment link from quickbooks, for when the time comes.\n\n"
            "Please let me know if you have any issues accessing the documents, or any questions.\n\n-E\n")
    htm = (f'<div dir="ltr">Hi Sasaki Team,<div><br></div><div>Please find Architecture + Advocacy&#39;s {month} '
           f'Invoice attached. You can access all of our <a href="{url}">documentation here</a>.</div><div><br></div>'
           "<div>You should have also received a payment link from quickbooks, for when the time comes.</div>"
           "<div><br></div><div>Please let me know if you have any issues accessing the documents, or any questions.</div>"
           "<div><br></div><div>-E</div></div>")
    msg = EmailMessage()
    msg["To"] = DRAFT_TO
    msg["Cc"] = DRAFT_CC
    msg["Bcc"] = DRAFT_BCC
    msg["Subject"] = subject
    msg.set_content(text)
    msg.add_alternative(htm, subtype="html")
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    gws("gmail", "users", "drafts", "create", {"userId": "me"}, body={"message": {"raw": raw}})
    report["draft"] = subject


def main():
    global title_by_id
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--invoice", required=True, help="invoice spreadsheet ID")
    ap.add_argument("--tab", help="invoice tab (default: first tab starting with INV)")
    ap.add_argument("--stamp", help="YYMMDD (default: invoice file-name prefix)")
    ap.add_argument("--start", help="period start YYYY-MM-DD (default: 'Services through' cell)")
    ap.add_argument("--end", help="period end YYYY-MM-DD")
    ap.add_argument("--parent", default=PARENT)
    ap.add_argument("--sender", default=RECAP_FROM)
    ap.add_argument("--skip", default="", help="comma list of steps to skip: docs,recaps,draft")
    a = ap.parse_args()
    skip = set(filter(None, a.skip.split(",")))

    title, tabs, tab, issue, period = invoice_meta(a.invoice, a.tab)
    title_by_id = {v: k for k, v in tabs.items()}
    stamp = a.stamp or (re.match(r"(\d{6})", title) or [None, None])[1]
    if not stamp:
        sys.exit("No YYMMDD prefix on the invoice file name; pass --stamp")
    yr = 2000 + int(stamp[:2])
    month = list(MONTHS)[int(stamp[2:4]) - 1].capitalize()
    start, end = parse_period(period, yr)
    if a.start:
        start = date.fromisoformat(a.start)
    if a.end:
        end = date.fromisoformat(a.end)
    prefix = f"[for invoice {stamp}] "
    report.update(invoice=title, tab=tab, issue_date=issue, period=f"{start} to {end}")

    folder, created = ensure_folder(a.parent, f"{stamp}_sasaki invoice_documentation")
    report["folder"] = {"id": folder, "url": f"https://drive.google.com/drive/folders/{folder}", "created": created}

    if "docs" not in skip:
        cells = scan_links(a.invoice)
        mapping = build_copies(cells, folder, prefix)
        relink(a.invoice, cells, mapping)
    if "recaps" not in skip:
        if not (start and end):
            report["warnings"].append(f"Could not parse service period from '{period}'; pass --start/--end")
        else:
            sub = recaps(start, end, folder, stamp, prefix, a.sender)
            if sub:
                report["recap_folder"] = f"https://drive.google.com/drive/folders/{sub}"
    if "draft" not in skip:
        draft(month, folder)
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
