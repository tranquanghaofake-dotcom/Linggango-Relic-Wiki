#!/usr/bin/env python3
"""Apply the equipment audit (build/pack_audit/eqa): raise Acts to the linggango_tweaks:gated/* tier or the
recipe-ingredient gate, and attach a source note (g.ob) to gear with no recipe/loot in the data. Idempotent."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent
P = H.parent / "src" / "gear_data.js"
F = json.loads((H / "gear_fix.json").read_text())
s = P.read_text(encoding="utf-8"); i = s.index("[")
GE, end = json.JSONDecoder().raw_decode(s, i)
n = 0
for g in GE:
    a = F["act"].get(g["id"])
    if a and a > g["a"]: g["a"] = a; g["ga"] = max(g.get("ga") or 0, a); n += 1
    if g["id"] in F["note"]: g["ob"] = F["note"][g["id"]]
# Audit v22.3: ctor speed 0.0 was read as 4.0; use the real or sword-default speed and scale the melee score.
SPD = {"alexsmobs:tendon_whip": 1.0, "lethality:hf_meowrasama": 1.6, "macabre:blood_cloth_dagger": 1.6,
       "macabre:plasma_dagger": 1.6, "lethality:pickle_paddle": 1.6}
for g in GE:
    v = SPD.get(g["id"])
    if v and g.get("spd") == 4.0:
        if g["sc"].get("ME") is not None: g["sc"]["ME"] = round(g["sc"]["ME"] * v / 4.0, 2)
        g["spd"] = v; n += 1
P.write_text(s[:i] + json.dumps(GE, separators=(",", ":"), ensure_ascii=False) + s[end:], encoding="utf-8")
# A set's Act is its latest piece.
s = P.read_text(encoding="utf-8"); j = s.index("GS=") + 3
GS, e2 = json.JSONDecoder().raw_decode(s, j); A = {g["id"]: g["a"] for g in GE}
for t in GS:
    m = max([A.get(x, 0) for x in t["p"]] + [t["a"]])
    if m > t["a"]: t["a"] = m; n += 1
P.write_text(s[:j] + json.dumps(GS, separators=(",", ":"), ensure_ascii=False) + s[e2:], encoding="utf-8")
print("gear_fix:", n, "acts raised,", len(F["note"]), "source notes")
