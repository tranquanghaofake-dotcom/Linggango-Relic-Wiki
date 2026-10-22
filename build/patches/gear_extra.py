#!/usr/bin/env python3
"""Append the weapons in gear_extra.json (made by build/gear/extra.py: Iron's staffs, Ars Nouveau spell books, a few modded
guns the full extraction left out) to the gear table. They carry no readable stats, so like every Ranged/Mage weapon they
are ranked by their unlock rung (gear.js). Stage 2."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent
X = json.loads((H / "gear_extra.json").read_text(encoding="utf-8"))

def apply(st):
    have = {g["id"] for g in st["GE"]}
    for x in X:
        if x["id"] in have: continue
        st["GE"].append(dict(x))
