"""Shared helpers for onboarding-phase-2 scripts.

Everything that touches raw employee forms lives in these scripts, so SSNs
never reach Claude's context. Scripts print only redacted summaries.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"
LOCK = Path.home() / ".claude" / "onboarding-phase2.lock"
VENV = Path.home() / ".cache" / "aa-onboarding-venv"

# 9 digits, optionally split 3-2-4 by dashes/spaces, not part of a longer number.
SSN_RE = re.compile(r"(?<!\d)\d{3}[- ]?\d{2}[- ]?\d{4}(?!\d)")
SSN_KEY_RE = re.compile(r"social|ssn|security\s*n|f1_05", re.I)


def ensure_pypdf():
    """Re-exec inside a private venv that has pypdf, creating it on first run."""
    try:
        import pypdf  # noqa: F401
        return
    except ImportError:
        pass
    py = VENV / "bin" / "python"
    if not py.exists():
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
        subprocess.run([str(py), "-m", "pip", "-q", "install", "pypdf"], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.execv(str(py), [str(py)] + sys.argv)


def redact(text):
    return SSN_RE.sub("[SSN REDACTED]", str(text))


def gws(args, params=None, body=None, upload=None, upload_type=None, output=None):
    """Run a gws command and return parsed JSON (stderr is discarded)."""
    cmd = ["gws"] + args
    if params is not None:
        cmd += ["--params", json.dumps(params)]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    cwd = None
    if upload:
        # gws only uploads files inside the working directory.
        cwd = str(Path(upload).parent)
        cmd += ["--upload", Path(upload).name]
        if upload_type:
            cmd += ["--upload-content-type", upload_type]
    if output:
        cmd += ["--output", str(output)]
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd).stdout
    if "{" not in out:
        return {}
    data = json.loads(out[out.index("{"):])
    if "error" in data:
        raise RuntimeError(f"gws {' '.join(args)}: {data['error'].get('message')}")
    return data


def upload_to_drive(path, folder_id, name=None, mime="application/pdf"):
    """Upload a file to a (shared-drive) folder, skipping if the name already exists."""
    name = name or Path(path).name
    q = f"'{folder_id}' in parents and trashed=false and name='{name.replace(chr(39), chr(92) + chr(39))}'"
    existing = gws(["drive", "files", "list"], params={
        "q": q, "supportsAllDrives": True, "includeItemsFromAllDrives": True,
        "fields": "files(id,name)"}).get("files", [])
    if existing:
        return existing[0]["id"], "already there"
    res = gws(["drive", "files", "create"], params={"supportsAllDrives": True},
              body={"name": name, "parents": [folder_id]}, upload=path, upload_type=mime)
    return res.get("id"), "uploaded"


def lock_on():
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(str(time.time()))


def lock_off():
    LOCK.unlink(missing_ok=True)
