#!/usr/bin/env python3
"""Stage 6. Attribute modifiers read inside the running game replace the ones read from the jars (build/patches/gear_runtime.json).

The pack has its own dump script: kubejs/server_scripts/dump_gear.js (run in game with /kubejs custom_command dump_gear) calls
ItemStack.getAttributeModifiers for every tiered tool/armor tag and every ArmorItem and writes kubejs/gear_dump.json. Re-run it and
convert the file when the pack updates. The current file is the 6.6.6hf dump (2,472 items); stale_666 is empty since it matches the
pack. That is what the game applies, after the
attributesetter rebalance and the linggango_tweaks ItemAttributeModifierEvent handlers (per-mod buffs, tier damage floor), so for
every item in it the static extraction, the jar overlays (gear_stats) and the modelled tweaks (gear_data.py runtime_bonus) are
superseded. Items not in the dump (mostly bows, guns, staves without a tier tag) keep the static values, and so do an all-zero dump
(stats in NBT) and a weapon whose dump has no attack damage or speed line.
Conventions kept: melee hit = dmg (1 player base + every ADDITION) x (1 + mul); speed = spd (4 player base + ADDITION) x (1 + mul);
armor pieces carry their armor / toughness / knockback in arm, tough, kbr; every other attribute goes to at[path] = [add, mul] (Goety's as at["ns.path"]),
with MULTIPLY_BASE and MULTIPLY_TOTAL folded into one factor. Marks g["rt"] = 1. Sets the lock g["ga"] from the pack's gate tags. Set totals and offence facts are recomputed."""
import json, pathlib, re
from gearlib import off_of, set_facts
H = pathlib.Path(__file__).resolve().parent
RT = json.loads((H / "gear_runtime.json").read_text(encoding="utf-8"))
R = RT["items"]
# items listed here keep the jar reading (used when a dump is older than the pack; empty for the 6.6.6hf dump)
STALE = set(RT.get("stale_666", []))
SLOT = {"HELMET": "head", "CHESTPLATE": "chest", "LEGGINGS": "legs", "BOOTS": "feet"}
ARMOR_KEYS = {"armor": "arm", "armor_toughness": "tough", "knockback_resistance": "kbr"}

# Goety's attributes (spell potency is a Goety spell level, goety_revelation:spell_power its own spell power) are not Iron's Spells or
# Attributeslib stats: they keep their namespace as "ns.path", the way ars_nouveau.perk.* keys carry theirs, so nothing scores them
# as Iron's spell power, cast time or cooldown. Every other namespace is dropped; the paths that two namespaces then share are the
# same stat (KEEP_SHARED, asserted in apply).
KEEP_NS = {"goety", "goety_revelation", "goetyawaken", "goety_cataclysm", "bosgoety"}
KEEP_SHARED = {"healing_received", "crit_damage", "summon_damage"}

def key(attr):
    if ":" not in attr: return None
    ns, p = attr.split(":", 1)
    p = p.replace("generic.", "").replace("player.", "")
    return ns + "." + p if ns in KEEP_NS else p

# The pack's own gates (linggango_tweaks-common.toml progression_gates): a #forge:<tier>_tools/_armor tag on the item (the dump's
# "tags") or the item in linggango_tweaks:gated/<tier> (gear_gated.json) locks it until that tier's keeper falls. g["ga"] is that
# lock and nothing else: an Act raised by an ingredient or a boss drop moves g["a"] (and g["mg"] says why), never g["ga"].
GATED = json.loads((H / "gear_gated.json").read_text(encoding="utf-8"))
TAG_ACT = {"iron": 2, "golden": 3, "emerald": 4, "diamond": 5, "netherite": 6, "elvenite": 7, "voiderite": 8, "bloody": 10, "helionite": 11}
assert set(TAG_ACT.values()) | {GATED["tiers"]["cataclysm"]} == set(GATED["tiers"].values()), "gear tag tiers and gated tiers disagree"

def gate(i):
    acts = [TAG_ACT[m.group(1)] for t in RT["tags"].get(i, []) for m in [re.match(r"^#forge:([a-z]+)_(?:tools|armor)$", t)] if m and m.group(1) in TAG_ACT]
    if i in GATED["items"]: acts.append(GATED["items"][i])
    return max(acts) if acts else None

def totals(mods):
    """{path: [add, multiply_base, multiply_total]} summed per operation, the way the game sums them"""
    t = {}
    for attr, amt, op in mods:
        k = key(attr)
        if k: t.setdefault(k, [0.0, 0.0, 0.0])[op] += amt
    return t

def eff(g):
    """what the wiki shows: hit and speed for weapons, armor and toughness for armor"""
    a = lambda k: (g["at"].get(k) or [0, 0])
    if g["k"] == "armor": return (round((g.get("arm") or 0) + a("armor")[0], 2), round((g.get("tough") or 0) + a("armor_toughness")[0], 2))
    if g.get("dmg") is None: return None
    return (round((g["dmg"] + a("attack_damage")[0]) * (1 + a("attack_damage")[1]), 2),
            round(((g.get("spd") or 4) + a("attack_speed")[0]) * (1 + a("attack_speed")[1]), 2))

def apply(st):
    GE, GS = st["GE"], st["GS"]
    shared = {}
    for r in R.values():
        for mods in r.values():
            for attr, _, _ in mods:
                if ":" in attr: shared.setdefault(key(attr), set()).add(attr.split(":", 1)[0])
    shared = {k for k, v in shared.items() if len(v) > 1}
    assert shared == KEEP_SHARED, ("attribute paths two mods share changed: check they are one stat before merging them", sorted(shared ^ KEEP_SHARED))
    for g in GE:
        ga = gate(g["id"])
        if ga is None: g.pop("ga", None)
        else: g["ga"] = ga; g["a"] = max(g["a"], ga)
    n = changed = 0
    for g in GE:
        r = R.get(g["id"])
        if not r or g["id"] in STALE: continue
        slot = SLOT.get(g.get("sl")) if g["k"] == "armor" else "mainhand"
        mods = r.get(slot) if slot else (next(iter(r.values())) if len(r) == 1 else None)
        # an all-zero dump is an item whose stats live in its NBT (Blood Magic sentient tools need demon will): keep the jar reading
        if mods is None or not any(m[1] for m in mods): continue
        before = eff(g)
        t = totals(mods); n += 1; g["rt"] = 1
        mul = lambda k: round((1 + t[k][1]) * (1 + t[k][2]) - 1, 4)
        new = {}
        if g["k"] == "armor":
            for k, f in ARMOR_KEYS.items():
                g[f] = round(t.pop(k, [0.0, 0.0, 0.0])[0], 4)
        else:
            for k, f, base in (("attack_damage", "dmg", 1.0), ("attack_speed", "spd", 4.0)):
                # not in the dump (Just Dire Things tools compute damage from their upgrades): keep the jar reading
                if k not in t:
                    if g["at"].get(k): new[k] = g["at"][k]
                    continue
                g[f] = round(base + t[k][0], 4)
                if mul(k): new[k] = [0.0, mul(k)]
                del t[k]
        for k in t:
            if t[k][0] or mul(k): new[k] = [round(t[k][0], 4), mul(k)]
        g["at"] = new
        g["off"] = {k: round(v, 3) for k, v in off_of(new).items() if v > 0.0005}
        changed += eff(g) != before
    by = {g["id"]: g for g in GE}
    for s in GS:
        ps = [by[x] for x in s["p"] if x in by]
        if ps: s.update(set_facts(ps))
    print("gear_runtime: %d items from the game's own dump, %d with different base stats than the jar reading" % (n, changed))
