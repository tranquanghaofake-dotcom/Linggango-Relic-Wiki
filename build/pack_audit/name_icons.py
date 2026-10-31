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
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))   # mcassets, block_render (also under python3 -I)
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
# 3. icons: the inventory picture (mcassets.py): flat layers, block models in the GUI view at 32 px, else the
# particle face, else the item or block texture of the same name
import mcassets
A = mcassets.Assets(rd=rd)
def icon(i):
    ns, n = mcassets.rl(i)
    im = A.icon(i, 32)
    if im is None:
        m = A.model(f"{ns}:item/{n}")
        im = A.texture(A.resolve(m, m["textures"].get("particle"))) if m else None
    if im is None: im = A.texture(f"{ns}:item/{n}") or A.texture(f"{ns}:block/{n}")
    if im is None or im.size[0] > 64: return None
    return mcassets.png_b64(im)
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
# stations with no flat texture, only a 3D model: drawn as the inventory draws a block (block_render.py)
import block_render
for i, how in (("bloodmagic:altar", ("obj", "assets/bloodmagic/models/bloodaltar.obj", "assets/bloodmagic/textures/models/altar.png")),
               ("somakespells:upgrade_forge", ("model", "somakespells:item/upgrade_forge"))):
    if i in IC: continue
    im = block_render.render_obj(how[1], how[2], rd, size=32) if how[0] == "obj" else block_render.render(how[1], rd, size=32)
    if im is not None: IC[i] = mcassets.png_b64(im)
MO = {k: v for k, v in MO.items() if v[1] in IC or v[1] in have}
for f, d in (("name_ids.json", NI), ("tag_ids.json", TG), ("mob_ids.json", MO), ("gear_icons.json", IC)):
    (P / f).write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":"), sort_keys=True), encoding="utf-8")
print(f"names +{add} (of {len(want)} wanted), tags {len(TG)}, mobs with an egg icon {len(MO)} (of {len(mobs)}), icons +{got} (of {len(need)})")
