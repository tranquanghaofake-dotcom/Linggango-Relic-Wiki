#!/usr/bin/env python3
"""Crafting grids for curios that had none, from curio_recipes.json (written by pack_audit/curio_recipes.py from the
pack's KubeJS scripts, kubejs/data and the mod jars). A tag slot shows the tag's usual member (tag_ids.json), as the other
grids do; ingredient names go into NM. Fills curios without a grid and updates the grids it wrote (marked `grx`); a grid
from elsewhere stays unless the pack's recipe replaces it (`over`: the wiki's grid was not one of the pack's recipes for
that curio, see pack_audit/curio_recipes.py; such grids are marked `gro` too). Running it again changes nothing."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent; P = H.parent / "src" / "data.js"
R = json.loads((H / "curio_recipes.json").read_text(encoding="utf-8")); G, NAMES = R["grids"], R.get("names", {}); T = json.loads((H / "tag_ids.json").read_text(encoding="utf-8"))
s = P.read_text(encoding="utf-8"); D, e = json.JSONDecoder().raw_decode(s, 8); n = 0
for d in D:
    g = G.get(d["id"])
    if not g: continue
    gr = {k: v for k, v in g.items() if k != "over"}; gr["c"] = [[c[0] or T.get(c[1], ""), c[1]] if c else None for c in g["c"]]
    if d.get("gr") and d["gr"] != gr and not d.get("grx") and not g.get("over"): continue      # a grid from elsewhere stays
    if d.get("gr") != gr: d["gr"] = gr; d["grx"] = 1; n += 1
    if g.get("over") and not d.get("gro"): d["gro"] = 1; n += 1
# ingredient names the recipe slots show (NM, declared after D in the same file)
i = s.find(",NM=", e); NM, e2 = json.JSONDecoder().raw_decode(s, i + 4); m = 0
for k, v in NAMES.items():
    if k not in NM: NM[k] = v; m += 1
if n or m: P.write_text("const D=" + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + s[e:i + 4] + json.dumps(NM, ensure_ascii=False, separators=(",", ":")) + s[e2:], encoding="utf-8")
print(f"curio_recipes: {n} grid changes, {m} ingredient names added ({sum(1 for g in G.values() if g.get('over'))} grids are the pack's recipe over the wiki's)")
