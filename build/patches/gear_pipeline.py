#!/usr/bin/env python3
"""Write build/src/gear_data.js. The whole gear table is built in memory and written once, like wiki_data.js; nothing reads the
generated file back. Stages run in the order below, each is a function on {GE, GS, GNS, IC}:
  1 gear_rebuild.load   gear_table.json (extraction), gear_names.json (mod names), gear_icons.json (icons)
  2 gear_extra          weapons the extraction skips (gear_extra.json)
  3 gear_gate           Acts raised by modded ingredients the pack unlocks late (gear_gate.json)
  4 gear_fix            audit fixes: gated Acts, source notes, attack speeds (gear_fix.json)
  5 gear_stats          attributes the extraction could not read: Summonity / Hazen / Iron's armor, Mowzie tools, trick pairs
  5b gear_added       weapons and armor only the 6.6.6hf in-game dump has (gear_new.json, pack_audit/gear_new.py)
  6 gear_runtime        attribute modifiers read in game (the pack's own kubejs dump_gear) replace the jar reading where present
  7 boss_order.gear     boss drops sit at their boss's Act
  8 gear_fx             what an item does on hit, while worn or held, on use (gear_fx.json, pack_audit/gear_fx.py: the mod's bytecode
                        and tooltip lines); a set carries the effects its pieces give while worn. Scoring reads them in src/gear.js
 8b gear_measure        measured in game (gear_measure.json, pack_audit/measure/import.py from kubejs/lgw_measure.js): a weapon's hit and
                        what its hits put on the target or the attacker replace the code reading of the same effects; a set's
                        worn effects replace its pieces' guesses, its set bonus is added, and the damage it lets through is kept
  9 drop_curios         items the curio list (data.js) already has and the gear reading found no stats for: Goety's robes
                        and crowns are Curios items (common/items/curios), not armor, so they left 0-armor rows and empty sets
  then every Act is snapped onto the wiki's Acts
Scoring is not here: src/gear.js ranks from the facts these stages leave."""
import json, pathlib, re
import gear_rebuild, gear_extra, gear_gate, gear_fix, gear_stats, gear_added, gear_runtime, boss_order
H = pathlib.Path(__file__).resolve().parent
st = gear_rebuild.load()
def roman(n):
    out = ""
    for v, s in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v: out += s; n -= v
    return out
def fx_doubt(fx, tip):
    """gear_fx.py took an effect's duration and level from whichever constants stood before the call, so a duration read
    from a field or config came out as 1-8 ticks and a level as 21 (Frostmourne's Strength XXI for 3 ticks). A level over
    10 or a duration under half a second stands only when the item's own tooltip says it (Brutality writes "Pulverized XXV
    for 3 ticks"; the code's level is that or one more); otherwise the number is dropped and the line marked `doubt`
    (shown without it, not scored) until gear_fx.py is re-run with its argument fix. check.js holds the rule."""
    t = " ".join(tip or [])
    for r in fx:
        lv, tk = r.get("level"), r.get("ticks")
        if isinstance(lv, int) and lv > 10 and not any(re.search(r"\b%s\b" % roman(x), t) for x in (lv, lv - 1)):
            r["level"] = None; r["doubt"] = True
        if isinstance(tk, int) and 0 < tk < 10 and not re.search(r"\b%d ticks?\b" % tk, t):
            r["ticks"] = None; r["doubt"] = True
    return fx
def gear_fx(st):
    F = json.loads((H / "gear_fx.json").read_text(encoding="utf-8"))
    by = {}
    for g in st["GE"]:
        f = F.get(g["id"])
        if not f: continue
        if f.get("fx"): g["fx"] = fx_doubt([dict(r) for r in f["fx"]], f.get("tip"))
        if f.get("tip"): g["tip"] = f["tip"]
        by[g["id"]] = g
    for x in st["GS"]:
        fx = [dict(r, src=i) for i in x["p"] for r in (by[i].get("fx", []) if i in by else []) if r.get("when") == "worn"]
        if fx: x["fx"] = fx
MS = json.loads((H / "gear_measure.json").read_text(encoding="utf-8"))
# melee weapons whose swing needs a condition the test player did not meet, read from the item's code
COND = [("enigmaticlegacy:", "Only a bearer of the Ring of the Seven Curses can use it (Enigmatic Legacy's isTheCursedOne)."),
        ("enigmaticaddons:", "Only a bearer of the Ring of the Seven Curses can use it (Enigmatic Legacy's isTheCursedOne)."),
        ("animus:spear_bound", "It has to be activated first (right-click, paid in Blood Magic Life Points).")]
def ename(e):
    return e.split(":")[1].replace("_", " ").title()
def gear_measure(st):
    I, S = MS["items"], MS["sets"]
    for g in st["GE"]:
        m = I.get(g["id"])
        if not m: continue
        n = m["n"]
        g["ms"] = {"hit": m["hit"], "sw": m["swings"], "ad": m.get("ad")}
        # spent after one hit: swung on, it averages its swings (Sharpened Candy Cane: 4, then 1 and 1 at 8 swings a second)
        if m.get("st") == "once": g["ms"]["hit"] = round(sum(m["swings"]) / len(m["swings"]), 2)
        if m.get("pct"): g["ms"]["pct"] = m["pct"]
        if m.get("swx"): g["ms"]["swx"] = m["swx"]
        how = m.get("st")
        # a swing that never lands: by design (the item cancels its own hit), a thrown or shot weapon's melee, or a condition
        if how == "nohit":
            how = "nodmg" if m.get("evc") else ("nomelee" if g.get("k") != "melee" else "cond")
            if how == "cond":
                g["ms"]["why"] = next((w for p, w in COND if g["id"].startswith(p)), "")
        # 1 a swing from a weapon whose full stats hit far harder: the stack in the test was uncharged (Just Dire Things and other
        # energy tools read attack damage 1 until charged), so the measured hit is not its use
        if not how and m["hit"] <= 1 and (g.get("dmg") or 0) > 2: how = "dull"
        if how: g["ms"]["st"] = how
        if m.get("heal"): g["ms"]["heal"] = [m["heal"][0], round(m["heal"][1] / n, 2)]
        rec = []
        for who, key in (("target", "tfx"), ("self", "sfx")):
            for e in m.get(key, []):
                r = {"when": "hit", "who": who, "effect": e["effect"], "name": ename(e["effect"]), "level": e["level"], "ticks": e["ticks"], "ms": 1}
                if e["n"] < n: r["chance"] = round(e["n"] / n, 2)
                rec.append(r)
        if m.get("fire"):
            r = {"when": "hit", "who": "target", "fire": m["fire"][0], "ms": 1}
            if m["fire"][1] < n: r["chance"] = round(m["fire"][1] / n, 2)
            rec.append(r)
        # a code-read on-hit effect the swings did not show: kept if the code gives it a chance, else it needs a condition the
        # test did not meet (night, a charged hit, a mob type) and is listed but not scored
        seen = {(r["who"], r.get("effect"), bool(r.get("fire"))) for r in rec}
        old = []
        for r in g.get("fx", []):
            if r.get("when") == "hit" and (r.get("who"), r.get("effect"), bool(r.get("fire"))) in seen: continue
            if r.get("when") == "hit" and not r.get("chance"): r = dict(r, unseen=1)
            old.append(r)
        if rec or old: g["fx"] = rec + old
    for x in st["GS"]:
        m = S.get(x["k"])
        if not m: continue
        x["ms"] = {"taken": m["taken"]}
        if m.get("evr"): x["ms"]["evr"] = m["evr"]
        # armor, toughness and health worn in game stand for the set where the stats could not be read (they were the Act's
        # median, 12 sets: Iron's gold, Mekanism hazmat, jetpack... have no armor at all)
        if not x.get("kn"):
            x["arm"], x["tough"], x["kbr"] = m["arm"], m["tough"], m["kbr"]
            x["hp"] = round(m["hp"] - 20, 2); x["kn"] = True; x["msk"] = 1
        if m.get("bonus"):
            x["ms"]["bonus"] = m["bonus"]
            b = m["bonus"]; at = x.setdefault("at", {})
            if "armor" in b: x["arm"] = round(x.get("arm", 0) + b["armor"], 2)
            if "armor_toughness" in b: x["tough"] = round(x.get("tough", 0) + b["armor_toughness"], 2)
            for k in ("attack_damage", "attack_speed"):
                if k in b: at[k] = [round((at.get(k) or [0, 0])[0] + b[k], 3), (at.get(k) or [0, 0])[1]]
        # the full set worn for 40 ticks shows which of the pieces' effects really apply; effects the code reading saw but the
        # wearer did not get (conditions: night, low health, water...) stay, the "one of these" guesses go
        fx = [{"when": "worn", "who": "self", "effect": e["effect"], "name": ename(e["effect"]), "level": e["level"], "ticks": e["ticks"], "ms": 1} for e in m.get("fx", [])]
        got = {r["effect"] for r in fx}
        keep = [dict(r, unseen=1) for r in x.get("fx", []) if not r.get("maybe") and r.get("effect") not in got]
        if fx or keep: x["fx"] = fx + keep
        elif "fx" in x: del x["fx"]
def drop_curios(st):
    s = (H.parent / "src" / "data.js").read_text(encoding="utf-8"); D, _ = json.JSONDecoder().raw_decode(s, s.index("["))
    cur = {d["id"] for d in D}
    gone = {g["id"] for g in st["GE"] if g["id"] in cur and not g.get("arm") and not g.get("at") and g.get("dmg") is None}
    st["GE"] = [g for g in st["GE"] if g["id"] not in gone]
    for x in st["GS"]: x["p"] = [i for i in x["p"] if i not in gone]
    st["GS"] = [x for x in st["GS"] if x["p"]]
for stage in (gear_extra.apply, gear_gate.apply, gear_fix.apply, gear_stats.apply, gear_added.apply, gear_runtime.apply, boss_order.gear, gear_fx, gear_measure, drop_curios):
    stage(st)
# the lock is the pack's gate and only that: no stage after gear_runtime may move it
bad = [(g["id"], g.get("ga"), gear_runtime.gate(g["id"])) for g in st["GE"] if g.get("ga") != gear_runtime.gate(g["id"])]
assert not bad, ("g.ga differs from the pack's gate tags", bad[:10])
# the wiki's Acts (app.js ORDER) have no Warden / Wither step: 6.1 and 6.2 sit in Act VI (a stray 6.1 once put a battleaxe at Act 0)
snap = lambda a: max(x for x in boss_order.ORDER if x <= a)
for x in st["GE"] + st["GS"]:
    for f in ("a", "ga"):
        if x.get(f) is not None: x[f] = snap(x[f])
    if x.get("mg"): x["mg"][0] = snap(x["mg"][0])
d = lambda x: json.dumps(x, separators=(",", ":"), ensure_ascii=False)
# an icon shared by several ids (variants, levels, recolours that kept the texture) is written once; the others point to it
first, uniq, alias = {}, {}, []
for k, v in st["IC"].items():
    if v in first: alias.append([k, first[v]])
    else: first[v] = k; uniq[k] = v
out = "const GE=" + d(st["GE"]) + ",GS=" + d(st["GS"]) + ",GNS=" + d(st["GNS"]) + ",GMN=" + d(MS["none_taken"]) + ";\nObject.assign(IC," + d(uniq) + ");"
if alias: out += "for(const [a,b] of " + d(alias) + ")IC[a]=IC[b];"
(H.parent / "src" / "gear_data.js").write_text(out, encoding="utf-8")
print("gear_pipeline: %d gear, %d sets, %d icons" % (len(st["GE"]), len(st["GS"]), len(st["IC"])))
