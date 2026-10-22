"""Facts about gear that more than one script needs, in one place: which attributes count as offence for a role (`off_of`) and how the
pieces of an armor set add up (`set_facts`). Scoring (what those facts are worth) lives only in src/gear.js; nothing here ranks anything.
Used by patches/gear_stats.py and build/gear/gear_data.py (build.sh copies this file next to it)."""
import re
SUMMON = re.compile(r"summon|minion|servant|sentry")
RANGED = re.compile(r"arrow|projectile|draw_speed|bow_|ranged")

def A(g, k, part=0):
    v = g["at"].get(k); return v[part] if v else 0.0

def off_of(at):
    """offence bonus per role from summed attributes {attr: [add, mul]} (fractions of extra output)"""
    sk = lambda rx, part=0: sum(v[part] for k, v in at.items() if re.search(rx, k))
    a = lambda k, part=0: at[k][part] if k in at else 0.0
    o = {"MA": sk(r"spell_power|spell_potency", 1) + sk(r"spell_power|spell_potency") + 0.5 * sk(r"cooldown_reduction|cast_time", 1) + sk(r"max_mana") / 200 + 0.5 * sk(r"mana_regen", 1),
         "SU": sk(SUMMON.pattern, 1) + sk(SUMMON.pattern) * 0.05, "RA": sk(RANGED.pattern, 1) + sk(RANGED.pattern)}
    # melee: expected damage multiplier. Two crit systems exist (attributeslib crit_* and brutality critical_strike_*);
    # their chances add up but a hit can only crit once, so chance is capped at 100%; a crit adds +50% plus crit damage.
    cc = min(1.0, sk(r"crit(ical)?_(strike_)?(chance|rate)") + sk(r"crit(ical)?_(strike_)?(chance|rate)", 1))
    cd = sk(r"crit(ical)?_(strike_)?damage") + sk(r"crit(ical)?_(strike_)?damage", 1)
    o["ME"] = (1 + a("attack_damage", 1)) * (1 + a("attack_speed", 1)) * (1 + cc * (0.5 + cd)) * (1 + 0.5 * sk(r"life_?steal")) - 1 + a("attack_damage") / 10
    return {k: max(0.0, v) for k, v in o.items()}

def worn(ps):
    """two pieces for one slot (Fireblossom Crown/Helmet, Wizard and Chaos hats) are alternatives: only the better one counts"""
    best = {}
    for g in ps:
        k = g.get("sl") or g["id"]
        val = (sum(off_of(g["at"]).values()), (g.get("arm") or 0) + A(g, "armor") + (g.get("tough") or 0))
        if k not in best or val > best[k][0]: best[k] = (val, g)
    return [g for _, g in best.values()]

def set_facts(ps):
    """totals of an armor set's worn pieces: the facts gear.js scores"""
    ps = worn(ps)
    at = {}
    for g in ps:
        for k, v in g["at"].items(): c = at.setdefault(k, [0.0, 0.0]); c[0] += v[0]; c[1] += v[1]
    dtk = -sum(A(g, "damage_taken") + A(g, "damage_taken", 1) for g in ps)
    off = off_of(at)
    return {"arm": round(sum((g.get("arm") or 0) + A(g, "armor") for g in ps), 2),
            "tough": round(sum((g.get("tough") or 0) + A(g, "armor_toughness") for g in ps), 2),
            "hp": round(sum(A(g, "max_health") for g in ps), 2),
            "kbr": round(sum((g.get("kbr") or 0) + A(g, "knockback_resistance") for g in ps), 3),
            "dtk": round(dtk, 3), "off": {r: round(v, 3) for r, v in off.items() if v > 0.0005}}
