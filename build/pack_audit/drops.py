import json,re,sys,zipfile,glob,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import lootlib  # vanilla 1.20.1 loot rules; the chance of at least one per kill, luck 0
W=sys.argv[1]
rec=json.load(open(W+'/rec.json'))
s=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','src','data.js'),encoding='utf-8').read();D,_=json.JSONDecoder().raw_decode(s,re.search(r'\bD\s*=\s*\[',s).end()-1)
want={d['id'] for d in D}
# index loot table files: table id -> loader
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
    j,n=idx[t]
    return json.loads((zipfile.ZipFile(j).read(n) if j else open(n,'rb').read()).decode('utf-8','ignore'))
def chances(o,item):
    r=lootlib.chances(o,lambda t:load(t) if t in idx else None,rec.get('tags'))
    return [round(r[item]['p']*100,2)]+r[item]['cond'] if item in r else []
for d in D:
    for t in rec['loot'].get(d['id'],[]):
        if '/entities/' in t or t.split(':')[1].startswith('entities/'):
            try: ch=chances(load(t),d['id'])
            except Exception as e: print('table not read:',t,repr(e)[:120]); continue
            mob=t.split('/')[-1]
            w=' / '.join(d['src'])
            print(d['id'],'|',t,ch,'|| wiki:',re.findall(r'Dropped by [^.;]*',w)[:3])
