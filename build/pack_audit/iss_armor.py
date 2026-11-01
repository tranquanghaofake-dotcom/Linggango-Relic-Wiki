"""Iron's Spellbooks armor materials (additional attributes per piece) from ExtendedArmorMaterials.<clinit>, read from the jar
through build/gear/classlib.py (no javap).
Usage: iss_armor.py ISS_JAR [--gear-stats SRG_JAR]
  writes iss_mats.json in the current folder: {MATERIAL: [[attribute, amount, operation], ...]} in constructor order; an ISS
  attribute is its AttributeRegistry field in lower case, a vanilla one 'vanilla:<SRG field>'.
  --gear-stats also rewrites "iss_materials" of build/patches/gear_stats.json: {MATERIAL: {attribute: [addition, multiplier]}}
  for the materials "iss_item_material" names, vanilla attributes named from the SRG jar (Forge's server-1.20.1-*-srg.jar).
Each enum constant starts at `new ExtendedArmorMaterials`, its name is the first String after it; a modifier is an attribute
(a getstatic of AttributeRegistry or Attributes), then its amount (a double), then its Operation."""
import json, os, re, sys, pathlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gear"))
import classlib

CLS = "io/redspace/ironsspellbooks/item/armor/ExtendedArmorMaterials"
ATTRS = "net/minecraft/world/entity/ai/attributes/Attributes"

def materials(jar):
    k = classlib.ClassPath([jar]).cf(CLS)
    ins, _ = classlib.code(k, classlib.method(k, "<clinit>"))
    mats = {}; cur = None; first = False; attr = pend = None
    for x in ins:
        mn = x.mnemonic
        if mn == "new" and classlib.class_name(k, x.operands[0].value) == CLS: cur = None; first = True; continue
        if mn in ("ldc", "ldc_w") and first:
            t, v = classlib.const(k, x.operands[0].value)
            if t == "S" and re.fullmatch(r"[A-Z][A-Z_]+", v): cur = v; mats[cur] = []; first = False
            continue
        if cur is None: continue
        if mn == "getstatic":
            owner, name, _ = classlib.ref(k, x.operands[0].value)
            if owner.endswith("/AttributeRegistry"): attr = name.lower()
            elif owner == ATTRS: attr = "vanilla:" + name
            elif owner.endswith("AttributeModifier$Operation") and attr is not None and pend is not None:
                mats[cur].append((attr, pend, name)); attr = pend = None
        elif mn == "ldc2_w":
            t, v = classlib.const(k, x.operands[0].value)
            if t == "D": pend = v
        elif mn in ("dconst_0", "dconst_1"): pend = float(mn[-1])
    return mats

def vanilla_names(srg):
    """Attributes SRG field -> name without 'generic.' (f_22281_ -> attack_damage), from Attributes.<clinit>"""
    k = classlib.ClassPath([srg]).cf(ATTRS); ins, _ = classlib.code(k, classlib.method(k, "<clinit>")); out = {}; last = None
    for x in ins:
        if x.mnemonic in ("ldc", "ldc_w"):
            t, v = classlib.const(k, x.operands[0].value)
            if t == "S" and v.startswith("generic."): last = v
        elif x.mnemonic == "putstatic" and last:
            out[classlib.ref(k, x.operands[0].value)[1]] = last[len("generic."):]; last = None
    return out

def gear_stats(mats, srg, path):
    d = json.loads(path.read_text(encoding="utf-8")); van = vanilla_names(srg); out = {}
    for mat in sorted(set(d["iss_item_material"].values()), key=list(mats).index):
        e = out[mat] = {}
        for a, v, op in mats[mat]:
            if a.startswith("vanilla:"):
                f = a[len("vanilla:"):]
                if f not in van: sys.exit("iss_armor.py: %s.%s has no generic.* name in the SRG jar" % (ATTRS, f))
                a = van[f]
            s = e.setdefault(a, [0.0, 0.0]); s[0 if op == "ADDITION" else 1] += v
    d["iss_materials"] = out
    path.write_text(json.dumps(d, indent=1), encoding="utf-8")
    print("wrote", len(out), "materials to", path)

if __name__ == "__main__":
    a = sys.argv[1:]
    mats = materials(a[0])
    for k, v in mats.items(): print(k, v)
    json.dump(mats, open("iss_mats.json", "w"))
    if "--gear-stats" in a:
        gear_stats(mats, a[a.index("--gear-stats") + 1], pathlib.Path(__file__).resolve().parents[1] / "patches" / "gear_stats.json")
