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
    # a shot with "sus" is not one shot: the weapon used again every tick for 40 ticks (lgw_measure.js, 2026-11-17: a gun with no item
    # cooldown), its dmg what the target lost all told
    d = [s.get("dmg", 0) for s in v.get("shots", []) if not s.get("sus")]
    sus = [s for s in v.get("shots", []) if s.get("sus") and s.get("dmg", 0) > 0]
    if not d: continue
    o = items.setdefault(k, {"ad": r2(v.get("ad", 0))})
    hit = [x for x in d if x > 0]
    dc = {int(a): b for a, b in (v.get("dcurve") or [])}
    # every 40-tick draw missed but a hold in world time landed (a beam held in one server tick lands once or not at all)
    if not hit and dc and max(dc.values()) > 0: hit = [max(dc.values())]
    if not hit: o["rng"] = {"miss": 1, "shots": d}; nm += 1; continue
    o["rng"] = {"hit": r2(statistics.median(hit)), "shots": d, "n": len(hit), "how": sorted({s.get("how", "") for s in v["shots"]})}
    # ticks a shot takes (lgw_measure.js drawCurve, 2026-11-17): a crossbow's charge, else the fewest ticks of drawing that reach
    # 97% of the fastest shot (the vanilla Bow reads 20, the Trident 10); none for an item thrown on use
    t = v.get("charge") or v.get("full")
    # a weapon used, not drawn (a gun, a throwable): the game's item cooldown after each use (lgw_measure.js, 2026-11-17)
    # a Brutality throwable ("throw"): its cooldown after the swing, 20 / attack speed ticks
    cds = [s["cd"] for s in v["shots"] if s.get("how") in ("use", "throw") and s.get("cd")]
    if not t and cds: t = statistics.median(cds)
    # no cooldown and used again every tick: its rate is what 40 ticks of use dealt (t = the ticks one median shot is worth)
    if not t and sus: t = r2(40 * o["rng"]["hit"] / sus[0]["dmg"]); o["rng"]["sus"] = sus[0]["dmg"]
    # drawn, its shot unseen by the speed curve (a beam, a projectile that is not an arrow): held 10, 20, 40, 60 ticks of world time
    # (v.dcurve). Still rising from 40 to 60 by a quarter: a beam, its rate the damage from 20 to 60 ticks over those 40 ticks; else
    # the fewest ticks that reach 97% of the most (a bow's full draw)
    # a held trigger that fires on (a gatling) is a beam too, whatever its speed curve said
    if dc and max(dc.values()) > 0:
        o["rng"]["dcurve"] = [[a, dc[a]] for a in sorted(dc)]
        # rising all the way, by half again from 20 to 40 ticks and by a third from 40 to 60: one sample a hold, and a bow's random
        # arrow crit moves a sample by up to half (fourth run: the vanilla Bow 3, 7, 8, 12, a full draw at 20 ticks)
        if dc.get(20, 0) > 0 and dc.get(40, 0) >= 1.5 * dc[20] and dc.get(60, 0) >= 1.3 * dc[40]:
            t = r2(40 * o["rng"]["hit"] / (dc[60] - dc.get(20, 0))); o["rng"]["beam"] = 1
        elif not t: t = min(a for a in sorted(dc) if dc[a] >= .97 * max(dc.values()))
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

# minions (lgw_measure.js minions, 2026-11-17): a summon weapon used once next to a 100,000-health no-AI zombie on the floor, the
# zombie's lost health read every 10 ticks for 300 (v.hp, cumulative). The rate is taken from the first reading with damage on to the
# last, so the minions' walk to the zombie is not counted: items[id].mn = {dmg, s (seconds of that window), n (minions that came),
# first (ticks to the first damage), kinds}. A weapon whose minions dealt nothing in 300 ticks (no minion came, or it does not attack:
# a focus staff, a whip, a support summon) keeps dmg 0, and the page lists it unranked. An older run's record (one reading, "dmg" in
# 200 ticks) is read as one window of 200 ticks.
nmn = 0
for k, v in (X.get("minions") or {}).items():
    hp = v.get("hp") or []
    seen = (v.get("seen") or {})
    kinds = {}
    for when in ("t10", "t100", "t0"):
        if seen.get(when): kinds = {t.split(" ")[0]: c for t, c in seen[when].items() if "experience_orb" not in t and "minecraft:item" not in t}; break
    if len(hp) >= 3:
        i = next((j for j, h in enumerate(hp) if h > 0), None)
        dmg, s, first = (r2(hp[-1] - hp[i]), r2((len(hp) - 1 - i) * 10 / 20), (i + 1) * 10) if i is not None and i < len(hp) - 1 else (0, 0, None)
    else:
        dmg, s, first = r2(v.get("dmg", 0)), r2(v.get("ticks", 200) / 20), None
    o = items.setdefault(k, {"ad": 0}); o["mn"] = {"dmg": dmg, "n": v.get("n", 0), "s": s, "kinds": kinds}
    if first: o["mn"]["first"] = first
    nmn += 1
if nmn: print(nmn, "summon weapons' minions measured,", sum(1 for k in (X.get("minions") or {}) if items[k]["mn"]["dmg"] > 0), "dealt damage")

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
