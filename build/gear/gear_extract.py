"""Run mjvm over each gear mod's registration classes; write gear_base.json:
id -> {k (kind), dmg, spd, arm, tough, kbr, slot, mods:[[attr,amt,op]], cls:[class chain]}"""
import sys, json, glob, zipfile, re, collections, time
sys.setrecursionlimit(20000)
sys.path.insert(0, sys.argv[1] + '/scripts')
import mjvm
from mjvm import VM, Obj, MMap, Attr, EnumC, Lam, RegObj, num

S = sys.argv[1]
SRG = glob.glob(S + '/srv/libraries/net/minecraft/server/1.20.1-*/server-1.20.1-*-srg.jar')[0]
ns2jar = json.load(open(S + '/ns2jar.json'))
targets = json.load(open(S + '/targets.json'))  # ns -> [names]
mjvm.load_cfg(S + '/pack/src/overrides/config'); mjvm.load_cfg(S + '/pack/src/overrides/defaultconfigs')
only = sys.argv[2:] if len(sys.argv) > 2 else None

alljars = glob.glob(S + '/pack/mods/*.jar')
out = json.load(open(S + '/gear_base.json')) if only and glob.glob(S + '/gear_base.json') else {}
SLOTS = ['MAINHAND', 'HEAD', 'CHEST', 'LEGS', 'FEET']

def mods_of(vm, o):
    res = {}
    if not isinstance(o, Obj): return res
    cands = []
    for sl in SLOTS:
        e = EnumC('net/minecraft/world/entity/EquipmentSlot', sl, mjvm.EQS.index(sl))
        for nm, ds in (('m_7167_', '(Lnet/minecraft/world/entity/EquipmentSlot;)Lcom/google/common/collect/Multimap;'),
                       ('getAttributeModifiers', '(Lnet/minecraft/world/entity/EquipmentSlot;Lnet/minecraft/world/item/ItemStack;)Lcom/google/common/collect/Multimap;')):
            r = vm.find(o.cls, nm, ds)
            if r and r[2].code and not r[0].startswith('net/minecraft'):
                try: v = vm.run(r[0], r[1], r[2], [o, e] + ([mjvm.Opaque('stack')] if 'ItemStack' in ds else []))
                except Exception: v = None
                if isinstance(v, MMap) and v.items: cands.append((sl, v)); break
    for f in o.f.values():
        if isinstance(f, MMap) and f.items: cands.append((None, f))
    for sl, mm in cands:
        l = []
        for k, v in mm.items:
            if isinstance(k, Attr) and isinstance(v, Obj) and num(v.f.get('amt')):
                op = v.f.get('op'); op = op.name if isinstance(op, EnumC) else str(op)
                l.append([k.n, v.f['amt'], op])
        if l: res[sl or 'field'] = l
    return res

for ns, names in sorted(targets.items()):
    jars = [S + '/pack/mods/' + j for j in ns2jar.get(ns, [])]
    if only and ns not in only: continue
    if not jars: continue
    t0 = time.time(); mjvm.CFG_NS[0] = ns.split('_')[0][:6]
    vm = VM(jars + [SRG] + [j for j in alljars if j not in jars])
    mjvm.srg_tables(vm, SRG)
    want = set(names)
    # candidate classes: those in the gear jars mentioning a wanted name string
    cls = []
    for j in jars:
        z = zipfile.ZipFile(j)
        for n in z.namelist():
            if not n.endswith('.class'): continue
            b = z.read(n)
            if b'<clinit>' not in b: continue
            hit = sum(1 for w in want if w.encode() in b)
            if not hit and re.search(r'(Items|ModItems|ItemRegistry|ItemsRegistry|ItemInit|Registration)$', n[:-6].split('/')[-1]): hit = 0.5
            if hit: cls.append((hit, n[:-6]))
    cls.sort(reverse=True)
    vm.regs = []
    for _, c in cls[:60]:
        try: vm.clinit(c)
        except Exception as ex: pass
        if time.time() - t0 > 240: break
    found = 0
    seen = {}
    for name, val in vm.regs:
        if not isinstance(name, str): continue
        nm = name.split(':')[-1]
        if nm not in want or nm in seen: continue
        vm.budget = vm.steps + 300000
        try: o = vm.resolve(val)
        except Exception: o = None
        if not isinstance(o, Obj): continue
        seen[nm] = o
    for nm, o in seen.items():
        rec = {k: v for k, v in o.gear.items() if k in ('k', 'dmg', 'spd', 'arm', 'tough', 'kbr', 'slot') and (num(v) or isinstance(v, str))}
        vm.budget = vm.steps + 300000
        try: m = mods_of(vm, o)
        except Exception: m = {}
        if m: rec['mods'] = m
        rec['cls'] = [c.split('/')[-1] for c in vm.supers(o.cls)][:6]
        out[ns + ':' + nm] = rec; found += 1
    print(ns, 'want', len(want), 'regs', len(vm.regs), 'found', found, 'stats', sum(1 for nm in seen if any(k in out[ns + ':' + nm] for k in ('dmg', 'arm', 'mods'))), '%.0fs' % (time.time() - t0), flush=True)
    json.dump(out, open(S + '/gear_base.json', 'w'))
