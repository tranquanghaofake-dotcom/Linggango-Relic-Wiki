#!/usr/bin/env python3
"""Boss stats with the pack's attribute overrides (kubejs/data/linggango/attributesetter/entity/
entitybalance.json, copied here). BASE replaces the mod's value, ADDITION adds to it. Then the
Armageddon HP bonus (kept from the earlier pre_hardmode − base gap) and, for bosses fought after the
Ender Dragon, Hardmode ×2.1 health and damage (armageddon_mod_config.toml; the Warden is exempt).
Keeps the original mod values in phase["mod"]. Idempotent."""
import json, pathlib, re
H = pathlib.Path(__file__).resolve().parent
P = H.parent / "src" / "data.js"
EB = json.loads((H / "entitybalance.json").read_text())
HM = 2.1
s = P.read_text(encoding="utf-8")
m = re.search(r"BST\s*=\s*", s); B, end = json.JSONDecoder().raw_decode(s, m.end())
def apply(base, mods):
    o = dict(base)
    for x in mods:
        k = {"max_health": "hp", "armor": "armor", "attack_damage": "dmg", "armor_toughness": "tough"}.get(x["attribute"].split(".")[-1])
        if not k: continue
        if x["operation"] == "BASE": o[k] = x["value"]
        elif x["operation"] == "ADDITION" and o.get(k) is not None: o[k] = o[k] + x["value"]
    return o
n = 0
for key, b in B.items():
    if key == "_claims": continue
    post = b.get("effective") == (b["phases"][0].get("hardmode") if b.get("phases") else None) and key not in ("wither", "ender_dragon", "warden")
    for p in b.get("phases", []):
        if "mod" not in p:
            p["mod"] = {"base": p["base"], "pre_hardmode": p.get("pre_hardmode"), "hardmode": p.get("hardmode")}
        mod = p["mod"]; bonus = (mod["pre_hardmode"]["hp"] - mod["base"]["hp"]) if mod.get("pre_hardmode") else 0
        base = apply(mod["base"], EB.get(p["entity"], []))
        if key == "ender_dragon": base["dmg"] = None  # its −60 attack_damage modifier only hits the melee value, which the dragon doesn't use
        pre = dict(base, hp=base["hp"] + bonus)
        hard = None if key == "warden" else dict(pre, hp=round(pre["hp"] * HM, 1), dmg=None if pre.get("dmg") is None else round(pre["dmg"] * HM, 1))
        p["base"], p["pre_hardmode"], p["hardmode"] = base, pre, hard
    ph = b["phases"][0] if b.get("phases") else None
    if ph:
        b["base"] = ph["base"]; b["effective"] = ph["hardmode"] if post else ph["pre_hardmode"]; n += 1
    r = [x for x in b.get("rules", []) if "entitybalance" not in x]
    if any(p["entity"] in EB for p in b.get("phases", [])):
        r.insert(0, "Pack override (attributesetter entitybalance.json) replaces the mod's health, armor, toughness and damage where set")
    if not any(p.get("hardmode") for p in b.get("phases", [])) or key in ("wither", "ender_dragon"):
        r = [x for x in r if not x.startswith("Assumption: Hardmode")]
    b["rules"] = r
s = s[:m.end()] + json.dumps(B, ensure_ascii=False, separators=(",", ":")) + s[end:]
P.write_text(s, encoding="utf-8")
print("bosses", n)
for k, b in B.items():
    if k != "_claims": print(f"  {k}: {b['effective']}")
