---
name: newsletter-from-transcript
description: "Process Q&A call transcripts into newsletter topic candidates. Use this skill whenever your_name mentions a Q&A transcript, wants newsletter topic ideas, says \"what should I write about this week\", or asks Claude to analyze a call recording. Also use when transcript text is pasted or your_name asks what patterns came up on a call. Even if newsletters aren't mentioned explicitly, trigger this skill whenever your_name is looking for content ideas from a Q&A or coaching call."
---

# Q&A Call Transcript Processor

Extract newsletter topic candidates from weekly Q&A call transcripts. The goal is to find patterns — not individual questions — that reveal a strategic insight worth a full newsletter.

## Step 1: Read the Transcript

Read in full. You need context to distinguish a one-off question from a pattern.

## Step 2: Identify Recurring Themes

Look for topics or problems that come up from multiple members or that the host spends significant time on.

Good themes: 2+ members asking variations of the same problem; the host's answer that reframes the question; a member's before/after story; a counterintuitive answer.

Poor themes: a single technical question with a one-step answer; too-niche topics; topics already covered recently; purely tactical with no strategic insight.

## Step 3: Extract Member Stories

For each theme, find the strongest member story: anonymized name, specific role, clear before-state with numbers, a moment of frustration, a turning point, clear after-state with numbers.

## Step 4: Identify the Strategic Insight

One bold sentence that reframes a common assumption. The test: would someone screenshot it? If not, sharpen it.

## Step 5: Check the Actionable Angle

Every newsletter needs something the reader can do in under 30 minutes: a prompt, checklist, tool setup, framework, or workflow.

## Step 6: Check Against Recent Newsletters

Maintain a small table of recent issues and cross-check each candidate. If a topic overlaps, find a distinct angle or drop it.

| Date | Topic | Core Insight |
|------|-------|--------------|
| YYYY-MM-DD | Recent topic 1 | Core insight 1 |
| YYYY-MM-DD | Recent topic 2 | Core insight 2 |

## Output Format

Recommend 3 topic candidates. For each:

### Topic [#]: [Title]
- The Pattern: what you're seeing across multiple members
- The Member Story: strongest anonymized example with specifics
- The Strategic Insight: one bold reframe sentence
- The Actionable Play: what the reader can do in under 30 min
- Why This Topic: timely, relatable, shareable, fresh?
- Draft Opening Hook: 2-3 sentences

Rank the 3 options and recommend which to pursue first.