#!/usr/bin/env python3
"""Recipe grids for curios that had none (their page only listed the ingredients from the source line, in a row).

For every crafted curio without a grid, finds the recipe that makes it (Crafting Table shaped or shapeless, Blood Magic's
Hellfire Forge and Alchemy Array) in the order the game applies them: a recipe the pack's KubeJS scripts add
(kubejs_recipes.js runs them), else a datapack recipe in kubejs/data, else the mod jar's own; a recipe the scripts remove
(by id or by output) does not count. The pack's recipe wins over the wiki's source line (written earlier, sometimes from
the mod's own recipe or naming only the main ingredients); curios whose line names other ingredients are printed.
Writes build/patches/curio_recipes.json {"grids": {curio id: grid in data.js's `gr` shape}, "names": {ingredient id: name}}
and adds icons for new ingredients to gear_icons.json; patches/curio_recipes.py puts them in.

Usage: python3 build/pack_audit/curio_recipes.py <dir with *.jar of the pack> <the pack's overrides/kubejs>"""
import sys, json, glob, zipfile, re, pathlib, subprocess, os
B = pathlib.Path(__file__).resolve().parents[1]
src = (B / "src" / "data.js").read_text(encoding="utf-8"); D, _ = json.JSONDecoder().raw_decode(src, 8)
NAMEID = json.loads((B / "patches" / "name_ids.json").read_text(encoding="utf-8")); ID2N = {v: k for k, v in NAMEID.items()}
for d in D: ID2N.setdefault(d["id"], d["n"])
want = {d["id"]: d for d in D if d.get("g") == "Craft" and (not d.get("gr") or d.get("grx"))}   # grx: a grid it wrote last time
lang = {}
zips = [zipfile.ZipFile(f) for f in sorted(glob.glob(sys.argv[1] + "/*.jar"))]
for z in zips:
    for n in z.namelist():
        if re.match(r"assets/[^/]+/lang/en_us\.json$", n):
            try: dd = json.loads(z.read(n).decode("utf-8", "replace"))
            except Exception: continue
            for k, v in dd.items():
                m = re.match(r"(?:item|block)\.([a-z0-9_.-]+)\.([a-z0-9_/.-]+)$", k)
                if m and isinstance(v, str): lang.setdefault(m.group(1) + ":" + m.group(2), v)
def ing(o):
    if isinstance(o, list): o = o[0] if o else {}
    if not isinstance(o, dict): return None
    if "item" in o: return [o["item"], ""]
    if "tag" in o: return ["", "#" + o["tag"]]
    return None
def grid(shaped, pattern, key, ingredients, n):
    if shaped:
        w = max(len(x) for x in pattern)
        cells = [key.get(ch) if ch != " " else None for row in pattern for ch in row.ljust(w)]
        return {"w": w, "h": len(pattern), "c": cells, "st": "Crafting Table", "n": n, "l": 0}
    return {"w": min(3, len(ingredients)), "h": (len(ingredients) + 2) // 3, "c": ingredients, "st": "Crafting Table (shapeless)", "n": n, "l": 1}
KJ = sys.argv[2]
ks = json.loads(subprocess.run(["node", str(pathlib.Path(__file__).with_name("kubejs_recipes.js")), KJ], capture_output=True, text=True, check=True).stdout)
gone_id = {r["id"] for r in ks["removed"] if isinstance(r, dict) and isinstance(r.get("id"), str)}
gone_out = {r["output"] for r in ks["removed"] if isinstance(r, dict) and isinstance(r.get("output"), str)}
cell = lambda x: None if not x else ["", x] if x.startswith("#") else [x, ""]
found, how = {}, {}
for a in ks["added"]:
    o = a.get("output")
    if o in want and o not in found and (a.get("pattern") or a.get("ingredients")):
        found[o] = grid(a["type"] == "shaped", a.get("pattern"), {k: cell(v) for k, v in (a.get("key") or {}).items()}, [cell(x) for x in a.get("ingredients") or []], a.get("count", 1)); how[o] = "KubeJS script"
def files():
    for f in sorted(glob.glob(KJ + "/data/*/recipes/**/*.json", recursive=True)):
        rel = os.path.relpath(f, KJ + "/data").split(os.sep); yield "kubejs data", rel[0] + ":" + "/".join(rel[2:])[:-5], open(f, "rb").read()
    for z in zips:
        for n in z.namelist():
            m = re.match(r"data/([^/]+)/recipes/(.*)\.json$", n)
            if m: yield "mod jar", m.group(1) + ":" + m.group(2), z.read(n)
for src_, rid, b in files():
    if rid in gone_id: continue
    try: o = json.loads(b)
    except Exception: continue
    if not isinstance(o, dict): continue
    if o.get("type") == "forge:conditional":
        o = next((r.get("recipe") for r in o.get("recipes", []) if isinstance(r, dict)), {}) or {}
    r = o.get("result") or o.get("output"); out = r if isinstance(r, str) else (r or {}).get("item") if isinstance(r, dict) else None
    if out not in want or out in found or out in gone_out: continue
    t, n = o.get("type", ""), (r.get("count", 1) if isinstance(r, dict) else 1)
    if t.endswith("crafting_shaped") and o.get("pattern"):
        found[out] = grid(True, o["pattern"], {k: ing(v) for k, v in o.get("key", {}).items()}, None, n); how[out] = src_
    elif t.endswith("crafting_shapeless") and o.get("ingredients"):
        found[out] = grid(False, None, None, [ing(x) for x in o["ingredients"]], n); how[out] = src_
    elif t == "bloodmagic:soulforge":       # Hellfire Forge: up to four inputs, any order, plus the Demon Will it needs
        found[out] = dict(grid(False, None, None, [ing(o[k]) for k in ("input0", "input1", "input2", "input3") if o.get(k)], n), st="Hellfire Forge (Blood Magic)"); how[out] = src_
    elif t == "bloodmagic:array":           # Alchemy Array: the base item, then the one added to it
        found[out] = dict(grid(False, None, None, [ing(o[k]) for k in ("baseinput", "addedinput") if o.get(k)], n), st="Alchemy Array (Blood Magic)"); how[out] = src_
# keep a recipe only when the source line names the same ingredients
def names(c): return {(ID2N.get(c[0]) or lang.get(c[0]) or "").lower() for c in c if c and c[0]}
keep, rej = {}, []  # rej: the source line does not name every ingredient
for i, g in found.items():
    line = " ".join(want[i]["src"]).lower()
    ns = names(g["c"]) - {""}
    keep[i] = g
    if not all(n in line for n in ns): rej.append(i); print("  line does not name:", i, f"({how[i]})", sorted(ns - {n for n in ns if n in line}))
# names and icons for ingredients the wiki has neither for (the recipe slots and the ingredient list show them)
src_all = (B / "src" / "data.js").read_text(encoding="utf-8"); NM, _ = json.JSONDecoder().raw_decode(src_all, src_all.find(",NM=") + 4)
GI = json.loads((B / "patches" / "gear_icons.json").read_text(encoding="utf-8"))
ICK = set(re.findall(r'"([a-z0-9_.-]+:[a-z0-9_/.-]+)":"iVBOR', src_all)) | set(GI)
def rd(p):
    for z in zips:
        try: return z.read(p)
        except KeyError: pass
def model(x, d=0):
    ns, p = x.split(":", 1) if ":" in x else ("minecraft", x)
    b = rd(f"assets/{ns}/models/{p}.json")
    if not b or d > 8: return {}
    try: m = json.loads(b)
    except Exception: return {}
    tex = {}
    if isinstance(m.get("parent"), str) and not m["parent"].startswith("builtin"): tex.update(model(m["parent"], d + 1).get("textures", {}))
    tex.update(m.get("textures", {})); m["textures"] = tex; return m
def icon(i):                         # the item's first layer (first frame of an animation), else its block's face
    import io, base64
    from PIL import Image
    ns, n = i.split(":", 1); t = model(f"{ns}:item/{n}").get("textures", {})
    for L in [t.get("layer0"), t.get("particle") or t.get("all") or t.get("side"), f"{ns}:item/{n}", f"{ns}:block/{n}"]:
        while isinstance(L, str) and L.startswith("#"): L = t.get(L[1:])
        if not isinstance(L, str): continue
        lns, lp = L.split(":", 1) if ":" in L else ("minecraft", L)
        b = rd(f"assets/{lns}/textures/{lp}.png")
        if not b: continue
        im = Image.open(io.BytesIO(b)).convert("RGBA"); w, h = im.size
        if h > w and h % w == 0: im = im.crop((0, 0, w, w))
        if im.size[0] > 64: continue
        bo = io.BytesIO(); im.save(bo, "PNG", optimize=True); return base64.b64encode(bo.getvalue()).decode()
names, icons, DIDS = {}, {}, {d["id"] for d in D}
for g in found.values():
    for c in g["c"]:
        if not c or not c[0] or c[0].startswith("minecraft:"): continue
        nm = ID2N.get(c[0]) or lang.get(c[0])
        if c[0] not in DIDS and nm and NM.get(c[0], nm) == nm: names[c[0]] = nm   # also the ones it added before
        if c[0] not in ICK:
            b = icon(c[0])
            if b: icons[c[0]] = b
if icons: GI.update(icons); (B / "patches" / "gear_icons.json").write_text(json.dumps(GI, ensure_ascii=False, separators=(",", ":"), sort_keys=True), encoding="utf-8")
print(f"ingredient names added: {len(names)}; icons added to gear_icons.json: {len(icons)}")
keep = {"grids": keep, "names": names}
(B / "patches" / "curio_recipes.json").write_text(json.dumps(keep, ensure_ascii=False, separators=(",", ":"), sort_keys=True), encoding="utf-8")
print(f"crafted curios without a grid: {len(want)}; recipe found in the jars: {len(found)}; written: {len(keep['grids'])}; source line names other ingredients: {len(rej)}")
