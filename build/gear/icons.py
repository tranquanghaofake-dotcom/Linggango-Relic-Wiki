"""Item icons for gear ids, the picture the inventory shows (pack_audit/mcassets.py): flat items are their layer
textures stacked (first animation frame per .mcmeta), block-element models are drawn in the GUI view by
pack_audit/block_render.py at 32 px (the slot at GUI scale 2, shown 1:1 next to x2 flat icons); models drawn by code
(builtin/entity) fall back to their particle texture, then to textures/item/<path>.png.
Search order, as the game stacks them (mcassets.pack_sources): kubejs assets, the resource packs options.txt enables
except the All Rights Reserved / NoDerivatives ones in mcassets.NO_ART (build/README.md line 55), mod jars, the
vanilla client jar. Tinted layers get the game's colours (pack_audit/tints.py: spawn eggs, leather, grass, the mods'
colour handlers); without javap or jawa they stay grey and a line says so.
Usage: icons.py W ids.json out.json   (writes id -> base64 png)"""
import sys, json, glob, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pack_audit'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # build.sh copies mcassets.py, tints.py next to this file
import mcassets
from PIL import Image
S = sys.argv[1]; ids = json.load(open(sys.argv[2])); outp = sys.argv[3]
CLIENT = next((c for c in (S + '/mc_client.jar', S + '/pack/mods/zz_client-1.20.1.jar.bak') if os.path.exists(c)), None)
A = mcassets.Assets(mcassets.pack_sources(S, client=CLIENT))
print('resource packs left out (mcassets.NO_ART):', len([p for p in glob.glob(S + '/pack/mods/*.zip') + glob.glob(S + '/pack/src/overrides/resourcepacks/*')
                                                         if not mcassets.art_allowed(p)]))
T = None
try:
    import tints
    cmap = lambda n: A.texture('minecraft:colormap/' + n)
    jars = [j for j in sorted(glob.glob(S + '/pack/mods/*.jar')) if mcassets.art_allowed(j)]
    try: T = tints.Tints(CLIENT, jars, colormap=cmap)
    except ImportError as e: print('mod colours not read (%s): vanilla tints only' % e); T = tints.Tints(CLIENT, colormap=cmap)
except Exception as e:   # no client jar, no javap
    print('no tints (%s): tinted layers stay grey' % e)
out, how = {}, {'model': 0, 'particle': 0, 'texture': 0, 'tinted': 0}
for i in ids:
    ns, n = mcassets.rl(i)
    ti = A.tint_indices(i) if T else set()
    tint = T.tint(i, max(ti) + 1)[0] if ti else None
    im = A.icon(i, 32, tint=tint); k = 'model'
    if im is None:
        m = A.model(f'{ns}:item/{n}')
        im = A.texture(A.resolve(m, m['textures'].get('particle'))) if m else None; k = 'particle'
    if im is None: im = A.texture(f'{ns}:item/{n}'); k = 'texture'
    if im is None: continue
    if im.size[0] > 64:   # 1/n of the source (pixel rules): the smallest n that brings it to 64 px or less, exact if one divides
        w, h = im.size; ns = [n for n in range(2, w + 1) if w / n <= 64]
        n = next((n for n in ns[:4] if w % n == 0 and h % n == 0), ns[0])
        im = im.resize((w // n, max(1, h // n)), Image.NEAREST)
    out[i] = mcassets.png_b64(im); how[k] += 1; how['tinted'] += bool(tint and k == 'model')
json.dump(out, open(outp, 'w'))
print(len(ids), 'icons', len(out), how)
