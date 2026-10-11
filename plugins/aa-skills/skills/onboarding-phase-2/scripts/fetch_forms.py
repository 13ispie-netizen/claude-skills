"""Move signed forms from Gmail and/or a shared Drive folder to the employee's folder,
and print a redacted summary.

Usage: fetch_forms.py --folder DRIVE_FOLDER_ID [--thread THREAD_ID ...] [--drive-folder ID_OR_URL ...]

- Downloads every attachment in the given threads, and every file in the given
  Drive folders (subfolders included, Google Docs exported as PDF), to a private temp dir.
- If the same filename was sent twice, keeps only the latest (older copies are noted).
- Uploads each form to the Drive folder (skips names already there).
- Prints JSON: each form's filled fields or text with SSNs redacted, plus an
  SSN cross-check result (match / mismatch). The SSN itself is never printed.
- Deletes the temp dir before exiting. Turns on the SSN-guard lock.
"""
import argparse
import base64
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (SSN_KEY_RE, SSN_RE, ensure_pypdf, gws, lock_on, redact,  # noqa: E402
                     upload_to_drive)

ensure_pypdf()
from pypdf import PdfReader  # noqa: E402

MAX_TEXT = 2500  # offer letters (need rate, hours, start date)
SHORT_TEXT = 300  # everything else: enough to spot a signature block


def walk(part):
    if part.get("filename") and part.get("body", {}).get("attachmentId"):
        yield part
    for child in part.get("parts", []) or []:
        yield from walk(child)


def gmail_items(threads):
    """Yield (timestamp, filename, fetch) for every attachment the employee sent."""
    msgs = []
    for tid in threads:
        t = gws(["gmail", "users", "threads", "get"], params={"userId": "me", "id": tid, "format": "full"})
        msgs += t.get("messages", [])
    for m in msgs:
        if "SENT" in m.get("labelIds", []):
            continue  # only what the employee sent back, never Erin's own attachments
        for part in walk(m["payload"]):
            def fetch(path, m=m, part=part):
                att = gws(["gmail", "users", "messages", "attachments", "get"],
                          params={"userId": "me", "messageId": m["id"], "id": part["body"]["attachmentId"]})
                path.write_bytes(base64.urlsafe_b64decode(att["data"] + "=="))
            yield int(m.get("internalDate", 0)), part["filename"].strip(), fetch


def drive_items(folder):
    """Yield (timestamp, filename, fetch) for every file in a shared Drive folder, recursively."""
    folder = re.sub(r".*/folders/([\w-]+).*", r"\1", folder)
    files = gws(["drive", "files", "list"], params={
        "q": f"'{folder}' in parents and trashed=false", "pageSize": 200,
        "supportsAllDrives": True, "includeItemsFromAllDrives": True,
        "fields": "files(id,name,mimeType,modifiedTime)"}).get("files", [])
    for f in files:
        mime = f["mimeType"]
        if mime == "application/vnd.google-apps.folder":
            yield from drive_items(f["id"])
            continue
        native = mime.startswith("application/vnd.google-apps.")
        if native and mime.split(".")[-1] not in ("document", "spreadsheet", "presentation"):
            continue  # shortcuts, forms, etc.
        ts = int(datetime.fromisoformat(f["modifiedTime"].replace("Z", "+00:00")).timestamp() * 1000)

        def fetch(path, f=f, native=native):
            if native:
                gws(["drive", "files", "export"], params={"fileId": f["id"], "mimeType": "application/pdf"},
                    output=path)
            else:
                gws(["drive", "files", "get"], params={"fileId": f["id"], "alt": "media",
                                                        "supportsAllDrives": True}, output=path)
        yield ts, f["name"].strip() + (".pdf" if native else ""), fetch


def collect(threads, drive_folders, tmp):
    """Return {filename: {"path", "superseded"}} keeping the latest copy of each name."""
    items = list(gmail_items(threads))
    for folder in drive_folders:
        items += list(drive_items(folder))
    items.sort(key=lambda x: x[0])
    files = {}
    for i, (_, name, fetch) in enumerate(items):
        path = Path(tmp) / f"{i}_file"
        fetch(path)
        if not path.exists():
            continue
        if path.read_bytes()[:4] == b"%PDF" and not name.lower().endswith(".pdf"):
            name += ".pdf"
        path = path.rename(Path(tmp) / f"{i}_{name}")
        key = name.lower()
        superseded = files[key]["superseded"] + 1 if key in files else 0
        files[key] = {"name": name, "path": path, "superseded": superseded}
    return files


def summarize(path):
    """Return (summary dict, set of SSN candidates) for one PDF."""
    try:
        reader = PdfReader(str(path))
    except Exception:
        return {"kind": "unreadable: Erin must review this form"}, set()
    ssns, fields = set(), {}
    for key, f in (reader.get_fields() or {}).items():
        val = f.get("/V")
        if val in (None, "", "/Off"):
            continue
        val = str(val)
        digits = "".join(c for c in val if c.isdigit())
        if SSN_KEY_RE.search(key):
            if len(digits) == 9:
                ssns.add(digits)
            fields[key] = "[SSN REDACTED]"
            continue
        ssns.update("".join(c for c in m if c.isdigit()) for m in SSN_RE.findall(val))
        fields[key] = redact(val)[:80]
    if fields:
        return {"kind": "fillable", "fields": fields}, ssns
    text = " ".join(" ".join((p.extract_text() or "").split()) for p in reader.pages).strip()
    if not text:
        return {"kind": "scanned: Erin must review this form"}, set()
    ssns.update("".join(c for c in m if c.isdigit()) for m in SSN_RE.findall(text))
    limit = MAX_TEXT if "offer" in path.name.lower() else SHORT_TEXT
    return {"kind": "text", "text": redact(text)[:limit]}, ssns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    ap.add_argument("--thread", action="append", default=[])
    ap.add_argument("--drive-folder", action="append", default=[])
    args = ap.parse_args()
    if not args.thread and not args.drive_folder:
        ap.error("give at least one --thread or --drive-folder")
    lock_on()
    tmp = tempfile.mkdtemp(prefix="aa-onb-")
    Path(tmp).chmod(0o700)
    out, ssn_sets = [], {}
    try:
        for f in collect(args.thread, args.drive_folder, tmp).values():
            is_pdf = f["path"].read_bytes()[:4] == b"%PDF"
            drive_id, status = upload_to_drive(f["path"], args.folder, f["name"],
                                               "application/pdf" if is_pdf else "application/octet-stream")
            entry = {"file": f["name"], "drive_id": drive_id, "status": status}
            if f["superseded"]:
                entry["note"] = f"latest of {f['superseded'] + 1} copies; older ones skipped"
            if is_pdf:
                summary, ssns = summarize(f["path"])
                entry.update(summary)
                if ssns:
                    ssn_sets[f["name"]] = ssns
            else:
                entry["kind"] = "not a PDF: Erin must review this form"
            out.append(entry)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    common = set.intersection(*ssn_sets.values()) if ssn_sets else set()
    all_ssns = set().union(*ssn_sets.values()) if ssn_sets else set()
    check = {
        "forms_with_ssn": sorted(ssn_sets),
        "result": ("no SSN found" if not ssn_sets else
                   "match" if common else "MISMATCH: SSNs differ across these forms"),
    }
    if any(s.startswith("9") for s in all_ssns):
        check["itin_warning"] = "a number starting with 9 looks like an ITIN; ITINs can't be accepted in place of an SSN"
    print(json.dumps({"forms": out, "ssn_check": check}, indent=1))


if __name__ == "__main__":
    main()
