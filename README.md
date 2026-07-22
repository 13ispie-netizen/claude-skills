# Erin's Claude Skills

A shared home for my personal Claude skills so they stay in sync across
**Claude Code**, **Cowork**, and **Claude.ai Chat**.

## Groups
- **aa-skills** (A+A / work): process-doc, sync-newsletter-contacts
- **general-skills** (general / productivity): grill-me
- **fun-skills** (personal): empty for now — drop your first fun skill in
  `plugins/fun-skills/skills/`, then it gets added to the marketplace.

## How to use this repo

### Claude Code
```
/plugin marketplace add 13ispie-netizen/claude-skills
/plugin install aa-skills@erin-skills
/plugin install general-skills@erin-skills
```

### Cowork
Customize → Plugins → Add marketplace → paste this repo's URL, then enable the groups.

### Claude.ai Chat
Settings → Capabilities → upload the skill folders (no direct GitHub import yet).

## Editing or adding a skill
Edit the `SKILL.md` under `plugins/<group>/skills/<skill-name>/`, commit, and push.
Code and Cowork pick up changes on update; Chat needs a re-upload.
