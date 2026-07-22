import openpyxl, re, math, random, json
from collections import defaultdict
random.seed(7)

# =====================================================================
# CONFIG -- fill this in fresh for every new spreadsheet. Everything
# below this block is generic layout/rendering logic that should not
# need to change. See SKILL.md step 0 for how to derive these values
# from a conversation with the user -- never guess silently.
# =====================================================================

SOURCE_XLSX = "/path/to/source.xlsx"   # absolute path to the uploaded workbook
SHEET_NAME  = "Sheet1"                 # exact sheet/tab name
HEADER_ROW  = 1                        # 1-indexed row containing column headers (data starts next row)

# 0-indexed column positions (A=0, B=1, C=2, ...). Confirm these with the
# user first -- do not assume column letters carry over between spreadsheets.
COL_NAME     = 0   # organization name -> becomes the square's label
COL_CATEGORY = 2   # category / grouping column -> determines which circle(s)
COL_PARTNERS = 3   # "notable partners" style column -> curved connector lines
COL_PARENT   = 4   # parent-org column -> curved connector lines
COL_PROJ_LEAD = 5  # "project lead" column (optional; set to None if unused)
COL_PROJ_PART = 6  # "project participant" column (optional; set to None if unused)
COL_BUDGET   = 7   # sizing metric (budget, headcount, etc.) -> square size, log scale

# Raw category string (lowercased, quote-normalized) -> canonical category name.
# The canonical name must exactly match a key in CIRCLES below.
# Map any category you want dropped entirely to 'IGNORE'.
# Map any category you want folded into another to that other category's name.
CATEGORY_ALIASES = {
    'institutional nonprofit': 'Institutional nonprofit',
    'funder': 'Funder',
    'designers who get it': 'Designers who get it',
    "architects that get it": 'Architects that get it',
    "planners that get it": 'Planners that get it',
    'planners': 'Planners',
    'architects': 'Architects',
    'grassroots nonprofits': 'Grassroots nonprofits',
    'youth education': 'Youth education',
    'advocacy': 'Advocacy',
    'government': 'Government',
    'adversaries': 'Adversaries',
    'performance/arts group': 'IGNORE',
}

# Known misspellings/variants of an org's own name as it appears in
# Partners/Parent columns elsewhere in the sheet -> the exact Column-A name.
# Populate this AFTER the first dry run shows you the "DROPPED" list.
MANUAL_ALIASES = {
    # 'typo or variant name': 'Exact Organization Name From Column A',
}

# Merge duplicate rows for the same org (same Column-A name appearing twice).
# By default the loader silently skips duplicates, keeping the first-seen row.
# Add name-specific merge rules here only if you need one row's data (e.g. a
# partner reference) to win over another's.
DUPLICATE_MERGE_RULES = {
    # 'Org Name': lambda existing, new_partners: new_partners if '<signal>' in str(new_partners) else existing['partners_raw'],
}

OUTPUT_SVG_PATH = "/path/to/output/YYMMDD_project_descriptive-name.svg"
CAPTION_TEXT = "Organization — Stakeholder Map — square size = <metric> (log scale) — curved lines = notable partners & parent orgs — dashed lines = shared projects (clustered by category)"

wb = openpyxl.load_workbook(SOURCE_XLSX, data_only=True)
ws = wb[SHEET_NAME]
rows = list(ws.iter_rows(min_row=HEADER_ROW+1, values_only=True))

# ---- category normalization ----
def norm_cat_token(t):
    t = t.strip().strip('"').strip('\u201c').strip('\u201d').lower()
    t = t.replace('\u2019', "'")
    mapping = CATEGORY_ALIASES
    if t in mapping:
        return mapping[t]
    for k,v in mapping.items():
        if k in t or t in k:
            return v
    return t.title()

def resolve_categories(catstr):
    if not catstr:
        return []
    parts = [p.strip() for p in catstr.split(',')]
    out = []
    for p in parts:
        c = norm_cat_token(p)
        if c not in out:
            out.append(c)
    return out

# ---- budget parsing ----
def parse_budget(s):
    if not s:
        return 100000.0
    s = str(s)
    su = s.upper()
    if 'N/A' in su:
        return 50000.0
    nums = re.findall(r'\$?\s*([\d,.]+)\s*([MK]?)', s)
    vals = []
    for num, suf in nums:
        num = num.replace(',', '')
        if num in ('', '.'):
            continue
        try:
            v = float(num)
        except ValueError:
            continue
        if suf == 'M':
            v *= 1_000_000
        elif suf == 'K':
            v *= 1_000
        vals.append(v)
    if not vals:
        return 100000.0
    if len(vals) >= 2 and ('-' in s or 'to' in s.lower()):
        return sum(vals[:2]) / 2
    return vals[0]

# ---- load orgs ----
orgs = {}
order = []
for r in rows:
    name = r[COL_NAME]
    if not name:
        continue
    cat = r[COL_CATEGORY]
    partners = r[COL_PARTNERS]
    parent = r[COL_PARENT]
    lead = r[COL_PROJ_LEAD] if COL_PROJ_LEAD is not None else None
    part = r[COL_PROJ_PART] if COL_PROJ_PART is not None else None
    budget = r[COL_BUDGET]
    cats = resolve_categories(cat)
    if 'IGNORE' in cats:
        continue
    if name in orgs:
        existing = orgs[name]
        if name in DUPLICATE_MERGE_RULES:
            existing['partners_raw'] = DUPLICATE_MERGE_RULES[name](existing, partners)
        continue
    orgs[name] = {
        'name': name,
        'categories': cats,
        'partners_raw': partners,
        'parent_raw': parent,
        'lead_raw': lead,
        'part_raw': part,
        'budget': parse_budget(budget),
    }
    order.append(name)

print("Total orgs included:", len(orgs))

# ---- name matching for partners/parents ----
def _norm(s):
    s = re.sub(r'\([^)]*\)', '', s)
    s = re.sub(r'[^a-z0-9 ]', '', s.lower())
    s = re.sub(r'\s+', ' ', s).strip()
    return s

name_lookup = {n.lower().strip(): n for n in orgs}
norm_lookup = {}
for n in orgs:
    norm_lookup.setdefault(_norm(n), n)

MANUAL_ALIASES = {
    'nyc good neighborhood committee': 'New York City Good Neighbor Committee (Ford Foundation)',
    'municipal art society of ny': 'Municipal Art Society of New York (MAS)',
}

def match_name(raw):
    raw = raw.strip()
    key = raw.lower()
    if key in name_lookup:
        return name_lookup[key]
    nk = _norm(raw)
    if nk in norm_lookup:
        return norm_lookup[nk]
    if nk in MANUAL_ALIASES:
        return MANUAL_ALIASES[nk]
    return None

# ---- partner / parent edges (curved lines) ----
rel_edges = []  # (a, b, kind)  kind in {partner, parent}
dropped_partners = []

for name, o in orgs.items():
    if o['partners_raw']:
        for p in str(o['partners_raw']).split(','):
            p = p.strip()
            if not p or p.lower() == 'none':
                continue
            m = match_name(p)
            if m and m != name:
                rel_edges.append((name, m, 'partner'))
            else:
                dropped_partners.append((name, p))
    if o['parent_raw']:
        for p in str(o['parent_raw']).split(','):
            p = p.strip()
            if not p:
                continue
            m = match_name(p)
            if m and m != name:
                rel_edges.append((name, m, 'parent'))
            else:
                dropped_partners.append((name+' [parent]', p))

seen = set()
final_rel_edges = []
for a,b,k in rel_edges:
    key = tuple(sorted([a,b]))
    if key in seen:
        continue
    seen.add(key)
    final_rel_edges.append((a,b,k))

print("Partner/parent edges:", len(final_rel_edges))
print("Dropped/unmatched refs:", len(dropped_partners))
for d in dropped_partners:
    print("  DROPPED:", d)

# ============ LAYOUT ============
SCALE = 1.4
CIRCLES = {
    'Institutional nonprofit':   dict(cx=650,  cy=480, r=300, color='#f5a17d', parent=None),
    'Funder':                    dict(cx=280,  cy=560, r=220, color='#2fa690', parent=None),
    'Designers who get it':      dict(cx=1270, cy=440, r=320, color='#f4bf5f', parent=None),
    'Architects that get it':    dict(cx=1160, cy=340, r=78,  color='#c99b4c', parent='Designers who get it'),
    'Planners that get it':      dict(cx=1400, cy=330, r=78,  color='#f8d491', parent='Designers who get it'),
    'Planners':                  dict(cx=1580, cy=500, r=115, color='#d9642f', parent=None),
    'Grassroots nonprofits':     dict(cx=1340, cy=970, r=430, color='#c97a5f', parent=None),
    'Youth education':           dict(cx=1000, cy=170, r=105, color='#6fd0bd', parent=None),
    'Advocacy':                  dict(cx=830,  cy=790, r=230, color='#e8926a', parent=None),
    'Government':                dict(cx=480,  cy=820, r=260, color='#1f7a68', parent=None),
}
for _c in CIRCLES.values():
    _c['cx'] *= SCALE; _c['cy'] *= SCALE; _c['r'] *= SCALE

def dist(x1,y1,x2,y2):
    return math.hypot(x1-x2, y1-y2)

def in_circle(x,y,c):
    return dist(x,y,c['cx'],c['cy']) <= c['r']*0.92

GOLDEN_ANGLE = 2.399963

def related_circles(cats):
    """A category's own circle, its parent (if it's a nested sub-group), and its
    children (if it HAS nested sub-groups) all count as 'the same territory' --
    not a crossover. Everything else is foreign territory."""
    rel = set()
    for cat in cats:
        if cat not in CIRCLES:
            continue
        rel.add(cat)
        p = CIRCLES[cat]['parent']
        if p:
            rel.add(p)
        for k, v in CIRCLES.items():
            if v['parent'] == cat:
                rel.add(k)
    return rel

def crosses_foreign_circle(x, y, cats):
    """True if (x,y) falls inside a circle that ISN'T part of this org's own
    category territory -- i.e. a real crossover into someone else's section."""
    allowed = related_circles(cats)
    for key, c in CIRCLES.items():
        if key in allowed:
            continue
        if in_circle(x, y, c):
            return True
    return False

def spiral_free_spot(cx, cy, side, max_radius=None, min_y=None, seed_angle=0.0, step=5.0, own_cats=None):
    """Vogel/Fermat spiral search outward from (cx,cy). Never gives up: keeps
    expanding until it finds a truly collision-free spot, so squares never overlap.
    If own_cats is given, also refuses any spot that crosses into a foreign
    category's circle (single-category orgs should never land in a crossover zone).
    Returns (x, y, r) so callers can tell how far outside the nominal circle it had to go."""
    angle = seed_angle
    r = 0.0
    for i in range(20000):
        x = cx + r*math.cos(angle)
        y = cy + r*math.sin(angle)
        ok = (min_y is None or y >= min_y) and not collides(x,y,side)
        if ok and own_cats is not None:
            ok = not crosses_foreign_circle(x, y, own_cats)
        if ok:
            return x, y, r
        angle += GOLDEN_ANGLE
        r += step
    return cx, cy, r  # should never hit this with 20000 steps

def sample_in_circle(c, avoid_top=True, radius_scale=0.82):
    for _ in range(200):
        ang = random.uniform(0, 2*math.pi)
        rad = c['r']*radius_scale*math.sqrt(random.uniform(0.05,1))
        x = c['cx'] + rad*math.cos(ang)
        y = c['cy'] + rad*math.sin(ang)
        top_clear = 0.55 if c['parent'] else 0.80
        if avoid_top and y < c['cy'] - c['r']*top_clear:
            continue
        return x,y
    return c['cx'], c['cy']

def sample_overlap(c1, c2):
    for _ in range(400):
        x,y = sample_in_circle(c1, avoid_top=False)
        if in_circle(x,y,c2):
            return x,y
    return (c1['cx']+c2['cx'])/2, (c1['cy']+c2['cy'])/2

# ---- budget -> square size (log scale), WIDER range per Erin's feedback ----
budgets = [o['budget'] for o in orgs.values()]
lo, hi = math.log10(min(budgets)), math.log10(max(budgets))
MIN_SIDE, MAX_SIDE = 14, 95
MIN_FONT, MAX_FONT = 8, 17

def side_for(b):
    t = (math.log10(b)-lo)/(hi-lo) if hi>lo else 0.5
    return MIN_SIDE + t*(MAX_SIDE-MIN_SIDE)

def font_for(side):
    t = (side-MIN_SIDE)/(MAX_SIDE-MIN_SIDE) if MAX_SIDE>MIN_SIDE else 0
    return max(MIN_FONT, min(MAX_FONT, MIN_FONT + t*(MAX_FONT-MIN_FONT)))

def wrap_label(name, max_chars=13, max_lines=3):
    words = name.replace('(', ' (').split(' ')
    lines = []
    cur = ''
    for w in words:
        if not w:
            continue
        trial = (cur + ' ' + w).strip()
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
        if len(lines) >= max_lines:
            break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    return lines[:max_lines]

def footprint(name, side):
    fsize = font_for(side)
    # bigger squares get roomier char-width wrap so text doesn't get absurdly narrow
    max_chars = max(10, int(side/6))
    lines = wrap_label(name, max_chars=max_chars)
    max_line_w = max((len(l) for l in lines), default=1) * fsize * 0.6
    box_w = max(side, max_line_w + 10)
    box_h = max(side, len(lines) * (fsize+3) + 8)
    return max(box_w, box_h), lines, fsize

placed = []  # (name, x, y, footprint)

def collides(x,y,s, exclude=None):
    # s is the square footprint (>= both real box_w and box_h), so requiring
    # the FULL combined half-width as clearance (plus a small gap) guarantees
    # the real (usually smaller, rectangular) boxes never actually overlap.
    hw = s/2
    for (n2,x2,y2,s2) in placed:
        if exclude and n2 == exclude:
            continue
        hw2 = s2/2
        if abs(x-x2) < (hw+hw2)+3 and abs(y-y2) < (hw+hw2)+3:
            return True
    return False

def place_free(cats, side):
    resolved_cats = [c for c in cats if c in CIRCLES]
    if len(resolved_cats) == 0:
        x,y,r = spiral_free_spot(950, 700, side, seed_angle=random.uniform(0,6.28))
        return x, y, {}
    elif len(resolved_cats) == 1:
        c = CIRCLES[resolved_cats[0]]
        top_clear = 0.55 if c['parent'] else 0.80
        min_y = c['cy'] - c['r']*top_clear
        x,y,r = spiral_free_spot(c['cx'], c['cy'], side, min_y=min_y, seed_angle=random.uniform(0,6.28),
                                  own_cats=resolved_cats)
        return x, y, {resolved_cats[0]: r}
    else:
        # if a category is a nested sub-group, use its PARENT circle for the
        # intersection test -- the sub-circle may not geometrically reach the
        # other category's circle even though the parent does.
        def effective(cat):
            p = CIRCLES[cat]['parent']
            return p if p else cat
        eff1, eff2 = effective(resolved_cats[0]), effective(resolved_cats[1])
        c1, c2 = CIRCLES[eff1], CIRCLES[eff2]
        mx, my = (c1['cx']+c2['cx'])/2, (c1['cy']+c2['cy'])/2
        angle = random.uniform(0,6.28)
        rr = 0.0
        found = None
        own_cats = [eff1, eff2]
        for i in range(20000):
            x = mx + rr*math.cos(angle)
            y = my + rr*math.sin(angle)
            if (in_circle(x,y,c1) and in_circle(x,y,c2) and not collides(x,y,side)
                    and not crosses_foreign_circle(x,y,own_cats)):
                found = (x,y,rr)
                break
            angle += GOLDEN_ANGLE
            rr += 4.0
            if rr > max(c1['r'], c2['r'])*1.3:
                break
        if found is None:
            # relax the "must be in both circles" constraint as a last resort;
            # still guaranteed collision-free and still avoids foreign circles
            x,y,rr = spiral_free_spot(mx, my, side, seed_angle=angle, own_cats=own_cats)
            found = (x,y,rr)
        x,y,rr = found
        return x, y, {eff1: dist(x,y,c1['cx'],c1['cy']), eff2: dist(x,y,c2['cx'],c2['cy'])}

# ============ PROJECT CLUSTERING ============
# gather project membership (leads + participants treated the same for clustering)
proj_members = defaultdict(set)   # project_lower -> set(org names)
proj_leads = defaultdict(set)     # project_lower -> set(org names) [from "lead" column]
for name, o in orgs.items():
    if o['lead_raw']:
        for p in str(o['lead_raw']).split(','):
            p = p.strip()
            if p:
                proj_members[p.lower()].add(name)
                proj_leads[p.lower()].add(name)
    if o['part_raw']:
        for p in str(o['part_raw']).split(','):
            p = p.strip()
            if p:
                proj_members[p.lower()].add(name)

def primary_category(name):
    cats = [c for c in orgs[name]['categories'] if c in CIRCLES]
    return cats[0] if cats else None

# build clusters: (project, category) -> list of org names   [only for projects w/ 2+ total orgs]
clusters = {}  # cluster_id -> {'project':.., 'category':.., 'members':[...], 'anchor_name':..}
org_cluster = {}  # org name -> cluster_id (primary cluster assignment, first one wins)

for proj, members in proj_members.items():
    if len(members) < 2:
        continue
    by_cat = defaultdict(list)
    for m in members:
        cat = primary_category(m)
        if cat:
            by_cat[cat].append(m)
    for cat, mem_list in by_cat.items():
        cluster_id = f"{proj}::{cat}"
        leads_here = [m for m in mem_list if m in proj_leads.get(proj, set())]
        if leads_here:
            anchor = max(leads_here, key=lambda n: orgs[n]['budget'])
        else:
            anchor = max(mem_list, key=lambda n: orgs[n]['budget'])
        clusters[cluster_id] = {'project': proj, 'category': cat, 'members': mem_list, 'anchor_name': anchor}
        for m in mem_list:
            org_cluster.setdefault(m, cluster_id)

# project connector edges: intra-cluster (star to anchor) + inter-cluster (one line per category pair)
project_edges = []  # (a, b, 'intra'|'inter')
for cid, c in clusters.items():
    anchor = c['anchor_name']
    for m in c['members']:
        if m != anchor:
            project_edges.append((m, anchor, 'intra'))

proj_to_clusters = defaultdict(list)
for cid, c in clusters.items():
    proj_to_clusters[c['project']].append(cid)

for proj, cids in proj_to_clusters.items():
    reps = [clusters[cid]['anchor_name'] for cid in cids]
    for i in range(len(reps)):
        for j in range(i+1, len(reps)):
            project_edges.append((reps[i], reps[j], 'inter'))

print("Clusters formed:", len(clusters))
print("Project connector lines:", len(project_edges))

# ============ PLACEMENT ============
# Circle growth (to fit sub-group contents) can retroactively swallow a
# neighboring circle's single-category orgs into what's now crossover
# territory. So we place + grow repeatedly until circle sizes stop changing --
# each pass respects the PREVIOUS pass's (possibly grown) circle sizes when
# deciding what counts as a foreign crossover.
circle_cluster_ids = defaultdict(list)
for cid, c in clusters.items():
    circle_cluster_ids[c['category']].append(cid)

for _iteration in range(9):
    placed = []
    cluster_anchor_pos = {}  # cluster_id -> (x,y)

    for cat, cids in circle_cluster_ids.items():
        circ = CIRCLES[cat]
        used_points = []
        for cid in sorted(cids, key=lambda cid: -len(clusters[cid]['members'])):
            for _ in range(300):
                x,y = sample_in_circle(circ, radius_scale=0.65)
                ok = True
                for (ux,uy) in used_points:
                    if dist(x,y,ux,uy) < circ['r']*0.55:
                        ok = False
                        break
                if ok:
                    break
            used_points.append((x,y))
            cluster_anchor_pos[cid] = (x,y)

    # 2. place each org: cluster members packed near their cluster anchor; others placed freely
    # largest-footprint orgs get first pick of space, since they're hardest to fit
    # needed_extent tracks, per circle, the farthest any of its members landed from
    # the circle's center -- used afterward to GROW circles so nothing overlaps.
    needed_extent = defaultdict(float)

    def note_extent(cat, cx_box, cy_box, box_w, box_h):
        if cat not in CIRCLES:
            return
        c = CIRCLES[cat]
        half_diag = math.hypot(box_w, box_h)/2
        reach = dist(cx_box, cy_box, c['cx'], c['cy']) + half_diag
        if reach > needed_extent[cat]:
            needed_extent[cat] = reach

    # Placement priority: orgs whose target circle is SMALL (e.g. nested sub-groups)
    # go first, so they claim their tight local space before a neighboring big
    # circle's content sprawls into it. Within that, bigger boxes / bigger clusters
    # go first since they're hardest to fit.
    def target_radius(name):
        cid = org_cluster.get(name)
        if cid:
            return CIRCLES[clusters[cid]['category']]['r']
        cats = [c for c in orgs[name]['categories'] if c in CIRCLES]
        if not cats:
            return 1e9
        return min(CIRCLES[c]['r'] for c in cats)

    def size_priority(name):
        cid = org_cluster.get(name)
        if cid:
            return len(clusters[cid]['members'])
        return side_for(orgs[name]['budget'])

    placement_order = sorted(
        [n for n in order if n in orgs],
        key=lambda n: (target_radius(n), -size_priority(n))
    )
    for name in placement_order:
        if name not in orgs:
            continue
        o = orgs[name]
        side = side_for(o['budget'])
        fp, lines, fsize = footprint(name, side)
        box_w = max(fp, max((len(l) for l in lines), default=1)*fsize*0.6+10)
        box_h = max(fp, len(lines)*(fsize+3)+8)

        cid = org_cluster.get(name)
        if cid:
            cx, cy = cluster_anchor_pos[cid]
            cat = clusters[cid]['category']
            circ = CIRCLES[cat]
            n_members = len(clusters[cid]['members'])
            dist_to_edge = max(20, circ['r']*0.94 - dist(cx,cy,circ['cx'],circ['cy']))
            # small clusters stay tight near the anchor; large ones are allowed to spread
            # across more of the available room in the circle -- but this is only a
            # *preference* for where to start searching, never a hard cap, so
            # crowded clusters simply spread further rather than overlap.
            spread_frac = min(1.0, 0.22 + 0.05*n_members)
            preferred_r = max(30.0, dist_to_edge * spread_frac)
            top_clear = 0.55 if circ['parent'] else 0.80
            min_y = circ['cy'] - circ['r']*top_clear
            x,y,r_used = spiral_free_spot(cx, cy, fp, min_y=min_y, seed_angle=random.uniform(0,6.28), step=4.0, own_cats=[cat])
            note_extent(cat, x, y, box_w, box_h)
        else:
            x,y,extents = place_free(o['categories'], fp)
            for cat, r_used in extents.items():
                note_extent(cat, x, y, box_w, box_h)

        placed.append((name,x,y,fp))
        o['x'], o['y'], o['side'], o['fsize'], o['lines'] = x, y, side, fsize, lines
        o['box_w'], o['box_h'] = box_w, box_h

    # grow circles (especially small sub-group circles) so every placed square is
    # actually contained, with a little breathing room -- guarantees no overlaps
    # AND no squares poking out past their circle's edge.
    grew = False
    for cat, extent in needed_extent.items():
        c = CIRCLES[cat]
        required_r = extent + 18
        if required_r > c['r'] + 0.5:
            print(f"[pass {_iteration}] Growing circle '{cat}': {c['r']:.0f} -> {required_r:.0f}")
            c['r'] = required_r
            grew = True
    if not grew:
        print(f"Layout converged after pass {_iteration}")
        break

json.dump({n:{k:v for k,v in o.items()} for n,o in orgs.items()}, open('/tmp/power_map_debug_orgs.json','w'), indent=1)  # debug artifact, safe to ignore/delete
print("placed", len(placed))

# ============ SVG RENDERING ============
# Compute a bounding box that actually contains every (possibly-grown) circle
# and every placed square, so nothing gets clipped off-canvas.
_minx = min(c['cx']-c['r'] for c in CIRCLES.values())
_maxx = max(c['cx']+c['r'] for c in CIRCLES.values())
_miny = min(c['cy']-c['r'] for c in CIRCLES.values())
_maxy = max(c['cy']+c['r'] for c in CIRCLES.values())
for (_n,_x,_y,_fp) in placed:
    _minx = min(_minx, _x-_fp/2); _maxx = max(_maxx, _x+_fp/2)
    _miny = min(_miny, _y-_fp/2); _maxy = max(_maxy, _y+_fp/2)
PAD = 60
VX, VY = _minx-PAD, _miny-PAD
W, H = (_maxx-_minx)+2*PAD, (_maxy-_miny)+2*PAD

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

svg = []
svg.append(f'<svg viewBox="{VX:.0f} {VY:.0f} {W:.0f} {H:.0f}" xmlns="http://www.w3.org/2000/svg" font-family="Public Sans, Arial, sans-serif">')
svg.append(f'<rect x="{VX:.0f}" y="{VY:.0f}" width="{W:.0f}" height="{H:.0f}" fill="#282739"/>')

top_level = [k for k,v in CIRCLES.items() if v['parent'] is None]
nested = [k for k,v in CIRCLES.items() if v['parent'] is not None]

for k in top_level:
    c = CIRCLES[k]
    svg.append(f'<circle cx="{c["cx"]}" cy="{c["cy"]}" r="{c["r"]}" fill="{c["color"]}" fill-opacity="0.22" />')
for k in nested:
    c = CIRCLES[k]
    svg.append(f'<circle cx="{c["cx"]}" cy="{c["cy"]}" r="{c["r"]}" fill="{c["color"]}" fill-opacity="0.30" stroke="{c["color"]}" stroke-opacity="0.5" stroke-width="1.5"/>')

# Anchor each label to the actual top of that category's own content, not the
# abstract circle geometry -- growth can push a circle's geometric top into
# unrelated, already-crowded territory, which used to bury the label under
# other categories' boxes.
cat_member_tops = defaultdict(lambda: None)
cat_member_x = defaultdict(list)
for name, o in orgs.items():
    cats = [c for c in o['categories'] if c in CIRCLES]
    cid = org_cluster.get(name)
    target_cats = [clusters[cid]['category']] if cid else cats
    top_y = o['y'] - o['box_h']/2
    for cat in target_cats:
        cur = cat_member_tops[cat]
        cat_member_tops[cat] = top_y if cur is None else min(cur, top_y)
        cat_member_x[cat].append(o['x'])

LABEL_OFFSET = {}
for k, c in CIRCLES.items():
    ox, oy = LABEL_OFFSET.get(k, (0,0))
    fsize = 24 if c['parent'] is None else 12
    content_top = cat_member_tops[k]
    geom_top = c['cy'] - c['r']
    if content_top is not None:
        # sit just above the highest box in this category, but never higher
        # than the circle's own visual top (keeps it inside the blob)
        label_y = max(geom_top + fsize*0.9, content_top - 14) + oy
    else:
        label_y = geom_top + (26 if c['parent'] is None else 16) + oy
    label_x = (sum(cat_member_x[k])/len(cat_member_x[k]) if cat_member_x[k] else c['cx']) + ox
    svg.append(f'<text x="{label_x:.0f}" y="{label_y:.0f}" font-size="{fsize}" font-weight="900" fill="#ffffff" text-anchor="middle" opacity="0.92">{esc(k)}</text>')

# ---- project connector lines: straight, dashed, drawn first (behind everything) ----
svg.append('<g stroke="#9694a8" stroke-opacity="0.35" stroke-width="1" fill="none" stroke-dasharray="3,3">')
for a,b,k in project_edges:
    if a not in orgs or b not in orgs:
        continue
    oa, ob = orgs[a], orgs[b]
    sw = 1.6 if k == 'inter' else 0.9
    svg.append(f'<path d="M{oa["x"]:.1f},{oa["y"]:.1f} L{ob["x"]:.1f},{ob["y"]:.1f}" stroke-width="{sw}"/>')
svg.append('</g>')

# ---- partner / parent lines: curved, solid ----
def curved_path(x1,y1,x2,y2, bend=0.18):
    mx, my = (x1+x2)/2, (y1+y2)/2
    dx, dy = x2-x1, y2-y1
    length = math.hypot(dx,dy) or 1
    # perpendicular offset, alternate direction based on coordinate parity for variety
    perp_x, perp_y = -dy/length, dx/length
    offset = length * bend
    cx, cy = mx + perp_x*offset, my + perp_y*offset
    return f'M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}'

svg.append('<g stroke="#e4e2ee" stroke-opacity="0.55" stroke-width="1.3" fill="none">')
for a,b,k in final_rel_edges:
    if a not in orgs or b not in orgs:
        continue
    oa, ob = orgs[a], orgs[b]
    svg.append(f'<path d="{curved_path(oa["x"],oa["y"],ob["x"],ob["y"])}"/>')
svg.append('</g>')

# ---- org squares + labels ----
svg.append('<g>')
for name in order:
    if name not in orgs:
        continue
    o = orgs[name]
    x,y = o['x'], o['y']
    fsize = o['fsize']
    lines = o['lines']
    box_w, box_h = o['box_w'], o['box_h']
    svg.append(f'<rect x="{x-box_w/2:.1f}" y="{y-box_h/2:.1f}" width="{box_w:.1f}" height="{box_h:.1f}" rx="3" fill="#f5f3ef" stroke="#282739" stroke-width="0.75"/>')
    lh = fsize + 3
    start_y = y - (len(lines)-1)*lh/2 + fsize*0.35
    tspans = ''.join(f'<tspan x="{x:.1f}" dy="{0 if i==0 else lh}">{esc(l)}</tspan>' for i,l in enumerate(lines))
    svg.append(f'<text x="{x:.1f}" y="{start_y:.1f}" font-size="{fsize:.1f}" font-weight="600" fill="#4d4d4d" text-anchor="middle">{tspans}</text>')
svg.append('</g>')

svg.append(f'<text x="{VX+30:.0f}" y="{VY+H-30:.0f}" font-size="18" fill="#ffffff" opacity="0.55">{esc(CAPTION_TEXT)}</text>')
svg.append('</svg>')

out_path = OUTPUT_SVG_PATH
open(out_path,'w').write('\n'.join(svg))
print("SVG written:", out_path)
