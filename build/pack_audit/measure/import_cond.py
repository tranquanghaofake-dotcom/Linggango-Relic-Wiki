"""Curios sampled in game in conditions (lgw_measure_cond, kubejs/lgw_cond_measure.json) -> build/patches/curio_cond.json.
Usage: python3 pack_audit/measure/import_cond.py lgw_cond_measure.json [more batches of the same run…]
Every file has its own bare-tester baseline ("(none)"), so batches run on separate servers (one run of 330 curios ran out of Java heap) are read each against its own.

Each curio (and the bare tester, "(none)") is worn in each state of lgw_measure.js section 3c (low health, night, burning, sprinting, an undead target,
a burning target, a target at a fifth of its health): N swings and M hits of 4 damage of each kind through the damage events. A curio's effect in a state is
its mean over the bare tester's in the same state. Per curio:
  cd   [[state, hs, {kind: tk}], ...] for the states where damage dealt (hs) or taken (tk) differs from the bare tester's by more than 5%
  hs, tk   the effect counted for scoring: each state's change times the share of the time a player is in it (patches/effect_uptime.json "states", an
           assumption)
  dfk  the effects ("hs" damage dealt, "tk:<kind>" damage taken of a kind) that show in five or more of the seven states: the tester meets its condition by default (it stands still, hits again and again so a stack
       builds, swings at half health, at a full-health target) and the number says nothing of a real fight (Rage Glove x4.7, Stillness Scarf x1.5, Berserk
       Charm x2): it is shown, not counted, the way gear.js GCTX keeps such curios out of the tiers
       The states overlap (a player can be at night and sprinting), so the sum of the shares is capped at the largest single state's change.
The size is measured; the share is not."""
import json, sys, pathlib, statistics
H = pathlib.Path(__file__).resolve().parents[2] / "patches"
XS = [json.load(open(f, encoding="utf-8")) for f in sys.argv[1:]]; X = XS[0]
SH = {k: v["share"] for k, v in json.load(open(H / "effect_uptime.json"))["states"].items()}
r3 = lambda v: round(v, 3); TH = 0.05
out = {}; NS = 0
for X1 in XS:
  C = X1["cond"]; B = C["(none)"]
  for k, v in C.items():
    if k == "(none)": continue
    NS += 1
    cd = []; hs_all = {}; tk_all = {}
    for st, rec in v.items():
        b = B[st]; hs = rec["hit"]["mean"] / b["hit"]["mean"] if b["hit"]["mean"] else 1
        tk = {kind: x["mean"] / b["hurt"][kind]["mean"] for kind, x in rec["hurt"].items() if b["hurt"][kind]["mean"]}
        tkc = {kind: r3(t) for kind, t in tk.items() if abs(t - 1) > TH}
        if abs(hs - 1) > TH or tkc: cd.append([st, r3(hs) if abs(hs - 1) > TH else 1, tkc])
        hs_all[st] = hs; tk_all[st] = tk
    if not cd: continue
    o = {"cd": cd}
    # damage dealt: always on (five or more states) at the median, else each state at its share
    ch = [s for s in v if abs(hs_all[s] - 1) > TH]
    if ch:
        if len(ch) >= 5: o.setdefault("dfk", []).append("hs")
        else:
            top = max((hs_all[s] - 1 for s in ch), key=abs); tot = sum((hs_all[s] - 1) * SH.get(s, 0) for s in ch)
            o["hs"] = r3(1 + (min(tot, top) if top > 0 else max(tot, top)))
    kinds = {kind for s in v for kind, t in tk_all[s].items() if abs(t - 1) > TH}
    tk = {}
    for kind in kinds:
        ch = [s for s in v if abs(tk_all[s].get(kind, 1) - 1) > TH]
        if len(ch) >= 5:
            o.setdefault("dfk", []).append("tk:" + kind)
            continue
        top = max((tk_all[s][kind] - 1 for s in ch), key=abs); tot = sum((tk_all[s][kind] - 1) * SH.get(s, 0) for s in ch)
        tk[kind] = r3(1 + (min(tot, top) if top > 0 else max(tot, top)))
    tk = {a: b2 for a, b2 in tk.items() if abs(b2 - 1) > 0.005}
    if tk: o["tk"] = tk
    if abs(o.get("hs", 1) - 1) < 0.005: o.pop("hs", None)
    out[k] = o
res = {"_source": "Linggango 6.6.6cf server pack, sampled in game by build/pack_audit/kubejs/server_scripts/lgw_measure.js (lgw_measure_cond, " + X.get("started", "") + "); see build/pack_audit/measure/import_cond.py for what each field is.", "curios": out}
(H / "curio_cond.json").write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(len(out), "curios ->", H / "curio_cond.json")
print("shown but not counted (the test meets the condition by default)", sum(1 for o in out.values() if o.get("dfk")), "|", end=" ")
print("damage dealt counted", sum(1 for o in out.values() if "hs" in o), "| damage taken counted", sum(1 for o in out.values() if "tk" in o), "of", NS, "sampled")
