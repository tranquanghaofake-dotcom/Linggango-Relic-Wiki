#!/usr/bin/env python3
"""Gear stats the full extraction could not read (build/patches/gear_stats.json; the checks are in pack_audit/verify2.json):
  - Summonity armor: armor, toughness and minion slots come from summonity-common.toml, not the ArmorMaterial.
  - Hazen 'N Stuff armor: every piece also carries its HnSArmorMaterial attributes (mana, spell power, cast time...).
  - Iron's Spellbooks armor: every piece also carries its ExtendedArmorMaterials attributes (125-150 mana, spell power, school power).
  - Mowzie's tools: each reads its own tool_config (the table had copied the wrought axe onto all of them).
  - Soulslike trick weapons: Kirkhammer/Silver Sword, Holy Moonlight Sword/Greatsword and Simon's Bowblade/Blade are one
    weapon each, switched in hand, so they become one entry (the stronger form, the other listed in `lv`).
Scores and armor sets are recomputed with the same formulas as build/gear/gear_data.py. Runs after gear_fix. Idempotent."""
import json, pathlib, re
H = pathlib.Path(__file__).resolve().parent
P = H.parent / "src" / "gear_data.js"
D = json.loads((H / "gear_stats.json").read_text(encoding="utf-8"))
s = P.read_text(encoding="utf-8"); i = s.index("[")
GE, e1 = json.JSONDecoder().raw_decode(s, i)
j = s.index("GS=") + 3
GS, e2 = json.JSONDecoder().raw_decode(s, j)
by = {g["id"]: g for g in GE}
SUMMON = re.compile(r"summon|minion|servant|sentry")
RANGED = re.compile(r"arrow|projectile|draw_speed|bow_|ranged")

def A(g, k, part=0):
    v = g["at"].get(k); return v[part] if v else 0.0
def sumk(g, rx, part=0): return sum(v[part] for k, v in g["at"].items() if re.search(rx, k))
def off_of(at):
    sk = lambda rx, part=0: sum(v[part] for k, v in at.items() if re.search(rx, k))
    a = lambda k, part=0: at[k][part] if k in at else 0.0
    o = {"MA": sk(r"spell_power|spell_potency", 1) + sk(r"spell_power|spell_potency") + 0.5 * sk(r"cooldown_reduction|cast_time", 1) + sk(r"max_mana") / 200 + 0.5 * sk(r"mana_regen", 1),
         "SU": sk(SUMMON.pattern, 1) + sk(SUMMON.pattern) * 0.05, "RA": sk(RANGED.pattern, 1) + sk(RANGED.pattern)}
    cc = min(1.0, sk(r"crit(ical)?_(strike_)?(chance|rate)") + sk(r"crit(ical)?_(strike_)?(chance|rate)", 1))
    cd = sk(r"crit(ical)?_(strike_)?damage") + sk(r"crit(ical)?_(strike_)?damage", 1)
    o["ME"] = (1 + a("attack_damage", 1)) * (1 + a("attack_speed", 1)) * (1 + cc * (0.5 + cd)) * (1 + 0.5 * sk(r"life_?steal")) - 1 + a("attack_damage") / 10
    return {k: max(0.0, v) for k, v in o.items()}
def melee_score(g):
    hit = (g["dmg"] + A(g, "attack_damage")) * (1 + A(g, "attack_damage", 1))
    spd = max(0.25, (g.get("spd") or 1.6) + A(g, "attack_speed")) * (1 + A(g, "attack_speed", 1))
    cc = sumk(g, r"crit(ical)?_(strike_)?chance"); cd = sumk(g, r"crit(ical)?_(strike_)?damage") + sumk(g, r"crit(ical)?_(strike_)?damage", 1)
    return hit * spd * (1 + min(cc, 1) * (0.5 + cd)) * (1 + 0.5 * sumk(g, r"life_?steal")) * (1 + 0.05 * A(g, "entity_reach"))
def rescore(g):
    off = off_of(g["at"]); sc = {}
    if g["k"] == "melee" and g.get("dmg") is not None: sc["ME"] = round(melee_score(g), 3)
    elif g["k"] == "ranged": sc["RA"] = round(1 + off["RA"] * 2 + 0.3 * sumk(g, r"crit"), 3)
    elif g["k"] == "magic":
        sc["MA"] = round(1 + off["MA"] * 2, 3)
        if off["SU"] > 0: sc["SU"] = round(1 + off["SU"] * 2, 3)
    elif g["k"] == "summon": sc["SU"] = round(1 + off["SU"] * 2 + 0.02 * (g.get("dmg") or 0), 3)
    g["off"] = {k: round(v, 3) for k, v in off.items() if v > 0.0005}
    if g["k"] != "armor": g["sc"] = sc
def add_at(g, k, flat, mul):
    a = g["at"].setdefault(k, [0.0, 0.0]); a[0] = round(a[0] + flat, 4); a[1] = round(a[1] + mul, 4)

n = {"sum": 0, "hns": 0, "iss": 0, "mow": 0, "pair": 0}
touched = set()
for g in GE:
    ns, p = g["id"].split(":")
    if g.get("sx") or g["k"] != "armor" and ns != "mowziesmobs": continue
    if ns == "summonity" and g["k"] == "armor":
        m = re.match(r"(.+)_(helmet|chestplate|leggings|boots)$", p)
        v = D["summonity_armor"].get(m.group(1), {}).get(m.group(2)) if m else None
        if v:
            g["arm"], g["tough"] = v[0], v[1]
            if v[2]: add_at(g, "minion_slots", v[2], 0)
            g["sx"] = 1; n["sum"] += 1; touched.add(g["id"])
    elif ns == "hazennstuff":
        key = max((k for k in D["hns_item_material"] if p.startswith(k)), key=len, default=None)
        if key:
            for k, (f, mu) in D["hns_materials"][D["hns_item_material"][key]].items(): add_at(g, k, f, mu)
            g["sx"] = 1; n["hns"] += 1; touched.add(g["id"])
    elif ns == "irons_spellbooks":
        key = max((k for k in D["iss_item_material"] if p.startswith(k)), key=len, default=None)
        if key:
            for k, (f, mu) in D["iss_materials"][D["iss_item_material"][key]].items(): add_at(g, k, f, mu)
            g["sx"] = 1; n["iss"] += 1; touched.add(g["id"])
    elif ns == "mowziesmobs" and p in D["mowzie_tools"]:
        g["dmg"], g["spd"] = D["mowzie_tools"][p]; g["sx"] = 1; n["mow"] += 1; touched.add(g["id"])
for g in GE:
    if g["id"] in touched: rescore(g)

# trick-weapon pairs: one entry, the stronger form; recipe and loot stay with the form you can obtain
for pr in D["trick_pairs"]:
    a, b = by.get(pr["main"]), by.get(pr["other"])
    if not a or not b or b["id"] not in by: continue
    for f in ("rc", "lt"):
        if not a.get(f) and b.get(f): a[f] = b[f]
    a["lv"] = [x for x in (a.get("lv") or []) if x != b["id"]] + [b["id"]]
    a["ob"] = a.get("ob") or pr["note"]
    GE = [g for g in GE if g["id"] != b["id"]]; by.pop(b["id"]); n["pair"] += 1

# armor sets that contain a touched piece, or two pieces for one slot (Fireblossom Crown/Helmet, Wizard and Chaos hats are
# alternatives: only the better one counts, the way you can only wear one)
A_ = lambda g, k, part=0: g["at"][k][part] if k in g["at"] else 0.0
def worn(ps):
    best = {}
    for g in ps:
        k = g.get("sl") or g["id"]
        val = (sum(off_of(g["at"]).values()), (g.get("arm") or 0) + A_(g, "armor") + (g.get("tough") or 0))
        if k not in best or val > best[k][0]: best[k] = (val, g)
    return [g for _, g in best.values()]
for t in GS:
    ps = [by[x] for x in t["p"] if x in by]
    dup = len({g.get("sl") or g["id"] for g in ps}) < len(ps)
    if not dup and not any(x["id"] in touched for x in ps): continue
    ps = worn(ps)
    arm = sum((g.get("arm") or 0) + A_(g, "armor") for g in ps); tough = sum((g.get("tough") or 0) + A_(g, "armor_toughness") for g in ps)
    hp = sum(A_(g, "max_health") for g in ps); kbr = sum((g.get("kbr") or 0) + A_(g, "knockback_resistance") for g in ps)
    dtk = -sum(A_(g, "damage_taken") + A_(g, "damage_taken", 1) for g in ps)
    at = {}
    for g in ps:
        for k, v in g["at"].items(): c = at.setdefault(k, [0.0, 0.0]); c[0] += v[0]; c[1] += v[1]
    off = off_of(at)
    defense = arm + 0.8 * tough + 0.5 * hp + 10 * min(1.0, kbr) + 60 * max(0, dtk)
    sc = {"TA": round(defense, 3)}
    for r, v in off.items():
        if v > 0.02: sc[r] = round((1 + v) * defense, 3)
    t.update(arm=round(arm, 2), tough=round(tough, 2), hp=round(hp, 2), kbr=round(kbr, 3), dtk=round(dtk, 3),
             off={r: round(v, 3) for r, v in off.items() if v > 0.0005}, sc=sc)

s = s[:i] + json.dumps(GE, separators=(",", ":"), ensure_ascii=False) + s[e1:]
j = s.index("GS=") + 3; _, e2 = json.JSONDecoder().raw_decode(s, j)
s = s[:j] + json.dumps(GS, separators=(",", ":"), ensure_ascii=False) + s[e2:]
P.write_text(s, encoding="utf-8")
print("gear_stats: %(sum)d Summonity armor, %(hns)d Hazen armor, %(iss)d Iron's armor, %(mow)d Mowzie tools, %(pair)d trick pairs merged" % n)
