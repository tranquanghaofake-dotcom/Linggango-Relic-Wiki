# for each unobtainable candidate, look for other sources
import json,glob,zipfile,sys,re,os
W=sys.argv[1]; u=json.load(open(W+'/equip_unobtainable.json'))
ids={x['id'] for x in u}
O=W+'/pack/src/overrides'
hits={i:set() for i in ids}
def scan(text,label):
    for i in ids:
        if i in text: hits[i].add(label)
quest=''.join(open(f,errors='ignore').read() for f in glob.glob(O+'/config/ftbquests/**/*.snbt',recursive=True))
qrew=re.findall(r'rewards:\s*\[(.*?)\n\t\]',quest,re.S)
scan(' '.join(qrew),'ftbquests reward'); 
for i in ids:
    if i in quest and 'ftbquests reward' not in hits[i]: hits[i].add('ftbquests (task/other)')
cfg=''.join(open(f,errors='ignore').read() for f in glob.glob(O+'/config/**/*',recursive=True)+glob.glob(O+'/defaultconfigs/**/*',recursive=True) if os.path.isfile(f) and 'ftbquests' not in f and 'linggango' not in f)
scan(cfg,'config mention')
ks=''.join(open(f,errors='ignore').read() for f in glob.glob(O+'/kubejs/server_scripts/**/*.js',recursive=True) if 'dump' not in f and 'progression_lock' not in f and not f.endswith('tags.js') and 'boss_tag' not in f)
scan(ks,'kubejs script mention')
dp=''
for f in glob.glob(O+'/kubejs/data/**/*.json',recursive=True):
    if '/tags/' in f or 'attributesetter' in f: continue
    dp+=open(f,errors='ignore').read()
scan(dp,'pack datapack (loot/modifier) mention')
for j in glob.glob(W+'/pack/mods/*.jar'):
    try: z=zipfile.ZipFile(j)
    except: continue
    for n in z.namelist():
        if n.startswith('data/') and n.endswith('.json') and '/tags/' not in n and '/recipes/' not in n and '/advancements/' not in n:
            t=z.read(n).decode('utf8','ignore')
            for i in ids:
                if i in t: hits[i].add('jar data: '+n.split('/')[1]+'/'+'/'.join(n.split('/')[2:4]))
        elif n.endswith('.class'):
            b=z.read(n)
            for i in ids:
                ns,p=i.split(':')
                if p.encode() in b and ns.encode()[:4] in j.lower().encode()+b: pass
for x in u:
    h=sorted(hits[x['id']]); x['other_sources']=h[:6]
    if x['why']==['no recipe and no loot']:
        x['verdict']='possible source outside recipes/loot tables' if h else 'no source found in data (likely code-only drop or unobtainable)'
    else: x['verdict']='flagged'
json.dump(u,open(W+'/equip_unobtainable.json','w'),indent=1)
import collections; print(collections.Counter(x['verdict'] for x in u)); print(collections.Counter(s.split(':')[0] for x in u for s in x['other_sources']))
