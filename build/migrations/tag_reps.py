#!/usr/bin/env python3
"""Recipe slots that take a tag showed an arbitrary member of it (Glacian Fur for any wool,
Pewen Log for any log, Ersatz Leather for leather...), and the source text named that member.
Show a vanilla member instead and say "any X" in the text. Idempotent."""
import json, pathlib, re
P = pathlib.Path(__file__).resolve().parents[1] / "src" / "data.js"
REP = {  # tag: (vanilla icon or None to keep the icon, wording, names the old text used for it)
 "#minecraft:wool": ("minecraft:white_wool", "any Wool", ["Black Wool"]),
 "#minecraft:logs": ("minecraft:oak_log", "any Log", ["Vexing Archwood Log"]),
 "#minecraft:planks": (None, "any Planks", ["Archwood Planks"]),
 "#minecraft:sand": ("minecraft:sand", "any Sand", ["Black Sand"]),
 "#forge:sand": ("minecraft:sand", "any Sand", ["Black Sand"]),
 "#forge:leather": ("minecraft:leather", "Leather", []),
 "#forge:glass": ("minecraft:glass", "Glass", ["Framed Glass"]),
 "#forge:glass_panes/colorless": ("minecraft:glass_pane", "Glass Pane", ["Framed Glass Pane"]),
 "#forge:rods/wooden": ("minecraft:stick", "Stick", ["Treated Stick"]),
 "#forge:armors/boots": ("minecraft:iron_boots", "any Boots", ["Flying Fish Boots"]),
 "#forge:gems/emerald": ("minecraft:emerald", "Emerald", ["Awakened Emerald"]),
 "#forge:slimeballs": ("minecraft:slime_ball", "Slimeball", []),
 "#forge:ingots": ("minecraft:iron_ingot", "any Ingot", ["Calorite Ingot"]),
 "#minecraft:dirt": (None, "any Dirt", ["Cobbled Dark Dirt"]),
 "#minecraft:leaves": (None, "any Leaves", ["Palm Leaves"]),
}
s = P.read_text(encoding="utf-8")
D, end = json.JSONDecoder().raw_decode(s, 8)
m = re.search(r"[,;\s]NM=", s); NM, _ = json.JSONDecoder().raw_decode(s, m.end())
m = re.search(r"[,;\s]IC=", s); IC, _ = json.JSONDecoder().raw_decode(s, m.end())
n = 0
for d in D:
    g = d.get("gr")
    if not g: continue
    swaps = {}
    for c in g["c"]:
        if c and c[1] in REP:
            new, word, olds = REP[c[1]]
            if new and new in IC: c[0] = new
            for o in olds: swaps[o] = word
    a = (list(d["src"]), d.get("src0"))
    for old, word in swaps.items():
        pat = re.compile(r"(?<![\w'])" + re.escape(old) + r"(?![\w])")
        d["src"] = [pat.sub(word, x) for x in d["src"]]
        if d.get("src0"): d["src0"] = pat.sub(word, d["src0"])
    n += (list(d["src"]), d.get("src0")) != a
P.write_text("const D=" + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + s[end:], encoding="utf-8")
print("text changed", n)
