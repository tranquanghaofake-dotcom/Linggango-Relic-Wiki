import json,re,sys,zipfile,glob,os
W=sys.argv[1]
rec=json.load(open(W+'/rec.json'))
s=open('/home/user/Linggango-Relic-Wiki/build/src/data.js',encoding='utf-8').read();D,_=json.JSONDecoder().raw_decode(s,8)
want={d['id'] for d in D}
# index loot table files: table id -> loader
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
    j,n=idx[t]
    return json.loads((zipfile.ZipFile(j).read(n) if j else open(n,'rb').read()).decode('utf-8','ignore'))
def chances(o,item):
    res=[]
    for p in o.get('pools',[]):
        pc=1.0
        for c in p.get('conditions',[]):
            if 'random_chance' in c.get('condition',''): pc*=c.get('chance',1)
        ents=p.get('entries',[]); tw=sum(e.get('weight',1) for e in ents if e.get('type','').endswith('item') or e.get('type','').endswith('empty'))
        rolls=p.get('rolls',1); rolls=rolls if isinstance(rolls,(int,float)) else rolls.get('max',1) if isinstance(rolls,dict) else 1
        for e in ents:
            if e.get('name')==item:
                ec=1.0
                for c in e.get('conditions',[]):
                    if 'random_chance' in c.get('condition',''): ec*=c.get('chance',1)
                w=e.get('weight',1)/tw if tw and len(ents)>1 else 1
                res.append(round(pc*ec*(1-(1-w)**rolls)*100,2))
    return res
for d in D:
    for t in rec['loot'].get(d['id'],[]):
        if '/entities/' in t or t.split(':')[1].startswith('entities/'):
            try: ch=chances(load(t),d['id'])
            except Exception as e: continue
            mob=t.split('/')[-1]
            w=' / '.join(d['src'])
            print(d['id'],'|',t,ch,'|| wiki:',re.findall(r'Dropped by [^.;]*',w)[:3])
