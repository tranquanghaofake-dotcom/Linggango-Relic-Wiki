"""Bytecode tests for the class layer and the tools that read mod classes: a hand tool, not a CI gate (docs/AGENT_TOOLS.md).
Usage: python3 build/tests/bytecode/run.py [--bench] [SET ...]      (exit 1 when a check fails)
Needs javac (JDK 17 or later; classes are compiled for 17, the game's level) and jawa. Each folder here is one set of Java
sources; it compiles into a temporary folder and its own classes go into a jar, while the stand-ins for game and library
classes (net/, com/) stay out of it, as the real game classes are absent from a mod jar.
Sets: classlib (build/gear/classlib.py: descriptors, typed constants, bootstrap methods, supers, interfaces, method lookup,
services, mods.toml, first jar wins), ops / ints / more_ops / armor / items (build/gear/mjvm.py: number semantics, switches,
string concatenation, lambdas, enum switches, item registration and attribute modifiers), config (mjvm's pack config
lookup, plain files), jmodel (pack_audit/side_bosses/jmodel.py: model parts), gear_fx (pack_audit/gear_fx.py: on-hit
effects), bench (mjvm steps per second, only with --bench). The expected values are what the JVM computes; jmodel's and
gear_fx's are their outputs on 2026-11-01, checked against the sources by hand."""
import os, sys, glob, shutil, struct, subprocess, tempfile, zipfile, time

HERE = os.path.dirname(os.path.abspath(__file__)); BUILD = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(BUILD, "gear"))
import classlib, mjvm

f32 = lambda x: struct.unpack(">f", struct.pack(">f", x))[0]
TMP = tempfile.mkdtemp(prefix="bytecode_tests_")
FAIL = []

def check(name, got, want):
    ok = got == want and type(got) == type(want)
    if not ok: FAIL.append(name)
    print("%-5s %-28s got=%r%s" % ("OK" if ok else "WRONG", name, got, "" if ok else "  want=%r" % (want,)))

def jar(set_name):
    """compile the set; returns the path of a jar with its own classes (not net/ or com/)"""
    src = os.path.join(HERE, set_name); out = os.path.join(TMP, set_name); os.makedirs(out, exist_ok=True)
    files = sorted(glob.glob(src + "/**/*.java", recursive=True))
    r = subprocess.run(["javac", "--release", "17", "-nowarn", "-d", out] + files, capture_output=True, text=True)
    if r.returncode: sys.exit("javac failed for %s:\n%s" % (set_name, r.stderr))
    p = os.path.join(TMP, set_name + ".jar")
    with zipfile.ZipFile(p, "w") as z:
        for f in sorted(glob.glob(out + "/**/*.class", recursive=True)):
            n = os.path.relpath(f, out).replace(os.sep, "/")
            if not n.startswith(("net/", "com/")): z.write(f, n)
    return p

def run(vm, cls, name, args):
    k = vm.cf(cls); m = next(x for x in k.methods if x.name.value == name)
    try: return vm.run(cls, k, m, list(args))
    except Exception as e: return "EXC %r" % e

# ---------------------------------------------------------------- sets
def t_classlib():
    j = jar("classlib")
    d = classlib.desc("(IJ[Ljava/lang/String;D)J")
    check("desc args", d.args, ["I", "J", "[Ljava/lang/String;", "D"]); check("desc kinds", d.kinds, "IJAD")
    check("desc slots", d.slots, 6); check("desc ret", d.ret, "J"); check("argc", classlib.argc("([[I[Lx;Z)V"), 3)
    cp = classlib.ClassPath([j]); k = cp.cf("c/Leaf")
    check("supers", cp.supers("c/Leaf"), ["c/Leaf", "c/Base", "java/lang/Object"])
    check("interfaces", cp.interfaces("c/Leaf"), ["java/lang/Runnable", "c/Tagged", "c/Named"])
    r = cp.find_method("c/Leaf", "name", "()Ljava/lang/String;"); check("find_method default", r and r[0], "c/Named")
    check("find_method missing", cp.find_method("c/Leaf", "nope"), None)
    m = classlib.method(k, "slots"); check("method desc", m.descriptor.value, "(IJ[Ljava/lang/String;D)J")
    consts = [classlib.const(k, x.operands[0].value) for x in classlib.code(k, classlib.method(k, "<clinit>"))[0]
              if x.mnemonic in ("ldc", "ldc_w", "ldc2_w")]
    check("const float", consts[0], ("F", f32(0.1))); check("const long", consts[1], ("J", 1 << 40))
    ldc = [x for x in classlib.code(k, classlib.method(k, "k"))[0] if x.mnemonic.startswith("ldc")][0]
    t, v = classlib.const(k, ldc.operands[0].value); check("const class", (t, v.name), ("C", "c/Leaf"))
    idy = [x for x in classlib.code(k, classlib.method(k, "mk"))[0] if x.mnemonic == "invokedynamic"][0]
    name, dsc, bsm, args = classlib.bootstrap(k, idy.operands[0].value)
    check("bootstrap", (name, dsc, bsm.owner, bsm.name), ("get", "()Ljava/util/function/Supplier;", "java/lang/invoke/LambdaMetafactory", "metafactory"))
    h = args[1][1]; check("bootstrap handle", (args[1][0], h.kind, h.owner, h.name, h.desc), ("H", 8, "c/Leaf", "<init>", "()V"))
    check("strings", "named" in classlib.strings(cp.cf("c/Named")), True)
    check("class_refs", "c/Leaf" in classlib.class_refs(k), True)
    check("field_refs", ("c/Leaf", "F", "F") in classlib.field_refs(k), True)
    check("method_refs", ("c/Base", "<init>", "()V") in classlib.method_refs(k), True)
    # a second jar that sorts first, holding another c/Leaf, a service file and a mods.toml
    z2 = os.path.join(TMP, "a_svc.jar"); zj = zipfile.ZipFile(j)
    with zipfile.ZipFile(z2, "w") as z:
        z.writestr("c/Leaf.class", zj.read("c/Base.class"))
        z.writestr("META-INF/services/c.Named", "# the implementation\nc.Leaf\n")
        z.writestr("META-INF/mods.toml", 'modLoader="javafml"\n[[mods]]\nmodId="testmod"\n')
    check("sorted, first wins", classlib.ClassPath([j, z2]).jar("c/Leaf"), z2)
    cp2 = classlib.ClassPath([j, z2], sort=False); check("given order", cp2.jar("c/Leaf"), j)
    check("over", classlib.ClassPath([j, z2]).over([cp2.zips[0][1]]).jar("c/Leaf"), j)
    check("services", cp2.services("c/Named"), ["c/Leaf"]); check("mod_ids", classlib.mod_ids(z2), {"testmod"})
    check("mod_ids none", classlib.mod_ids(j), set())
    vm = mjvm.VM([j]); o = vm.call_lam(run(vm, "c/Leaf", "mk", []), [])
    check("mjvm X::new", type(o).__name__ + ":" + o.cls, "Obj:c/Leaf")

def t_ops():
    vm = mjvm.VM([jar("ops")])
    for name, args, want in [("dec", [], 9), ("sub3", [], 7), ("widesub", [], -200), ("f2i", [], 7), ("f2i2", [], 9), ("rem", [], -1),
            ("arr", [], 10), ("arrinc", [], 7), ("dbl", [4, 1.5, 2], 9.0), ("sw", ["a"], 1), ("sw", ["bb"], 2), ("sw", ["zz"], 0),
            ("tsw", [2], 20), ("cat", [f32(0.1), 3], "x0.1_3"), ("i2b", [], -56), ("fl", [], f32(f32(0.1) * 3)), ("loopsum", [], 6),
            ("down", [], 6), ("lshift", [], 1 << 40), ("idiv", [], -3), ("cmpd", [], 1), ("deflt", [], 5), ("en", [], 105),
            ("enumsw2", [], 2), ("dsum", [], 4.0)]:
        check("ops." + name + (repr(args) if name == "sw" else ""), run(vm, "t/T", name, args), want)

def t_ints():
    vm = mjvm.VM([jar("ints")])
    for name, want in (("sat", 2147483647), ("shl", -2147483648), ("ovf", -2147483648), ("m1", -2147483644)):
        check("ints." + name, run(vm, "t/U", name, []), want)

def t_more_ops():
    vm = mjvm.VM([jar("more_ops")])
    TY = mjvm.EnumC("net/minecraft/world/item/ArmorItem$Type", "CHESTPLATE", -1)
    for name, args, want in [("sd", [], 7.0), ("fld", [], 3.5), ("fld2", [], 506), ("expr", [], 11.0), ("lmix", [3, 4, 2.9], 14),
            ("call", [], 17.0), ("cmpl", [], 1), ("cat2", [7], "item_7_x"), ("cat3", [7], "a\x01b7"), ("lam", [], 4.5),
            ("usw", [mjvm.OP], -1), ("usw", [5], 50), ("tsw", [TY], 8), ("tsw2", [], 6), ("dneg", [], -3.75), ("lshr", [], -4 + 15),
            ("fdiv", [], 35), ("ldiv", [], -2333333333333333333 + -2), ("drem", [], -1.5), ("i2c", [], 65535), ("sh", [], 4464 + 127)]:
        check("more_ops." + name + (repr(args) if name == "usw" else ""), run(vm, "t/W2", name, args), want)
    real = vm.getstatic  # an exception inside the interpreter is recorded where it was raised
    def bad(c, n, d):
        if c == "t/W3": raise TypeError("boom")
        return real(c, n, d)
    vm.getstatic = bad; run(vm, "t/W2", "boom", [])
    check("more_ops.errors", vm.errors, [("t/W2", "boom", 0, "TypeError('boom')")])

def t_armor():
    mjvm.EQF.update({n: n for n in mjvm.EQS})  # srg_tables() fills this from the srg jar
    vm = mjvm.VM([jar("armor")]); CH = mjvm.EnumC("net/minecraft/world/entity/EquipmentSlot", "CHEST", mjvm.EQS.index("CHEST"))
    for name, args, want in (("prot", [CH], 8), ("protIf", [CH], 8), ("dmg", [], 14.0)): check("armor." + name, run(vm, "mod/A", name, args), want)

def t_items():
    mjvm.EQF.update({n: n for n in mjvm.EQS})
    vm = mjvm.VM([jar("items")]); vm.attrname = {"f_22281_": "generic.attack_damage", "f_22283_": "generic.attack_speed"}
    vm.clinit("mod/ModItems"); got = {}
    for name, val in vm.regs:
        o = vm.resolve(val)
        if not isinstance(o, mjvm.Obj): continue
        mods = []
        r = vm.find(o.cls, "m_7167_", "(Lnet/minecraft/world/entity/EquipmentSlot;)Lcom/google/common/collect/Multimap;")
        if r and not r[0].startswith("net/minecraft"):
            mm = vm.run(r[0], r[1], r[2], [o, mjvm.EnumC("net/minecraft/world/entity/EquipmentSlot", "MAINHAND", 0)])
            mods = [(k.n, v.f.get("amt"), str(v.f.get("op"))) for k, v in getattr(mm, "items", [])]
        got[name] = ({k: v for k, v in o.gear.items() if k in ("k", "dmg", "spd")}, {k: v for k, v in o.f.items() if k in ("reach", "bonus", "seed")}, mods)
    check("items.katana", got.get("katana"), ({"k": "sword", "dmg": 6.0, "spd": f32(-2.4)}, {"reach": 1.5}, []))
    check("items.ring", got.get("ring"), ({}, {"seed": 12345678901, "bonus": 5.0}, [("generic.attack_damage", 7.5, "A(AttributeModifier$Operation.ADDITION)"),
                                               ("generic.attack_speed", -0.1, "A(AttributeModifier$Operation.MULTIPLY_BASE)")]))
    check("items.errors", vm.errors, [])

def t_config():
    d = os.path.join(TMP, "config"); shutil.copytree(os.path.join(HERE, "config"), d)
    import io, contextlib
    with contextlib.redirect_stderr(io.StringIO()): mjvm.load_cfg(d)  # broken.toml is meant not to parse
    for ns, key, dflt, want, path in [("too", "bow_damage", 1.0, 6, None),  # 'too' (too_many_bows) is not mekanismtools
            ("simplyswords", "katana_damage", 1.0, 9.0, None), ("simplyswords", "katana_damage", 1.0, 9.0, "weapons.katana_damage"),
            ("simplyswords", "enabled", 1, 0, None),  # a boolean option read from the pack
            ("simplyswords", "enabled", 2.5, 2.5, None),  # a bool never stands for a number
            ("simplyswords", "level", 1, 3, None), ("", "y", 1.0, 2.5, None), ("enigma", "Flag", 0, 1, None), ("enigma", "Dmg", 1.0, 8.0, None)]:
        mjvm.CFG_NS[0] = ns; check("config.%s/%s(%r)%s" % (ns, key, dflt, "@path" if path else ""), mjvm.cfg_get(key, dflt, path), want)
    check("config.unparsed", [os.path.basename(f) for f, _ in mjvm.CFG_ERR], ["broken.toml"])

def t_jmodel():
    sys.path.insert(0, os.path.join(BUILD, "pack_audit", "side_bosses")); import jmodel
    j = jar("jmodel")
    def tree(r):
        out = ["%s %s" % (r["tw"], r["th"])]
        def show(p, d=0):
            out.append("%s%s %s %s" % ("  " * d, p["name"], [round(x, 3) for x in p["pose"]], p["cubes"]))
            for c in p["children"]: show(c, d + 1)
        show(r["root"]); return "\n".join(out)
    check("jmodel.Boss", tree(jmodel.model(j, "m.Boss")), "\n".join([
        "64.0 32.0", "root [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] []",
        "  body [0.0, 12.0, 0.0, 0.0, 0.0, 0.0] [[-4.0, 0.0, -2.0, 8.0, 12.0, 4.0, 0.0, 0.0, 0.0, False]]",
        "    leg0 [-3.0, 6.0, 0.0, 0.0, 0.0, 0.0] [[-1.0, 0.0, -1.0, 2.0, 6.0, 2.0, 0.0, 0.0, 16.0, False]]",
        "  tail [0.0, 10.0, 2.0, 0.524, 0.0, 0.5] [[-1.0, 0.0, 0.0, 2.0, 2.0, 6.0, 0.0, 0, 0, False]]",
        "  neck [0.0, 4.0, 0.0, 0.0, 0.0, 0.0] [[-1.0, -1.0, -1.0, 1.0, 2.0, 2.0, 0.0, 0, 0, False]]"]))
    check("jmodel.Boss unknown", jmodel.CTX.get("unk"), 0)
    check("jmodel.Boss2", tree(jmodel.model(j, "m.Boss2")), "\n".join([
        "32.0 32.0", "root [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] []",
        "  arm [0.0, 5.0, 1.0, 0.0, 0.0, 0.0] [[-1.0, 0.0, -1.0, 2.0, 8.0, 2.0, 0.0, 0, 0, False]]",
        "  rem [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] [[1.0, -1.0, -3.0, 1.0, 1.0, 1.0, 0.0, 0, 0, False]]"]))
    check("jmodel.Boss2 unknown", jmodel.CTX.get("unk"), 1)

def t_gear_fx():
    jd = os.path.join(TMP, "gear_fx_jars"); os.makedirs(jd, exist_ok=True); shutil.copy(jar("gear_fx"), jd)
    mp = os.path.join(TMP, "srg.json"); open(mp, "w").write("{}")
    gf = os.path.join(BUILD, "pack_audit", "gear_fx.py")  # its functions only: the tail reads the wiki's gear table and writes gear_fx.json
    src = open(gf).read(); src = src[:src.index("res, n_fx, n_tip = {}, 0, 0")]
    src = src.replace('s = (H / "src" / "gear_data.js").read_text(encoding="utf-8"); GE, _ = json.JSONDecoder().raw_decode(s, s.index("[", s.index("GE=")))', "GE = []")
    argv = sys.argv; sys.argv = ["gear_fx", jd, mp]; ns = {"__file__": gf}
    try: exec(compile(src, "gear_fx", "exec"), ns)
    finally: sys.argv = argv
    ns["SRG"].update({"f_19614_": "net.minecraft.world.effect.MobEffects.POISON", "f_19615_": "net.minecraft.world.effect.MobEffects.WITHER",
                      "f_19597_": "net.minecraft.world.effect.MobEffects.MOVEMENT_SLOWDOWN"})
    fx = lambda c: [{k: v for k, v in r.items() if k != "when"} for r in ns["item_fx"]([c], "fx")]
    E = lambda who, e, t, l, ch=None: dict(who=who, effect="minecraft:" + e, ticks=t, level=l, **({} if ch is None else {"chance": ch}))
    check("gear_fx.Blade", fx("Blade"), [E("target", "poison", 100, 2, 0.2), E("target", "wither", 60, 1), E("target", "slowness", None, 3),
                                         E("target", "slowness", None, 2)])
    check("gear_fx.Blade2", fx("Blade2"), [E("target", "poison", 100, 2, 0.25), E("target", "wither", 40, 1, 0.75), E("self", "slowness", 20, 1, 0.1),
                                           E("target", "wither", 100, 3), E("target", "poison", None, 1), E("target", "slowness", 60, 2, 0.5)])

def t_bench():
    vm = mjvm.VM([jar("bench")]); vm.fsteps = 10 ** 8; k = vm.cf("t/B"); m = classlib.method(k, "bench")
    t = time.time(); v = vm.run("t/B", k, m, []); dt = time.time() - t
    check("bench.result", v, -2146883654); print("      %d steps in %.2f s, %.0f steps/s" % (vm.steps, dt, vm.steps / dt))

SETS = {"classlib": t_classlib, "ops": t_ops, "ints": t_ints, "more_ops": t_more_ops, "armor": t_armor, "items": t_items,
        "config": t_config, "jmodel": t_jmodel, "gear_fx": t_gear_fx, "bench": t_bench}

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")] or [s for s in SETS if s != "bench" or "--bench" in sys.argv]
    try:
        for s in want: print("== " + s); SETS[s]()
    finally: shutil.rmtree(TMP, ignore_errors=True)
    print("%s: %d failed%s" % ("FAIL" if FAIL else "all green", len(FAIL), (": " + ", ".join(FAIL)) if FAIL else ""))
    sys.exit(1 if FAIL else 0)
