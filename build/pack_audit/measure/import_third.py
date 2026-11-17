"""The third run (lgw_measure_third, kubejs/lgw_third_measure.json) -> adds to build/patches/gear_measure.json and curio_measure.json.
Usage: python3 pack_audit/measure/import_third.py lgw_third_measure.json [lgw_third_1k.json]   (after import.py and import_curios.py; the run's "grows"
weapons are pooled by import.py itself, given the file as its fourth argument)

  ranged  each bow, crossbow and throwable shot three times at a 10,000-health pig 5 blocks in front of the tester, arrows in the
          off hand, a bow drawn 40 ticks: per item {hit: median shot, shots, how} into gear_measure.json items[id].rng. A shot that
          missed or never left reads 0: an item with every shot 0 is kept as {miss: 1} (the page says it was not measured). t: the
          ticks a shot takes (a crossbow's charge, else the draw that reaches full speed).
          A run where most shooters read 0 is a fault of the run, not of the items (third run: 113 of 118, with arrows that landed
          and did nothing): its shots are left out
  blocks  each curio that cancelled a test hit (Ace of Iron, Opal Necklace...) worn alone and hit with 8 melee damage ten times, a
          second or two apart. One that cancelled the melee test hit, or any of the ten (Nullifying Dice: explosions in the extra
          run, 1 of 10 melee hits here): {n, blocked, tk} into curio_measure.json curios[id].blk, its
          block rate at that pace and the melee damage it lets through on average (a blocked hit as the 13% the pack's
          zeroed_hit_floor lets land). One that cancelled another kind is not tested for that kind here, but its ten melee hits
          replace the one melee hit of the extra run (Halo of the End: 13% of one hit, half of each of ten)"""
import json, sys, pathlib, statistics
H = pathlib.Path(__file__).resolve().parents[2] / "patches"
X = json.load(open(sys.argv[1], encoding="utf-8"))
# a second run of the same shooters at a 1,000-health target (plan "rhp": 1000; 2026-11-17): its median shot is the one scored, the
# health melee takes for a share-of-max-health weapon; the 10,000-health shot is kept as h10k when it hit harder (a share of the
# target's health: Rainfall Serenity)
K1 = (json.load(open(sys.argv[2], encoding="utf-8")).get("ranged") or {}) if len(sys.argv) > 2 else {}
r2 = lambda v: round(v, 2)
GM = json.loads((H / "gear_measure.json").read_text(encoding="utf-8"))
CM = json.loads((H / "curio_measure.json").read_text(encoding="utf-8"))
items, curios = GM["items"], CM["curios"]

nr = nm = 0
R = X.get("ranged") or {}
hit_any = sum(1 for v in R.values() if any(s.get("dmg", 0) > 0 for s in v.get("shots", [])))
# a run whose calibration shooter (the vanilla Bow) hit is sound however many others missed: Mage weapons with no attack of their
# own and throwables that need other targets read 0 by nature (2026-11-17)
bow_hit = any(s.get("dmg", 0) > 0 for s in (R.get("minecraft:bow") or {}).get("shots", []))
if R and hit_any < 0.5 * len(R) and not bow_hit:
    print("ranged left out:", hit_any, "of", len(R), "shooters did any damage"); R = {}
for k, v in R.items():
    d = [s.get("dmg", 0) for s in v.get("shots", [])]
    if not d: continue
    o = items.setdefault(k, {"ad": r2(v.get("ad", 0))})
    hit = [x for x in d if x > 0]
    if not hit: o["rng"] = {"miss": 1, "shots": d}; nm += 1; continue
    o["rng"] = {"hit": r2(statistics.median(hit)), "shots": d, "n": len(hit), "how": sorted({s.get("how", "") for s in v["shots"]})}
    # ticks a shot takes (lgw_measure.js drawCurve, 2026-11-17): a crossbow's charge, else the fewest ticks of drawing that reach
    # 97% of the fastest shot (the vanilla Bow reads 20, the Trident 10); none for an item thrown on use
    t = v.get("charge") or v.get("full")
    # a weapon used, not drawn (a gun, a throwable): the game's item cooldown after each use (lgw_measure.js, 2026-11-17)
    cds = [s["cd"] for s in v["shots"] if s.get("how") == "use" and s.get("cd")]
    if not t and cds: t = statistics.median(cds)
    if t: o["rng"]["t"] = t
    h1 = [s.get("dmg", 0) for s in (K1.get(k) or {}).get("shots", []) if s.get("dmg", 0) > 0]
    if h1:
        m1 = r2(statistics.median(h1))
        # a share of the target's health shows as every 10,000-health shot above every 1,000-health one, by half again; a random
        # arrow crit moves a shot by a few points either way (Dreadbow 12 and 9)
        if min(hit) > max(h1) and o["rng"]["hit"] > 1.5 * m1: o["rng"]["h10k"] = o["rng"]["hit"]
        o["rng"]["hit"] = m1; o["rng"]["shots"] = [s.get("dmg", 0) for s in K1[k]["shots"]]
    fire = [s["fire"] for s in v["shots"] if s.get("fire", -1) > 0]
    if fire: o["rng"]["fire"] = r2(max(fire) / 20)
    tf = {}
    for s in v["shots"]:
        for e, (amp, dur) in (s.get("tfx") or {}).items(): tf[e] = [amp + 1, dur]
    if tf: o["rng"]["tfx"] = [[e, lv, du] for e, (lv, du) in tf.items()]
    nr += 1

# minions (lgw_measure.js minions, 2026-11-17): what a summon weapon's minions dealt to a 1,000-health no-AI zombie in 200 ticks after one
# use, how many came and what they were; items[id].mn = {dmg, n, s (seconds), kinds}
nmn = 0
for k, v in (X.get("minions") or {}).items():
    o = items.setdefault(k, {"ad": 0}); o["mn"] = {"dmg": r2(v.get("dmg", 0)), "n": v.get("n", 0), "s": r2(v.get("ticks", 200) / 20), "kinds": v.get("kinds", {})}; nmn += 1
if nmn: print(nmn, "summon weapons' minions measured")

nk = 0
r3 = lambda v: round(v, 3)
# a run whose blockers all stopped every hit is a fault of the run (2026-11-17: a creative-mode tester takes no damage), not of the
# curios: its block rates are left out
B = X.get("blocks") or {}
if B and all(sum(1 for h in hs if h is not None and h <= 0.4) == len([h for h in hs if h is not None]) for hs in B.values()):
    print("blocks left out: every blocker stopped every hit"); B = {}
for k, hits in B.items():
    hs = [h for h in hits if h is not None]
    c = curios.get(k)
    if not hs or c is None: continue
    b = sum(1 for h in hs if h <= 0.4)
    if b or "melee" in (c.get("neg") or []):
        c["blk"] = {"n": len(hs), "blocked": b, "tk": r3(sum(h if h > 0.4 else 0.13 * 8 for h in hs) / len(hs) / 8)}; nk += 1
    else:
        tk = r3(sum(hs) / len(hs) / 8); t = c.setdefault("tk", {})
        if abs(tk - 1) > 0.01: t["melee"] = tk
        else: t.pop("melee", None)
        if not t: del c["tk"]

GM["_third"] = "ranged and blocks: lgw_measure_third (" + X.get("started", "") + "), pack_audit/measure/import_third.py"
if nk: CM["_third"] = GM["_third"]   # the curios' block rates came from this run only if it gave any
(H / "gear_measure.json").write_text(json.dumps(GM, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
(H / "curio_measure.json").write_text(json.dumps(CM, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(nr, "ranged measured,", nm, "every shot missed |", nk, "curios with a block rate")
