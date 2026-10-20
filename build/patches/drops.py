#!/usr/bin/env python3
"""Mob drop chances recomputed from the loot tables in the pack's own jars (TerraCurio-0.1.13-all.jar,
terramity-0.9.8). Ultra Sniffer: 2 rolls over 4 equal entries = 1-(3/4)^2 = 43.75%. Bat: one roll over
Radar 50% / Compass 20% / Depth Meter 20% entries, each with its own chance, one picked among those that pass."""
import json, pathlib, re
P = pathlib.Path(__file__).resolve().parents[1] / "src" / "data.js"
FIX = {  # id: (mob, new chance)
 "confluence:brain_of_confusion": ("Zombie Villager", "15%"),
 "confluence:hand_drill": ("Elder Guardian", "100%"),
 "confluence:frog_leg": ("Frog", "100%"),
 "terramity:dragon_band": ("Ultra Sniffer", "44%"),
 "terramity:ultra_sniffer_fur": ("Ultra Sniffer", "44%"),
 "terramity:ultra_sniffers_pelt": ("Ultra Sniffer", "44%"),
 "confluence:radar": ("Bat", "41%"),
 "confluence:compass": ("Bat", "14%"),
 "confluence:depth_meter": ("Bat", "14%"),
}
s = P.read_text(encoding="utf-8")
D, end = json.JSONDecoder().raw_decode(s, 8)
n = 0
for d in D:
    if d["id"] not in FIX: continue
    mob, ch = FIX[d["id"]]
    pat = re.compile(r"(Dropped by " + re.escape(mob) + r" \()[0-9.]+%(\))")
    for k in ("src",):
        new = [pat.sub(r"\g<1>" + ch + r"\2", x) for x in d[k]]
        if new != d[k]: d[k] = new; n += 1
    if d.get("src0"): d["src0"] = re.sub(r"(" + re.escape(mob) + r" drop \()[0-9.]+%", r"\g<1>" + ch, d["src0"])
P.write_text("const D=" + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + s[end:], encoding="utf-8")
print("updated", n)
