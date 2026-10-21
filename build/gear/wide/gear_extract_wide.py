"""Wide gear extraction: run mjvm over the registration code of every namespace that ships gear classes or has explicit
gear targets (targets.json / ns_plan.json from tools/targets_wide.py).
Per namespace: candidate registry classes = classes in the namespace's jars that reference a gear class (clsgraph refs)
or name a wanted item, ranked; their <clinit> runs in the mini JVM; every captured registration whose object resolves to
a gear class (or is an explicit target) is recorded.
Output: ext_raw/<ns>.json  {records: id -> rec, fail: id -> reason, info}
rec: k (constructor model: sword/axe/tool/tiered/armor/trident/bow/crossbow/shield), kind (class graph), dmg/spd (modifier
amounts, as SwordItem stores them), arm/tough/kbr, slot, mods {slot: [[attr, amount, op]]}, cls (class chain), src."""
import sys, json, glob, zipfile, re, time, os, collections, traceback
sys.setrecursionlimit(20000)
G = sys.argv[1]; sys.path.insert(0, G)
import mjvm
from mjvm import VM, Obj, MMap, Attr, EnumC, Lam, RegObj, num

SRG = glob.glob(G + '/srv/libraries/net/minecraft/server/1.20.1-*/server-1.20.1-*-srg.jar')[0]
JARS = sorted(glob.glob(G + '/pack/mods/*.jar')) + sorted(glob.glob(G + '/nested/*.jar'))
OUTD = os.environ.get('OUTD', G + '/ext_raw'); os.makedirs(OUTD, exist_ok=True)
SLOTS = ['MAINHAND', 'OFFHAND', 'HEAD', 'CHEST', 'LEGS', 'FEET']
I = 'net/minecraft/world/item/'
VBASE = {I + 'SwordItem': 'sword', I + 'AxeItem': 'axe', I + 'TridentItem': 'trident', I + 'BowItem': 'bow', I + 'CrossbowItem': 'crossbow',
         I + 'ProjectileWeaponItem': 'ranged', I + 'ArmorItem': 'armor', I + 'DyeableArmorItem': 'armor', I + 'ShieldItem': 'shield',
         I + 'PickaxeItem': 'pickaxe', I + 'ShovelItem': 'shovel', I + 'HoeItem': 'hoe', I + 'DiggerItem': 'digger', I + 'TieredItem': 'tiered'}
TOOLN = re.compile(r'(pickaxe|shovel|(^|_)hoe(_|$)|paxel|excavator|_drill$|^drill|multitool|aiot|mattock|fishing_rod|shears|wrench|spanner|_spade$|_saw$|hammer_drill|trowel)')
REGNAME = re.compile(r'(Items|ModItems|ItemRegistry|ItemsRegistry|ItemInit|Registration|Registry|Weapons|Armors?|Armou?rs|Tools|Gear|Equipment|Content|Init)$')
OPN = {0: 'ADDITION', 1: 'MULTIPLY_BASE', 2: 'MULTIPLY_TOTAL'}

def opname(op):
    if isinstance(op, EnumC): return op.name
    if isinstance(op, Attr): return op.n.split('.')[-1]
    if isinstance(op, int) and op in OPN: return OPN[op]
    s = str(op); m = re.search(r'(ADDITION|MULTIPLY_BASE|MULTIPLY_TOTAL)', s)
    return m.group(1) if m else s

def r4(v): return round(v, 4) if isinstance(v, float) else v

ATTRB = 'net/minecraft/world/entity/ai/attributes/Attribute'
ITEMC = 'net/minecraft/world/item/Item'
def attr_name(vm, k):
    """vanilla attributes are Attr('generic.x'); mod attributes are the registered Attribute object: name them
    ns:registry_name (namespace from the description id 'attribute.name.<ns>.<name>') or by the description id"""
    if isinstance(k, Attr): return k.n
    if not isinstance(k, Obj) or ATTRB not in vm.supers(k.cls): return None
    reg = k.f.get('$regname'); did = k.f.get('f_22078_')  # Attribute.descriptionId
    if isinstance(reg, str) and ':' in reg: return reg
    if isinstance(did, str):
        p = did.split('.')
        if isinstance(reg, str) and p[-1] == reg and len(p) >= 2 and p[-2] not in ('name', 'attribute', 'generic', 'player'): return p[-2] + ':' + reg
        if isinstance(reg, str): return reg + ' [' + did + ']'
        return did
    return reg if isinstance(reg, str) else None

def mods_of(vm, o):
    res = {}
    if not isinstance(o, Obj): return res
    cands = []
    def ent(mm): return {(attr_name(vm, k), r4(v.f['amt']), opname(v.f.get('op'))) for k, v in mm.items
                         if attr_name(vm, k) and isinstance(v, Obj) and num(v.f.get('amt'))}
    for sl in SLOTS:
        e = EnumC('net/minecraft/world/entity/EquipmentSlot', sl, mjvm.EQS.index(sl))
        got = {}
        for nm, ds in (('m_7167_', '(Lnet/minecraft/world/entity/EquipmentSlot;)Lcom/google/common/collect/Multimap;'),
                       ('getAttributeModifiers', '(Lnet/minecraft/world/entity/EquipmentSlot;Lnet/minecraft/world/item/ItemStack;)Lcom/google/common/collect/Multimap;')):
            r = vm.find(o.cls, nm, ds)
            if r and r[2].code and not r[0].startswith('net/minecraft'):
                vm.budget = vm.steps + 300000
                try: v = vm.run(r[0], r[1], r[2], [o, e] + ([mjvm.Opaque('stack')] if 'ItemStack' in ds else []))
                except Exception: v = None
                if isinstance(v, MMap) and v.items: got[nm] = v
        A, B = got.get('m_7167_'), got.get('getAttributeModifiers')
        # the game calls the stack-aware Forge method; prefer it when it keeps every default modifier (it only adds to them)
        if B is not None and ent(B) and (A is None or ent(A) <= ent(B)): cands.append((sl + '~stack', B))
        elif A is not None: cands.append((sl, A))
    for fk, f in o.f.items():
        if isinstance(f, MMap) and f.items: cands.append((None, f))
    for sl, mm in cands:
        l = []
        for k, v in mm.items:
            an = attr_name(vm, k)
            if an and isinstance(v, Obj) and num(v.f.get('amt')):
                e = [an, r4(v.f['amt']), opname(v.f.get('op'))]
                if e not in l: l.append(e)  # a loop with an unknown bound repeats the same put; real items do not stack identical modifiers
        sl = sl or 'field'
        if sl.endswith('~stack'):
            sl = sl[:-6]
            if l: res.setdefault('_stack_dependent', []).append(sl)
        if l and sl not in res: res[sl] = l
    return res

_W = {}
def winit():
    idx = {}; zs = {}
    for j in JARS + [SRG]:
        try: z = zipfile.ZipFile(j)
        except Exception: continue
        zs[os.path.basename(j)] = z
        for n in z.namelist():
            if n.endswith('.class') and not n.startswith('META-INF'): idx.setdefault(n[:-6], (z, n))
    vm = VM([]); vm.idx = idx; mjvm.srg_tables(vm, SRG)
    mjvm.load_cfg(G + '/pack/src/overrides/config'); mjvm.load_cfg(G + '/pack/src/overrides/defaultconfigs')
    cg = json.load(open(G + '/clsgraph.json'))
    _W.update(idx=idx, zs=zs, attrname=dict(vm.attrname), cg=cg, gearset=set(cg['gear']), attrset=set(cg['attr']),
              plan=json.load(open(G + '/ns_plan.json')), meta=json.load(open(G + '/targets_meta.json')),
              lang=json.load(open(G + '/lang_wide.json')), curio=set(json.load(open(G + '/curio_ids.json'))))

def class_kind(vm, cls):
    chain = vm.supers(cls)
    for c in chain:
        k = _W['cg']['gear'].get(c) or VBASE.get(c)
        if k: return k, chain
    if any(c in _W['attrset'] for c in chain): return 'attr', chain
    return None, chain

def has_model(ns, nm, jars):
    for j in jars:
        z = _W['zs'].get(j)
        if z is None: continue
        try: z.getinfo('assets/%s/models/item/%s.json' % (ns, nm)); return True
        except KeyError: pass
    return False

def stats_ok(rec):
    k = rec.get('kind') or rec.get('k')
    m = rec.get('mods') or {}
    flat = [a for l in m.values() for a in l]
    if k == 'armor':
        return num(rec.get('arm')) or any(a[0].endswith('armor') and a[2] == 'ADDITION' for a in flat)
    if k in ('bow', 'crossbow', 'ranged'): return True  # no melee stats by design
    return num(rec.get('dmg')) or any(a[0].endswith('attack_damage') and a[2] == 'ADDITION' for a in flat)

def build_rec(vm, nm, o, kind, chain):
    g = o.gear
    rec = {'src': 'mjvm'}
    for f in ('k', 'dmg', 'spd', 'arm', 'tough', 'kbr', 'slot'):
        v = g.get(f)
        if num(v): rec[f] = r4(v)
        elif isinstance(v, str): rec[f] = v
    if kind: rec['kind'] = kind
    t = g.get('tier')
    if t is not None and not num(rec.get('dmg')) and rec.get('k') in ('sword', 'axe', 'tool', 'tiered', 'pickaxe', 'shovel', 'hoe'):
        rec['why_no_dmg'] = 'tier bonus unresolved (%s)' % (type(t).__name__ if not isinstance(t, (Obj, EnumC)) else getattr(t, 'cls', '?').split('/')[-1])
    try: m = mods_of(vm, o)
    except Exception: m = {}
    sd = m.pop('_stack_dependent', None)
    if m: rec['mods'] = m
    if sd: rec['mods_stack_dependent'] = sorted(set(sd))  # getAttributeModifiers(slot, stack): may include conditional bonuses
    try: gt = getters(vm, o)
    except Exception: gt = {}
    if gt: rec['getters'] = gt
    rec['cls'] = [c.split('/')[-1] for c in chain][:6]
    return rec

GETN = re.compile(r'(?i)(damage|dmg|attack_?speed|range|reach|cooldown|velocity|power)')
def getters(vm, o):
    """no-argument numeric methods the mod declares on the item (whip damage, gun bullet damage, staff power...): read-only
    values the item's code computes from its fields / config; informational, not attribute modifiers"""
    out = {}; seen = set()
    for c in vm.supers(o.cls):
        if c.startswith(mjvm.VPFX): break
        k = vm.cf(c)
        if not k: continue
        for m in k.methods:
            nm = m.name.value; ds = m.descriptor.value
            if nm in seen or not m.code or m.access_flags.get('acc_static') or ds not in ('()D', '()F', '()I') or not GETN.search(nm): continue
            seen.add(nm)
            vm.budget = vm.steps + 100000
            try: v = vm.run(c, k, m, [o])
            except Exception: v = None
            if num(v): out[nm] = r4(float(v)) if isinstance(v, float) else v
    return out

def candidates(vm, ns, P, want, explicit):
    jarset = set(P['jars']); cg = _W['cg']; sc = collections.Counter()
    for c, gr in cg['refs'].items():
        if cg['jar'].get(c) in jarset:
            sc[c] += 10 * len(gr) + sum(1 for s in cg['strs'].get(c, ()) if s in want)
    ex = [w.encode() for w in explicit]
    for j in P['jars']:
        z = _W['zs'].get(j)
        if z is None: continue
        for n in z.namelist():
            if not n.endswith('.class') or n.startswith('META-INF'): continue
            c = n[:-6]
            b = z.read(n)
            if b'<clinit>' not in b: continue
            hit = sum(1 for w in ex if w in b)
            if hit: sc[c] += hit
            elif c not in sc and REGNAME.search(c.split('/')[-1]): sc[c] += 0.5
    # registry holders first (the mod constructor touches them first in the real JVM; running a material or item class
    # first can trigger the registry's <clinit> while that class is still half-initialised)
    reg = lambda c: 0 if '$' not in c and re.search(r'(Items?|ItemRegistry|ItemsRegistry|ItemInit|Weapons|Armou?rs|Equipment)(Registry|Init|Register|Reg)?$', c.split('/')[-1]) else 1
    return [c for c, v in sorted(sc.items(), key=lambda kv: (reg(kv[0]), -kv[1], kv[0]))]

def mod_classes(jars):
    out = []
    for j in jars:
        z = _W['zs'].get(j)
        if z is None: continue
        for n in z.namelist():
            if n.endswith('.class') and not n.startswith('META-INF') and '$' not in n:
                try: b = z.read(n)
                except Exception: continue
                if b'Lnet/minecraftforge/fml/common/Mod;' in b: out.append(n[:-6])
    return out

def run_ns(ns):
    t0 = time.time()
    P = _W['plan'][ns]; lang = _W['lang']; meta = _W['meta']
    vm = VM([]); vm.idx = dict(_W['idx']); vm.attrname = _W['attrname']; vm.hard = int(os.environ.get('HARD_STEPS', 60_000_000))
    for j in P['jars']:
        z = _W['zs'].get(j)
        if z is None: continue
        for n in z.namelist():
            if n.endswith('.class') and not n.startswith('META-INF'): vm.idx[n[:-6]] = (z, n)
    mjvm.CFG_NS[0] = ns.split('_')[0][:6]
    explicit = set(P['explicit']); want = set(P['want_all']) | explicit
    cls = candidates(vm, ns, P, want, explicit)
    vm.regs = []; ran = 0
    # the @Mod entry classes first: their constructors create the config objects (and registries) the items read later
    for c in mod_classes(P['jars']):
        k = vm.cf(c)
        if not k: continue
        ini = [m for m in k.methods if m.name.value == '<init>' and m.code]
        if not ini: continue
        ds = min((m.descriptor.value for m in ini), key=mjvm.argc)
        vm.budget = vm.steps + 600000
        try: vm.construct(c, ds, [mjvm.Opaque('modctx')] * mjvm.argc(ds))
        except Exception: pass
    for c in cls[:160]:
        try: vm.clinit(c)
        except Exception: pass
        ran += 1
        if time.time() - t0 > 300: break
    seen, why, kept, notgear = {}, {}, {}, {}
    curio = _W['curio']
    def take(name, val):
        if not isinstance(name, str): return
        nm = name.split(':')[-1]
        if ':' in name and name.split(':')[0] not in (ns, 'minecraft') and name.split(':')[0] != '': return
        if nm in kept and kept[nm][1] != 'item': return
        if not re.fullmatch(r'[a-z0-9_./-]+', nm): return
        vm.budget = vm.steps + 300000
        try: o = vm.resolve(val)
        except Exception: o = None
        if not isinstance(o, Obj):
            if nm in explicit: why.setdefault(nm, 'registered but supplier did not resolve to an object (%s)' % type(o).__name__)
            return
        kind, chain = class_kind(vm, o.cls)
        if ITEMC not in chain:  # a string + object pair that is no Item (config/type objects named like the item)
            if nm in explicit: why.setdefault(nm, 'name captured with a non-Item object (%s)' % o.cls.split('/')[-1])
            return
        if nm in kept and not (kind and kind != 'item'): return  # only upgrade a plain-Item capture to a gear-class one
        iid = ns + ':' + nm
        if nm not in explicit:
            if not kind: return
            if ('/' in nm or 'compat' in nm) and nm not in want: return  # optional-compat registrations (other mod absent)
            if nm not in want and not has_model(ns, nm, P['jars']): return
            if kind in ('pickaxe', 'shovel', 'hoe', 'digger', 'attr', 'tiered') and TOOLN.search(nm): return
            if iid in curio and kind in ('attr', 'tiered'): return
        elif not kind:
            kind = 'item'  # explicit target whose class is no gear class (wands, tomes, plain Item subclasses)
        kept[nm] = (o, kind, chain)
    for name, val in vm.regs: take(name, val)
    # second pass for explicit targets still missing: run the static methods of the candidate classes that mention them
    miss = explicit - set(kept)
    if miss and time.time() - t0 < 420:
        mb = set()
        for w in miss:  # the full name, or a string-concat recipe that builds it ("armor_faraday_\u0001", "\u0001_helmet")
            mb.add(w.encode()); t = w.split('_')
            for q in range(1, len(t)):
                a, b = '_'.join(t[:q]) + '_', '_' + '_'.join(t[q:])
                if len(a) >= 4: mb.add(a.encode() + b'\x01')
                if len(b) >= 4: mb.add(b'\x01' + b.encode())
        r0 = len(vm.regs)
        for c in cls[:160]:
            e = vm.idx.get(c)
            if not e: continue
            b = e[0].read(e[1])
            if not any(w in b for w in mb): continue
            k = vm.cf(c)
            if not k: continue
            recv = None
            for m in k.methods:
                if not m.code or m.name.value in ('<clinit>', '<init>'): continue
                n = mjvm.argc(m.descriptor.value)
                if n > 3: continue
                st = m.access_flags.get('acc_static')
                if not st and recv is None:  # module-style registration (Quark modules, event handlers): run on a default instance
                    vm.budget = vm.steps + 400000
                    try: recv = vm.construct(c, '()V', [])
                    except Exception: recv = Obj(c)
                vm.budget = vm.steps + 400000
                try: vm.run(c, k, m, ([] if st else [recv]) + [mjvm.Opaque('arg')] * n)
                except Exception: pass
            if time.time() - t0 > 480: break
        for name, val in vm.regs[r0:]: take(name, val)
    miss = explicit - set(kept)
    if miss and time.time() - t0 < 500:
        vm2 = VM([]); vm2.idx = vm.idx; vm2.attrname = vm.attrname; vm2.hard = vm.hard; vm2.cache = vm.cache
        vm2.regs = []; vm0 = vm; vm = vm2
        for c in list(reversed(cls[:160])):
            try: vm.clinit(c)
            except Exception: pass
            if time.time() - t0 > 560: break
        for name, val in vm.regs:
            if isinstance(name, str) and name.split(':')[-1] in miss: take(name, val)
        info_retry = len(explicit - set(kept))
    recs = {}; nongear = {}
    for nm, (o, kind, chain) in kept.items():
        try: rec = build_rec(vm, nm, o, kind, chain)
        except Exception as ex: rec = {'src': 'mjvm', 'error': repr(ex)[:200]}
        recs[ns + ':' + nm] = rec
    fail = {}
    regnames = {n.split(':')[-1] for n, _ in vm.regs if isinstance(n, str)}
    for nm in sorted(explicit - set(kept)):
        fail[ns + ':' + nm] = why.get(nm) or ('name never seen in captured registrations' if nm not in regnames else 'registered under this name but value unresolved')
    amb = sorted([k, list(v)] for n0, k, v in mjvm.CFG_AMBIG if n0 == mjvm.CFG_NS[0]); mjvm.CFG_AMBIG.clear()
    info = {'ns': ns, 'cfg_ambiguous': amb, 'cands': len(cls), 'ran': ran, 'regs': len(vm.regs), 'kept': len(recs), 'explicit': len(explicit),
            'secs': round(time.time() - t0, 1), 'steps': vm.steps}
    hint_miss = sorted(set(P.get('hints', [])) - set(kept))
    json.dump({'records': recs, 'fail': fail, 'nongear': nongear, 'hint_miss': hint_miss, 'info': info}, open(OUTD + '/' + ns + '.json', 'w'))
    return info

def job(ns):
    try: return run_ns(ns)
    except Exception as ex:
        info = {'ns': ns, 'crash': traceback.format_exc()[-800:]}
        json.dump({'records': {}, 'fail': {}, 'info': info}, open(OUTD + '/' + ns + '.json', 'w'))
        return info

if __name__ == '__main__':
    import multiprocessing as mp
    plan = json.load(open(G + '/ns_plan.json'))
    only = sys.argv[2:]
    todo = [ns for ns in plan if (not only or ns in only)]
    todo.sort(key=lambda n: -len(plan[n]['want_all']))
    nproc = int(os.environ.get('NPROC', '4'))
    if nproc == 1:
        winit()
        for ns in todo: print(json.dumps(job(ns)), flush=True)
    else:
        with mp.get_context('fork').Pool(nproc, initializer=winit, maxtasksperchild=6) as pool:
            for info in pool.imap_unordered(job, todo): print(json.dumps(info), flush=True)
