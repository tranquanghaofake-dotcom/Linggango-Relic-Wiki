"""Vanilla 1.20.1 loot-table chances, shared by side_bosses/loot_chance.py, side_bosses/loot.py, drops.py and chests.py.

chances(table, load, tags=None) -> {item id: {"p", "lo", "hi", "cond"}} for one generation of the table (one kill, one chest):
  p       the chance of at least one of the item; lo-hi the stack size when it comes (count_text() prints it)
  cond    conditions on the way that were taken as met (killed_by_player, entity_properties, mod conditions...)
load(table id) returns a nested table's JSON (or None: its id goes into chances.missing); tags maps a tag to its ids, for tag entries.

What the game does and this follows:
- a pool runs if its conditions pass, then rolls times (a number provider: constant, uniform = an inclusive integer range after
  rounding, binomial = successes of n draws); each roll expands the entries again and picks one of those that came out, by weight
  (one alone is taken whatever its weight; weight 0 never). So an item of weight w among W turns up with
  P = sum_n P(rolls = n) (1 - (1 - w/W)^n); pools are independent, so an item in several is 1 - prod(1 - p).
- entries: item, tag (expand true: one pick per item of the tag), loot_table (run in full when picked), empty, dynamic; group expands
  every child, sequence its children until one fails, alternatives the first child that passes; a composite's conditions gate its
  children. Random conditions on entries change which entries are in the draw: their pass/fail cases are summed exactly
  (up to 12 random entries in a pool, else each entry's yield is scaled by its chance).
- conditions: random_chance; random_chance_with_looting at looting 0 (its plain chance); table_bonus at enchantment level 0;
  inverted, any_of / alternative, all_of; killed_by_player is met (the player kills the boss), its inverse is not; survives_explosion
  is met. Conditions on what the game state is (entity_properties, damage_source_properties, match_tool, time, weather, scores,
  mod conditions) cannot be known here: they are taken as met, and so is their inverse, and named in cond.
- counts: set_count (replace, or add: true), limit_count; a count that can come out 0 lowers p (the stack is empty).
Not followed: luck. bonus_rolls (rolls + floor(bonus_rolls x luck)) and entry quality (weight + quality x luck) act only with luck
from the killer or opener; at luck 0 they add nothing, which is what these numbers assume. Looting counts (looting_enchant) likewise."""
import itertools, math

def jround(x): return math.floor(x + 0.5)  # NumberProvider.getInt: Math.round

def mean(v):
    """a float number provider's mean (binomial p and the like)"""
    if isinstance(v, (int, float)): return float(v)
    if not isinstance(v, dict): return 1.0
    t = v.get("type", "").split(":")[-1] or ("uniform" if "min" in v or "max" in v else "binomial" if "n" in v else "constant")
    if t == "uniform": return (mean(v.get("min", 0)) + mean(v.get("max", 0))) / 2
    if t == "binomial": return mean(v.get("n", 1)) * mean(v.get("p", 0.5))
    return float(v.get("value", 1)) if isinstance(v.get("value", 1), (int, float)) else 1.0

def dist(v):
    """an integer number provider as {value: probability}"""
    if isinstance(v, (int, float)): return {jround(v): 1.0}
    if not isinstance(v, dict): return {1: 1.0}
    t = v.get("type", "").split(":")[-1] or ("uniform" if "min" in v or "max" in v else "binomial" if "n" in v else "constant")
    out = {}
    if t == "constant": return {jround(mean(v)): 1.0}
    if t == "uniform":  # Mth.nextInt(min.getInt, max.getInt): inclusive; min when max is not above it
        for lo, pl in dist(v.get("min", 0)).items():
            for hi, ph in dist(v.get("max", 0)).items():
                xs = range(lo, hi + 1) if hi > lo else [lo]
                for x in xs: out[x] = out.get(x, 0) + pl * ph / len(xs)
        return out
    if t == "binomial":
        p = mean(v.get("p", 0.5))
        for n, pn in dist(v.get("n", 1)).items():
            for k in range(max(n, 0) + 1): out[k] = out.get(k, 0) + pn * math.comb(n, k) * p ** k * (1 - p) ** (n - k)
        return out
    return {1: 1.0}  # score / storage providers: unknown here

def cond(cs, why, neg=False):
    """chance that every condition of the list passes (taken as independent), or with neg that the list fails"""
    p = 1.0
    for c in cs or []: p *= c1(c, why)
    return 1 - p if neg else p
def c1(c, why, neg=False):
    t = c.get("condition", "").split(":")[-1] if isinstance(c, dict) else ""
    if t in ("random_chance", "random_chance_with_looting"): x = float(c.get("chance", 1)); return 1 - x if neg else x
    if t == "table_bonus": x = float((c.get("chances") or [1])[0]); return 1 - x if neg else x
    if t == "inverted": return c1(c.get("term", {}), why, not neg)
    if t in ("any_of", "alternative"):
        q = math.prod(1 - c1(x, why) for x in c.get("terms", []))
        return q if neg else 1 - q
    if t == "all_of": return cond(c.get("terms", []), why, neg)
    if t == "killed_by_player": why.add("not killed by a player" if neg else "killed by a player"); return 0.0 if neg else 1.0
    if t == "survives_explosion": return 0.0 if neg else 1.0
    why.add(("not " if neg else "") + (t or "?")); return 1.0

def counts(fns, why):
    """stack size as {count: probability} after set_count / limit_count, 1 to start with"""
    d = {1: 1.0}
    for f in fns:
        t = f.get("function", "").split(":")[-1]
        if t not in ("set_count", "limit_count"): continue
        q = cond(f.get("conditions"), why); nd = {}
        for c, pc in d.items():
            if t == "set_count":
                for x, px in dist(f.get("count", 1)).items():
                    k = max(0, (c if f.get("add") else 0) + x); nd[k] = nd.get(k, 0) + pc * px * q
            else:
                lim = f.get("limit", {}); lim = lim if isinstance(lim, dict) else {"min": lim, "max": lim}
                lo = jround(mean(lim["min"])) if "min" in lim else -10**9; hi = jround(mean(lim["max"])) if "max" in lim else 10**9
                k = min(max(c, lo), hi); nd[k] = nd.get(k, 0) + pc * q
            if q < 1: nd[c] = nd.get(c, 0) + pc * (1 - q)
        d = nd
    return d

def chances(t, load, tags=None, d=0, seen=()):
    """per item of a table: {"p", "lo", "hi", "cond"} (see the module doc)"""
    out = {}
    if not isinstance(t, dict) or d > 6: return out
    tfn = t.get("functions", [])
    for pool in t.get("pools", []):
        why = set(); pq = cond(pool.get("conditions"), why)
        if pq <= 0: continue
        pfn = pool.get("functions", []) + tfn
        nodes = []
        def node(e, wy):
            w = set(wy); n = {"e": e, "t": e.get("type", "").split(":")[-1], "q": cond(e.get("conditions"), w), "why": w}
            n["kids"] = [node(k, w) for k in e.get("children", [])] if n["t"] in ("alternatives", "group", "sequence") else []
            nodes.append(n); return n
        top = [node(e, why) for e in pool.get("entries", [])]
        rnd = [n for n in nodes if 0 < n["q"] < 1]
        exact = len(rnd) <= 12
        yields = {}  # id(leaf node) -> {item: (p, lo, hi, why)}
        def yld(n, item=None):
            k = (id(n), item)
            if k in yields: return yields[k]
            e = n["e"]; r = {}
            if n["t"] == "item" and e.get("name") not in (None, "minecraft:air"):
                c = counts(e.get("functions", []) + pfn, n["why"]); r[e["name"]] = (c, n["why"])
            elif n["t"] == "tag":
                ids = [item] if item else tag_items(e.get("name", ""), tags)
                for i in ids: r[i] = (counts(e.get("functions", []) + pfn, n["why"]), n["why"])
            elif n["t"] == "loot_table":
                nm = e.get("name") if isinstance(e.get("name"), str) else e.get("value")
                sub = load(nm) if isinstance(nm, str) and nm not in seen else None
                if sub is None and isinstance(nm, str) and nm not in seen: chances.missing.add(nm)
                for i, v in chances(sub, load, tags, d + 1, seen + (nm,)).items():
                    r[i] = ({1: v["p"], 0: 1 - v["p"]}, n["why"] | set(v["cond"]), v["lo"], v["hi"])
            yields[k] = r; return r
        def expand(n, ok, cand):  # vanilla expand(): whether the entry came out, the picks it adds
            if not ok(n): return False
            if n["t"] == "alternatives": return any(expand(k, ok, cand) for k in n["kids"])
            if n["t"] == "sequence": return all(expand(k, ok, cand) for k in n["kids"])
            if n["t"] == "group":
                for k in n["kids"]: expand(k, ok, cand)
                return True
            w = n["e"].get("weight", 1)
            if w > 0:
                if n["t"] == "tag" and n["e"].get("expand") and tag_items(n["e"].get("name", ""), tags):
                    cand += [(n, w, i) for i in tag_items(n["e"].get("name", ""), tags)]
                else: cand.append((n, w, None))
            return True
        def scale(n):  # the inexact case: a random entry is always in the draw, its yield scaled by its chance
            s = 1.0; m = n
            while m is not None: s *= m["q"] if 0 < m["q"] < 1 else 1; m = m.get("up")
            return s
        for n in nodes:
            for k in n["kids"]: k["up"] = n
        roll = {}  # item -> chance in one roll, and its stack sizes and conditions
        cases = itertools.product((True, False), repeat=len(rnd)) if exact else [()]
        for case in cases:
            on = dict(zip(map(id, rnd), case)); pc = math.prod(n["q"] if on[id(n)] else 1 - n["q"] for n in rnd) if exact else 1.0
            ok = (lambda n: n["q"] >= 1 or (n["q"] > 0 and on[id(n)])) if exact else (lambda n: n["q"] > 0)
            cand = []
            for n in top: expand(n, ok, cand)
            tw = sum(w for _, w, _ in cand)
            for n, w, it in cand:
                pick = pc * (1.0 if len(cand) == 1 else w / tw) * (1.0 if exact else scale(n))
                for i, y in yld(n, it).items():
                    c = y[0]; got = sum(v for x, v in c.items() if x >= 1)
                    sizes = [x for x, v in c.items() if x >= 1 and v > 0]
                    lo, hi = (y[2], y[3]) if len(y) > 2 else (min(sizes), max(sizes)) if sizes else (None, None)
                    o = roll.setdefault(i, [0.0, lo, hi, set()]); o[0] += pick * got; o[3] |= y[1]
                    if lo is not None: o[1] = lo if o[1] is None else min(o[1], lo); o[2] = hi if o[2] is None else max(o[2], hi)
        rd = dist(pool.get("rolls", 1))
        for i, (p1, lo, hi, w) in roll.items():
            p = pq * sum(pn * (1 - (1 - min(p1, 1.0)) ** n) for n, pn in rd.items() if n > 0)
            o = out.setdefault(i, {"p": 0.0, "lo": lo, "hi": hi, "cond": set()})
            o["p"] = 1 - (1 - o["p"]) * (1 - p); o["cond"] |= w
            if lo is not None: o["lo"] = lo if o["lo"] is None else min(o["lo"], lo); o["hi"] = hi if o["hi"] is None else max(o["hi"], hi)
    for o in out.values(): o["cond"] = sorted(o["cond"])
    return {i: o for i, o in out.items() if o["p"] > 0}
chances.missing = set()  # nested tables load() did not find

def tag_items(tag, tags, d=0):
    tag = tag.lstrip("#")
    if not tags or d > 6: return []
    out = []
    for x in tags.get(tag, []):
        x = x["id"] if isinstance(x, dict) else x; x = x.rstrip("?")
        out += tag_items(x, tags, d + 1) if x.startswith("#") else [x]
    return out

def count_text(o):
    lo, hi = o.get("lo"), o.get("hi")
    if lo is None: return "1"
    return f"{lo:g}" if lo == hi else f"{lo:g}–{hi:g}"
