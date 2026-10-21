import json,re,glob,sys,collections,os
W=sys.argv[1]; R='/home/user/Linggango-Relic-Wiki/build/src/gear_data.js'
s=open(R).read(); d=json.JSONDecoder()
GE,_=d.raw_decode(s,s.index('[',s.index('const GE='))); GS,_=d.raw_decode(s,s.index('[',s.index('GS=')))
G={e['id']:e for e in GE}
rec=json.load(open(W+'/rec.json')); lang=json.load(open(W+'/lang.json')); cls=json.load(open(W+'/eqa/cls.json'))
tags=rec['tags']; K=W+'/pack/src/overrides/kubejs'
def res(t,seen=None):
    seen=seen or set(); out=set()
    if t in seen: return out
    seen.add(t)
    for x in tags.get(t,[]):
        if x.startswith('#'): out|=res(x[1:],seen)
        else: out.add(x)
    return out
# ---- removals / hides
txt=''.join(open(f,errors='ignore').read() for f in glob.glob(K+'/server_scripts/**/*.js',recursive=True))
rid=set(re.findall(r"id\s*:\s*['\"`]([a-z0-9_.-]+:[a-z0-9_/.-]+)['\"`]",txt))
rout=set(re.findall(r"output\s*:\s*['\"]([a-z0-9_.-]+:[a-z0-9_/.-]+)['\"]",txt))|set(rec['removed'])
rid|=set(json.load(open(W+'/removed_ids.json')))
for f in glob.glob(K+'/server_scripts/**/*.js',recursive=True):
    t=open(f,errors='ignore').read()
    for arr,v,kk in re.findall(r"(\w+)\.forEach\(\s*\(?(\w+)\)?\s*=>\s*\w+\.remove\(\{\s*(output|id)\s*:\s*\w+",t):
        mm=re.search(r"(?:const|let|var)\s+"+arr+r"\s*=\s*\[(.*?)\]",t,re.S)
        if mm:
            xs=set(re.findall(r"['\"]([a-z0-9_.-]+:[a-z0-9_/.-]+)['\"]",mm.group(1)))
            (rout if kk=='output' else rid).update(xs)
print('removed outputs',len(rout),'ids',len(rid))
ctxt=''.join(open(f,errors='ignore').read() for f in glob.glob(K+'/client_scripts/jei_hide*.js'))
hidden=set(re.findall(r"['\"]([a-z0-9_.-]+:[a-z0-9_/.-]+)['\"]",ctxt))
hide_rx=[r for r in re.findall(r"/([^/\n]+)/",ctxt) if ':' in r or '_' in r]
NS=set(json.load(open(W+'/ns2jar.json')))|{'minecraft','forge','c','kubejs'}
def valid(r): return all(x.lstrip('#').split(':')[0] in NS for x in r['ing'] if ':' in x and not x.startswith('#'))
def recipes(i): return [r for r in rec['recipes'].get(i,[]) if r.get('id') not in rid and i not in rout and valid(r) and i not in r['ing']]
def obtain(i):
    rs=recipes(i); lt=rec['loot'].get(i,[])
    o=[]
    if rs: o.append('recipe:'+rs[0].get('t',''))
    if lt: o.append('loot:'+lt[0]+('(+%d)'%(len(lt)-1) if len(lt)>1 else ''))
    return o
# ---- gates
TIER={'iron':2,'gold':3,'emerald':4,'diamond':5,'netherite':6,'elvenite':7,'voiderite':8,'cataclysm':9,'blood':10,'sun':11}
GT={'iron':2,'golden':3,'emerald':4,'diamond':5,'netherite':6,'elvenite':7,'voiderite':8,'bloody':10,'helionite':11}
gate=collections.defaultdict(dict)
for f in glob.glob(K+'/data/linggango_tweaks/tags/items/gated/*.json'):
    t=os.path.basename(f)[:-5]
    for v in json.load(open(f))['values']:
        v=v['id'] if isinstance(v,dict) else v
        ids=res(v[1:]) if v.startswith('#') else {v}
        for i in ids: gate[i]['gated/'+t]=TIER[t]
for tg,ids in list(json.load(open(W+'/gates.json')).items())+list(tags.items()):
    m=re.match(r'forge:(\w+?)_(tools|armor)$',tg)
    if m and m.group(1) in GT:
        for i in ids:
            for x in (res(i[1:]) if i.startswith('#') else {i}): gate[x][tg]=GT[m.group(1)]
def gact(i): return max(gate[i].values()) if i in gate else 0
# ---- curios
curio=set()
for t in tags:
    if t.startswith('curios:'): curio|=res(t)
# ---- candidates
WT=re.compile(r'^(minecraft:(swords|axes|trimmable_armor|head_armor|chest_armor|leg_armor|foot_armor)|(forge|c):(swords|axes|bows|crossbows|tridents|spears|armors?(/.*)?|(head|chest|leg|foot)_armor|helmets|chestplates|leggings|boots|weapons|melee_weapons|ranged_weapons|tools/(swords?|axes?|bows?|crossbows?|tridents?|spears?|daggers?|maces?|hammers?|katanas?|scythes?|halberds?|glaives?|rapiers?|claws?|longswords?|greatswords?|lances?|guns?|staffs?|wands?|melee_weapons?|ranged_weapons?))|.*:(swords|ranged_weapons|big_weapons|tridents|melee_weapons|weapons))$')
TOOL=re.compile(r'(pickaxe|shovel|_hoe$|paxel|excavator|_drill$|multitool|aiot|mattock|fishing_rod|shears|_knife$)')
cand={}
for t in tags:
    if WT.match(t):
        for i in res(t): cand.setdefault(i,set()).add('tag:'+t)
ARM=r'_(helmet|chestplate|leggings|boots|hood|robe|robes|cap|tunic|pants|crown|mask|greaves|sabatons|helm|cuirass)$'
WEP=r'(sword|_axe$|battleaxe|waraxe|greataxe|_bow$|longbow|crossbow|trident|spear|dagger|katana|scythe|halberd|glaive|rapier|cutlass|saber|sabre|claymore|longsword|greatsword|mace|warhammer|_hammer$|lance|_staff$|_wand$|_blade$|_sickle$|_club$|_whip$|_gun$|rifle|pistol|cannon|blaster|shotgun|_tome$|scepter)'
def camel(p): return p.replace('_','')
for i in lang:
    ns,p=i.split(':',1)
    if '/' in p: continue
    for c in (camel(p),camel(p)+'item',camel(p)+'armor',camel(p)+'armoritem'):
        for fq,k,j in cls.get(c,[]):
            if k not in('tool','shield') : cand.setdefault(i,set()).add('class:'+fq.split('/')[-1]+'/'+k)
    if re.search(ARM,p) or re.search(WEP,p): cand.setdefault(i,set()).add('name')
for f in glob.glob(K+'/data/linggango/attributesetter/item/*.json'):
    for k,v in json.load(open(f)).items():
        if k.startswith('#') or ':' not in k: continue
        at={x['attribute'].split(':')[-1] for x in v}
        cand.setdefault(k,set()).add('attributesetter'+(':armor' if at & {'generic.armor','generic.armor_toughness'} else ''))
def kindof(i,why):
    p=i.split(':')[1]; w=' '.join(why)
    if TOOL.search(p): return None
    if '/armor' in w or 'armor' in w.split('tag:')[-1] or 'attributesetter:armor' in w or re.search(ARM,p): return 'armor'
    if 'ranged' in w or re.search(r'(bow|crossbow|gun|rifle|pistol|cannon|blaster|shotgun|launcher)',p): return 'ranged'
    if re.search(r'(staff|wand|scepter|tome|grimoire|rod)$',p): return 'magic'
    if re.search(r'shield',p): return None
    return 'melee'
def slot(i):
    p=i.split(':')[1]
    for t,rx in (('HELMET','helmet|hood|cap|crown|mask|hat|helm'),('CHESTPLATE','chestplate|robe|tunic|chest|cuirass'),('LEGGINGS','leggings|pants|greaves'),('BOOTS','boots|sabatons|shoes')):
        if re.search(rx,p): return t
    return None
def recipe_act(i,d=0,memo={}):
    if i.startswith('#'):
        vs=sorted(res(i[1:]))[:12]
        return min([recipe_act(x,d+1) for x in vs] or [0])
    if i in memo: return memo[i]
    if d>5: return gact(i)
    memo[i]=gact(i)
    rs=recipes(i)
    ra=min([max([recipe_act(x,d+1) for x in r['ing'] if ':' in x and x!=r.get('t')] or [0]) for r in rs[:3]]) if rs else 0
    memo[i]=max(gact(i),ra); return memo[i]
miss=[]
for i,why in sorted(cand.items()):
    if i in G or i in curio: continue
    if i.split(':')[0] not in NS: continue
    k=kindof(i,why)
    if not k: continue
    # name-only hits need a second signal or obtain
    o=obtain(i)
    if not o: continue
    if why=={'name'} and not o: continue
    rs=recipes(i)
    ra=min([max([recipe_act(x) for x in r['ing'] if ':' in x and x!=r.get('t')] or [0]) for r in rs[:3]]) if rs else 0
    miss.append({'id':i,'name':lang.get(i,i),'kind':k,'slot':slot(i) if k=='armor' else None,'mod':i.split(':')[0],'obtain':o,'act_guess':max(gact(i),ra),'evidence':sorted(why)[:4],'hidden_in_jei':i in hidden,'confidence':''})
json.dump(miss,open(W+'/equip_missing.json','w'),indent=1)
# ---- unobtainable
un=[]
for e in GE:
    i=e['id']; rs=recipes(i); lt=rec['loot'].get(i,[]); why=[]
    allr=rec['recipes'].get(i,[])
    if not rs and not lt:
        why.append('no recipe and no loot' + (' (all %d recipes removed/invalid)'%len(allr) if allr else ''))
    if i in rout: why.append('kubejs remove({output}) on this item')
    rem=[r['id'] for r in allr if r.get('id') in rid]
    if rem and not rs: why.append('recipe removed by kubejs: '+', '.join(rem[:3]))
    if i in hidden: why.append('hidden in JEI (kubejs client hide)')
    if re.search(r'creative|debug|admin|_test$|dev_',i): why.append('creative/debug id')
    if i.split(':')[0] not in NS: why.append('mod not in pack')
    if why: un.append({'id':i,'name':e['n'],'a':e['a'],'why':why,'wiki_rc':len(e.get('rc',[])),'wiki_lt':len(e.get('lt',[]))})
json.dump(un,open(W+'/equip_unobtainable.json','w'),indent=1)
# ---- act check
ac=[]
for e in GE:
    i=e['id']; g=gact(i); a=e['a']
    rs=recipes(i); ra=None
    if rs:
        ra=min([max([recipe_act(x) for x in r['ing'] if ':' in x and x!=r.get('t')] or [0]) for r in rs[:3]])
    issues=[]
    if g and int(a)<g: issues.append('wiki act %s < gate %s (%s)'%(a,g,','.join(gate[i])))
    if ra is not None and ra>int(a) and ra>g: issues.append('recipe ingredients gate to Act %s'%ra)
    if e.get('ga',0)!=g and g: issues.append('wiki ga=%s but current gate tags say %s'%(e.get('ga'),g))
    if issues: ac.append({'id':i,'name':e['n'],'wiki_a':a,'wiki_ga':e.get('ga'),'gate':g,'gate_tags':sorted(gate.get(i,{})),'recipe_act':ra,'issues':issues})
json.dump(ac,open(W+'/equip_act.json','w'),indent=1)
print('miss',len(miss),collections.Counter(m['confidence'] for m in miss),collections.Counter(m['kind'] for m in miss))
print('unob',len(un)); print('act',len(ac))
