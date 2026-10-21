import json,sys,os,glob
G=sys.argv[1]; dirs=sys.argv[2:]
sys.path.insert(0,G)
num=lambda v: isinstance(v,(int,float)) and not isinstance(v,bool)
def hs(rec):
    k=rec.get('kind') or rec.get('k'); m=rec.get('mods') or {}
    fl=[a for l in m.values() for a in l]
    if k=='item': return True
    if k=='attr': return bool(m) or num(rec.get('dmg'))
    if k=='armor': return num(rec.get('arm')) or any(a[0].endswith('armor') and a[2]=='ADDITION' for a in fl)
    if k in ('bow','crossbow','ranged','shield'): return True
    return num(rec.get('dmg')) or any(a[0].endswith('attack_damage') and a[2]=='ADDITION' for a in fl)
nss=sorted(set(os.path.basename(f)[:-5] for d in dirs for f in glob.glob(G+'/'+d+'/*.json')))
for ns in nss:
    row=[ns]
    for d in dirs:
        p=G+'/'+d+'/'+ns+'.json'
        if not os.path.exists(p): row.append('-'); continue
        j=json.load(open(p)); r=j['records']
        row.append('%d/%d/f%d'%(len(r),sum(1 for v in r.values() if hs(v)),len(j['fail'])))
    print(' '.join('%-26s'%x for x in row))
