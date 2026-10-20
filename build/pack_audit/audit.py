import json,re,glob,sys,collections
W=sys.argv[1]; R=sys.argv[2]
s=open(R+'/build/src/data.js',encoding='utf-8').read(); D,_=json.JSONDecoder().raw_decode(s,8)
lang=json.load(open(W+'/lang.json'))
for f in glob.glob(W+'/pack/src/overrides/kubejs/assets/*/lang/en_us.json'):
    for k,v in json.load(open(f)).items():
        m=re.match(r'item\.([a-z0-9_]+)\.([a-z0-9_/]+)$',k)
        if m: lang[m.group(1)+':'+m.group(2)]=v
for m in re.finditer(r"renameItem\('([^']+)',\s*'([^']+)'\)",open(W+'/pack/src/overrides/kubejs/client_scripts/lang.js').read()): lang[m.group(1)]=m.group(2)
rec=json.load(open(W+'/rec.json')); gates=json.load(open(W+'/gates.json'))
clean=lambda t:re.sub(r'§.','',t).strip()
out=collections.defaultdict(list)
for d in D:
    i=d['id']; L=lang.get(i)
    if L is None: out['no_lang'].append(i)
    elif clean(L)!=d['n'] and clean(L).lower()!=d['n'].lower(): out['name'].append(f"{i}: wiki '{d['n']}' vs game '{clean(L)}'")
    rs=rec['recipes'].get(i,[]); lt=rec['loot'].get(i,[])
    if d['g']=='Craft' and not rs: out['craft_no_recipe'].append(f"{i} | {d['src'][0][:90]}")
    if d.get('gr') and rs:
        wing={c[0] for c in d['gr']['c'] if c and c[0]}
        best=max(rs,key=lambda r:len(wing & set(r['ing'])))
        miss=wing-set(best['ing'])
        if miss: out['recipe_diff'].append(f"{i}: wiki has {sorted(miss)} not in {best['id']} {best['ing']}")
    if d['g']=='Loot' and not lt and not rs: out['loot_unseen'].append(f"{i} | {d['src'][0][:90]}")
    if rs and d['g']=='Loot': out['loot_but_recipe'].append(f"{i} | {[r['id']+':'+r['t'] for r in rs][:2]}")
    gt=[t.split('/')[-1] for t,v in gates.items() if t.startswith('linggango_tweaks:gated/') and i in v]
    if gt: out['gated'].append(f"{i} {gt} wiki gk={d.get('gk')}")
for k,v in out.items():
    print('##',k,len(v))
    for x in v[:int(sys.argv[3]) if len(sys.argv)>3 else 40]: print('  ',x)
