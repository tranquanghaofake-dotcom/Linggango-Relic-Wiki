"""Pack jrender.js output into build/patches/side_imgs.json {boss: webp data URL}, cropped to the model and centred
on a 256 px square like imgs.py does for the GeckoLib renders. Usage: pack.py W/jm_out.json"""
import json, sys, base64, io, pathlib
from PIL import Image
H = pathlib.Path(__file__).resolve().parents[2] / "patches"
# Mutant Enderman: its arms are built by a custom class jmodel.py does not follow (the render is a black stick);
# the others are not in the wiki's boss list (app.js drops them), so their pictures would never show
DROP = {"Mutant Enderman", "Yeti", "Infernal Dragon", "Nameless Guardian"}
def fit(im):
    im = im.convert("RGBA"); bb = im.getbbox()
    if bb: im = im.crop(bb)
    s = max(im.size); c = Image.new("RGBA", (s, s), (0, 0, 0, 0)); c.paste(im, ((s - im.width) // 2, (s - im.height) // 2))
    return c.resize((256, 256), Image.LANCZOS)
out = {}
for k, v in json.load(open(sys.argv[1])).items():
    if k in DROP: continue
    o = io.BytesIO(); fit(Image.open(io.BytesIO(base64.b64decode(v)))).save(o, "WEBP", quality=88, method=6)
    out[k] = "data:image/webp;base64," + base64.b64encode(o.getvalue()).decode()
(H / "side_imgs.json").write_text(json.dumps(out, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
print(len(out), "portraits,", sum(len(v) for v in out.values()) // 1024, "kB")
