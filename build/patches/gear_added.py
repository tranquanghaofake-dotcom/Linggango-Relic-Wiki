#!/usr/bin/env python3
"""Stage 5b. Gear the extraction table lacks but the 6.6.6hf in-game dump has (gear_new.json, from pack_audit/gear_new.py):
weapons and armor pieces with their names, Acts, recipes and loot tables, and the armor sets they form. Their stats come
from the dump in the next stage (gear_runtime), like every other piece; set totals are computed there too.
An added armor piece that no set holds (gear_new.py groups only two or more: Goety's Malefic Helm, Mob Grinding Utils'
Monocle) is a one-piece set of its own, as gear_data.py makes for the Turtle Shell, so its page is an armor page."""
import json, pathlib, re
H = pathlib.Path(__file__).resolve().parent
N = json.loads((H / "gear_new.json").read_text(encoding="utf-8"))
SLOTW = r"(helmet|chestplate|leggings|boots|helm|cap|hood|robe|robes|pants|tunic|greaves|crown|mask|hat|chest|legs|feet|head|armor|armour)"
EMPTY = lambda: dict(arm=0.0, tough=0.0, hp=0.0, kbr=0.0, dtk=0.0, off={}, at={})  # totals: gear_runtime

def apply(st):
    have = {g["id"] for g in st["GE"]}
    add = [dict(g) for g in N["ge"] if g["id"] not in have]
    st["GE"].extend(add)
    keys = {s["k"] for s in st["GS"]}
    new = [dict(s, **EMPTY()) for s in N["gs"] if s["k"] not in keys]
    st["GS"].extend(new); keys |= {s["k"] for s in new}
    held = {i for s in st["GS"] for i in s["p"]}
    lone = []
    for g in add:
        if g["k"] != "armor" or g["id"] in held: continue
        ns, p = g["id"].split(":", 1)
        k = ns + ":" + ("_".join(w for w in p.split("_") if not re.fullmatch(SLOTW, w)) or p)
        if k in keys: k = g["id"]
        lone.append(dict(k=k, n=re.sub(r"\s+(Armor|Armour)$", "", g["n"]), p=[g["id"]], a=g["a"], kn=True, **EMPTY())); keys.add(k)
    st["GS"].extend(lone)
    print("gear_added: %d pieces, %d sets from the in-game dump, %d lone pieces as one-piece sets" % (len(add), len(new), len(lone)))
