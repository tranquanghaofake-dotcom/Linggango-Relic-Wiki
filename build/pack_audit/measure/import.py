"""Turn an in-game measurement (kubejs/lgw_measure.json, written by pack_audit/kubejs/server_scripts/lgw_measure.js) into
build/patches/gear_measure.json, which the gear_measure stage of patches/gear_pipeline.py reads.
Usage: python3 pack_audit/measure/import.py lgw_measure.json [lgw_items.json]   (the plan prep.py wrote; default: next to the measurement)

Per weapon: the hit is the median of the measured swings at full attack strength on a 100,000-health pig with no armor (a swing
1.5x the others is a crit; the median drops it, crits are scored from the crit attributes as before). Effects seen on the target or
the attacker, fire and health gained are kept with how many of the swings showed them (an effect seen on 1 of 3 swings has a
chance). Per armor set: a 20-damage hit of each kind sent through the damage events while the set is worn; the hurt event can
come out 1.5x (a random crit on the incoming hit), so what gets through is scaled back to a 20-damage hit. The effects the wearer
has after 40 ticks and the set bonus: an attribute the wearer has beyond the plain sum of the pieces (only attributes the bare
player also reports, so the base value is known)."""
import json, sys, pathlib, statistics
H = pathlib.Path(__file__).resolve().parents[2] / "patches"
M = json.load(open(sys.argv[1], encoding="utf-8"))
OP = {"ADDITION": 0, "MULTIPLY_BASE": 1, "MULTIPLY_TOTAL": 2}
r2 = lambda v: round(v, 2)

def fx_of(hits, key):
    out = {}
    for h in hits:
        for e, (amp, dur) in (h.get(key) or {}).items():
            o = out.setdefault(e, {"effect": e, "level": amp + 1, "ticks": dur, "n": 0})
            o["n"] += 1; o["level"] = max(o["level"], amp + 1); o["ticks"] = max(o["ticks"], dur)
    return list(out.values())

items = {}
for id_, v in M["melee"].items():
    if id_ == "(none)": continue
    hits = v.get("hits") or []
    if not hits: continue
    d = [h["dmg"] for h in hits]
    ad = v.get("ad", 0)
    o = {"hit": r2(statistics.median(d)), "swings": d, "n": len(hits), "ad": r2(ad), "as": r2(v.get("as", 0))}
    # when the swings stand for normal use (else the score keeps the attribute reading and the page says why):
    #  "dull": 1 or less a swing while the stack has more attack damage: needs charge (energy tools) or a condition;
    #  "once": the first swing lands, the next ones do 1 (spent, recharging): the first swing is the hit;
    #  "grows": far above the attack damage: damage from the target's health (the test pig has 100,000) or a condition
    #  (behind the target, a charged hit), which a plain number would overstate
    # every swing 0: "nohit"; evc when the hit was also cancelled sent straight through the damage events (the item stops its
    # own melee damage, e.g. Create's cardboard sword), else the hit is fine once it lands and the swing needs a condition
    ev = v.get("ev") or {}
    if max(d) <= 0:
        o["st"] = "nohit"
        if ev.get("cancelled"): o["evc"] = 1
        elif ev.get("dmg"): o["evd"] = r2(ev["dmg"])
    elif max(d) <= 1 and ad > 2: o["st"] = "dull"
    elif d[0] > 1 and all(x <= 1 for x in d[1:]): o["st"] = "once"; o["hit"] = r2(d[0])
    elif ad > 0 and o["hit"] > 1.6 * ad: o["st"] = "grows"
    tf = fx_of(hits, "tfx")
    if tf: o["tfx"] = tf
    sf = fx_of(hits, "sfx")
    if sf: o["sfx"] = sf
    fire = [h["fire"] for h in hits if h.get("fire", -1) > 0]
    if fire: o["fire"] = [r2(max(fire) / 20), len(fire)]
    heal = [h["heal"] for h in hits if h.get("heal", 0) > 0]
    if heal: o["heal"] = [r2(statistics.median(heal)), len(heal)]
    if not v.get("ticked", True): o["unticked"] = 1
    items[id_] = o

def taken(hurt):
    o = {}
    for k, (pre, post) in (hurt or {}).items():
        if pre > 0: o[k] = r2(post / pre * 20)
    return o

# what the bare player reports, and the pieces' own modifiers, for the set bonus
base = M["armor"]["(none)"]["attrs"]
A = M.get("attrs", {})
SLOT = {"HEAD": "head", "CHEST": "chest", "LEGS": "legs", "FEET": "feet"}
plan_sets = {}
try:
    P = json.load(open(sys.argv[2] if len(sys.argv) > 2 else pathlib.Path(sys.argv[1]).with_name("lgw_items.json"), encoding="utf-8"))
    plan_sets = {s["k"]: s["p"] for s in P.get("sets", [])}
except (OSError, ValueError):
    print("no plan file: set bonuses left out")

def expected(k):
    pieces = plan_sets.get(k)
    if pieces is None: return None
    add, mb, mt = {}, {}, {}
    # one piece per slot: a set with a crown and a helmet wore the later one (setItemSlot replaces), so only that one counts
    worn = {sl: pid for pid, sl in pieces}
    for sl, pid in worn.items():
        for attr, amt, op in (A.get(pid, {}).get(SLOT.get(sl, "chest")) or []):
            op = OP.get(op, op)
            if op == 0: add[attr] = add.get(attr, 0) + amt
            elif op == 1: mb[attr] = mb.get(attr, 0) + amt
            else: mt[attr] = mt.get(attr, 1) * (1 + amt)
    out = {}
    for attr, b in base.items():
        out[attr] = (b + add.get(attr, 0)) * (1 + mb.get(attr, 0)) * mt.get(attr, 1)
    return out

EFFECT_ATTR = {"minecraft:speed": ["minecraft:generic.movement_speed"], "minecraft:slowness": ["minecraft:generic.movement_speed"],
               "minecraft:health_boost": ["minecraft:generic.max_health"], "minecraft:strength": ["minecraft:generic.attack_damage"],
               "minecraft:weakness": ["minecraft:generic.attack_damage"], "minecraft:luck": ["minecraft:generic.luck"],
               "minecraft:unluck": ["minecraft:generic.luck"], "minecraft:haste": ["minecraft:generic.attack_speed"],
               "minecraft:mining_fatigue": ["minecraft:generic.attack_speed"]}
# the game clamps these: a set whose pieces add up past the cap reads the cap
CAP = {"minecraft:generic.knockback_resistance": 1.0}
none_taken = taken(M["armor"]["(none)"].get("hurt"))
sets = {}
for k, v in M["armor"].items():
    if k == "(none)": continue
    at = v.get("attrs", {})
    o = {"taken": taken(v.get("hurt")), "hp": r2(v.get("hp", 0)), "arm": r2(at.get("minecraft:generic.armor", 0)),
         "tough": r2(at.get("minecraft:generic.armor_toughness", 0)), "kbr": r2(at.get("minecraft:generic.knockback_resistance", 0))}
    # protection the armor formula does not see (a hurt or damage handler: Resonarium pushes a hit to the floor): the melee hit
    # that got through, against Apothic's a / (a + armor) on what the hurt event left, held to the pack's half-health cap and
    # 13% floor. Below 0.85 of it, the share is kept and counts as damage taken off
    pre, post = (v.get("hurt") or {}).get("melee", [0, 0])
    if pre > 0:
        av = 10 if pre < 20 else 10 + (pre - 20) / 2
        pred = max(min(pre * av / (av + o["arm"]), 0.5 * v.get("hp", 20)), 0.13 * pre)
        if pred > 0 and post < 0.85 * pred: o["evr"] = r2(post / pred)
    if v.get("abs"): o["abs"] = r2(v["abs"])
    fx = [{"effect": e, "level": amp + 1, "ticks": dur} for e, (amp, dur) in (v.get("fx") or {}).items()]
    if fx: o["fx"] = fx
    ex = expected(k)
    if ex:
        bon = {}
        # attributes an active effect moves (Speed, Health Boost...) are that effect, not a bonus of their own
        moved = {a for e in (v.get("fx") or {}) for a in EFFECT_ATTR.get(e, ())}
        for attr, want in ex.items():
            got = v["attrs"].get(attr)
            if got is None or attr in moved: continue
            if attr in CAP: want = min(want, CAP[attr])
            if abs(got - want) > max(0.01, 0.01 * abs(want)): bon[attr.split(":")[-1].replace("generic.", "")] = r2(got - want)
        if bon: o["bonus"] = bon
    sets[k] = o

out = {"_source": "Linggango 6.6.6hf, measured in game by build/pack_audit/kubejs/server_scripts/lgw_measure.js ("
       + M.get("started", "") + "): a FakePlayer given Armageddon's twelve Keeper advancements (their tier locks cancel every "
       "tiered weapon's hits otherwise). See pack_audit/measure/import.py for what each number is.",
       "none_taken": none_taken, "items": items, "sets": sets}
(H / "gear_measure.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(len(items), "weapons,", len(sets), "sets ->", H / "gear_measure.json")
print("no armor, of a 20 hit:", none_taken)
print("sets with worn effects:", sum(1 for s in sets.values() if s.get("fx")), " with a set bonus:", sum(1 for s in sets.values() if s.get("bonus")))
