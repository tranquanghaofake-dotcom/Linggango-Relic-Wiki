"""Landscape backgrounds for bosses added after the v21 crawl (pack_audit/boss_audit/bg.py): Chorusling, Bone Chimera.
Usage: boss_bg_extra.py patches/pack_imgs.json "Name=image file" ...
Cover-crops each image to 229x200 and stores it as webp in pack_imgs.json["scene"], like the existing scenes."""
import json, sys, io, base64
from PIL import Image
P = sys.argv[1]; d = json.load(open(P, encoding="utf-8"))
for a in sys.argv[2:]:
    name, f = a.split("=", 1)
    im = Image.open(f).convert("RGB"); W, H = 229, 200
    r = max(W / im.width, H / im.height); im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2; im = im.crop((x, y, x + W, y + H))
    b = io.BytesIO(); im.save(b, "WEBP", quality=70, method=6)
    d["scene"][name] = "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode(); print(name, len(b.getvalue()))
open(P, "w", encoding="utf-8").write(json.dumps(d))
