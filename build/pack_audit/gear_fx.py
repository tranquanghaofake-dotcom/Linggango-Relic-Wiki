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
import json, re, sys, zipfile, glob, subprocess, tempfile, os, pathlib, collections
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

def scan(body, roles, own, depth, seen, out, when):
    st = []; chance = None; last_load = None
    for line in body:
        m = re.match(r"\s*\d+: (\w+)\s*(.*)", line)
        if not m: continue
        op, rest = m.groups(); com = rest.split("// ", 1)[1] if "// " in rest else ""
        if re.match(r"aload(_\d)?$", op): last_load = int(op[-1]) if "_" in op else int(rest.split()[0]); st.append(("L", last_load)); continue
        if op == "getstatic":
            ref, typ = com.split()[1].split(":", 1)
            if re.search(r"MobEffect;|RegistryObject;|Supplier;|Holder;|DeferredHolder;", typ): st.append(("F", ref))
            continue
        k = re.match(r"(?:float|int|double|long) ([-\d.E]+)", com) if op.startswith("ldc") else None
        if k: st.append(("N", float(k.group(1)))); continue
        if re.match(r"[ifld]const_m?\d", op): st.append(("N", float(op[-1]) * (-1 if "m1" in op else 1))); continue
        if op in ("bipush", "sipush"): st.append(("N", float(rest.split()[0]))); continue
        if op == "new" and "MobEffectInstance" in com: st.append(("NEW", last_load)); continue
        if op.startswith("invoke"):
            if "nextFloat" in com or "nextDouble" in com: st.append(("RND", None)); continue
            if "MobEffectInstance.\"<init>\"" in com:
                i = max((x for x in range(len(st)) if st[x][0] == "NEW"), default=None)
                if i is not None:
                    seg = st[i:]; fld = next((v for t, v in seg if t == "F"), None); nums = [v for t, v in seg if t == "N"]
                    who = roles.get(st[i][1], "target" if when == "hit" else "self")
                    if fld:
                        out.append({"when": when, "who": who, "effect": effname(fld, NS[0]), "ticks": int(nums[0]) if nums else None, "level": int(nums[1]) + 1 if len(nums) > 1 else 1, **({"chance": chance} if chance else {})})
                    del st[i:]
                continue
            if re.search(r"\.m_20254_:\(I\)V", com):  # setSecondsOnFire
                n = [v for t, v in st if t == "N"]; out.append({"when": when, "who": roles.get(last_load, "target"), "fire": int(n[-1]) if n else None}); st = []; continue
            if re.search(r"\.m_5634_:\(F\)V", com):  # heal
                n = [v for t, v in st if t == "N"]; out.append({"when": when, "who": roles.get(last_load, "self"), "heal": n[-1] if n else None}); st = []; continue
            mm = re.match(r"(?:Interface)?Method (?:(\S+?)\.)?([\w$]+):(\S+)", com)
            if mm and depth < 2 and (mm.group(1) in (None, own)) and mm.group(2) not in seen:  # the class's own helper: follow it once
                seen.add(mm.group(2)); out.append(("CALL", mm.group(2), when)); continue
            continue
        if op in ("fcmpg", "fcmpl", "dcmpg", "dcmpl") and any(t == "RND" for t, _ in st[-3:]):
            n = [v for t, v in st[-3:] if t == "N"]
            if n: chance = round(n[-1], 3)
            continue

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
            for _, helper, when in calls:  # one level into the class's own helpers
                for d, body in by.get(helper, []):
                    res = []; scan(body, {}, path, 1, {helper}, res, when)
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
