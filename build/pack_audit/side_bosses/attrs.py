"""Side-boss attribute builders, run on build/gear/mjvm.py's VM (no javap).
Usage: attrs.py W JARS_DIR SRG_JAR   (after reg.py: reads W/ent_class.json; SRG_JAR = Forge's server-1.20.1-*-srg.jar, which
names the vanilla Attributes fields and holds the vanilla superclasses)
Writes W/attrs.json {jar: {dotted.entity.Class: {method: [[key, value], ...]}}} and W/supers.json {entity id: true | false}
for stats.py. The classes are each side boss's registered class (ent_class.json) or the one stats' MAN table names (man.json),
and every class of its superclass chain below net.minecraft. A builder method is a static method of that class returning
AttributeSupplier$Builder; it runs with a stand-in builder: a vanilla factory (Mob.createMobAttributes, Monster.
createMonsterAttributes, ...) gives an empty one, and Builder.add(attribute, value) (SRG m_22268_) is recorded in call
order; a mod's own helper or superclass builder runs inline, so what it adds is recorded too. key: hp armor tough dmg kbr
for the five stats.py keeps, else the attribute's name (null: a mod attribute the VM cannot name); value: a number, "<ConfigSimpleName>.<field>" for a read of one of
cfg.py's config classes (stats.py looks it up in cfg.json), or null when the interpreter could not tell.
supers.json: whether the entity's class (registered, else MAN's) extends net.minecraft.world.entity.monster.Monster."""
import json, sys, os, glob, pathlib, zipfile
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(D, "..", "..", "gear")); sys.path.insert(0, D)
import mjvm, cfg

BUILDER = "Lnet/minecraft/world/entity/ai/attributes/AttributeSupplier$Builder;"
KEY = {"generic.max_health": "hp", "generic.armor": "armor", "generic.armor_toughness": "tough", "generic.attack_damage": "dmg",
       "generic.knockback_resistance": "kbr"}
MONSTER = "net/minecraft/world/entity/monster/Monster"
# entities with no EntityType of their own: Goety Revelation's ritual summons goety_revelation:summon_apollyon, whose class
# SummonApollyon extends Goety's SummonApostle, so Apollyon is Goety's Apostle (stats.py takes its health from ModConfig)
SAME = {"goety_revelation:apollyon": "goety:apostle"}

class Tag:  # a config read: passes through .get(), unboxing and casts unchanged
    def __init__(s, t): s.t = t
    def __repr__(s): return "Tag(%s)" % s.t

class Builder:
    def __init__(s): s.adds = []

class AVM(mjvm.VM):
    tags = {}  # internal config class name -> simple name
    def getstatic(s, cls, name, desc):
        if cls in s.tags: return Tag(s.tags[cls] + "." + name)
        return super().getstatic(cls, name, desc)
    def invoke(s, kind, cls, name, desc, args, recv=None):
        rt = mjvm.rettype(desc)
        if isinstance(recv, Tag): return recv
        if isinstance(recv, Builder):
            if name == "m_22268_" and len(args) == 2: recv.adds.append((args[0], args[1]))
            return recv if rt == BUILDER else (mjvm.OP if rt != "V" else None)
        if kind == "invokestatic" and rt == BUILDER and cls.startswith("net/minecraft/"): return Builder()
        if kind == "invokestatic" and name == "valueOf" and args and isinstance(args[0], Tag): return args[0]
        return super().invoke(kind, cls, name, desc, args, recv)

def attr_key(a):
    n = a.n if isinstance(a, mjvm.Attr) else None
    return KEY.get(n, n)

def val(v):
    if isinstance(v, Tag): return v.t
    return v if mjvm.num(v) else None

def builders(vm, cls):
    """{method: [[key, value], ...]} for the static builder methods cls declares, in class-file order"""
    k = vm.cf(cls); out = {}
    for m in k.methods if k else []:
        if not (m.code and m.access_flags.get("acc_static") and mjvm.rettype(m.descriptor.value) == BUILDER): continue
        args = [mjvm.OP] * len(mjvm.dtypes(m.descriptor.value))
        try: r = vm.run(cls, k, m, args)
        except Exception as ex: vm.err(cls, m.name.value, None, ex); continue
        if not isinstance(r, Builder): continue
        nm = m.name.value if m.name.value not in out else m.name.value + m.descriptor.value
        out[nm] = [[attr_key(a), val(v)] for a, v in r.adds]
    return out

def chain(vm, cls):
    return [c for c in vm.supers(cls) if not c.startswith(("net/minecraft/", "java/"))]

if __name__ == "__main__":
    W, JD, SRG = sys.argv[1], sys.argv[2], sys.argv[3]
    H = pathlib.Path(D).parents[1] / "patches"
    SB = json.loads((H / "side_bosses.json").read_text()); BX = json.loads((H / "boss_extra.json").read_text())
    IDS = sorted({e for v in SB.values() for e in (v["entity"] if isinstance(v["entity"], list) else [v["entity"]])} | {r[6] for r in BX})
    ENT = json.load(open(W + "/ent_class.json")); MAN = json.load(open(os.path.join(D, "man.json")))
    jars = sorted(glob.glob(JD + "/*.jar"))
    vm = AVM(jars + [SRG]); mjvm.srg_tables(vm, SRG)
    AVM.tags = {c: simple for simple, (_, c) in cfg.find_classes(JD).items()}
    by = cfg.jars_by_mod(JD); jarof = {}
    def man_class(e):  # MAN's simple name, in the jars of the entity's namespace
        if e not in MAN: return None
        for j in by.get(e.split(":")[0], []):
            if j not in jarof: jarof[j] = {n[:-6].split("/")[-1]: n[:-6] for n in sorted(zipfile.ZipFile(j).namelist()) if n.endswith(".class")}
            if MAN[e] in jarof[j]: return jarof[j][MAN[e]]
        return None
    attrs, sup, done = {}, {}, set()
    for e in IDS:
        a = SAME.get(e, e); reg = ENT[a].replace(".", "/") if a in ENT else None; man = man_class(e)
        for top in filter(None, (reg, man)):
            for c in chain(vm, top):
                if c in done: continue
                done.add(c); b = builders(vm, c)
                if b: attrs.setdefault(os.path.basename(vm.idx[c][0].filename), {})[c.replace("/", ".")] = b
        top = reg or man
        if top and vm.cf(top): sup[e] = MONSTER in vm.supers(top)
    json.dump(attrs, open(W + "/attrs.json", "w"), indent=0)
    json.dump(sup, open(W + "/supers.json", "w"), indent=0)
    print(sum(map(len, attrs.values())), "classes with builders in", len(attrs), "jars;", len(sup), "of", len(IDS), "entities with a superclass chain")
    print("no class:", *[e for e in IDS if e not in sup])
    if vm.errors: print(len(vm.errors), "interpreter errors, first:", vm.errors[:3], file=sys.stderr)
