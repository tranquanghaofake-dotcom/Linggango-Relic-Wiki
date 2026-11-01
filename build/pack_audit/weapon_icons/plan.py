"""The inventory icon of each wiki gear item, read the way the game resolves it (../mcassets.py: the resource stack
the pack enables, models merged over their parents, the `gui` perspective of forge:separate_transforms):
  flat  the model reaches builtin/generated: its layers stacked at their own resolution (the picture the slot shows)
  el    a JSON element model (Blockbench cubes: staffs, most Too Many Bows bows): drawn here by ../block_render.py
        render_model at 32 px, as the GUI draws it (the model's display.gui, none = no transform, its gui_light)
  geo   builtin/entity with a GeckoLib .geo.json: geometry, first texture frame and display.gui for render.js
        (../geo_icon_render.html), which draws it as GeoItemRenderer does in the GUI
  java  builtin/entity drawn by a Java renderer listed in JAVA (chests, shield, banner, Goety's plushies, Pyrium Staff):
        the renderer's PoseStack steps, ModelPart models and render types for render.js (renderJava)
  none  nothing to draw (no model, or a model drawn by Java code not in JAVA)
32 px is one slot at GUI scale 2, shown 1:1 next to the x2 flat 16 px icons.
Run from a folder holding W (W/pack/mods/*.jar, W/pack/src = the unzipped pack, W/mc_client.jar = client-1.20.1.jar;
another place: W=<dir>; CLIENT_SRG=<client jar with SRG names> for JAVA): [ONLY=dump | ONLY=id,id,...] [NO_PACKS=1]
python3 plan.py -> plan.json, then node render.js -> rendered.json, then python3 plan.py --put rendered.json (an id outside
the gear list in ONLY is planned too: a curio recipe ingredient whose icon lives in data.js IC)."""
import json, glob, os, re, sys, collections, math, struct
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


# ---- items the game draws with Java code: builtin/entity models whose renderByItem draws ModelPart models (vanilla
# BlockEntityWithoutLevelRenderer and the mods' own), read from the bytecode with javap. Vanilla classes come from
# client-1.20.1.jar remapped to Mojang class / SRG member names (CLIENT_SRG, default W/client-1.20.1-srg.jar: made by
# gear/wide/srgjar.py client-1.20.1.jar client.txt joined.tsrg OUT.jar, client.txt = Mojang's 1.20.1 client mappings,
# SHA-1 6c48521e); their geometry runs through side_bosses/jmodel.py; render.js draws them with ../geo_icon_render.html
# renderJava. Each builder returns the draws in the renderer's order: PoseStack steps after ItemRenderer's
# translate(-0.5), the model (or baked quads), texture, render type (see renderJava) and the pose the renderer sets.
sys.path.insert(0, os.path.join(HERE, '..', 'side_bosses'))
import jmodel
SRGJAR = os.environ.get('CLIENT_SRG') or os.path.join(W, 'client-1.20.1-srg.jar')
_JM = {}
def jm(cls, method=None):
    """a ModelPart tree (jmodel.py) of a vanilla class (net.minecraft.*, from SRGJAR) or a mod's (the jar that holds it);
    an argument the stack machine could not work out is an error, not a guess"""
    if (cls, method) not in _JM:
        path = cls.replace('.', '/') + '.class'
        jar = SRGJAR if cls.startswith('net.minecraft.') else next((v[0].filename for k, v in A.src if k == 'z' and path in v[1]), None)
        if not jar or not os.path.exists(jar): raise FileNotFoundError(f'{cls}: no jar (CLIENT_SRG for vanilla)')
        m = jmodel.model(jar, cls, method)
        if not m or jmodel.CTX.get('unk'): raise ValueError(f'{cls}.{method}: model not read ({jmodel.CTX.get("unk")} unknown arguments)')
        _JM[(cls, method)] = m
    return _JM[(cls, method)]
def tex(ref):
    im = A.texture(ref)
    if im is None: raise FileNotFoundError(ref)
    return mcassets.png_b64(im)
def item_transform(g, z_is_x=False):
    """ItemTransform.apply as PoseStack steps: translate (JSON / 16, clamped to 5), rotationXYZ, scale (clamped to 4);
    z_is_x: Iron's PyriumStaffRenderer.applyTransform scales z by the transform's x"""
    g = g or {}; c = lambda v, a: min(a, max(-a, v))
    t = [c(v * 0.0625, 5) for v in g.get('translation') or [0, 0, 0]]; r = g.get('rotation') or [0, 0, 0]
    s = [c(v, 4) for v in g.get('scale') or [1, 1, 1]]
    return [['t', *t], ['r', 'x', r[0]], ['r', 'y', r[1]], ['r', 'z', r[2]], ['s', s[0], s[1], s[0] if z_is_x else s[2]]]
FLOAT = lambda v: struct.unpack('f', struct.pack('f', v))[0]   # Java float arithmetic
DEG = FLOAT(0.017453292)

# ChestRenderer.render without a level (BEWLR's chest): a CHEST block facing SOUTH (no turn), openness 0 (lid xRot 0),
# lid, lock, bottom from ModelLayers.CHEST (createSingleBodyLayer, m_173608_), Material.buffer(entityCutout).
# Ars Nouveau's ArchwoodChestRenderer is the same code over the same layer; its getMaterial gives SINGLE
# ars_nouveau:model/chest/archwood/archwood (assets/minecraft/atlases/chests.json in its jar).
CHEST = ('net.minecraft.client.renderer.blockentity.ChestRenderer', 'm_173608_')
def chest(texture):
    return lambda: [{'model': jm(*CHEST), 'parts': ['lid', 'lock', 'bottom'], 'tex': tex(texture), 'mode': 'cutout',
                     'ops': [['t', .5, .5, .5], ['r', 'y', -0.0], ['t', -.5, -.5, -.5]]}]
# BEWLR shield without BlockEntityTag: scale(1, -1, -1), ShieldModel (m_170912_) handle then plate in
# entity/shield_base_nopattern, entitySolid
SHIELD = ('net.minecraft.client.model.ShieldModel', 'm_170912_')
def shield():
    return [{'model': jm(*SHIELD), 'parts': [k], 'tex': tex('minecraft:entity/shield_base_nopattern'), 'mode': 'solid', 'ops': [['s', 1, -1, -1]]}
            for k in ('handle', 'plate')]
# BannerRenderer.render without a level, partial tick 0, at BlockPos.ZERO: translate(0.5), scale(2/3, -2/3, -2/3), pole and
# bar in entity/banner_base (entitySolid), the flag at y -32 swaying (-0.0125 + 0.01 cos(0)) pi, then renderPatterns: the
# flag in banner_base (entitySolid) and each pattern of getPatterns() (no item patterns: only BASE in the block's colour)
# in entity/banner/<pattern> through entityNoOutline, tinted by DyeColor.textureDiffuseColors
BANNER = ('net.minecraft.client.renderer.blockentity.BannerRenderer', 'm_173522_')
DYE = {'red': 0xB02E26}   # DyeColor RED(14, "red", 11546150, ...) in client-1.20.1.jar
def banner(color):
    k = FLOAT(2 / 3); ops = [['t', .5, .5, .5], ['s', k, -k, -k]]
    sway = FLOAT(FLOAT(-0.0125 + FLOAT(0.01) * math.cos(0)) * FLOAT(math.pi)); flag = {'flag': [None, -32, None, sway, None, None]}
    c = DYE[color]; tint = [(c >> 16 & 255) / 255, (c >> 8 & 255) / 255, (c & 255) / 255]
    def draws():
        base = tex('minecraft:entity/banner_base')
        return ([{'model': jm(*BANNER), 'parts': [p], 'tex': base, 'mode': 'solid', 'ops': ops} for p in ('pole', 'bar')]
                + [{'model': jm(*BANNER), 'parts': ['flag'], 'pose': flag, 'tex': base, 'mode': 'solid', 'ops': ops},
                   {'model': jm(*BANNER), 'parts': ['flag'], 'pose': flag, 'tex': tex('minecraft:entity/banner/base'), 'mode': 'nooutline',
                    'cull': False, 'tint': tint, 'ops': ops}])
    return draws
# Goety's ModISTER in the GUI: translate(0.5), rotate X 30, Y 45 (Axis.YN by -45), translate(-0.5), translate(0, 0.25, 0);
# then PlushieBlockEntityRenderer.renderItemPlushie: translate(0.5, 0, 0.5), scale(-1, -1, 1), scale(0.5),
# PlushieModel.setupAnim(0, 180, 0) (root yRot 180 deg, plushie y -8 at scale 1), entityTranslucent (no cull) with
# goety:textures/entity/plushie/<type>.png; PlushieBlock type 0 for goety:plushie, 1 for goety:plushie_1 (ModBlocks)
def plushie(n):
    ops = [['t', .5, .5, .5], ['r', 'x', 30], ['r', 'y', 45], ['t', -.5, -.5, -.5], ['t', 0, .25, 0], ['t', .5, 0, .5], ['s', -1, -1, 1], ['s', .5, .5, .5]]
    return lambda: [{'model': jm('com.Polarice3.Goety.client.render.model.PlushieModel'), 'tex': tex(f'goety:entity/plushie/{n}'), 'mode': 'translucent',
                     'cull': False, 'pose': {'root': [None, None, None, 0, FLOAT(180 * DEG), None], 'plushie': [None, -8, None, None, None, None]}, 'ops': ops}]
# Iron's PyriumStaffRenderer in the GUI: translate(0.5), setupFor3DItems; the haft (item/pyrium_staff_haft, item/generated)
# through ItemRenderer.render (its display.gui, translate(-0.5), the baked quads in the translucent cull item sheet); then
# applyTransform(the haft's gui transform), rotate Z 135, Y -90, translate(0, -0.3984375, 0), scale(0.5),
# PyriumStaffHeadModel (entityCutout, item/pyrium_staff_head); translate(0, -0.296875, 0) and the orb's bob, which is 0 at
# time 0 (MinecraftInstanceHelper.getPlayer() null; in a world it bobs with the player's tick count), PyriumStaffOrbModel
# in its own type (dark_portal_cull: rendertype_energy_swirl, unlit, cutout, cull)
PYR = 'io.redspace.ironsspellbooks.item.weapons.pyrium_staff.'
def pyrium():
    hm = A.model('irons_spellbooks:item/pyrium_staff_haft'); hg = hm['display'].get('gui'); lay = A.resolve(hm, '#layer0')
    els = block_render.generated_elements(A.texture(lay))
    quads = [[(c / 16).tolist(), (uv / 16).tolist(), n.tolist()] for c, uv, _, n in block_render._quads_of({'elements': els}, lambda r: A.texture(lay))]
    head = [['t', .5, .5, .5]] + item_transform(hg, True) + [['r', 'z', 135], ['r', 'y', -90], ['t', 0, -0.3984375, 0], ['s', .5, .5, .5]]
    return [{'quads': quads, 'tex': tex(lay), 'mode': 'translucent', 'ops': [['t', .5, .5, .5]] + item_transform(hg) + [['t', -.5, -.5, -.5]]},
            {'model': jm(PYR + 'PyriumStaffHeadModel'), 'tex': tex('irons_spellbooks:item/pyrium_staff_head'), 'mode': 'cutout', 'ops': head},
            {'model': jm(PYR + 'PyriumStaffOrbModel'), 'tex': tex('irons_spellbooks:item/pyrium_staff_orb'), 'mode': 'unlit',
             'ops': head + [['t', 0, -0.296875, 0], ['t', 0, 0, 0], ['s', 1, 1, 1]]}]
JAVA = {'minecraft:chest': chest('minecraft:entity/chest/normal'), 'minecraft:ender_chest': chest('minecraft:entity/chest/ender'),
        'ars_nouveau:archwood_chest': chest('ars_nouveau:model/chest/archwood/archwood'), 'minecraft:shield': shield,
        'minecraft:red_banner': banner('red'), 'goety:plushie': plushie(0), 'goety:plushie_1': plushie(1),
        'irons_spellbooks:pyrium_staff': pyrium}


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
    if i in JAVA:   # Java renderer: the item model gives display.gui and gui_light (none = side, the 3D light)
        return {'kind': 'java', 'gui': m['display'].get('gui'), 'light': m['gui_light'] or 'side', 'draws': JAVA[i](), 'model': m['chain'][0]}
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


def put(rendered):
    """rendered.json into the wiki: an id data.js IC already holds (a curio recipe ingredient) is replaced there in place,
    anything else goes into patches/gear_icons.json; run build/patches/apply_all.sh afterwards"""
    R = {k: mcassets.repack_b64(v) for k, v in json.load(open(rendered)).items()}   # the browser's PNG, packed as the others
    B = os.path.join(HERE, '..', '..')
    dj = os.path.join(B, 'src', 'data.js'); s = open(dj, encoding='utf-8').read()
    i = s.index(',IC=') + 4; IC, e = json.JSONDecoder().raw_decode(s, i)
    gp = os.path.join(B, 'patches', 'gear_icons.json'); GI = json.load(open(gp, encoding='utf-8'))
    for k, v in R.items():
        if k in IC: IC[k] = v
        else: GI[k] = v
    open(dj, 'w', encoding='utf-8').write(s[:i] + json.dumps(IC, ensure_ascii=False, separators=(',', ':')) + s[e:])
    json.dump(GI, open(gp, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'), sort_keys=True)
    print(sum(k in IC for k in R), 'into data.js IC,', sum(k not in IC for k in R), 'into gear_icons.json')


if __name__ == '__main__':
    if sys.argv[1:2] == ['--put']: put(sys.argv[2]); sys.exit()
    out = {}; c = collections.Counter()
    GE = load()[0]
    only = os.environ.get('ONLY')   # ONLY=dump: just the pieces added from the in-game dump; or a comma-separated list of ids
    ids = {g['id']: g['k'] for g in GE if only != 'dump' or g.get('dump')}
    if only and only != 'dump': ids = {i: ids.get(i, 'ingredient') for i in only.split(',')}   # an id outside the gear list: a recipe ingredient
    for i, k in ids.items():
        pl = plan(i); out[i] = pl; c[(k, pl['kind'])] += 1
    for k, v in sorted(c.items()): print(k, v)
    json.dump(out, open('plan.json', 'w'))
