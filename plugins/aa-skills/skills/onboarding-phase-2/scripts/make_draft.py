"""Create the Gmail draft reply in the employee's onboarding thread, then turn off the SSN-guard lock.

Usage: make_draft.py --reply-to MESSAGE_ID --to first@architectureandadvocacy.org
           --body-file body.txt [--attach /path/to/pfl.pdf]

Threads the draft onto MESSAGE_ID's thread. Deletes the attachment's local copy
after the draft is saved (it's already in Drive).
"""
import argparse
import base64
import json
import sys
from email.message import EmailMessage
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import gws, lock_off  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reply-to", required=True)
    ap.add_argument("--to", required=True)
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--attach")
    a = ap.parse_args()

    orig = gws(["gmail", "users", "messages", "get"], params={
        "userId": "me", "id": a.reply_to, "format": "metadata",
        "metadataHeaders": ["Subject", "Message-ID", "References"]})
    headers = {h["name"].lower(): h["value"] for h in orig["payload"]["headers"]}
    subject = headers.get("subject", "")
    if not subject.lower().startswith("re:"):
        subject = "Re: " + subject

    msg = EmailMessage()
    msg["To"] = a.to
    msg["Subject"] = subject
    if headers.get("message-id"):
        msg["In-Reply-To"] = headers["message-id"]
        msg["References"] = (headers.get("references", "") + " " + headers["message-id"]).strip()
    msg.set_content(Path(a.body_file).read_text())
    if a.attach:
        p = Path(a.attach)
        msg.add_attachment(p.read_bytes(), maintype="application", subtype="pdf", filename=p.name)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    d = gws(["gmail", "users", "drafts", "create"], params={"userId": "me"},
            body={"message": {"raw": raw, "threadId": orig["threadId"]}})
    if a.attach:
        Path(a.attach).unlink(missing_ok=True)
    Path(a.body_file).unlink(missing_ok=True)
    lock_off()
    print(json.dumps({"draft_id": d.get("id"), "thread_id": orig["threadId"]}))


if __name__ == "__main__":
    main()
