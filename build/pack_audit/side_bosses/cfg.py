"""Mod config defaults the side-boss stats need, read from the jars on build/gear/mjvm.py's VM (the mods' own code, not the pack).
Usage: cfg.py W JARS_DIR   writes W/cfg.json {ConfigSimpleName: {field: number}} for stats.py.
A config class is looked up by its simple name in the jar whose mods.toml declares the mod id CLASSES gives (simple names collide
across jars: BossConfig is in fdbosses, Soulslike Weaponry and Dungeon Now Loading). Its <clinit> runs, so a ForgeConfigSpec
field holds define*(key, default ...) and reads as that default; plain static fields (Soulslike's MidnightConfig) read as
assigned; a class with a no-argument constructor (BoMD's and fdbosses' config objects) is also constructed and its instance
fields read. No pack config is loaded (mjvm.load_cfg is not called): these are the mods' defaults, stats.py lays the pack's
values over them. attrs.py tags reads of these classes in attribute builders as "<SimpleName>.<field>"."""
import json, sys, os, glob, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "gear"))
import mjvm
from classlib import mod_ids

# simple name -> mod id of the jar that holds it
CLASSES = {"AttributesConfig": "goety", "BossConfig": "soulsweapons", "GauntletConfig": "bosses_of_mass_destruction",
           "LichConfig": "bosses_of_mass_destruction", "ObsidilithConfig": "bosses_of_mass_destruction",
           "VoidBlossomConfig": "bosses_of_mass_destruction", "MalkuthConfig": "fdbosses", "ChesedConfig": "fdbosses",
           "ModConfig": "goety_revelation"}

def jars_by_mod(jd):
    """mod id -> [jar paths], jars in name order"""
    out = {}
    for j in sorted(glob.glob(jd + "/*.jar")):
        try: z = zipfile.ZipFile(j)
        except Exception: continue
        for i in mod_ids(z): out.setdefault(i, []).append(j)
    return out

def find_classes(jd, table=CLASSES):
    """simple name -> (jar, internal class name)"""
    by = jars_by_mod(jd); out = {}
    for simple, mod in table.items():
        for j in by.get(mod, []):
            hit = sorted(n[:-6] for n in zipfile.ZipFile(j).namelist() if n.endswith("/" + simple + ".class"))
            if hit: out[simple] = (j, hit[0]); break
    return out

def value(v):
    if isinstance(v, mjvm.CfgVal): v = v.dflt
    return v if mjvm.num(v) else None

def read(vm, cls):
    vm.clinit(cls); r = {}
    k = vm.cf(cls)
    for f in k.fields:
        n = f.name.value
        if f.access_flags.get("acc_static") and value(vm.statics.get((cls, n))) is not None: r[n] = value(vm.statics[(cls, n)])
    if vm.find(cls, "<init>", "()V") and any(not f.access_flags.get("acc_static") for f in k.fields):
        o = vm.construct(cls, "()V", [])
        for n, v in o.f.items():
            if value(v) is not None: r.setdefault(n, value(v))
    return r

if __name__ == "__main__":
    W, JD = sys.argv[1], sys.argv[2]
    found = find_classes(JD); out = {}
    for simple in CLASSES:
        if simple not in found: sys.exit("cfg.py: %s not found in the %s jar" % (simple, CLASSES[simple]))
        j, cls = found[simple]
        vm = mjvm.VM([j])
        out[simple] = read(vm, cls)
        if vm.errors: print(simple, "interpreter errors:", vm.errors[:3], file=sys.stderr)
        print(simple, os.path.basename(j), len(out[simple]), "values")
    json.dump(out, open(W + "/cfg.json", "w"), indent=0)
