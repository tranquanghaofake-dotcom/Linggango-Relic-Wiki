#!/usr/bin/env python3
"""Boss stats with the pack's attribute overrides (kubejs/data/linggango/attributesetter/entity/
entitybalance.json, copied here). BASE replaces the mod's value, ADDITION adds to it. Then the
Armageddon HP bonus (kept from the earlier pre_hardmode − base gap). Hardmode (×2.1 health and damage
after the Ender Dragon, armageddon_mod_config.toml) skips every entity in the forge:armageddon_bosses
tag (armageddon_bosses.json, copied from the Armageddon jar: every Keeper phase, the Wither and the
Ender Dragon) and the blacklisted Warden, so none of these bosses gets a Hardmode value. The Ender
Dragon's health and armor come from the pack mod ender_dragon_configuration (ender_dragon_configuration.json).
Keeps the original mod values in phase["mod"]. Idempotent."""
import json, pathlib, re
H = pathlib.Path(__file__).resolve().parent
P = H.parent / "src" / "data.js"
EB = json.loads((H / "entitybalance.json").read_text())
TAG = {v if ":" in v else "minecraft:" + v for v in json.loads((H / "armageddon_bosses.json").read_text())["values"]}
DC = json.loads((H / "ender_dragon_configuration.json").read_text())
HM = 2.1
EXEMPT = "Exempt from Hardmode (forge:armageddon_bosses tag)"
DRAGON = (f"Pack mod ender_dragon_configuration: {DC['vanillaHp']:g} HP ×{DC['defaultHpMultiplier']:g}, {DC['defaultArmorValue']:g} armor, "
          f"damage to players ×{DC['defaultDmgMultiplier']:g} (world default; /enderdragonconfig can change it per world)")
TAG_EV = "data/forge/tags/entity_types/armageddon_bosses.json (Armageddon jar, copied to patches/armageddon_bosses.json): IncreaseLifeOfMobsAndDamgetestProcedure returns before the Hardmode multipliers for every entity in it"
DC_EV = (f"config/ender_dragon_configuration_common.toml: defaultHpMultiplier = {DC['defaultHpMultiplier']}, defaultDmgMultiplier = {DC['defaultDmgMultiplier']}, "
         f"defaultArmorValue = {DC['defaultArmorValue']} (ender_dragon_configuration-0.2.jar DragonEvents.applyDragonStats / onLivingHurt)")
OLD_RULES = ("After Ender Dragon kill (Hardmode)", "Assumption: Hardmode", "Is the Hardmode trigger", EXEMPT, "Pack mod ender_dragon_configuration", "Its death turns on Hardmode")
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
        if key == "ender_dragon":
            base["dmg"] = None  # its −60 attack_damage modifier only hits the melee value, which the dragon doesn't use; its real damage is ×defaultDmgMultiplier (a rule)
            num = lambda v: int(v) if v == int(v) else v
            base["hp"], base["armor"] = num(DC["vanillaHp"] * DC["defaultHpMultiplier"]), num(DC["defaultArmorValue"])  # applyDragonStats: MAX_HEALTH and ARMOR base values on join
        pre = dict(base, hp=base["hp"] + bonus)
        hard = None if key == "warden" or p["entity"] in TAG else dict(pre, hp=round(pre["hp"] * HM, 1), dmg=None if pre.get("dmg") is None else round(pre["dmg"] * HM, 1))
        p["base"], p["pre_hardmode"], p["hardmode"] = base, pre, hard
    ph = b["phases"][0] if b.get("phases") else None
    if ph:
        b["base"] = ph["base"]; b["effective"] = ph["hardmode"] if post and ph["hardmode"] else ph["pre_hardmode"]; n += 1
    r = [x for x in b.get("rules", []) if "entitybalance" not in x]
    if any(p["entity"] in EB for p in b.get("phases", [])):
        r.insert(0, "Pack override (attributesetter entitybalance.json) replaces the mod's health, armor, toughness and damage where set")
    r = [x for x in r if not x.startswith(OLD_RULES)]
    tagged = b.get("phases") and all(p["entity"] in TAG for p in b["phases"])
    if key == "ender_dragon":
        r = [x for x in r if not x.startswith("No pack HP bonus")]  # its health is the ender_dragon_configuration rule below
        r.insert(1 if r and r[0].startswith("Pack override") else 0, DRAGON)
        r.append("Its death turns on Hardmode for the world")
    if tagged: r.append(EXEMPT)
    b["rules"] = r
    ev = [x for x in b.get("evidence", []) if x not in (TAG_EV, DC_EV)]
    if tagged: ev.append(TAG_EV)
    if key == "ender_dragon": ev.append(DC_EV)
    b["evidence"] = ev
B["_claims"]["hardmode_skips_armageddon_bosses"] = {"verdict": True, "evidence": [TAG_EV, "tag values: " + ", ".join(sorted(TAG))]}
s = s[:m.end()] + json.dumps(B, ensure_ascii=False, separators=(",", ":")) + s[end:]
P.write_text(s, encoding="utf-8")
print("bosses", n)
for k, b in B.items():
    if k != "_claims": print(f"  {k}: {b['effective']}")
