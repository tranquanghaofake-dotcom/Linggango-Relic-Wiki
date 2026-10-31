"""Entity id -> entity class, read from the jars' EntityType registrations (javap -c -p -v, one JVM per jar).
Usage: reg.py W JARS_DIR [namespace,...]   (default: the namespaces of the bosses in patches/side_bosses.json and boss_extra.json)
Writes W/reg.json {jar file: {registry name: class}} (for stats.py) and W/ent_class.json {entity id: class} for the side
bosses (for renders.py). A jar is read for a namespace when its mods.toml declares that modId. Every method of a class that
names EntityType$EntityFactory is walked in order, with the lambdas it creates inlined where they are created
(DeferredRegister.register("x", () -> Builder.of(X::new, ...)), MCreator's register("x", Builder.<X>of(X::new, ...)),
a factory class's create()); a factory (a constructor reference or `new X(EntityType, Level)`) belongs to the last
registry-name string before it. A mod shipped inside another jar (META-INF/jarjar) is read once extracted into JARS_DIR:
RevelationFix, inside GoetyRevelation, registers the Ice Hermit. Not found on 2026-10-31: goety_revelation:apollyon (a reskin
drawn with Goety's ApostleModel, a PICK in renders.py) and soulsweapons:moonknight_phase_2 (drawn as Moonknight)."""
import json, sys, zipfile, subprocess, re, glob, os, pathlib, tomllib
W, JD = sys.argv[1], sys.argv[2]
H = pathlib.Path(__file__).resolve().parents[2] / "patches"
SB = json.loads((H / "side_bosses.json").read_text()); BX = json.loads((H / "boss_extra.json").read_text())
IDS = sorted({e for v in SB.values() for e in (v["entity"] if isinstance(v["entity"], list) else [v["entity"]])} | {r[6] for r in BX})
NS = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else {e.split(":")[0] for e in IDS}
FAC = "(Lnet/minecraft/world/entity/EntityType;Lnet/minecraft/world/level/Level;"
def mod_ids(z):
    try: return {m.get("modId") for m in tomllib.loads(z.read("META-INF/mods.toml").decode("utf8", "ignore")).get("mods", [])}
    except Exception: return set()
def javap(jar, classes):  # {class: text}, in batches (one JVM each)
    out = {}
    for i in range(0, len(classes), 150):
        t = subprocess.run(["javap", "-c", "-p", "-v", "-cp", jar] + classes[i:i + 150], capture_output=True, text=True).stdout
        for part in re.split(r"(?m)^(?=Classfile )", t)[1:]:
            m = re.search(r"(?m)^(?:public |final |abstract |synthetic |private |protected |static )*(?:class|interface|enum) (\S+)", part)
            if m: out[m.group(1).split("<")[0].replace(".", "/")] = part
    return out
def parse(text):  # methods {name: [code lines]}, bootstraps {index: [argument lines]}
    meths, boots, cur = {}, {}, None
    body = text[:text.find("\nBootstrapMethods:")] if "\nBootstrapMethods:" in text else text
    for line in body.split("\n"):
        m = re.match(r"  (?! )(?:.* )?([\w$.<>]+)\(.*\);$|  static \{\};$", line)
        if m: cur = meths.setdefault((m.group(1) or "<clinit>").split(".")[-1], []); continue
        if cur is not None and re.match(r"\s+\d+: ", line): cur.append(line)
    if "\nBootstrapMethods:" in text:
        for line in text[text.find("\nBootstrapMethods:") + 1:].split("\n")[1:]:
            m = re.match(r"  (\d+): ", line)
            if m: b = boots.setdefault(int(m.group(1)), []); continue
            if re.match(r"\s+#\d+ ", line): b.append(line.strip())
            elif line and not line.startswith(" "): break
    return meths, boots
def events(C, cls, meth, seen):
    """registry names ('s', name) and factories ('f', class) in the order the method makes them, lambdas inlined"""
    meths, boots = C[cls]; out = []; new = None
    if (cls, meth) in seen or meth not in meths: return out
    seen = seen | {(cls, meth)}
    for line in meths[meth]:
        com = line.split("// ", 1)[1] if "// " in line else ""
        if re.search(r": ldc", line) and com.startswith("String "):
            s = com[7:].strip()
            if re.fullmatch(r"[a-z0-9_.:/-]+", s): out.append(("s", s.split(":")[-1]))
        elif ": new " in line: new = com.split()[-1]
        elif ": invokespecial" in line and new and ('"<init>":' + FAC) in com: out.append(("f", new)); new = None
        elif ": invokedynamic" in line:
            k = re.search(r"InvokeDynamic #(\d+):", com)
            for a in boots.get(int(k.group(1)), []) if k else []:
                h = re.search(r"REF_(\w+) ([\w/$]+)\.(\"?<?[\w$]+>?\"?):(\S+)", a)
                if not h: continue
                if h.group(1) == "newInvokeSpecial" and h.group(4).startswith(FAC): out.append(("f", h.group(2)))
                elif h.group(2) in C and h.group(3).startswith("lambda$"): out += events(C, h.group(2), h.group(3), seen)
        if ": new " in line and new in C and new != cls:  # a factory class (Kotlin): its create(), m_20721_ in SRG names
            out += next((events(C, new, f, seen) for f in ("m_20721_", "create") if f in C[new][0]), [])
    return out
reg, ent = {}, {}
for j in sorted(glob.glob(JD + "/*.jar")):
    try: z = zipfile.ZipFile(j)
    except Exception: continue
    ids = mod_ids(z) & NS
    if not ids: continue
    cs = [n[:-6] for n in z.namelist() if n.endswith(".class") and b"EntityType$EntityFactory" in z.read(n)]
    C = {c: parse(t) for c, t in javap(j, cs).items()}
    R = reg.setdefault(os.path.basename(j), {})
    for c in C:
        for m in C[c][0]:
            if m.startswith("lambda$"): continue
            last = None
            for kind, v in events(C, c, m, frozenset()):
                if kind == "s": last = v
                elif last: R.setdefault(last, v.replace("/", ".")); last = None
    for e in IDS:
        ns, p = e.split(":")
        if ns in ids and p in R: ent.setdefault(e, R[p])
json.dump(reg, open(W + "/reg.json", "w"), indent=0)
json.dump(ent, open(W + "/ent_class.json", "w"), indent=0)
print(len(ent), "of", len(IDS), "side-boss entities;", sum(map(len, reg.values())), "registrations in", len(reg), "jars")
print("not found:", *[e for e in IDS if e not in ent])
