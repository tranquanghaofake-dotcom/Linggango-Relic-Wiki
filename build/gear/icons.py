"""Item icons for gear ids, the picture the inventory shows (pack_audit/mcassets.py): flat items are their layer
textures stacked (first animation frame per .mcmeta), block-element models are drawn in the GUI view by
pack_audit/block_render.py at 32 px (the slot at GUI scale 2, shown 1:1 next to x2 flat icons); models drawn by code
(builtin/entity) fall back to their particle texture, then to textures/item/<path>.png.
Search order, as the game stacks them: kubejs assets, pack resource zips, mod jars, the vanilla client jar.
Usage: icons.py W ids.json out.json   (writes id -> base64 png)"""
import sys, json, glob, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pack_audit'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # build.sh copies mcassets.py next to this file
import mcassets
from PIL import Image
S = sys.argv[1]; ids = json.load(open(sys.argv[2])); outp = sys.argv[3]
A = mcassets.Assets([S + '/pack/src/overrides/kubejs'] + glob.glob(S + '/pack/mods/*.zip') + glob.glob(S + '/pack/src/overrides/resourcepacks/*.zip')
                    + sorted(glob.glob(S + '/pack/mods/*.jar')) + [S + '/pack/mods/zz_client-1.20.1.jar.bak'])
out, how = {}, {'model': 0, 'particle': 0, 'texture': 0}
for i in ids:
    ns, n = mcassets.rl(i)
    im = A.icon(i, 32); k = 'model'
    if im is None:
        m = A.model(f'{ns}:item/{n}')
        im = A.texture(A.resolve(m, m['textures'].get('particle'))) if m else None; k = 'particle'
    if im is None: im = A.texture(f'{ns}:item/{n}'); k = 'texture'
    if im is None: continue
    if im.size[0] > 64:   # 1/n of the source (pixel rules): the smallest n that brings it to 64 px or less, exact if one divides
        w, h = im.size; ns = [n for n in range(2, w + 1) if w / n <= 64]
        n = next((n for n in ns[:4] if w % n == 0 and h % n == 0), ns[0])
        im = im.resize((w // n, max(1, h // n)), Image.NEAREST)
    out[i] = mcassets.png_b64(im); how[k] += 1
json.dump(out, open(outp, 'w'))
print(len(ids), 'icons', len(out), how)
