"""Contact sheet of portraits, to look at by eye. Usage: sheet.py OUT.png SCALE NEW.json [OLD.json | -] [name|name...] [--diff]
Each JSON is {name: base64 PNG/WebP or data URL}. With OLD, every boss is a pair, old on the left and new on the right; --diff
adds a third picture with the changed pixels in red. Pictures keep their own size times SCALE (nearest neighbour, so ×1 and ×2
show the pixels as the site does), centred in equal cells on the page's dark grey."""
import json, sys, base64, io
from PIL import Image, ImageDraw, ImageChops
args = [x for x in sys.argv[1:] if x != "--diff"]; diff = "--diff" in sys.argv
def load(f): return {k: Image.open(io.BytesIO(base64.b64decode(v.split(",", 1)[-1]))).convert("RGBA") for k, v in json.load(open(f)).items() if v}
out, k = args[0], int(args[1]); N = load(args[2]); O = load(args[3]) if len(args) > 3 and args[3] != "-" else None
ks = args[4].split("|") if len(args) > 4 else sorted(N, key=str.lower)
def red(a, b):  # the new picture greyed, its changed pixels red
    if a is None or b is None or a.size != b.size: return None
    m = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v else 0)
    g = Image.merge("RGBA", (*[b.convert("L")] * 3, b.getchannel(3))).point(lambda v: v // 3)
    return Image.composite(Image.new("RGBA", b.size, (255, 40, 40, 255)), g, m)
ims = [im for n in ks for im in ((O.get(n) if O else None), N.get(n)) if im is not None]
cell = max([256] + [max(im.size) for im in ims]) * k; per = (2 if O else 1) + (1 if O and diff else 0)
cols = max(1, 2080 // (per * cell + 8)); rows = (len(ks) + cols - 1) // cols
S = Image.new("RGBA", (cols * (per * cell + 8), rows * (cell + 18)), (40, 40, 48, 255)); D = ImageDraw.Draw(S)
for i, n in enumerate(ks):
    x, y = (i % cols) * (per * cell + 8), (i // cols) * (cell + 18)
    row = ([O.get(n)] if O else []) + [N.get(n)] + ([red(O.get(n), N.get(n))] if O and diff else [])
    for j, im in enumerate(row):
        if im is None: D.text((x + j * cell + 8, y + cell // 2), "none", fill=(160, 160, 160, 255)); continue
        im = im.resize((im.width * k, im.height * k), Image.NEAREST)
        S.alpha_composite(im, (x + j * cell + (cell - im.width) // 2, y + (cell - im.height) // 2))
    D.text((x + 2, y + cell + 3), (n + ("   (old | new" + (" | changed" if diff else "") + ")" if O else ""))[:70], fill=(255, 255, 255, 255))
S.save(out); print(out, S.size)
