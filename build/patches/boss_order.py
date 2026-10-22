#!/usr/bin/env python3
"""Order side bosses by the quest book's Bosses chapter (boss_graph.json: who each quest depends on, its
dimension), then push every boss drop to at least its boss's Act. Writes boss_acts.json (read by wiki_data
as BACT), raises curio Acts in data.js and gear Acts in gear_data.js. Idempotent.

Rules: a boss is never before its dimension (Nether V, End 6.3 after the Dragon) nor before the bosses its
quest depends on; the quest chain's depth spreads it over Acts II-X; it is pulled down to the earliest boss
that depends on it first, then the dependency rule wins. Wither, Warden (main line) and Apollyon are fixed."""
import json, pathlib, re
H = pathlib.Path(__file__).resolve().parent; S = H.parent / "src"
ORDER = [0, 2, 3, 4, 5, 6, 6.3, 7, 8, 9, 10, 11, 12]
G = json.loads((H / "boss_graph.json").read_text()); dep, dim = G["dep"], G["dim"]
app = (S / "app.js").read_text(encoding="utf-8"); i = app.index("const BOSSR=") + 12
BOSSR, _ = json.JSONDecoder().raw_decode(app, i)
EXTRA = json.loads((H / "boss_extra.json").read_text())
A = {r[0]: r[1] for r in BOSSR}; A.update({x[0]: x[1] for x in EXTRA}); A["Warden"] = 6
FIX = {"Wither", "Warden", "Apollyon"}
kids = {}
for n, ps in dep.items():
    for p in ps: kids.setdefault(p, []).append(n)
D = {}
def depth(n):
    if n not in D: D[n] = 1 + max(depth(p) for p in dep[n]) if dep[n] else 0
    return D[n]
def base(n):
    v = 2 + depth(n) * 8 / 17
    return max(a for a in ORDER if a <= v and a != 6.3)
def lo(n): return max([dim.get(n, 0), base(n)] + [A.get(p, 0) for p in dep[n]])
for _ in range(40):
    ch = 0
    for n in dep:
        if n in FIX or n not in A or n not in kids: continue
        v = max(min(A.get(k, 99) for k in kids[n]), dim.get(n, 0))
        if A[n] > v: A[n] = v; ch += 1
    if not ch: break
for _ in range(40):
    ch = 0
    for n in dep:
        if n in FIX or n not in A: continue
        l = lo(n)
        if A[n] < l: A[n] = l; ch += 1
    if not ch: break
bad = [(p, n) for n in dep for p in dep[n] if n in A and p in A and A[p] > A[n]]
assert not bad, bad
(H / "boss_acts.json").write_text(json.dumps(A, ensure_ascii=False, indent=0))

# Boss entity -> Act, for loot tables; names as curio sources word them -> Act.
SB = json.loads((H / "side_bosses.json").read_text())
ENT = {}
for n, b in SB.items():
    for e in ([b["entity"]] if isinstance(b.get("entity"), str) else b.get("entity") or []):
        if n in A: ENT[e] = A[n]
for x in EXTRA:
    if x[0] in A: ENT[x[6]] = A[x[0]]
# bosses no longer listed still gate their drops (old Acts)
ENT.update({"terramity:gob": 7, "terramity:virtue": 9, "terramity:super_sniffer": 6, "terramity:ultra_sniffer": 9,
            "terramity:sorceress_circe": A.get("Gundalf, Circe, Merlin (Shadow Wizards)", 6.3),
            "terramity:enchanter_merlin": A.get("Gundalf, Circe, Merlin (Shadow Wizards)", 6.3),
            "mowziesmobs:naga": 4, "block_factorys_bosses:yeti": 3, "block_factorys_bosses:infernal_dragon": 6,
            "eeeabsmobs:nameless_guardian": 7, "goety:vizier": 5, "undergarden:forgotten_guardian": 6})
# How curio sources name a boss ("Dropped by The Dead King") -> its Act
NAME = {n.split(" (")[0].split(" →")[0].split(",")[0]: a for n, a in A.items() if n in dep and n not in FIX}
NAME.update({"The Dead King": A["Dead King"], "Enraged Dead King": A["Dead King"], "Archmage Gundalf": A["Gundalf, Circe, Merlin (Shadow Wizards)"],
             "Dark Doppelganger": A["Dark Doppelganger"]})
oi = lambda a: ORDER.index(a) if a in ORDER else 0

# Gear: a loot table entities/<boss> sets the floor.
P = S / "gear_data.js"; s = P.read_text(encoding="utf-8"); j = s.index("["); GE, e = json.JSONDecoder().raw_decode(s, j)
ng = 0
for g in GE:
    fl = [ENT[m.group(1) + ":" + m.group(2)] for l in g.get("lt") or [] for m in [re.match(r"^([a-z0-9_]+):entities/(.+)$", l)] if m and m.group(1) + ":" + m.group(2) in ENT]
    if fl and oi(max(fl, key=oi)) > oi(g["a"]):
        g["a"] = max(fl, key=oi); g["ga"] = max(g.get("ga") or 0, g["a"]); ng += 1
# Items only bosses drop (no live recipe, no chest/block loot: boss_only_items.json from the pack's recipes and
# loot tables) carry that boss's Act into gear recipes that use them.
ONLY = json.loads((H / "boss_only_items.json").read_text()); DROP = {}
def drop(it, a):
    if it not in ONLY or "treasure_pouch" in it: return
    DROP[it] = min(DROP.get(it, a), a, key=oi)
for r in BOSSR:
    if r[0] in A and r[0] in dep:
        for it in r[4] or []: drop(it, A[r[0]])
for n, b in SB.items():
    if n in A and n in dep:
        for x in b.get("drops") or []: drop(x["id"], A[n])
for x in EXTRA:
    if x[0] in A:
        for it in x[4]: drop(it, A[x[0]])
GA = {g["id"]: g["a"] for g in GE}
for _ in range(4):
    for g in GE:
        ins = [y for rc in g.get("rc") or [] for y in rc.get("i", [])[1:] if isinstance(y, str)]
        fl = [DROP[y] for y in ins if y in DROP] + [GA[y] for y in ins if y in GA and y != g["id"]]
        if fl and g.get("rc") and len(g["rc"]) == 1 and not g.get("lt"):
            m = max(fl, key=oi)
            if oi(m) > oi(g["a"]): g["a"] = GA[g["id"]] = m; g["ga"] = max(g.get("ga") or 0, m); ng += 1
# a set's Act is its latest piece
k = s.index("GS=", e) + 3; GS, e2 = json.JSONDecoder().raw_decode(s, k)
for t in GS:
    m = max([GA.get(x, 0) for x in t["p"]] + [t["a"]], key=oi)
    if oi(m) > oi(t["a"]): t["a"] = m
s = s[:k] + json.dumps(GS, separators=(",", ":"), ensure_ascii=False) + s[e2:]
P.write_text(s[:j] + json.dumps(GE, separators=(",", ":"), ensure_ascii=False) + s[e:], encoding="utf-8")

# Curios: "(bag|drop: <boss>)" / "dropped by <boss>" in the source line.
P = S / "data.js"; s = P.read_text(encoding="utf-8"); Dd, e = json.JSONDecoder().raw_decode(s, 8)
nc = 0
for d in Dd:
    txt = d.get("src0", "")
    hit = [(k, a) for k, a in NAME.items() if re.match(r"(?:The )?" + re.escape(k) + r"(?: Additions New)? drop\b", txt)]
    if not hit: continue
    a = max((a for _, a in hit), key=oi)
    # a pure boss drop sits at its boss's Act (raised or lowered), but never under its keeper gate
    if "Also" not in txt and " or " not in txt: a = max(a, d.get("gk") or 0, key=oi)
    elif oi(a) <= oi(d["t"]): continue
    if a != d["t"]:
        d["t"] = d["a"] = a; nc += 1
        why = "Boss drop: sits at its boss's Act in the quest-book order"
        d["why"] = [w for w in d.get("why", []) if not w.startswith(("Random loot", "Earliest at Act", "Boss drop:"))] + [why]
P.write_text("const D=" + json.dumps(Dd, ensure_ascii=False, separators=(",", ":")) + s[e:], encoding="utf-8")
print("boss_order:", len(A), "bosses;", ng, "gear and", nc, "curios raised to their boss's Act")
