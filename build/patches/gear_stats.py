#!/usr/bin/env python3
"""Gear stats the full extraction could not read (build/patches/gear_stats.json; the checks are in pack_audit/verify2.json):
  - Summonity armor: armor, toughness and minion slots come from summonity-common.toml, not the ArmorMaterial.
  - Hazen 'N Stuff armor: every piece also carries its HnSArmorMaterial attributes (mana, spell power, cast time...).
  - Iron's Spellbooks armor: every piece also carries its ExtendedArmorMaterials attributes (125-150 mana, spell power, school power).
  - Mowzie's tools: each reads its own tool_config (the table had copied the wrought axe onto all of them).
  - Soulslike trick weapons: Kirkhammer/Silver Sword, Holy Moonlight Sword/Greatsword and Simon's Bowblade/Blade are one
    weapon each, switched in hand, so they become one entry (the stronger form, the other listed in `lv`).
Offence facts (`off`) and set totals (with their summed attributes `at`) are recomputed with gearlib, the same code gear_data.py uses; nothing is scored here (src/gear.js does). Stage 5."""
import json, pathlib, re
from gearlib import off_of, set_facts
H = pathlib.Path(__file__).resolve().parent
D = json.loads((H / "gear_stats.json").read_text(encoding="utf-8"))

def refresh(g):
    g["off"] = {k: round(v, 3) for k, v in off_of(g["at"]).items() if v > 0.0005}
def add_at(g, k, flat, mul):
    a = g["at"].setdefault(k, [0.0, 0.0]); a[0] = round(a[0] + flat, 4); a[1] = round(a[1] + mul, 4)

def apply(st):
    GE, GS = st["GE"], st["GS"]
    by = {g["id"]: g for g in GE}
    touched = set()
    for g in GE:
        ns, p = g["id"].split(":")
        if g["k"] != "armor" and ns != "mowziesmobs": continue
        if ns == "summonity" and g["k"] == "armor":
            m = re.match(r"(.+)_(helmet|chestplate|leggings|boots)$", p)
            v = D["summonity_armor"].get(m.group(1), {}).get(m.group(2)) if m else None
            if v:
                g["arm"], g["tough"] = v[0], v[1]
                if v[2]: add_at(g, "minion_slots", v[2], 0)
                touched.add(g["id"])
        elif ns == "hazennstuff":
            key = max((k for k in D["hns_item_material"] if p.startswith(k)), key=len, default=None)
            if key:
                for k, (f, mu) in D["hns_materials"][D["hns_item_material"][key]].items(): add_at(g, k, f, mu)
                touched.add(g["id"])
        elif ns == "irons_spellbooks":
            key = max((k for k in D["iss_item_material"] if p.startswith(k)), key=len, default=None)
            if key:
                for k, (f, mu) in D["iss_materials"][D["iss_item_material"][key]].items(): add_at(g, k, f, mu)
                touched.add(g["id"])
        elif ns == "mowziesmobs" and p in D["mowzie_tools"]:
            g["dmg"], g["spd"] = D["mowzie_tools"][p]; touched.add(g["id"])
    for g in GE:
        if g["id"] in touched: refresh(g)

    # trick-weapon pairs: one entry, the stronger form; recipe and loot stay with the form you can obtain
    for pr in D["trick_pairs"]:
        a, b = by.get(pr["main"]), by.get(pr["other"])
        if not a or not b: continue
        for f in ("rc", "lt"):
            if not a.get(f) and b.get(f): a[f] = b[f]
        a["lv"] = [x for x in (a.get("lv") or []) if x != b["id"]] + [b["id"]]
        a["ob"] = a.get("ob") or pr["note"]
        GE = [g for g in GE if g["id"] != b["id"]]; by.pop(b["id"])
    st["GE"] = GE

    # set totals are recomputed for every set from its pieces as they stand now (touched pieces included); two pieces for one slot
    # (Fireblossom Crown/Helmet, Wizard and Chaos hats) are alternatives: set_facts counts only the better one, the way you can only wear one
    for t in GS:
        ps = [by[x] for x in t["p"] if x in by]
        if ps: t.update(set_facts(ps))
