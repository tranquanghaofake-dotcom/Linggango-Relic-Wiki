#!/usr/bin/env python3
"""Keeper gates beat the random-loot rule: a gated curio can't be equipped before its Act (idempotent)."""
import json, pathlib
P = pathlib.Path(__file__).resolve().parents[1] / "src" / "data.js"
FIX = {"l2hostility:oddeyes_glasses": (8, "Needs a Voiderite Block (first given by the Act VII boss); quest book: Act VIII"),
       "goety:void_crown": (6.3, "End ritual with a Void Block: after the Ender Dragon"),
       "goety:void_robe": (6.3, "End ritual with a Void Block: after the Ender Dragon")}
s = P.read_text(encoding="utf-8")
D, end = json.JSONDecoder().raw_decode(s, 8)
n = 0
for d in D:
    g = d.get("gk") or 0
    if g and d["t"] < g:
        d["t"] = d["a"] = g
        d["why"] = [w for w in d.get("why", []) if not w.startswith("Random loot")] + ["Keeper-gated: it can't be equipped before this Act"]
        n += 1
    if d["id"] in FIX and d["t"] != FIX[d["id"]][0]:
        d["t"] = d["a"] = FIX[d["id"]][0]; d["why"] = d.get("why", []) + [FIX[d["id"]][1]]; n += 1
P.write_text("const D=" + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + s[end:], encoding="utf-8")
print("curio_gate", n)
