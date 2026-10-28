"""Write the plan for kubejs/server_scripts/lgw_measure.js: which items to measure in game.
Usage: prep.py OUT.json [--stop]  (copy OUT.json to the game's kubejs/lgw_items.json; --stop shuts the server down when done)
attrs: every gear item and curio of the wiki; melee: every weapon with a melee score; sets: every armor set with its pieces' slots.
The result (kubejs/lgw_measure.json) goes back into build/patches/ the way gear_runtime.json does."""
import json, sys, pathlib, re
H = pathlib.Path(__file__).resolve().parents[2]
s = (H / "src" / "gear_data.js").read_text(encoding="utf-8"); d = json.JSONDecoder()
GE, i = d.raw_decode(s, s.index("[", s.index("GE="))); GS, _ = d.raw_decode(s, s.index("[", s.index("GS=", i)))
c = (H / "src" / "data.js").read_text(encoding="utf-8"); D, _ = d.raw_decode(c, c.index("["))
SLOT = {"HELMET": "HEAD", "CHESTPLATE": "CHEST", "LEGGINGS": "LEGS", "BOOTS": "FEET"}
by = {g["id"]: g for g in GE}
plan = {"hits": 3, "stop": "--stop" in sys.argv,
        "attrs": sorted({g["id"] for g in GE} | {x["id"] for x in D}),
        "melee": sorted(g["id"] for g in GE if g["k"] == "melee" or g.get("dmg") is not None),
        "sets": [{"k": x["k"], "p": [[p, SLOT.get(by[p].get("sl"), "CHEST")] for p in x["p"] if p in by]} for x in GS]}
json.dump(plan, open(sys.argv[1], "w"), indent=0)
print(len(plan["attrs"]), "items,", len(plan["melee"]), "melee,", len(plan["sets"]), "sets ->", sys.argv[1])
