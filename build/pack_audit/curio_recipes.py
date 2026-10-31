#!/usr/bin/env python3
"""Curio recipe grids as the pack makes them.

The recipes the game ends up with: the datapack recipes of every mod jar, loaded in FML's mod order (a later jar's file
with the same recipe id replaces an earlier one: Covenant of the Seven declares itself AFTER Enigmatic Legacy and replaces
14 of its recipes), then kubejs/data over them, then the KubeJS server scripts (kubejs_recipes.js runs them): what they
remove (by id or by output) is gone, what they add counts, and their replaceInput swaps (curio_dedupe.js) apply to the
recipes there were when they ran. A datapack recipe whose `conditions` fail, or that names an item no mod registers, does
not load (vanilla drops it with "Unknown item"); in a KubeJS recipe an unregistered id is an empty ingredient, and KubeJS
blanks that key's cells (ShapedRecipeJS.afterLoaded), so the cell is left empty here too. Drawn: Crafting Table (shaped,
shapeless), Blood Magic's Hellfire Forge and Alchemy Array.

For each crafted curio with no grid (or one this script wrote, `grx`) it writes the pack's recipe. A curio whose grid came
from elsewhere keeps it while the grid's ingredients are those of one of the pack's recipes for it; when they are not (the
wiki was written from the mod's own recipe, which the pack replaced), the pack's recipe is written with `over: 1` and
patches/curio_recipes.py replaces the grid. curios whose source line names other ingredients are printed.

Writes
  build/patches/curio_recipes.json      {"grids": {curio id: grid in data.js's `gr` shape (+ over)}, "names": {ingredient id:
                                         name}, "nopic": {ingredient id: why it has no flat picture}}
  build/patches/curio_eff_recipes.json  {"sets": {curio id: [[ingredient ids, tags as #tag], one per recipe the pack
                                         has for it]}, "allow": {curio id: why its grid differs}}; check.js holds every grid
                                         to it
and adds icons for ingredients without one to gear_icons.json, drawn as the inventory draws them (mcassets.py, from the
game's resource stack minus the All Rights Reserved packs). patches/curio_recipes.py puts the grids and names in data.js.

Usage: python3 build/pack_audit/curio_recipes.py <dir with *.jar of the pack> <the pack's kubejs dir> <W: work dir with
       mc_client.jar, lang.json and pack/ (mcassets.pack_sources)>"""
import sys, json, glob, zipfile, re, pathlib, subprocess, os, heapq
B = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
JARS, KJ, W = sys.argv[1], sys.argv[2], sys.argv[3]
src = (B / "src" / "data.js").read_text(encoding="utf-8"); D, _ = json.JSONDecoder().raw_decode(src, 8)
NM, _ = json.JSONDecoder().raw_decode(src, src.find(",NM=") + 4)
NAMEID = json.loads((B / "patches" / "name_ids.json").read_text(encoding="utf-8")); ID2N = {v: k for k, v in NAMEID.items()}
for d in D: ID2N.setdefault(d["id"], d["n"])
DIDS = {d["id"] for d in D}
BYID = {d["id"]: d for d in D}
want = {d["id"]: d for d in D if d.get("g") == "Craft" and (not d.get("gr") or d.get("grx"))}   # grx: a grid it wrote last time
DRAWN = {"Crafting Table", "Crafting Table (shapeless)", "Hellfire Forge (Blood Magic)", "Alchemy Array (Blood Magic)"}

# ---- mod jars in FML 47's order: file names sorted (lower case), then a topological sort over the mods.toml BEFORE/AFTER
# orderings, ties broken by that index (ModSorter). Datapack files load in this order, the last one of an id wins.
def toml_blocks(t):
    parts = re.split(r'^\s*\[\[?([^\]]+)\]\]?\s*(?:#.*)?$', t, flags=re.M)
    return [(parts[k].strip(), parts[k + 1]) for k in range(1, len(parts), 2)]
def toml_val(body, key):
    m = re.search(r'^\s*' + key + r'\s*=\s*"?([^"\n#]+?)"?\s*(?:#.*)?$', body, re.M)
    return m.group(1).strip() if m else None
files = sorted(glob.glob(JARS + "/*.jar"), key=lambda p: os.path.basename(p).lower())
idx = {f: i for i, f in enumerate(files)}; mod2file, deps, MODS = {}, [], {"minecraft", "forge"}
for f in files:
    try: t = zipfile.ZipFile(f).read("META-INF/mods.toml").decode("utf-8", "replace")
    except Exception: continue
    for h, body in toml_blocks(t):
        if h == "mods":
            mid = toml_val(body, "modId")
            if mid: mod2file.setdefault(mid, f); MODS.add(mid)
        elif h.startswith("dependencies."):
            dep, order = toml_val(body, "modId"), (toml_val(body, "ordering") or "NONE").upper()
            if dep and order in ("AFTER", "BEFORE"): deps.append((h.split(".", 1)[1], dep, order))
edges, indeg = {f: set() for f in files}, {f: 0 for f in files}
for owner, dep, order in deps:
    fo, fd = mod2file.get(owner), mod2file.get(dep)
    if not fo or not fd or fo == fd: continue
    a, c = (fd, fo) if order == "AFTER" else (fo, fd)   # a loads before c
    if c not in edges[a]: edges[a].add(c); indeg[c] += 1
h = [(idx[f], f) for f in files if indeg[f] == 0]; heapq.heapify(h); order = []
while h:
    _, f = heapq.heappop(h); order.append(f)
    for c in edges[f]:
        indeg[c] -= 1
        if indeg[c] == 0: heapq.heappush(h, (idx[c], c))
order += [f for f in files if f not in order]          # a dependency cycle: FML would refuse to start; keep them last
zips = [(os.path.basename(f), zipfile.ZipFile(f)) for f in order]
POS = {jn: k for k, (jn, _) in enumerate(zips)}
client = zipfile.ZipFile(os.path.join(W, "mc_client.jar")); CLIENT_N = set(client.namelist())

# ---- names and registered ids: lang files (later resources win, as in game), the vanilla client jar, W/lang.json
lang, trait, models = {}, {}, set()
def read_lang(z, n):
    try: dd = json.loads(z.read(n).decode("utf-8", "replace"))
    except Exception: return
    for k, v in dd.items():
        if not isinstance(v, str): continue
        m = re.match(r"(item|block|trait)\.([a-z0-9_.-]+)\.([a-z0-9_/.-]+)$", k)
        if not m: continue
        (trait if m.group(1) == "trait" else lang)[m.group(2) + ":" + m.group(3)] = v
read_lang(client, "assets/minecraft/lang/en_us.json")
for _, z in zips:
    for n in z.namelist():
        if re.match(r"assets/[^/]+/lang/en_us\.json$", n): read_lang(z, n)
        m = re.match(r"assets/([^/]+)/models/item/(.+)\.json$", n)
        if m: models.add(m.group(1) + ":" + m.group(2))
WL = json.loads(open(os.path.join(W, "lang.json"), encoding="utf-8").read())
for k, v in WL.items(): lang.setdefault(k, v)
for k, v in trait.items(): lang.setdefault(k, v)   # L2 Hostility's trait items are named by their trait
def registered(i):
    return (i in lang or i in DIDS or i in ID2N or i in models
            or i.startswith("minecraft:") and f"assets/minecraft/models/item/{i[10:]}.json" in CLIENT_N)
unreg = {}   # id -> recipes that name it

# ---- KubeJS server scripts
ks = json.loads(subprocess.run(["node", str(pathlib.Path(__file__).with_name("kubejs_recipes.js")), KJ], capture_output=True, text=True, check=True).stdout)
gone_id = {r["id"] for r in ks["removed"] if isinstance(r, dict) and isinstance(r.get("id"), str)}
gone_out = set()
for r in ks["removed"]:
    o = r.get("output") if isinstance(r, dict) else None
    gone_out.update([o] if isinstance(o, str) else [x for x in o if isinstance(x, str)] if isinstance(o, list) else [])
def swap(c, upto):
    """a cell after the scripts' replaceInput calls made while the recipe existed (upto: how many script recipes were added
    when it was made; datapack recipes existed from the start)"""
    if not c or not c[0]: return c
    for rp in ks.get("replaced", []):
        if upto <= rp["at"] and c[0] == rp["from"]: c = [rp["to"], ""]
    return c
def grid(shaped, pattern, key, ingredients, n):
    if shaped:
        w = max(len(x) for x in pattern)
        cells = [key.get(ch) if ch != " " else None for row in pattern for ch in row.ljust(w)]
        return {"w": w, "h": len(pattern), "c": cells, "st": "Crafting Table", "n": n, "l": 0}
    return {"w": min(3, len(ingredients)), "h": (len(ingredients) + 2) // 3, "c": ingredients, "st": "Crafting Table (shapeless)", "n": n, "l": 1}
def kcell(x, rid):
    if not x: return None
    if x.startswith("#"): return ["", x]
    if not registered(x): unreg.setdefault(x, set()).add(rid); return None   # an empty ingredient: KubeJS blanks its cells
    return [x, ""]
eff = {}   # output -> [(how, recipe id, grid)], in the order a grid is chosen: script, kubejs/data, jars
for n_, a in enumerate(ks["added"]):
    o = a.get("output")
    if not isinstance(o, str) or o not in DIDS or not (a.get("pattern") or a.get("ingredients")): continue
    rid = "KubeJS script #%d" % n_
    g = grid(a["type"] == "shaped", a.get("pattern"), {k: kcell(v, o) for k, v in (a.get("key") or {}).items()},
             [kcell(x, o) for x in a.get("ingredients") or []], a.get("count", 1))
    g["c"] = [swap(c, n_ + 1) for c in g["c"]]
    eff.setdefault(o, []).append(("KubeJS script", rid, g))

# ---- datapack recipes by id: jars in load order, then kubejs/data; the last file of an id is the one the game reads
DP = {}
for jn, z in zips:
    for n in z.namelist():
        m = re.match(r"data/([^/]+)/recipes/(.*)\.json$", n)
        if m: DP[m.group(1) + ":" + m.group(2)] = (jn, z, n)
for f in sorted(glob.glob(KJ + "/data/*/recipes/**/*.json", recursive=True)):
    rel = os.path.relpath(f, KJ + "/data").split(os.sep); DP[rel[0] + ":" + "/".join(rel[2:])[:-5]] = ("kubejs data", None, f)
def cond_ok(cs):
    if not cs: return True
    for c in cs if isinstance(cs, list) else [cs]:
        if not isinstance(c, dict): continue
        t = c.get("type", "")
        if t == "forge:mod_loaded" and c.get("modid") not in MODS: return False
        if t == "forge:not" and cond_ok([c.get("value")]): return False
        if t == "forge:and" and not cond_ok(c.get("values", [])): return False
        if t == "forge:or" and not any(cond_ok([v]) for v in c.get("values", [])): return False
        if t == "forge:item_exists" and not registered(c.get("item", "")): return False
        if t == "forge:false": return False
    return True   # the mods' own conditions (enigmaticlegacy:is_enabled, ...) hold with the pack's configs
def ing(o):
    if isinstance(o, list): o = o[0] if o else {}
    if not isinstance(o, dict): return None
    if "item" in o: return [o["item"], ""]
    if "tag" in o: return ["", "#" + o["tag"]]
    return None
dp_found = {}   # output -> [(how, id, grid)] kubejs/data first, then the jars from the last loaded
for rid, (src_, z, n) in DP.items():
    if rid in gone_id: continue
    try: o = json.loads(z.read(n) if z else open(n, "rb").read())
    except Exception: continue
    if not isinstance(o, dict): continue
    if o.get("type") == "forge:conditional":
        o = next((r.get("recipe") for r in o.get("recipes", []) if isinstance(r, dict) and cond_ok(r.get("conditions"))), None) or {}
    if not isinstance(o, dict) or not cond_ok(o.get("conditions")): continue
    r = o.get("result") or o.get("output"); out = r if isinstance(r, str) else (r or {}).get("item") if isinstance(r, dict) else None
    if out not in DIDS or out in gone_out: continue
    t, cnt = o.get("type", ""), (r.get("count", 1) if isinstance(r, dict) else 1)
    if t.endswith("crafting_shaped") and o.get("pattern"):
        g = grid(True, o["pattern"], {k: ing(v) for k, v in o.get("key", {}).items()}, None, cnt)
    elif t.endswith("crafting_shapeless") and o.get("ingredients"):
        g = grid(False, None, None, [ing(x) for x in o["ingredients"]], cnt)
    elif t == "bloodmagic:soulforge":       # Hellfire Forge: up to four inputs, any order, plus the Demon Will it needs
        g = dict(grid(False, None, None, [ing(o[k]) for k in ("input0", "input1", "input2", "input3") if o.get(k)], cnt), st="Hellfire Forge (Blood Magic)")
    elif t == "bloodmagic:array":           # Alchemy Array: the base item, then the one added to it
        g = dict(grid(False, None, None, [ing(o[k]) for k in ("baseinput", "addedinput") if o.get(k)], cnt), st="Alchemy Array (Blood Magic)")
    else: continue
    bad = sorted({c[0] for c in g["c"] if c and c[0] and not registered(c[0])})
    if bad:   # "Unknown item": the recipe does not load
        for b in bad: unreg.setdefault(b, set()).add(rid + " (not loaded)")
        continue
    g["c"] = [swap(c, 0) for c in g["c"]]
    dp_found.setdefault(out, []).append((src_ if src_ == "kubejs data" else "mod jar " + src_, rid, g, -1 if z is None else POS[src_]))
for out, rs in dp_found.items():
    eff.setdefault(out, []).extend((a, b, c) for a, b, c, _ in sorted(rs, key=lambda r: (r[3] != -1, -r[3], r[1])))
for i, rs in sorted(unreg.items()): print("  not a registered item, left out:", i, "in", ", ".join(sorted(rs)))

key = lambda c: c[1] or c[0]
cset = lambda g: sorted({key(c) for c in g["c"] if c and key(c)})
SETS = {i: [cset(g) for _, _, g in rs] for i, rs in sorted(eff.items())}
SETS = {i: [s for k, s in enumerate(v) if s and s not in v[:k]] for i, v in SETS.items()}
SETS = {i: v for i, v in SETS.items() if v}
EP = B / "patches" / "curio_eff_recipes.json"
allow = json.loads(EP.read_text(encoding="utf-8")).get("allow", {}) if EP.exists() else {}   # kept by hand: grids that may differ
keep, how, over = {}, {}, []
for i, d in BYID.items():
    rs = [r for r in eff.get(i, []) if cset(r[2])]
    if not rs: continue
    gr = d.get("gr")
    if i in want:   # no grid, or the one it wrote (gro: a grid it replaced, so the replacement stays marked)
        keep[i] = dict(rs[0][2], over=1) if d.get("gro") else rs[0][2]; how[i] = rs[0][0]
        if d.get("gro"): over.append(i)
        continue
    if not gr or gr.get("st") not in DRAWN or cset(gr) in SETS[i]: continue
    if i in allow: print("  the pack's recipe differs from the wiki's grid, allowed:", i, "-", allow[i]); continue
    keep[i] = dict(rs[0][2], over=1); how[i] = rs[0][0]; over.append(i)
    print("  the pack's recipe differs from the wiki's grid:", i, f"({rs[0][0]} {rs[0][1]})", "wiki only", sorted(set(cset(gr)) - set(cset(rs[0][2]))),
          "pack only", sorted(set(cset(rs[0][2])) - set(cset(gr))))
# the source line should name the ingredients
def names_of(cs): return {(ID2N.get(c[0]) or lang.get(c[0]) or "").lower() for c in cs if c and c[0]}
rej = []
for i, g in keep.items():
    line = " ".join(BYID[i]["src"]).lower(); ns = names_of(g["c"]) - {""}
    if not all(n in line for n in ns): rej.append(i); print("  line does not name:", i, f"({how[i]})", sorted(n for n in ns if n not in line))

# ---- names and pictures for the ingredients of every grid the pages draw
GI = json.loads((B / "patches" / "gear_icons.json").read_text(encoding="utf-8"))
ICK = set(re.findall(r'"([a-z0-9_.-]+:[a-z0-9_/.-]+)":"iVBOR', src)) | set(GI)
import mcassets
A = mcassets.Assets(mcassets.pack_sources(W, client=os.path.join(W, "mc_client.jar")))
def icon(i):   # as name_icons.py: the inventory picture (flat layers, block models at 32 px), else the particle face of a
    ns, n = mcassets.rl(i)   # model that is not drawn by code, else the item or block texture of the same name
    im = A.icon(i, 32)
    m = A.model(f"{ns}:item/{n}")
    if im is None: im = A.texture(A.resolve(m, m["textures"].get("particle"))) if m and not m["entity"] else None
    if im is None and not (m and m["entity"]): im = A.texture(f"{ns}:item/{n}") or A.texture(f"{ns}:block/{n}")
    if im is None or im.size[0] > 64: return None, ("its item model is builtin/entity: the game draws it in code, there is no flat picture"
                                                     if m and m["entity"] else "no item model or texture in the pack")
    return mcassets.png_b64(im), None
# NM as it would be without the names this script wrote last time (patches/curio_recipes.py copied them in), so a rerun
# writes them again instead of seeing them as the wiki's own
CR = B / "patches" / "curio_recipes.json"
PREV = json.loads(CR.read_text(encoding="utf-8")).get("names", {}) if CR.exists() else {}
NMB = {k: v for k, v in NM.items() if PREV.get(k) != v}
grids = [(g, 1) for g in keep.values()] + [(d["gr"], 0) for d in D if d.get("gr") and d["id"] not in keep]
names, icons, nopic = {}, {}, {}
TAGID = json.loads((B / "patches" / "tag_ids.json").read_text(encoding="utf-8"))   # a tag slot shows its usual member
for g, new in grids:
    for c in g["c"]:
        i = c and (c[0] or TAGID.get(c[1]))
        if not i: continue
        nm = ID2N.get(i) or lang.get(i)
        if i not in DIDS and nm and (i not in NMB and i not in ID2N                # a name the pages lack
                                     or new and not i.startswith("minecraft:") and NMB.get(i, nm) == nm):  # a new grid's (also the ones it added before)
            names[i] = nm
        if i not in ICK and i not in icons and i not in nopic:
            b, why = icon(i)
            if b: icons[i] = b
            else: nopic[i] = why
    # ids of one recipe the game names alike (Blood Magic's four Demon Wills: the tooltip gives the type): the id's last word
    same = {}
    for c in g["c"]:
        i = c and (c[0] or TAGID.get(c[1]))
        if i and i in names: same.setdefault(names[i], set()).add(i)
    for nm, ids in same.items():
        if len(ids) > 1:
            for i in ids: names[i] = f"{nm} ({i.rsplit('_', 1)[-1].title()})"
# a curio made from another curio is listed on that one's page ("Used to craft"), which names it from NM
for i, g in keep.items():
    if i not in NMB and any(c and c[0] in DIDS for c in g["c"]): names[i] = BYID[i]["n"]
if icons: GI.update(icons); (B / "patches" / "gear_icons.json").write_text(json.dumps(GI, ensure_ascii=False, separators=(",", ":"), sort_keys=True), encoding="utf-8")
for i, why in sorted(nopic.items()): print("  no picture:", i, "-", why)
print(f"ingredient names: {len(names)}; icons added to gear_icons.json: {len(icons)} {sorted(icons)}")
CR.write_text(json.dumps({"grids": keep, "names": names, "nopic": nopic}, ensure_ascii=False, separators=(",", ":"), sort_keys=True), encoding="utf-8")
J1 = lambda o: json.dumps(o, ensure_ascii=False)   # one curio per line, so a diff shows which recipes moved
EP.write_text('{"allow": {\n' + ",\n".join(J1(k) + ": " + J1(v) for k, v in sorted(allow.items())) + '},\n"sets": {\n'
              + ",\n".join(J1(k) + ": " + J1(v) for k, v in SETS.items()) + "}}\n", encoding="utf-8")
print(f"crafted curios with no grid or one this script wrote: {len(want)}; written: {len(keep) - len(over)}; grids the pack's recipe replaces: {len(over)} {sorted(over)}; "
      f"curios with a recipe the pages can draw: {len(SETS)}; source line names other ingredients: {len(rej)}")
