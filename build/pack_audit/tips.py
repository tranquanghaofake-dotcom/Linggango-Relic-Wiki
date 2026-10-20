import json,re,sys,zipfile,glob
W=sys.argv[1]
s=open('/home/user/Linggango-Relic-Wiki/build/src/data.js',encoding='utf-8').read();D,_=json.JSONDecoder().raw_decode(s,8)
ns2jar=json.load(open(W+'/ns2jar.json'))
V=[d for d in D if re.search(r'\+[A-Z][a-z]|\+[a-z]+ (?!slot)|\((moderate|high|very high)\)|[Ss]light|\bSmall\b',d['fx']) and not re.search(r'\d',d['fx'])]
cache={}
def langof(j):
    if j not in cache:
        z=zipfile.ZipFile(W+'/pack/mods/'+j);L={}
        for n in z.namelist():
            if n.endswith('lang/en_us.json'):
                try: L.update(json.loads(z.read(n).decode('utf-8','ignore')))
                except Exception: pass
        cache[j]=L
    return cache[j]
for d in V:
    ns,p=d['id'].split(':')
    js=ns2jar.get(ns,[]); hits=[]
    for j in js:
        for k,v in langof(j).items():
            if p in k and k!=f'item.{ns}.{p}' and isinstance(v,str): hits.append(f'{k} = {re.sub("§.","",v)[:200]}')
    print('##',d['id'],'|',d['fx']);[print('   ',h) for h in hits[:8]]
