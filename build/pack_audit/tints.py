#!/usr/bin/env python3
"""The colours the game multiplies into tinted item layers (ItemColors), read from the jars, for mcassets.icon(..., tint).

  T = Tints("client-1.20.1.jar", mod_jars, colormap=assets)   # mod_jars optional: spawn eggs and colour handlers of mods
  T.tint("minecraft:allay_spawn_egg", 2)    -> ({0: 0x00DAFF, 1: 0x00ADFF}, "source")  or (None, why not)
  T.tint("minecraft:potion", 2, potion="minecraft:healing")   -> ({0: 0xF82423}, ...)
  T.eggs  {egg id: (entity id or None, primary, secondary, source)};  T.egg_for(entity id) -> its egg

The item shader multiplies a quad's texel by the colour ItemColors returns for its tintindex (layerN of item/generated
has tintindex N; element faces carry their own; a face without one is never tinted); -1 means no tint.
  - vanilla (client jar, obfuscated: every class is found by a constant only it holds, nothing is typed in by hand):
    ItemColors.createDefault and BlockColors.createDefault are parsed into (lambda, items) pairs and each lambda runs in
    a small interpreter (`_Jvm`) on an ItemStack without NBT, so the defaults are the game's own branches: leather
    0xA06540 on layer 0, firework star 0x8A8A8A on layer 1, spawn eggs SpawnEggItem.getColor (tintindex 0 = the
    constructor's first int, any other = the second; the ints from Items.<clinit>; all 77 equal minecraft.wiki's base /
    overlay table), grass and ferns GrassColor.get(0.5, 1.0) = colormap/grass.png at (127, 127) = 0x7CBD6B (0x91BD59 is
    the plains biome, not the item), leaves FoliageColor constants, lily pad 0x71C35C. Potions and tipped arrows go
    through PotionUtils.getColor: a stack without NBT is Potions.EMPTY, the magenta 0xF800F8 "Uncraftable Potion", so
    the caller names a potion and its colour is worked out as PotionUtils does (effect colours from MobEffects.<clinit>,
    weighted by amplifier + 1, in float).
  - mods (Mojang class names, SRG members): registration code runs in gear/mjvm.py. ForgeSpawnEggItem / SpawnEggItem
    (or a subclass's super call) records its two ints, through helpers (Alex's Caves' spawnEgg(name, type, a, b, biome),
    EEEAB's rgb2dec(r, g, b)); Forge registers egg.getColor(layer) for every ForgeSpawnEggItem at the highest priority,
    so the vanilla rule applies unless the mod registers its own colour later. Every method that takes
    RegisterColorHandlersEvent.Item, or calls ItemColors.register / the event's register itself, runs with a stand-in
    event; each (ItemColor, items) it registers is evaluated per tintindex on a stack without NBT, with DyeColor read
    from the client jar (Ars Nouveau armour: DyeColor.PURPLE.getTextColor() 0xA020F0) and vanilla defaults where a mod
    calls into vanilla (DyeableLeatherItem, PotionUtils, GrassColor, FoliageColor). Items are named by their
    RegistryObject, a wrapper holding one, the id they were registered under (register("ns:path", supplier)), or, for
    Registrate-style fields the interpreter cannot follow, the static field's name. What the interpreter cannot decide
    (an NBT module, a clock, an Optional) comes back unknown and that layer is not tinted.
Needs `javap` (any JDK) for the vanilla jar and jawa (pip install jawa) for mjvm."""
import io, os, re, struct, subprocess, sys, zipfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gear"))

# ---------------------------------------------------------------- javap text of the (obfuscated) client jar
_INS = re.compile(r"^\s+(\d+): (\w+)\s*(.*?)\s*(?://\s*(.*))?$")


class _Class:
    def __init__(s, name, text):
        s.name, s.methods, s.boot, s.fields = name, {}, [], set()
        cur = None
        lines = text.splitlines()
        for i, ln in enumerate(lines):
            if re.match(r"^  [A-Za-z].*\);$|^  static \{\};$", ln):
                head = ln.strip()
                nm = "<clinit>" if head.startswith("static {}") else head[:head.index("(")].split()[-1]
                if nm == name or nm.endswith("." + name): nm = "<init>"
                desc = lines[i + 1].strip()[len("descriptor: "):] if i + 1 < len(lines) and "descriptor:" in lines[i + 1] else ""
                cur = []; s.methods[(nm, desc)] = cur
                continue
            if re.match(r"^  [A-Za-z][^(]*;$", ln):
                cur = None
                f = ln.strip().rstrip(";").split()
                if f: s.fields.add(f[-1])
                continue
            m = _INS.match(ln)
            if m and cur is not None:
                cur.append((int(m.group(1)), m.group(2), m.group(3), m.group(4) or ""))
        # BootstrapMethods (javap -v): index -> "owner.name:desc" of the lambda body
        bm = text.find("BootstrapMethods:")
        if bm >= 0:
            for blk in re.split(r"\n\s+\d+: #\d+ REF_invokeStatic", text[bm:])[1:]:
                r = re.findall(r"REF_\w+ (\S+)", blk)
                s.boot.append(r[0] if r else None)

    def method(s, name, desc=None):
        for (n, d), v in s.methods.items():
            if n == name and (desc is None or d == desc): return (n, d), v
        return None, None


def _ref(c):
    """'Method cfz.d:()Lcfu;' -> ('cfz', 'd', '()Lcfu;'); an own-class reference has no owner"""
    m = re.match(r"(?:Interface)?(?:Method|Field) (?:(\S+)\.)?([^.:\s]+):(\S+)", c)
    return (m.group(1), m.group(2), m.group(3)) if m else (None, None, None)


def _int(op, arg, com):
    if op.startswith("iconst_"): return -1 if op.endswith("m1") else int(op[7:])
    if op in ("bipush", "sipush"): return int(arg)
    if op.startswith("ldc") and com.startswith("int "): return int(com[4:])
    return None


class _Obj:
    def __init__(s, cls): s.cls, s.f = cls, {}


class _Jvm:
    """just enough of the JVM for the colour lambdas of client-1.20.1.jar: ints, floats, doubles, null, objects with
    fields, branches, calls into the jar's own methods (else null / 0); `hooks` answer the calls that need game state"""
    def __init__(s, jar):
        s.jar = jar; s.z = zipfile.ZipFile(jar); s.names = {n[:-6] for n in s.z.namelist() if n.endswith(".class") and "/" not in n}
        s._c = {}; s.hooks = {}; s.grass = None

    def _is_grass(s, cn):
        """GrassColor.get(temperature, downfall): a static (DD)I that answers -65281 for a pixel outside the colormap"""
        c = s.cls(cn); _, ins = c.method("a", "(DD)I") if c else (None, None)
        return bool(ins) and any(_int(*i[1:]) == -65281 for i in ins)

    def cls(s, n):
        if n not in s._c:
            if n not in s.names: s._c[n] = None
            else:
                t = subprocess.run(["javap", "-cp", s.jar, "-c", "-p", "-s", "-v", "-constants", n], capture_output=True, text=True).stdout
                s._c[n] = _Class(n, t)
        return s._c[n]

    def having(s, *needles):
        """root classes whose bytes contain every needle"""
        out = []
        for n in sorted(s.names):
            b = s.z.read(n + ".class")
            if all(x in b for x in needles): out.append(n)
        return out

    def run(s, cn, key, args, d=0):
        if d > 16: return None
        c = s.cls(cn)
        if not c: return None
        k, ins = c.method(*key) if isinstance(key, tuple) else c.method(key)
        if not ins: return None
        loc, slot = {}, 0   # arguments into local slots (a long or double takes two); `this` first when there is one
        kinds = re.findall(r"\[*(?:L[^;]+;|[ZBCSIFJD])", k[1][1:k[1].index(")")])
        for a, kd in zip(args, ([None] if len(args) > len(kinds) else []) + kinds):
            loc[slot] = a; slot += 2 if kd in ("J", "D") else 1
        st = []; pos = {o: i for i, (o, *_) in enumerate(ins)}; pc = 0; n = 0
        while pc < len(ins) and n < 5000:
            n += 1; off, op, arg, com = ins[pc]; pc += 1
            v = _int(op, arg, com)
            if v is not None: st.append(v); continue
            if op.startswith("ldc"):
                st.append(float(com.split()[1].rstrip("fd")) if com.startswith(("float", "double")) else com.split(" ", 1)[1] if com.startswith("String") else None)
            elif op in ("dconst_0", "dconst_1", "fconst_0", "fconst_1", "fconst_2"): st.append(float(op[-1]))
            elif op == "aconst_null": st.append(None)
            elif op[1:5] == "load": st.append(loc.get(int(op[-1]) if "_" in op else int(arg)))
            elif op[1:6] == "store": loc[int(op[-1]) if "_" in op else int(arg)] = st.pop()
            elif op in ("dup",): st.append(st[-1])
            elif op in ("pop",): st.pop()
            elif op == "checkcast": pass
            elif op == "instanceof": st.pop(); st.append(0)
            elif op == "new": st.append(_Obj(com.split()[-1]))
            elif op == "getfield":
                o = st.pop(); st.append(o.f.get(_ref(com)[1]) if isinstance(o, _Obj) else None)
            elif op == "putfield":
                v = st.pop(); o = st.pop()
                if isinstance(o, _Obj): o.f[_ref(com)[1]] = v
            elif op == "getstatic": st.append(("static",) + _ref(com)[:2])
            elif op == "putstatic": st.pop()
            elif op.startswith("invoke") and op != "invokedynamic":
                own, nm, desc = _ref(com); own = own or cn
                na = len(re.findall(r"\[*(?:L[^;]+;|[ZBCSIFJD])", desc[1:desc.index(")")]))
                a = [st.pop() for _ in range(na)][::-1]
                recv = st.pop() if op != "invokestatic" else None
                h = s.hooks.get((own, nm, desc))
                if h is None and desc == "(DD)I" and s.grass and s._is_grass(own): h = s.grass
                if h: r = h(recv, a)
                elif nm == "<init>": r = s.run(own, (nm, desc), [recv] + a, d + 1) if isinstance(recv, _Obj) and recv.cls == own else None
                else:
                    tgt = recv.cls if isinstance(recv, _Obj) and s.cls(recv.cls) and s.cls(recv.cls).method(nm, desc)[1] else own
                    r = s.run(tgt, (nm, desc), ([] if op == "invokestatic" else [recv]) + a, d + 1)
                rt = desc[desc.index(")") + 1:]
                if rt != "V": st.append(r if r is not None or rt[0] in "L[" else 0)
            elif op in ("i2f", "i2d", "f2d", "d2f"): st.append(float(st.pop() or 0))
            elif op in ("f2i", "d2i"): st.append(int(st.pop() or 0))
            elif op[0] in "ifd" and op[1:] in ("add", "sub", "mul", "div"):
                b, a = st.pop() or 0, st.pop() or 0
                r = a + b if op[1:] == "add" else a - b if op[1:] == "sub" else a * b if op[1:] == "mul" else (a / b if op[0] != "i" else int(a / b)) if b else 0
                st.append(_f32(r) if op[0] == "f" else r)
            elif op in ("iand", "ior", "ishl", "ishr", "iushr"):
                b, a = st.pop() or 0, st.pop() or 0
                st.append(a & b if op == "iand" else a | b if op == "ior" else (a << b) & 0xFFFFFFFF if op == "ishl" else a >> b)
            elif op.startswith("if"):
                tgt = int(arg.split()[0])
                num = lambda x: x if isinstance(x, (int, float)) else 0
                if op.startswith("if_acmp"):
                    b, a = st.pop(), st.pop(); r = (a is b or (isinstance(a, tuple) and a == b)) == (op[7:] == "eq")
                elif op.startswith("if_icmp"):
                    b, a = num(st.pop()), num(st.pop()); r = _cmp(op[7:], a, b)
                elif op in ("ifnull", "ifnonnull"): r = (st.pop() is None) == (op == "ifnull")
                else: r = _cmp(op[2:], num(st.pop()), 0)
                if r: pc = pos[tgt]
            elif op in ("goto", "goto_w"): pc = pos[int(arg.split()[0])]
            elif op.endswith("return"): return st.pop() if op != "return" else None
            else: return None   # anything else (arrays, switches, exceptions) is not needed by the colour code
        return None


def _f32(x): return struct.unpack("f", struct.pack("f", x))[0]


def _cmp(c, a, b): return a == b if c == "eq" else a != b if c == "ne" else a < b if c == "lt" else a >= b if c == "ge" else a > b if c == "gt" else a <= b


def _registrations(c, owner):
    """[(lambda 'owner.name:desc', what the lambda captures (its indy descriptor's arguments), [static fields])] for
    each `owner.register(Color, ItemLike/Block...)` call in c's methods (an invokevirtual on its own class taking an
    array as the last argument, after an invokedynamic)"""
    out = []
    for key, ins in c.methods.items():
        lam, cap, fields = None, [], []
        for off, op, arg, com in ins:
            if op == "invokedynamic":
                m = re.search(r"InvokeDynamic #(\d+):\w+:\(([^)]*)\)", com)
                lam = c.boot[int(m.group(1))] if m and int(m.group(1)) < len(c.boot) else None
                cap = re.findall(r"L([^;]+);", m.group(2)) if m else []; fields = []
            elif op == "getstatic": fields.append(_ref(com)[:2])
            elif op == "invokevirtual" and lam and (_ref(com)[0] in (None, owner)) and re.search(r";\[L[^;]+;\)V$", com):
                out.append((lam, cap, fields)); lam, cap, fields = None, [], []
    return out


class Vanilla:
    def __init__(s, client_jar, colormap=None):
        """colormap(name) -> RGBA image of textures/colormap/<name>.png (GrassColor reads its pixels); default: the jar"""
        J = s.J = _Jvm(client_jar)
        z = J.z
        def cmap(n):
            from PIL import Image
            if colormap: return colormap(n)
            return Image.open(io.BytesIO(z.read(f"assets/minecraft/textures/colormap/{n}.png"))).convert("RGBA")
        # registries: static field -> registry name, from <clinit> (ldc "name" ... putstatic F)
        s.items_cls = J.having(b"allay_spawn_egg", b"netherite_sword")[0]
        s.blocks_cls = max(J.having(b"grass_block", b"lily_pad", b"mangrove_leaves"), key=lambda n: len(J.cls(n).fields))
        s.eggs = {}
        s.block_names = s._names(s.blocks_cls)
        s.item_names = s._names(s.items_cls, eggs=True)
        # ItemColors / BlockColors
        s.ic_cls = [n for n in J.having(b"Explosion", b"Colors", b"getColor") if J.cls(n).boot][0]
        fac = [k for k in J.cls(s.ic_cls).methods if k[1].endswith(")L" + s.ic_cls + ";") and k[1].count("L") == 2][0]
        s.bc_cls = fac[1][2:fac[1].index(";")]
        s.ic = _registrations(J.cls(s.ic_cls), s.ic_cls)
        s.bc = _registrations(J.cls(s.bc_cls), s.bc_cls)
        s.potion_cls = [n for n in J.having(b"CustomPotionColor", b"CustomPotionEffects") if J.cls(n).method("a", "(Ljava/util/Collection;)I")[1]][0]
        # hooks: GrassColor.get(t, d) reads colormap/grass.png (pixels[(1 - d·t)·255 << 8 | (1 - t)·255]);
        # PotionUtils.getColor(stack) and BlockColors.getColor(state, level, pos, i) are answered by the caller
        px = cmap("grass")
        def grass(recv, a):
            t, dn = a[0], a[1] * a[0]
            r, g, b, _ = px.getpixel((int((1 - t) * 255), int((1 - dn) * 255))); return (r << 16) | (g << 8) | b
        J.grass = grass
        J.hooks[(s.potion_cls, "c", "(L%s;)I" % s._stack())] = lambda recv, a: ("POTION",)
        for (nm, desc) in J.cls(s.bc_cls).methods:
            if nm == "a" and desc.endswith("I)I") and desc.count(";") == 3:   # BlockColors.getColor(state, level, pos, tintindex)
                J.hooks[(s.bc_cls, nm, desc)] = lambda recv, a: ("BLOCK", a[3])
        s.dyes = s._dyes()
        s.effects, s.effect_field = s._effects()
        s.potions = s._potions()
        s.empty_potion, s.water = s._potion_consts()

    def _stack(s):
        """the ItemStack class: ItemColor.getColor's first parameter"""
        lam = [l for l, cap, f in s.ic if not cap][0]; d = lam.split(":", 1)[1]
        return re.findall(r"L([^;]+);", d)[0]

    def _names(s, cn, eggs=False):
        c = s.J.cls(cn); _, ins = c.method("<clinit>")
        out, strs, ints, egg_cls = {}, [], [], None
        for off, op, arg, com in ins:
            v = _int(op, arg, com)
            if v is not None: ints.append(v)
            elif op.startswith("ldc") and com.startswith("String "): strs.append(com[7:])
            elif op == "getstatic" and not strs and _ref(com)[0] == s.blocks_cls: strs.append(("block", _ref(com)[1]))
            elif eggs and op == "invokespecial" and re.search(r"<init>\":\(L[^;]+;IIL[^;]+;\)V", com) and strs and isinstance(strs[0], str) and strs[0].endswith("_spawn_egg"):
                egg_cls = _ref(com)[0]; s.eggs.setdefault("minecraft:" + strs[0], (ints[-2], ints[-1]))
            elif op == "putstatic":
                f = _ref(com)[1]
                if strs:
                    nm = strs[0] if isinstance(strs[0], str) else getattr(s, "block_names", {}).get(strs[0][1])
                    if nm: out[f] = "minecraft:" + nm if ":" not in nm else nm
                strs, ints = [], []
        if eggs: s.egg_cls = egg_cls
        return out

    def _dyes(s):
        """DyeColor.<clinit>: new DyeColor(ENUM, ordinal, id, name, textureDiffuse, MapColor, fireworkColor, textColor)"""
        J = s.J; cn = [n for n in J.having(b"LIGHT_BLUE", b"light_blue", b"MAGENTA") if J.cls(n).method("<clinit>")[1]]
        cn = min(cn, key=lambda n: len(J.cls(n).methods)); _, ins = J.cls(cn).method("<clinit>")
        out, strs, ints = {}, [], []
        for off, op, arg, com in ins:
            v = _int(op, arg, com)
            if v is not None: ints.append(v)
            elif op.startswith("ldc") and com.startswith("String "): strs.append(com[7:])
            elif op == "invokespecial" and len(strs) == 2 and len(ints) >= 5:
                out[strs[0]] = {"ord": ints[0], "id": ints[1], "name": strs[1], "diffuse": ints[2], "firework": ints[-2], "text": ints[-1]}
            if op in ("putstatic", "invokespecial"): strs, ints = ([], []) if op == "putstatic" else (strs, ints)
        return out

    def _effects(s):
        J = s.J; cn = J.having(b"instant_health", b"night_vision", b"bad_omen")
        cn = [n for n in cn if J.cls(n).method("<clinit>")[1] and len(J.cls(n).fields) > 30][0]
        _, ins = J.cls(cn).method("<clinit>")
        # register(id, "name", new X(MobEffectCategory.C, colour[, ...])): the first int after the category is the colour
        col, field, nm, cat = {}, {}, None, False
        for off, op, arg, com in ins:
            if op.startswith("ldc") and com.startswith("String ") and nm is None: nm = com[7:]
            v = _int(op, arg, com)
            if op == "getstatic" and nm: cat = True
            elif v is not None and cat and nm and "minecraft:" + nm not in col: col["minecraft:" + nm] = v; cat = False
            if op == "putstatic" and nm: field[_ref(com)[1]] = "minecraft:" + nm; nm, cat = None, False
        s.effects_cls = cn
        # MobEffect itself: the last parameter of MobEffects.register(int id, String name, MobEffect effect)
        s.effect_base = next(m.group(1) for o, op, a, c in ins if op == "invokestatic" for m in [re.search(r"\(ILjava/lang/String;L([^;]+);\)", c)] if m)
        return col, field

    def _potions(s):
        """potion id -> [(effect id, amplifier)] from Potions.<clinit> (new MobEffectInstance(effect, duration[, amp]))"""
        J = s.J; cn = [n for n in J.having(b"long_night_vision", b"strong_healing") if J.cls(n).method("<clinit>")[1]]
        cn = max(cn, key=lambda n: len(J.cls(n).fields)); _, ins = J.cls(cn).method("<clinit>")
        out, nm, eff, ints, cur = {}, None, [], [], None
        for off, op, arg, com in ins:
            if op.startswith("ldc") and com.startswith("String ") and nm is None: nm = com[7:]
            v = _int(op, arg, com)
            if v is not None: ints.append(v)
            if op == "getstatic" and _ref(com)[0] == s.effects_cls: cur = s.effect_field.get(_ref(com)[1]); ints = []
            if op == "invokespecial" and cur and re.search(r"\(L%s;II?\)V$" % re.escape(s.effect_base), com):
                eff.append((cur, ints[1] if len(ints) > 1 else 0)); cur = None   # (effect, duration[, amplifier])
            if op == "putstatic" and nm: out["minecraft:" + nm] = eff; nm, eff = None, []
        return out

    def _potion_consts(s):
        c = s.J.cls(s.potion_cls)
        _, ins = c.method("a", "(Ljava/util/Collection;)I")
        water = next(_int(*i[1:]) for i in ins if _int(*i[1:]) is not None)
        k, ins2 = c.method("c", "(L%s;)I" % s._stack())
        empty = [v for v in (_int(*i[1:]) for i in ins2) if v is not None and v > 255]
        return (empty[0] if empty else None), water

    def potion_colour(s, effects):
        """PotionUtils.getColor(Collection<MobEffectInstance>): weighted by amplifier + 1, float arithmetic, f2i"""
        if not effects: return s.water
        r = g = b = 0.0; n = 0
        for e, amp in effects:
            c = s.effects[e]; w = amp + 1
            r = _f32(r + _f32(w * ((c >> 16) & 255) / 255.0)); g = _f32(g + _f32(w * ((c >> 8) & 255) / 255.0)); b = _f32(b + _f32(w * (c & 255) / 255.0)); n += w
        return int(_f32(_f32(r / n) * 255.0)) << 16 | int(_f32(_f32(g / n) * 255.0)) << 8 | int(_f32(_f32(b / n) * 255.0))

    def colour(s, item, layer, potion=None):
        """what ItemColors returns for `item` (an id) at tintindex `layer`; None = no entry; -1 = untinted"""
        J = s.J; stack = _Obj(s._stack())
        for lam, cap, fields in s.ic:
            if not lam: continue
            own, rest = lam.split(".", 1); nm, desc = rest.split(":", 1)
            if cap == [s.egg_cls]:   # for (SpawnEggItem egg : SpawnEggItem.eggs()) register((stack, i) -> egg.getColor(i), egg)
                if item not in s.eggs: continue
                egg = _Obj(s.egg_cls); p, q = s.eggs[item]
                init = [k for k in J.cls(s.egg_cls).methods if k[0] == "<init>" and re.match(r"\(L[^;]+;IIL[^;]+;\)V", k[1])][0]
                J.run(s.egg_cls, init, [egg, None, p, q, None])
                args = [egg, stack, layer]
            else:
                names = [s.item_names.get(f) if o == s.items_cls else s.block_names.get(f) if o == s.blocks_cls else None for o, f in fields]
                if item not in names: continue
                args = ([_Obj(s.bc_cls)] if desc.startswith("(L" + s.bc_cls) else []) + [stack, layer]
            v = J.run(own, (nm, desc), args)
            if isinstance(v, tuple) and v[0] == "POTION":
                v = s.potion_colour(s.potions[potion]) if potion else s.empty_potion; s.used_potion = True
            if isinstance(v, tuple) and v[0] == "BLOCK": v = s.block_colour(item, v[1])
            return v
        return None

    def block_colour(s, block, layer):
        for lam, cap, fields in s.bc:
            if not lam: continue
            if block not in [s.block_names.get(f) for o, f in fields if o == s.blocks_cls]: continue
            own, rest = lam.split(".", 1); nm, desc = rest.split(":", 1)
            return s.J.run(own, (nm, desc), [None, None, None, layer])   # no level, no position: the item's default
        return -1


# ---------------------------------------------------------------- mods: registration and colour handler code in mjvm
def _mod_vm():
    import mjvm
    O, OP, Op = mjvm.Obj, mjvm.OP, mjvm.Opaque
    DYE = "net/minecraft/world/item/DyeColor"

    class TintVM(mjvm.VM):
        EGGS = ("net/minecraftforge/common/ForgeSpawnEggItem", "net/minecraft/world/item/SpawnEggItem")

        def __init__(s, jars, vanilla):
            super().__init__(jars); s.colour_regs = []; s.keep_reg = 0; s.tag_fields = False; s.V = vanilla; s.lamname = {}; s.potion = None; s.used_potion = False

        def init(s, cls, desc, o, args):
            if cls in s.EGGS:   # (Supplier<EntityType> | EntityType, int primary, int secondary, Properties)
                if isinstance(o, O): o.f["$egg"] = (args[0], args[1], args[2])
                return
            return super().init(cls, desc, o, args)

        def call_lam(s, l, args):
            if l.name == "register" and l.owner.endswith("RegisterColorHandlersEvent$Item") and len(l.cap) + len(args) >= 3:
                a = list(l.cap) + list(args); s.colour_regs.append((a[-2], a[-1])); return None   # event::register as a BiConsumer
            r = super().call_lam(l, args)
            nm = s.lamname.get(id(l))
            if nm and nm[1] is l and isinstance(r, O) and not isinstance(r.f.get("$regname"), str): r.f["$regname"] = nm[0]
            return r

        def capture(s, name, args, ret):
            """a registration call (an 'ns:path' id and the supplier that makes the item): the supplier remembers the id"""
            ids = [a for a in args if isinstance(a, str) and re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_/.-]+", a)]
            for a in args:
                if ids and isinstance(a, mjvm.Lam): s.lamname.setdefault(id(a), (ids[0], a))
            return super().capture(name, args, ret)

        def getstatic(s, cls, name, desc):
            if cls == DYE and name in s.V.dyes: return mjvm.EnumC(cls, name, s.V.dyes[name]["ord"])
            v = super().getstatic(cls, name, desc)
            if s.tag_fields and isinstance(v, Op) and not cls.startswith(("net/minecraft/", "net/minecraftforge/", "java/")) \
                    and desc.startswith("L") and v.d not in ("props",):
                return Op("F:%s.%s" % (cls, name))   # an item field whose registration the interpreter could not follow
            return v

        def invoke(s, kind, cls, name, desc, args, recv=None):
            rt = mjvm.rettype(desc); V = s.V
            if isinstance(recv, O) and recv.cls == "$event":
                if name == "register" and desc.startswith("(Lnet/minecraft/client/color/item/ItemColor;"):
                    s.colour_regs.append((args[0], args[1])); return None
                if name == "getItemColors": return O("$itemcolors")
                return OP if rt != "V" else None
            if isinstance(recv, O) and recv.cls == "$itemcolors" and name in ("m_92689_", "register"):
                s.colour_regs.append((args[0], args[1])); return None
            if rt == "Lnet/minecraft/client/color/item/ItemColors;": return O("$itemcolors")   # Minecraft.getItemColors(), accessors
            if isinstance(recv, O) and recv.cls == "$stack":   # an ItemStack of the item, count 1, no NBT
                it = recv.f.get("$item")
                if name == "m_41720_": return it if it is not None else OP              # getItem
                if name in ("m_41783_", "m_41737_", "m_41618_"): return None             # getTag, getTagElement, getEnchantmentTags
                if name in ("m_41782_", "m_41619_", "m_41788_"): return 0                # hasTag, isEmpty, hasCustomHoverName
                if name == "m_41613_": return 1                                          # getCount
                if name == "m_150930_" and args and isinstance(it, O): return 1 if args[0] is it else 0
                if name in ("m_41784_", "m_41698_"): return O("$tag")                    # getOrCreateTag(Element)
                return OP if rt != "V" else None
            if isinstance(recv, O) and recv.cls == "$tag":   # an empty CompoundTag
                if rt in ("I", "Z", "B", "S", "J"): return 0
                if rt in ("F", "D"): return 0.0
                if rt == "Ljava/lang/String;": return ""
                return O("$tag") if rt.startswith("Lnet/minecraft/nbt/") else None
            if isinstance(recv, mjvm.EnumC) and recv.cls == DYE:
                d = V.dyes[recv.name]
                if name == "m_41071_": return d["text"]                                  # getTextColor
                if name == "m_41070_": return d["firework"]                              # getFireworkColor
                if name == "m_41060_": return d["id"]                                    # getId
                if name in ("m_41065_", "m_7912_"): return d["name"]                     # getName, getSerializedName
                if name == "m_41068_":                                                   # getTextureDiffuseColors
                    a = mjvm.Arr(3); c = d["diffuse"]; a.v = [_f32(((c >> k) & 255) / 255.0) for k in (16, 8, 0)]; return a
            if cls == DYE and name in ("m_41057_", "m_41053_"):                          # byName(name, default), byId(id)
                hit = [k for k, d in V.dyes.items() if d["name" if name == "m_41057_" else "id"] == args[0]]
                return mjvm.EnumC(DYE, hit[0], V.dyes[hit[0]]["ord"]) if hit else (args[1] if name == "m_41057_" else OP)
            if name == "m_41121_" and isinstance(recv, O):   # DyeableLeatherItem.getColor(stack): the item's override, else vanilla's default
                r = s.find(recv.cls, name, desc)
                if not (r and r[2].code and not r[0].startswith("net/minecraft/")): return V.colour("minecraft:leather_helmet", 0)
            if cls == "net/minecraft/world/item/alchemy/PotionUtils" and name == "m_43575_":   # getColor(stack): no NBT, or the caller's potion
                s.used_potion = True
                return V.potion_colour(V.potions[s.potion]) if s.potion else V.empty_potion
            if cls == "net/minecraft/world/item/alchemy/PotionUtils" and name == "m_43564_": return V.water          # getColor(Collection)
            if cls == "net/minecraft/world/level/GrassColor":
                if name == "m_276205_": return V.block_colour("minecraft:grass", 0)          # getDefaultColor
                if name == "m_46415_" and all(mjvm.num(a) for a in args): return V.J.grass(None, args)
            if cls == "net/minecraft/world/level/FoliageColor":
                v = {"m_46106_": "minecraft:spruce_leaves", "m_46112_": "minecraft:birch_leaves", "m_46113_": "minecraft:oak_leaves",
                     "m_220346_": "minecraft:mangrove_leaves"}.get(name)
                if v: return V.block_colour(v, 0)
            if name in ("get", "m_123015_") and isinstance(recv, mjvm.RegObj) and s.keep_reg: return recv
            if name in ("get", "asItem", "m_5456_") and isinstance(recv, Op) and recv.d.startswith("F:"): return recv
            if cls == "java/util/Collections" and name == "singletonMap": m = mjvm.MMap(); m.items.append((args[0], args[1])); return m
            v = super().invoke(kind, cls, name, desc, args, recv)
            if isinstance(v, Op) and rt == "Ljava/util/function/Supplier;" and any(id(a) in s.lamname for a in args if isinstance(a, mjvm.Lam)):
                return next(a for a in args if isinstance(a, mjvm.Lam) and id(a) in s.lamname)   # register(id, supplier) -> a supplier of it
            return v

    return TintVM, mjvm


class Mods:
    def __init__(s, jars, vanilla):
        TintVM, mjvm = _mod_vm()
        s.mjvm = mjvm; s.jars = list(jars); s.V = vanilla
        s.vm = TintVM(s.jars, vanilla)
        s.models, s.jar_ns = {}, {}   # item model path -> namespaces; jar -> namespaces with item models
        for j in s.jars:
            try: z = zipfile.ZipFile(j)
            except Exception: continue
            for n in z.namelist():
                m = re.match(r"assets/([^/]+)/models/item/(.+)\.json$", n)
                if m: s.models.setdefault(m.group(2), set()).add(m.group(1)); s.jar_ns.setdefault(z.filename, set()).add(m.group(1))
        s.eggs, s.handlers = {}, []
        s._read_eggs(); s._read_handlers()

    def _classes_with(s, *needles):
        out = []
        for cls, (z, n) in s.vm.idx.items():
            try: b = z.read(n)
            except Exception: continue
            if any(x in b for x in needles): out.append(cls)
        return sorted(out)

    def _regname(s, name, ns=None, cls=None):
        """'ns:name'; without a namespace, the one namespace whose item model has that path (in the class's own jar first)"""
        if not isinstance(name, str): return None
        if ":" in name: return name
        if ns: return ns + ":" + name
        nss = set(s.models.get(name, ()))
        if cls and cls in s.vm.idx: nss = (nss & s.jar_ns.get(s.vm.idx[cls][0].filename, set())) or nss
        return (sorted(nss)[0] + ":" + name) if len(nss) == 1 else None

    def _read_eggs(s):
        vm, mjvm = s.vm, s.mjvm
        for cls in s._classes_with(b"SpawnEggItem"):
            if cls.startswith(("net/minecraft/", "net/minecraftforge/")): continue
            try: vm.clinit(cls)
            except Exception as e: vm.err(cls, "<clinit>", None, e)
        def egg_of(v, d=0):
            if isinstance(v, mjvm.Obj) and "$egg" in v.f: return v
            if isinstance(v, (mjvm.Lam, mjvm.RegObj)) and d < 3:
                try: return egg_of(vm.resolve(v), d + 1)
                except Exception: return None
            return None
        cands = [(getattr(v, "ns", None), v.name, v, c) for (c, f), v in list(vm.statics.items()) if isinstance(v, mjvm.RegObj)]
        cands += [(None, n, v, None) for n, v in vm.regs if isinstance(n, str)]
        for ns, name, v, cls in cands:
            rid = s._regname(name, ns, cls)
            if not rid or rid in s.eggs: continue
            o = egg_of(v)
            if o is None: continue
            ent, p, q = o.f["$egg"]
            if not (isinstance(p, int) and isinstance(q, int)): continue
            s.eggs.setdefault(rid, (s._entity(ent), p & 0xFFFFFF, q & 0xFFFFFF, "mod jar, registration run in mjvm: new %s(entity, %d, %d)" % (o.cls.split("/")[-1], p, q)))

    def _entity(s, e):
        mjvm = s.mjvm
        if isinstance(e, mjvm.RegObj): return s._regname(e.name, getattr(e, "ns", None))
        if isinstance(e, mjvm.Lam):   # () -> ModEntities.X.get(): keep the RegistryObject
            s.vm.keep_reg += 1
            try: r = s.vm.call_lam(e, [])
            except Exception: r = None
            finally: s.vm.keep_reg -= 1
            if isinstance(r, mjvm.RegObj): return s._entity(r)
        return None

    def _read_handlers(s):
        """run every method that registers item colours: event handlers (they take RegisterColorHandlersEvent.Item) and
        code that calls ItemColors.register or the event's register itself (Minecraft.getInstance().getItemColors(),
        a Runnable); helpers that take the ItemColor as a parameter run from their callers"""
        vm, mjvm = s.vm, s.mjvm
        REG = ("net/minecraftforge/client/event/RegisterColorHandlersEvent$Item", "net/minecraft/client/color/item/ItemColors")
        vm.tag_fields = True
        for cls in s._classes_with(b"RegisterColorHandlersEvent$Item", b"m_92689_"):
            k = vm.cf(cls)
            if not k: continue
            for m in k.methods:
                if not m.code: continue
                d = m.descriptor.value
                if "Lnet/minecraft/client/color/item/ItemColor;" in d: continue   # a helper: its callers pass the colour
                calls = "RegisterColorHandlersEvent$Item;" in d
                for x in m.code.disassemble():
                    if x.mnemonic.startswith("invoke") and x.mnemonic != "invokedynamic":
                        r = k.constants.get(x.operands[0].value)
                        try: own, nm = r.class_.name.value, r.name_and_type.name.value
                        except Exception: continue
                        if own in REG and nm in ("register", "m_92689_"): calls = True; break
                if not calls: continue
                args = [] if m.access_flags.get("acc_static") else [mjvm.Obj(cls)]
                args += [mjvm.Obj("$event") if "ColorHandlersEvent" in t else mjvm.OP for t in re.findall(r"L[^;]+;|\[*[ZBCSIFJD]", d[1:d.index(")")])]
                n0 = len(vm.colour_regs)
                try: vm.run(cls, k, m, args)
                except Exception as e: vm.err(cls, m.name.value, None, e)
                for lam, items in vm.colour_regs[n0:]:
                    s.handlers.append((cls + "." + m.name.value, lam, items, cls))
        vm.tag_fields = False

    def items_of(s, items, cls=None):
        """[(item id, item object or None, how the id was found)]"""
        vm, mjvm = s.vm, s.mjvm
        vals = items.v if isinstance(items, mjvm.Arr) else (items.items and [v for _, v in items.items]) if isinstance(items, mjvm.MMap) else [items]
        out = []
        for v in vals:
            reg = v if isinstance(v, mjvm.RegObj) else None
            if isinstance(v, mjvm.Obj) and not isinstance(v.f.get("$regname"), str):   # a mod's wrapper around a RegistryObject
                reg = next((x for x in v.f.values() if isinstance(x, mjvm.RegObj)), None)
            if reg is not None:
                try: o = vm.resolve(reg)
                except Exception: o = None
                out.append((s._regname(reg.name, getattr(reg, "ns", None), cls), o if isinstance(o, mjvm.Obj) else None, "registry"))
            elif isinstance(v, mjvm.Obj) and isinstance(v.f.get("$regname"), str):
                out.append((v.f["$regname"], v, "registry"))
            elif isinstance(v, mjvm.Opaque) and v.d.startswith("F:"):   # Registrate and the like: the field's name
                c, f = v.d[2:].rsplit(".", 1)
                out.append((s._regname(f.lower(), None, c), None, "field name %s.%s" % (c.split("/")[-1], f)))
        return out

    def handler_tints(s):
        """{item id: (colour handler, item object, ItemColor, how the id was found)}"""
        out = {}
        for where, lam, items, cls in s.handlers:
            for rid, o, how in s.items_of(items, cls):
                if rid: out.setdefault(rid, (where, o, lam, how))
        return out

    def colour(s, entry, layer, potion=None):
        """the handler's ItemColor for a stack of the item without NBT (potion: what PotionUtils.getColor(stack) answers)"""
        where, o, lam, how = entry
        st = s.mjvm.Obj("$stack"); st.f["$item"] = o
        if not isinstance(lam, s.mjvm.Lam): return None
        s.vm.potion = potion
        try: v = s.vm.call_lam(lam, [st, layer])
        except Exception: return None
        finally: s.vm.potion = None
        return v if isinstance(v, int) and not isinstance(v, bool) else None


# ---------------------------------------------------------------- one entry point
# A potion-coloured item named without its potion (a recipe's "Potion", Goety's "Brew") is drawn as the plain water
# bottle (no effects, PotionUtils' 0x385DC6) rather than the magenta "Uncraftable Potion" a stack without NBT would be.
DEFAULT_POTION = "minecraft:water"


class Tints:
    def __init__(s, client_jar, mod_jars=(), colormap=None):
        s.v = Vanilla(client_jar, colormap)
        s.m = Mods(mod_jars, s.v) if mod_jars else None
        s.eggs = {k: ("minecraft:" + k.split(":")[1][:-len("_spawn_egg")], p, q, "client jar: Items.<clinit>") for k, (p, q) in s.v.eggs.items()}
        if s.m:
            for k, v in s.m.eggs.items(): s.eggs.setdefault(k, v)
        s.handlers = s.m.handler_tints() if s.m else {}
        s._egg_of = {}
        for k in sorted(s.eggs):
            if s.eggs[k][0]: s._egg_of.setdefault(s.eggs[k][0], k)

    def egg_for(s, entity):
        """the spawn egg whose constructor names this entity (ids such as alexscaves:spawn_egg_caniac or
        mowziesmobs:wroughtnaut_spawn_egg do not follow <entity>_spawn_egg), else <entity>_spawn_egg if that egg exists"""
        return s._egg_of.get(entity) or (entity + "_spawn_egg" if entity + "_spawn_egg" in s.eggs else None)

    def tint(s, item, layers=2, potion=DEFAULT_POTION):
        """({tintindex: 0xRRGGBB} for tint indices 0 .. layers-1 that are tinted, source) or (None, why not).
        A mod's own colour handler wins over the spawn-egg rule (it registers later, as ItemColors keeps the last).
        potion: what PotionUtils.getColor answers for the stack (potions, tipped arrows, Goety's brews ...); None gives
        what a stack without NBT really shows, the magenta "Uncraftable Potion"."""
        out, unk = {}, []
        s.v.used_potion = False
        if s.m: s.m.vm.used_potion = False
        if item.startswith("minecraft:") and s.v.colour(item, 0, potion) is not None:
            for i in range(layers):
                c = s.v.colour(item, i, potion)
                if isinstance(c, int) and c != -1: out[i] = c & 0xFFFFFF
            src = "client jar: ItemColors" + (" + PotionUtils(%s)" % (potion or "no NBT") if s.v.used_potion else "")
        elif item in s.handlers:
            e = s.handlers[item]; src = "mod colour handler %s (item found by %s)" % (e[0], e[3])
            for i in range(layers):
                c = s.m.colour(e, i, potion)
                if c is None: unk.append(i)
                elif c != -1: out[i] = c & 0xFFFFFF
            if s.m.vm.used_potion: src += ", PotionUtils as %s" % (potion or "no NBT")
            if unk: src += "; tintindex %s not decided, left untinted" % ",".join(map(str, unk))
        elif item in s.eggs:
            ent, p, q, src = s.eggs[item]
            out = {i: (p if i == 0 else q) for i in range(layers)}
        else:
            return None, "no ItemColors entry"
        return (out, src) if out else (None, "ItemColors entry, untinted: " + src)


if __name__ == "__main__":
    # python3 tints.py client.jar [mod jars...]: print every colour read
    import glob, json
    a = sys.argv[1:]
    T = Tints(a[0], [j for x in a[1:] for j in sorted(glob.glob(x))])
    print(json.dumps({"vanilla eggs": len(T.v.eggs), "mod eggs": len(T.m.eggs) if T.m else 0, "handlers": len(T.handlers)}))
    for k in sorted(T.eggs): print(k, "%06X %06X" % T.eggs[k][1:3], T.eggs[k][0], T.eggs[k][3])
