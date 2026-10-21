"""Class hierarchy over every jar (pack/mods/*.jar, nested jar-in-jar mods in gx/nested, and the 1.20.1 SRG server jar).
Writes clsgraph.json:
  sup:   cls -> super            ifs: cls -> [interfaces]      jar: cls -> jar basename
  gear:  cls -> kind (sword/axe/trident/bow/crossbow/ranged/armor/tiered/digger/pickaxe/shovel/hoe/shield) for every
         mod class whose superclass chain reaches a vanilla gear base (or a GeckoLib armor base)
  attr:  [cls]  mod classes that override Item.getAttributeModifiers(EquipmentSlot[, ItemStack])
  refs:  cls -> [gear classes referenced in its constant pool]  (classes with a <clinit> or static methods only)
  strs:  cls -> [string constants that look like registry names] (same classes)"""
import zipfile, glob, struct, sys, json, os, re
G = sys.argv[1]
SRG = glob.glob(G + '/srv/libraries/net/minecraft/server/1.20.1-*/server-1.20.1-*-srg.jar')[0]
jars = sorted(glob.glob(G + '/pack/mods/*.jar')) + sorted(glob.glob(G + '/nested/*.jar')) + [SRG]
IDRX = re.compile(r'^[a-z0-9_./-]{3,80}$')

def parse(b):
    if b[:4] != b'\xca\xfe\xba\xbe': return None
    n = struct.unpack('>H', b[8:10])[0]; i = 10; cp = [None] * n; k = 1
    while k < n:
        t = b[i]
        if t == 1:
            l = struct.unpack('>H', b[i + 1:i + 3])[0]; cp[k] = ('u', b[i + 3:i + 3 + l].decode('utf8', 'replace')); i += 3 + l
        elif t == 7: cp[k] = ('c', struct.unpack('>H', b[i + 1:i + 3])[0]); i += 3
        elif t == 8: cp[k] = ('s', struct.unpack('>H', b[i + 1:i + 3])[0]); i += 3
        elif t in (16, 19, 20): i += 3
        elif t == 15: i += 4
        elif t in (3, 4, 9, 10, 11, 12, 17, 18): i += 5
        elif t in (5, 6): i += 9; k += 1
        else: return None
        k += 1
    u = lambda x: cp[x][1] if x and cp[x] and cp[x][0] == 'u' else None
    cn = lambda x: u(cp[x][1]) if x and cp[x] and cp[x][0] == 'c' else None
    acc, this, su = struct.unpack('>HHH', b[i:i + 6]); i += 6
    ni = struct.unpack('>H', b[i:i + 2])[0]; i += 2
    ifs = [cn(struct.unpack('>H', b[i + 2 * q:i + 2 * q + 2])[0]) for q in range(ni)]; i += 2 * ni
    def skip_members(i, keep):
        cnt = struct.unpack('>H', b[i:i + 2])[0]; i += 2; out = []
        for _ in range(cnt):
            ma, mn, md, ac = struct.unpack('>HHHH', b[i:i + 8]); i += 8
            for _ in range(ac):
                l = struct.unpack('>I', b[i + 2:i + 6])[0]; i += 6 + l
            if keep: out.append((ma, u(mn), u(md)))
        return i, out
    i, _ = skip_members(i, False)
    i, ms = skip_members(i, True)
    refs = [cn(q) for q in range(1, n) if cp[q] and cp[q][0] == 'c']
    strs = [u(cp[q][1]) for q in range(1, n) if cp[q] and cp[q][0] == 's']
    return cn(this), cn(su), ifs, ms, refs, strs

sup, ifs, jar, meth, raw = {}, {}, {}, {}, {}
for j in jars:
    try: z = zipfile.ZipFile(j)
    except Exception: continue
    is_srg = j == SRG
    for n in z.namelist():
        if not n.endswith('.class') or n.startswith('META-INF'): continue
        try: r = parse(z.read(n))
        except Exception: r = None
        if not r or not r[0]: continue
        c, s, fi, ms, refs, strs = r
        if c in sup: continue
        sup[c] = s; jar[c] = os.path.basename(j)
        if fi: ifs[c] = fi
        if is_srg: continue
        am = any((nm == 'm_7167_' and d == '(Lnet/minecraft/world/entity/EquipmentSlot;)Lcom/google/common/collect/Multimap;') or
                 (nm == 'getAttributeModifiers' and d.startswith('(Lnet/minecraft/world/entity/EquipmentSlot;Lnet/minecraft/world/item/ItemStack;)')) for _, nm, d in ms)
        hasstatic = any(nm == '<clinit>' or (ma & 0x0008) for ma, nm, d in ms)
        if am: meth[c] = 1
        if hasstatic: raw[c] = (refs, [x for x in strs if x and IDRX.match(x)])

I = 'net/minecraft/world/item/'
BASE = {I + 'SwordItem': 'sword', I + 'AxeItem': 'axe', I + 'TridentItem': 'trident', I + 'BowItem': 'bow', I + 'CrossbowItem': 'crossbow',
        I + 'ProjectileWeaponItem': 'ranged', I + 'ArmorItem': 'armor', I + 'ShieldItem': 'shield', I + 'PickaxeItem': 'pickaxe',
        I + 'ShovelItem': 'shovel', I + 'HoeItem': 'hoe', I + 'DiggerItem': 'digger', I + 'TieredItem': 'tiered',
        I + 'ElytraItem': 'elytra', I + 'HorseArmorItem': 'horse_armor'}
memo = {}
def kind(c):
    path = []; k = None; d = 0
    while c and d < 60:
        if c in memo: k = memo[c]; break
        if c in BASE: k = BASE[c]; break
        if 'geckolib' in c and 'GeoArmor' in c and c.endswith('Item'): k = 'armor'; break
        path.append(c); c = sup.get(c); d += 1
    for p in path: memo[p] = k
    return k
gear = {}
for c in sup:
    if c.startswith('net/minecraft/') or c in BASE: continue
    k = kind(c)
    if k and k not in ('elytra', 'horse_armor'): gear[c] = k
attr = sorted(c for c in meth if c not in gear)
gs = set(gear)
refs, strs = {}, {}
for c, (rf, st) in raw.items():
    g = sorted({x for x in rf if x in gs and x != c})
    if g: refs[c] = g; strs[c] = sorted(set(st))[:4000]
json.dump({'sup': sup, 'ifs': ifs, 'jar': jar, 'gear': gear, 'attr': attr, 'refs': refs, 'strs': strs}, open(G + '/clsgraph.json', 'w'))
import collections
print('classes', len(sup), 'gear classes', len(gear), collections.Counter(gear.values()), 'attr-override classes', len(attr), 'registry-like (refs gear)', len(refs))
