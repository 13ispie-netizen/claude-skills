#!/usr/bin/env python3
"""PreToolUse hook: force an explicit approval prompt before any email goes out.

Matches Gmail send/reply/forward tools (any connector prefix) and returns
permissionDecision "ask", so Erin must approve each send even when the
connector itself is set to "Always allow". Drafts are not affected.
"""
import json
import sys

try:
    tool = json.load(sys.stdin).get("tool_name", "")
except Exception:
    tool = ""

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": f"Email send guard: {tool} will deliver an email. Approve only if Erin said yes to this exact draft.",
    }
}))
