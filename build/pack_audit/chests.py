"""Chance that one chest of each loot table holds the curio (all pools, all rolls), vs the wiki text."""
import json,re,sys,zipfile,glob
W=sys.argv[1]; R=sys.argv[2]
rec=json.load(open(W+'/rec.json'))
s=open(R+'/build/src/data.js',encoding='utf-8').read();D,_=json.JSONDecoder().raw_decode(s,8)
idx={}
for j in glob.glob(W+'/pack/mods/*.jar'):
    try: z=zipfile.ZipFile(j)
    except: continue
    for n in z.namelist():
        m=re.match(r'data/([^/]+)/loot_tables/(.+)\.json$',n)
        if m: idx[m.group(1)+':'+m.group(2)]=(j,n)
for f in glob.glob(W+'/pack/src/overrides/kubejs/data/*/loot_tables/**/*.json',recursive=True):
    m=re.search(r'data/([^/]+)/loot_tables/(.+)\.json$',f); idx[m.group(1)+':'+m.group(2)]=(None,f)
def load(t):
    j,n=idx[t]; return json.loads((zipfile.ZipFile(j).read(n) if j else open(n,'rb').read()).decode('utf-8','ignore'))
def rolls(r):
    if isinstance(r,(int,float)): return r
    if isinstance(r,dict): return (r.get('min',1)+r.get('max',r.get('min',1)))/2
    return 1
def cond(cs):
    p=1
    for c in cs or []:
        if 'random_chance' in c.get('condition',''): p*=c.get('chance',1)
    return p
def flat(es):
    out=[]
    for e in es:
        t=e.get('type','')
        if t.endswith('alternatives') or t.endswith('group') or t.endswith('sequence'): out+=flat(e.get('children',[]))
        else: out.append(e)
    return out
def chance(o,item):
    miss=1.0
    for p in o.get('pools',[]):
        es=flat(p.get('entries',[])); tw=sum(e.get('weight',1) for e in es)
        if not tw: continue
        pe=sum(e.get('weight',1)*cond(e.get('conditions')) for e in es if e.get('name')==item)/tw
        if pe: miss*=(1-pe*cond(p.get('conditions')))**rolls(p.get('rolls',1))
    return 1-miss
out=[]
for d in D:
    best={}
    for t in rec['loot'].get(d['id'],[]):
        if t not in idx or '/entities/' in t or t.split(':')[1].startswith('entities/'): continue
        try: c=chance(load(t),d['id'])
        except Exception: continue
        if c>0: best[t]=round(c*100,2)
    if not best: continue
    txt=' / '.join(d['src'])
    nums=[float(x) for x in re.findall(r'([0-9.]+)% per chest',txt)]
    mx=max(best.values())
    flag='' if not nums or abs(max(nums)-mx)<=max(0.6,0.15*mx) else '  <<< DIFF'
    out.append(f"{d['id']} | pack max {mx}% ({max(best,key=best.get)}) n={len(best)} | wiki {nums[:4]}{flag}")
print('\n'.join(out))
