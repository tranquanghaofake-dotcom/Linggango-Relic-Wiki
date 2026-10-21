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
P.write_text(s[:i] + json.dumps(GE, separators=(",", ":"), ensure_ascii=False) + s[end:], encoding="utf-8")
print("gear_fix:", n, "acts raised,", len(F["note"]), "source notes")
