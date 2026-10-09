---
name: policy-endorsement-quick-facts
description: "Research a policy, bill, ordinance, or ballot measure and fill out A+A's Policy Endorsement Quick Facts (.docx) so the board can vote on whether to endorse it. Use whenever Erin says 'should we endorse [X]', 'endorsement quick facts', 'fill out the endorsement template', 'policy endorsement for the board', or shares supporter materials for a measure and asks for a board-ready summary. Also use to produce the blank template."
---

# Policy Endorsement Quick Facts

Produces A+A's two-page board decision doc. Page 1 has the endorsement criteria checklists and the 501(c)(3) lobbying note. Page 2 has a two-column Quick Facts table. The layout is fixed in `scripts/build_quick_facts.js`, so Claude only supplies the content as JSON.

## Workflow

### 1. Intake
- Get the policy name and any supporter materials (docs, Drive folders, sites). Assume supporter materials are biased.
- Log every link Erin shares in Board HQ `MEMORY.md` under Reference Links (Date | Link | Description).

### 2. Research, neutral sources first
Read in this order, and stop once every field is answered:
1. **Official sources.** Ballot or bill text, the impartial analysis, the fiscal impact statement, and the official arguments for and against, with their signers. For LA City measures, that's the City Clerk measure PDF and the council file's CAO report.
2. **Neutral press.** LAist, LA Times, CalMatters, local outlets. Use these for opposition, council votes, and context.
3. **Supporter materials.** Use them only for the supporter list and for stats, which go in as "Supporters cite...". Never use them to judge risks or opposition. When numbers conflict, use the official figure.

For a large PDF that the Read tool can't render, extract its text with macOS PDFKit (a short `swift` script), `pdftotext`, or a subagent.

### 3. Ask Erin, in ONE AskUserQuestion call, before filling
- **A+A's firsthand evidence.** What have A+A's projects or residents shown about this issue? This is often the strongest line in the doc.
- **Partners who support.** Pull the campaign's full public endorsement list, then show Erin the likely matches with A+A partners as a multi-select. Never write "None confirmed" without asking.

### 4. Fill the fields (style rules learned from Erin's edits)
- **Pre-check the boxes.** Mark each "must" and "disqualification" box with Claude's honest assessment. The board reacts to a call; it doesn't start from blank.
- **Expertise blank:** name the issue area plus A+A's firsthand evidence.
- **Connection to mission:** bullets. Include the equity stat, the policy's relevant priorities, A+A's firsthand evidence, and any gap, such as no community engagement requirement.
- **Risks:** short and neutral, like "Could increase LA's budget deficit." Don't inflate them with dollar figures or by naming which departments could lose funding. Keep design flaws (what it doesn't fix, whether equity is guaranteed).
- **Polarizing:** answer directly ("No." / "Yes.") plus one short reason. Don't hedge with "low to moderate" or invent tension.
- **Opposition:** list organized opposition and official recommendations against. Leave out individual lone votes.
- **What endorsing means:** concrete actions only. The lobbying note already lives on page 1, so don't repeat it.
- **General:** plain language, short sentences, no em dashes, no caveats or "verify" notes in the doc. Flags go to Erin in chat.

### 5. Build
Write the JSON to a temp file, then run:
```bash
cd <tmp> && npm install docx --silent
NODE_PATH=<tmp>/node_modules node <skill>/scripts/build_quick_facts.js data.json "<out>.docx"
```
JSON shape. Arrays become bullets, and `{text,url}` items become hyperlinks:
```json
{
  "subtitle": "Charter Amendment PRK (Los Angeles)",
  "prepared": "10.08.26",
  "expertise": "parks and public space in underserved neighborhoods. ...",
  "checks": { "must": [true, true, true, true, true], "disqualify": [false, false, false, false] },
  "facts": {
    "policy": "", "jurisdiction": "", "sponsor": "", "next_decision": "", "deadline": "",
    "summary": "", "mission": ["", ""], "supporters": "", "opposition": ["", ""],
    "partners": "", "risks": ["", ""], "polarizing": "", "conflicts": "",
    "endorsing_means": ["", ""], "time": "", "links": [{"text": "", "url": ""}]
  }
}
```
- `must` has 5 entries: the expertise item first, then the 4 others. `disqualify` has 4.
- For a blank template, pass `{}`.
- Save to the local Board HQ folder as `YYMMDD_Board_[Short-Name]-endorsement-quick-facts.docx`. If Node isn't available, build the same layout with whatever docx tooling the environment has.

### 6. Report in chat
Give a one-line audience note, the filename, the 2-3 findings the board most needs, any open questions (deadline, partner list), and a Sources list with hyperlinks.
