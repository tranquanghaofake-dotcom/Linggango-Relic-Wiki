"""Build the icon render plan for wiki gear: what each item's inventory icon should be, read from the jars.
flat -> texture png, el -> Java element model for the three.js renderer, geo -> GeckoLib model + texture."""
import json, zipfile, glob, io, base64, re, sys, collections
from PIL import Image
sys.path.insert(0, '.')
from ld import load
GE, GS, IC, S = load()
Z = {}
for j in sorted(glob.glob('W/pack/mods/*.jar')):
    try: z = zipfile.ZipFile(j)
    except Exception: continue
    for n in z.namelist(): Z.setdefault(n, z)
# vanilla assets: only needed for parents; the pack's armor/tool bases are not rendered here
def rd(n): return Z[n].read(n) if n in Z else None
def rl(s, kind):
    ns, p = s.split(':', 1) if ':' in s else ('minecraft', s)
    return f'assets/{ns}/{kind}/{p}'
def jm(path):
    b = rd(rl(path, 'models') + '.json')
    if b is None: return None
    try: return json.loads(b)
    except Exception: return None
def png_b64(path, first=True):
    b = rd(rl(path, 'textures') + '.png')
    if b is None: return None
    im = Image.open(io.BytesIO(b)).convert('RGBA')
    if first and im.height > im.width and im.height % im.width == 0: im = im.crop((0, 0, im.width, im.width))
    o = io.BytesIO(); im.save(o, 'PNG'); return base64.b64encode(o.getvalue()).decode()

def resolve(path, d=0):
    """-> dict(kind, textures, elements, gui, sep_gui) following parents; kind in flat|el|sep|entity|none"""
    m = jm(path)
    if m is None or d > 8: return None
    if (m.get('loader') or '').endswith('separate_transforms'):
        g = (m.get('perspectives') or {}).get('gui')
        if g:
            r = resolve_inline(g, d + 1)
            if r: return r
        b = m.get('base')
        return resolve_inline(b, d + 1) if b else None
    return resolve_inline(m, d)
def resolve_inline(m, d=0):
    if not isinstance(m, dict) or d > 8: return None
    tex = dict(m.get('textures') or {}); par = m.get('parent'); disp = dict(m.get('display') or {})
    out = None
    if 'elements' in m:
        out = {'kind': 'el', 'elements': m['elements'], 'textures': tex, 'display': disp}
    elif par in ('builtin/entity', 'minecraft:builtin/entity'):
        return {'kind': 'entity', 'textures': tex}
    elif par and not par.startswith(('minecraft:item/', 'item/', 'minecraft:builtin', 'builtin')):
        r = resolve(par, d + 1)
        if r is None:
            out = {'kind': 'flat', 'textures': tex} if 'layer0' in tex else None
        else:
            r['textures'] = {**r.get('textures', {}), **tex}
            if r['kind'] == 'el': r['display'] = {**r.get('display', {}), **disp}
            out = r
    elif 'layer0' in tex:
        out = {'kind': 'flat', 'textures': tex}
    if out and out['kind'] == 'flat' and 'layer0' not in out['textures']: return None
    return out
def deref(t, tex):
    k = 0
    while isinstance(t, str) and t.startswith('#') and k < 8: t = tex.get(t[1:]); k += 1
    return t if isinstance(t, str) else None

def geo_for(i, extra=()):
    ns, p = i.split(':'); base = re.sub(r'_level_(one|two|three)$', '', p)
    stems = [p, base] + [e for e in extra if e]
    G = []
    for st in stems:
        for n in (f'assets/{ns}/geo/item/{st}.geo.json', f'assets/{ns}/geo/{st}.geo.json'):
            if n in Z and n not in G: G.append(n)
    if not G:
        G = [n for n in Z if n.startswith(f'assets/{ns}/geo/') and n.endswith('.geo.json') and n.rsplit('/', 1)[1] in [x for st in stems for x in (st + '.geo.json', st + '_item.geo.json')]]
    if not G: return None
    g = G[0]; stem = g.rsplit('/', 1)[1][:-9]
    T = [n for n in Z if n.startswith(f'assets/{ns}/textures/') and n.endswith('.png') and n.rsplit('/', 1)[1] in [x for st in [stem] + stems for x in (st + '.png', st + '_item.png')] and '/entity/' not in n and '/armor/' not in n and '/gui/' not in n and '/block/' not in n]
    T.sort(key=lambda n: ('/item' not in n and '/weapons/' not in n and '/staves/' not in n, n))
    if not T: return None
    im = Image.open(io.BytesIO(rd(T[0]))).convert('RGBA')
    if im.height > im.width and im.height % im.width == 0 and False: pass
    geo = json.loads(rd(g))
    # player-arm placeholders and muzzle flashes are animation props, not part of the item
    for b in geo['minecraft:geometry'][0]['bones']:
        if re.fullmatch(r'(left|right)(_?arm)?|flash|muzzle_?flash', b['name'].lower()): b['cubes'] = []
    return {'geo': geo, 'tex': base64.b64encode(rd(T[0])).decode(), 'src': [g, T[0]]}

def plan(i):
    ns, p = i.split(':')
    r = resolve(f'{ns}:item/{p}')
    if r is None: return {'kind': 'none'}
    if r['kind'] == 'flat':
        t = deref(r['textures'].get('layer0'), r['textures'])
        b = png_b64(t) if t else None
        return {'kind': 'flat', 'png': b, 'tex': t} if b else {'kind': 'none'}
    if r['kind'] == 'el':
        texs = {}
        for k, t in r['textures'].items():
            t = deref(t, r['textures']); b = png_b64(t, first=False) if t else None
            if b: texs[k] = b
        if not texs: return {'kind': 'none'}
        # a '#ref' face texture: deref to a key present in texs
        els = json.loads(json.dumps(r['elements']))
        for e in els:
            for f in (e.get('faces') or {}).values():
                t = f.get('texture')
                if isinstance(t, str) and t.startswith('#'):
                    k = t[1:]
                    if k not in texs:
                        dk = r['textures'].get(k)
                        # alias to another key
                        if isinstance(dk, str) and dk.startswith('#') and dk[1:] in texs: f['texture'] = dk
        return {'kind': 'el', 'el': els, 'tex': texs, 'gui': r.get('display', {}).get('gui')}
    if r['kind'] == 'entity':
        ex = [t.rsplit('/', 1)[-1] for t in r['textures'].values() if isinstance(t, str) and not t.startswith('#')]
        g = geo_for(i, ex)
        return ({'kind': 'geo', **g} if g else {'kind': 'none', 'why': 'entity-nogeo'})
    return {'kind': 'none'}

if __name__ == '__main__':
    out = {}; c = collections.Counter()
    for g in GE:
        pl = plan(g['id']); out[g['id']] = pl; c[(g['k'], pl['kind'])] += 1
    for k, v in sorted(c.items()): print(k, v)
    json.dump(out, open('plan.json', 'w'))
