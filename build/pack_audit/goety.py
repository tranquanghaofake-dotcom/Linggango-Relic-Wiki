"""Goety rituals as the pack ships them: ritual types (requirements + example picture from the Black Book),
and every ritual recipe from Goety and its addons, with the pack's KubeJS datapack recipes on top and
KubeJS removals taken out. Usage: goety.py W out.json"""
import json, re, sys, zipfile, glob, base64, collections, os
W, OUT = sys.argv[1], sys.argv[2]
M = W + "/pack/mods/"
JARS = [os.path.basename(glob.glob(M + p)[0]) for p in ("goety-2*.jar", "GoetyRevelation-*.jar", "goety_cataclysm-*.jar", "goetydelight-*.jar", "goetyhostility-*.jar", "goetyawaken-*.jar") if glob.glob(M + p)]
lang = json.load(open(W + "/lang.json"))
for m in re.finditer(r"renameItem\('([^']+)',\s*'([^']+)'\)", open(W + "/pack/src/overrides/kubejs/client_scripts/lang.js").read()): lang[m.group(1)] = m.group(2)
ent = {}
VL = json.load(open(W + "/mc_en_us.json"))  # vanilla 1.20.1 lang, from the client jar
for k, v in VL.items():
    mm = re.match(r"(item|block)\.minecraft\.([a-z0-9_]+)$", k)
    if mm and ("minecraft:" + mm.group(2)) not in lang: lang["minecraft:" + mm.group(2)] = v
    mm = re.match(r"entity\.minecraft\.([a-z0-9_]+)$", k)
    if mm: ent["minecraft:" + mm.group(1)] = v
    mm = re.match(r"enchantment\.minecraft\.([a-z0-9_]+)$", k)
    if mm: ent["ench:minecraft:" + mm.group(1)] = v
for j in glob.glob(M + "*.jar"):
    try: z = zipfile.ZipFile(j)
    except Exception: continue
    for n in z.namelist():
        if re.match(r"assets/[^/]+/lang/en_us\.json$", n):
            try:
                for k, v in json.loads(z.read(n).decode("utf-8", "ignore")).items():
                    mm = re.match(r"entity\.([a-z0-9_]+)\.([a-z0-9_]+)$", k)
                    if mm: ent[mm.group(1) + ":" + mm.group(2)] = v
                    mm = re.match(r"(item|block)\.([a-z0-9_]+)\.([a-z0-9_/]+)$", k)
                    if mm and (mm.group(2) + ":" + mm.group(3)) not in lang: lang[mm.group(2) + ":" + mm.group(3)] = v
                    mm = re.match(r"enchantment\.([a-z0-9_]+)\.([a-z0-9_]+)$", k)
                    if mm: ent["ench:" + mm.group(1) + ":" + mm.group(2)] = v
            except Exception: pass
clean = lambda t: re.sub(r"§.", "", str(t)).strip()
def nm(x):
    if isinstance(x, dict):
        if "item" in x: return clean(lang.get(x["item"], x["item"].split(":")[-1].replace("_", " ").title()))
        if "tag" in x: return "any " + x["tag"].split(":")[-1].split("/")[-1].replace("_", " ")
    if isinstance(x, list) and x: return " or ".join(nm(y) for y in x[:2])
    return str(x)
iid = lambda x: x.get("item") if isinstance(x, dict) else (x[0].get("item") if isinstance(x, list) and x and isinstance(x[0], dict) else None)
removed = set()
for f in glob.glob(W + "/pack/src/overrides/kubejs/server_scripts/**/*.js", recursive=True):
    removed |= set(re.findall(r"\.remove\(\{\s*id:\s*['\"]([^'\"]+)['\"]", open(f).read()))
recs = {}
for j in JARS:
    z = zipfile.ZipFile(M + j)
    for n in z.namelist():
        mm = re.match(r"data/([^/]+)/recipes/(.+)\.json$", n)
        if not mm: continue
        try: o = json.loads(z.read(n))
        except Exception: continue
        if o.get("type") == "goety:ritual": recs[mm.group(1) + ":" + mm.group(2)] = (o, j)
for f in glob.glob(W + "/pack/src/overrides/kubejs/data/*/recipes/**/*.json", recursive=True):
    mm = re.search(r"data/([^/]+)/recipes/(.+)\.json$", f)
    try: o = json.load(open(f))
    except Exception: continue
    if o.get("type") == "goety:ritual": recs[mm.group(1) + ":" + mm.group(2)] = (o, "pack")
rows = []
for rid, (o, src) in recs.items():
    if rid in removed: continue
    rt = o.get("ritual_type", "").split(":")[-1]
    ings = collections.Counter(nm(i) for i in o.get("ingredients", []))
    res = o.get("result") or {}
    r = {"id": rid, "kind": rt, "type": o.get("craftType"), "soul": o.get("soulCost"), "dur": o.get("duration"),
         "act": nm(o.get("activation_item")), "act_id": iid(o.get("activation_item")),
         "ings": [f"{c}× {n}" if c > 1 else n for n, c in ings.items()], "src": src}
    if rt.startswith("craft"):
        r["out"] = nm(res); r["out_id"] = iid(res); n = res.get("count", 1) if isinstance(res, dict) else 1
        if n > 1: r["out"] = f"{n}× " + r["out"]
    elif rt.startswith("summon"):
        e = o.get("entity_to_summon", ""); e = (e.get("entity") or e.get("type") or "") if isinstance(e, dict) else e; r["out"] = "Summon " + clean(ent.get(e, e.split(":")[-1].replace("_", " ").title())) + (" (tamed)" if "tamed" in rt else "")
    elif rt.startswith("convert"):
        def ev(v):
            if isinstance(v, dict):
                dn = v.get("display_name", "")
                if dn.startswith("entity."): return ".".join(dn.split(".")[1:3]).replace(".", ":", 1)
                return v.get("entity") or v.get("type") or (v.get("tag", "").split(":")[-1].rstrip("s"))
            return v or ""
        a, b = ev(o.get("entity_to_convert")), ev(o.get("entity_to_convert_into"))
        r["out"] = f"Turn {clean(ent.get(a, a.split(':')[-1].replace('_',' ').title()))} into {clean(ent.get(b, b.split(':')[-1].replace('_',' ').title()))}" + (" (tamed)" if "tamed" in rt else "")
    elif rt == "enchant":
        e = o.get("enchantment", ""); r["out"] = "Enchant: " + clean(ent.get("ench:" + e, e.split(":")[-1].replace("_", " ").title())); r["xp"] = o.get("xpLevelCost")
    elif rt == "locate":
        st = o.get("structure_to_locate") or o.get("structure") or ""
        st = (st.get("tag") or st.get("structure") or "") if isinstance(st, dict) else st
        nmst = st.split(":")[-1].split("/")[-1]
        nmst = {"eye_of_ender_located": "stronghold", "on_woodland_explorer_maps": "woodland_mansion"}.get(nmst, nmst)
        r["out"] = "Locate " + (nmst.replace("_", " ").title() or "a structure")
    elif rt == "teleport": r["out"] = "Teleport to a Waystone"
    else: r["out"] = rt
    for k in ("weather", "time", "research"):
        if o.get(k): r[k] = o[k]
    sx = o.get("entity_to_sacrifice")
    if sx:
        if isinstance(sx, dict):
            dn = sx.get("display_name", "")
            r["sacrifice"] = clean(ent.get(".".join(dn.split(".")[1:3]).replace(".", ":", 1), dn) if dn.startswith("entity.") else (dn or sx.get("entity") or sx.get("tag", "")))
        else: r["sacrifice"] = clean(ent.get(sx, sx))
    rows.append(r)
TYPES = {"animation": ("animation_ritual", "animalis_ritual"), "necroturgy": ("necroturgy_ritual", "necroturgy_ritual"), "forge": ("forge_ritual", "forge_ritual"),
         "magic": ("magic_ritual", "magic_ritual"), "sabbath": ("sabbath_ritual", "sabbath_ritual"), "adept_nether": ("adept_nether_ritual", "adept_nether"),
         "expert_nether": ("expert_nether_ritual", "expert_nether"), "deep": ("deep_ritual", "deep_ritual"), "divination": ("divination_ritual", "divination_ritual"),
         "end": ("end_ritual", "end_ritual"), "frost": ("frost_ritual", "frost_ritual"), "geoturgy": ("geoturgy_ritual", "geoturgy_ritual"),
         "overgrown": ("overgrown_ritual", "overgrown_ritual"), "sky": ("sky_ritual", "sky_ritual"), "storm": ("storm_ritual", "storm_ritual"),
         "master_forge": ("master_forge_ritual", "master_forge_ritual"), "culinary": ("culinary_rituals", None)}
def book(entry):
    for j in JARS:
        z = zipfile.ZipFile(M + j); n = f"assets/goety/patchouli_books/black_book/en_us/entries/rituals/{entry}.json"
        if n in z.namelist(): return json.loads(z.read(n)), z
    return None, None
types = {}
for t, (entry, pic) in TYPES.items():
    o, z = book(entry)
    if not o: continue
    texts = [re.sub(r"\$\([^)]*\)", "", p.get("text", "")) for p in o["pages"] if p.get("type") == "patchouli:text"]
    raw = next((p.get("text", "") for p in o["pages"] if p.get("text", "").startswith("Requirements")), "")
    req = [re.sub(r"\$\([^)]*\)", "", x).strip() for x in re.split(r"\$\(li\)", raw)[1:]] or [texts[0]]
    img = None
    for p in o["pages"]:
        for im in p.get("images", []) or []:
            pth = "assets/" + im.replace(":", "/", 1)
            for zj in [z] + [zipfile.ZipFile(M + j) for j in JARS]:
                if pth in zj.namelist(): img = base64.b64encode(zj.read(pth)).decode(); break
            if img: break
    types[t] = {"name": o["name"], "req": req, "lore": next((x for x in texts if not x.startswith("Requirements")), ""), "img": img}
cnt = collections.Counter(r["type"] for r in rows)
out = {"range": 8, "types": types, "rituals": sorted(rows, key=lambda r: (r["type"] or "", r["kind"], r["out"])), "counts": cnt}
from PIL import Image
import io
for t in out["types"].values():
    if t["img"]:
        im = Image.open(io.BytesIO(base64.b64decode(t["img"])))
        if "A" in im.getbands(): im = im.crop(im.getchannel("A").getbbox())  # Patchouli draws only the opaque part; transparency would turn black
        im = im.convert("RGB"); w, h = im.size
        assert any(im.getpixel((w - 1, y)) != (0, 0, 0) for y in range(h)) and any(im.getpixel((x, h - 1)) != (0, 0, 0) for x in range(w)), "all-black edge in a ritual type picture"
        b = io.BytesIO(); im.save(b, "WEBP", quality=78); t["img"] = base64.b64encode(b.getvalue()).decode()
# type names as JEI's ritual category shows them (jei.goety.craftType.<type>), not the book entry titles
JL = {}
for j in JARS:
    z = zipfile.ZipFile(M + j)
    for n in z.namelist():
        if re.match(r"assets/[^/]+/lang/en_us\.json$", n): JL.update({k: v for k, v in json.loads(z.read(n).decode("utf-8", "ignore")).items() if k.startswith("jei.goety.craftType.")})
def tname(t):
    k = "jei.goety.craftType." + t
    assert k in JL, "missing lang key " + k
    return JL[k] + " Ritual"
for t in out["types"]: out["types"][t]["name"] = tname(t)
out["types"]["te_magic"] = {"name": tname("te_magic") + " (Goety Revelation)", "req": ["Set in Goety Revelation's code; no block list ships in the pack files"], "lore": "", "img": None}
out["types"]["the_end"] = {"name": tname("the_end") + " (Goety Revelation)", "req": ["Set in Goety Revelation's code; needs the Forbidden research and a player sacrifice"], "lore": "", "img": None}
out["research"] = {k: clean(lang.get(f"goety:{k}_scroll", k)) for k in ["ravaging", "warred", "buried", "haunting", "front", "mistral", "floral", "bygone", "terminus", "forbidden"]}
out["research"]["lord"] = "the Lord research (Goety Revelation: \u201cforging secrets of divine artifacts\u201d)"
out["research"]["viziers_cookbook"] = "Viziers Cookbook (Goety Delight)"
G = json.load(open(W + "/gated_items.json"))
for r in out["rituals"]:
    t = [G[x] for x in (r.get("out_id"), r.get("act_id")) if x and x in G]
    if t: r["gate"] = max(t)
    if r["id"] == "goety_revelation:the_end_ritual" and not r.get("sacrifice"): r["sacrifice"] = "a player"
out["base_gate"] = {n: G.get(i) for n, i in [("Dark Altar", "goety:dark_altar"), ("Pedestal", "goety:pedestal"), ("Cursed Cage", "goety:cursed_cage"), ("Totem of Souls", "goety:totem_of_souls"), ("Dark Wand", "goety:dark_wand")]}
json.dump(out, open(OUT, "w"), ensure_ascii=False, separators=(",", ":"))
print(len(rows), "rituals;", {k: cnt[k] for k in sorted(cnt, key=lambda x: -cnt[x])})
print("types with book text:", sorted(types), "missing:", sorted(set(cnt) - set(types)))
print([r for r in rows if r["src"] == "pack"][:3])
