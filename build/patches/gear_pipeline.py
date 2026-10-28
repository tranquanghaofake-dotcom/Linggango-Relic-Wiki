#!/usr/bin/env python3
"""Write build/src/gear_data.js. The whole gear table is built in memory and written once, like wiki_data.js; nothing reads the
generated file back. Stages run in the order below, each is a function on {GE, GS, GNS, IC}:
  1 gear_rebuild.load   gear_table.json (extraction), gear_names.json (mod names), gear_icons.json (icons)
  2 gear_extra          weapons the extraction skips (gear_extra.json)
  3 gear_gate           Acts raised by modded ingredients the pack unlocks late (gear_gate.json)
  4 gear_fix            audit fixes: gated Acts, source notes, attack speeds (gear_fix.json)
  5 gear_stats          attributes the extraction could not read: Summonity / Hazen / Iron's armor, Mowzie tools, trick pairs
  5b gear_added       weapons and armor only the 6.6.6hf in-game dump has (gear_new.json, pack_audit/gear_new.py)
  6 gear_runtime        attribute modifiers read in game (the pack's own kubejs dump_gear) replace the jar reading where present
  7 boss_order.gear     boss drops sit at their boss's Act
  8 drop_curios         items the curio list (data.js) already has and the gear reading found no stats for: Goety's robes
                        and crowns are Curios items (common/items/curios), not armor, so they left 0-armor rows and empty sets
  then every Act is snapped onto the wiki's Acts
Scoring is not here: src/gear.js ranks from the facts these stages leave."""
import json, pathlib
import gear_rebuild, gear_extra, gear_gate, gear_fix, gear_stats, gear_added, gear_runtime, boss_order
H = pathlib.Path(__file__).resolve().parent
st = gear_rebuild.load()
def drop_curios(st):
    s = (H.parent / "src" / "data.js").read_text(encoding="utf-8"); D, _ = json.JSONDecoder().raw_decode(s, s.index("["))
    cur = {d["id"] for d in D}
    gone = {g["id"] for g in st["GE"] if g["id"] in cur and not g.get("arm") and not g.get("at") and g.get("dmg") is None}
    st["GE"] = [g for g in st["GE"] if g["id"] not in gone]
    for x in st["GS"]: x["p"] = [i for i in x["p"] if i not in gone]
    st["GS"] = [x for x in st["GS"] if x["p"]]
for stage in (gear_extra.apply, gear_gate.apply, gear_fix.apply, gear_stats.apply, gear_added.apply, gear_runtime.apply, boss_order.gear, drop_curios):
    stage(st)
# the wiki's Acts (app.js ORDER) have no Warden / Wither step: 6.1 and 6.2 sit in Act VI (a stray 6.1 once put a battleaxe at Act 0)
snap = lambda a: max(x for x in boss_order.ORDER if x <= a)
for x in st["GE"] + st["GS"]:
    for f in ("a", "ga"):
        if x.get(f) is not None: x[f] = snap(x[f])
    if x.get("mg"): x["mg"][0] = snap(x["mg"][0])
d = lambda x: json.dumps(x, separators=(",", ":"), ensure_ascii=False)
out = "const GE=" + d(st["GE"]) + ",GS=" + d(st["GS"]) + ",GNS=" + d(st["GNS"]) + ";\nObject.assign(IC," + d(st["IC"]) + ");"
(H.parent / "src" / "gear_data.js").write_text(out, encoding="utf-8")
print("gear_pipeline: %d gear, %d sets, %d icons" % (len(st["GE"]), len(st["GS"]), len(st["IC"])))
