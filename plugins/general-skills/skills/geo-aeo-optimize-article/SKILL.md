---
name: geo-aeo-optimize-article
description: "Convert a YouTube transcript, blog post, podcast transcript, or pasted text into a long-form article optimized for GEO (Generative Engine Optimization) and AEO (Answer Engine Optimization). Use this skill whenever your_name says /article, asks to \"turn this into an article,\" wants to repurpose a video or transcript into a citation-friendly post, or asks how to write content that ChatGPT, Claude, or Perplexity will cite. Output saves to output_folder as a dated markdown file in your_name's voice."
---

---

# /article — Source → GEO + AEO-optimized article

This skill takes a piece of source content (YouTube video, blog post, podcast transcript, or pasted text) and produces a long-form article structured to get cited by AI search engines (ChatGPT, Claude, Perplexity, Gemini, Google AI Overviews).

The job is not to summarize the source. It's to restructure it into the shape AI engines extract from.

## Workflow

### 1. Identify the input

| Input shape | How to get the source text |
|---|---|
| YouTube URL | Hand off to a `/watch` skill (or transcript tool) to pull the transcript |
| Blog post URL | Use `WebFetch` to retrieve the article body |
| File path ending in `.md`, `.txt`, `.vtt`, `.srt` | `Read` the file. Strip timestamps and speaker tags from `.vtt`/`.srt` |
| Pasted transcript text | Use directly |

If ambiguous, ask one clarifying question.

### 2. Read the source and pick the core question

Read in full. Decide: what single question does this article answer? Everything ladders up to it. If the source covers four big ideas, pick the strongest and note that choice so the user can redirect.

### 3. Draft the Answer Block first

Write a 40-60 word Answer Block that directly answers the core question. It sits in the first 100 words of the article. This is the single highest-leverage element for getting cited. If you can't write it tight, your core question is wrong.

### 4. Outline question-format H2s

Each H2 should be a question a real person would type into ChatGPT or Google. Each section's first 1-2 sentences answer its heading directly.

### 5. Draft the sections

- Claim-level reuse: every non-obvious claim sits in a self-contained paragraph with measurement, scope, and source named in the same chunk.
- Evidence density: specific numbers, named examples, direct quotes.
- Short paragraphs (2-4 sentences). Long paragraphs get skipped by extraction.
- Concrete nouns in headings.
- Don't invent facts. The article is a transformation of the source.

### 6. Add Key Takeaways and FAQ

- Key Takeaways: 3-5 bullets right under the Answer Block, each a distinct claim.
- FAQ: 4-6 question/answer pairs at the end. Questions must be net-new (edge cases, platform variants, what-ifs), not restatements of H2s. Maps to FAQPage schema.

### 7. Add 3-5 outbound citations

Link to specific articles (never homepages), authoritative sources only, inline at the claim. 3-5 total.

### 8. Length-and-density pass

Length follows substance. Targets are ceilings, not floors:
- Standard how-to (1-3 claims): 1,000-1,500 words
- Listicle (5-10 items): 1,500-2,200 words
- Deep explainer: 1,800-2,500 words

Cut: section openers that restate the heading, redundant summaries, callbacks ("as I mentioned"), padding hedging, recaps that list every rule again.

### 9. Voice pass

Replace the rules below with your own voice notes. Examples:
- No em-dashes — use periods, commas, or restructure
- No jargon for non-technical audience
- Conversational rhythm, short paragraphs, first-person where source allows
- Lead with WHAT, not how
- One emoji max (often zero)
- No observer phrases if writing for your own community

### 10. Write the file

Save to `output_folder/YYYY-MM-DD-{slug}.md`. `{slug}` is kebab-case, max ~6 words. Frontmatter must include: title, slug, author, published, updated, source_type, source_url (if applicable), faq (mirroring the FAQ), schema_types.

After writing, print the saved path and a one-sentence summary.

## References

- `references/geo-aeo-playbook.md` — deeper context on why each structural element works, platform-specific behavior, freshness window, Princeton GEO research.
- `references/article-template.md` — the literal markdown skeleton. Open every run.

## Judgment note

The 10 structural elements (Answer Block, question H2s, claim-level reuse, evidence density, outbound citations, FAQ, Key Takeaways, freshness dates, schema-friendly frontmatter, named author) aren't a checklist. If a source doesn't lend itself to one element, drop it and lean harder on the ones that fit.