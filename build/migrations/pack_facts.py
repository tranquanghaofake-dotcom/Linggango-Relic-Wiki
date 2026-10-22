#!/usr/bin/env python3
"""Facts the Linggango pack itself adds (Linggango-V6.6.5b4.zip overrides: kubejs client tooltips,
configs). Appends them to effect text once (idempotent)."""
import json, pathlib, re
P = pathlib.Path(__file__).resolve().parents[1] / "src" / "data.js"
MATH = "pi exponential addition subtraction multiplication division sum sine cosine".split()
ADD = {f"brutality:{k}_charm": "needs the Scientific Calculator to work (pack tooltip)" for k in MATH}
ADD["enigmaticaddons:bless_ring"] = "don't wear it together with the Ring of the Seven Curses (pack tooltip)"
FX = {"enigmaticaddons:lost_engine": "Spellstone; +10% movement speed, +4 toughness, +20% knockback resistance, lower gravity, -25% item cooldowns, +35% crit damage; immune to fall and explosion damage, golems won't attack first; in return weak to magic, and a lightning strike destroys items in your inventory (pack tooltip)"}
s = P.read_text(encoding="utf-8")
D, end = json.JSONDecoder().raw_decode(s, 8)
n = 0
for d in D:
    i = d["id"]
    if i in FX and d["fx"] != FX[i]: d["fx"] = FX[i]; n += 1
    if i in ADD and ADD[i] not in d["fx"]: d["fx"] += "; " + ADD[i]; n += 1
P.write_text("const D=" + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + s[end:], encoding="utf-8")
print("updated", n)
