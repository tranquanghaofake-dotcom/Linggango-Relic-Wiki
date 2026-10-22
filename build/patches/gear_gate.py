"""Stage 3. Raise the Act of gear whose recipe needs a modded material the pack only lets you use later
(e.g. Old GPU needs Conductite, whose own tools are gated at Act VII). gear_gate.json maps
item -> [act, material]; made from rec.json: a material's Act = the earliest gate of any gated
gear crafted from it. Sets g.a and g.mg=[act, material]."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent
fix = json.loads((H / "gear_gate.json").read_text())
LV = {"one": "Lv 1", "two": "Lv 2", "three": "Lv 3"}

def apply(st):
    for g in st["GE"]:
        f = fix.get(g["id"])
        if f and g["a"] < f[0]:
            g["a"] = f[0]; g["mg"] = f
    # Travel Optics level variants share one name in the lang file; tell them apart
    for g in st["GE"]:
        m = g["id"].rsplit("_level_", 1)
        if len(m) == 2 and m[1] in LV and "Lv" not in g["n"]:
            g["n"] += " (" + LV[m[1]] + ")"
