"""Vanilla 1.20.1 gear straight from the server bytecode (SRG jar).
1. interpret Tiers.<clinit> and ArmorMaterials.<clinit>, read every constant through its getter -> check mjvm's VTIER/VARM tables
2. interpret TridentItem.<init> (no model) -> its attribute modifiers
3. interpret Items.<clinit> -> every registered SwordItem/AxeItem/TridentItem/BowItem/CrossbowItem/ArmorItem
Writes vanilla_gear.json: id -> record in gear_base format (dmg/spd = modifier amounts as SwordItem stores them; dmg_total/spd_total
= what the tooltip shows: base 1 attack damage and 4 attack speed added), and vanilla_check.json."""
import sys, json, glob, os
sys.setrecursionlimit(20000)
G = sys.argv[1]; sys.path.insert(0, G)
import mjvm
from mjvm import VM, Obj, MMap, Attr, EnumC, num
SRG = glob.glob(G + '/srv/libraries/net/minecraft/server/1.20.1-*/server-1.20.1-*-srg.jar')[0]
vm = VM([SRG]); mjvm.srg_tables(vm, SRG); vm.fsteps = 2_000_000
check = {'tiers': {}, 'armor_materials': {}, 'mismatch': []}
# ---- 1. enums
T = 'net/minecraft/world/item/Tiers'; AM = 'net/minecraft/world/item/ArmorMaterials'
for cn in (T, AM):
    k = vm.cf(cn); m = k.methods.find_one(name='<clinit>'); vm.run(cn, k, m, [])
TYP = {t: EnumC('net/minecraft/world/item/ArmorItem$Type', t, i) for i, t in enumerate(mjvm.TYPES)}
for (cn, fld), name in mjvm.SRGNAME.items():
    o = vm.statics.get((cn, fld))
    if not isinstance(o, Obj): check['mismatch'].append('could not interpret %s.%s' % (cn, name)); continue
    if cn == T:
        v = {g: vm.call_virtual(o, m, '()' + r, []) for g, m, r in (('level', 'm_6604_', 'I'), ('uses', 'm_6609_', 'I'), ('speed', 'm_6624_', 'F'), ('dmg_bonus', 'm_6631_', 'F'))}
        check['tiers'][name] = v
        old = mjvm.VTIER0[name]
        if not all(num(a) and abs(a - b) < 1e-6 for a, b in zip((v['level'], v['uses'], v['speed'], v['dmg_bonus']), old)): check['mismatch'].append('Tiers.%s bytecode %s != mjvm %s' % (name, v, old))
    else:
        d = tuple(vm.call_virtual(o, 'm_7366_', '(Lnet/minecraft/world/item/ArmorItem$Type;)I', [TYP[t]]) for t in mjvm.TYPES)
        tg = vm.call_virtual(o, 'm_6651_', '()F', []); kb = vm.call_virtual(o, 'm_6649_', '()F', [])
        check['armor_materials'][name] = {'defense': dict(zip(mjvm.TYPES, d)), 'toughness': tg, 'kbr': kb}
        close = lambda a, b: num(a) and num(b) and abs(a - b) < 1e-6
        o1 = mjvm.VARM0[name]
        if not (d == o1[0] and close(tg, o1[1]) and close(kb, o1[2])):
            # TURTLE has only a helmet; compare the helmet value there
            o0 = mjvm.VARM0[name]
            if not (name == 'TURTLE' and d[0] == o0[0][0] and tg == o0[1] and kb == o0[2]):
                check['mismatch'].append('ArmorMaterials.%s bytecode %s/%s/%s != mjvm %s' % (name, d, tg, kb, o0))
# ---- 2. TridentItem constructor, interpreted for real
real = VM.model_init
def no_trident(s, cls, obj, args):
    if cls == 'net/minecraft/world/item/TridentItem': return False
    return real(s, cls, obj, args)
VM.model_init = no_trident
tr = vm.construct('net/minecraft/world/item/TridentItem', '(Lnet/minecraft/world/item/Item$Properties;)V', [mjvm.Opaque('props')])
VM.model_init = real
tmods = []
for f in tr.f.values():
    if isinstance(f, MMap):
        for a, v in f.items:
            if isinstance(a, Attr) and isinstance(v, Obj): tmods.append([a.n, v.f.get('amt'), v.f.get('op').name if isinstance(v.f.get('op'), EnumC) else str(v.f.get('op'))])
check['trident_modifiers'] = tmods
tdmg = next((m[1] for m in tmods if m[0] == 'generic.attack_damage'), None); tspd = next((m[1] for m in tmods if m[0] == 'generic.attack_speed'), None)
if (tdmg, tspd) != (8.0, -2.9) and not (num(tspd) and abs(tspd + 2.9) < 1e-6 and tdmg == 8.0): check['mismatch'].append('TridentItem bytecode %s/%s != mjvm model 8.0/-2.9' % (tdmg, tspd))
# ---- 3. Items.<clinit>
vm.regs = []; vm.budget = 10**9
k = vm.cf('net/minecraft/world/item/Items'); m = k.methods.find_one(name='<clinit>')
vm.run('net/minecraft/world/item/Items', k, m, [])
out = {}
KEEP = {'sword', 'axe', 'trident', 'bow', 'crossbow', 'armor'}
for name, val in vm.regs:
    if not isinstance(name, str) or not isinstance(val, Obj): continue
    g = val.gear; kd = g.get('k')
    if kd not in KEEP: continue
    nm = name.split(':')[-1]
    if nm in out: continue
    rec = {'k': kd, 'src': 'vanilla', 'cls': [c.split('/')[-1] for c in vm.supers(val.cls)][:6]}
    for f in ('dmg', 'spd', 'arm', 'tough', 'kbr', 'slot'):
        v = g.get(f)
        if num(v): rec[f] = round(v, 4) if isinstance(v, float) else v
        elif isinstance(v, str): rec[f] = v
    if kd == 'trident' and tmods: rec['dmg'], rec['spd'] = round(tdmg, 4), round(tspd, 4)
    if num(rec.get('dmg')): rec['dmg_total'] = round(rec['dmg'] + 1, 4)
    if num(rec.get('spd')): rec['spd_total'] = round(rec['spd'] + 4, 4)
    t = g.get('tier')
    if isinstance(t, tuple): rec['tier'] = mjvm.SRGNAME.get((T, t[1]), t[1])
    out['minecraft:' + nm] = rec
check['items_regs'] = len(vm.regs); check['steps'] = vm.steps
json.dump(out, open(G + '/vanilla_gear.json', 'w'), indent=1)
json.dump(check, open(G + '/vanilla_check.json', 'w'), indent=1)
print(len(out), 'vanilla gear; mismatches:', check['mismatch'])
for i, r in sorted(out.items()): print(i, {k: v for k, v in r.items() if k not in ('cls', 'src')})
