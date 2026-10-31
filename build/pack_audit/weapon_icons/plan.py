"""The inventory icon of each wiki gear item, read the way the game resolves it (../mcassets.py: the resource stack
the pack enables, models merged over their parents, the `gui` perspective of forge:separate_transforms):
  flat  the model reaches builtin/generated: its layers stacked at their own resolution (the picture the slot shows)
  el    a JSON element model (Blockbench cubes: staffs, most Too Many Bows bows): drawn here by ../block_render.py
        render_model at 32 px, as the GUI draws it (the model's display.gui, none = no transform, its gui_light)
  geo   builtin/entity with a GeckoLib .geo.json: geometry, first texture frame and display.gui for render.js
        (../geo_icon_render.html), which draws it as GeoItemRenderer does in the GUI
  none  nothing to draw (no model, or a model drawn by Java code)
32 px is one slot at GUI scale 2, shown 1:1 next to the x2 flat 16 px icons.
Run from a folder holding W (W/pack/mods/*.jar, W/pack/src = the unzipped pack, W/mc_client.jar = client-1.20.1.jar;
another place: W=<dir>): [ONLY=dump | ONLY=id,id,...] [NO_PACKS=1] python3 plan.py -> plan.json, then node render.js -> rendered.json."""
import json, glob, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..')]
import mcassets, block_render
from ld import load

SIZE = 32


def sources(W, packs=True):
    """the game's resource stack (mcassets.pack_sources): kubejs/assets, the resource packs options.txt enables minus the
    All Rights Reserved / NoDerivatives ones in mcassets.NO_ART (packs=False leaves every pack out: the mods' own
    models), the mod jars, the vanilla client jar"""
    return mcassets.pack_sources(W, packs, client=os.path.join(W, 'mc_client.jar'))


W = os.environ.get('W', 'W')
A = mcassets.Assets(sources(W, os.environ.get('NO_PACKS') != '1'))   # NO_PACKS=1: without the pack's resource packs
NAMES = collections.defaultdict(set)   # namespace -> every assets/<ns>/... path in any source (for the geo lookups)
for k, v in A.src:
    it = v[1] if k == 'z' else (os.path.relpath(os.path.join(r, f), v).replace(os.sep, '/') for r, _, fs in os.walk(v) for f in fs)
    for n in it:
        if n.startswith('assets/') and n.count('/') > 2: NAMES[n.split('/', 2)[1]].add(n)


def gui_model(m):
    """the model the GUI draws: a forge:separate_transforms model shows its `gui` perspective, else its base"""
    if m and (m['loader'] or '').endswith('separate_transforms'):
        g = (m['raw'].get('perspectives') or {}).get('gui') or m['raw'].get('base')
        return A.model(g) if isinstance(g, str) else A.merge(g) if isinstance(g, dict) else None
    return m


def ref_of(path):
    """assets/ns/textures/p.png -> ns:p"""
    _, ns, _, p = path.split('/', 3)
    return f'{ns}:{p[:-4]}'


_CLS = {}
def class_textures(g):
    """textures named by the GeoModel classes that name the geo file g (string constants of the classes in the jar that
    serves g); [] when the path is built at run time (Celestisynth, Ars' coloured books)"""
    z = next((v[0] for k, v in A.src if k == 'z' and g in v[1]), None)
    if z is None: return []
    if z.filename not in _CLS:
        _CLS[z.filename] = [(n, [s.decode() for s in re.findall(rb'(?:geo|textures)/[a-z0-9_/.\-]+', b)])
                            for n in z.namelist() if n.endswith('.class') for b in [z.read(n)] if b'geo/' in b]
    rel, ns = g.split('/', 2)[2], g.split('/')[1]
    hit = sorted((('Item' not in n.rsplit('/', 1)[-1], n), ss) for n, ss in _CLS[z.filename] if rel in ss)
    return [f'assets/{ns}/{s}' for _, ss in hit for s in ss if s.startswith('textures/') and s.endswith('.png')]


def geo_for(i, extra=()):
    """the .geo.json and texture a GeckoLib item renderer names: the geo found by file name, the texture the GeoModel
    class of that geo names (else found by file name too)"""
    ns, p = i.split(':'); base = re.sub(r'_level_(one|two|three)$', '', p)
    stems = [p, base] + [e for e in extra if e]
    N = NAMES[ns]
    G = []
    for st in stems:
        for n in (f'assets/{ns}/geo/item/{st}.geo.json', f'assets/{ns}/geo/{st}.geo.json'):
            if n in N and n not in G: G.append(n)
    if not G:
        want = {x for st in stems for x in (st + '.geo.json', st + '_item.geo.json')}
        G = sorted((n for n in N if n.startswith(f'assets/{ns}/geo/') and n.rsplit('/', 1)[1] in want), key=lambda n: ('/entity/' in n, n))   # the item geo before the thrown entity's
    if not G: return None
    g = G[0]; stem = g.rsplit('/', 1)[1][:-9]
    want = {x for st in [stem] + stems for x in (st + '.png', st + '_item.png')}
    T = [n for n in N if n.startswith(f'assets/{ns}/textures/') and n.rsplit('/', 1)[1] in want
         and not any(s in n for s in ('/entity/', '/armor/', '/gui/', '/block/'))]
    T.sort(key=lambda n: ('/item' not in n and '/weapons/' not in n and '/staves/' not in n, n))
    C = [n for n in class_textures(g) if n in N]
    if C: T = [t for t in T if t in C] or C   # soulsweapons:comet_spear: CometSpearItemModel names entity/comet_spear.png
    if not T: return None
    return geo_entry(g, T[0])


# not part of the item: muzzle flashes (animation props) and player-arm placeholders, the bones MCreator's GeckoLib
# renderers (Terramity) hide by name ("left", "right"); a bone of that name is only dropped when its cubes have the
# size of a player arm, since soulsweapons, hazennstuff and others name parts of the weapon left / right
FLASH, ARM = re.compile(r'(muzzle_?)?flash'), re.compile(r'(left|right)(_?arm)?')
def arm_like(b):
    cs = b.get('cubes') or []
    return bool(cs) and all(sorted(c.get('size') or [0, 0, 0])[1:] in ([4, 12], [3, 12]) and min(c.get('size') or [0]) >= 3 for c in cs)
def geo_entry(g, t, hide=()):
    geo = json.loads(A.read(g))
    for b in geo['minecraft:geometry'][0]['bones']:
        n = b['name'].lower()
        if FLASH.fullmatch(n) or (ARM.fullmatch(n) and arm_like(b)): b['cubes'] = []
    im = A.texture(ref_of(t))   # first frame when an .mcmeta animates it (GeckoLib's AnimatableTexture shows a frame too)
    if im is None: return None
    return {'geo': geo, 'tex': mcassets.png_b64(im), 'src': [g, t], 'hide': list(hide)}


# items whose model or picture has another name than the item (read from the mod's renderer classes and model files)
# Ars Nouveau's SpellBookRenderer draws spellbook_closed in the GUI with the default purple cover and hides the tier
# bones of other tiers (actuallyRender: tier1 shown at tier 1, tier2 at tier 2, tier3 from tier 3 up)
GEOX = {f'ars_nouveau:{b}_spell_book': ('assets/ars_nouveau/geo/spellbook_closed.geo.json', 'assets/ars_nouveau/textures/item/spellbook_purple.png', h)
        for b, h in (('novice', ('tier2', 'tier3')), ('apprentice', ('tier1', 'tier3')), ('archmage', ('tier1', 'tier2')))}
# (ars_nouveau:spell_bow, spellbow.geo.json, draws only its gold trim this way: left as a placeholder)
FLATX = {'mahoutsukai:weapon_projectile_bow': 'mahoutsukai:item/weapon_projectile_bow_standby'}   # the bow at rest


def plan(i):
    ns, p = i.split(':')
    if i in FLATX:
        im = A.texture(FLATX[i])
        return {'kind': 'flat', 'png': mcassets.png_b64(im), 'tex': FLATX[i]} if im else {'kind': 'none', 'why': 'no texture'}
    if i in GEOX:
        g, t, h = GEOX[i]; e = geo_entry(g, t, h)
        return {'kind': 'geo', **e, 'gui': (gui_model(A.model(f'{ns}:item/{p}')) or {'display': {}})['display'].get('gui')} if e else {'kind': 'none'}
    m = gui_model(A.model(f'{ns}:item/{p}'))
    if m is None: return {'kind': 'none', 'why': 'no model'}
    if m['generated']:
        im = A.draw(m)
        return {'kind': 'flat', 'png': mcassets.png_b64(im), 'model': m['chain'][0]} if im else {'kind': 'none', 'why': 'no layer0'}
    if m['elements']:
        im = block_render.render_model(m, lambda r: A.texture(A.resolve(m, r)), SIZE)
        return {'kind': 'el', 'png': mcassets.png_b64(im), 'model': m['chain'][0], 'gui': m['display'].get('gui')} if im else {'kind': 'none', 'why': 'empty render'}
    if m['entity']:
        ex = [t.rsplit('/', 1)[-1] for t in m['textures'].values() if isinstance(t, str) and not t.startswith('#')]
        g = geo_for(i, ex)
        return {'kind': 'geo', **g, 'gui': m['display'].get('gui'), 'model': m['chain'][0]} if g else {'kind': 'none', 'why': 'entity-nogeo'}
    return {'kind': 'none', 'why': 'loader ' + str(m['loader'])}


if __name__ == '__main__':
    out = {}; c = collections.Counter()
    GE = load()[0]
    only = os.environ.get('ONLY')   # ONLY=dump: just the pieces added from the in-game dump; or a comma-separated list of ids
    for g in GE:
        if only == 'dump' and not g.get('dump'): continue
        if only and only != 'dump' and g['id'] not in only.split(','): continue
        pl = plan(g['id']); out[g['id']] = pl; c[(g['k'], pl['kind'])] += 1
    for k, v in sorted(c.items()): print(k, v)
    json.dump(out, open('plan.json', 'w'))
