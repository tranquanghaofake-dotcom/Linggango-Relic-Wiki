#!/usr/bin/env python3
"""Gear the 6.6.6hf in-game dump has and the wiki did not (the extraction table predates it).

Reads gear_runtime.json (the dump), the current gear table and the pack's jars, and writes build/patches/gear_new.json:
  ge       new weapons and armor pieces: id, name (en_us lang), kind, Act, armor slot, recipes, loot tables; the dump's
           modifiers fill their stats later in the pipeline (gear_runtime), exactly as for every other piece
  gs       new armor sets (pieces grouped by their name, as gear_data.py groups them)
  skipped  what was left out, by reason: mining tools (the wiki ranks weapons and armor), pieces with no modifiers at all
           (stats kept in NBT or guns: nothing to rank), heads and utility items in an armor slot with no armor, and ids the
           wiki already shows as a stage or variant of another piece
Also adds their icons to gear_icons.json (item model layers, first frame).

Act: the highest of (1) the dump's Keeper tier tag (#forge:<tier>_tools / _armor), (2) the Acts of the recipe's
ingredients that the wiki already places (gear, curios, tier tags of the dump, gear_gate.json), When neither a tag nor a placed ingredient decides it, the piece sits at Act 0-I
and its page says the Act is unverified.

Usage: python3 build/pack_audit/gear_new.py <pack dir with files/<project>/*.jar>"""
import sys, json, glob, zipfile, io, base64, re, pathlib, collections
from PIL import Image
PK = pathlib.Path(sys.argv[1]); B = pathlib.Path(__file__).resolve().parents[1]; P = B / "patches"; SRC = B / "src"
J = lambda f: json.loads((P / f).read_text(encoding="utf-8"))
RT = J("gear_runtime.json"); R, TAGS = RT["items"], RT.get("tags", {})
gsrc = (SRC / "gear_data.js").read_text(encoding="utf-8"); gsrc = gsrc[:gsrc.index(";\nObject.assign(IC")]
GE = json.loads(re.search(r"const GE=(\[.*?\]),GS=", gsrc, re.S).group(1))
listed = {g["id"] for g in GE}; mentioned = set(re.findall(r'"([a-z0-9_.-]+:[a-z0-9_/.-]+)"', gsrc))
ORDER = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]; oi = ORDER.index
GATE_ACT = {"iron": 2, "golden": 3, "emerald": 4, "diamond": 5, "netherite": 6, "elvenite": 7, "voiderite": 8, "bloody": 10, "helionite": 11}
# where an id already has an Act on the wiki
ACT = {g["id"]: g["a"] for g in GE}
dj = (SRC / "data.js").read_text(encoding="utf-8")
for m in re.finditer(r'\{"id":"([^"]+)".*?"t":(-?[\d.]+)', dj):
    t = float(m.group(2)); ACT.setdefault(m.group(1), int(t) if t >= 0 else 0)
def tag_act(i):
    a = None
    for t in TAGS.get(i, []):
        m = re.match(r"#forge:(\w+?)_(tools|armor)$", t)
        if m and m.group(1) in GATE_ACT:
            x = GATE_ACT[m.group(1)]; a = x if a is None or oi(x) > oi(a) else a
    return a
for i in TAGS:
    a = tag_act(i)
    if a is not None: ACT.setdefault(i, a)
for i, v in J("gear_gate.json").items(): ACT[i] = v[0]
# jars
zips = []
for f in sorted(glob.glob(str(PK / "files" / "*" / "*.jar"))):
    try: z = zipfile.ZipFile(f); zips.append((z, set(z.namelist())))
    except Exception: pass
def rd(p):
    for z, n in zips:
        if p in n: return z.read(p)
lang = {}
for z, n in zips:
    for p in n:
        if re.match(r"assets/[^/]+/lang/en_us\.json$", p):
            try: d = json.loads(z.read(p).decode("utf-8", "replace"))
            except Exception: continue
            for k, v in d.items():
                m = re.match(r"item\.([a-z0-9_.-]+)\.([a-z0-9_/.-]+)$", k)
                if m and isinstance(v, str): lang.setdefault(m.group(1) + ":" + m.group(2), re.sub(r"§.", "", v).strip())
new = [i for i in sorted(R) if i not in mentioned]
# recipes and loot tables that make or drop a new id
want = set(new); RC = collections.defaultdict(list); LT = collections.defaultdict(list)
def ings(o, acc):
    if isinstance(o, dict):
        if "item" in o and isinstance(o["item"], str): acc.append(o["item"])
        elif "tag" in o and isinstance(o["tag"], str): acc.append("#" + o["tag"])
        for k, v in o.items():
            if k not in ("result", "output", "results", "item", "tag"): ings(v, acc)
    elif isinstance(o, list):
        for v in o: ings(v, acc)
def outs(o):
    r = o.get("result") or o.get("output") or o.get("results")
    if isinstance(r, str): return [r]
    if isinstance(r, dict): return [r.get("item") or r.get("id")]
    if isinstance(r, list): return [x.get("item") or x.get("id") for x in r if isinstance(x, dict)]
    return []
for z, n in zips:
    for p in n:
        if not p.endswith(".json"): continue
        if re.match(r"data/[^/]+/recipes/", p):
            try: o = json.loads(z.read(p))
            except Exception: continue
            if not isinstance(o, dict): continue
            if o.get("type") == "forge:conditional":            # Thermal and others wrap their recipes in conditions
                o = next((r.get("recipe") for r in o.get("recipes", []) if isinstance(r, dict) and isinstance(r.get("recipe"), dict)), {})
            for out in outs(o):
                if out in want:
                    acc = []; ings(o.get("key") or o.get("ingredients") or o.get("base") or o, acc)
                    for extra in ("addition", "input", "center"):
                        if o.get(extra) and o.get(extra) is not (o.get("key") or o.get("ingredients") or o.get("base")): ings(o[extra], acc)
                    if o.get("template"): ings(o["template"], acc)
                    RC[out].append({"t": o.get("type", "?"), "i": [o.get("type", "?")] + [x for x in acc if x != out]})
        elif re.match(r"data/[^/]+/loot_tables/", p):
            b = z.read(p).decode("utf-8", "replace")
            for i in want & set(re.findall(r'"name"\s*:\s*"([a-z0-9_.-]+:[a-z0-9_/.-]+)"', b)):
                ns = p.split("/")[1]; LT[i].append(ns + ":" + p.split("/loot_tables/")[1][:-5])
TOOL = re.compile(r"(pickaxe|shovel|_hoe$|hoe_|paxel|excavator|_drill|disassembler|meka_tool|_aiot|_shears)")
ARMOR_W = re.compile(r"(helmet|chestplate|leggings|boots|helm|cap|hood|robe|pants|tunic|greaves|crown|mask|hat)$")
SLOT = {"head": "HELMET", "chest": "CHESTPLATE", "legs": "LEGGINGS", "feet": "BOOTS"}
def kind(i, mods):
    names = {m[0].split(":")[-1] for m in mods}
    if any("spell_power" in x or x in ("max_mana", "mana_regen", "cast_time_reduction") for x in names) and not any(x == "attack_damage" for x in names): return "magic"
    if re.search(r"(bow|crossbow|gun|blaster|launcher|cannon|rifle|pistol|revolver|magnum|knives|dynamite|grenade|bomb)", i): return "ranged"
    if i.startswith("brutality:"): return "ranged"   # Brutality's new held items are its throwables (balls, cubes, bottles, cards)
    if any(x in ("summon_damage", "minion_slots") for x in names): return "summon"
    if re.search(r"(staff|wand|scepter|sceptre|tome|grimoire|orb)", i): return "magic"
    return "melee"
ge, skipped = [], collections.defaultdict(list)
for i in new:
    slots = R[i]; nm = lang.get(i) or i.split(":")[1].replace("_", " ").title()
    allm = [m for s in slots.values() for m in s]
    if TOOL.search(i): skipped["mining tool"].append(i); continue
    if not any(m[1] for m in allm): skipped["no modifiers (stats in NBT, or none)"].append(i); continue
    arm = [s for s in slots if s in SLOT]
    if arm and "mainhand" not in slots:
        if not any(m[0].endswith("armor") and m[1] for m in slots[arm[0]]): skipped["armor slot, no armor (head or utility item)"].append(i); continue
        k, sl, mods = "armor", SLOT[arm[0]], slots[arm[0]]
    elif "mainhand" in slots:
        mods = slots["mainhand"]
        if not any(m[0].endswith("attack_damage") for m in mods) and kind(i, mods) == "melee": skipped["held item with no attack damage"].append(i); continue
        k, sl = kind(i, mods), None
    else: skipped["other slot"].append(i); continue
    a, why = tag_act(i), "tier tag"
    for r in RC.get(i, []):
        for x in r["i"][1:]:
            xa = ACT.get(x.lstrip("#"))
            if xa is not None and (a is None or oi(xa) > oi(a)): a, why = xa, "recipe"
    g = {"id": i, "n": nm, "ns": i.split(":")[0], "k": k, "a": a if a is not None else 0, "ga": a if a is not None else 0, "at": {}, "src": [],
         "rc": RC.get(i, [])[:3], "lt": LT.get(i, [])[:4], "cls": [], "off": {}, "dump": 1}
    if sl: g["sl"] = sl
    if a is None: g["ob"] = "?Added from the 6.6.6hf in-game dump; its Act could not be read from a tier tag or a recipe, so it sits at the start."
    ge.append(g)
# a piece made from another new piece is at least that piece's Act (Mystical Agriculture's armor tiers build on each other)
for _ in range(6):
    for g in ge:
        ACT.setdefault(g["id"], g["a"])
    moved = False
    for g in ge:
        for r in g["rc"]:
            for x in r["i"][1:]:
                xa = ACT.get(x.lstrip("#"))
                if xa is not None and oi(xa) > oi(g["a"]):
                    g["a"] = g["ga"] = xa; ACT[g["id"]] = xa; moved = True
                    g["ob"] = "?Added from the 6.6.6hf in-game dump; its Act is read from the piece it is upgraded from." if "ob" in g else g.get("ob")
                    if g["ob"] is None: g.pop("ob")
    if not moved: break
# sets: pieces grouped like gear_data.py does (the id without its slot word)
SLOTW = r"(helmet|chestplate|leggings|boots|helm|cap|hood|robe|robes|pants|tunic|greaves|crown|mask|hat|chest|legs|feet|head|armor|armour)"
def setkey(i):
    n = i.split(":")[1]; t = [x for x in n.split("_") if not re.fullmatch(SLOTW, x)]
    return i.split(":")[0] + ":" + ("_".join(t) or n)
sets = collections.defaultdict(list)
for g in ge:
    if g["k"] == "armor": sets[setkey(g["id"])].append(g)
gs = []
for k, ps in sorted(sets.items()):
    if len(ps) < 2: continue
    ps.sort(key=lambda g: ["HELMET", "CHESTPLATE", "LEGGINGS", "BOOTS"].index(g["sl"]))
    ws = [p["n"].split() for p in ps]; pre = []
    for col in zip(*ws):
        if all(w == col[0] for w in col): pre.append(col[0])
        else: break
    name = re.sub(r"\s+(Armor|Armour)$", "", " ".join(pre)).strip() or ps[0]["n"]
    gs.append({"k": k, "n": name, "p": [g["id"] for g in ps], "a": max((g["a"] for g in ps), key=oi), "kn": True})
# icons
IC = J("gear_icons.json")
def model(x, d=0):
    ns, p = x.split(":", 1) if ":" in x else ("minecraft", x)
    b = rd(f"assets/{ns}/models/{p}.json")
    if not b or d > 8: return {}
    try: m = json.loads(b)
    except Exception: return {}
    tex = {}
    if isinstance(m.get("parent"), str) and not m["parent"].startswith("builtin"): tex.update(model(m["parent"], d + 1).get("textures", {}))
    tex.update(m.get("textures", {})); m["textures"] = tex; return m
def icon(i):
    ns, n = i.split(":", 1); t = model(f"{ns}:item/{n}").get("textures", {})
    layers = [t[k] for k in sorted(t) if re.match(r"layer\d+$", k)] or [f"{ns}:item/{n}"]
    im = None
    for L in layers:
        while isinstance(L, str) and L.startswith("#"): L = t.get(L[1:])
        if not isinstance(L, str): continue
        lns, lp = L.split(":", 1) if ":" in L else ("minecraft", L)
        b = rd(f"assets/{lns}/textures/{lp}.png")
        if not b: continue
        f = Image.open(io.BytesIO(b)).convert("RGBA"); w, h = f.size
        if h > w and h % w == 0: f = f.crop((0, 0, w, w))
        im = f if im is None else (im.alpha_composite(f if f.size == im.size else f.resize(im.size, Image.NEAREST)) or im)
    if im is None or im.size[0] > 64: return None
    bo = io.BytesIO(); im.save(bo, "PNG", optimize=True); return base64.b64encode(bo.getvalue()).decode()
got = 0
for g in ge:
    if g["id"] not in IC:
        b = icon(g["id"])
        if b: IC[g["id"]] = b; got += 1
(P / "gear_icons.json").write_text(json.dumps(IC, separators=(",", ":"), sort_keys=True), encoding="utf-8")
(P / "gear_new.json").write_text(json.dumps({"_source": "build/pack_audit/gear_new.py over gear_runtime.json (6.6.6hf dump) and the pack's jars",
    "ge": ge, "gs": gs, "skipped": {k: sorted(v) for k, v in sorted(skipped.items())}}, ensure_ascii=False, indent=0), encoding="utf-8")
c = collections.Counter(g["k"] for g in ge)
print(f"new: {len(ge)} pieces {dict(c)}, {len(gs)} sets, icons +{got}; unverified Act {sum(1 for g in ge if 'ob' in g)}")
print("skipped:", {k: len(v) for k, v in skipped.items()})
