#!/usr/bin/env python3
"""Pack armor_render.js output into build/patches/armor_renders.json {set key: data URL}: each picture cropped to the
figure and stored as the smallest lossless PNG (mcassets.png_b64; the earlier pictures were lossy WebP).
Only sets that already have a picture are replaced, unless --add: a set the prep matched to the wrong texture comes out
as a bare mannequin, and the list on the site was checked by eye.
Usage: python3 -I build/pack_audit/armor_pack.py W/armor_out.json [--add]"""
import base64, io, json, pathlib, sys
from PIL import Image
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mcassets
F = pathlib.Path(__file__).resolve().parents[1] / "patches" / "armor_renders.json"
out = json.loads(F.read_text(encoding="utf-8")); add = "--add" in sys.argv
n = 0
for k, v in json.load(open(sys.argv[1])).items():
    if k not in out and not add: continue
    im = Image.open(io.BytesIO(base64.b64decode(v))).convert("RGBA")
    if im.getbbox(): im = im.crop(im.getbbox())
    out[k] = "data:image/png;base64," + mcassets.png_b64(im); n += 1
F.write_text(json.dumps(out, separators=(",", ":"), sort_keys=True), encoding="utf-8")
print(n, "pictures replaced;", len(out), "in", F.name, sum(len(v) for v in out.values()) // 1024, "kB")
