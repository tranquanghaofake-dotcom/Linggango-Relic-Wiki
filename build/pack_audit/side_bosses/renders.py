"""Portraits for side bosses drawn with Java models (no GeckoLib .geo.json in the jar).
Usage: renders.py W JARS_DIR [boss|boss...]  (W: ent_class.json from reg.py, sb_geo_in.json from bgeo.py; writes W/jm_in.json for jrender.js)
Every side boss (side_bosses.json, boss_extra.json) that bgeo.py does not draw as a GeckoLib model, the ones pictured from
fandom/wiki.gg pages included.
For each boss entity: the renderer class whose generic signature names the entity class gives the model class
(`new XModel(...)` in the renderer) and the texture (the first .png string that is not a glow/eye/overlay layer);
jmodel.py reads the model out of the bytecode. A boss with a hand entry in PICK uses that model/texture instead; one in REST
is posed as the game poses it at rest (its setupAnim run with the entity standing still), the rest show their build pose."""
import json, sys, zipfile, subprocess, tempfile, re, base64, glob, os, pathlib, io, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jmodel
from PIL import Image
W, JD = sys.argv[1], sys.argv[2]; ONLY = sys.argv[3].split("|") if len(sys.argv) > 3 else None
H = pathlib.Path(__file__).resolve().parents[2] / "patches"
ENT = json.load(open(W + "/ent_class.json")); GEO = set(json.load(open(W + "/sb_geo_in.json")))
SB = json.loads((H / "side_bosses.json").read_text()); BX = json.loads((H / "boss_extra.json").read_text())
need = {n: v["entity"] if isinstance(v["entity"], str) else v["entity"][0] for n, v in SB.items()}
for r in BX: need.setdefault(r[0], r[6])
need = {n: e for n, e in need.items() if n not in GEO and (not ONLY or n in ONLY)}
# hand picks: the renderer names an Easter-egg or phase texture first, keeps the model elsewhere, or draws a loose prop
# (jar name prefix, model class, texture jar prefix, texture path, parts to leave out)
LM, CA, GO = "legendarymonsters", "L_Enders_Cataclysm", "goety-2"
PICK = {"Dune Sentinel": (LM, "net.miauczel.legendary_monsters.entity.client.Model.DuneSentinelModel", LM, "assets/legendary_monsters/textures/entity/dune_sentinel/dune_sentinel.png", []),
        "Infernal Dragon": ("bossesrise", "net.unusual.blockfactorysbosses.client.model.Modeldragon", "bossesrise", "assets/block_factorys_bosses/textures/entities/dragon.png", []),
        "Scylla": (CA, "com.github.L_Ender.cataclysm.client.model.entity.Scylla_Model", CA, "assets/cataclysm/textures/entity/scylla/scylla.png", ["anchor2"]),
        "Maledictus": (CA, "com.github.L_Ender.cataclysm.client.model.entity.Maledictus_Model", CA, "assets/cataclysm/textures/entity/maledictus/maledictus_armor.png", []),
        "Apollyon": (GO, "com.Polarice3.Goety.client.render.model.ApostleModel", "GoetyRevelation", "assets/goety_revelation/textures/entity/apollyon/apollyon.png", []),
        "Redstone Golem": (GO, "com.Polarice3.Goety.client.render.model.RedstoneGolemModel", GO, "assets/goety/textures/entity/servants/redstone_golem/redstone_golem.png", []),
        # the renderer's type is a bound (<T extends Mob & IRM>), not the entity class
        "Redstone Monstrosity": (GO, "com.Polarice3.Goety.client.render.model.RedstoneMonstrosityModel", GO, "assets/goety/textures/entity/servants/redstone_monstrosity/redstone_monstrosity.png", []),
        # an animated texture whose name is built in code: frame 0 of the idle one
        "Ignis": (CA, "com.github.L_Ender.cataclysm.client.model.entity.Ignis_Model", CA, "assets/cataclysm/textures/entity/ignis/ignis_idle_0.png", []),
        # RevelationFix ships inside GoetyRevelation (META-INF/jarjar): extract it into JARS_DIR as RevelationFix-<version>.jar
        "Ice Hermit": ("RevelationFix", "com.mega.revelationfix.client.model.entity.IceHermitGeometry", "RevelationFix", "assets/revelationfix/textures/entity/ice_hermit/ice_hermit.png", [])}
# Tongbi (a GeckoLib model) is drawn by bgeo.py
# poses at rest, read from each model's own code (jmodel.model rest=): its setupAnim followed through its branches with the
# entity standing still (limb swing 0, age 0, no target, no animation playing), or a vanilla idle animation at time 0.
# Without one a constructor-built model shows its build pose: the Wroughtnaut's T-pose, the Forsaken's arms flat out
REST = {"Ferrous Wroughtnaut": {}, "Forsaken": {}, "Apostle": {}, "Apollyon": {"as": "goety:apostle"},  # Apollyon is an Apostle (isApollyon)
        "Redstone Monstrosity": {"anim": ("com.Polarice3.Goety.client.render.animation.RedstoneMonstrosityAnimations", "IDLE")},
        "Mutant Enderman": {"follow": True}}  # its arms are built with ternaries on constant arguments: followed, one side each
def jar(prefix): return next(j for j in glob.glob(JD + "/*.jar") if os.path.basename(j).startswith(prefix))
def rec(mod, png, src):  # alpha "blend" when the texture has semi-transparent texels, as for the Keepers
    A = Image.open(io.BytesIO(png)).convert("RGBA").getchannel(3); semi = sum(A.histogram()[1:255])
    names = lambda p: {p["name"]} | {n for k in p["children"] for n in names(k)}
    if "arms" in names(mod["root"]): prune(mod["root"], {"left_arm", "right_arm"})  # an illager at rest: arms crossed, the separate ones hidden (IllagerModel.setupAnim, ArmPose.CROSSED)
    seen(mod["root"], A, mod["tw"], mod["th"], 1 if semi else 26)
    return {"model": mod, "tex": base64.b64encode(png).decode(), "alpha": "blend" if semi else "cutout", "src": src}
def seen(p, A, tw, th, lim):
    """drop the cubes that draw nothing (every face of the box UV on texels the shader discards: alpha under 0.1, or 0 when
    blended), so the framing fits what shows: Maledictus's and the Possessed Paladin's empty wing and trident boxes doubled
    their bounds"""
    sx, sy = A.width / tw, A.height / th
    def lit(u0, v0, u1, v1):
        x0, y0 = max(0, int(u0 * sx)), max(0, int(v0 * sy)); x1, y1 = min(A.width, max(x0 + 1, math.ceil(u1 * sx))), min(A.height, max(y0 + 1, math.ceil(v1 * sy)))
        return x1 > x0 and y1 > y0 and A.crop((x0, y0, x1, y1)).getextrema()[1] >= lim
    def shows(c):
        x, y, z, w, h, d, g, u, v, m = c
        return any(a and b and lit(*r) for a, b, r in ((d, h, (u, v + d, u + d, v + d + h)), (d, h, (u + d + w, v + d, u + 2 * d + w, v + d + h)),
                                                       (w, d, (u + d, v, u + d + w, v + d)), (w, d, (u + d + w, v, u + d + 2 * w, v + d)),
                                                       (w, h, (u + d, v + d, u + d + w, v + d + h)), (w, h, (u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h))))
    p["cubes"] = [c for c in p["cubes"] if shows(c)]
    for k in p["children"]: seen(k, A, tw, th, lim)
def prune(p, hide):
    p["children"] = [prune(k, hide) for k in p["children"] if k["name"] not in hide]; return p
SKIP = re.compile(r"glow|eye|emissive|overlay|layer|_e\.png|crack|charg|aura|beam|laser|shield|armor|ghost|chain|bands|damage|translucent|angry|break|vulnerable|connection|explode|summon|circle|second|_2\.png|_3\.png|christmas|servant", re.I)
CL = {}  # class -> jar, every class of every jar
for j in sorted(glob.glob(JD + "/*.jar")):
    try: z = zipfile.ZipFile(j)
    except Exception: continue
    for c in z.namelist():
        if c.endswith(".class"): CL.setdefault(c[:-6].replace("/", "."), j)
SZ = {3: 4, 4: 4, 5: 8, 6: 8, 7: 2, 8: 2, 9: 4, 10: 4, 11: 4, 12: 4, 15: 3, 16: 2, 17: 4, 18: 4, 19: 2, 20: 2}
def super_of(c):  # the super_class of a class file, read from its constant pool
    b = zipfile.ZipFile(CL[c]).read(c.replace(".", "/") + ".class"); u = lambda i: int.from_bytes(b[i:i + 2], "big"); n, i, k, cp = u(8), 10, 1, {}
    while k < n:
        t = b[i]
        if t == 1: cp[k] = b[i + 3:i + 3 + u(i + 1)].decode("utf8", "replace"); i += 3 + u(i + 1)
        else: cp[k] = u(i + 1); i += 1 + SZ[t]
        k += 2 if t in (5, 6) else 1
    return cp[cp[u(i + 4)]].replace("/", ".") if u(i + 4) else None
def chain(c):  # the entity class, then its parents below Minecraft's (a renderer may name an abstract parent: AbstractWitherNecromancer)
    out = []
    while c in CL and not c.startswith("net.minecraft"): out.append(c); c = super_of(c)
    return out
def javap(jar, cls_path):
    tmp = tempfile.mkdtemp(); zipfile.ZipFile(jar).extract(cls_path, tmp)
    return subprocess.run(["javap", "-c", "-p", "-constants", tmp + "/" + cls_path], capture_output=True, text=True).stdout
CH = {e: chain(ENT[e]) for e in need.values() if e in ENT}; T = {c for v in CH.values() for c in v}
jmodel.CTX["cp"] = {c.replace(".", "/"): j for c, j in CL.items()}  # the classes a pose runs through (llibrary, citadel, Goety…)
def build(n, e, jar_, cls):
    r = REST.get(n)
    if r is None: return jmodel.model(jar_, cls)
    e = r.get("as", e); m = jmodel.model(jar_, cls, rest={"chain": chain(ENT[e]) if e in ENT else [], **{k: v for k, v in r.items() if k not in ("as", "follow")}},
                                          follow=r.get("follow", False))
    print(n, "pose at rest:", jmodel.CTX.get("ub", 0), "branches decided by the skip rule,", jmodel.CTX.get("loops", 0), "loops cut"); jmodel.CTX["ub"] = jmodel.CTX["loops"] = 0
    return m
heads = {}  # entity class -> [(jar, renderer path)], from the renderer classes of the jars that hold the entity classes
for j in sorted({CL[c] for c in T}):
    z = zipfile.ZipFile(j)
    for c in z.namelist():
        if c.endswith(".class") and "render" in c.lower():
            d = z.read(c)
            for ec in T:
                if ec.replace(".", "/").encode() + b";" in d: heads.setdefault(ec, []).append((j, c))
out, miss = {}, []
for n, e in need.items():
    cand = [(ec, j, c) for ec in CH.get(e, []) for j, c in sorted(heads.get(ec, []), key=lambda x: ("layer" in x[1].lower(), len(x[1])))]
    got = None
    if n in PICK:
        mj, mc, tj, tp, hide = PICK[n]; z = zipfile.ZipFile(jar(tj))
        mod = build(n, e, jar(mj), mc)
        if not mod: miss.append((n, "pick failed")); continue
        mod["root"] = prune(mod["root"], hide)
        out[n] = rec(mod, z.read(tp), [os.path.basename(jar(mj)), mc.split(".")[-1], tp])
        continue
    for ec, j, c in cand:
        t = javap(j, c)
        hd = t.split("{")[0]
        if not re.search(r"(Renderer<\s*|extends\s+)" + re.escape(ec) + r"\b", hd): continue
        models = [m for m in re.findall(r"// class (\S+)", t) if re.search(r"model", m, re.I) and "Layer" not in m and "geom" not in m and "/minecraft/" not in m]
        texs = [s for s in re.findall(r"// String (\S+\.png)", t) if not SKIP.search(s)]
        if not models: continue
        z = zipfile.ZipFile(j); ns = e.split(":")[0]
        paths = ["assets/" + (t if ":" in t else ns + ":" + t).replace(":", "/", 1) for t in texs]
        paths += [x for x in z.namelist() if x.startswith("assets/" + ns + "/textures/entit") and x.endswith("/" + e.split(":")[1] + ".png")]  # held in a field: by the entity's name
        tpath = next((x for x in paths if x in z.namelist()), None)
        if not tpath: continue
        for m in models:
            try: mod = build(n, e, j, m.replace("/", "."))
            except Exception as ex: mod = None
            if mod and mod.get("root") and (mod["root"]["cubes"] or mod["root"]["children"]):
                got = rec(mod, z.read(tpath), [os.path.basename(j), m.split("/")[-1], tpath]); break
        if got: break
    if got: out[n] = got
    else: miss.append((n, e, ENT.get(e), len(cand)))
json.dump(out, open(W + "/jm_in.json", "w"))
print(len(out), "models;", "missing:", *miss, sep="\n ")
