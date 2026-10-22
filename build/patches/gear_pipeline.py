#!/usr/bin/env python3
"""Write build/src/gear_data.js. The whole gear table is built in memory and written once, like wiki_data.js; nothing reads the
generated file back. Stages run in the order below, each is a function on {GE, GS, GNS, IC}:
  1 gear_rebuild.load   gear_table.json (extraction), gear_names.json (mod names), gear_icons.json (icons)
  2 gear_extra          weapons the extraction skips (gear_extra.json)
  3 gear_gate           Acts raised by modded ingredients the pack unlocks late (gear_gate.json)
  4 gear_fix            audit fixes: gated Acts, source notes, attack speeds (gear_fix.json)
  5 gear_stats          attributes the extraction could not read: Summonity / Hazen / Iron's armor, Mowzie tools, trick pairs
  6 gear_runtime        attribute modifiers read in game (the pack's own kubejs dump_gear) replace the jar reading where present
  7 boss_order.gear     boss drops sit at their boss's Act
  then every Act is snapped onto the wiki's Acts
Scoring is not here: src/gear.js ranks from the facts these stages leave."""
import json, pathlib
import gear_rebuild, gear_extra, gear_gate, gear_fix, gear_stats, gear_runtime, boss_order
H = pathlib.Path(__file__).resolve().parent
st = gear_rebuild.load()
for stage in (gear_extra.apply, gear_gate.apply, gear_fix.apply, gear_stats.apply, gear_runtime.apply, boss_order.gear):
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
