"""Boss summon guide from the pack: summon item, where/how to use it (the mod's own item tooltip),
its recipe as a 3×3 grid (pack KubeJS recipe wins over the jar's), and where each ingredient comes from.
Usage: summons.py W out.json"""
import json, re, sys, zipfile, glob, os
W, OUT = sys.argv[1], sys.argv[2]
J = glob.glob(W + "/pack/mods/Armageddon for *1.20.1*.jar")[0]
z = zipfile.ZipFile(J); L = json.loads(z.read("assets/armageddon_mod/lang/en_us.json"))
lang = json.load(open(W + "/lang.json")); rec = json.load(open(W + "/rec.json"))
for m in re.finditer(r"renameItem\('([^']+)',\s*'([^']+)'\)", open(W + "/pack/src/overrides/kubejs/client_scripts/lang.js").read()): lang[m.group(1)] = m.group(2)
clean = lambda t: re.sub(r"§.", "", t).strip()
# the pack's full lang (item./block. keys) when W has it, and names lang.json does not hold (vanilla; Blood Magic's block lang)
PL = json.load(open(W + "/pack_lang.json")) if os.path.exists(W + "/pack_lang.json") else {}
NAMES = {"minecraft:gold_block": "Block of Gold", "minecraft:emerald_block": "Block of Emerald", "minecraft:diamond_block": "Block of Diamond",
           "minecraft:redstone_block": "Block of Redstone", "minecraft:iron_block": "Block of Iron", "minecraft:redstone": "Redstone Dust",
           "bloodmagic:blankrune": "Blank Rune"}
def nm(i):
    if i in NAMES: return NAMES[i]
    ns, p = i.split(":", 1)
    return clean(lang.get(i) or PL.get(f"item.{ns}.{p}") or PL.get(f"block.{ns}.{p}") or p.replace("_", " ").title())
tagn = lambda t: "any " + t.split("/")[-1].split(":")[-1].replace("_", " ")   # '#minecraft:small_flowers' -> 'any small flowers'
# boss_info.json drops: item -> (Keeper, the treasure bag that holds it); a bag's contents follow the bag in the list
BINFO = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "patches", "boss_info.json")))
BAGOF = {}
for bk, bv in BINFO.items():
    cur = None
    for x in bv.get("drops", []):
        if x.get("via") == "direct drop" and re.search(r"treasure_?bag", x["id"]): cur = x["n"]
        elif x.get("via") == "treasure bag" and cur: BAGOF.setdefault(x["id"], (bk, cur))
BIKEY = {"bringer_of_doom": "discord", "famine": "discord", "chaos": "discord"}   # summons key -> boss_info key
# items with a natural source: where() names it instead of 'crafted' (they all have some recipe)
NATURAL = {"minecraft:iron_ingot": "smelt mined Raw Iron", "minecraft:gold_ingot": "smelt mined Raw Gold", "minecraft:raw_gold": "mined (Gold Ore)",
           "minecraft:emerald": "mined, or villager trades", "minecraft:diamond": "mined", "minecraft:lapis_lazuli": "mined", "minecraft:redstone": "mined",
           "minecraft:coal": "mined", "minecraft:stone": "smelt Cobblestone", "minecraft:netherrack": "mined in the Nether", "minecraft:end_stone": "mined in the End",
           "minecraft:lava_bucket": "a Bucket filled from lava", "minecraft:nether_wart": "Nether Fortresses, then farmed", "minecraft:egg": "laid by Chickens",
           "minecraft:ender_pearl": "Enderman drop", "minecraft:sunflower": "Sunflower Plains", "undergarden:utherium_crystal": "mined in the Undergarden"}
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
def keyval(v):
    """recipe key -> item id; a list of options that holds Boss Souls (6.6.6) becomes linggango_tweaks:boss_soul"""
    if isinstance(v, dict): return v.get("item") or "#" + v.get("tag", "")
    if isinstance(v, list):
        if any(isinstance(x, dict) and x.get("item") == "linggango_tweaks:boss_soul" for x in v): return "linggango_tweaks:boss_soul"
        return v[0].get("item") if v and isinstance(v[0], dict) else None
    return v
def soul_opts(o):
    """the bosses whose soul fits the recipe's soul slot, and the other items that fit it"""
    for v in o.get("key", {}).values():
        if isinstance(v, list) and any(isinstance(x, dict) and x.get("item") == "linggango_tweaks:boss_soul" for x in v):
            return {"bosses": [x["nbt"]["boss"] for x in v if x.get("item") == "linggango_tweaks:boss_soul" and "boss" in x.get("nbt", {})],
                    "or": [x["item"] for x in v if x.get("item") and x.get("item") != "linggango_tweaks:boss_soul"]}
def jar_recipe(item):
    for r in rec["recipes"].get(item, []):
        if r["id"] in removed or not r["t"].startswith("minecraft:crafting"): continue
        ns, p = r["id"].split(":", 1)
        kj = f"{W}/pack/src/overrides/kubejs/data/{ns}/recipes/{p}.json"   # the pack's datapack override wins over the jar
        o = json.load(open(kj)) if os.path.exists(kj) else (json.loads(z.read(f"data/{ns}/recipes/{p}.json")) if f"data/{ns}/recipes/{p}.json" in z.namelist() else None)
        if o and "pattern" in o:
            return {"pattern": o["pattern"], "key": {k: keyval(v) for k, v in o["key"].items()}, "src": "pack datapack" if os.path.exists(kj) else "Armageddon", "soul": soul_opts(o)}
RT = {"create:mechanical_crafting": "Create Mechanical Crafter", "bloodmagic:alchemytable": "Blood Magic Alchemy Table",
      "ars_nouveau:enchanting_apparatus": "Ars Nouveau Enchanting Apparatus", "immersiveengineering:blueprint": "Immersive Engineering Engineer's Workbench",
      "mysticalagriculture:infusion": "Mystical Agriculture Infusion Altar", "goety:ritual": "Goety ritual", "naturesaura:altar": "Nature's Aura Natural Altar",
      "thermal:smelter": "Thermal Induction Smelter", "mekanism:combining": "Mekanism Combiner", "mekanism:metallurgic_infusing": "Mekanism Metallurgic Infuser",
      "mekanism:nucleosynthesizing": "Mekanism Antiprotonic Nucleosynthesizer", "industrialforegoing:dissolution_chamber": "Industrial Foregoing Dissolution Chamber",
      "ae2:inscriber": "AE2 Inscriber", "hexerei:mixingcauldron": "Hexerei Mixing Cauldron", "ad_astra:nasa_workbench": "Ad Astra NASA Workbench",
      "evolvedmekanism:alloying": "Evolved Mekanism Alloyer", "ars_nouveau:imbuement": "Ars Nouveau Imbuement Chamber", "bloodmagic:altar": "Blood Magic Blood Altar",
      "bloodmagic:soulforge": "Blood Magic Hellfire Forge", "create:mixing": "Create Mechanical Mixer", "evolvedmekanism:chemixing": "Evolved Mekanism Chemixer",
      "goety:brazier": "Goety Necro Brazier", "immersiveengineering:alloy": "Immersive Engineering Alloy Kiln", "immersiveengineering:arc_furnace": "Immersive Engineering Arc Furnace",
      "mekanism:injecting": "Mekanism Chemical Injection Chamber", "mekanism:reaction": "Mekanism Pressurized Reaction Chamber", "naturesaura:tree_ritual": "Nature's Aura Ritual of the Forest", "evolvedmekanism:apt": "Evolved Mekanism APT", "mekanism:crushing": "Mekanism Crusher"}
def routes(it):
    """6.6.6 summon routes: every recipe for the item in kubejs/data/linggango_integration/recipes/38_summon_routes"""
    out = []
    for f in sorted(glob.glob(f"{W}/pack/src/overrides/kubejs/data/linggango_integration/recipes/38_summon_routes/{it}_*.json")):
        o = json.load(open(f)); t = o.get("type", "")
        a = []; walk = [{k: v for k, v in o.items() if k not in ("result", "output", "conditions")}]
        while walk:
            x = walk.pop(0)
            if isinstance(x, dict):
                if isinstance(x.get("item"), str): a.append(x["item"])
                elif isinstance(x.get("tag"), str): a.append("#" + x["tag"])
                else: walk += list(x.values())
            elif isinstance(x, list): walk += x
        cnt = {}
        for i in a: cnt[i] = cnt.get(i, 0) + 1
        out.append({"type": t, "label": RT.get(t, t.split(":")[0].replace("_", " ").title() + " " + t.split(":")[1].replace("_", " ")),
                    "ings": [{"id": i, "n": nm(i) if not i.startswith("#") else tagn(i), "c": c} for i, c in cnt.items()]})
    return out
def grid(r):
    g = []
    for row in r["pattern"]:
        g.append([r["key"].get(c) if c != " " else None for c in row.ljust(3)])
    return g
def where(i, boss):
    """where an ingredient comes from: a natural source first (and another Keeper's bag that also holds it), then the
    treasure bag boss_info.json lists it in (bags given out by code, like the Ender Dragon's, are not loot tables),
    'crafted' only for an item with neither, then chest loot. Never a bare 'treasure bag'."""
    bag = BAGOF.get(i); own = BIKEY.get(boss, boss)
    if i in NATURAL: return NATURAL[i] + (f"; also the {bag[1]}" if bag and bag[0] != own else "")
    crafted = bool(rec["recipes"].get(i))
    if bag: return bag[1] + (", or crafted" if crafted else "")
    if crafted: return "crafted"
    lt = rec["loot"].get(i, [])
    if lt: return ", ".join(sorted({t.split(":")[1].split("/")[-1].replace("_", " ").title() + (" chests" if "/chests/" in "/" + t.split(":")[1] else "") for t in lt}))[:120]
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
                   "ings": [{"id": c, "n": nm(c) if not c.startswith("#") else tagn(c)} for c in sorted({c for row in (grid(ri) if ri else []) for c in row if c})]}
            break
    out[boss] = {"item": iid, "name": nm(iid), "use": use, "info": info, "recipe": g, "recipe_src": r and r["src"],
                 "infinite": inf, "soul": r and r.get("soul"), "routes": routes(it),
                 "ings": [{"id": i, "n": nm(i) if not i.startswith("#") else tagn(i), "from": where(i, boss) if not i.startswith("#") else ""} for i in ings]}
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
for k, v in out.items(): print(k, "|", v["name"], "|", v["use"][:70], "|", v["recipe_src"], [x["n"] + " (" + x["from"] + ")" for x in v["ings"]])
