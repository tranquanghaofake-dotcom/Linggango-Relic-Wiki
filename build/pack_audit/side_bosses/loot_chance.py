"""Drop chances for side bosses whose drops came from the quest book or boss_extra.json without numbers.
Usage: loot_chance.py JARS_DIR  -> build/patches/side_drops.json {boss: {"src", "drops": [{id, n, chance, count[, cond]}]}}
Reads each boss's entity loot table from the mod jars and works the chance of at least one out with ../lootlib.py (vanilla
1.20.1 rules: rolls as a distribution, conditions, composite entries, nested tables, pools combined; luck 0). count is the stack
size when it drops; cond names conditions taken as met (killed by a player...). A boss with several entities keeps the best
table per item. The pack's own kubejs/data loot overrides are not read here (no pack zip): the page says the chance is
the mod's."""
import json, zipfile, glob, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import lootlib
JD = sys.argv[1]; H = pathlib.Path(__file__).resolve().parents[2] / "patches"
BOSS = {"Minister": ["goety:minister"], "Crone": ["goety:crone"], "Heresiarch": ["goety:heresiarch"], "Skull Lord": ["goety:skull_lord"],
        "Wither Necromancer": ["goety:wither_necromancer"], "Brood Mother": ["goety:brood_mother"], "Wight": ["goety:wight"],
        "Ender Keeper": ["goety:ender_keeper"], "Redstone Golem": ["goety:hostile_redstone_golem"], "Tongbi, the Sculptor": ["mowziesmobs:sculptor"],
        "Possessed Paladin": ["legendary_monsters:posessed_paladin"], "Withered Abomination": ["legendary_monsters:withered_abomination"],
        "Lava Eater": ["legendary_monsters:lava_eater"], "Shulker Mimic": ["legendary_monsters:shulker_mimic"], "Endersent": ["legendary_monsters:endersent"],
        "Chorusling": ["legendary_monsters:chorusling"], "Mutant Enderman": ["mutantmonsters:mutant_enderman"], "Vizier": ["goety:vizier"]}
ZS = [zipfile.ZipFile(j) for j in sorted(glob.glob(JD + "/*.jar"))]
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
def walk(tid, out):
    t = load(tid)
    if not t: return False
    for i, o in lootlib.chances(t, load).items():
        if i not in out or o["p"] > out[i]["p"]: out[i] = o
    return True
R = {}
for b, ents in BOSS.items():
    out = {}; ok = [e for e in ents if walk(e.split(":")[0] + ":entities/" + e.split(":")[1], out)]
    if not ok: print("no table", b); continue
    L = []
    for k, v in sorted(out.items(), key=lambda kv: -kv[1]["p"]):
        ns, p = k.split(":")
        n = LANG.get(f"item.{ns}.{p}") or LANG.get(f"block.{ns}.{p}") or VAN.get(k) or p.replace("_", " ").title()
        pct = v["p"] * 100
        L.append({"id": k, "n": n, "chance": f"{pct:.0f}%" if pct >= 1 else f"{pct:.1f}%", "count": lootlib.count_text(v), **({"cond": v["cond"]} if v["cond"] else {})})
    R[b] = {"src": "mod loot table: " + ", ".join(e.split(":")[0] + ":entities/" + e.split(":")[1] for e in ok), "drops": L}
(H / "side_drops.json").write_text(json.dumps(R, ensure_ascii=False, indent=0), encoding="utf-8")
for b, v in R.items(): print(b, [(d["id"].split(":")[1], d["chance"], d["count"]) + tuple(d.get("cond", ())) for d in v["drops"]])
if lootlib.chances.missing: print("nested tables not in the jars (left out):", sorted(lootlib.chances.missing))
