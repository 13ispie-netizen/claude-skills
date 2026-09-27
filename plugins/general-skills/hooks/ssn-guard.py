"""PreToolUse guard: keep employee SSNs out of Claude's context during onboarding.

While the onboarding-phase-2 skill is running (lock file present, < 3 hours old),
Claude may not open PDFs or images directly, read/download Drive files, or fetch
Gmail attachments outside the skill's own scripts. Those scripts redact SSNs.
The skill's private temp dirs (aa-onb-*) are blocked at all times.
"""
import json
import re
import sys
import time
from pathlib import Path

LOCK = Path.home() / ".claude" / "onboarding-phase2.lock"
MAX_AGE = 3 * 3600
FORM_FILE = re.compile(r"\.(pdf|png|jpe?g|heic|tiff?)\b", re.I)
SKILL_SCRIPTS = "onboarding-phase-2/scripts/"
DRIVE_READS = {"mcp__claude_ai_Google_Drive__read_file_content",
               "mcp__claude_ai_Google_Drive__download_file_content"}


def block(reason):
    print(f"Blocked by ssn-guard: {reason}", file=sys.stderr)
    sys.exit(2)


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        return
    tool = event.get("tool_name", "")
    inp = event.get("tool_input", {}) or {}
    target = inp.get("file_path", "") if tool == "Read" else inp.get("command", "") if tool == "Bash" else ""

    if "aa-onb-" in target:
        block("that folder holds raw employee forms. Use the onboarding-phase-2 scripts.")

    active = LOCK.exists() and time.time() - LOCK.stat().st_mtime < MAX_AGE
    if not active:
        return
    if tool in DRIVE_READS:
        block("onboarding is running, so Drive files can't be opened directly. Use the skill's scripts.")
    if tool == "Read" and FORM_FILE.search(target):
        block("onboarding is running, so forms can't be opened directly. Use fetch_forms.py.")
    if tool == "Bash" and SKILL_SCRIPTS not in target and (
            FORM_FILE.search(target) or "attachments get" in target):
        block("onboarding is running, so forms and attachments can only go through the skill's scripts.")


if __name__ == "__main__":
    main()
