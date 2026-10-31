"""Stage 4 (runs after gear_added, before gear_runtime). Apply the equipment audit (build/pack_audit/eqa) and the pack-reading fixes
in gear_fix.json:
  act      raise an Act (g.a) to the recipe-ingredient gate; the lock g.ga is gear_runtime's alone (the pack's gate tags)
  note     a source note (g.ob): '!' not obtainable in survival (hidden from the lists), '?' unverified
  drop_rc  recipes the pack never loads: forge:false stubs, variants whose conditions fail, recipes needing an absent mod.
           "all" drops every recipe of the item, else a list of ingredient lists (rc.i) to drop
  merge    armor families the scan's setkey() split into several sets (Geomancer beads/robe/belt/sandals, MekaSuit and its
           bodyarmor, Create's diving helmet/backtank/boots...): one set per family, scored on all its pieces in gear_runtime"""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent
F = json.loads((H / "gear_fix.json").read_text())
# Audit v22.3: ctor speed 0.0 was read as 4.0; use the real or sword-default speed (gear.js scores from it).
SPD = {"alexsmobs:tendon_whip": 1.0, "lethality:hf_meowrasama": 1.6, "macabre:blood_cloth_dagger": 1.6,
       "macabre:plasma_dagger": 1.6, "lethality:pickle_paddle": 1.6}
SLOTS = ["HELMET", "CHESTPLATE", "LEGGINGS", "BOOTS"]
# set keys made by a merge: the in-game measurement of the same key was taken on one piece, so gear_measure skips them
MERGED = set(F["merge"])

def merge(st):
    by = {g["id"]: g for g in st["GE"]}
    keys = [s["k"] for s in st["GS"]]
    assert len(keys) == len(set(keys)), "GS keys not unique"
    GS = {s["k"]: s for s in st["GS"]}
    gone = set()
    for k, m in F["merge"].items():
        src = [GS.get(x) for x in m["from"]]
        assert all(src), ("merge source set missing", k, [x for x, s in zip(m["from"], src) if not s])
        ps = sorted({i for s in src for i in s["p"]}, key=lambda i: SLOTS.index(by[i]["sl"]))
        sl = [by[i]["sl"] for i in ps]
        assert len(sl) == len(set(sl)), ("merged pieces share a slot", k, ps)
        assert len({i.split(":")[0] for i in ps} | {k.split(":")[0]}) == 1, ("merge across namespaces", k)
        # one family: the pieces share their item class, or (Create's backtank and diving helmet, Ad Astra's suit and helmet,
        # Mekanism's scuba tank and mask) a mod class above it; never only ArmorItem
        com = set.intersection(*[set(by[i].get("cls") or []) for i in ps]) - {"ArmorItem", "Item", "DyeableArmorItem"}
        assert com, ("merged pieces share no mod class", k, [by[i].get("cls") for i in ps])
        new = dict(src[0], k=k, n=m["n"], p=ps, a=max(s["a"] for s in src), kn=all(s.get("kn") for s in src))
        new.pop("ms", None)
        gone.update(m["from"])
        GS[k] = new
    st["GS"] = [s for s in st["GS"] if s["k"] not in gone] + [GS[k] for k in F["merge"]]

def apply(st):
    merge(st)
    for g in st["GE"]:
        a = F["act"].get(g["id"])
        if a and a > g["a"]: g["a"] = a
        if g["id"] in F["note"]: g["ob"] = F["note"][g["id"]]
        d = F["drop_rc"].get(g["id"])
        if d == "all": g["rc"] = []
        elif d: g["rc"] = [r for r in g.get("rc", []) if r["i"] not in d]
        v = SPD.get(g["id"])
        if v and g.get("spd") == 4.0: g["spd"] = v
    have = {g["id"] for g in st["GE"]}
    miss = [i for i in F["drop_rc"] if i not in have]
    assert not miss, ("gear_fix.json drop_rc names gear the table does not have", miss)
    # A set's Act is its latest piece.
    A = {g["id"]: g["a"] for g in st["GE"]}
    for t in st["GS"]:
        m = max([A.get(x, 0) for x in t["p"]] + [t["a"]])
        if m > t["a"]: t["a"] = m
