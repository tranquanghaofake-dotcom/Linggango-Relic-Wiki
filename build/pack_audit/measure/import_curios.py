"""Curios measured in game (lgw_measure_extra, kubejs/lgw_extra_measure.json) -> build/patches/curio_measure.json.
Usage: python3 pack_audit/measure/import_curios.py lgw_extra_measure.json

Each curio was worn alone, in the first Curios slot type it takes, on a bare 20-health tester for 40 ticks (lgw_measure.js): its
attribute totals, its effects, two diamond-sword swings with it on (the bare tester hits 15), and an 8-damage hit of each kind
sent through the damage events (8 is under the pack's half-health cap, which would hide a reduction).

Per curio:
  sl   the slot type it went into
  d    attribute changes against the bare tester: {attr: change}. Attributes the bare tester does not report sit at their default,
       taken from DEF (or 1 for a multiplier-style attribute whose values sit between 0.5 and 5); wearing any curio adds +0.1
       attack speed by itself except Armageddon's (a pack-wide bonus), so attack speed counts against the usual value of the
       curio's mod (of its slot type when the mod has fewer than 5 curios)
  hit  the lower of the two swings over 15 (a random crit on one swing is left out; crit attributes are scored on their own)
  tk   damage taken of an 8 hit, by kind, against the bare tester's 8: below 1 the curio cuts that kind of damage
  neg  kinds whose test hit it cancelled outright (Opal Necklace, Ace of Iron...): that is a block on a cooldown or a chance, which
       one hit cannot measure (and the pack's zeroed_hit_floor still lets 13% of such a hit land), so those kinds leave tk
  hp   max health added; fx its effects while worn [effect, level, ticks]"""
import json, sys, pathlib, statistics, collections
H = pathlib.Path(__file__).resolve().parents[2] / "patches"
X = json.load(open(sys.argv[1], encoding="utf-8"))
C = X["curios"]; B = C["(none)"]; BA = B["attrs"]
REF = min(h["dmg"] for h in B["hits"]) or 15
# defaults of attributes the bare tester does not list (it lists only those off their default)
DEF = {"irons_spellbooks:max_mana": 100, "attributeslib:crit_chance": 0.05, "attributeslib:crit_damage": 1.5, "attributeslib:dodge_chance": 0,
       "attributeslib:armor_pierce": 0, "attributeslib:armor_shred": 0, "brutality:critical_strike_damage": 1.5, "summonity:minion_slots": 1,
       "forge:block_reach": 4.5, "forge:entity_reach": 3, "forge:entity_gravity": 0.08, "l2hostility:extra_difficulty": 0,
       "brutality:lethality": 0, "minecraft:generic.attack_knockback": 0, "too_many_bows:bow_crit_chance": 0, "brutality:max_rage": 100,
       "summonity:minion_range": 16, "caelus:fall_flying": 0, "confluence:aggro": 0, "confluence:pickup_range": 0,
       "ars_nouveau:ars_elemental.perk.summon_power": 0}
r3 = lambda v: round(v, 3)

# attack speed: the usual value for the curio's mod, else its slot type
AS = "minecraft:generic.attack_speed"
by_slot, by_mod = collections.defaultdict(list), collections.defaultdict(list)
for k, v in C.items():
    if k == "(none)": continue
    x = round(v["attrs"].get(AS, BA[AS]), 3); by_slot[v.get("slot")].append(x); by_mod[k.split(":")[0]].append(x)
mode = lambda vs: collections.Counter(vs).most_common(1)[0][0]
AS0 = {s: mode(vs) for s, vs in by_slot.items()}; ASM = {m: mode(vs) for m, vs in by_mod.items() if len(vs) >= 5}

out = {}
for k, v in C.items():
    if k == "(none)": continue
    o = {"sl": v.get("slot")}
    d = {}
    for a, val in v["attrs"].items():
        if a == AS: base = ASM.get(k.split(":")[0], AS0.get(o["sl"], BA[AS]))
        elif a in BA: base = BA[a]
        elif a in DEF: base = DEF[a]
        elif 0.5 <= val <= 5: base = 1
        else: continue
        if abs(val - base) > 1e-6: d[a] = r3(val - base)
    if d: o["d"] = d
    sw = [h["dmg"] for h in v.get("hits", [])]
    if sw:
        hr = min(sw) / REF
        if abs(hr - 1) > 0.005: o["hit"] = r3(hr)
        tf = {}
        for h in v["hits"]:
            for e, (amp, dur) in (h.get("tfx") or {}).items(): tf[e] = [amp + 1, dur]
        if tf: o["tfx"] = [[e, lv, du] for e, (lv, du) in tf.items()]
        fire = max((h.get("fire", -1) for h in v["hits"]), default=-1)
        if fire > 0: o["fire"] = round(fire / 20, 1)
        heal = max((h.get("heal", 0) for h in v["hits"]), default=0)
        if heal > 0: o["heal"] = r3(heal)
    tk = {}
    # a curio that lowers max health far enough has its test hit held at half its health by the pack's cap (Withered Heart: 1
    # health, the 8 hit lands 0.5): that is the cap, not protection, so that kind is left out
    cap = 0.5 * v.get("hp", 20)
    for kind, (pre, post) in (v.get("hurt") or {}).items():
        if cap < 8 and abs(post - cap) < 0.02: continue
        b = B["hurt"].get(kind, [8, 8])[1]
        if b > 0 and abs(post / b - 1) > 0.01: tk[kind] = r3(post / b)
    neg = [k2 for k2, x in tk.items() if x <= 0.05]
    for k2 in neg: del tk[k2]
    if neg: o["neg"] = neg
    if tk: o["tk"] = tk
    if abs(v.get("hp", 20) - B.get("hp", 20)) > 0.01: o["hp"] = r3(v["hp"] - B["hp"])
    fx = [[e, a + 1, t] for e, (a, t) in (v.get("fx") or {}).items()]
    if fx: o["fx"] = fx
    out[k] = o

res = {"_source": "Linggango 6.6.6hf, measured in game by build/pack_audit/kubejs/server_scripts/lgw_measure.js (lgw_measure_extra, "
       + X.get("started", "") + "); see build/pack_audit/measure/import_curios.py for what each field is.", "ref_hit": REF, "curios": out}
(H / "curio_measure.json").write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
n = lambda f: sum(1 for o in out.values() if f(o))
print(len(out), "curios ->", H / "curio_measure.json")
print("attribute change", n(lambda o: o.get("d")), "| hit change", n(lambda o: o.get("hit")), "| damage taken change", n(lambda o: o.get("tk")),
      "| effects", n(lambda o: o.get("fx")), "| on-hit effects", n(lambda o: o.get("tfx")), "| nothing measurable",
      n(lambda o: not (o.get("d") or o.get("hit") or o.get("tk") or o.get("fx") or o.get("tfx") or o.get("hp") or o.get("fire") or o.get("heal"))))
