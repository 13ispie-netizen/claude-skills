# Erin's Claude Skills

A shared home for my personal Claude skills so they stay in sync across
**Claude Code**, **Cowork**, and **Claude.ai Chat**.

## Skills in here
- **grill-me** — interview me relentlessly to stress-test a plan or design
- **process-doc** — document a business process (flowcharts, RACI, SOPs)
- **sync-newsletter-contacts** — push new sheet contacts into Squarespace before a newsletter

## How to use this repo

### Claude Code
```
/plugin marketplace add 13ispie-netizen/claude-skills
/plugin install erin-skills@erin-skills
```

### Cowork
Customize → Plugins → Add marketplace → paste this repo's URL, then enable the skills.

### Claude.ai Chat
Settings → Capabilities → upload the skill folders (no direct GitHub import yet).

## Editing a skill
Edit the `SKILL.md` under `plugins/erin-skills/skills/<skill-name>/`, commit, and push.
Code and Cowork pick up changes on update; Chat needs a re-upload.
