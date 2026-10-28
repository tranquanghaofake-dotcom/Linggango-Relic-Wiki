"""Read a Java entity model (vanilla LayerDefinition createBodyLayer(), or lionfishapi AdvancedModelBox built in the
constructor, as L_Ender's Cataclysm does) out of a mod jar by running its bytecode on a tiny stack machine (javap text).
Only model-building calls are understood; everything else becomes an opaque value. Output, per model:
{"tw", "th", "root": {"name", "pose": [x, y, z, rx, ry, rz], "cubes": [[x, y, z, w, h, d, grow, u, v, mirror]], "children": [...]}}
Usage: jmodel.py out.json "jar:pkg.Class[:method]" ...   (method defaults to createBodyLayer, else the constructor)"""
import json, re, subprocess, sys, tempfile, zipfile

class Op:  # value the machine does not model
    def __repr__(s): return "Op"
class Part:
    def __init__(s, name="root"):
        s.name, s.pose, s.cubes, s.kids, s.u, s.v, s.mirror = name, [0.0] * 6, [], [], 0, 0, False
    def dump(s):
        return {"name": s.name, "pose": s.pose, "cubes": s.cubes, "children": [k.dump() for k in s.kids]}
class Builder:
    def __init__(s): s.cubes, s.u, s.v, s.mirror = [], 0, 0, False
class Pose:
    def __init__(s, v): s.v = v
class Obj:
    def __init__(s, cls): s.cls, s.f, s.g = cls, {}, 0.0

def args_of(desc):
    inner = desc[desc.index("(") + 1:desc.index(")")]
    return re.findall(r"\[*(?:[ZBCSIFJD]|L[^;]+;)", inner), desc[desc.index(")") + 1:]

def run(code, this, statics, args=None):
    st, loc = [], {0: this} if this is not None else {}
    if args:  # static method arguments in locals 0..n (wide types are not used by model code)
        loc = {i: v for i, v in enumerate(args)}
    result = None
    for line in code:
        m = re.match(r"\s*\d+: (\w+)\s*(.*)", line)
        if not m: continue
        op, rest = m.groups()
        cm = re.search(r"// (.*)$", rest)
        com = cm.group(1) if cm else ""
        if op in ("ldc", "ldc_w", "ldc2_w"):
            k = re.match(r"(float|int|double|long|String) (.*)", com)
            if k.group(1) == "String": st.append(k.group(2))
            else: st.append(float(k.group(2).rstrip("fdlFDL")))
        elif re.match(r"[fid]const_m?\d|iconst_m1", op): st.append(-1.0 if op.endswith("m1") else float(op[-1]))
        elif op in ("bipush", "sipush"): st.append(float(rest.split()[0]))
        elif op == "aconst_null": st.append(None)
        elif re.match(r"[aifld]load(_\d)?$", op): st.append(loc.get(int(op[-1]) if "_" in op else int(rest.split()[0])))
        elif re.match(r"[aifld]store(_\d)?$", op): loc[int(op[-1]) if "_" in op else int(rest.split()[0])] = st.pop()
        elif op == "dup": st.append(st[-1])
        elif op == "pop": st.pop()
        elif op in ("fneg", "ineg", "dneg"): v = st.pop(); st.append(-v if isinstance(v, float) else Op())
        elif op[1:] in ("add", "sub", "mul", "div") and op[0] in "fid":
            b, a = st.pop(), st.pop()
            if isinstance(a, float) and isinstance(b, float):
                st.append({"add": a + b, "sub": a - b, "mul": a * b, "div": a / b if b else 0.0}[op[1:]])
            else: st.append(Op())
        elif op in ("i2f", "f2i", "i2d", "d2f", "f2d", "checkcast"): pass
        elif op == "new": st.append(Obj(com.split()[-1]))
        elif op == "getstatic":
            f = com.split()[1].split(":")[0]
            st.append(statics.get(f, Op()))
        elif op == "putstatic": statics[com.split()[1].split(":")[0]] = st.pop()
        elif op == "getfield": o = st.pop(); st.append(o.f.get(com.split()[1].split(":")[0], Op()) if isinstance(o, Obj) else Op())
        elif op == "putfield":
            v, o = st.pop(), st.pop()
            if isinstance(o, Obj): o.f[com.split()[1].split(":")[0]] = v
        elif op.startswith("invoke"):
            k = re.match(r"(?:Interface)?Method (?:(\S+?)\.)?(\"?<?[\w$]+>?\"?):(\S+)", com)
            if not k:  # invokedynamic and the like
                st.append(Op()); continue
            owner, name, desc = k.groups(); name = name.strip('"'); owner = owner or CTX.get("cls", ""); cls = owner.split("/")[-1]
            ats, ret = args_of(desc); a = [st.pop() for _ in ats][::-1]
            recv = st.pop() if op != "invokestatic" else None
            r = None
            if op == "invokestatic" and not owner.startswith(("net/minecraft", "java")) and re.search(r"(MeshDefinition|LayerDefinition|PartDefinition);$", ret):
                r = user(owner, name, desc, a)  # the mod's own helper (CultistModel.createMesh, createBodyLayer(float)): run it too
            if r is None: r = call(cls, name, recv, a, ats)
            if ret != "V": st.append(r)
        elif op in ("areturn", "return"):
            result = st.pop() if op == "areturn" and st else None
            break
    return result, loc

def humanoid(g, y):
    """HumanoidModel.createMesh(CubeDeformation, yOffset) of vanilla 1.20.1, which many mob models start from."""
    m = Obj("MeshDefinition"); r = m.f["root"] = Part()
    for nm, u, v, box, pose, mir, gg in (("head", 0, 0, [-4, -8, -4, 8, 8, 8], [0, 0, 0], False, g), ("hat", 32, 0, [-4, -8, -4, 8, 8, 8], [0, 0, 0], False, g + .5),
                                         ("body", 16, 16, [-4, 0, -2, 8, 12, 4], [0, 0, 0], False, g), ("right_arm", 40, 16, [-3, -2, -2, 4, 12, 4], [-5, 2, 0], False, g),
                                         ("left_arm", 40, 16, [-1, -2, -2, 4, 12, 4], [5, 2, 0], True, g), ("right_leg", 0, 16, [-2, 0, -2, 4, 12, 4], [-1.9, 12, 0], False, g),
                                         ("left_leg", 0, 16, [-2, 0, -2, 4, 12, 4], [1.9, 12, 0], True, g)):
        p = Part(nm); p.pose = [float(pose[0]), pose[1] + y, float(pose[2]), 0.0, 0.0, 0.0]; p.cubes = [[float(x) for x in box] + [gg, u, v, mir]]; r.kids.append(p)
    return m

def nums(a): return [x for x in a if isinstance(x, float)]
def call(cls, name, recv, a, ats):
    n = nums(a)
    if cls == "MeshDefinition" and name == "m_171576_":
        if not isinstance(recv, Obj): return Part()
        return recv.f.setdefault("root", Part())
    if cls == "HumanoidModel" and name == "m_170681_": return humanoid(a[0].g if isinstance(a[0], Obj) else 0.0, n[0] if n else 0.0)
    if cls == "PartDefinition" and name == "m_171599_":  # addOrReplaceChild(name, builder, pose)
        p = Part(a[0] if isinstance(a[0], str) else "?"); b, pose = a[1], a[2]
        if isinstance(b, Builder): p.cubes = b.cubes
        if isinstance(pose, Pose): p.pose = pose.v
        if isinstance(recv, Part): recv.kids = [k for k in recv.kids if k.name != p.name] + [p]
        return p
    if cls == "CubeListBuilder":
        b = recv if isinstance(recv, Builder) else Builder()
        if name == "m_171558_": return Builder()
        if name == "m_171514_": b.u, b.v = n[0], n[1]; return b
        if name in ("m_171555_",): b.mirror = bool(n[0]) if n else True; return b
        if name == "m_171480_": b.mirror = True; return b
        if len(n) >= 6:
            g = next((x.g for x in a if isinstance(x, Obj) and x.cls.endswith("CubeDeformation")), 0.0)
            u, v = (n[6], n[7]) if len(n) >= 8 else (b.u, b.v)
            mir = any(t == "Z" and x for t, x in zip(ats, a)) or b.mirror
            b.cubes.append(n[:6] + [g, u, v, bool(mir)])
        return b
    if cls == "PartPose":
        if name == "m_171419_": return Pose(n[:3] + [0.0] * 3)
        if name == "m_171423_": return Pose(n[:6])
        if name == "m_171430_": return Pose([0.0] * 3 + n[:3])
        return Pose([0.0] * 6)
    if cls == "CubeDeformation" and name == "<init>": recv.g = n[0] if n else 0.0; return None
    if cls == "CubeDeformation" and name == "m_171469_": o = Obj("CubeDeformation"); o.g = (recv.g if isinstance(recv, Obj) else 0) + n[0]; return o
    if cls == "LayerDefinition" and name == "m_171565_": return {"root": a[0].f.get("root") if isinstance(a[0], Obj) else None, "tw": n[0], "th": n[1]}
    # lionfishapi AdvancedModelBox (constructor style)
    if cls in ("AdvancedModelBox", "BasicModelPart", "ModelPart") or "ModelBox" in cls:
        if name == "<init>":
            recv.part = Part(next((x for x in a if isinstance(x, str)), "?"))
            if len(n) >= 2: recv.part.u, recv.part.v = n[-2], n[-1]
            return None
        p = getattr(recv, "part", None)
        if p is None: return recv
        if name in ("setRotationPoint", "setPos"): p.pose[:3] = n[:3]
        elif name in ("setTextureOffset", "texOffs"): p.u, p.v = n[0], n[1]
        elif name == "addChild" and a and hasattr(a[0], "part"): p.kids.append(a[0].part)
        elif name.startswith("addBox") and len(n) >= 6:
            g = n[6] if len(n) >= 7 else 0.0
            mir = any(t == "Z" and x for t, x in zip(ats, a)) or p.mirror
            p.cubes.append(n[:6] + [g, p.u, p.v, bool(mir)])
        elif name in ("setMirror",) or (name == "mirror"): p.mirror = bool(n[0]) if n else True
        return recv
    if name in ("setRotateAngle", "setRotationAngle") and a and hasattr(a[0], "part"): a[0].part.pose[3:] = n[:3]; return None
    if name in ("texWidth", "texHeight"): return None
    return Op()

CTX = {"jar": None, "depth": 0}
def javap_methods(jar, cls):
    z = zipfile.ZipFile(jar); tmp = tempfile.mkdtemp(); path = cls.replace(".", "/") + ".class"; z.extract(path, tmp)
    t = subprocess.run(["javap", "-c", "-p", "-constants", tmp + "/" + path], capture_output=True, text=True).stdout
    return re.split(r"\n\n(?=  \S)", t)
def user(owner, name, desc, a):
    if not CTX["jar"] or CTX["depth"] > 4: return None
    try: meths = javap_methods(CTX["jar"], owner)
    except KeyError: return None
    ats, _ = args_of(desc)
    for m in meths:
        head = m.strip().split("\n")[0]
        if re.search(r"\b" + re.escape(name) + r"\(", head) and "static" in head and head.count(",") + (1 if "()" not in head else 0) == len(ats):
            CTX["depth"] += 1; prev = CTX["cls"]; CTX["cls"] = owner
            try:
                r, _ = run(m.split("\n"), None, {"net/minecraft/client/model/geom/builders/CubeDeformation.f_171458_": Obj("CubeDeformation")}, list(a))
            finally: CTX["depth"] -= 1; CTX["cls"] = prev
            return r
    return None

def model(jar, cls, method=None):
    CTX["jar"] = jar; CTX["cls"] = cls.replace(".", "/")
    z = zipfile.ZipFile(jar); tmp = tempfile.mkdtemp(); path = cls.replace(".", "/") + ".class"; z.extract(path, tmp)
    t = subprocess.run(["javap", "-c", "-p", "-constants", tmp + "/" + path], capture_output=True, text=True).stdout
    meths = re.split(r"\n\n(?=  \S)", t)
    def body(pred):
        for m in meths:
            head = m.strip().split("\n")[0]
            if pred(head): return m.split("\n")
    statics = {"net/minecraft/client/model/geom/builders/CubeDeformation.f_171458_": Obj("CubeDeformation")}
    for k, v in (("net/minecraft/client/model/geom/PartPose.f_171404_", Pose([0.0] * 6)),): statics[k] = v
    b = body(lambda h: (method or "createBodyLayer") + "(" in h and "LayerDefinition" in h) if not method or method == "createBodyLayer" else body(lambda h: method + "(" in h)
    if b:
        r, _ = run(b, None, statics)
        if isinstance(r, dict) and isinstance(r.get("root"), Part): return {"tw": r["tw"], "th": r["th"], "root": r["root"].dump()}
    # constructor style: run <init>, take the part with no parent that holds the most cubes below it
    b = body(lambda h: re.search(r"\b" + re.escape(cls.split(".")[-1]) + r"\(", h) is not None)
    if not b: return None
    this = Obj(cls); run(b, this, statics)
    parts = [v.part for v in this.f.values() if hasattr(v, "part")]
    kids = {id(k) for p in parts for k in p.kids}
    roots = [p for p in parts if id(p) not in kids]
    if not roots: return None
    size = lambda p: len(p.cubes) + sum(size(k) for k in p.kids)
    tw = next((v for k, v in this.f.items() if k in ("texWidth", "f_102610_") and isinstance(v, float)), 64.0)
    th = next((v for k, v in this.f.items() if k in ("texHeight", "f_102611_") and isinstance(v, float)), 64.0)
    root = Part("root"); root.kids = roots if len(roots) > 1 else roots
    return {"tw": tw, "th": th, "root": (max(roots, key=size) if len(roots) == 1 else root).dump()}

if __name__ == "__main__":
    out = {}
    for spec in sys.argv[2:]:
        jar, cls, *m = spec.split(":")
        try: out[cls.split(".")[-1]] = model(jar, cls, m[0] if m else None)
        except Exception as e: print("FAIL", cls, e); out[cls.split(".")[-1]] = None
    json.dump(out, open(sys.argv[1], "w"))
    cnt = lambda p: len(p["cubes"]) + sum(cnt(k) for k in p["children"]) if p else 0
    for k, v in out.items(): print(k, v and (v["tw"], v["th"], cnt(v["root"])))
