#!/usr/bin/env python3
"""Append the weapons in gear_extra.json (made by build/gear/extra.py: Iron's staffs, Ars Nouveau spell books, a few modded
guns the full extraction left out) to the gear table. They carry no readable stats, so like every Ranged/Mage weapon they
are ranked by their unlock rung (gear.js). Runs right after gear_rebuild. Idempotent: the table is reset by gear_rebuild."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent
P = H.parent / "src" / "gear_data.js"
X = json.loads((H / "gear_extra.json").read_text(encoding="utf-8"))
s = P.read_text(encoding="utf-8"); i = s.index("const GE=") + len("const GE=")
GE, e1 = json.JSONDecoder().raw_decode(s, i)
have = {g["id"] for g in GE}
ROLE = {"magic": "MA", "ranged": "RA", "summon": "SU", "melee": "ME"}
add = []
for x in X:
    if x["id"] in have: continue
    x = dict(x); x["a"] = 6 if x["a"] in (6.1, 6.2) else x["a"]  # the wiki's Acts have no Warden / Wither step: both sit in Act VI
    x["sc"] = {ROLE[x["k"]]: 1.0}; add.append(x)
GE += add
s = s[:i] + json.dumps(GE, separators=(",", ":"), ensure_ascii=False) + s[e1:]
P.write_text(s, encoding="utf-8")
print("gear_extra: +%d weapons" % len(add))
