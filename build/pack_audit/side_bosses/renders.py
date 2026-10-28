"""Portraits for side bosses drawn with Java models (no GeckoLib .geo.json in the jar).
Usage: renders.py W JARS_DIR  (W: ent_class.json from stats.py; writes W/jm_in.json for jrender.js)
For each boss entity: the renderer class whose generic signature names the entity class gives the model class
(`new XModel(...)` in the renderer) and the texture (the first .png string that is not a glow/eye/overlay layer);
jmodel.py reads the model out of the bytecode. A boss with a hand entry in PICK uses that model/texture instead."""
import json, sys, zipfile, subprocess, tempfile, re, base64, glob, os, pathlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jmodel
W, JD = sys.argv[1], sys.argv[2]
H = pathlib.Path(__file__).resolve().parents[2] / "patches"
ENT = json.load(open(W + "/ent_class.json"))
SB = json.loads((H / "side_bosses.json").read_text()); BX = json.loads((H / "boss_extra.json").read_text())
need = {}
for n, v in SB.items():
    if not v.get("img"): need[n] = v["entity"] if isinstance(v["entity"], str) else v["entity"][0]
for r in BX:
    if r[0] not in SB or not SB[r[0]].get("img"): need[r[0]] = r[6]
# hand picks: the renderer names an Easter-egg or phase texture first, keeps the model elsewhere, or draws a loose prop
# (jar name prefix, model class or GeckoLib geo path, texture jar prefix, texture path, parts to leave out)
LM, CA, GO = "legendarymonsters", "L_Enders_Cataclysm", "goety-2"
PICK = {"Dune Sentinel": (LM, "net.miauczel.legendary_monsters.entity.client.Model.DuneSentinelModel", LM, "assets/legendary_monsters/textures/entity/dune_sentinel/dune_sentinel.png", []),
        "Infernal Dragon": ("bossesrise", "net.unusual.blockfactorysbosses.client.model.Modeldragon", "bossesrise", "assets/block_factorys_bosses/textures/entities/dragon.png", []),
        "Scylla": (CA, "com.github.L_Ender.cataclysm.client.model.entity.Scylla_Model", CA, "assets/cataclysm/textures/entity/scylla/scylla.png", ["anchor2"]),
        "Maledictus": (CA, "com.github.L_Ender.cataclysm.client.model.entity.Maledictus_Model", CA, "assets/cataclysm/textures/entity/maledictus/maledictus_armor.png", []),
        "Apollyon": (GO, "com.Polarice3.Goety.client.render.model.ApostleModel", "GoetyRevelation", "assets/goety_revelation/textures/entity/apollyon/apollyon.png", []),
        "Redstone Golem": (GO, "com.Polarice3.Goety.client.render.model.RedstoneGolemModel", GO, "assets/goety/textures/entity/servants/redstone_golem/redstone_golem.png", []),
        "Tongbi, the Sculptor": ("mowziesmobs", "geo:assets/mowziesmobs/geo/sculptor.geo.json", "mowziesmobs", "assets/mowziesmobs/textures/entity/sculptor.png", [])}
def jar(prefix): return next(j for j in glob.glob(JD + "/*.jar") if os.path.basename(j).startswith(prefix))
def prune(p, hide):
    p["children"] = [prune(k, hide) for k in p["children"] if k["name"] not in hide]; return p
SKIP = re.compile(r"glow|eye|emissive|overlay|layer|_e\.png|crack|charg|aura|beam|laser|shield|armor|ghost|chain|bands|damage|translucent|angry|break|vulnerable|connection|explode|summon|circle|second|_2\.png|_3\.png|christmas|servant", re.I)
jars = {}
for j in glob.glob(JD + "/*.jar"):
    z = zipfile.ZipFile(j)
    for n in z.namelist():
        if n.endswith(".class") and ("render" in n.lower()): jars.setdefault(j, []).append(n)
def javap(jar, cls_path):
    tmp = tempfile.mkdtemp(); zipfile.ZipFile(jar).extract(cls_path, tmp)
    return subprocess.run(["javap", "-c", "-p", "-constants", tmp + "/" + cls_path], capture_output=True, text=True).stdout
heads = {}  # entity class -> [(jar, renderer path)]
for j, cs in jars.items():
    z = zipfile.ZipFile(j)
    for c in cs:
        d = z.read(c)
        for ec in set(ENT.values()):
            if ec.replace(".", "/").encode() + b";" in d: heads.setdefault(ec, []).append((j, c))
out, miss = {}, []
for n, e in need.items():
    ec = ENT.get(e)
    cand = heads.get(ec, []) if ec else []
    got = None
    if n in PICK:
        mj, mc, tj, tp, hide = PICK[n]; z = zipfile.ZipFile(jar(tj))
        if mc.startswith("geo:"): mod = {"geo": json.loads(zipfile.ZipFile(jar(mj)).read(mc[4:]))}
        else:
            mod = jmodel.model(jar(mj), mc)
            if not mod: miss.append((n, "pick failed")); continue
            mod["root"] = prune(mod["root"], hide)
        out[n] = {"model": mod, "tex": base64.b64encode(z.read(tp)).decode(), "src": [os.path.basename(jar(mj)), mc.split(".")[-1].split("/")[-1], tp]}
        continue
    for j, c in sorted(cand, key=lambda x: ("layer" in x[1].lower(), len(x[1]))):
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
            try: mod = jmodel.model(j, m.replace("/", "."))
            except Exception as ex: mod = None
            if mod and mod.get("root") and (mod["root"]["cubes"] or mod["root"]["children"]):
                got = {"model": mod, "tex": base64.b64encode(z.read(tpath)).decode(), "src": [os.path.basename(j), m.split("/")[-1], tpath]}; break
        if got: break
    if got: out[n] = got
    else: miss.append((n, e, ec, len(cand)))
json.dump(out, open(W + "/jm_in.json", "w"))
print(len(out), "models;", "missing:", *miss, sep="\n ")
