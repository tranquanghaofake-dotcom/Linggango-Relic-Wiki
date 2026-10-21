#!/usr/bin/env python3
"""Replace the gear table (GE, GS) in build/src/gear_data.js with build/patches/gear_table.json, the output of the
full gear extraction (build/gear: mjvm over every jar's item registration, vanilla values, pack attributesetter,
progression_lock and linggango_tweaks:gated tags; summon weapons, one entry per level/form variant).
Runs first among the gear patches; gear_icons, gear_gate and gear_fix then re-apply on top. Idempotent."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent
P = H.parent / "src" / "gear_data.js"
T = json.loads((H / "gear_table.json").read_text(encoding="utf-8"))
s = P.read_text(encoding="utf-8")
i = s.index("const GE=") + len("const GE=")
_, e1 = json.JSONDecoder().raw_decode(s, i)
assert s[e1:e1 + 4] == ",GS=", s[e1:e1 + 10]
_, e2 = json.JSONDecoder().raw_decode(s, e1 + 4)
assert s[e2:e2 + 5] == ",GNS=", s[e2:e2 + 10]
k = e2 + 5
GNS, e3 = json.JSONDecoder().raw_decode(s, k)
GNS.update({"minecraft": "Minecraft", "tiered": "Tiered"})
d = lambda x: json.dumps(x, separators=(",", ":"), ensure_ascii=False)
s = s[:i] + d(T["GE"]) + ",GS=" + d(T["GS"]) + ",GNS=" + d(GNS) + s[e3:]
P.write_text(s, encoding="utf-8")
print("gear_rebuild:", len(T["GE"]), "gear,", len(T["GS"]), "sets")
