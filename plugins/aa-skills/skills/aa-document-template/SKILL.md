---
name: aa-document-template
description: >
  Apply A+A branded styling to any Word (.docx) or PDF document created for Architecture + Advocacy.
  Trigger whenever Erin creates, exports, or converts any document for A+A — proposals, reports,
  agendas, one-pagers, briefs, or any other formal output. Also trigger when she says "use the A+A
  template," "brand this," or "make it look like our docs." Always use this skill when the output
  is a .docx or .pdf intended for external or internal A+A use.
---

# A+A Document Template

Apply this styling to every .docx or PDF created for Architecture + Advocacy. Read this in full before writing any code.

---

## Typography

| Style | Font face name (exact) | Size | Color | Notes |
|-------|------------------------|------|-------|-------|
| Body | `Nunito` | 11pt (22 half-pts) | `#36354d` | Default paragraph text |
| H1 | `Public Sans Black` | 19pt (38 half-pts) | `#36354d` | Use exact face name — do NOT use `bold: true` |
| H2 | `Public Sans ExtraLight` | 13pt (26 half-pts) | `#f5a17d` | ALL CAPS always. Exact face name required |
| H3 | `Public Sans ExtraBold` | 12pt (24 half-pts) | `#36354d` | Exact face name required |
| Subtitle/date | `Public Sans` | 11pt (22 half-pts) | `#f5a17d` | Light weight, header block only |
| Org name in header | `Public Sans ExtraLight` | 13pt (26 half-pts) | `#f5a17d` | ALL CAPS |

**Critical:** Font weights must be specified as exact installed face names (`Public Sans Black`, `Public Sans ExtraLight`, `Public Sans ExtraBold`). Never rely on `bold: true` alone — it will not render the correct weight.

---

## First-Page Header

**Layout:** Org name top-left, logo top-right — first page only.

```
[ARCHITECTURE + ADVOCACY]     [logo]
[Document Title — H1]
[Subtitle | DATE]
────────────────────────────────────────
```

**Logo — use floating/anchored image only:**
- File: `/Users/erin/Documents/Cowork Playground/00. Resources/A+A+Logos-03.png`
- Bash path: `/sessions/<session-id>/mnt/Cowork Playground/00. Resources/A+A+Logos-03.png`
- Size: 72×72px
- Position: floating, anchored top-right of page
- **Never** use tab stops or table columns to position the logo — they break in Word

```javascript
new ImageRun({
  type: 'png',
  data: logoData,
  transformation: { width: 72, height: 72 },
  altText: { title: 'A+A Logo', description: 'A+A Logo', name: 'logo' },
  floating: {
    horizontalPosition: {
      relative: HorizontalPositionRelativeFrom.PAGE,
      align: HorizontalPositionAlign.RIGHT,
    },
    verticalPosition: {
      relative: VerticalPositionRelativeFrom.TOP_MARGIN,
      offset: 0,
    },
    allowOverlap: false,
    behindDocument: false,
    wrap: { type: 'none' },
  },
})
```

**Horizontal rule:** Must include a `TextRun('')` child or Word will skip the paragraph entirely.

```javascript
new Paragraph({
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: '36354d', space: 8 } },
  spacing: { before: 120, after: 240 },
  children: [new TextRun('')],  // required — never use children: []
})
```

**Subsequent pages:** no header, no logo.

---

## Page Setup

- **Size:** US Letter (8.5 × 11 in) = 12240 × 15840 twips
- **Margins:** 1 inch all sides = 1440 twips each
- **Content width:** 9360 twips (6.5 inches)

---

## .docx Rules (non-negotiable)

### Never use tables
Tables render unpredictably in Word — columns collapse, text stacks vertically. **Always use a list-based or inline alternative.**

For data that would naturally be a table (labels + descriptions), use bulleted paragraphs with bold inline labels:
```javascript
new Paragraph({
  children: [
    new TextRun({ text: '•  ', font: 'Nunito', size: 22, color: '36354d' }),
    new TextRun({ text: 'Label — ', font: 'Public Sans ExtraBold', size: 22, color: '36354d' }),
    new TextRun({ text: 'Description here', font: 'Nunito', size: 22, color: '36354d' }),
  ],
  indent: { left: 200 },
  spacing: { after: 60 },
})
```

### Never use Word's built-in BULLET renderer
`bullet: { level: 0 }` produces oversized bullets that don't match body font size. Always use inline `•` and `◦` characters with manual indentation:

```javascript
function bullet(children, indent = 0) {
  const prefix = indent === 0 ? '•  ' : '      ◦  ';
  const leftIndent = indent === 0 ? 200 : 500;
  const textChildren = typeof children === 'string'
    ? [new TextRun({ text: prefix + children, font: 'Nunito', size: 22, color: '36354d' })]
    : [new TextRun({ text: prefix, font: 'Nunito', size: 22, color: '36354d' }), ...children];
  return new Paragraph({
    children: textChildren,
    indent: { left: leftIndent },
    spacing: { after: 60 },
  });
}
```

### Numbered / sequential lists — use a real auto-numbered list
For any sequence of items (questions, steps, ranked points), do NOT type "1." / "2." characters manually. Use Word's numbering, but style the number run to match body text (Nunito, 11pt = size 22, color `36354d`) so it does not render oversized. Give each independent list its own `reference` so numbering restarts at 1.

```javascript
const { LevelFormat, AlignmentType } = require('docx');

// One config per independent list (restarts numbering):
function numCfg(ref) {
  return {
    reference: ref,
    levels: [{
      level: 0,
      format: LevelFormat.DECIMAL,
      text: '%1.',
      alignment: AlignmentType.START,
      style: {
        run: { font: 'Nunito', size: 22, color: '36354d' },
        paragraph: { indent: { left: 460, hanging: 260 } },
      },
    }],
  };
}

// Register on the Document:
// new Document({ numbering: { config: [numCfg('listA'), numCfg('listB')] }, sections: [...] })

function numItem(ref, text) {
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    children: [new TextRun({ text, font: 'Nunito', size: 22, color: '36354d' })],
    spacing: { after: 70 },
  });
}
```

### Always preserve hyperlinks
Never drop links when converting content to docx. Use `ExternalHyperlink`:

```javascript
function link(text, url) {
  return new ExternalHyperlink({
    link: url,
    children: [new TextRun({ text, font: 'Nunito', size: 22, color: '0563C1', underline: {} })],
  });
}

// Mix into a paragraph alongside other text:
new Paragraph({
  children: [
    new TextRun({ text: '•  See ', font: 'Nunito', size: 22, color: '36354d' }),
    link('source', 'https://example.com'),
    new TextRun({ text: ' for details.', font: 'Nunito', size: 22, color: '36354d' }),
  ],
  indent: { left: 200 },
  spacing: { after: 60 },
})
```

---

## Implementation: .docx (Node.js docx library)

Install: `npm install docx` in /tmp.

```javascript
const {
  Document, Packer, Paragraph, TextRun, ImageRun, ExternalHyperlink,
  AlignmentType, BorderStyle,
  HorizontalPositionRelativeFrom, HorizontalPositionAlign,
  VerticalPositionRelativeFrom,
} = require('/tmp/node_modules/docx');
const fs = require('fs');

const COLORS = { dark: '36354d', salmon: 'f5a17d' };

function h1(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: 'Public Sans Black', size: 38, color: COLORS.dark })],
    spacing: { before: 280, after: 100 },
  });
}

function h2(text) {
  return new Paragraph({
    children: [new TextRun({ text: text.toUpperCase(), font: 'Public Sans ExtraLight', size: 26, color: COLORS.salmon })],
    spacing: { before: 260, after: 60 },
  });
}

function h3(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: 'Public Sans ExtraBold', size: 24, color: COLORS.dark })],
    spacing: { before: 200, after: 60 },
  });
}

function body(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, font: 'Nunito', size: 22, color: COLORS.dark, ...opts })],
    spacing: { after: 80 },
  });
}

function bullet(children, indent = 0) {
  const prefix = indent === 0 ? '•  ' : '      ◦  ';
  const leftIndent = indent === 0 ? 200 : 500;
  const textChildren = typeof children === 'string'
    ? [new TextRun({ text: prefix + children, font: 'Nunito', size: 22, color: COLORS.dark })]
    : [new TextRun({ text: prefix, font: 'Nunito', size: 22, color: COLORS.dark }), ...children];
  return new Paragraph({ children: textChildren, indent: { left: leftIndent }, spacing: { after: 60 } });
}

function link(text, url) {
  return new ExternalHyperlink({
    link: url,
    children: [new TextRun({ text, font: 'Nunito', size: 22, color: '0563C1', underline: {} })],
  });
}

function rule() {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: COLORS.dark, space: 8 } },
    spacing: { before: 120, after: 240 },
    children: [new TextRun('')],
  });
}

function blank() {
  return new Paragraph({ children: [new TextRun('')], spacing: { after: 80 } });
}
```

---

## Implementation: PDF (HTML → Playwright)

```html
<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@200;300;400;800;900&family=Nunito:wght@400&display=swap');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Nunito', Arial, sans-serif; font-size: 11pt; color: #36354d; padding: 1in; max-width: 8.5in; }
  .doc-header { display: flex; justify-content: space-between; align-items: flex-start; }
  .org-name { font-family: 'Public Sans'; font-weight: 200; font-size: 13pt; color: #f5a17d; text-transform: uppercase; }
  .doc-title { font-family: 'Public Sans'; font-weight: 900; font-size: 19pt; color: #36354d; }
  .doc-subtitle { font-family: 'Public Sans'; font-weight: 300; font-size: 11pt; color: #f5a17d; }
  .doc-logo { height: 64px; }
  .doc-rule { border: none; border-top: 0.5pt solid #36354d; margin: 12px 0 24px 0; }
  h1 { font-family: 'Public Sans'; font-weight: 900; font-size: 19pt; color: #36354d; margin: 20px 0 6px; }
  h2 { font-family: 'Public Sans'; font-weight: 200; font-size: 13pt; color: #f5a17d; text-transform: uppercase; margin: 18px 0 4px; }
  h3 { font-family: 'Public Sans'; font-weight: 800; font-size: 12pt; color: #36354d; margin: 14px 0 4px; }
  p { margin-bottom: 10px; line-height: 1.5; }
  ul { margin: 6px 0 10px 20px; } li { margin-bottom: 4px; line-height: 1.5; }
</style></head><body>
<div class="doc-header">
  <div><div class="org-name">Architecture + Advocacy</div>
  <div class="doc-title">DOCUMENT TITLE</div>
  <div class="doc-subtitle">Context | PREPARED MM.DD.YY</div></div>
  <img class="doc-logo" src="LOGO_BASE64" alt="A+A Logo">
</div>
<hr class="doc-rule">
<!-- body here -->
</body></html>
```

Set Playwright PDF margins to 0 — margins are handled by `padding: 1in` on body.

---

## Workflow

1. Gather document content
2. Identify: title, subtitle/context, date
3. Choose format (.docx or .pdf)
4. Build using helpers above — no tables, no Word bullet renderer, preserve all hyperlinks
5. Save to source folder: `YYMMDD_A+A_descriptive-name.docx/.pdf`
6. Present via `mcp__cowork__present_files`
