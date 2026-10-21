# superclass graph across jars -> gear class set; out: cls.json {simpleName(lower,no Item suffix): [fqcn, kind]}
import zipfile,glob,struct,sys,json,os
W=sys.argv[1]
def sup(b):
    if b[:4]!=b'\xca\xfe\xba\xbe': return None
    n=struct.unpack('>H',b[8:10])[0]; i=10; cp=[None]*n; k=1
    while k<n:
        t=b[i]
        if t==1: l=struct.unpack('>H',b[i+1:i+3])[0]; cp[k]=('u',b[i+3:i+3+l].decode('utf8','replace')); i+=3+l
        elif t in(7,8,16,19,20): cp[k]=('c',struct.unpack('>H',b[i+1:i+3])[0]); i+=3
        elif t==15: i+=4
        elif t in(3,4,9,10,11,12,17,18): i+=5
        elif t in(5,6): i+=9; k+=1
        else: return None
        k+=1
    _,this,su=struct.unpack('>HHH',b[i:i+6])
    nm=lambda x: cp[cp[x][1]][1] if x and cp[x] else None
    return nm(this),nm(su)
S={}; jar={}
for j in glob.glob(W+'/pack/mods/*.jar'):
    try: z=zipfile.ZipFile(j)
    except: continue
    for n in z.namelist():
        if n.endswith('.class') and not n.startswith('META-INF'):
            try: r=sup(z.read(n))
            except Exception: r=None
            if r and r[0]: S[r[0]]=r[1]; jar[r[0]]=os.path.basename(j)
BASE={'net/minecraft/world/item/SwordItem':'melee','net/minecraft/world/item/AxeItem':'melee','net/minecraft/world/item/TridentItem':'melee',
'net/minecraft/world/item/BowItem':'ranged','net/minecraft/world/item/CrossbowItem':'ranged','net/minecraft/world/item/ProjectileWeaponItem':'ranged',
'net/minecraft/world/item/ArmorItem':'armor','net/minecraft/world/item/DyeableArmorItem':'armor','net/minecraft/world/item/TieredItem':'tiered',
'net/minecraft/world/item/PickaxeItem':'tool','net/minecraft/world/item/ShovelItem':'tool','net/minecraft/world/item/HoeItem':'tool','net/minecraft/world/item/ShieldItem':'shield'}
def kind(c,d=0):
    while c and d<40:
        if c in BASE: return BASE[c]
        if 'GeoArmor' in c or c.endswith('/GeoArmorItem'): return 'armor'
        c=S.get(c); d+=1
    return None
out={}
for c in S:
    k=kind(S[c]) if c not in BASE else None
    if k:
        sn=c.split('/')[-1].split('$')[-1]
        out.setdefault(sn.lower(),[]).append([c,k,jar[c]])
json.dump(out,open(W+'/eqa/cls.json','w'))
print(len(S),len(out))
