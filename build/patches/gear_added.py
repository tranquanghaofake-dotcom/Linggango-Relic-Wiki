#!/usr/bin/env python3
"""Stage 5b. Gear the extraction table lacks but the 6.6.6hf in-game dump has (gear_new.json, from pack_audit/gear_new.py):
weapons and armor pieces with their names, Acts, recipes and loot tables, and the armor sets they form. Their stats come
from the dump in the next stage (gear_runtime), like every other piece; set totals are computed there too."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent
N = json.loads((H / "gear_new.json").read_text(encoding="utf-8"))

def apply(st):
    have = {g["id"] for g in st["GE"]}
    add = [dict(g) for g in N["ge"] if g["id"] not in have]
    st["GE"].extend(add)
    keys = {s["k"] for s in st["GS"]}
    st["GS"].extend(dict(s, arm=0.0, tough=0.0, hp=0.0, kbr=0.0, dtk=0.0, off={}, at={}) for s in N["gs"] if s["k"] not in keys)
    print("gear_added: %d pieces, %d sets from the in-game dump" % (len(add), len([s for s in N["gs"] if s["k"] not in keys])))
