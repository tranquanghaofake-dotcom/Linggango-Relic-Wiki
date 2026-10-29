"""The third run (lgw_measure_third, kubejs/lgw_third_measure.json) -> adds to build/patches/gear_measure.json and curio_measure.json.
Usage: python3 pack_audit/measure/import_third.py lgw_third_measure.json   (after import.py and import_curios.py)

  ranged  each bow, crossbow and throwable shot three times at a 10,000-health pig 5 blocks in front of the tester, arrows in the
          off hand, a bow drawn 40 ticks: per item {hit: median shot, shots, how} into gear_measure.json items[id].rng. A shot that
          missed or never left reads 0: an item with every shot 0 is kept as {miss: 1} (the page says it was not measured)
  grows   the 12 "grows" weapons again, with the pig turned so "behind" really is behind: a weapon whose swing from behind is over
          1.3x the swing from the front gets {front, behind} into items[id].back, and its hit is the front swing
  blocks  each curio that cancelled a test hit (Ace of Iron, Opal Necklace...) worn alone and hit with 8 melee damage ten times, a
          second or two apart: {n, blocked} into curio_measure.json curios[id].blk; the share of hits it stopped is its block rate
          at that pace"""
import json, sys, pathlib, statistics
H = pathlib.Path(__file__).resolve().parents[2] / "patches"
X = json.load(open(sys.argv[1], encoding="utf-8"))
r2 = lambda v: round(v, 2)
GM = json.loads((H / "gear_measure.json").read_text(encoding="utf-8"))
CM = json.loads((H / "curio_measure.json").read_text(encoding="utf-8"))
items, curios = GM["items"], CM["curios"]

nr = nm = 0
for k, v in (X.get("ranged") or {}).items():
    d = [s.get("dmg", 0) for s in v.get("shots", [])]
    if not d: continue
    o = items.setdefault(k, {"ad": r2(v.get("ad", 0))})
    hit = [x for x in d if x > 0]
    if not hit: o["rng"] = {"miss": 1, "shots": d}; nm += 1; continue
    o["rng"] = {"hit": r2(statistics.median(hit)), "shots": d, "n": len(hit), "how": sorted({s.get("how", "") for s in v["shots"]})}
    fire = [s["fire"] for s in v["shots"] if s.get("fire", -1) > 0]
    if fire: o["rng"]["fire"] = r2(max(fire) / 20)
    tf = {}
    for s in v["shots"]:
        for e, (amp, dur) in (s.get("tfx") or {}).items(): tf[e] = [amp + 1, dur]
    if tf: o["rng"]["tfx"] = [[e, lv, du] for e, (lv, du) in tf.items()]
    nr += 1

nb = 0
for k, g in (X.get("grows") or {}).items():
    o = items.get(k)
    if not o: continue
    fr, bh = (g.get("front") or [0])[0], (g.get("behind") or [0])[0]
    if fr > 0 and bh > 1.3 * fr:
        o["back"] = {"front": r2(fr), "behind": r2(bh)}; o["hit"] = r2(fr); o.pop("swx", None); nb += 1

nk = 0
for k, hits in (X.get("blocks") or {}).items():
    hs = [h for h in hits if h is not None]
    if not hs or k not in curios: continue
    curios[k]["blk"] = {"n": len(hs), "blocked": sum(1 for h in hs if h <= 0.4)}; nk += 1

GM["_third"] = "ranged, behind and blocks: lgw_measure_third (" + X.get("started", "") + "), pack_audit/measure/import_third.py"
CM["_third"] = GM["_third"]
(H / "gear_measure.json").write_text(json.dumps(GM, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
(H / "curio_measure.json").write_text(json.dumps(CM, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(nr, "ranged measured,", nm, "every shot missed |", nb, "hit harder from behind |", nk, "curios with a block rate")
