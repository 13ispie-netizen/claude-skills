#!/usr/bin/env python3
"""Stop hook: three guards against skill/hook work that never reaches a machine.

1. ~/claude-skills must have nothing uncommitted and nothing unpushed.
2. ~/.claude/settings*.json must not define hooks locally -- hooks belong in the
   general-skills plugin so they sync to every machine.
3. The installed plugin cache must match the repo. Pushing changes the source,
   not what Claude loads; plugins run from a pinned snapshot under
   ~/.claude/plugins/cache/ that only moves on `claude plugin update`.

Guard 3 catches the two ways a shipped skill silently fails to arrive:
  - repo version ahead of installed version -> nobody ran the update
  - contents differ at the SAME version -> the updater no-ops forever, because
    it compares version numbers rather than file contents

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

# --- Guard 3: installed plugin cache matches the repo -------------------------
# Compare only the files that carry behavior, so install metadata never trips this.
TRACKED = ("SKILL.md", "hooks.json", ".py", ".sh", "plugin.json")


def tracked_files(root):
    """Relative paths of behavior-carrying files under root."""
    found = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in filenames:
            if fn.startswith("."):
                continue
            if fn in TRACKED or fn.endswith(TRACKED[2:]):
                full = os.path.join(dirpath, fn)
                found[os.path.relpath(full, root)] = full
    return found


def read(path):
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except Exception:
        return None


try:
    with open(os.path.expanduser("~/.claude/plugins/installed_plugins.json")) as fh:
        installed = json.load(fh).get("plugins", {})
except Exception:
    installed = {}

plugins_dir = os.path.join(repo, "plugins")
if installed and os.path.isdir(plugins_dir):
    for entry in sorted(os.listdir(plugins_dir)):
        plugin_root = os.path.join(plugins_dir, entry)
        manifest = read(os.path.join(plugin_root, ".claude-plugin", "plugin.json"))
        if manifest is None:
            continue
        try:
            meta = json.loads(manifest)
        except Exception:
            continue
        name = meta.get("name", entry)
        repo_version = str(meta.get("version", ""))

        # Match "<name>@<marketplace>" regardless of which marketplace it came from.
        record = next(
            (v[0] for k, v in installed.items()
             if k.split("@")[0] == name and isinstance(v, list) and v),
            None,
        )
        # Not installed on this machine is a deliberate choice, not a mistake.
        if not record:
            continue

        install_path = record.get("installPath", "")
        installed_version = str(record.get("version", ""))

        if not os.path.isdir(install_path):
            continue

        if repo_version != installed_version:
            problems.append(
                f"Plugin '{name}' is v{repo_version} in the repo but v{installed_version} "
                f"is installed. Pushing does not update what Claude loads.\n"
                f"Run: claude plugin update {name}@erin-skills"
            )
            continue

        # Same version: any content difference means the bump was forgotten, and
        # `claude plugin update` will report success while doing nothing.
        stale = [
            rel for rel, full in sorted(tracked_files(plugin_root).items())
            if read(os.path.join(install_path, rel)) != read(full)
        ]
        if stale:
            problems.append(
                f"Plugin '{name}' differs from what is installed, but both are "
                f"v{repo_version}, so the updater will no-op:\n  "
                + "\n  ".join(stale)
                + f"\nBump the version in plugins/{entry}/.claude-plugin/plugin.json, "
                  f"push, then run: claude plugin update {name}@erin-skills"
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
