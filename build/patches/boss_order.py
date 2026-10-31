#!/usr/bin/env python3
"""Order side bosses by the quest book's Bosses chapter (boss_graph.json: who each quest depends on, its
dimension), then push every boss drop to at least its boss's Act. Writes boss_acts.json (read by wiki_data
as BACT), raises curio Acts in data.js (run as a script) and gear Acts (gear(), stage 6 of gear_pipeline.py). Idempotent.

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
            "eeeabsmobs:nameless_guardian": 7, "undergarden:forgotten_guardian": 6})
ENT["born_in_chaos_v1:pumpkinhead"] = A.get("Lord Pumpkinhead", 5)   # the loot table is named without "lord_"
# How curio sources name a boss ("Dropped by The Dead King") -> its Act
NAME = {n.split(" (")[0].split(" →")[0].split(",")[0]: a for n, a in A.items() if n in dep and n not in FIX}
NAME.update({"The Dead King": A["Dead King"], "Enraged Dead King": A["Dead King"], "Archmage Gundalf": A["Gundalf, Circe, Merlin (Shadow Wizards)"]})
oi = lambda a: ORDER.index(a) if a in ORDER else 0
# the Warden (6.1) and Wither (6.2) Acts sit between Act VI and the Dragon Act (ORDER above has no place for them)
ok = lambda a: ORDER.index(6) + round(a - 6, 1) * 3 if a in (6.1, 6.2) else oi(a)

def drop_map():
    """Items only bosses drop (no live recipe, no chest/block loot: boss_only_items.json from the pack's recipes and
    loot tables) -> the earliest Act of a boss that drops them."""
    ONLY = json.loads((H / "boss_only_items.json").read_text()); DROP = {}
    # a vanilla mob's table (Terramity's villager drops the Spiteful Soul) means anyone can get it
    bad = [it for it, ts in ONLY.items() if any(t.startswith("minecraft:entities/") for t in ts)]
    assert not bad, ("boss_only_items.json lists items a vanilla mob drops", bad)
    def drop(it, a):
        if it not in ONLY or "treasure_pouch" in it: return
        DROP[it] = min(DROP.get(it, a), a, key=ok)
    for r in BOSSR:
        if r[0] in A and r[0] in dep:
            for it in r[4] or []: drop(it, A[r[0]])
    for n, b in SB.items():
        if n in A and n in dep:
            for x in b.get("drops") or []: drop(x["id"], A[n])
    for x in EXTRA:
        if x[0] in A:
            for it in x[4]: drop(it, A[x[0]])
    return DROP

def recipe_ins(g):
    """Every ingredient of a gear piece's recipes. Some recipes repeat their type as i[0], most start with an ingredient
    (Dinosaur Bone Club: dinosaur_bone, stick), so drop the type by value, not by position."""
    return [y for rc in g.get("rc") or [] for y in rc.get("i", []) if isinstance(y, str) and y != rc.get("t")]

def gear(st):
    """Stage 6 of the gear pipeline: boss drops sit at their boss's Act."""
    GE, GS = st["GE"], st["GS"]
    # a loot table entities/<boss> sets the floor
    for g in GE:
        fl = [ENT[m.group(1) + ":" + m.group(2)] for l in g.get("lt") or [] for m in [re.match(r"^([a-z0-9_]+):entities/(.+)$", l)] if m and m.group(1) + ":" + m.group(2) in ENT]
        if fl and ok(max(fl, key=ok)) > ok(g["a"]):
            g["a"] = max(fl, key=ok); g["ga"] = max(g.get("ga") or 0, g["a"], key=ok)
    # boss-only items carry that boss's Act into gear recipes that use them
    DROP = drop_map()
    GA = {g["id"]: g["a"] for g in GE}
    for _ in range(4):
        for g in GE:
            ins = recipe_ins(g)
            fl = [DROP[y] for y in ins if y in DROP] + [GA[y] for y in ins if y in GA and y != g["id"]]
            if fl and g.get("rc") and len(g["rc"]) == 1 and not g.get("lt"):
                m = max(fl, key=ok)
                if ok(m) > ok(g["a"]): g["a"] = GA[g["id"]] = m; g["ga"] = max(g.get("ga") or 0, m, key=ok)
    late = [(g["id"], y) for g in GE if g.get("rc") and len(g["rc"]) == 1 and not g.get("lt")
            for y in recipe_ins(g) if y in DROP and ok(DROP[y]) > ok(g["a"])]
    assert not late, ("gear listed before the boss that drops its ingredient", late[:10])
    # a set's Act is its latest piece
    for t in GS:
        m = max([GA.get(x, 0) for x in t["p"]] + [t["a"]], key=ok)
        if ok(m) > ok(t["a"]): t["a"] = m

def main():
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
    # a crafted curio whose only recipe needs another curio (a specific item, not "any of a tag") cannot come before that
    # curio: Blood Howl Pendant needs the Gold Medal, which only Archmage Gundalf drops. Loot curios keep their Act.
    # A curio whose recipe needs an item only a boss drops (Violet Bloom, only from Rosalyne) sits at that boss's Act.
    by = {d["id"]: d for d in Dd}; nr = nb = 0; DROP = drop_map()
    for _ in range(4):
        for d in Dd:
            if d.get("g") != "Craft" or not d.get("gr"): continue
            cur = [by[c[0]]["t"] for c in d["gr"]["c"] if c and c[0] in by and not c[1] and c[0] != d["id"]]
            bos = [DROP[c[0]] for c in d["gr"]["c"] if c and c[0] in DROP and not c[1]]
            if not cur and not bos: continue
            m = max(cur + bos, key=ok)
            if ok(m) > ok(d["t"]):
                d["t"] = m; d["a"] = max(d["a"], m, key=ok)
                if bos and ok(max(bos, key=ok)) >= ok(m):
                    nb += 1; why = "Needs a boss-only drop: sits at that boss's Act"
                else:
                    nr += 1; why = "Needs a curio from a later Act: sits where its ingredient becomes available"
                d["why"] = [w for w in d.get("why", []) if not w.startswith(("Needs a curio", "Needs a boss-only drop"))] + [why]
    P.write_text("const D=" + json.dumps(Dd, ensure_ascii=False, separators=(",", ":")) + s[e:], encoding="utf-8")
    print("boss_order:", len(A), "bosses;", nc, "curios raised to their boss's Act;", nr, "raised to an ingredient's Act;", nb, "to a boss-only drop's Act")

if __name__ == "__main__":
    main()
