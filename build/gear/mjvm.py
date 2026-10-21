"""Tiny symbolic JVM: runs mod item-registration code far enough to read
weapon damage / attack speed and armor values the way the mods construct them.
Vanilla base classes (SwordItem, DiggerItem, ArmorItem, Tiers, ArmorMaterials)
are modelled, not interpreted. Unknown calls return Opaque values."""
import zipfile, io, re, struct, sys, glob, json
from jawa.cf import ClassFile
import jawa.constants as C

class Opaque:
    __slots__ = ('d',)
    def __init__(s, d=''): s.d = d
    def __repr__(s): return 'Op(%s)' % s.d
OP = Opaque()

class Obj:
    def __init__(s, cls):
        s.cls = cls; s.f = {}; s.gear = {}; s.mods = []
    def __repr__(s): return 'Obj(%s)' % s.cls

_EC = {}
class EnumC:
    def __new__(c, cls, name, ordinal):
        k = (cls, name)
        if k in _EC: return _EC[k]
        o = object.__new__(c); o.cls, o.name, o.ord = cls, name, ordinal; _EC[k] = o
        return o
    def __init__(s, cls, name, ordinal): pass
    def __repr__(s): return 'E(%s.%s)' % (s.cls.split('/')[-1], s.name)

class Lam:
    def __init__(s, kind, owner, name, desc, cap): s.kind, s.owner, s.name, s.desc, s.cap = kind, owner, name, desc, cap
    def __repr__(s): return 'Lam(%s.%s)' % (s.owner.split('/')[-1], s.name)

class Arr:
    def __init__(s, n): s.v = [0] * n if isinstance(n, int) and n < 4096 else []

class MMap:  # multimap / map / builder / list
    def __init__(s): s.items = []

class Entry:  # Map.Entry
    def __init__(s, k, v): s.k, s.v = k, v

class Iter:
    def __init__(s, el): s.el, s.i = list(el), 0

def view(el):
    m = MMap(); m.items = [(None, e) for e in el]; m.view = True; return m

class RegObj:
    def __init__(s, name, sup): s.name, s.sup = name, sup
    def __repr__(s): return 'Reg(%s)' % s.name

class CfgVal:
    def __init__(s, key, dflt, path=None): s.key, s.dflt, s.path = key, dflt, path
    def __repr__(s): return 'Cfg(%s)' % s.key

CFG = {}  # key -> [(file, value)]
CFGP = {}  # full dotted toml path -> [(file, value)]
CFG_NS = ['']
CFG_AMBIG = set()  # (ns prefix, key, values): leaf key found with different values in several config files
def load_cfg(root):
    import os, tomllib
    def walk(path, d, f):
        if isinstance(d, dict):
            for k, v in d.items(): walk(path + [k], v, f)
        elif isinstance(d, (int, float)) and not isinstance(d, bool) and path:
            CFG.setdefault(path[-1], []).append((f, d)); CFGP.setdefault('.'.join(path), []).append((f, d))
    for dp, _, fs in os.walk(root):
        for fn in fs:
            fp = os.path.join(dp, fn); t = None
            try:
                raw = open(fp, encoding='utf8', errors='ignore').read()
                if fn.endswith('.omniconf'):  # Omniconfig (Enigmatic mods): '    D:TheTwistAttackDamage=8.0'
                    for mm in re.finditer(r'(?m)^\s*[DIFL]:(\w+)=(-?[0-9.]+(?:[eE][-+]?[0-9]+)?)\s*$', raw):
                        v = float(mm.group(2)); CFG.setdefault(mm.group(1), []).append((fp, int(v) if v.is_integer() and '.' not in mm.group(2) else v))
                    continue
                if fn.endswith('.toml'): t = tomllib.loads(raw)
                elif fn.endswith(('.json', '.json5')):
                    r = re.sub(r'(?m)^\s*//.*$', '', raw); r = re.sub(r'/\*.*?\*/', '', r, flags=re.S); r = re.sub(r',(\s*[}\]])', r'\1', r)
                    t = json.loads(r)
            except Exception: t = None
            if t is not None: walk([], t, fp)

def cfg_get(key, dflt, path=None):
    if isinstance(key, list): key = key[-1] if key else None
    if not isinstance(key, str): return dflt
    if path:  # ForgeConfigSpec path known (builder push/pop): exact toml path, the mod's own file first
        c = CFGP.get(path)
        if c:
            pref = [v for f, v in c if CFG_NS[0] and CFG_NS[0] in f.lower()]
            v = (pref or [c[0][1]])[0]
            if isinstance(dflt, int) and not isinstance(dflt, bool) and isinstance(v, float) and v.is_integer(): v = int(v)
            return v
        c = [(f, v) for f, v in CFG.get(key, []) if CFG_NS[0] and CFG_NS[0] in f.lower()]
        if not c: return dflt  # not in the pack's configs: the mod's default applies
    else:
        c = CFG.get(key) or CFG.get(key.split('.')[-1])
    if not c: return dflt
    pref = [v for f, v in c if CFG_NS[0] and CFG_NS[0] in f.lower()]
    cand = pref or [x[1] for x in c]
    if len(set(cand)) > 1: CFG_AMBIG.add((CFG_NS[0], key, tuple(sorted(set(map(str, cand)))[:6])))
    v = (pref or [c[0][1]])[0]
    if isinstance(dflt, int) and not isinstance(dflt, bool) and isinstance(v, float) and v.is_integer(): v = int(v)
    return v

class Attr:
    def __init__(s, n): s.n = n
    def __repr__(s): return 'A(%s)' % s.n

class AMod:
    def __init__(s, amt, op): s.amt, s.op = amt, op

def num(v): return isinstance(v, (int, float)) and not isinstance(v, bool)
IDLIKE = re.compile(r'([a-z0-9_.-]+:)?[a-z0-9_./-]+')
VPFX = ('java/', 'javax/', 'net/minecraft/', 'com/google/', 'com/mojang/', 'net/minecraftforge/', 'org/apache/', 'org/slf4j/', 'org/joml/', 'org/lwjgl/', 'org/objectweb/', 'org/spongepowered/', 'org/jetbrains/', 'org/intellij/', 'org/checkerframework/', 'org/openjdk/', 'org/w3c/', 'org/xml/', 'org/yaml/', 'org/antlr/', 'org/jline/', 'org/tomlj/', 'org/json/', 'it/unimi', 'kotlin/', 'sun/', 'jdk/')

VTIER = {'WOOD': (0, 59, 2.0, 0.0), 'STONE': (1, 131, 4.0, 1.0), 'IRON': (2, 250, 6.0, 2.0),
         'DIAMOND': (3, 1561, 8.0, 3.0), 'GOLD': (0, 32, 12.0, 0.0), 'NETHERITE': (4, 2031, 9.0, 4.0)}
# ArmorMaterials: name -> (defense helmet,chest,legs,boots), toughness, kbr
VARM = {'LEATHER': ((1, 3, 2, 1), 0, 0), 'CHAINMAIL': ((2, 5, 4, 1), 0, 0), 'CHAIN': ((2, 5, 4, 1), 0, 0), 'IRON': ((2, 6, 5, 2), 0, 0),
        'GOLD': ((2, 5, 3, 1), 0, 0), 'DIAMOND': ((3, 8, 6, 3), 2, 0), 'TURTLE': ((2, 6, 5, 2), 0, 0),
        'NETHERITE': ((3, 8, 6, 3), 3, 0.1)}
TYPES = ['HELMET', 'CHESTPLATE', 'LEGGINGS', 'BOOTS']
# getters of the modelled vanilla gear classes (srg): ArmorItem getType/getEquipmentSlot/getDefense/getToughness/getMaterial,
# SwordItem.getDamage, DiggerItem.getAttackDamage, TieredItem.getTier
VGET = {'m_266204_': 'type', 'm_40402_': 'eslot', 'm_40404_': 'arm', 'm_40405_': 'tough', 'm_40401_': 'mat',
        'm_43299_': 'dmg', 'm_41008_': 'dmg', 'm_43314_': 'tier'}
VATTR_DEF = {'generic.max_health': 20.0, 'generic.follow_range': 32.0, 'generic.knockback_resistance': 0.0, 'generic.movement_speed': 0.699999988079071,
             'generic.flying_speed': 0.4000000059604645, 'generic.attack_damage': 2.0, 'generic.attack_knockback': 0.0, 'generic.attack_speed': 4.0,
             'generic.armor': 0.0, 'generic.armor_toughness': 0.0, 'generic.luck': 0.0}  # RangedAttribute defaults, server-1.20.1 Attributes
SRGNAME = {}  # (class, srg field) -> enum constant name
VTIER0, VARM0 = dict(VTIER), dict(VARM)  # canonical-name tables; srg_tables() rebuilds VTIER/VARM keyed by srg field
TYPEF = {}  # srg field -> name, filled from srg jar
EQF = {}
EQS = ['MAINHAND', 'OFFHAND', 'FEET', 'LEGS', 'CHEST', 'HEAD']
EQIDX = {'MAINHAND': 0, 'OFFHAND': 1, 'FEET': 0, 'LEGS': 1, 'CHEST': 2, 'HEAD': 3}

def argc(desc):
    a = desc[1:desc.index(')')]; n = 0; i = 0
    while i < len(a):
        while a[i] == '[': i += 1
        if a[i] == 'L': i = a.index(';', i)
        i += 1; n += 1
    return n

def rettype(desc): return desc[desc.index(')') + 1:]

class VM:
    def __init__(s, jars):
        s.idx = {}
        for j in jars:
            try: z = zipfile.ZipFile(j)
            except Exception: continue
            for n in z.namelist():
                if n.endswith('.class') and not n.startswith('META-INF'):
                    s.idx.setdefault(n[:-6], (z, n))
        s.cache = {}; s.statics = {}; s.inited = set(); s.regs = []; s.steps = 0; s.attrname = {}
        s.depth = 0; s.budget = 10**12; s.fsteps = 100000; s.clinit_budget = 600000; s.hard = 10**12

    def cf(s, cls):
        if cls in s.cache: return s.cache[cls]
        e = s.idx.get(cls); r = None
        if e:
            try:
                r = ClassFile(io.BytesIO(e[0].read(e[1])))
                r._code = {}
            except Exception: r = None
        s.cache[cls] = r; return r

    def supers(s, cls):
        out = []
        while cls and len(out) < 20:
            out.append(cls); c = s.cf(cls)
            if not c or not c.super_: break
            cls = c.super_.name.value
        return out

    def find(s, cls, name, desc=None):
        chain = s.supers(cls)
        for c in chain:
            k = s.cf(c)
            if not k: continue
            for m in k.methods:
                if m.name.value == name and (desc is None or m.descriptor.value == desc):
                    return c, k, m
        # default methods of implemented interfaces (breadth first)
        todo = []; seen = set()
        for c in chain:
            k = s.cf(c)
            if k: todo += [i.name.value for i in k.interfaces]
        while todo and len(seen) < 64:
            c = todo.pop(0)
            if c in seen: continue
            seen.add(c); k = s.cf(c)
            if not k: continue
            for m in k.methods:
                if m.name.value == name and (desc is None or m.descriptor.value == desc) and m.code:
                    return c, k, m
            todo += [i.name.value for i in k.interfaces]
        return None

    def clinit(s, cls):
        if cls in s.inited: return
        s.inited.add(cls)
        k = s.cf(cls)
        if not k: return
        sup = k.super_.name.value if k.super_ else None
        if sup: s.clinit(sup)
        m = k.methods.find_one(name='<clinit>')
        if m and m.code:
            ob = s.budget; st0 = s.steps; s.budget = s.steps + s.clinit_budget
            od = s.depth; s.depth = min(s.depth, 8)  # a nested <clinit> starts a fresh frame stack in the real JVM
            try: s.run(cls, k, m, [])
            except RecursionError: pass
            except Exception as ex: pass
            finally: s.budget = ob + (s.steps - st0); s.depth = od

    def getstatic(s, cls, name, desc):
        if cls == 'net/minecraft/world/item/Tiers' and name in VTIER: return ('VT', name)
        if cls == 'net/minecraft/world/item/ArmorMaterials' and name in VARM: return ('VA', name)
        if cls == 'net/minecraft/world/item/ArmorItem$Type': return EnumC(cls, TYPEF.get(name, name), TYPES.index(TYPEF[name]) if TYPEF.get(name) in TYPES else -1)
        if cls == 'net/minecraft/world/entity/EquipmentSlot' and name in EQF: return EnumC(cls, EQF[name], EQS.index(EQF[name]))
        if cls == 'net/minecraft/world/entity/ai/attributes/Attributes': return Attr(s.attrname.get(name, name))
        if cls == 'net/minecraftforge/common/ForgeMod' and name in ('ENTITY_REACH', 'BLOCK_REACH', 'SWIM_SPEED', 'NAMETAG_DISTANCE', 'ENTITY_GRAVITY', 'STEP_HEIGHT_ADDITION'):
            return Attr('forge:' + name.lower())  # RegistryObject<Attribute>; .get() keeps the Attr
        if cls.startswith(('net/minecraft/', 'java/', 'com/google/', 'net/minecraftforge/')):
            if desc.startswith('Lnet/minecraft/world/entity/ai/attributes/'): return Attr(cls.split('/')[-1] + '.' + name)
            return Opaque('S:' + name)
        # attributes registered by mods: field holding RegistryObject<Attribute>
        s.clinit(cls)
        omni = desc.startswith('Lcom/aizistral/omniconfig/wrappers/Omniconfig$')
        for c in s.supers(cls):
            if (c, name) in s.statics and not (omni and s.statics[(c, name)] is None): return s.statics[(c, name)]
        if omni and ('omni', cls) not in s.inited:
            s.inited.add(('omni', cls))  # @SubscribeConfig onConfig(OmniconfigWrapper) fills these statics at config load
            k = s.cf(cls)
            for m in (k.methods if k else []):
                if m.code and m.access_flags.get('acc_static') and m.descriptor.value == '(Lcom/aizistral/omniconfig/wrappers/OmniconfigWrapper;)V':
                    w = Obj('com/aizistral/omniconfig/wrappers/OmniconfigWrapper'); w.f['$pfx'] = []
                    ob = s.budget; st0 = s.steps; s.budget = s.steps + 200000; od = s.depth; s.depth = min(s.depth, 8)
                    try: s.run(cls, k, m, [w])
                    except Exception: pass
                    finally: s.budget = ob + (s.steps - st0); s.depth = od
            if (cls, name) in s.statics: return s.statics[(cls, name)]
        if 'Attribute' in desc: return Attr(cls.split('/')[-1] + '.' + name)
        return Opaque('S:' + cls.split('/')[-1] + '.' + name)

    # ---- evaluation of Tier / ArmorMaterial values ----
    def call_virtual(s, obj, name, desc, args):
        if isinstance(obj, Obj):
            r = s.find(obj.cls, name, desc)
            if r and r[2].code: return s.run(r[0], r[1], r[2], [obj] + args)
        if isinstance(obj, EnumC) and obj.cls in s.idx:
            r = s.find(obj.cls, name, desc)
            if r and r[2].code: return s.run(r[0], r[1], r[2], [obj] + args)
        return OP

    def tier(s, t):
        if isinstance(t, tuple) and t[0] == 'VT': return VTIER[t[1]][3]
        if isinstance(t, Obj) and t.cls == 'net/minecraftforge/common/ForgeTier': return t.f.get('dmg')
        if isinstance(t, (Obj, EnumC)):
            v = s.call_virtual(t, 'm_6631_', '()F', [])
            return v if num(v) else None
        return None

    def armor(s, mat, typ):
        ti = typ.ord if isinstance(typ, EnumC) else -1
        if isinstance(mat, tuple) and mat[0] == 'VA':
            d, t, k = VARM[mat[1]]; return (d[ti] if ti >= 0 else None), t, k
        if isinstance(mat, (Obj, EnumC)):
            d = s.call_virtual(mat, 'm_7366_', '(Lnet/minecraft/world/item/ArmorItem$Type;)I', [typ])
            t = s.call_virtual(mat, 'm_6651_', '()F', [])
            k = s.call_virtual(mat, 'm_6649_', '()F', [])
            return (d if num(d) else None), (t if num(t) else None), (k if num(k) else None)
        return None, None, None

    # ---- modelled constructors ----
    def model_init(s, cls, obj, args):
        """returns True if handled (no interpretation of cls.<init>)"""
        g = obj.gear if isinstance(obj, Obj) else {}
        if cls == 'net/minecraft/world/item/SwordItem':
            t, d, sp = args[0], args[1], args[2]; b = s.tier(t)
            g.update(k='sword', tier=t, dmg=(d + b) if num(d) and num(b) else None, spd=sp if num(sp) else None); return True
        if cls == 'net/minecraft/world/item/DiggerItem':
            d, sp, t = args[0], args[1], args[2]; b = s.tier(t)
            g.setdefault('k', 'tool'); g.update(tier=t, dmg=(d + b) if num(d) and num(b) else None, spd=sp if num(sp) else None); return True
        if cls in ('net/minecraft/world/item/AxeItem', 'net/minecraft/world/item/PickaxeItem',
                   'net/minecraft/world/item/ShovelItem', 'net/minecraft/world/item/HoeItem'):
            t, d, sp = args[0], args[1], args[2]; b = s.tier(t)
            g.update(k=cls.split('/')[-1][:-4].lower(), tier=t, dmg=(d + b) if num(d) and num(b) else None, spd=sp if num(sp) else None); return True
        if cls == 'net/minecraft/world/item/TieredItem':
            g.setdefault('k', 'tiered'); g['tier'] = args[0]; return True
        if cls == 'net/minecraft/world/item/ArmorItem':
            d, t, k = s.armor(args[0], args[1])
            g.update(k='armor', slot=args[1].name if isinstance(args[1], EnumC) else None, arm=d, tough=t, kbr=k)
            if isinstance(obj, Obj):  # vanilla fields a subclass may read: type, defense, toughness, kbr, material
                obj.f.update({'f_265916_': args[1], 'f_40381_': d if num(d) else OP, 'f_40382_': t if num(t) else OP,
                              'f_40378_': k if num(k) else OP, 'f_40379_': args[0]})
            return True
        if cls == 'net/minecraft/world/item/TridentItem': g.update(k='trident', dmg=8.0, spd=-2.9); return True
        if cls == 'net/minecraft/world/item/BowItem': g.setdefault('k', 'bow'); return True
        if cls == 'net/minecraft/world/item/CrossbowItem': g.setdefault('k', 'crossbow'); return True
        if cls == 'net/minecraft/world/item/ShieldItem': g.setdefault('k', 'shield'); return True
        if cls == 'net/minecraftforge/common/ForgeTier':
            obj.f.update(lvl=args[0], uses=args[1], speed=args[2], dmg=args[3], ench=args[4] if len(args) > 4 else OP); return True
        if cls == 'net/minecraft/world/entity/ai/attributes/AttributeModifier':
            if isinstance(obj, Obj):
                amt = args[2] if len(args) >= 4 else (args[1] if len(args) == 3 else None)
                obj.f['amt'] = amt; obj.f['op'] = args[-1]
                nm = [x for x in args if isinstance(x, str)]
                if nm: obj.f['name'] = nm[0]
            return True
        if cls == 'java/lang/Enum':
            if isinstance(obj, Obj): obj.f['$name'] = args[0]; obj.f['$ord'] = args[1]
            return True
        return False

    def construct(s, cls, desc, args):
        """new cls + <init>(desc)(args)"""
        if cls in ('com/google/common/collect/ImmutableMultimap$Builder', 'com/google/common/collect/HashMultimap',
                   'java/util/HashMap', 'java/util/EnumMap', 'java/util/ArrayList', 'java/util/LinkedHashMap',
                   'com/google/common/collect/ArrayListMultimap', 'com/google/common/collect/LinkedHashMultimap'):
            return MMap()
        if cls == 'net/minecraft/resources/ResourceLocation':
            st = [a for a in args if isinstance(a, str)]
            return ':'.join(st) if st else Opaque('rl')
        if cls in ('java/lang/StringBuilder', 'java/lang/StringBuffer'):
            o = Obj(cls); o.f['$sb'] = args[0] if args and isinstance(args[0], str) else ''; return o
        o = Obj(cls)
        s.init(cls, desc, o, args)
        if o.gear:  # items that take their registry name as a constructor argument (registered later from a list)
            ids = [a for a in args if isinstance(a, str) and IDLIKE.fullmatch(a)]
            if ids: s.regs.append((ids[0], o))
        return o

    def init(s, cls, desc, o, args):
        if s.model_init(cls, o, args): return
        r = s.find(cls, '<init>', desc)
        if r and r[0] == cls and r[2].code:
            s.run(cls, r[1], r[2], [o] + args)

    def invoke(s, kind, cls, name, desc, args, recv=None):
        n = argc(desc)
        rt = rettype(desc)
        # --- collections ---
        if isinstance(recv, MMap):
            if name in ('put', 'putAll', 'add') and len(args) >= 1:
                s.mm_put(recv, args); return recv if rt.startswith('L') and 'Builder' in rt else (True if rt == 'Z' else None)
            if name in ('build', 'copyOf', 'unmodifiable'): return recv
            islist = all(k is None for k, _ in recv.items)
            if name == 'get' and args:
                if islist and isinstance(args[0], int) and not isinstance(args[0], bool):
                    return recv.items[args[0]][1] if 0 <= args[0] < len(recv.items) else OP
                for k, v in recv.items:
                    if s.same(k, args[0]): return v
                return OP
            if name in ('entrySet', 'entries'): return view([Entry(k, v) for k, v in recv.items]) if not islist else recv
            if name in ('keySet', 'keys'): return view([k for k, _ in recv.items])
            if name == 'values': return view([v for _, v in recv.items])
            if name == 'iterator': return Iter([v for _, v in recv.items])
            if name in ('size',): return len(recv.items)
            if name == 'isEmpty': return 0 if recv.items else 1
            if name == 'containsKey' and args: return 1 if any(s.same(k, args[0]) for k, _ in recv.items) else 0
            if name == 'forEach' and args and isinstance(args[0], Lam):
                for k, v in list(recv.items)[:64]:
                    s.call_lam(args[0], [v] if islist else [k, v])
                return None
            return OP if rt != 'V' else None
        if isinstance(recv, Iter):
            if name == 'hasNext': return 1 if recv.i < len(recv.el) else 0
            if name == 'next':
                if recv.i < len(recv.el): recv.i += 1; return recv.el[recv.i - 1]
                return OP
            return OP if rt != 'V' else None
        if isinstance(recv, Entry):
            if name == 'getKey': return recv.k
            if name == 'getValue': return recv.v
            return OP if rt != 'V' else None
        if cls in ('com/google/common/collect/ImmutableMultimap', 'com/google/common/collect/ImmutableMultimap$Builder',
                   'com/google/common/collect/ImmutableSetMultimap', 'com/google/common/collect/ImmutableListMultimap',
                   'com/google/common/collect/HashMultimap', 'com/google/common/collect/LinkedHashMultimap',
                   'com/google/common/collect/ArrayListMultimap', 'com/google/common/collect/Multimaps',
                   'java/util/Map', 'com/google/common/collect/ImmutableMap', 'com/google/common/collect/Maps') and kind == 'invokestatic':
            if name in ('builder', 'create'): return MMap()
            if name == 'of':
                m = MMap()
                for i in range(0, len(args) - 1, 2): m.items.append((args[i], args[i + 1]))
                return m
            if name in ('copyOf', 'newEnumMap', 'newHashMap', 'unmodifiableMultimap') or name.startswith(('new', 'unmodifiable', 'synchronized')):
                return args[0] if args and isinstance(args[0], MMap) and not name.startswith('new') else MMap()
        if cls == 'net/minecraft/Util' and name == 'm_137469_':  # Util.make(obj, consumer)
            if isinstance(args[1], Lam): s.call_lam(args[1], [args[0]])
            return args[0]
        if cls == 'net/minecraft/Util' and name == 'm_137537_':  # Util.make(supplier)
            return s.call_lam(args[0], []) if isinstance(args[0], Lam) else OP
        # --- java.util.ServiceLoader: platform helpers (multiloader mods) -> the META-INF/services implementation ---
        if cls == 'java/util/ServiceLoader' and name == 'load' and args and isinstance(args[0], Opaque) and args[0].d.startswith('class:'):
            impl = s.service_impl(args[0].d[6:])
            return ('OPT', s.construct(impl, '()V', [])) if impl else OP
        if isinstance(recv, tuple) and recv and recv[0] == 'OPT':
            if name in ('findFirst', 'iterator', 'stream', 'filter', 'map'): return recv
            if name in ('orElseThrow', 'get', 'orElse', 'next', 'orElseGet'): return recv[1]
            if name in ('hasNext', 'isPresent'): return 1
            return OP if rt != 'V' else None
        # --- Omniconfig (com.aizistral.omniconfig): builder with key prefixes -> config values ---
        if cls.startswith('com/aizistral/omniconfig/') and kind != 'invokestatic':
            if isinstance(recv, CfgVal):
                return cfg_get(recv.key, recv.dflt) if name in ('getValue', 'getValueOrDefault', 'get') else (OP if rt != 'V' else None)
            if isinstance(recv, Obj) and '$pfx' in recv.f:
                pf = recv.f['$pfx']
                if name == 'pushPrefix' and args and isinstance(args[0], str): pf.append(args[0]); return recv
                if name == 'popPrefix':
                    if pf: pf.pop()
                    return recv
                if name.startswith('get') and len(args) >= 2 and isinstance(args[0], str):
                    return CfgVal(''.join(pf) + args[0], args[1] if num(args[1]) else None)
                if rt.startswith('Lcom/aizistral/omniconfig/wrappers/OmniconfigWrapper'): return recv
                return OP if rt != 'V' else None
        # --- registration capture ---
        if cls == 'net/minecraftforge/registries/DeferredRegister' and kind == 'invokestatic' and name in ('create', 'createOptional'):
            o = Obj(cls); ss = [a for a in args if isinstance(a, str)]; o.f['$ns'] = ss[-1] if ss else None; return o
        if name == 'register' and cls == 'net/minecraftforge/registries/DeferredRegister' and len(args) >= 2 and isinstance(args[0], str):
            ro = RegObj(args[0], args[1]); ro.ns = recv.f.get('$ns') if isinstance(recv, Obj) else None
            s.regs.append((args[0], args[1])); return ro
        if name in ('get', 'm_123015_') and isinstance(recv, RegObj):
            v = s.resolve(recv.sup)
            if isinstance(v, Obj):  # lets mod-registered attributes be named
                ns = getattr(recv, 'ns', None)
                v.f.setdefault('$regname', (ns + ':' + recv.name) if isinstance(ns, str) and ':' not in recv.name else recv.name)
            return v
        if name in ('get', 'apply', 'accept', 'create', 'm_7969_') and isinstance(recv, Lam):
            return s.call_lam(recv, args)
        if kind == 'invokeinterface' and isinstance(recv, Lam) and name not in ('andThen', 'compose', 'negate', 'and', 'or', 'equals', 'hashCode', 'toString'):
            return s.call_lam(recv, args)  # the functional interface's single abstract method, whatever it is called
        if kind == 'invokestatic' and name in ('of', 'memoize', 'concurrentOf') and args and isinstance(args[0], Lam) and cls in (
                'net/minecraftforge/common/util/Lazy', 'net/minecraftforge/common/util/NonNullLazy', 'com/google/common/base/Suppliers'):
            return args[0]  # lazy supplier: .get() runs the lambda
        if name == 'm_22245_' and args and isinstance(args[0], Attr):  # AttributeSupplier.getBaseValue (player defaults)
            v = {'generic.attack_damage': 1.0, 'generic.attack_speed': 4.0, 'generic.movement_speed': 0.1, 'generic.max_health': 20.0,
                 'generic.armor': 0.0, 'generic.armor_toughness': 0.0, 'generic.knockback_resistance': 0.0, 'generic.luck': 0.0}.get(args[0].n)
            if v is not None: return v
        if name in ('get', 'getValue') and isinstance(recv, Opaque) and recv.d.startswith('S:') and cls.endswith('RegistryObject'):
            return OP
        # boxing
        if cls in ('java/lang/Integer', 'java/lang/Float', 'java/lang/Double', 'java/lang/Long') and name == 'valueOf' and args and num(args[0]):
            return args[0]
        if name in ('intValue', 'floatValue', 'doubleValue', 'longValue') and num(recv): return recv
        if cls == 'net/minecraft/resources/ResourceLocation' and kind == 'invokestatic' and args and all(isinstance(a, str) for a in args):
            return ':'.join(args) if len(args) > 1 else args[0]
        if cls == 'java/lang/Math' and all(num(a) for a in args):
            import math
            f = {'max': max, 'min': min, 'abs': abs, 'floor': lambda x: float(math.floor(x)), 'ceil': lambda x: float(math.ceil(x)),
                 'round': lambda x: int(math.floor(x + 0.5)), 'sqrt': math.sqrt, 'pow': math.pow}.get(name)
            try: return f(*args) if f else OP
            except Exception: return OP
        if cls == 'net/minecraft/util/Mth' and kind == 'invokestatic' and args and all(num(a) for a in args):
            r = s.find(cls, name, desc)  # pure math helpers (floor/ceil/clamp/...): interpret the vanilla bytecode
            if r and r[2].code:
                v = s.run(r[0], r[1], r[2], args)
                return v if num(v) else OP
        if name in ('m_20749_', 'getIndex') and isinstance(recv, EnumC) and recv.cls.endswith('EquipmentSlot'): return EQIDX.get(recv.name, -1)
        if name == 'm_20743_' and isinstance(recv, EnumC) and recv.cls.endswith('EquipmentSlot'): return EnumC('net/minecraft/world/entity/EquipmentSlot$Type', 'HAND' if 'HAND' in recv.name else 'ARMOR', 0 if 'HAND' in recv.name else 1)
        if name == 'name' and not args and isinstance(recv, EnumC): return recv.name
        if name == 'm_266355_' and isinstance(recv, EnumC) and recv.cls.endswith('ArmorItem$Type'): return recv.name.lower()  # Type.getName
        if name == 'm_20751_' and isinstance(recv, EnumC) and recv.cls.endswith('EquipmentSlot'): return recv.name.lower()  # EquipmentSlot.getName
        if name == 'name' and not args and isinstance(recv, Obj) and isinstance(recv.f.get('$name'), str): return recv.f['$name']
        if isinstance(recv, Obj) and '$sb' in recv.f:
            if name == 'append' and args:
                a = args[0]; sb = recv.f['$sb']
                recv.f['$sb'] = (sb + (a if isinstance(a, str) else str(int(a)) if isinstance(a, int) else str(a))) if isinstance(sb, str) and isinstance(a, (str, int, float)) and not isinstance(a, bool) else None
                return recv
            if name == 'toString': return recv.f['$sb'] if isinstance(recv.f['$sb'], str) else OP
        if isinstance(recv, str) and kind != 'invokestatic':
            if name in ('toLowerCase', 'toUpperCase', 'trim', 'strip', 'intern', 'toString'):
                return {'toLowerCase': recv.lower, 'toUpperCase': recv.upper, 'trim': recv.strip, 'strip': recv.strip}.get(name, lambda: recv)()
            if name == 'concat' and args and isinstance(args[0], str): return recv + args[0]
            if name == 'replace' and len(args) == 2 and all(isinstance(a, str) for a in args): return recv.replace(args[0], args[1])
            if name == 'length': return len(recv)
            if name == 'hashCode':  # java.lang.String.hashCode (string switch)
                h = 0
                for ch in recv.encode('utf-16-be').decode('utf-16-be'): h = (31 * h + ord(ch)) & 0xFFFFFFFF
                return h - (1 << 32) if h >= (1 << 31) else h
            if name in ('startsWith', 'endsWith', 'contains') and args and isinstance(args[0], str):
                return 1 if getattr(recv, {'startsWith': 'startswith', 'endsWith': 'endswith', 'contains': '__contains__'}[name])(args[0]) else 0
        if cls == 'java/lang/String' and name == 'valueOf' and args and isinstance(args[0], (str, int)) and not isinstance(args[0], bool): return str(args[0])
        if name == 'clone' and isinstance(recv, Arr):
            a = Arr(0); a.v = list(recv.v); return a
        if name == 'ordinal' and isinstance(recv, EnumC): return recv.ord
        if name == 'ordinal' and isinstance(recv, Obj) and '$ord' in recv.f: return recv.f['$ord']
        if name in ('m_266308_',) and isinstance(recv, EnumC):  # Type.getSlot
            return EnumC('net/minecraft/world/entity/EquipmentSlot', {'HELMET': 'HEAD', 'CHESTPLATE': 'CHEST', 'LEGGINGS': 'LEGS', 'BOOTS': 'FEET'}.get(recv.name, recv.name), -1)
        if cls == 'net/minecraft/world/item/ArmorItem$Type' and name == 'values':
            a = Arr(4); a.v = [EnumC(cls, t, i) for i, t in enumerate(TYPES)]; return a
        if name == 'equals' and recv is not None and args: return 1 if s.same(recv, args[0]) else 0
        if isinstance(recv, Obj) and recv.cls == 'net/minecraft/world/entity/ai/attributes/AttributeModifier' and kind != 'invokestatic':
            if name == 'm_22218_': return recv.f.get('amt', OP)  # getAmount
            if name == 'm_22217_': return recv.f.get('op', OP)  # getOperation
            if name == 'm_22214_': return recv.f.get('name', 'modifier')  # getName
        if isinstance(recv, Obj) and recv.cls.startswith('net/minecraft/world/entity/ai/attributes/') and rt == 'Lnet/minecraft/world/entity/ai/attributes/Attribute;' and kind != 'invokestatic':
            return recv  # fluent Attribute setters (setSyncable)
        if name == 'm_22082_' and isinstance(recv, Attr):  # Attribute.getDefaultValue (vanilla Attributes <clinit>)
            v = VATTR_DEF.get(recv.n)
            return v if v is not None else OP
        if name == 'm_22082_' and isinstance(recv, Obj) and num(recv.f.get('f_22076_')): return recv.f['f_22076_']
        if name == 'get' and isinstance(recv, Attr):  # RegistryObject.get on attribute
            return recv
        # cloth AutoConfig: build the config object from its defaults, then apply the pack's json values by field name
        if cls == 'me/shedaniel/autoconfig/AutoConfig' and name == 'getConfigHolder' and args and isinstance(args[0], Opaque) and args[0].d.startswith('class:'):
            return ('HOLDER', args[0].d[6:])
        if name == 'getConfig' and isinstance(recv, tuple) and recv and recv[0] == 'HOLDER':
            o = s.construct(recv[1], '()V', [])
            def apply(o, d=0):
                if not isinstance(o, Obj) or d > 4: return
                for fk, fv in list(o.f.items()):
                    if isinstance(fv, Obj): apply(fv, d + 1)
                    elif num(fv) or isinstance(fv, bool): o.f[fk] = cfg_get(fk, fv)
            apply(o); return o
        # config values
        if isinstance(recv, tuple) and recv and recv[0] == 'PAIR':  # commons-lang Pair from ForgeConfigSpec.Builder.configure
            if name in ('getLeft', 'getKey', 'left', 'getFirst'): return recv[1]
            return Opaque('spec')
        if cls == 'net/minecraftforge/common/ForgeConfigSpec$Builder' and name == 'configure' and args and isinstance(args[0], Lam):
            return ('PAIR', s.call_lam(args[0], [recv if recv is not None else Obj(cls)]))
        if cls.startswith('net/minecraftforge/common/ForgeConfigSpec'):
            pth = recv.f.setdefault('$path', []) if isinstance(recv, Obj) and recv.cls.startswith('net/minecraftforge/common/ForgeConfigSpec') else None
            def strs(a):
                if isinstance(a, str): return a.split('.')
                if isinstance(a, Arr): return [x for x in a.v if isinstance(x, str)] if all(isinstance(x, str) for x in a.v) else None
                if isinstance(a, MMap): return [x for _, x in a.items] if all(isinstance(x, str) for _, x in a.items) else None
                return None
            if pth is not None and name == 'push' and args:
                q = strs(args[0])
                if q is None: recv.f['$path'] = None
                elif pth is not None: pth.extend(q)
                return recv
            if pth is not None and name == 'pop':
                n = args[0] if args and isinstance(args[0], int) else 1
                if isinstance(recv.f.get('$path'), list): del recv.f['$path'][max(0, len(recv.f['$path']) - n):]
                return recv
            if name.startswith('define') and args:
                key = args[0] if isinstance(args[0], str) else (args[0].v[-1] if isinstance(args[0], Arr) and args[0].v else None)
                d0 = args[1] if len(args) > 1 else None
                if isinstance(d0, Lam): d0 = None
                q = strs(args[0]); base = recv.f.get('$path') if isinstance(recv, Obj) else None
                return CfgVal(key, d0, '.'.join(base + q) if isinstance(base, list) and q else None)
            if name in ('get', 'getAsDouble', 'getAsInt', 'getAsLong', 'getAsBoolean') and isinstance(recv, CfgVal):
                return cfg_get(recv.key, recv.dflt, recv.path)
            if rt.startswith('Lnet/minecraftforge/common/ForgeConfigSpec$Builder') and recv is not None: return recv
            return Opaque('cfg') if rt != 'V' else None
        if name in ('get', 'getAsDouble', 'getAsInt') and isinstance(recv, CfgVal): return cfg_get(recv.key, recv.dflt, recv.path)
        if rt in ('F', 'I', 'D', 'J') and kind == 'invokestatic' and len(args) >= 2 and isinstance(args[0], str) and num(args[-1]):
            return cfg_get(args[0], args[-1])
        if cls == 'net/minecraftforge/common/TierSortingRegistry' and name == 'registerTier' and args: return args[0]
        if kind != 'invokestatic' and isinstance(recv, Obj) and recv.gear and name in VGET:
            g = recv.gear; f = VGET[name]
            if f == 'type' and g.get('k') == 'armor' and g.get('slot') in TYPES:
                return EnumC('net/minecraft/world/item/ArmorItem$Type', g['slot'], TYPES.index(g['slot']))
            if f == 'eslot' and g.get('k') == 'armor' and g.get('slot') in TYPES:
                es = {'HELMET': 'HEAD', 'CHESTPLATE': 'CHEST', 'LEGGINGS': 'LEGS', 'BOOTS': 'FEET'}[g['slot']]
                return EnumC('net/minecraft/world/entity/EquipmentSlot', es, EQS.index(es))
            if f == 'mat' and 'f_40379_' in recv.f: return recv.f['f_40379_']
            if f in ('arm', 'tough', 'dmg', 'tier'):
                v = g.get(f)
                if v is not None and (num(v) or f == 'tier'): return v
        if kind != 'invokestatic' and isinstance(recv, Obj) and recv.cls == 'net/minecraftforge/common/ForgeTier':
            f = {'m_6604_': 'lvl', 'm_6609_': 'uses', 'm_6624_': 'speed', 'm_6631_': 'dmg', 'm_6601_': 'ench'}.get(name)
            if f: v = recv.f.get(f); return v if num(v) else OP
        if kind != 'invokestatic' and isinstance(recv, tuple) and len(recv) == 2 and recv[0] in ('VT', 'VA'):
            v = s.vanilla_getter(recv, name, args)
            if v is not None: return v
        if kind == 'invokespecial' and isinstance(recv, Obj) and name in ('m_7167_', 'getAttributeModifiers') and cls.startswith(('net/minecraft/world/item/', 'net/minecraftforge/common/extensions/IForgeItem')):
            return s.vanilla_mods(recv, args[0] if args else None)  # super.getDefaultAttributeModifiers(slot): the modelled base item's modifiers
        if kind not in ('invokestatic', 'invokespecial') and isinstance(recv, (Obj, EnumC)) and cls.startswith(VPFX) and not recv.cls.startswith(VPFX) and recv.cls in s.idx:
            r = s.find(recv.cls, name, desc)
            if r and r[2].code and not r[0].startswith(VPFX):
                v = s.run(r[0], r[1], r[2], [recv] + args)
                s.capture(name, args, v); return v
        # mod-defined code
        if not cls.startswith(('java/', 'javax/', 'net/minecraft/', 'com/google/', 'com/mojang/', 'net/minecraftforge/', 'org/apache/', 'org/slf4j/', 'org/joml/', 'org/lwjgl/', 'org/objectweb/', 'org/spongepowered/', 'org/jetbrains/', 'org/intellij/', 'org/checkerframework/', 'org/openjdk/', 'org/w3c/', 'org/xml/', 'org/yaml/', 'org/antlr/', 'org/jline/', 'org/tomlj/', 'org/json/', 'it/unimi', 'kotlin/')):
            if kind == 'invokestatic':
                s.clinit(cls)
                r = s.find(cls, name, desc)
                if r and r[2].code:
                    v = s.run(r[0], r[1], r[2], args)
                    s.capture(name, args, v); return v
            else:
                tgt = cls if kind == 'invokespecial' else recv.cls if isinstance(recv, Obj) else (recv.cls if isinstance(recv, EnumC) and recv.cls in s.idx else cls)  # super.m() binds statically
                r = s.find(tgt, name, desc) or s.find(cls, name, desc)
                if r and r[2].code and recv is not None:
                    v = s.run(r[0], r[1], r[2], [recv] + args)
                    s.capture(name, args, v); return v
        s.capture(name, args, None)
        if rt == 'V': return None
        if name.startswith('m_') and isinstance(recv, Opaque) and rt.startswith('L') and recv.d == 'props':
            return recv  # Item.Properties builder chain
        if rt == 'Lnet/minecraft/world/item/Item$Properties;': return Opaque('props')
        return Opaque(name)

    def service_impl(s, iface):
        if not hasattr(s, '_svc'): s._svc = {}
        if iface in s._svc: return s._svc[iface]
        r = None; seen = set()
        for z, _ in list(s.idx.values()):
            if id(z) in seen: continue
            seen.add(id(z))
            try: t = z.read('META-INF/services/' + iface.replace('/', '.')).decode('utf8', 'ignore')
            except KeyError: continue
            except Exception: continue
            for line in t.splitlines():
                line = line.split('#')[0].strip()
                if line: r = line.replace('.', '/'); break
            if r: break
        s._svc[iface] = r; return r

    def vanilla_mods(s, o, slot):
        m = MMap(); g = o.gear; sl = slot.name if isinstance(slot, EnumC) else None
        def put(a, v):
            if num(v):
                mo = Obj('net/minecraft/world/entity/ai/attributes/AttributeModifier'); mo.f['amt'] = v; mo.f['op'] = Opaque('S:ADDITION')
                m.items.append((Attr(a), mo))
        k = g.get('k')
        if k in ('sword', 'tool', 'axe', 'pickaxe', 'shovel', 'hoe', 'trident') and sl == 'MAINHAND':
            put('generic.attack_damage', g.get('dmg')); put('generic.attack_speed', g.get('spd'))
        if k == 'armor' and sl and {'HELMET': 'HEAD', 'CHESTPLATE': 'CHEST', 'LEGGINGS': 'LEGS', 'BOOTS': 'FEET'}.get(g.get('slot')) == sl:
            put('generic.armor', g.get('arm'))
            if g.get('tough'): put('generic.armor_toughness', g.get('tough'))
            if g.get('kbr'): put('generic.knockback_resistance', g.get('kbr'))
        return m

    def vanilla_getter(s, recv, name, args):
        t, n = recv
        if t == 'VT' and n in VTIER:
            lv, uses, spd, dmg = VTIER[n]
            return {'m_6604_': lv, 'm_6609_': uses, 'm_6624_': spd, 'm_6631_': dmg}.get(name)
        if t == 'VA' and n in VARM:
            d, tg, kb = VARM[n]
            if name == 'm_7366_' and args and isinstance(args[0], EnumC) and 0 <= args[0].ord < 4: return d[args[0].ord]
            return {'m_6651_': float(tg), 'm_6649_': float(kb)}.get(name)
        return None

    def capture(s, name, args, ret):
        strs = [a for a in args if isinstance(a, str)]
        ids = [a for a in strs if IDLIKE.fullmatch(a)]
        if ids: strs = ids + [a for a in strs if a not in ids]
        vals = [a for a in args if isinstance(a, (Lam, Obj))]
        if strs and isinstance(ret, Obj) and ret not in vals and (ret.gear or 'net/minecraft/world/item/Item' in s.supers(ret.cls)):
            vals = [ret] + vals  # factory(name, ...) -> item
        if strs and vals:
            for v in vals:
                if isinstance(v, Obj) and not v.gear and v.cls.startswith('net/minecraft/'): continue
                s.regs.append((strs[0], v))

    def resolve(s, v, d=0):
        if isinstance(v, Lam) and d < 4: return s.resolve(s.call_lam(v, []), d + 1)
        if isinstance(v, RegObj) and d < 4: return s.resolve(v.sup, d + 1)
        return v

    def same(s, a, b):
        if isinstance(a, Attr) and isinstance(b, Attr): return a.n == b.n
        if isinstance(a, EnumC) and isinstance(b, EnumC): return a.name == b.name
        return a is b or (num(a) and num(b) and a == b) or (isinstance(a, str) and a == b)

    def mm_put(s, m, args):
        if len(args) == 2: m.items.append((args[0], args[1]))
        elif len(args) == 1 and isinstance(args[0], MMap) and getattr(args[0], 'view', False):
            m.items += [((e.k, e.v) if isinstance(e, Entry) else (None, e)) for _, e in args[0].items]
        elif len(args) == 1 and isinstance(args[0], MMap): m.items += args[0].items
        elif len(args) == 1: m.items.append((None, args[0]))

    def call_lam(s, l, args):
        a = list(l.cap) + list(args)
        if l.kind == 8:  # newInvokeSpecial (X::new)
            return s.construct(l.owner, l.desc, a + [Opaque('props')] * max(0, argc(l.desc) - len(a)))
        r = s.find(l.owner, l.name, l.desc)
        if not r or not r[2].code: return OP
        need = argc(l.desc) + (0 if l.kind == 6 else 1)
        a = a + [Opaque('props')] * max(0, need - len(a))
        return s.run(r[0], r[1], r[2], a[:need])

    # ---- interpreter ----
    def run(s, cls, k, m, args):
        if s.depth > 24 or s.steps >= s.budget or s.steps >= s.hard: return OP
        s.depth += 1
        try: return s._run(cls, k, m, args)
        finally: s.depth -= 1

    def code(s, k, m):
        key = id(m)
        if key not in k._code:
            ins = list(m.code.disassemble()); pos = {x.pos: i for i, x in enumerate(ins)}
            k._code[key] = (ins, pos)
        return k._code[key]

    def _run(s, cls, k, m, args):
        ins, pos = s.code(k, m)
        static = 'static' in str(m.access_flags.to_dict()) and m.access_flags.get('acc_static')
        loc = {}
        i = 0
        for a in args:
            loc[i] = a; i += 1
            if isinstance(a, float) and False: i += 1
        # long/double take 2 slots: recompute from descriptor
        loc = {}; slot = 0; ai = 0
        if not m.access_flags.get('acc_static'):
            loc[0] = args[0] if args else OP; slot = 1; ai = 1
        d = m.descriptor.value[1:m.descriptor.value.index(')')]
        j = 0
        while j < len(d):
            c = d[j]; arr = False
            while d[j] == '[': j += 1; arr = True
            if d[j] == 'L': j = d.index(';', j)
            loc[slot] = args[ai] if ai < len(args) else OP
            slot += 2 if (c in 'JD' and not arr) else 1; ai += 1; j += 1
        st = []; pc = 0; cp = k.constants; steps = 0; opq = set()
        def cst(ix):
            c = cp.get(ix)
            if isinstance(c, (C.Integer, C.Float, C.Long, C.Double)): return c.value
            if isinstance(c, C.String): return c.string.value
            if isinstance(c, C.ConstantClass): return Opaque('class:' + c.name.value)
            return OP
        def pop(n=1):
            r = []
            for _ in range(n): r.append(st.pop() if st else OP)
            return r[::-1]
        while pc < len(ins) and steps < s.fsteps and s.steps < s.budget:
            steps += 1; s.steps += 1
            x = ins[pc]; mn = x.mnemonic; ops = x.operands; pc += 1
            try:
                if mn in ('iconst_m1',): st.append(-1)
                elif mn.startswith('iconst_'): st.append(int(mn[-1]))
                elif mn.startswith('lconst_'): st.append(int(mn[-1]))
                elif mn.startswith('fconst_') or mn.startswith('dconst_'): st.append(float(mn[-1]))
                elif mn in ('bipush', 'sipush'): st.append(ops[0].value)
                elif mn in ('ldc', 'ldc_w', 'ldc2_w'): st.append(cst(ops[0].value))
                elif mn == 'aconst_null': st.append(None)
                elif mn[1:5] == 'load' and len(mn) <= 7:
                    ix = int(mn[-1]) if '_' in mn else ops[0].value; st.append(loc.get(ix, OP))
                elif mn[1:6] == 'store':
                    ix = int(mn[-1]) if '_' in mn else ops[0].value; loc[ix] = st.pop() if st else OP
                elif mn == 'iinc': ix = ops[0].value; v = loc.get(ix); loc[ix] = v + ops[1].value if num(v) else OP
                elif mn in ('iaload', 'faload', 'aaload', 'daload', 'laload', 'baload', 'saload', 'caload'):
                    a, ix = pop(2); st.append(a.v[ix] if isinstance(a, Arr) and isinstance(ix, int) and 0 <= ix < len(a.v) else OP)
                elif mn in ('iastore', 'fastore', 'aastore', 'dastore', 'lastore', 'bastore', 'sastore', 'castore'):
                    a, ix, v = pop(3)
                    if isinstance(a, Arr) and isinstance(ix, int) and 0 <= ix < len(a.v): a.v[ix] = v
                elif mn in ('newarray', 'anewarray'): n = pop()[0]; st.append(Arr(n if isinstance(n, int) else 0))
                elif mn == 'multianewarray': pop(ops[1].value); st.append(Arr(0))
                elif mn == 'arraylength': a = pop()[0]; st.append(len(a.v) if isinstance(a, Arr) else OP)
                elif mn == 'pop': pop()
                elif mn == 'pop2': pop(1)
                elif mn == 'dup': v = st[-1] if st else OP; st.append(v)
                elif mn == 'dup_x1': a, b = pop(2); st += [b, a, b]
                elif mn == 'dup_x2': a, b, c = pop(3); st += [c, a, b, c]
                elif mn == 'dup2': v = st[-1] if st else OP; st.append(v)
                elif mn == 'swap': a, b = pop(2); st += [b, a]
                elif mn[1:] in ('add', 'sub', 'mul', 'div', 'rem') and mn[0] in 'ifdl':
                    a, b = pop(2)
                    if num(a) and num(b):
                        o = mn[1:]
                        try: v = a + b if o == 'add' else a - b if o == 'sub' else a * b if o == 'mul' else (a / b if mn[0] in 'fd' else int(a / b)) if o == 'div' else a % b
                        except ZeroDivisionError: v = OP
                        st.append(v)
                    else: st.append(OP)
                elif mn[1:] == 'neg': a = pop()[0]; st.append(-a if num(a) else OP)
                elif mn in ('i2f', 'i2d', 'l2f', 'l2d', 'f2d', 'd2f'): a = pop()[0]; st.append(float(a) if num(a) else OP)
                elif mn in ('f2i', 'd2i', 'f2l', 'd2l', 'i2l', 'l2i', 'i2b', 'i2s', 'i2c'): a = pop()[0]; st.append(int(a) if num(a) else OP)
                elif mn[1:] in ('and', 'or', 'xor', 'shl', 'shr', 'ushr'):
                    a, b = pop(2); st.append(OP if not (isinstance(a, int) and isinstance(b, int)) else {'and': a & b, 'or': a | b, 'xor': a ^ b, 'shl': a << (b & 31), 'shr': a >> (b & 31), 'ushr': (a % (1 << 32)) >> (b & 31)}[mn[1:]])
                elif mn in ('lcmp', 'fcmpl', 'fcmpg', 'dcmpl', 'dcmpg'):
                    a, b = pop(2); st.append((a > b) - (a < b) if num(a) and num(b) else OP)
                elif mn.startswith('if'):
                    tgt = x.pos + ops[0].value; unk = False
                    if mn.startswith('if_icmp') or mn.startswith('if_acmp'):
                        a, b = pop(2); c = mn[7:]
                        if mn.startswith('if_acmp'): r = (a is b) if c == 'eq' else (a is not b)
                        elif num(a) and num(b): r = {'eq': a == b, 'ne': a != b, 'lt': a < b, 'ge': a >= b, 'gt': a > b, 'le': a <= b}[c]
                        else: r = False; unk = True
                    elif mn in ('ifnull', 'ifnonnull'):
                        a = pop()[0]; r = (a is None) == (mn == 'ifnull')
                        if isinstance(a, Opaque): r = False; unk = True
                    else:
                        a = pop()[0]; c = mn[2:]
                        if a is True: a = 1
                        if a is False: a = 0
                        if num(a): r = {'eq': a == 0, 'ne': a != 0, 'lt': a < 0, 'ge': a >= 0, 'gt': a > 0, 'le': a <= 0}[c]
                        else: r = False; unk = True
                    if unk:  # unknown condition: fall through the first time, take the branch on any later visit (a loop runs once)
                        if x.pos in opq: r = True
                        else: opq.add(x.pos)
                    if r: pc = pos[tgt]
                elif mn in ('goto', 'goto_w'):
                    tgt = x.pos + ops[0].value
                    if tgt < x.pos and steps > s.fsteps * 2 // 3: continue
                    pc = pos[tgt]
                elif mn in ('tableswitch', 'lookupswitch'):
                    v = pop()[0]; sw = ops[0] if isinstance(ops[0], dict) else None
                    tgt = None
                    try:
                        if mn == 'lookupswitch':  # jawa: [ {match: offset}, default ]
                            table = next(o for o in ops if isinstance(o, dict)); dflt = next(o for o in ops if not isinstance(o, dict))
                            if not isinstance(v, int) or isinstance(v, bool): return OP
                            tgt = x.pos + table.get(v, dflt.value)
                        else:
                            dflt, low, high = ops[0].value, ops[1].value, ops[2].value; offs = [o.value for o in ops[3:]]
                            tgt = x.pos + (offs[v - low] if isinstance(v, int) and low <= v <= high else dflt)
                    except Exception: tgt = None
                    if tgt is None or tgt not in pos: return OP
                    pc = pos[tgt]
                elif mn in ('ireturn', 'freturn', 'areturn', 'dreturn', 'lreturn'): return st.pop() if st else OP
                elif mn == 'return': return None
                elif mn == 'athrow': return OP
                elif mn == 'getstatic':
                    f = cp.get(ops[0].value); c = f.class_.name.value; n = f.name_and_type.name.value
                    if c == cls and (c, n) in s.statics and s.statics[(c, n)] is not None: st.append(s.statics[(c, n)])
                    else: st.append(s.getstatic(c, n, f.name_and_type.descriptor.value))
                elif mn == 'putstatic':
                    f = cp.get(ops[0].value); v = pop()[0]; s.statics[(f.class_.name.value, f.name_and_type.name.value)] = v
                    if isinstance(v, EnumC) or (isinstance(v, Obj) and '$name' in v.f): pass
                elif mn == 'getfield':
                    f = cp.get(ops[0].value); o = pop()[0]; n = f.name_and_type.name.value
                    st.append(o.f.get(n, OP) if isinstance(o, Obj) else (o.f.get(n, OP) if hasattr(o, 'f') else OP))
                elif mn == 'putfield':
                    f = cp.get(ops[0].value); o, v = pop(2)
                    if isinstance(o, Obj): o.f[f.name_and_type.name.value] = v
                elif mn == 'new':
                    st.append(('NEW', cp.get(ops[0].value).name.value))
                elif mn in ('invokevirtual', 'invokespecial', 'invokestatic', 'invokeinterface'):
                    mr = cp.get(ops[0].value); c = mr.class_.name.value; n = mr.name_and_type.name.value; dsc = mr.name_and_type.descriptor.value
                    a = pop(argc(dsc))
                    if mn == 'invokestatic':
                        v = s.invoke(mn, c, n, dsc, a)
                    elif n == '<init>':
                        r = pop()[0]
                        if isinstance(r, tuple) and r and r[0] == 'NEW':
                            v2 = s.construct(r[1], dsc, a)
                            # replace the dup'd NEW marker below with the object
                            for q in range(len(st) - 1, -1, -1):
                                if st[q] is r: st[q] = v2; break
                            for q in list(loc):
                                if loc[q] is r: loc[q] = v2
                        elif isinstance(r, Obj):  # super(...) / this(...)
                            s.init(c, dsc, r, a)
                        v = None
                    else:
                        r = pop()[0]; v = s.invoke(mn, c, n, dsc, a, r)
                    if rettype(dsc) != 'V' and n != '<init>': st.append(v)
                elif mn == 'invokedynamic':
                    idy = cp.get(ops[0].value); nt = idy.name_and_type; dsc = nt.descriptor.value
                    cap = pop(argc(dsc))
                    bsm = k.bootstrap_methods[idy.method_attr_index] if hasattr(k, 'bootstrap_methods') else None
                    if bsm is None:
                        for at in k.attributes:
                            if hasattr(at, 'table'): bsm = at.table[idy.method_attr_index]; break
                    v = OP
                    try:
                        if nt.name.value == 'makeConcatWithConstants':
                            recipe = cp.get(bsm.bootstrap_args[0]).string.value
                            if all(isinstance(z, (str, int, float)) for z in cap):
                                it = iter(cap); v = ''.join(str(next(it)) if ch == '\x01' else ch for ch in recipe)
                        else:
                            mh = cp.get(bsm.bootstrap_args[1])
                            ref = mh.reference
                            v = Lam(mh.reference_kind, ref.class_.name.value, ref.name_and_type.name.value, ref.name_and_type.descriptor.value, cap)
                    except Exception: v = OP
                    st.append(v)
                elif mn in ('checkcast', 'nop', 'monitorenter', 'monitorexit') or mn.startswith('wide'):
                    if mn.startswith('monitor'): pop()
                elif mn == 'instanceof': pop(); st.append(OP)
                else:
                    pass
            except IndexError:
                st.append(OP)
        return OP


def srg_tables(vm, srgjar):
    """Attributes srg field -> 'generic.attack_damage', ArmorItem$Type fields"""
    z = zipfile.ZipFile(srgjar)
    k = ClassFile(io.BytesIO(z.read('net/minecraft/world/entity/ai/attributes/Attributes.class')))
    m = k.methods.find_one(name='<clinit>'); last = None
    for x in m.code.disassemble():
        if x.mnemonic in ('ldc', 'ldc_w'):
            c = k.constants.get(x.operands[0].value)
            if isinstance(c, C.String) and c.string.value.startswith(('generic.', 'horse.', 'zombie.')): last = c.string.value
        if x.mnemonic == 'putstatic' and last:
            vm.attrname[k.constants.get(x.operands[0].value).name_and_type.name.value] = last; last = None
    for cn, tab, names in (('net/minecraft/world/item/Tiers', VTIER, ['WOOD','STONE','IRON','DIAMOND','GOLD','NETHERITE']),
                           ('net/minecraft/world/item/ArmorMaterials', VARM, ['LEATHER','CHAINMAIL','CHAIN','IRON','GOLD','DIAMOND','TURTLE','NETHERITE'])):
        k = ClassFile(io.BytesIO(z.read(cn + '.class'))); m = k.methods.find_one(name='<clinit>'); last = None
        old = dict(VTIER0 if tab is VTIER else VARM0); tab.clear()
        for x in m.code.disassemble():
            if x.mnemonic in ('ldc', 'ldc_w'):
                c = k.constants.get(x.operands[0].value)
                if isinstance(c, C.String) and c.string.value in names: last = c.string.value
            if x.mnemonic == 'putstatic' and last:
                fn = k.constants.get(x.operands[0].value).name_and_type.name.value
                tab[fn] = old[last]; SRGNAME[(cn, fn)] = last; last = None
    k = ClassFile(io.BytesIO(z.read('net/minecraft/world/entity/EquipmentSlot.class'))); m = k.methods.find_one(name='<clinit>'); last = None
    for x in m.code.disassemble():
        if x.mnemonic in ('ldc', 'ldc_w'):
            c = k.constants.get(x.operands[0].value)
            if isinstance(c, C.String) and c.string.value in EQS: last = c.string.value
        if x.mnemonic == 'putstatic' and last:
            EQF[k.constants.get(x.operands[0].value).name_and_type.name.value] = last; last = None
    k = ClassFile(io.BytesIO(z.read('net/minecraft/world/item/ArmorItem$Type.class')))
    m = k.methods.find_one(name='<clinit>'); last = None
    for x in m.code.disassemble():
        if x.mnemonic in ('ldc', 'ldc_w'):
            c = k.constants.get(x.operands[0].value)
            if isinstance(c, C.String) and c.string.value in TYPES: last = c.string.value  # not the lowercase name arg
        if x.mnemonic == 'putstatic' and last in TYPES:
            TYPEF[k.constants.get(x.operands[0].value).name_and_type.name.value] = last; last = None
