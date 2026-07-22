---
name: aa-brand-guidlines
description: "instructions for graphic designs for Architecture + Advocacy. use when asked to create a visual, graphic, or presentation in Architecture + Advocacy (A+A)'s style"
---

# Architecture + Advocacy Brand Styling

This skill defines A+A's visual identity for all graphics, carousels, presentations, posters, and social content. Read this in full before writing a single line of code or design. No exceptions.

**Canonical reference design** — inspect this before designing if anything is unclear:
`https://www.canva.com/design/DAG4igDQd1M/` — "10 Tips from 5 Years of Community-Led Design"

---

## Colors

**Background:**
- Dark Navy `#282739` — always the canvas. Every A+A graphic lives on dark. Never light.

**Text:**
- White `#FFFFFF` — all body text on dark backgrounds. Always fully opaque.
- Mid Gray `#4d4d4d` — body text on light backgrounds only (rare)

**Accent colors (priority order):**
- Salmon `#f5a17d` — primary; always slide 1; all primary headers + CTAs
- Green `#2fa690` — secondary
- Yellow `#f4bf5f` — tertiary
- Orange `#d9642f` — fourth; use sparingly, never for gradient circles

**Accent color rules:**
- Each slide gets ONE accent color, tied to its content category
- That color applies consistently to: header text, eyebrow, bullet dots, accent bar, and one glow circle
- Never rotate arbitrarily — colors carry meaning
- Salmon is always the first slide's accent

---

## Typography

- **Headings**: Public Sans Black, weight 900, white or accent color
- **Eyebrow labels**: Public Sans Regular, weight 400, in the slide's accent color
- **Body / bullets**: Public Sans Light, weight 300, white
- **Sub-notes**: Public Sans Light, weight 300, `rgba(255,255,255,0.45)`
- Load via: `@import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;700;900&display=swap');`
- Arial fallback

**Hard rules:**
- Body text is NEVER italic
- Headers NEVER end with a period
- Headers are NEVER hyphenated across lines — rewrite the copy to fit
- Eyebrow labels are plain case — NOT uppercase, NOT letter-tracked
- Eyebrow labels match the slide's header accent color
- Sub-notes are on their own line inside the bullet, smaller and dimmed — not a separate bullet

---

## Gradient Circles (required on every slide)

Every slide must have exactly TWO gradient glow circles. Erin notices immediately if they are missing.

**Specs:**
- **Bottom-left**: 680px diameter, `bottom: -280px; left: -280px`
- **Top-right**: 560px diameter, `top: -230px; right: -230px`
- Both bleed off canvas, `border-radius: 50%`, `pointer-events: none`, `z-index: 0`
- CSS-only radial gradients — never images

**Color rules:**
- One circle matches the slide's header accent color
- The second circle uses a different accent color — never match both on the same slide
- Colors are salmon, green, or yellow ONLY — never orange (reads too aggressive)
- Opacity: soft. Center ~0.28–0.30, fade to transparent by 70%
- CSS: `radial-gradient(circle, rgba(R,G,B,0.28) 0%, rgba(R,G,B,0.07) 50%, transparent 70%)`

**Standard carousel assignments:**
- Slide 1: salmon (BL) + yellow (TR)
- Slide 2: salmon (BL) + green (TR)
- Slide 3: green (BL) + yellow (TR)
- Slide 4: yellow (BL) + salmon (TR)
- Slide 5: green (BL) + salmon (TR)

---

## Logo

- A+A illustrated + mark, bottom-right corner of every slide footer
- Size: 72x72px, `object-fit: contain`, `opacity: 0.85`
- MUST use transparent-background version
- The original PNG has a black background — remove it by thresholding: pixels with R,G,B < 40 → alpha = 0
- Never use the logo with a black background visible

---

## Layout — Instagram Carousel

**Canvas size**: 1080x1350px (portrait — Instagram standard)
**Padding**: `72px 108px`

**Slide structure (top to bottom):**
1. Slide number — top left, 13px, weight 300, `rgba(255,255,255,0.3)`, tracked
2. Eyebrow label — accent color, weight 400, 17–26px, plain case
3. Section title — weight 900, 72–76px, accent color, no period, no hyphenation
4. Accent bar — 3px tall, 56px wide, accent color, `margin-bottom: 40px`
5. Bullet list — weight 300, 23–25px, white, colored dot + optional sub-note
6. Footer — URL left `rgba(255,255,255,0.25)`, A+A logo right

**Cover slide (Slide 1) specifics:**
- Can use full-bleed photo background with dark overlay `rgba(40,39,57,0.72)`
- Glow circles sit above photo overlay, below text (z-index layering)
- Heading 108px, stacked vertically, accent word in salmon
- Include: eyebrow label, tagline, CTA button (salmon bg), swipe prompt

**Bullet list specs:**
- Colored dot 7px circle, `flex-shrink: 0`, `margin-top: 9px`
- `gap: 18px`, `align-items: flex-start`
- Separator: `1px solid rgba(255,255,255,0.07)`, none on last item
- Sub-notes: `font-size: 20px`, `rgba(255,255,255,0.45)`, nested `<div>` inside `<li>` — NOT a separate bullet

---

## Building + Exporting

**Always build in HTML + CSS. Never use Canva's AI generation tools.**

Canva generation ignores brand style entirely. The correct workflow is:

1. Write HTML/CSS per this skill
2. Embed assets (logo, photos) as base64
3. Export PNGs via Playwright

**Playwright render script:**
```python
from playwright.async_api import async_playwright
import asyncio, os

async def render():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = await browser.new_page(viewport={"width": 1080, "height": 1350})
        await page.goto("file:///mnt/user-data/outputs/aa_carousel.html", wait_until="networkidle")
        await page.evaluate("document.fonts.ready")
        await page.wait_for_timeout(2500)

        os.makedirs("/mnt/user-data/outputs/slides", exist_ok=True)
        slides = await page.query_selector_all('.slide')
        for i, slide in enumerate(slides):
            await slide.scroll_into_view_if_needed()
            await page.wait_for_timeout(200)
            bbox = await slide.bounding_box()
            await page.screenshot(
                path=f"/mnt/user-data/outputs/slides/slide_{i+1:02d}.png",
                clip={"x": bbox["x"], "y": bbox["y"], "width": 1080, "height": 1350}
            )
        await browser.close()

asyncio.run(render())
```

- Always wait for `document.fonts.ready` — Public Sans 900 must load or headings fall back
- Scroll each slide into view before screenshotting or clip coordinates break

---

## Canva API — When It's Useful

The API can edit existing designs but cannot build from scratch.

**Can do:**
- Replace or find-and-replace text in existing elements
- Change text color, size, weight, alignment, line height
- Swap images in existing image slots
- Reposition and resize existing elements

**Cannot do:**
- Set background color
- Create new text boxes
- Set font family
- Place gradient shapes
- Build layout from nothing
- Add or remove pages

Use the API only when Erin wants to edit copy in an already-built Canva template. For everything else, use HTML.

---

## Quick Reference

| Rule | Value |
|------|-------|
| Background | `#282739` always |
| Heading font | Public Sans 900 |
| Body font | Public Sans 300 |
| Canvas size (Instagram) | 1080x1350px |
| Header periods | Never |
| Header hyphenation | Never |
| Eyebrow case | Plain, not uppercase |
| Gradient circles | 2 per slide, required, never matching |
| Glow colors | Salmon, green, yellow only — never orange |
| Logo | Bottom-right, transparent bg, 72px |
| Build tool | HTML + CSS |
| Export tool | Playwright + Chromium |
| Canva AI generation | Never use |
