"""Drop chances for side bosses whose drops came from the quest book or boss_extra.json without numbers.
Usage: loot_chance.py JARS_DIR  -> build/patches/side_drops.json {boss: {"src", "drops": [{id, n, chance, count}]}}
Reads each boss's entity loot table from the mod jars and works the chance out the way loot.py does (one roll of a
weighted pool: weight / total; n rolls: 1 - (1 - w/total)^n; random_chance conditions multiply; nested tables are
followed). The pack's own kubejs/data loot overrides are not read here (no pack zip): the page says the chance is
the mod's."""
import json, zipfile, glob, sys, pathlib
JD = sys.argv[1]; H = pathlib.Path(__file__).resolve().parents[2] / "patches"
BOSS = {"Minister": ["goety:minister"], "Crone": ["goety:crone"], "Heresiarch": ["goety:heresiarch"], "Skull Lord": ["goety:skull_lord"],
        "Wither Necromancer": ["goety:wither_necromancer"], "Brood Mother": ["goety:brood_mother"], "Wight": ["goety:wight"],
        "Ender Keeper": ["goety:ender_keeper"], "Redstone Golem": ["goety:hostile_redstone_golem"], "Tongbi, the Sculptor": ["mowziesmobs:sculptor"],
        "Possessed Paladin": ["legendary_monsters:posessed_paladin"], "Withered Abomination": ["legendary_monsters:withered_abomination"],
        "Lava Eater": ["legendary_monsters:lava_eater"], "Shulker Mimic": ["legendary_monsters:shulker_mimic"], "Endersent": ["legendary_monsters:endersent"],
        "Chorusling": ["legendary_monsters:chorusling"], "Mutant Enderman": ["mutantmonsters:mutant_enderman"], "Vizier": ["goety:vizier"]}
ZS = [zipfile.ZipFile(j) for j in glob.glob(JD + "/*.jar")]
LANG = {}
for z in ZS:
    for n in z.namelist():
        if n.endswith("lang/en_us.json"):
            try: LANG.update({k: v for k, v in json.loads(z.read(n).decode("utf8", "ignore")).items() if k.startswith(("item.", "block."))})
            except ValueError: pass
VAN = {"minecraft:" + k: k.replace("_", " ").title() for k in ("emerald", "glowstone_dust", "redstone", "gold_ingot", "golden_carrot", "skeleton_skull",
       "wither_skeleton_skull", "netherite_scrap", "cobweb", "ender_pearl", "bone", "string", "spider_eye", "experience_bottle")}
def load(tid):
    ns, p = tid.split(":", 1)
    for z in ZS:
        try: return json.loads(z.read(f"data/{ns}/loot_tables/{p}.json"))
        except KeyError: continue
    return None
def cch(conds):
    c = 1.0
    for x in conds or []:
        if x.get("condition", "").split(":")[-1] in ("random_chance", "random_chance_with_looting"): c *= x.get("chance", 1)
    return c
def num(v):
    if isinstance(v, dict): return (v.get("min", v.get("value", 1)), v.get("max", v.get("value", 1)))
    return (v, v)
def count(e):
    for f in e.get("functions", []):
        if f.get("function", "").split(":")[-1] == "set_count":
            lo, hi = num(f.get("count", 1)); lo = max(lo, 0)  # a uniform from -1 gives 0 that often
            return f"{lo:g}" if lo == hi else f"{lo:g}–{hi:g}"
    return "1"
def walk(tid, mult, out, d=0):
    t = load(tid)
    if not t or d > 4: return False
    for pool in t.get("pools", []):
        r = max(1, int(num(pool.get("rolls", 1))[1])); pc = cch(pool.get("conditions")); ents = []
        def flat(es):
            for e in es:
                if e.get("type", "").split(":")[-1] in ("alternatives", "group", "sequence"): flat(e.get("children", []))
                else: ents.append(e)
        flat(pool.get("entries", []))
        tw = sum(e.get("weight", 1) for e in ents) or 1
        for e in ents:
            ty = e.get("type", "").split(":")[-1]; w = e.get("weight", 1)
            p = (1 - (1 - w / tw) ** r if len(ents) > 1 else 1) * pc * cch(e.get("conditions")) * mult
            if ty == "item" and e["name"] != "minecraft:air":
                o = out.setdefault(e["name"], {"p": 0, "c": count(e)}); o["p"] = max(o["p"], p)
            elif ty == "loot_table": walk(e["name"], p, out, d + 1)
    return True
R = {}
for b, ents in BOSS.items():
    out = {}; ok = [e for e in ents if walk(e.split(":")[0] + ":entities/" + e.split(":")[1], 1, out)]
    if not ok: print("no table", b); continue
    L = []
    for k, v in sorted(out.items(), key=lambda kv: -kv[1]["p"]):
        ns, p = k.split(":")
        n = LANG.get(f"item.{ns}.{p}") or LANG.get(f"block.{ns}.{p}") or VAN.get(k) or p.replace("_", " ").title()
        pct = v["p"] * 100
        L.append({"id": k, "n": n, "chance": f"{pct:.0f}%" if pct >= 1 else f"{pct:.1f}%", "count": v["c"]})
    R[b] = {"src": "mod loot table: " + ", ".join(e.split(":")[0] + ":entities/" + e.split(":")[1] for e in ok), "drops": L}
(H / "side_drops.json").write_text(json.dumps(R, ensure_ascii=False, indent=0), encoding="utf-8")
for b, v in R.items(): print(b, [(d["id"].split(":")[1], d["chance"], d["count"]) for d in v["drops"]])
