// Build A+A's Policy Endorsement Quick Facts .docx from a JSON file.
// Usage: NODE_PATH=<dir with node_modules> node build_quick_facts.js <data.json> <out.docx>
// Omit "facts" (or leave values empty) to produce the blank template.
const path = require('path');
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, BorderStyle, ExternalHyperlink,
  Table, TableRow, TableCell, WidthType, TableLayoutType, ShadingType, HeightRule, VerticalAlign,
  HorizontalPositionRelativeFrom, HorizontalPositionAlign, VerticalPositionRelativeFrom,
} = require('docx');

const [, , dataPath, outPath] = process.argv;
const data = dataPath ? JSON.parse(fs.readFileSync(dataPath, 'utf8')) : {};
const logo = fs.readFileSync(path.join(__dirname, '..', 'assets', 'logo.png'));

const C = { dark: '36354d', salmon: 'f5a17d' };
const run = (text, font = 'Nunito', extra = {}) => new TextRun({ text, font, size: 22, color: C.dark, ...extra });
const link = (text, url) => new ExternalHyperlink({ link: url, children: [new TextRun({ text, font: 'Nunito', size: 22, color: '0563C1', underline: {} })] });

const h2 = text => new Paragraph({
  children: [new TextRun({ text: text.toUpperCase(), font: 'Public Sans ExtraLight', size: 26, color: C.salmon })],
  spacing: { before: 300, after: 100 },
});
const rule = () => new Paragraph({
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: C.dark, space: 8 } },
  spacing: { before: 120, after: 240 },
  children: [new TextRun('')],
});
const check = (on, children) => new Paragraph({
  children: [run(on ? '☒  ' : '☐  '), ...children],
  indent: { left: 200 },
  spacing: { after: 80 },
});

// Value cell content. A string -> one paragraph. An array -> one inline-bullet
// paragraph per item. Items may be strings or {text, url} links.
function cellParas(value) {
  if (value == null || value === '') return [new Paragraph({ children: [run('')] })];
  const items = Array.isArray(value) ? value : [value];
  const bulleted = Array.isArray(value) && value.length > 1;
  return items.map(it => {
    const body = typeof it === 'string' ? run(it) : link(it.text, it.url);
    return new Paragraph({
      children: bulleted ? [run('•  '), body] : [body],
      indent: bulleted ? { left: 240, hanging: 240 } : undefined,
      spacing: { after: 60 },
    });
  });
}

const LINE = { style: BorderStyle.SINGLE, size: 4, color: C.dark };
const borders = { top: LINE, bottom: LINE, left: LINE, right: LINE };
const margins = { top: 80, bottom: 80, left: 120, right: 120 };
function row(label, hint, tall, value) {
  const labelKids = [new Paragraph({ children: [run(label, 'Public Sans ExtraBold')] })];
  if (hint) labelKids.push(new Paragraph({ children: [run(hint, 'Nunito', { color: '6b6a7d', size: 18 })] }));
  return new TableRow({
    cantSplit: true,
    height: tall ? { value: 900, rule: HeightRule.ATLEAST } : undefined,
    children: [
      new TableCell({ width: { size: 3200, type: WidthType.DXA }, borders, margins, verticalAlign: VerticalAlign.TOP,
        shading: { type: ShadingType.CLEAR, color: 'auto', fill: 'F2F2F2' }, children: labelKids }),
      new TableCell({ width: { size: 6160, type: WidthType.DXA }, borders, margins, verticalAlign: VerticalAlign.TOP,
        children: cellParas(value) }),
    ],
  });
}

// [key, label, hint, tall]
const FIELDS = [
  ['policy', 'Policy name / ID'],
  ['jurisdiction', 'Jurisdiction', 'City / county / state / federal'],
  ['sponsor', 'Sponsor or lead org'],
  ['next_decision', 'Next decision date / description'],
  ['deadline', 'Endorsement deadline'],
  ['summary', 'One-sentence summary', null, true],
  ['mission', 'Connection to mission', null, true],
  ['supporters', 'Main supporters'],
  ['opposition', 'Known opposition'],
  ['partners', 'A+A partners who support', 'If any'],
  ['risks', 'Reasons to say no / risks', null, true],
  ['polarizing', 'Is this a polarizing topic? How so?', null, true],
  ['conflicts', 'Conflicts of interest', 'Board / staff / funders / partners'],
  ['endorsing_means', 'What endorsing means here', 'Sign-on letter / public comment / testimony / social posts / events'],
  ['time', 'Staff and volunteer time needed'],
  ['links', 'Links to more resources', null, true],
];

const MUST = [
  "Align with A+A's mission",
  'Call for a specific, actionable change',
  'Have no conflict of interest with board members, staff, funders, or partners',
  'Not drive away current or potential partners',
];
const DQ = [
  'The policy or recommendation is a good idea, but falls flat in the details',
  'Risk of doing harm to the communities we work with',
  'Limits community power in land use',
  'Endorses a specific candidate (not allowed for a 501(c)(3))',
];
const checks = data.checks || {};
const must = checks.must || [];
const dq = checks.disqualify || [];
const facts = data.facts || {};
const subtitle = data.subtitle || 'Board decision tool';
const prepared = data.prepared || '';

const children = [
  new Paragraph({
    children: [
      new TextRun({ text: 'ARCHITECTURE + ADVOCACY', font: 'Public Sans ExtraLight', size: 26, color: C.salmon }),
      new ImageRun({
        type: 'png', data: logo,
        transformation: { width: 72, height: 72 },
        altText: { title: 'A+A Logo', description: 'A+A Logo', name: 'logo' },
        floating: {
          horizontalPosition: { relative: HorizontalPositionRelativeFrom.MARGIN, align: HorizontalPositionAlign.RIGHT },
          verticalPosition: { relative: VerticalPositionRelativeFrom.TOP_MARGIN, offset: 0 },
          allowOverlap: false, behindDocument: false, wrap: { type: 'none' },
        },
      }),
    ],
  }),
  new Paragraph({
    children: [new TextRun({ text: 'Policy Endorsement Quick Facts', font: 'Public Sans Black', size: 38, color: C.dark })],
    spacing: { before: 120, after: 60 },
  }),
  new Paragraph({
    children: [new TextRun({ text: subtitle + (prepared ? ` | PREPARED ${prepared}` : ''), font: 'Public Sans', size: 22, color: C.salmon })],
  }),
  rule(),

  h2('An endorsement or statement must'),
  check(must[0], [run("Address an issue within A+A's expertise: "),
    data.expertise ? run(data.expertise, 'Nunito', { underline: {} }) : run('_______________________________')]),
  ...MUST.map((t, i) => check(must[i + 1], [run(t)])),

  h2('Automatic disqualifications'),
  ...DQ.map((t, i) => check(dq[i], [run(t)])),

  h2('A note on lobbying limits'),
  new Paragraph({
    children: [run('501(c)(3) nonprofits can attempt to influence legislation related to their tax-exempt purpose, but lobbying must not be a "substantial" amount of either their time or expenses, or they can lose 501(c)(3) status. By default, "substantial" has no clear definition. Nonprofits that plan to lobby in amounts that take time or resources should consider filing the 501(h) election, which sets specific lobbying limits on a sliding scale based on the organization\'s annual exempt-purpose expenditures (e.g., 20% of the first $500,000, capped at $1,000,000 total).')],
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: C.salmon, space: 10 } },
    indent: { left: 240 },
    spacing: { after: 120, line: 300 },
  }),

  new Paragraph({ pageBreakBefore: true, children: [new TextRun({ text: 'Quick Facts', font: 'Public Sans Black', size: 38, color: C.dark })], spacing: { after: 60 } }),
  rule(),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3200, 6160],
    layout: TableLayoutType.FIXED,
    rows: FIELDS.map(([k, label, hint, tall]) => row(label, hint, !!tall, facts[k])),
  }),
];

const doc = new Document({
  styles: { default: { document: { run: { font: 'Nunito', size: 22, color: C.dark } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children,
  }],
});

Packer.toBuffer(doc).then(b => { fs.writeFileSync(outPath, b); console.log('saved', outPath); });
