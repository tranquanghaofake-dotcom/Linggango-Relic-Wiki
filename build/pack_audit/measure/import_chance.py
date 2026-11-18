"""Curios sampled in game (lgw_measure_chance, kubejs/lgw_chance_measure.json) -> build/patches/curio_chance.json.
Usage: python3 pack_audit/measure/import_chance.py lgw_chance_measure.json [lgw_chance_luck_measure.json]

A curio whose effect is a chance (a dice, a coin, a proc on a hit) cannot be read from the two swings of lgw_measure_extra, so
lgw_measure.js (section 3b) samples it: worn, N diamond-sword swings at fresh pigs and M hits of 4 damage of each kind through the damage
events, with the tester's Luck at 0. The mean over N against the bare tester's mean is the expected value the wiki scores.

Per curio:
  hs   the mean damage of a swing with it worn over the bare tester's mean (omitted within 1%)
  tk   the mean damage taken of a 4 hit by kind over the bare tester's 4 (omitted within 1%); a curio that cancels some hits reads below 1,
       one that raises them (Fateful Coin) above 1
  o    the outcomes of the swings that came up in at least 3% of them: [damage, share], so the page can say what the chance is
  n, m the swings and the hits taken
  lk   (second file, Luck effect levels): the same hs and tk at each level, [level, hs, {kind: tk}]
4 is the test hit because the pack caps a hit at half the tester's health (10): an 8 hit raised x1.5 reads 10, not 12."""
import json, sys, pathlib
H = pathlib.Path(__file__).resolve().parents[2] / "patches"
X = json.load(open(sys.argv[1], encoding="utf-8"))
C = X["chance"]; B = C["(none)"]["0"]
r3 = lambda v: round(v, 3)
def at(rec):
    b = B
    o = {}
    hs = rec["hit"]["mean"] / b["hit"]["mean"]
    if abs(hs - 1) > 0.01: o["hs"] = r3(hs)
    tk = {}
    for k, v in rec["hurt"].items():
        t = v["mean"] / b["hurt"][k]["mean"] if b["hurt"][k]["mean"] else 1
        if abs(t - 1) > 0.01: tk[k] = r3(t)
    if tk: o["tk"] = tk
    return o
out = {}
for k, v in C.items():
    if k == "(none)" or "0" not in v: continue
    rec = v["0"]; o = at(rec)
    n = rec["hit"]["n"]
    oc = sorted(([float(a), round(c / n, 3)] for a, c in rec["hit"]["hist"].items() if c / n >= 0.03), key=lambda x: -x[1])
    o["o"] = oc; o["n"] = n; o["m"] = rec["hurt"]["melee"]["n"]
    out[k] = o
if len(sys.argv) > 2:
    L = json.load(open(sys.argv[2], encoding="utf-8"))["chance"]
    for k, v in L.items():
        if k == "(none)" or k not in out: continue
        lv = []
        for lvl, rec in v.items():
            if not lvl.startswith("e"): continue
            b2 = L["(none)"][lvl]
            hs = rec["hit"]["mean"] / b2["hit"]["mean"]
            tk = {kk: r3(vv["mean"] / b2["hurt"][kk]["mean"]) for kk, vv in rec["hurt"].items() if b2["hurt"][kk]["mean"] and abs(vv["mean"] / b2["hurt"][kk]["mean"] - 1) > 0.01}
            lv.append([int(lvl[1:]), r3(hs), tk])
        if lv: out[k]["lk"] = sorted(lv)
res = {"_source": "Linggango 6.6.6cf server pack, sampled in game by build/pack_audit/kubejs/server_scripts/lgw_measure.js (lgw_measure_chance, "
       + X.get("started", "") + "); see build/pack_audit/measure/import_chance.py for what each field is.", "ref_hit": B["hit"]["mean"], "curios": out}
(H / "curio_chance.json").write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
n = lambda f: sum(1 for o in out.values() if f(o))
print(len(out), "curios ->", H / "curio_chance.json")
print("damage dealt changed", n(lambda o: "hs" in o), "| damage taken changed", n(lambda o: "tk" in o), "| nothing measurable", n(lambda o: "hs" not in o and "tk" not in o))
