"""Read a Java entity model (vanilla LayerDefinition createBodyLayer(), or parts built in the constructor: lionfishapi and
citadel AdvancedModelBox as L_Ender's Cataclysm and Alex's Caves do, llibrary AdvancedModelRenderer as Mowzie's Mobs does)
out of a mod jar by running its bytecode on a tiny stack machine (javap text).
Only model-building calls are understood; everything else becomes an opaque value. Output, per model:
{"tw", "th", "root": {"name", "pose": [x, y, z, rx, ry, rz], "cubes": [[x, y, z, w, h, d, grow, u, v, mirror]], "children": [...]}}
Usage: jmodel.py out.json "jar:pkg.Class[:method]" ...   (method defaults to createBodyLayer, else the constructor)
Building runs the code top to bottom once (a loop body once, both sides of an if); arguments are read by their place in the
descriptor, and one the machine could not work out reads 0 and is counted in CTX["unk"]. model(..., follow=True) builds following
branches instead (Mutant Enderman's arms: ternaries on constant arguments), and model(..., rest=...) poses the model at rest:
its setupAnim (and the parent classes' and helpers' code it calls, found through CTX["cp"]) runs following branches with the
entity standing still (Rest), or a vanilla idle animation is applied at time 0 (keyframes, animate). A branch whose condition
is not known skips forward (counted in CTX["ub"]). One interpreter for mjvm.py and this (javap text here, jawa there) would
belong in a shared class-reading layer."""
import json, math, re, subprocess, sys, tempfile, zipfile

class Op:  # value the machine does not model
    def __repr__(s): return "Op"
class Part:
    def __init__(s, name="root"):
        s.name, s.pose, s.cubes, s.kids, s.u, s.v, s.mirror, s.hide = name, [0.0] * 6, [], [], 0, 0, False, None
    def dump(s):  # hide: "all" (visible / showModel false: the part and its children), "self" (llibrary isHidden: its own boxes)
        if s.hide == "all": return None
        d = {"name": s.name, "pose": s.pose, "cubes": [] if s.hide == "self" else s.cubes, "children": [d for d in (k.dump() for k in s.kids) if d]}
        if getattr(s, "scale", None): d["scale"] = s.scale
        return d
class Builder:
    def __init__(s): s.cubes, s.u, s.v, s.mirror = [], 0, 0, False
class Pose:
    def __init__(s, v): s.v = v
class Obj:
    def __init__(s, cls): s.cls, s.f, s.g = cls, {}, 0.0

def args_of(desc):
    inner = desc[desc.index("(") + 1:desc.index(")")]
    return re.findall(r"\[*(?:[ZBCSIFJD]|L[^;]+;)", inner), desc[desc.index(")") + 1:]

class Rest(Obj):
    """the entity, or something it holds, standing still (for a model's setupAnim): numbers 0, flags false, no animation
    playing, held objects null; `over` sets named getters or fields (the Ferrous Wroughtnaut's isActive), `chain` its classes"""
    def __init__(s, cls="rest", over=None, chain=()): super().__init__(cls); s.over, s.chain = over or {}, set(chain)
NOANIM = Obj("NO_ANIMATION")  # what getAnimation() returns at rest; IAnimatedEntity.NO_ANIMATION is the same object
CMP = {"eq": lambda a, b: a == b, "ne": lambda a, b: a != b, "lt": lambda a, b: a < b, "ge": lambda a, b: a >= b, "gt": lambda a, b: a > b, "le": lambda a, b: a <= b}
def same(a, b):  # if_acmp: identity when both are known, else None
    if a is b: return True
    if isinstance(a, Op) and isinstance(b, Op): return None
    if NOANIM in (a, b) or a is None or b is None or (isinstance(a, Obj) and isinstance(b, Obj)): return False
    return None
def frame(vals, ats, this=None):  # arguments into local slots (long and double take two)
    loc, i = ({0: this}, 1) if this is not None else ({}, 0)
    for t, v in zip(ats, vals): loc[i] = v; i += 2 if t in ("J", "D") else 1
    return loc

def run(code, this, statics, args=None, follow=False, loc=None):
    """follow=False: every instruction once, top to bottom (model building). follow=True (a pose: setupAnim at rest): branches
    are taken when their condition is known; an unknown one skips forward (an `if` body is left out) and does not loop back"""
    st = []
    if loc is None:
        loc = {0: this} if this is not None else {}
        if args:  # static method arguments in locals 0..n (wide types are not used by model code)
            loc = {i: v for i, v in enumerate(args)}
    result = None
    L, sw = [], {}
    for i, line in enumerate(code):
        m = re.match(r"\s*(\d+): ([a-z]\w*)\s*(.*)", line)
        if not m: continue
        L.append((int(m.group(1)), m.group(2), m.group(3)))
        if follow and m.group(2) in ("tableswitch", "lookupswitch"):
            t = sw[int(m.group(1))] = {}
            for l2 in code[i + 1:]:
                k = re.match(r"\s*(-?\d+|default): (\d+)", l2)
                if k: t[k.group(1)] = int(k.group(2))
                if "}" in l2: break
    at = {o: i for i, (o, _, _) in enumerate(L)}; pc = back = 0
    while pc < len(L):
        off, op, rest = L[pc]; pc += 1
        cm = re.search(r"// (.*)$", rest)
        com = cm.group(1) if cm else ""
        if follow:
            if op.startswith(("if", "goto")):
                tgt = int(rest.split()[0])
                if op.startswith("goto"): c = True
                elif op in ("ifnull", "ifnonnull"): v = st.pop(); c = None if isinstance(v, Op) else (v is None) == (op == "ifnull")
                elif op.startswith("if_acmp"): b, a = st.pop(), st.pop(); c = same(a, b); c = None if c is None else c == (op == "if_acmpeq")
                elif op.startswith("if_icmp"): b, a = st.pop(), st.pop(); c = CMP[op[7:]](a, b) if isinstance(a, float) and isinstance(b, float) else None
                else: v = st.pop(); c = CMP[op[2:]](v, 0.0) if isinstance(v, float) else None
                if c is None: c = tgt > off; CTX["ub"] = CTX.get("ub", 0) + 1  # counted: branches decided by the rule, not the code
                if c:
                    if tgt <= off:
                        back += 1
                        if back > 4000: CTX["loops"] = CTX.get("loops", 0) + 1; break
                    pc = at[tgt]
                continue
            if op in ("tableswitch", "lookupswitch"):
                v = st.pop(); t = sw.get(off, {}); tgt = t.get(str(int(v)), t.get("default")) if isinstance(v, float) else t.get("default")
                if tgt is not None: pc = at[tgt]
                continue
            if op in ("fcmpl", "fcmpg", "dcmpl", "dcmpg", "lcmp"):
                b, a = st.pop(), st.pop(); st.append(float((a > b) - (a < b)) if isinstance(a, float) and isinstance(b, float) else Op()); continue
            if op in ("f2i", "d2i", "f2l", "d2l"):
                v = st.pop(); st.append(float(math.trunc(v)) if isinstance(v, float) and math.isfinite(v) else v); continue
            if op == "iinc":
                k = re.match(r"(\d+),\s*(-?\d+)", rest); i = int(k.group(1)); v = loc.get(i)
                loc[i] = v + float(k.group(2)) if isinstance(v, float) else Op(); continue
            if op in ("ireturn", "freturn", "dreturn", "lreturn"): result = st.pop() if st else None; break
            if op == "athrow": break
            if op in ("dup_x1", "dup_x2"):
                v = [st.pop() for _ in range(2 if op == "dup_x1" else 3)]; st += [v[0]] + v[::-1]; continue
            if op == "swap": st[-1], st[-2] = st[-2], st[-1]; continue
            if op == "instanceof":
                o = st.pop(); c = com.split()[-1].replace("/", ".")
                st.append((1.0 if c in o.chain else 0.0) if isinstance(o, Rest) and o.chain else 0.0 if o is None else Op()); continue
            if op in ("monitorenter", "monitorexit"): st.pop(); continue
            if op in ("iand", "ior", "ixor", "ishl", "ishr", "iushr", "land", "lor", "lxor", "lshl", "lshr", "lushr"):
                b, a = st.pop(), st.pop()
                if isinstance(a, float) and isinstance(b, float):
                    a, b = int(a), int(b); o = op[1:]
                    st.append(float(a & b if o == "and" else a | b if o == "or" else a ^ b if o == "xor" else a << (b & 63) if o == "shl" else a >> (b & 63)))
                else: st.append(Op())
                continue
        if op in ("ldc", "ldc_w", "ldc2_w"):
            k = re.match(r"(float|int|double|long|String) (.*)", com)
            if not k: st.append(Op())  # a class literal, a method handle
            elif k.group(1) == "String": st.append(k.group(2))
            else: st.append(float(k.group(2).rstrip("fdlFDL")))
        elif re.match(r"[fid]const_m?\d|iconst_m1", op): st.append(-1.0 if op.endswith("m1") else float(op[-1]))
        elif op in ("bipush", "sipush"): st.append(float(rest.split()[0]))
        elif op == "aconst_null": st.append(None)
        elif re.match(r"[aifld]load(_\d)?$", op): st.append(loc.get(int(op[-1]) if "_" in op else int(rest.split()[0])))
        elif re.match(r"[aifld]store(_\d)?$", op): loc[int(op[-1]) if "_" in op else int(rest.split()[0])] = st.pop()
        elif op == "dup": st.append(st[-1])
        elif op == "pop": st.pop()
        elif op in ("anewarray", "newarray"):  # arrays (a Keyframe[] in an animation, a part list)
            n = st.pop(); st.append([0.0 if op == "newarray" else None] * int(n) if isinstance(n, float) and 0 <= n < 4096 else Op())
        elif op[1:] == "astore" and len(op) == 7:
            v, i, arr = st.pop(), st.pop(), st.pop()
            if isinstance(arr, list) and isinstance(i, float) and 0 <= i < len(arr): arr[int(i)] = v
        elif op[1:] == "aload" and len(op) == 6:
            i, arr = st.pop(), st.pop(); st.append(arr[int(i)] if isinstance(arr, list) and isinstance(i, float) and 0 <= i < len(arr) else Op())
        elif op == "arraylength": arr = st.pop(); st.append(float(len(arr)) if isinstance(arr, list) else Op())
        elif op in ("fneg", "ineg", "dneg", "lneg"): v = st.pop(); st.append(-v if isinstance(v, float) else Op())
        elif op[1:] in ("add", "sub", "mul", "div", "rem") and op[0] in "fidl":
            b, a = st.pop(), st.pop()
            if isinstance(a, float) and isinstance(b, float) and (b or op[1:] not in ("div", "rem")):
                o = op[1:]  # every number is a float here; int and long division truncate toward zero, % keeps the dividend's sign
                st.append(a + b if o == "add" else a - b if o == "sub" else a * b if o == "mul" else math.fmod(a, b) if o == "rem" else float(math.trunc(a / b)) if op[0] in "il" else a / b)
            else: st.append(Op())
        elif op in ("i2f", "f2i", "i2d", "d2f", "f2d", "checkcast"): pass
        elif op == "new": st.append(Obj(com.split()[-1]))
        elif op == "getstatic":
            f = com.split()[1].split(":")[0]
            t = com.split(":")[-1]; own = com.split()[1].split(":")[0].rsplit(".", 1)[0] if "." in com.split()[1].split(":")[0] else CTX.get("cls", "")
            if follow and f.endswith("NO_ANIMATION"): st.append(NOANIM)
            elif follow and f not in statics and t == "L" + own + ";": st.append(statics.setdefault(f, Obj(f)))  # an enum constant: one object, so == works
            else: st.append(statics.get(f, Op()))
        elif op == "putstatic": statics[com.split()[1].split(":")[0]] = st.pop()
        elif op == "getfield":
            o = st.pop(); f = com.split()[1].split(":")[0].split(".")[-1]; p = getattr(o, "part", None)
            if isinstance(o, Rest):  # the entity at rest: its numbers 0, the objects it holds at rest too
                t = com.split(":")[-1]; st.append(o.over.get(f, 0.0) if t in ("I", "F", "D", "J", "Z", "S", "B", "C") else NOANIM if t.endswith("Animation;") else Rest(f))
            elif isinstance(o, Part) and f in MP_F:  # a vanilla ModelPart's x, y, z, xRot, yRot, zRot, visible, xScale…
                i = MP_F[f]; st.append(o.pose[i] if i < 6 else (0.0 if o.hide == "all" else 1.0) if i == 6 else (getattr(o, "scale", None) or [1.0] * 3)[i - 7])
            else: st.append(p.pose[POSE_F[f]] if p is not None and f in POSE_F else p.default[DEF_F[f]] if p is not None and f in DEF_F and getattr(p, "default", None) else o.f.get(f, Op()) if isinstance(o, Obj) else Op())
        elif op == "putfield":
            v, o = st.pop(), st.pop(); f = com.split()[1].split(":")[0].split(".")[-1]
            if isinstance(o, Rest): continue
            if isinstance(o, Part) and f in MP_F and isinstance(v, float):
                i = MP_F[f]
                if i < 6: o.pose[i] = v
                elif i == 6: o.hide = None if v else "all"
                else: o.scale = (getattr(o, "scale", None) or [1.0] * 3)[:]; o.scale[i - 7] = v
                continue
            if isinstance(o, Obj): o.f[f] = v
            p = getattr(o, "part", None)
            if p is not None and f in POSE_F and isinstance(v, float): p.pose[POSE_F[f]] = v  # rotationPointX.., rotateAngleX..
            if p is not None and f == "mirror": p.mirror = bool(v) if isinstance(v, float) else True  # llibrary/1.12 ModelRenderer.mirror
            if p is not None and f in ("showModel", "visible", "isHidden") and isinstance(v, float):
                p.hide = ("self" if v else None) if f == "isHidden" else (None if v else "all")
            if hasattr(v, "part") and v.part.name == "?": v.part.name = f  # a part stored in a field takes the field's name
        elif op == "invokedynamic":  # pops its arguments; a string concatenation of known values is built from its recipe
            k = re.match(r"InvokeDynamic #(\d+):(\w+):(\S+)", com)
            if not k: st.append(Op()); continue
            ats, ret = args_of(k.group(3)); a = [st.pop() if st else Op() for _ in ats][::-1]; r = Op()
            rec = CTX.get("bsm", {}).get(int(k.group(1)), [None])
            if k.group(2) == "makeConcatWithConstants" and isinstance(rec[0], str) and all(isinstance(x, (str, float)) for x in a):
                it = iter(jfmt(t, x) for t, x in zip(ats, a)); kst = iter(rec[1:])
                r = "".join(next(it, "") if c == "\x01" else next(kst, "") if c == "\x02" else c for c in rec[0])
            if ret != "V": st.append(r)
        elif op.startswith("invoke"):
            k = re.match(r"(?:Interface)?Method (?:(\S+?)\.)?(\"?<?[\w$]+>?\"?):(\S+)", com)
            if not k:
                st.append(Op()); continue
            owner, name, desc = k.groups(); name = name.strip('"'); owner = owner or CTX.get("cls", ""); cls = owner.split("/")[-1]
            ats, ret = args_of(desc); a = [st.pop() for _ in ats][::-1]
            recv = st.pop() if op != "invokestatic" else None
            r = None
            if follow:
                r = invoke(op, owner, name, ats, ret, recv, a)
                if r is not NOT:
                    if ret != "V": st.append(r)
                    continue
                r = None
            if op == "invokestatic" and not owner.startswith(("net/minecraft", "java")) and re.search(r"(MeshDefinition|LayerDefinition|PartDefinition);", desc):
                r = user(owner, name, desc, a)  # the mod's own helper (CultistModel.createMesh, createBodyLayer(float), Arm.createArmLayer(name, parent, ..)): run it too
                if ret == "V": continue
            if op == "invokespecial" and name == "<init>" and recv is CTX.get("this") and owner != CTX["cls"] and not owner.startswith(("net/minecraft", "java")) and not PARTS(cls):
                user(owner, name, desc, a, recv); r = Op()  # super(...) of the model: its parent's constructor builds parts too (SauropodBaseModel)
            if r is None: r = call(cls, name, recv, a, ats)
            if ret != "V": st.append(r)
        elif op in ("areturn", "return"):
            result = st.pop() if op == "areturn" and st else None
            break
    return result, loc

POSE_F = {f: i for i, f in enumerate(("rotationPointX", "rotationPointY", "rotationPointZ", "rotateAngleX", "rotateAngleY", "rotateAngleZ"))}
MP_F = {f: i for i, f in enumerate(("f_104200_", "f_104201_", "f_104202_", "f_104203_", "f_104204_", "f_104205_", "f_104207_", "f_233553_", "f_233554_", "f_233555_"))}
# ModelPart x y z xRot yRot zRot visible xScale yScale zScale by SRG name (the fields of client-1.20.1.jar's fee in that order)
DEF_F = {f: i for i, f in enumerate(("defaultPositionX", "defaultPositionY", "defaultPositionZ", "defaultRotationX", "defaultRotationY", "defaultRotationZ"))}
def _wrap(d):
    d = math.fmod(d, 360.0); return d - 360.0 if d >= 180.0 else d + 360.0 if d < -180.0 else d
MTH = {"m_14031_": math.sin, "m_14089_": math.cos, "m_14036_": lambda v, a, b: a if v < a else min(v, b), "m_14008_": lambda v, a, b: a if v < a else min(v, b),
       "m_14177_": _wrap, "m_14175_": _wrap, "m_14179_": lambda t, a, b: a + t * (b - a), "m_14139_": lambda t, a, b: a + t * (b - a),
       "m_14189_": lambda t, a, b: a + t * _wrap(b - a), "m_14154_": abs, "m_14116_": math.sqrt, "m_14143_": math.floor, "m_14107_": math.floor,
       "m_14167_": math.ceil, "m_14165_": math.ceil, "m_14207_": lambda v: v * v, "m_14136_": math.atan2, "m_14187_": lambda v: v - math.floor(v),
       "m_14118_": lambda a, b: _wrap(b - a), "m_14156_": lambda f, g: (abs(math.fmod(f, g) - g * 0.5) - g * 0.25) / (g * 0.25),
       "m_144920_": lambda a, b, t: a if t < 0 else b if t > 1 else a + t * (b - a)}  # net.minecraft.util.Mth by SRG name (server.txt + joined.tsrg)
NOT = object()
PART_CALLS = ("setRotationPoint", "setPos", "setTextureOffset", "texOffs", "addChild", "setMirror", "mirror", "setIsHidden", "setRotateAngle", "setRotationAngle", "<init>")
def invoke(op, owner, name, ats, ret, recv, a):
    """a call met while following a pose: Mth by its SRG name, the entity at rest, llibrary/citadel default poses, and the
    bytecode of the model, its parents and their helpers (walk, swing, flap, bob, progressRotationPrev…), run the same way.
    NOT: left to call()"""
    if owner == "net/minecraft/util/Mth" and name in MTH and all(isinstance(x, float) for x in a): return float(MTH[name](*a))
    if isinstance(recv, Rest):  # the entity at rest: a named value, else its own code (Apostle.getArmPose), else 0 / false / null
        if name in recv.over: return recv.over[name]
        if ret.endswith("Animation;"): return NOANIM  # no animation playing (llibrary/citadel getAnimation reads a field)
        if not owner.startswith(("net/minecraft", "java")) and CTX["depth"] <= 10:
            for c in recv.chain:
                m = find_method(c.replace(".", "/"), name, ats)
                if m and m[0] == c.replace(".", "/"):
                    pb, prev = CTX.get("bsm", {}), CTX["cls"]; CTX["bsm"], CTX["cls"] = m[2], m[0]; CTX["depth"] += 1
                    try: return run(m[1], None, CTX.setdefault("statics", {}), follow=True, loc=frame(a, ats, recv))[0]
                    finally: CTX["bsm"], CTX["cls"] = pb, prev; CTX["depth"] -= 1
        return 0.0 if ret in "FDIJSBCZ" else NOANIM if ret.endswith("Animation;") else None
    if recv is None and op != "invokestatic": return 0.0 if ret in "FDIJSBCZ" else None  # something absent at rest (an empty slot's item)
    if name in ("resetToDefaultPose", "updateDefaultPose") and isinstance(recv, Obj):
        for p in [recv.part] if hasattr(recv, "part") else [v.part for v in recv.f.values() if hasattr(v, "part")]:
            if name == "updateDefaultPose": p.default = p.pose[:]
            elif getattr(p, "default", None): p.pose = p.default[:]
        return None
    if (hasattr(recv, "part") or PARTS(owner.split("/")[-1])) and (name in PART_CALLS or name.startswith("addBox")): return NOT
    if owner == "net/minecraft/client/model/HumanoidModel" and name == "<init>" and a and isinstance(a[0], Part) and isinstance(recv, Obj):
        # vanilla HumanoidModel(ModelPart): head, hat, body, right_arm, left_arm, right_leg, left_leg from the root (client-1.20.1.jar, fbs.<init>)
        for f, n in zip(("f_102808_", "f_102809_", "f_102810_", "f_102811_", "f_102812_", "f_102813_", "f_102814_"), ("head", "hat", "body", "right_arm", "left_arm", "right_leg", "left_leg")):
            recv.f[f] = next((k for k in a[0].kids if k.name == n), Op())
        return None
    if owner.startswith(("net/minecraft", "java", "org/joml", "com/mojang")) or CTX["depth"] > 10: return NOT
    start = recv.cls.replace(".", "/") if op in ("invokevirtual", "invokeinterface") and isinstance(recv, Obj) else owner
    m = find_method(start, name, ats)
    if m is None: return NOT
    c, body, bsm = m; pb, prev = CTX.get("bsm", {}), CTX["cls"]; CTX["bsm"], CTX["cls"] = bsm, c; CTX["depth"] += 1
    try: r, _ = run(body, None, CTX.setdefault("statics", {}), follow=True, loc=frame(a, ats, None if op == "invokestatic" else recv))
    finally: CTX["bsm"], CTX["cls"] = pb, prev; CTX["depth"] -= 1
    return r
_CLS = {}
def find_method(cls, name, ats):
    """(class, code lines, bootstraps) of `name` taking these arguments in cls or the nearest parent that has it; classes
    are found in CTX["cp"] (class -> jar) or the model's jar"""
    for _ in range(12):
        if cls not in _CLS:
            jar = CTX.get("cp", {}).get(cls) or CTX["jar"]; pb = CTX.get("bsm", {})
            try: _CLS[cls] = (javap_methods(jar, cls), CTX.get("bsm", {}))
            except Exception: _CLS[cls] = None
            finally: CTX["bsm"] = pb
        if not _CLS[cls]: return None
        meths, bsm = _CLS[cls]
        nm = cls.split("/")[-1] if name == "<init>" else name  # javap names a constructor after its class
        for m in meths:
            head = m.strip().split("\n")[0]
            k = re.search(r"[ .]" + re.escape(nm) + r"\((.*?)\);", head)
            if k and "abstract" not in head.split("(")[0] and jtypes(k.group(1)) == [t if t in "ZBCSIFJD" else "L" for t in ats]: return cls, m.split("\n"), bsm
        decl = next((l for l in meths[0].split("\n") if re.search(r"\b(class|interface) ", l)), "")
        while "<" in decl: decl = re.sub(r"<[^<>]*>", "", decl)
        sup = re.search(r" extends ([\w.$]+)", decl)
        if name == "<init>" or not sup or sup.group(1).startswith(("java.", "net.minecraft")): return None
        cls = sup.group(1).replace(".", "/")
    return None
JT = {"float": "F", "int": "I", "double": "D", "long": "J", "boolean": "Z", "short": "S", "byte": "B", "char": "C"}
def jtypes(params):  # javap's parameter list as descriptor letters (any object type is "L")
    return [JT.get(t.strip(), "L") for t in params.split(",")] if params.strip() else []
def humanoid(g, y):
    """HumanoidModel.createMesh(CubeDeformation, yOffset) of vanilla 1.20.1, which many mob models start from."""
    m = Obj("MeshDefinition"); r = m.f["root"] = Part()
    for nm, u, v, box, pose, mir, gg in (("head", 0, 0, [-4, -8, -4, 8, 8, 8], [0, 0, 0], False, g), ("hat", 32, 0, [-4, -8, -4, 8, 8, 8], [0, 0, 0], False, g + .5),
                                         ("body", 16, 16, [-4, 0, -2, 8, 12, 4], [0, 0, 0], False, g), ("right_arm", 40, 16, [-3, -2, -2, 4, 12, 4], [-5, 2, 0], False, g),
                                         ("left_arm", 40, 16, [-1, -2, -2, 4, 12, 4], [5, 2, 0], True, g), ("right_leg", 0, 16, [-2, 0, -2, 4, 12, 4], [-1.9, 12, 0], False, g),
                                         ("left_leg", 0, 16, [-2, 0, -2, 4, 12, 4], [1.9, 12, 0], True, g)):
        p = Part(nm); p.pose = [float(pose[0]), pose[1] + y, float(pose[2]), 0.0, 0.0, 0.0]; p.cubes = [[float(x) for x in box] + [gg, u, v, mir]]; r.kids.append(p)
    return m

def jfmt(t, x):  # a value as string concatenation prints it
    if isinstance(x, str): return x
    return str(int(x)) if t in "IJSBC" else ("true" if x else "false") if t == "Z" else repr(x)
MODELLED = ("CubeListBuilder", "PartPose", "CubeDeformation", "LayerDefinition", "HumanoidModel", "AdvancedModelBox", "BasicModelPart", "ModelPart",
            "AdvancedModelRenderer", "BasicModelRenderer", "ModelRenderer")
PARTS = lambda cls: cls in MODELLED[5:] or "ModelBox" in cls  # constructor-style parts: lionfishapi/citadel AdvancedModelBox, llibrary AdvancedModelRenderer (Mowzie's)
def nums(a, ats, cls=""):
    """the numeric arguments in descriptor order (booleans are not numbers here); one the machine does not know reads 0, so the
    rest keep their places, and is counted when it went into a model call"""
    out = []
    for t, x in zip(ats, a):
        if t in "FIDJSBC":
            if not isinstance(x, float):
                if cls in MODELLED or PARTS(cls): CTX["unk"] = CTX.get("unk", 0) + 1
                x = 0.0
            out.append(x)
    return out
MATH = {"toRadians": math.radians, "toDegrees": math.degrees, "sin": math.sin, "cos": math.cos, "sqrt": math.sqrt, "abs": abs, "max": max, "min": min}
def call(cls, name, recv, a, ats):
    n = nums(a, ats, cls)
    flag = lambda: bool(a[0]) if a and isinstance(a[0], float) else True  # mirror(boolean); mirror() is true
    if cls == "Math" and name in MATH and all(isinstance(x, float) for x in a): return float(MATH[name](*a))
    # vanilla keyframe animations (AnimationDefinition.Builder withLength/addAnimation/looping/build, AnimationChannel, Keyframe,
    # KeyframeAnimations posVec (y negated) / degreeVec (radians) / scaleVec (minus 1); SRG names read from client-1.20.1.jar)
    if cls == "AnimationDefinition$Builder":
        if name == "m_232275_": o = Obj("AnimationDefinition"); o.f["bones"] = {}; return o
        if name == "m_232279_" and isinstance(recv, Obj) and "bones" in recv.f: recv.f["bones"].setdefault(a[0], []).append(a[1])
        return recv
    if cls in ("AnimationChannel", "Keyframe") and name == "<init>" and isinstance(recv, Obj):
        if cls == "AnimationChannel": recv.f["target"], recv.f["kf"] = a[0], a[1]
        else: recv.f["t"], recv.f["v"] = (n[0] if n else 0.0), a[1]
        return None
    if cls == "KeyframeAnimations" and len(n) == 3:
        return {"m_253126_": [n[0], -n[1], n[2]], "m_253186_": [math.radians(x) for x in n], "m_253004_": [x - 1.0 for x in n]}.get(name, Op())
    if cls == "MeshDefinition" and name == "m_171576_":
        if not isinstance(recv, Obj): return Part()
        return recv.f.setdefault("root", Part())
    if cls == "HumanoidModel" and name == "m_170681_": return humanoid(a[0].g if isinstance(a[0], Obj) else 0.0, n[0] if n else 0.0)
    if cls == "ModelPart" and name == "m_171324_":  # ModelPart.getChild(name) on the baked model (a vanilla model's constructor)
        return next((k for k in recv.kids if k.name == a[0]), Op()) if isinstance(recv, Part) else Op()
    if cls == "PartDefinition" and name == "m_171597_":  # getChild(name): a part built elsewhere (ApostleModel adds its hat and halo to CultistModel's head)
        return next((k for k in recv.kids if k.name == a[0]), Op()) if isinstance(recv, Part) else Op()
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
        if name in ("m_171555_",): b.mirror = flag(); return b
        if name == "m_171480_": b.mirror = True; return b
        if len(n) >= 6:
            g = next((x.g for x in a if isinstance(x, Obj) and x.cls.endswith("CubeDeformation")), 0.0)
            nt = [t for t in ats if t in "FIDJSBC"]  # addBox(name, x, y, z, w, h, d, deformation, u, v) has int texture offsets; floats there are a uv scale
            u, v = (n[6], n[7]) if len(n) >= 8 and nt[6] == nt[7] == "I" else (b.u, b.v)
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
    # lionfishapi AdvancedModelBox, llibrary AdvancedModelRenderer (constructor style)
    if PARTS(cls):
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
        elif name in ("setMirror",) or (name == "mirror"): p.mirror = flag()
        elif name == "setIsHidden": p.hide = "self" if flag() else None
        return recv
    if name in ("setRotateAngle", "setRotationAngle") and a and hasattr(a[0], "part"): a[0].part.pose[3:] = n[:3]; return None
    if name in ("texWidth", "texHeight"): return None
    return Op()

CTX = {"jar": None, "depth": 0}
def javap_methods(jar, cls):
    z = zipfile.ZipFile(jar); tmp = tempfile.mkdtemp(); path = cls.replace(".", "/") + ".class"; z.extract(path, tmp)
    t = subprocess.run(["javap", "-c", "-p", "-constants", tmp + "/" + path], capture_output=True, text=True).stdout
    CTX["bsm"] = bootstraps(tmp + "/" + path) if "InvokeDynamic" in t else {}
    return re.split(r"\n\n(?=  \S)", t)
def bootstraps(path):
    """BootstrapMethods of a class (javap -v): index -> [string arguments] (a concatenation's recipe first, then its constants)"""
    t = subprocess.run(["javap", "-v", path], capture_output=True, text=True).stdout
    out = {}; cur = None
    for line in t[t.find("\nBootstrapMethods:") + 1:].split("\n")[1:]:
        m = re.match(r"  (\d+): #\d+ ", line)
        if m: cur = out.setdefault(int(m.group(1)), []); continue
        m = re.match(r"      #\d+ (.*)$", line)
        if m and cur is not None: cur.append(re.sub(r"\\u([0-9a-fA-F]{4})", lambda q: chr(int(q.group(1), 16)), m.group(1)))
        elif not line.startswith("    "): break
    return out
def user(owner, name, desc, a, this=None):  # a static helper, or with `this` a parent's constructor
    if not CTX["jar"] or CTX["depth"] > 4: return None
    pb = CTX.get("bsm", {})  # the caller's bootstrap table, back when the helper is done
    try: meths = javap_methods(CTX["jar"], owner)
    except KeyError: return None
    ats, _ = args_of(desc)
    try:
        for m in meths:
            head = m.strip().split("\n")[0]
            nm = owner.split("/")[-1] if this is not None else name
            if re.search(r"\b" + re.escape(nm) + r"\(", head) and ("static" in head) == (this is None) and head.count(",") + (1 if "()" not in head else 0) == len(ats):
                CTX["depth"] += 1; prev = CTX["cls"]; CTX["cls"] = owner
                try:
                    r, _ = run(m.split("\n"), None, {"net/minecraft/client/model/geom/builders/CubeDeformation.f_171458_": Obj("CubeDeformation")}, ([this] if this is not None else []) + list(a))
                finally: CTX["depth"] -= 1; CTX["cls"] = prev
                return r
        decl = next((l for l in meths[0].split("\n") if " class " in l), "")  # not here: an inherited static (CroneModel.createMesh is CultistModel's)
        while "<" in decl: decl = re.sub(r"<[^<>]*>", "", decl)
        sup = re.search(r" extends ([\w.$]+)", decl)
        return user(sup.group(1).replace(".", "/"), name, desc, a, this) if this is None and sup and not sup.group(1).startswith(("net.minecraft", "java")) else None
    finally: CTX["bsm"] = pb

def keyframes(jar, cls, field):
    """an AnimationDefinition a class builds in its static initializer (vanilla KeyframeAnimations, as Goety writes them):
    {bone: [AnimationChannel]}"""
    CTX["jar"], CTX["cls"] = jar, cls.replace(".", "/")
    b = next((m.split("\n") for m in javap_methods(jar, cls) if m.strip().startswith("static {}")), None)
    T = "net/minecraft/client/animation/AnimationChannel$Targets."  # POSITION, ROTATION, SCALE: offsetPos/offsetRotation/offsetScale
    statics = {T + "f_232250_": "POSITION", T + "f_232251_": "ROTATION", T + "f_232252_": "SCALE"}
    if b: run(b, None, statics)
    d = statics.get(field)
    return d.f["bones"] if isinstance(d, Obj) and "bones" in d.f else None
def animate(root, bones):
    """KeyframeAnimations.animate at time 0: every channel at its first keyframe (the clamped fraction is 0 before or at it)
    added to the part the vanilla lookup finds (the first part, parents before children, with a child of that name)"""
    def find(p, n):
        for k in p.kids:
            if k.name == n: return k
        for k in p.kids:
            r = find(k, n)
            if r: return r
    miss = 0
    for n, chans in bones.items():
        p = find(root, n)
        for ch in chans:
            kf = ch.f.get("kf") if isinstance(ch, Obj) else None; v = kf[0].f.get("v") if isinstance(kf, list) and kf and isinstance(kf[0], Obj) else None
            if p is None or not (isinstance(v, list) and all(isinstance(x, float) for x in v)): miss += 1; continue
            t = ch.f.get("target")
            if t == "POSITION": p.pose[:3] = [a + b for a, b in zip(p.pose[:3], v)]
            elif t == "ROTATION": p.pose[3:] = [a + b for a, b in zip(p.pose[3:], v)]
            elif t == "SCALE": p.scale = [a + b for a, b in zip(getattr(p, "scale", None) or [1.0] * 3, v)]
    CTX["unk"] = CTX.get("unk", 0) + miss

def pose(this, rest):
    """the model's setupAnim (m_6973_) at rest, followed through its branches: no movement (limb swing 0), age 0, head
    straight, the entity standing still (Rest, with rest["entity"] for named getters and rest["chain"] its classes)"""
    for v in this.f.values():
        if hasattr(v, "part"): v.part.default = v.part.pose[:]
    CTX["statics"], CTX["depth"] = {}, 0
    ent = Rest("entity", rest.get("entity"), rest.get("chain", ()))
    invoke("invokevirtual", this.cls.replace(".", "/"), "m_6973_", ["Lnet/minecraft/world/entity/Entity;"] + ["F"] * 5, "V", this, [ent] + [0.0] * 5)

def model(jar, cls, method=None, rest=None, follow=False):
    """rest: a pose at rest (see pose(), or {"anim": (class, field)} for a vanilla idle animation at time 0); follow: build
    createBodyLayer following its branches (a ternary on a constant argument then takes one side)"""
    CTX["jar"] = jar; CTX["cls"] = cls.replace(".", "/"); CTX["unk"] = 0; CTX["this"] = None
    meths = javap_methods(jar, cls)
    def body(pred):
        for m in meths:
            head = m.strip().split("\n")[0]
            if pred(head): return m.split("\n")
    statics = {"net/minecraft/client/model/geom/builders/CubeDeformation.f_171458_": Obj("CubeDeformation")}
    for k, v in (("net/minecraft/client/model/geom/PartPose.f_171404_", Pose([0.0] * 6)),): statics[k] = v
    b = body(lambda h: (method or "createBodyLayer") + "(" in h and "LayerDefinition" in h) if not method or method == "createBodyLayer" else body(lambda h: method + "(" in h)
    if b:
        CTX["depth"], CTX["statics"] = 0, {}
        r, _ = run(b, None, statics, follow=follow)
        if isinstance(r, dict) and isinstance(r.get("root"), Part):
            if rest and rest.get("anim"):  # the idle animation at its first frame (setupAnim at rest of a vanilla HierarchicalModel)
                bones = keyframes(jar, *rest["anim"])
                if bones: animate(r["root"], bones)
            elif rest is not None:  # a vanilla model: its constructor takes the baked parts (getChild), then setupAnim at rest
                this = CTX["this"] = Obj(cls); CTX["cls"] = cls.replace(".", "/")
                invoke("invokespecial", cls.replace(".", "/"), "<init>", ["Lnet/minecraft/client/model/geom/ModelPart;"], "V", this, [r["root"]])
                pose(this, rest)
            return {"tw": r["tw"], "th": r["th"], "root": r["root"].dump()}
    # constructor style: run <init> (the longest one: the others hand over with this(...); a parent's constructor in the jar
    # runs too), then take the parts with no parent
    b = max(([m.split("\n") for m in meths if re.search(r"\b" + re.escape(cls.split(".")[-1]) + r"\(", m.strip().split("\n")[0])]), key=len, default=None)
    if not b: return None
    this = CTX["this"] = Obj(cls); run(b, this, statics)
    if rest is not None and not rest.get("anim"): pose(this, rest)
    parts = [v.part for v in this.f.values() if hasattr(v, "part")]
    kids = {id(k) for p in parts for k in p.kids}
    roots = [p for p in parts if id(p) not in kids]
    # the roots the model draws (renderToBuffer, citadel's parts()): a part left without a parent (Mowzie's groin, re-parented
    # under rootBox but still holding its own copy of the legs) is not drawn
    shown = {f for m in meths if re.search(r"\b(m_7695_|renderToBuffer|parts)\(", m.strip().split("\n")[0]) for f in re.findall(r"getfield .*// Field (\w+):", m)}
    roots = [p for p in roots if any(getattr(this.f.get(f), "part", None) is p for f in shown)] or roots
    if not roots: return None
    size = lambda p: len(p.cubes) + sum(size(k) for k in p.kids)
    tw = next((v for k, v in this.f.items() if k in ("texWidth", "textureWidth", "f_102610_") and isinstance(v, float)), 64.0)
    th = next((v for k, v in this.f.items() if k in ("texHeight", "textureHeight", "f_102611_") and isinstance(v, float)), 64.0)
    root = Part("root"); root.kids = roots if len(roots) > 1 else roots
    return {"tw": tw, "th": th, "root": (max(roots, key=size) if len(roots) == 1 else root).dump()}

if __name__ == "__main__":
    out, unk = {}, {}
    for spec in sys.argv[2:]:
        jar, cls, *m = spec.split(":")
        try: out[cls.split(".")[-1]] = model(jar, cls, m[0] if m else None)
        except Exception as e: print("FAIL", cls, e); out[cls.split(".")[-1]] = None
        unk[cls.split(".")[-1]] = CTX.get("unk", 0)
    json.dump(out, open(sys.argv[1], "w"))
    cnt = lambda p: len(p["cubes"]) + sum(cnt(k) for k in p["children"]) if p else 0
    for k, v in out.items(): print(k, v and (v["tw"], v["th"], cnt(v["root"])), "| model arguments not worked out (read as 0): %d" % unk[k] if unk.get(k) else "")
