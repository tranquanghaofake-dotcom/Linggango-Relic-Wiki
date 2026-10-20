"""Boss summon guide from the pack: summon item, where/how to use it (the mod's own item tooltip),
its recipe as a 3×3 grid (pack KubeJS recipe wins over the jar's), and where each ingredient comes from.
Usage: summons.py W out.json"""
import json, re, sys, zipfile, glob
W, OUT = sys.argv[1], sys.argv[2]
J = glob.glob(W + "/pack/mods/Armageddon for 1.20.1*.jar")[0]
z = zipfile.ZipFile(J); L = json.loads(z.read("assets/armageddon_mod/lang/en_us.json"))
lang = json.load(open(W + "/lang.json")); rec = json.load(open(W + "/rec.json"))
for m in re.finditer(r"renameItem\('([^']+)',\s*'([^']+)'\)", open(W + "/pack/src/overrides/kubejs/client_scripts/lang.js").read()): lang[m.group(1)] = m.group(2)
clean = lambda t: re.sub(r"§.", "", t).strip()
nm = lambda i: clean(lang.get(i, i.split(":")[1].replace("_", " ").title()))
BOSS = {"iron_colossus": "iron_remote", "goblin_lord": "strange_coin", "arion": "emerald_totem", "eldorath": "builder_stone",
        "zoranth_forgotten": "fiery_wither_skull", "elvenite_paladin": "titan_insigna", "vaedric": "wanderers_fallen_shard",
        "bringer_of_doom": "the_key_of_doom", "discord": "sigil_of_calamity", "famine": "sigil_of_calamity", "chaos": "sigil_of_calamity",
        "sanghor": "cocoon_of_blood", "zoranth_newborn": "the_sun_emblem", "nyxaris": "the_corrupted_tear"}
JEI = {"iron_remote": "iron_remote", "strange_coin": "strange_coin", "emerald_totem": "emerald_totem", "builder_stone": "builder_stone",
       "fiery_wither_skull": "fiery_wither_skull", "titan_insigna": "titans_insigna", "wanderers_fallen_shard": "wanderers_fallen_shard",
       "the_key_of_doom": "key_of_doom", "sigil_of_calamity": "sigil_of_calamities", "cocoon_of_blood": "cocoon_of_blood",
       "the_sun_emblem": "sun_emblem", "the_corrupted_tear": "corrupted_tear"}
kjs = {}
for f in glob.glob(W + "/pack/src/overrides/kubejs/server_scripts/**/*.js", recursive=True):
    src = open(f).read()
    for m in re.finditer(r'e\.shaped\(\s*"([^"]+)"\s*,\s*\[([^\]]*)\]\s*,\s*\{([^}]*)\}', src):
        pat = re.findall(r'"([^"]*)"', m.group(2)); key = dict(re.findall(r'([A-Z])\s*:\s*"([^"]+)"', m.group(3)))
        kjs.setdefault(m.group(1), {"pattern": pat, "key": key, "src": "pack KubeJS"})
removed = set()
for f in glob.glob(W + "/pack/src/overrides/kubejs/server_scripts/**/*.js", recursive=True):
    removed |= set(re.findall(r"\.remove\(\{\s*id:\s*['\"]([^'\"]+)['\"]", open(f).read()))
def jar_recipe(item):
    for r in rec["recipes"].get(item, []):
        if r["id"] in removed or not r["t"].startswith("minecraft:crafting"): continue
        ns, p = r["id"].split(":", 1)
        for n in (f"data/{ns}/recipes/{p}.json",):
            if n in z.namelist():
                o = json.loads(z.read(n))
                if "pattern" in o:
                    key = {k: (v.get("item") or "#" + v.get("tag", "")) if isinstance(v, dict) else (v[0].get("item") if isinstance(v, list) else v) for k, v in o["key"].items()}
                    return {"pattern": o["pattern"], "key": key, "src": "Armageddon"}
def grid(r):
    g = []
    for row in r["pattern"]:
        g.append([r["key"].get(c) if c != " " else None for c in row.ljust(3)])
    return g
def where(i):
    lt = rec["loot"].get(i, [])
    bag = [t for t in lt if "treasure_bag" in t or "bag" in t.split("/")[-1]]
    if bag: return "treasure bag: " + ", ".join(sorted({b.split("/")[-1].replace("_", " ") for b in bag}))[:120]
    if rec["recipes"].get(i): return "crafted"
    if lt: return "loot: " + ", ".join(sorted({t.split(":")[1].split("/")[-1].replace("_", " ") for t in lt}))[:120]
    return ""
out = {}
for boss, it in BOSS.items():
    iid = "armageddon_mod:" + it
    use = " ".join(clean(L.get(f"item.armageddon_mod.{it}.description_{n}", "")) for n in (1, 2)).strip()
    info = clean(L.get(f"jei.armageddon_mod.{JEI[it]}_info", ""))
    r = kjs.get(iid) or jar_recipe(iid)
    g = grid(r) if r else None
    ings = sorted({c for row in (g or []) for c in row if c})
    inf = None
    for cand in ("infinite_" + it, "infinite_" + it.replace("the_", "")):
        ii = "armageddon_mod:" + cand
        if ii in rec["recipes"]:
            ri = kjs.get(ii) or jar_recipe(ii)
            inf = {"item": ii, "name": nm(ii), "recipe": grid(ri) if ri else None,
                   "ings": [{"id": c, "n": nm(c) if not c.startswith("#") else "any " + c.split("/")[-1].replace("_", " ")} for c in sorted({c for row in (grid(ri) if ri else []) for c in row if c})]}
            break
    out[boss] = {"item": iid, "name": nm(iid), "use": use, "info": info, "recipe": g, "recipe_src": r and r["src"],
                 "infinite": inf,
                 "ings": [{"id": i, "n": nm(i) if not i.startswith("#") else "any " + i.split("/")[-1].replace("_", " "), "from": where(i) if not i.startswith("#") else ""} for i in ings]}
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
for k, v in out.items(): print(k, "|", v["name"], "|", v["use"][:70], "|", v["recipe_src"], [x["n"] + " (" + x["from"] + ")" for x in v["ings"]])
