#!/usr/bin/env python3
"""Source lines read straight from the pack: recipes its KubeJS adds (server_scripts/mods/*/recipes.js)
and recipes it removes (e.remove({id})), for curios the wiki listed as loot only. Idempotent."""
import json, pathlib
P = pathlib.Path(__file__).resolve().parents[1] / "src" / "data.js"
ADD = {
 "covenant_of_the_seven:virtue_ring": "The pack also adds a crafting recipe: 4 Brass Ingot, Divine Pact and Concentrated Emerald at a Crafting Table.",
 "enigmaticlegacy:cursed_ring": "The pack replaces the mod's recipe with its own: 4 Dark Metal Ingot, Maledictus Pact and Orb of the Summoner at a Crafting Table.",
 "irons_spellbooks:necronomicon_spell_book": "Also craftable (pack recipe): 3 Weak Blood Shard, 3 Crimson Piece, 2 Crystallized Blood and a Copper Spell Book at a Crafting Table.",
 "uniqueaccessories:rose_of_temptation": "Also craftable (pack recipe, shapeless): Beetroot, Wheat, Potato, Carrot, Rose Bush, Tree Fertilizer, Industrial Fertilizer and Bio-Alchemical Fertilizer.",
 "enigmaticlegacy:darkest_scroll": "Can be duplicated at a Crafting Table: 1 Darkest Scroll + 2 Blank Scroll + 4 Black Dye + 2 Wither Rose → 2 Darkest Scrolls (Enigmatic Addons recipe).",
}
GONE = ["terramity:focus_scarf", "terramity:spring", "terramity:chthonic_curse_bracelets", "terramity:die_of_revival"]
NOTE = "Its crafting recipe is removed by the pack's KubeJS, so chests are the only way."
s = P.read_text(encoding="utf-8")
D, end = json.JSONDecoder().raw_decode(s, 8)
n = 0
for d in D:
    for line in ([ADD[d["id"]]] if d["id"] in ADD else []) + ([NOTE] if d["id"] in GONE else []):
        if line not in d["src"]: d["src"].append(line); n += 1
P.write_text("const D=" + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + s[end:], encoding="utf-8")
print("added", n)
