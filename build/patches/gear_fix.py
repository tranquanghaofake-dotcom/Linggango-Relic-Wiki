"""Stage 4. Apply the equipment audit (build/pack_audit/eqa): raise Acts to the linggango_tweaks:gated/* tier or the
recipe-ingredient gate, and attach a source note (g.ob) to gear with no recipe/loot in the data."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent
F = json.loads((H / "gear_fix.json").read_text())
# Audit v22.3: ctor speed 0.0 was read as 4.0; use the real or sword-default speed (gear.js scores from it).
SPD = {"alexsmobs:tendon_whip": 1.0, "lethality:hf_meowrasama": 1.6, "macabre:blood_cloth_dagger": 1.6,
       "macabre:plasma_dagger": 1.6, "lethality:pickle_paddle": 1.6}

def apply(st):
    for g in st["GE"]:
        a = F["act"].get(g["id"])
        if a and a > g["a"]: g["a"] = a; g["ga"] = max(g.get("ga") or 0, a)
        if g["id"] in F["note"]: g["ob"] = F["note"][g["id"]]
        v = SPD.get(g["id"])
        if v and g.get("spd") == 4.0: g["spd"] = v
    # A set's Act is its latest piece.
    A = {g["id"]: g["a"] for g in st["GE"]}
    for t in st["GS"]:
        m = max([A.get(x, 0) for x in t["p"]] + [t["a"]])
        if m > t["a"]: t["a"] = m
