"""What a weapon or armor piece DOES beyond its attributes, read from the mod's bytecode (javap, nothing is run).
Usage: gear_fx.py JARS_DIR SRG2MOJ.json  -> build/patches/gear_fx.json {item id: {"fx": [...], "tip": [...]}}
For each gear item of src/gear_data.js the item's class (and its parents inside the same jar, up to vanilla) is read; in the
methods the game calls on hit (hurtEnemy), while worn or held (onArmorTick, inventoryTick), on use and on bow release
(use, releaseUsing, finishUsingItem), and in the class's own helpers those call, it finds:
  effect   new MobEffectInstance(effect, ticks, level) given to the target or the wearer, with a random chance when the
           call sits behind `random.nextFloat() < c`
  fire     setSecondsOnFire(n) on the target
  heal     heal(x) on the wearer (life steal and the like)
  hurt     an extra hurt(...) on the target
Effects are named by vanilla's MobEffects field (mapped from srg with SRG2MOJ.json, made from Mojang's server.txt and
MCPConfig's joined.tsrg) or by the mod's own registry field (BLEEDING, SOUL_BURN...). Lines of the item's own tooltip are
taken from the mods' en_us.json (keys that start with the item's translation key and are not the name itself).
What this cannot see: effects written in event handlers of other classes (many set bonuses), values read from configs at
run time, and spells. Those need the in-game measurement (kubejs/server_scripts/lgw_measure.js)."""
import json, re, sys, zipfile, glob, subprocess, tempfile, os, pathlib, collections, math
JD, MAPF = sys.argv[1], sys.argv[2]
H = pathlib.Path(__file__).resolve().parents[1]
SRG = json.load(open(MAPF))
s = (H / "src" / "gear_data.js").read_text(encoding="utf-8"); GE, _ = json.JSONDecoder().raw_decode(s, s.index("[", s.index("GE=")))

# index: class path -> jar; namespace -> jars; lang
CLS, LANG = {}, {}
for j in glob.glob(JD + "/*.jar"):
    try: z = zipfile.ZipFile(j)
    except zipfile.BadZipFile: continue
    for n in z.namelist():
        if n.endswith(".class"): CLS.setdefault(n[:-6].split("/")[-1], []).append((j, n[:-6]))
        elif n.endswith("lang/en_us.json"):
            try: LANG.update(json.loads(z.read(n).decode("utf8", "ignore")))
            except ValueError: pass

JAVAP = {}
def javap(jar, path):
    k = (jar, path)
    if k not in JAVAP:
        tmp = tempfile.mkdtemp(); zipfile.ZipFile(jar).extract(path + ".class", tmp)
        JAVAP[k] = subprocess.run(["javap", "-c", "-p", "-constants", tmp + "/" + path + ".class"], capture_output=True, text=True).stdout
    return JAVAP[k]

ITEM = "Lnet/minecraft/world/item/ItemStack;"
ROLE = {  # method descriptor -> (when, {local index: who})
    "(Lnet/minecraft/world/item/ItemStack;Lnet/minecraft/world/entity/LivingEntity;Lnet/minecraft/world/entity/LivingEntity;)Z": ("hit", {2: "target", 3: "self"}),
    "(Lnet/minecraft/world/item/ItemStack;Lnet/minecraft/world/level/Level;Lnet/minecraft/world/entity/Entity;IZ)V": ("carried", {3: "self"}),
    "(Lnet/minecraft/world/item/ItemStack;Lnet/minecraft/world/level/Level;Lnet/minecraft/world/entity/player/Player;)V": ("worn", {3: "self"}),
    "(Lnet/minecraft/world/level/Level;Lnet/minecraft/world/entity/player/Player;Lnet/minecraft/world/InteractionHand;)Lnet/minecraft/world/InteractionResultHolder;": ("use", {2: "self"}),
    "(Lnet/minecraft/world/item/ItemStack;Lnet/minecraft/world/level/Level;Lnet/minecraft/world/entity/LivingEntity;I)V": ("release", {3: "self"}),
    "(Lnet/minecraft/world/item/ItemStack;Lnet/minecraft/world/level/Level;Lnet/minecraft/world/entity/LivingEntity;)Lnet/minecraft/world/item/ItemStack;": ("use", {3: "self"}),
}
SPLIT = re.compile(r"\n(?=  [a-z].*\);\n    descriptor:|  \S[^\n]*\);\n)")

def methods(text):
    """javap -c text -> [(header, descriptor-less name, body lines)]"""
    out = []
    for blk in re.split(r"\n\n(?=  \S)", text):
        lines = blk.strip("\n").split("\n")
        if not lines or "(" not in lines[0]: continue
        out.append((lines[0].strip(), lines[1:]))
    return out

def desc_of(header):
    # rebuild a JVM descriptor from javap's Java-style header: enough for the shapes in ROLE
    m = re.search(r"([\w.$<>]+)\(([^)]*)\)", header)
    if not m: return None, None
    name, args = m.group(1).split(".")[-1], [a.strip() for a in m.group(2).split(",") if a.strip()]
    ret = header[:m.start()].split()[-1] if header[:m.start()].split() else "void"
    def t(x):
        x = re.sub(r"<.*>", "", x)
        prim = {"boolean": "Z", "int": "I", "float": "F", "double": "D", "long": "J", "void": "V", "byte": "B", "short": "S", "char": "C"}
        arr = x.count("[]"); x = x.replace("[]", "")
        return "[" * arr + (prim[x] if x in prim else "L" + x.replace(".", "/") + ";")
    return name, "(" + "".join(t(a) for a in args) + ")" + t(ret)

# vanilla MobEffects field -> registry name (the game's id; the field names are older)
VAN = {"MOVEMENT_SPEED": "speed", "MOVEMENT_SLOWDOWN": "slowness", "DIG_SPEED": "haste", "DIG_SLOWDOWN": "mining_fatigue", "DAMAGE_BOOST": "strength",
       "HEAL": "instant_health", "HARM": "instant_damage", "JUMP": "jump_boost", "CONFUSION": "nausea", "DAMAGE_RESISTANCE": "resistance"}
REGNAME = {}
def regnames(owner):
    """field -> registry name, from the effect registry class's static init (ldc "name" ... putstatic FIELD)"""
    if owner in REGNAME: return REGNAME[owner]
    m = {}
    for jar, path in CLS.get(owner.split("/")[-1], []):
        if path != owner: continue
        last = None
        for line in javap(jar, path).split("static {};")[-1].split("\n"):
            k = re.search(r"// String ([a-z0-9_]+(?::[a-z0-9_]+)?)\s*$", line)
            if k: last = k.group(1); continue
            k = re.search(r"putstatic\s+#\d+\s+// Field (\w+):", line)
            if k and last: m[k.group(1)] = last; last = None
    REGNAME[owner] = m; return m
def effname(fieldref, ns):
    owner, f = fieldref.rsplit(".", 1)
    if owner == "net/minecraft/world/effect/MobEffects":
        n = SRG.get(f, f).split(".")[-1]
        return "minecraft:" + VAN.get(n, n.lower())
    n = regnames(owner).get(f)
    if n: return (n if ":" in n else ns + ":" + n)
    return ns + ":" + re.sub(r"^effect_?", "", f.lower())

ARGS = re.compile(r"\[*(?:[ZBCSIFJD]|L[^;]+;)")
RND = re.compile(r"\.(nextFloat|nextDouble|m_188501_|m_188500_):\(\)[FD]|java/lang/Math\.random:")  # RandomSource.nextFloat/nextDouble (srg), Random, Math.random
FLIP = {"lt": "gt", "gt": "lt", "le": "ge", "ge": "le", "eq": "eq", "ne": "ne"}
POP2 = re.compile(r"[ilfd](add|sub|mul|div|rem|and|or|xor|shl|shr|ushr)$|[lfd]cmp[lg]?$|[ilfdabcs]aload$")
POP1 = re.compile(r"[ilfda]store(_\d)?$|pop$|monitor\w+$|putstatic$|athrow$|[ilfda]?return$|if(eq|ne|lt|ge|gt|le|null|nonnull)$|(table|lookup)switch$")
class T:  # a value on the scanned stack: N number, F effect field, L local, RND random draw, CMP a comparison with one, E an effect instance, ? unknown
    def __init__(s, k, v=None, w=False): s.k, s.v, s.w = k, v, w

def scan(body, roles, own, depth, seen, out, when, base=1.0):
    """Stack-tracking pass over one javap method body, top to bottom (branches are not followed: a value that differs where two
    paths join reads unknown). Effect arguments are taken by the constructor's descriptor; a random draw compared with a number
    gives a chance to the code its `if` guards (and 1 - chance to an else part), nothing else."""
    ins = []
    for line in body:
        m = re.match(r"\s*(\d+): ([a-z]\w*)\s*(.*)", line)  # not the "key: target" lines of a switch
        if m: ins.append((int(m.group(1)), m.group(2), m.group(3)))
    at = {p: q for q, (p, _, _) in enumerate(ins)}
    st, loc, scopes, snap = [], {}, [], {}
    def pop(n=1): return [st.pop() if st else T("?") for _ in range(n)][::-1]
    def chance(p): return base * math.prod(c for a, e, c in scopes if a < p < e)
    dead = False
    for q, (p, op, rest) in enumerate(ins):
        if p in snap:  # a jump lands here: keep its stack, or where it meets the stack that ran in, what agrees
            j = snap.pop(p)
            st = j if dead or len(j) != len(st) else [x if x is y else T("?") for x, y in zip(j, st)]
        dead = False
        com = rest.split("// ", 1)[1] if "// " in rest else ""
        tgt = int(rest.split()[0]) if (op.startswith("if") or op.startswith("goto")) and rest.split() and rest.split()[0].isdigit() else None
        if re.match(r"[ilfda]load(_\d)?$", op):
            ix = int(op[-1]) if "_" in op else int(rest.split()[0]); v = loc.get(ix)
            st.append(v if v is not None and v.k in ("N", "E", "F") else T("L", ix, op[0] in "ld"))
        elif re.match(r"[ilfda]store(_\d)?$", op): loc[int(op[-1]) if "_" in op else int(rest.split()[0])] = pop()[0]
        elif re.match(r"[ilfd]const_(m1|\d)$", op): st.append(T("N", -1.0 if op.endswith("m1") else float(op[-1]), op[0] in "ld"))
        elif op in ("bipush", "sipush"): st.append(T("N", float(rest.split()[0])))
        elif op.startswith("ldc"):
            k = re.match(r"(float|int|double|long) ([-\d.E]+|NaN|-?Infinity)", com)
            st.append(T("N", float(k.group(2)), k.group(1) in ("double", "long")) if k else T("?"))
        elif op == "aconst_null": st.append(T("?"))
        elif op == "getstatic":
            ref, typ = com.split()[1].split(":", 1)
            st.append(T("F", ref) if re.search(r"MobEffect;|RegistryObject;|Supplier;|Holder;|DeferredHolder;", typ) else T("?", None, typ[0] in "JD"))
        elif op == "getfield": pop(); st.append(T("?", None, com.split(":")[-1][:1] in "JD"))
        elif op == "putfield": pop(2)
        elif op == "new": st.append(T("NEW", "MobEffectInstance" in com))
        elif op == "dup": st.append(st[-1] if st else T("?"))
        elif op == "dup_x1": a, b = pop(2); st += [b, a, b]
        elif op == "dup2": st += st[-1:] if st and st[-1].w else st[-2:]
        elif op == "swap": a, b = pop(2); st += [b, a]
        elif op == "pop2": pop(1 if st and st[-1].w else 2)
        elif op in ("fcmpl", "fcmpg", "dcmpl", "dcmpg"):
            a, b = pop(2)
            st.append(T("CMP", ("RND", b.v) if a.k == "RND" and b.k == "N" else ("NUM", a.v) if b.k == "RND" and a.k == "N" else None))
        elif op.startswith("if"):
            c = pop(2 if op.startswith(("if_icmp", "if_acmp")) else 1)[0]
            if c.k == "CMP" and c.v and tgt and tgt > p and op[2:] in FLIP:
                rel = op[2:] if c.v[0] == "RND" else FLIP[op[2:]]  # the jump is taken when RND <rel> the number
                x = min(1.0, max(0.0, c.v[1]))
                run = {"lt": 1 - x, "le": 1 - x, "gt": x, "ge": x}.get(rel)  # the guarded code runs when the jump is not taken
                if run is not None:
                    scopes.append((p, tgt, run))
                    pj = ins[at[tgt] - 1] if tgt in at and at[tgt] > 0 else None
                    if pj and pj[1].startswith("goto") and int(pj[2].split()[0]) > tgt: scopes.append((tgt - 0.5, int(pj[2].split()[0]), 1 - run))
            if tgt and tgt > p: snap.setdefault(tgt, list(st))
        elif op.startswith("goto"):
            if tgt and tgt > p: snap[tgt] = list(st)
            dead = True
        elif op in ("areturn", "ireturn", "freturn", "dreturn", "lreturn", "return", "athrow"): pop(0 if op == "return" else 1); dead = True
        elif op.startswith("invoke"):
            k = re.match(r"(?:Interface)?Method (?:(\S+?)\.)?(\"?[\w$<>]+\"?):(\S+)", com) or re.match(r"InvokeDynamic #\d+:(\w+):(\S+)", com)
            if not k: continue
            owner, name, desc = (k.group(1), k.group(2).strip('"'), k.group(3)) if k.re.groups == 3 else (None, k.group(1), k.group(2))
            args = pop(len(ARGS.findall(desc[1:desc.index(")")])))
            recv = pop()[0] if op not in ("invokestatic", "invokedynamic") else None
            ret = desc[desc.index(")") + 1:]
            res = T("?", None, ret in ("J", "D"))
            if RND.search(com): res = T("RND")
            elif name == "<init>" and recv.k == "NEW" and recv.v:  # new MobEffectInstance(effect, duration, amplifier, ...)
                kinds = ARGS.findall(desc[1:desc.index(")")])
                eff = args[0] if args and kinds[0].endswith("MobEffect;") else None
                if eff and eff.k == "F":
                    d = args[1] if len(args) > 1 else None; a = args[2] if len(args) > 2 else None
                    r = {"when": when, "who": None, "effect": effname(eff.v, NS[0]), "ticks": int(d.v) if d and d.k == "N" else None,
                         "level": 1 if len(args) < 3 else int(a.v) + 1 if a.k == "N" else None}
                    c = chance(p)
                    if c < 0.9995: r["chance"] = round(c, 3)
                    out.append(r); recv.k, recv.v = "E", r  # the dup'd reference below is the same instance
                else: recv.k = "?"
                continue
            elif re.search(r"\.m_20254_:\(I\)V", com):  # setSecondsOnFire
                r = {"when": when, "who": roles.get(recv.v, "target") if recv.k == "L" else "target", "fire": int(args[0].v) if args[0].k == "N" else None}
                c = chance(p)
                if c < 0.9995: r["chance"] = round(c, 3)
                out.append(r)
            elif re.search(r"\.m_5634_:\(F\)V", com):  # heal
                out.append({"when": when, "who": roles.get(recv.v, "self") if recv.k == "L" else "self", "heal": args[0].v if args[0].k == "N" else None})
            elif recv is not None and recv.k == "F" and name in ("get", "value", "m_203334_"): res = recv  # RegistryObject.get / Holder.value: still that effect
            elif depth < 2 and owner in (None, own) and name not in seen:  # the class's own helper: follow it once
                seen.add(name); out.append(("CALL", name, when, chance(p)))
            for e in args:  # target.addEffect(instance): whose effect it is, from the receiver
                if e.k == "E" and e.v.get("who") is None and recv is not None and recv.k == "L" and recv.v in roles: e.v["who"] = roles[recv.v]
            if ret != "V": st.append(res)
        elif op == "multianewarray": pop(int(rest.split()[-1])); st.append(T("?"))
        elif op in ("instanceof", "arraylength", "newarray", "anewarray"): pop(); st.append(T("?"))
        elif re.match(r"[ilfd]2[ilfdbcs]$", op):
            a = pop()[0]; st.append(T("N", float(int(a.v)) if op[2] in "ilbcs" else a.v, op[2] in "ld") if a.k == "N" else T("?", None, op[2] in "ld"))
        elif re.match(r"[ilfd]neg$", op): a = pop()[0]; st.append(T("N", -a.v, a.w) if a.k == "N" else T("?", None, op[0] in "ld"))
        elif POP2.match(op):  # constant arithmetic folds (20 * seconds when seconds is a constant local)
            a, b = pop(2)
            if a.k == "N" and b.k == "N" and op[1:] in ("add", "sub", "mul"):
                st.append(T("N", a.v + b.v if op[1:] == "add" else a.v - b.v if op[1:] == "sub" else a.v * b.v, op[0] in "ld"))
            else: st.append(T("?", None, op in ("laload", "daload") or (op[0] in "ld" and "cmp" not in op and not op.endswith("aload"))))
        elif re.match(r"[ilfdabcs]astore$", op): pop(3)
        elif POP1.match(op): pop()
    for r in out:  # effects never handed to an entity in sight: the target on a hit, else the wearer or holder
        if isinstance(r, dict) and r.get("who") is None: r["who"] = "target" if when == "hit" else "self"

NS = [""]
def item_fx(cls_names, ns):
    out, tried = [], set(); NS[0] = ns
    for cn in cls_names[:3]:
        cands = [c for c in CLS.get(cn, []) if f"/{ns}/" in c[1] or ns.replace("_", "") in c[1].lower().replace("_", "")] or CLS.get(cn, [])[:1]
        for jar, path in cands[:1]:
            if path in tried: continue
            tried.add(path)
            ms = methods(javap(jar, path)); by = {}
            for hdr, body in ms:
                name, d = desc_of(hdr)
                if name: by.setdefault(name, []).append((d, body))
            calls = []
            for name, lst in by.items():
                for d, body in lst:
                    if d in ROLE or name in ("onArmorTick", "onHit", "hurtEnemy"):
                        when, roles = ROLE.get(d, ("worn" if name == "onArmorTick" else "hit", {3: "self", 2: "target"}))
                        res = []; scan(body, roles, path, 0, {name}, res, when)
                        for r in res:
                            if isinstance(r, tuple): calls.append(r)
                            else: out.append(r)
            for _, helper, when, ch in calls:  # one level into the class's own helpers, under the chance of the call
                for d, body in by.get(helper, []):
                    res = []; scan(body, {}, path, 1, {helper}, res, when, ch)
                    out += [r for r in res if not isinstance(r, tuple)]
    uniq, seen = [], set()
    for r in out:
        k = json.dumps(r, sort_keys=True)
        if k not in seen: seen.add(k); uniq.append(r)
    # one shared class that gives a different effect per armor material (Adam's Ars Plus): which one this item gets is
    # decided at run time, so these are only "one of"
    for when in ("worn", "carried"):
        e = [r for r in uniq if r.get("when") == when and r.get("effect")]
        if len({r["effect"] for r in e}) > 3:
            for r in e: r["maybe"] = True
    return uniq

def efflabel(e):
    ns, p = e.split(":", 1)
    return LANG.get(f"effect.{ns}.{p}") or p.replace("_", " ").title().replace("Of ", "of ")

def tips(iid):
    ns, p = iid.split(":"); base = f"item.{ns}.{p}"; out = []
    for k, v in LANG.items():
        if k.startswith(base + ".") and not k.endswith((".name", ".jei")) and isinstance(v, str) and len(v) > 3:
            out.append(re.sub(r"§.", "", v).strip())
    return out[:8]

res, n_fx, n_tip = {}, 0, 0
for g in GE:
    if g["k"] not in ("melee", "ranged", "magic", "summon", "armor"): continue
    f = item_fx(g.get("cls") or [], g["ns"])
    t = tips(g["id"])
    for r in f:
        if r.get("effect"): r["name"] = efflabel(r["effect"])
    if f or t:
        res[g["id"]] = {k: v for k, v in (("fx", f), ("tip", t)) if v}; n_fx += bool(f); n_tip += bool(t)
(H / "patches" / "gear_fx.json").write_text(json.dumps(res, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
c = collections.Counter(r.get("effect") or ("fire" if "fire" in r else "heal" if "heal" in r else "?") for v in res.values() for r in v.get("fx", []))
print(len(res), "items;", n_fx, "with effects from code,", n_tip, "with tooltip lines; top effects:", c.most_common(15))
