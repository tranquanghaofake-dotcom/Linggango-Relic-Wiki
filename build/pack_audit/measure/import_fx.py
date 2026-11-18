"""Status effects measured in game (lgw_measure_fx, kubejs/lgw_fx_measure.json) -> build/patches/effect_measure.json and effect_sources.json.
Usage: python3 -I pack_audit/measure/import_fx.py lgw_fx_measure.json MODS_DIR VANILLA_CLIENT_JAR

lgw_measure.js (section 5) puts each effect at level I and II on a pig of its own (1,000 max health at 500, AI on, 100 ticks of the world's own time)
and on the tester (20 of its ticks, then three bare-hand swings at a fresh pig, crit off). This file keeps, per effect and level, only what differs
from the bare pig of the same batch and the bare tester:
  hp    health gained (+) or lost (-) per second on the pig
  tk    damage taken from a 10-damage hit, as a share of 10 (1.33 = takes 33% more); absorption counts as taken
  ab    absorption (golden hearts) the pig has
  hit   [bare tester's bare-hand hit, the hit with the effect] (the smallest of three)
  at    attributes that differ: {attribute: [without, with]} (the tester's where it has the attribute, else the pig's; the crit chance the
        script zeroes itself is left out)
  dy    blocks the pig rose (+) or sank (-) in the 5 seconds, beyond the bare pig
  fire  the pig is on fire;  frz: the pig is freezing
  gx    other effects the tester gained at every level measured (the tester is measured alone; the pigs stand 16 blocks apart and an aura
        reaches its neighbours; a single level's gain can be a random event of another mod)
  tfx   effects a hit with it puts on the target
  end   the effect was gone before the 5 seconds were up (an instant effect always is: not marked)
  dead  the pig died
  nb    the pig was reached by a neighbour's effect: its pig readings (hp, tk, ab, dy, fire, frz, dead, the pig's attributes) are dropped
Not kept: the tester's may-fly flag (noise), a hit of 999 or more (the target pig gone), and any reading only one of the two levels shows
(the same reading, the same way, at both levels or not at all).
An effect that crashes the server when it ticks (plan fxSkip) is {"crash": 1}.
Sources: every potion's effects and every food's (effect_sources.json: {effect: [[kind, name, level, seconds, chance]]}), names from the jars' lang."""
import json, sys, math, re, glob, zipfile, pathlib
H = pathlib.Path(__file__).resolve().parents[2] / "patches"
X = json.load(open(sys.argv[1], encoding="utf-8")); MODS, CLIENT = sys.argv[2], sys.argv[3]
G = {e["id"]: e for e in json.load(open(H / "game_registry.json", encoding="utf-8"))["effects"]}
r2 = lambda v: round(v, 2)
nan = lambda v: isinstance(v, float) and math.isnan(v)
SELF = {"attributeslib:crit_chance"}

def level(amp):
    P, L = X["fxPig"][amp], X["fxPlayer"][amp]
    base = {k: v for k, v in P.items() if k.startswith("(none)")}
    LB = L["(none)"]
    out = {}
    # pigs are measured in batches of fxBatch, each after its bare pig: the bare pig of an effect's batch is its baseline
    order = [k for k in P]; bb = None
    for k in order:
        if k.startswith("(none)"): bb = P[k]; continue
        v, pl, o = P[k], L.get(k, {}), {}
        # gained by the tester (measured alone, one effect at a time): the effects it gives with it
        pgx = set(pl.get("fx") or {}) - {k} - set(LB.get("fx") or {})
        # a pig that carries an effect neither its own nor one the tester gained was reached by a neighbour's aura (full run 2: the same
        # 7 curses on 22 pigs of one batch): its pig readings are dropped, the tester's kept
        nb = set(v.get("fx") or {}) - {k} - pgx - set(bb.get("fx") or {})
        if nb: v = {"attrs": {}}; o["nb"] = 1
        if v.get("alive") is False: o["dead"] = 1
        if v.get("hp") is not None and v.get("alive") is not False:
            d = (v["hp"] - bb["hp"]) / 5
            if abs(d) >= 0.05: o["hp"] = r2(d)
        if v.get("took") is not None and bb.get("took"):
            t = v["took"] / bb["took"]
            if abs(t - 1) > 0.01: o["tk"] = r2(t)
        if (v.get("abs") or 0) - (bb.get("abs") or 0) > 0.01: o["ab"] = r2(v["abs"] - (bb.get("abs") or 0))
        # a hit of 999 or more is the whole 1,000-health target pig gone (24 effects, the same at both levels, the swings next to them normal): the
        # test cannot read that hit, so none is kept
        if pl.get("hit") is not None and LB.get("hit") is not None and abs(pl["hit"] - LB["hit"]) > 0.01 and pl["hit"] < 999: o["hit"] = [LB["hit"], pl["hit"]]
        at = {}
        for a, x in (v.get("attrs") or {}).items():
            y = (bb.get("attrs") or {}).get(a)
            if a in SELF or nan(x) or nan(y) or y is None or abs(x - y) < 1e-6: continue
            at[a] = [y, x]
        # the tester's reading wins where it has the attribute (it has more: spell power, mana…); one the bare tester lacks is left to the pig
        for a, x in (pl.get("attrs") or {}).items():
            y = (LB.get("attrs") or {}).get(a)
            if a in SELF or y is None or nan(x) or nan(y): continue
            if abs(x - y) < 1e-6: at.pop(a, None)
            else: at[a] = [y, x]
        if at: o["at"] = at
        dy = (v.get("dy") or 0) - (bb.get("dy") or 0)
        if abs(dy) >= 0.5: o["dy"] = r2(dy)
        if (v.get("fire") or 0) > 0 and not (bb.get("fire") or 0) > 0: o["fire"] = 1
        if (v.get("frozen") or 0) > 0 and not (bb.get("frozen") or 0) > 0: o["frz"] = 1
        if pgx: o["gx"] = sorted(pgx)
        tfx = sorted(set(pl.get("tfx") or {}) - set(LB.get("tfx") or {}))
        if tfx: o["tfx"] = tfx
        if v.get("added") and k not in (v.get("fx") or {}) and not (G.get(k) or {}).get("instant"): o["end"] = 1
        # may-fly is not kept: Slowness, Strength and Weakness read it (full run 2), so the flag is noise on a FakePlayer
        out[k] = o
    # a bare pig that changed at all means something in its batch reached it
    for bk, b in base.items():
        if b.get("hp") or (b.get("fx") or {}) or b.get("alive") is False: print("warning: bare pig", bk, "changed:", {x: b.get(x) for x in ("hp", "fx", "alive", "dy")})
    return out

lv = [level(a) for a in sorted(X["fxPig"], key=int)]
# some mods put an effect on a player now and then (Celestial Core's curses, Tetanus: scattered over 10 to 24 testers each, full run 2); an
# effect counts as given with another only when the tester gained it at every level measured, two separate samples
for k in set().union(*[set(x) for x in lv]):
    both = set.intersection(*[set(x.get(k, {}).get("gx", [])) for x in lv])
    for x in lv:
        if k in x:
            if both: x[k]["gx"] = sorted(both)
            else: x[k].pop("gx", None)
# a reading counts only when the other level shows the same reading the same way (full run 3: dozens of unrelated effects read the same armor 6,
# toughness 4, attack speed 12 at level II only, which is the test's surroundings, not the effect): what one level alone shows is dropped
sg = lambda x: (x > 0) - (x < 0)
def agree(a, b):
    o = {}
    for f, x in a.items():
        if f in ("nb", "gx"): o[f] = x; continue
        if f == "at":
            at = {t: pq for t, pq in x.items() if (b.get("at") or {}).get(t) and sg(pq[1] - pq[0]) == sg(b["at"][t][1] - b["at"][t][0])}
            if at: o["at"] = at
        elif f in ("hp", "dy", "ab"):
            if b.get(f) is not None and sg(x) == sg(b[f]): o[f] = x
        elif f == "tk":
            if b.get(f) is not None and sg(x - 1) == sg(b[f] - 1): o[f] = x
        elif f == "hit":
            if b.get(f) and sg(x[1] - x[0]) == sg(b[f][1] - b[f][0]): o[f] = x
        elif f in b: o[f] = x
    return o
if len(lv) == 2:
    for k in set(lv[0]) & set(lv[1]):
        lv[0][k], lv[1][k] = agree(lv[0][k], lv[1][k]), agree(lv[1][k], lv[0][k])
M = {}
for k in sorted(set().union(*[set(x) for x in lv])):
    M[k] = {"l": [x.get(k, {}) for x in lv]}
for k in X.get("fxSkip", []): M[k] = {"crash": 1}
json.dump(M, open(H / "effect_measure.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)

# names of potions and foods from the jars' en_us
lang = {}
for p in sorted(glob.glob(MODS + "/*.jar")) + [CLIENT]:
    try: z = zipfile.ZipFile(p)
    except Exception: continue
    for n in z.namelist():
        if re.match(r"assets/[^/]+/lang/en_us\.json$", n):
            try: d = json.loads(re.sub(r",(\s*[}\]])", r"\1", z.read(n).decode("utf-8", "replace")))
            except Exception: continue
            for kk, v in d.items():
                if isinstance(v, str) and (kk.startswith("item.") or kk.startswith("block.")): lang.setdefault(kk, re.sub(r"§.", "", v))
def potion_name(pid):
    ns, path = pid.split(":", 1)
    for p2 in (path, re.sub(r"^(long|strong|extended|extra|very_long|very_strong)_", "", path), re.sub(r"_(long|strong|\d+)$", "", path)):
        n = lang.get("item.minecraft.potion.effect." + p2)
        if n: return n
    return "Potion: " + path.replace("_", " ")
def item_name(iid):
    ns, path = iid.split(":", 1)
    return lang.get("item.%s.%s" % (ns, path)) or lang.get("block.%s.%s" % (ns, path)) or path.replace("_", " ").title()
S = {}
src = X.get("fxSources") or {}
for pid, l in (src.get("potions") or {}).items():
    for e, amp, dur in l: S.setdefault(e, []).append(["potion", potion_name(pid), amp + 1, round(dur / 20), 1])
for iid, l in (src.get("foods") or {}).items():
    for e, amp, dur, ch in l: S.setdefault(e, []).append(["food", item_name(iid), amp + 1, round(dur / 20), ch, iid])
for e in S: S[e] = sorted({json.dumps(x): x for x in S[e]}.values(), key=lambda x: (x[0], x[1], x[2], -x[3]))
json.dump(S, open(H / "effect_sources.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
print("effects measured", sum(1 for v in M.values() if "l" in v), "crash", sum(1 for v in M.values() if v.get("crash")),
      "with a reading", sum(1 for v in M.values() if any(v.get("l", [{}]))), "| sources for", len(S), "effects:",
      sum(1 for e in S for x in S[e] if x[0] == "potion"), "potion rows,", sum(1 for e in S for x in S[e] if x[0] == "food"), "food rows")
