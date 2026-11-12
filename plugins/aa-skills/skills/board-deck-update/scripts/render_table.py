"""Render the visible (unfiltered) rows of a Google Sheet as a PNG table.
grid.json = `gws sheets spreadsheets get` with includeGridData + fields for rowMetadata,
columnMetadata, formattedValue, effectiveFormat. Usage: python render_table.py grid.json out.png NROWS NCOLS"""
import json, sys
from PIL import Image, ImageDraw, ImageFont
grid, out, nrows, ncols = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
d = json.load(open(grid))['sheets'][0]['data'][0]
S = 2.0
import os
_C = [('/System/Library/Fonts/Supplemental/Arial.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'),
      ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')]
FONT, FONTB = next((c for c in _C if os.path.exists(c[0])), (None, None))
def font(sz, b):
    if not FONT: return ImageFont.load_default(size=int(sz * 1.333 * S))
    return ImageFont.truetype(FONTB if b else FONT, int(sz * 1.333 * S))
colw = [int(c.get('pixelSize', 100) * 1.0 * S) for c in d['columnMetadata'][:ncols]]
rows = [i for i, m in enumerate(d['rowMetadata']) if not (m.get('hiddenByFilter') or m.get('hiddenByUser'))][:nrows + 1]
STATUS = {'Pending': (150, 110, 0), 'Awarded': (40, 120, 50), 'Lost': (190, 30, 30)}
pad = int(4 * S)
def wrap(text, f, w):
    lines = []
    for para in text.split('\n'):
        words, cur = para.split(), ''
        for wd in words:
            t = (cur + ' ' + wd).strip()
            if f.getlength(t) <= w - 2 * pad or not cur: cur = t
            else: lines.append(cur); cur = wd
        lines.append(cur)
    return lines
cells, heights = [], []
for ri in rows:
    vals = d['rowData'][ri].get('values', [])
    rc, h = [], int(21 * 1.35 * S)
    for ci in range(ncols):
        c = vals[ci] if ci < len(vals) else {}
        txt = ' '.join(c.get('formattedValue', '').split()) if ri == 0 else c.get('formattedValue', '')
        ef = c.get('effectiveFormat', {}); tf = ef.get('textFormat', {})
        f = font(tf.get('fontSize', 10), tf.get('bold', False))
        lines = wrap(txt, f, colw[ci]) if txt else []
        lh = int(f.size * 1.2)
        h = max(h, len(lines) * lh + 2 * pad)
        bg = ef.get('backgroundColor', {})
        rc.append(dict(lines=lines, f=f, lh=lh, ul=tf.get('underline', False),
            bg=tuple(int(bg.get(k, 1 if not bg else 0) * 255) for k in ('red', 'green', 'blue')) if bg else (255, 255, 255),
            al=ef.get('horizontalAlignment') or ('RIGHT' if txt[:1].isdigit() else 'LEFT'), txt=txt, ci=ci, ri=ri))
    cells.append(rc); heights.append(h)
W, H = sum(colw), sum(heights)
img = Image.new('RGB', (W, H), 'white'); dr = ImageDraw.Draw(img)
y = 0
for rc, h in zip(cells, heights):
    x = 0
    for c, w in zip(rc, colw):
        bg = c['bg']
        if c['ci'] == 0 and c['ri'] > 0:  # status chip column: slightly deeper tint
            bg = tuple(max(0, v - 12) for v in bg)
        dr.rectangle([x, y, x + w, y + h], fill=bg, outline=(200, 200, 200))
        color = STATUS.get(c['txt'], (0, 0, 0)) if c['ci'] == 0 and c['ri'] > 0 else (0, 0, 0)
        ty = y + h - pad - len(c['lines']) * c['lh']
        for ln in c['lines']:
            tw = c['f'].getlength(ln)
            tx = x + pad if c['al'] == 'LEFT' else (x + w - pad - tw if c['al'] == 'RIGHT' else x + (w - tw) / 2)
            dr.text((tx, ty), ln, font=c['f'], fill=color)
            if c['ul']: dr.line([tx, ty + c['f'].size + 2, tx + tw, ty + c['f'].size + 2], fill=color, width=max(1, int(S)))
            ty += c['lh']
        x += w
    y += h
img.save(out); print(out, img.size)
