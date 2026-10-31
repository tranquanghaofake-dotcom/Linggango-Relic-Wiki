"""Pack side-boss portraits into the wiki's data: each render (jrender.js's jm_out.json, boss_portraits.js's sb_geo_out.json from
bgeo.py) is a 256 px picture framed like the Keepers', kept as it is (no crop, no resize) and stored as the smallest lossless PNG
(mcassets.png_b64). Usage: pack.py [--out DIR] RENDERS.json ...
A boss whose picture lives in side_bosses.json ("img": the GeckoLib renders and the pictures once taken from fandom/wiki.gg
pages) gets its new one there, with img_src "render"; the others go to side_imgs.json (SIMG), merged: the portraits it is given
replace those of the same name, the rest stay. --out DIR writes DIR/side_imgs.json (the whole merged file) and
DIR/side_bosses_img.json ({boss: data URL}, for side_bosses.json) instead of touching build/patches."""
import json, sys, base64, io, pathlib, os
from PIL import Image
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from mcassets import png_b64
H = pathlib.Path(__file__).resolve().parents[2] / "patches"
# not in the wiki's boss list (app.js drops them), so their pictures would never show
DROP = {"Yeti", "Infernal Dragon", "Nameless Guardian"}
a = sys.argv[1:]; out_dir = a[a.index("--out") + 1] if "--out" in a else None
ins = [x for i, x in enumerate(a) if x != "--out" and (i == 0 or a[i - 1] != "--out")]
SB = json.loads((H / "side_bosses.json").read_text(encoding="utf-8"))
F = H / "side_imgs.json"; simg = json.loads(F.read_text(encoding="utf-8")) if F.exists() else {}; sbimg = {}
for f in ins:
    for k, v in json.load(open(f)).items():
        if k in DROP: continue
        im = Image.open(io.BytesIO(base64.b64decode(v.split(",", 1)[-1]))).convert("RGBA")
        if im.size != (256, 256): print("not 256 px, left out:", k, im.size); continue
        (sbimg if SB.get(k, {}).get("img") else simg)[k] = "data:image/png;base64," + png_b64(im)
if out_dir:
    os.makedirs(out_dir, exist_ok=True)
    json.dump(simg, open(out_dir + "/side_imgs.json", "w"), ensure_ascii=False, indent=0, sort_keys=True)
    json.dump(sbimg, open(out_dir + "/side_bosses_img.json", "w"), ensure_ascii=False, indent=0, sort_keys=True)
else:
    F.write_text(json.dumps(simg, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
    for k, v in sbimg.items(): SB[k]["img"], SB[k]["img_src"] = v, "render"
    (H / "side_bosses.json").write_text(json.dumps(SB, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(simg), "in side_imgs.json,", sum(len(v) for v in simg.values()) // 1024, "kB;", len(sbimg), "for side_bosses.json,",
      sum(len(v) for v in sbimg.values()) // 1024, "kB")
