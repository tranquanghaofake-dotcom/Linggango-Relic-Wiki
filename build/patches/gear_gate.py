#!/usr/bin/env python3
"""Raise the Act of gear whose recipe needs a modded material the pack only lets you use later
(e.g. Old GPU needs Conductite, whose own tools are gated at Act VII). gear_gate.json maps
item -> [act, material]; made from rec.json: a material's Act = the earliest gate of any gated
gear crafted from it. Sets g.a and g.mg=[act, material]. Idempotent."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent
P = H.parent / "src" / "gear_data.js"
fix = json.loads((H / "gear_gate.json").read_text())
s = P.read_text(encoding="utf-8")
i = s.index("[")
GE, end = json.JSONDecoder().raw_decode(s, i)
n = 0
for g in GE:
    f = fix.get(g["id"])
    if f and g["a"] < f[0]:
        g["a"] = f[0]; g["mg"] = f; n += 1
# Travel Optics level variants share one name in the lang file; tell them apart
LV = {"one": "Lv 1", "two": "Lv 2", "three": "Lv 3"}
for g in GE:
    m = g["id"].rsplit("_level_", 1)
    if len(m) == 2 and m[1] in LV and "Lv" not in g["n"]:
        g["n"] += " (" + LV[m[1]] + ")"
P.write_text(s[:i] + json.dumps(GE, separators=(",", ":"), ensure_ascii=False) + s[end:], encoding="utf-8")
print("gear_gate:", n, "items moved later")
