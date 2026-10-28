#!/usr/bin/env python3
"""Names the wiki writes as text, turned into the pack's own items and icons.

The curio and gear pages draw recipes, stations, drops and tag ingredients as slots. Where a name had no item id (an
ingredient only named in a source line, a station block, a tag such as #forge:robes, a modded mob) the slot showed the
name as text or a stand-in. This reads the pack's jars:
  - every en_us lang file (item.* / block.* / entity.* keys) -> display name to id
  - item tags (data/*/tags/items/**.json) -> one real member per tag
  - item models -> the icon (item layers, else the block's particle face; first frame of an animation)
and adds what is missing to build/patches/name_ids.json (NAMEID), tag_ids.json (TAGID), mob_ids.json (MOBID: mob name ->
entity id and spawn egg) and gear_icons.json (IC). Run apply_all.sh afterwards.

Usage: python3 build/pack_audit/name_icons.py <pack dir with files/<project>/*.jar>"""
import sys, json, glob, zipfile, io, base64, re, pathlib
from PIL import Image
PK = pathlib.Path(sys.argv[1]); P = pathlib.Path(__file__).resolve().parents[1] / "patches"; SRC = P.parent / "src"
J = lambda f: json.loads((P / f).read_text(encoding="utf-8")) if (P / f).exists() else {}
zips = []
for f in sorted(glob.glob(str(PK / "files" / "*" / "*.jar"))):
    try: z = zipfile.ZipFile(f); zips.append((z, set(z.namelist())))
    except Exception: pass
def rd(p):
    for z, n in zips:
        if p in n: return z.read(p)
# 1. lang
names, ents = {}, {}
for z, n in zips:
    for p in n:
        if not re.match(r"assets/[^/]+/lang/en_us\.json$", p): continue
        try: d = json.loads(z.read(p).decode("utf-8", "replace"))
        except Exception: continue
        for k, v in d.items():
            m = re.match(r"(item|block|entity)\.([a-z0-9_.-]+)\.([a-z0-9_/.-]+)$", k)
            if not m or not isinstance(v, str): continue
            v = re.sub(r"§.", "", v).strip(); i = m.group(2) + ":" + m.group(3)
            (ents if m.group(1) == "entity" else names).setdefault(v, [])
            L = (ents if m.group(1) == "entity" else names)[v]
            if i not in L: L.append(i)
# 2. tags
tags = {}
def tagvals(t, d=0):
    if d > 5: return []
    ns, p = t.lstrip("#").split(":", 1); out = []
    for z, n in zips:
        b = z.read(f"data/{ns}/tags/items/{p}.json") if f"data/{ns}/tags/items/{p}.json" in n else None
        if not b: continue
        try: vs = json.loads(b).get("values", [])
        except Exception: continue
        for v in vs:
            v = v["id"] if isinstance(v, dict) else v
            out += tagvals(v, d + 1) if v.startswith("#") else [v]
    return out
# 3. icons
def model(x, d=0):
    ns, p = x.split(":", 1) if ":" in x else ("minecraft", x)
    b = rd(f"assets/{ns}/models/{p}.json")
    if not b or d > 8: return {}
    try: m = json.loads(b)
    except Exception: return {}
    tex = {}
    if isinstance(m.get("parent"), str) and not m["parent"].startswith("builtin"): tex.update(model(m["parent"], d + 1).get("textures", {}))
    tex.update(m.get("textures", {})); m["textures"] = tex; return m
def frame(b):
    im = Image.open(io.BytesIO(b)).convert("RGBA"); w, h = im.size
    return im.crop((0, 0, w, w)) if h > w and h % w == 0 else im
def icon(i):
    ns, n = i.split(":", 1); t = model(f"{ns}:item/{n}").get("textures", {})
    layers = [t[k] for k in sorted(t) if re.match(r"layer\d+$", k)]
    if not layers: layers = [t.get("particle") or t.get("side") or t.get("front") or t.get("all") or t.get("texture")] if t else []
    if not layers or not layers[0]: layers = [f"{ns}:item/{n}", f"{ns}:block/{n}"]
    im = None
    for L in layers:
        while isinstance(L, str) and L.startswith("#"): L = t.get(L[1:])
        if not isinstance(L, str): continue
        lns, lp = L.split(":", 1) if ":" in L else ("minecraft", L)
        b = rd(f"assets/{lns}/textures/{lp}.png")
        if not b: continue
        try: f = frame(b)
        except Exception: continue
        if im is None: im = f
        else: im.alpha_composite(f if f.size == im.size else f.resize(im.size, Image.NEAREST))
        if not t.get("layer1"): break
    if im is None or im.size[0] > 64: return None
    bo = io.BytesIO(); im.save(bo, "PNG", optimize=True); return base64.b64encode(bo.getvalue()).decode()
# what the pages name
text = (SRC / "data.js").read_text(encoding="utf-8"); gtext = (SRC / "gear_data.js").read_text(encoding="utf-8")
want = set()
for m in re.finditer(r'(?:Craft|Combine|Infuse|Forge|Upgrade|Imbue|Perform)[^"]*? (?:from|with|:) ([^"]+?)\.?"', text):
    for x in re.split(r",\s*|\s+and\s+", m.group(1)): want.add(x.strip(" .…"))
for m in re.finditer(r'"st":"([^"]+)"', text): want.add(re.sub(r"\s*\(.*\)$", "", m.group(1)))
want |= {"Enchanting Apparatus", "Arcane Pedestal", "Tinkerer's Workshop", "Upgrade Forge", "Blood Altar", "Natural Altar", "Offering Table",
         "Wood Stand", "Imbuement Chamber", "Mixing Cauldron", "Dark Altar", "Pedestal", "Cursed Infuser", "Accessory Box", "Suspicious Bag"}
mobs = set(re.findall(r"[Dd]ropped by ([A-Z][^(;\"]+?)\s*\(", text)) | {m.replace("_", " ").title() for m in re.findall(r'entities/([a-z0-9_]+)"', gtext)}
NI, IC = J("name_ids.json"), J("gear_icons.json")
# lang names that carry a suffix in game ("Tinkerer's Workshop (WIP)") or a station under another name
NI.update({"Tinkerer's Workshop": "armageddon_mod:tinkerer_workshop", "Wood Stand": "naturesaura:wood_stand"})
have = set(re.findall(r'"([a-z0-9_.-]+:[a-z0-9_/.-]+)":"iVBOR', text + gtext)) | set(IC)
add = 0
for w in sorted(want):
    if not w or w in NI or w not in names: continue
    ids = sorted(names[w], key=lambda i: (i.split(":")[0] == "minecraft", len(i)))
    NI[w] = ids[0]; add += 1
TG = {}
for t in sorted(set(re.findall(r'"(#[a-z0-9_.-]+:[a-z0-9_/.-]+)"', gtext + text))):
    vs = [v for v in tagvals(t) if not v.startswith("minecraft:")] or tagvals(t)
    if vs: TG[t] = vs[0]
MO = {}
for m in sorted(mobs):
    e = (ents.get(m) or ents.get(m.rstrip("s")) or [None])[0]
    if not e: continue
    egg = e + "_spawn_egg"; MO[m] = [e, egg]
need = {v for v in list(NI.values()) + list(TG.values()) + [x[1] for x in MO.values()] if v not in have}
got = 0
for i in sorted(need):
    b = icon(i)
    if b: IC[i] = b; got += 1
MO = {k: v for k, v in MO.items() if v[1] in IC or v[1] in have}
for f, d in (("name_ids.json", NI), ("tag_ids.json", TG), ("mob_ids.json", MO), ("gear_icons.json", IC)):
    (P / f).write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":"), sort_keys=True), encoding="utf-8")
print(f"names +{add} (of {len(want)} wanted), tags {len(TG)}, mobs with an egg icon {len(MO)} (of {len(mobs)}), icons +{got} (of {len(need)})")
