"""Chance that one chest of each loot table holds the curio (all pools, all rolls; lootlib.py, luck 0), vs the wiki text.
Usage: chests.py W REPO"""
import json,re,sys,zipfile,glob,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import lootlib
W=sys.argv[1]; R=sys.argv[2]
rec=json.load(open(W+'/rec.json'))
s=open(R+'/build/src/data.js',encoding='utf-8').read();D,_=json.JSONDecoder().raw_decode(s,re.search(r'\bD\s*=\s*\[',s).end()-1)
idx={}
for j in sorted(glob.glob(W+'/pack/mods/*.jar')):
    try: z=zipfile.ZipFile(j)
    except: continue
    for n in z.namelist():
        m=re.match(r'data/([^/]+)/loot_tables/(.+)\.json$',n)
        if m: idx[m.group(1)+':'+m.group(2)]=(j,n)
for f in glob.glob(W+'/pack/src/overrides/kubejs/data/*/loot_tables/**/*.json',recursive=True):
    m=re.search(r'data/([^/]+)/loot_tables/(.+)\.json$',f); idx[m.group(1)+':'+m.group(2)]=(None,f)
def load(t):
    j,n=idx[t]; return json.loads((zipfile.ZipFile(j).read(n) if j else open(n,'rb').read()).decode('utf-8','ignore'))
def chance(o,item):
    r=lootlib.chances(o,lambda t:load(t) if t in idx else None,rec.get('tags'))
    return r[item]['p'] if item in r else 0
out=[]
for d in D:
    best={}
    for t in rec['loot'].get(d['id'],[]):
        if t not in idx or '/entities/' in t or t.split(':')[1].startswith('entities/'): continue
        try: c=chance(load(t),d['id'])
        except Exception as e: print('table not read:',t,repr(e)[:120]); continue
        if c>0: best[t]=round(c*100,2)
    if not best: continue
    txt=' / '.join(d['src'])
    nums=[float(x) for x in re.findall(r'([0-9.]+)% per chest',txt)]
    mx=max(best.values())
    flag='' if not nums or abs(max(nums)-mx)<=max(0.6,0.15*mx) else '  <<< DIFF'
    out.append(f"{d['id']} | pack max {mx}% ({max(best,key=best.get)}) n={len(best)} | wiki {nums[:4]}{flag}")
print('\n'.join(out))
