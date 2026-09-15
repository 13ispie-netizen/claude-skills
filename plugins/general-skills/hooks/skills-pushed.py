#!/usr/bin/env python3
"""Stop hook: two guards against skill/hook work that never leaves this machine.

1. ~/claude-skills must have nothing uncommitted and nothing unpushed.
2. ~/.claude/settings*.json must not define hooks locally -- hooks belong in the
   general-skills plugin so they sync to every machine.

Enforces the Skill Development rules in CLAUDE.md. Exits 0 silently when clean.
"""
import json, os, subprocess, sys

try:
    data = json.load(sys.stdin)
except Exception:
    data = {}

# Claude Code sets this when re-invoking after a block; bail out so we can't loop.
if data.get("stop_hook_active"):
    sys.exit(0)

problems = []

# --- Guard 1: skills repo is fully pushed -------------------------------------
repo = os.path.expanduser("~/claude-skills")
if os.path.isdir(os.path.join(repo, ".git")):
    def git(*args):
        return subprocess.run(
            ["git", "-C", repo, *args], capture_output=True, text=True
        ).stdout.strip()

    dirty = git("status", "--porcelain")
    has_upstream = git("rev-parse", "--abbrev-ref", "@{u}")
    unpushed = git("log", "--oneline", "@{u}..HEAD") if has_upstream else ""

    if dirty:
        problems.append("~/claude-skills has uncommitted changes:\n" + dirty)
    if unpushed:
        problems.append("~/claude-skills has unpushed commits:\n" + unpushed)

# --- Guard 2: no locally-defined hooks ----------------------------------------
for name in ("settings.json", "settings.local.json"):
    path = os.path.expanduser(f"~/.claude/{name}")
    try:
        with open(path) as fh:
            local_hooks = json.load(fh).get("hooks")
    except Exception:
        continue
    if local_hooks:
        problems.append(
            f"~/.claude/{name} defines hooks locally: {', '.join(local_hooks)}.\n"
            "Hooks belong in plugins/general-skills/hooks/ so they sync to every machine."
        )

if not problems:
    sys.exit(0)

print(json.dumps({
    "decision": "block",
    "reason": (
        "Work here would not survive leaving this machine. Per CLAUDE.md (Skill Development): "
        "a skill is not done until it is committed and pushed, and hooks live in the "
        "general-skills plugin, never in local settings.\n\n"
        + "\n\n".join(problems)
        + "\n\nFix it, then report the commit hash. If this is deliberately unfinished, say that "
          "to Erin explicitly instead of ending the turn silently."
    ),
}))
