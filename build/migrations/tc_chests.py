#!/usr/bin/env python3
"""Terra Curio puts its curios into vanilla chests through loot modifiers keyed on the vanilla table id
(TerraCurio-0.1.13-all.jar: data/confluence/loot_modifiers/chests/*.json → loot_tables/with/chests/*).
The wiki listed only modded structures. Chances = pool chance × entry chance over the pool's rolls.
Needs the jar: python3 tc_chests.py <TerraCurio jar>; without it, re-applies the stored lines."""
import json, pathlib, re, sys, zipfile, math
P = pathlib.Path(__file__).resolve().parents[1] / "src" / "data.js"
CACHE = pathlib.Path(__file__).with_suffix(".json")
NAME = {"shipwreck_supply": "Shipwreck supply", "shipwreck_treasure": "Shipwreck treasure", "jungle_temple": "Jungle Temple",
        "igloo_chest": "Igloo", "ancient_city": "Ancient City", "ancient_city_ice_box": "Ancient City ice box",
        "abandoned_mineshaft": "Mineshaft", "simple_dungeon": "Dungeon", "desert_pyramid": "Desert Pyramid",
        "end_city_treasure": "End City", "bastion_treasure": "Bastion treasure", "stronghold_corridor": "Stronghold corridor",
        "stronghold_crossing": "Stronghold crossing", "stronghold_library": "Stronghold library", "woodland_mansion": "Woodland Mansion",
        "nether_bridge": "Nether Fortress", "underwater_ruin_big": "big Ocean Ruin", "underwater_ruin_small": "small Ocean Ruin",
        "village/village_fisher": "village Fisher", "village/village_toolsmith": "village Toolsmith",
        "village/village_armorer": "village Armorer", "village/village_plains_house": "Plains village house"}
if len(sys.argv) > 1:
    z = zipfile.ZipFile(sys.argv[1]); cc = lambda cs: math.prod(k.get("chance", 1) for k in cs or [] if "random_chance" in k.get("condition", ""))
    res = {}
    for n in z.namelist():
        m = re.match(r"data/confluence/loot_tables/with/chests/(.+)\.json$", n)
        if not m or m.group(1) not in NAME: continue
        for p in json.loads(z.read(n))["pools"]:
            es = p["entries"]; tw = sum(e.get("weight", 1) for e in es); r = p.get("rolls", 1)
            r = r if isinstance(r, (int, float)) else (r["min"] + r["max"]) / 2
            for e in es:
                ch = cc(p.get("conditions")) * (1 - (1 - e.get("weight", 1) / tw * cc(e.get("conditions"))) ** r)
                res.setdefault(e["name"], []).append((round(ch * 100, 1), NAME[m.group(1)]))
    lines = {i: "Vanilla chests (Terra Curio adds it): " + ", ".join(f"{n} {('%g' % c)}%" for c, n in sorted(v, reverse=True)) + "."
             for i, v in res.items()}
    CACHE.write_text(json.dumps(lines, indent=0, ensure_ascii=False))
lines = json.loads(CACHE.read_text())
s = P.read_text(encoding="utf-8")
D, end = json.JSONDecoder().raw_decode(s, 8)
n = 0
for d in D:
    L = lines.get(d["id"])
    if not L: continue
    d["src"] = [x for x in d["src"] if not x.startswith("Vanilla chests (Terra Curio")]
    d["src"].insert(0 if d["g"] == "Loot" else len(d["src"]), L); n += 1
P.write_text("const D=" + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + s[end:], encoding="utf-8")
print("lines", n)
