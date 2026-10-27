import json,sys,urllib.request,urllib.parse
P=sys.argv[1]; d=json.load(open(P+'/scan.json'))
H={'User-Agent':'lgw-asset-audit (tranquanghaofake-dotcom/Linggango-Relic-Wiki)','Content-Type':'application/json'}
def req(u,body=None):
    return json.loads(urllib.request.urlopen(urllib.request.Request(u,data=json.dumps(body).encode() if body else None,headers=H),timeout=120).read())
hs=[r['sha1'] for r in d.values()]
vf=req('https://api.modrinth.com/v2/version_files',{'hashes':hs,'algorithm':'sha1'})
pids=sorted({v['project_id'] for v in vf.values()})
projs={}
for i in range(0,len(pids),100):
    for p in req('https://api.modrinth.com/v2/projects?ids='+urllib.parse.quote(json.dumps(pids[i:i+100]))): projs[p['id']]=p
for r in d.values():
    v=vf.get(r['sha1'])
    if v:
        p=projs[v['project_id']]
        r['mr']={'slug':p['slug'],'license':p['license']['id'],'license_url':p['license'].get('url'),'source':p.get('source_url'),'wiki':p.get('wiki_url')}
json.dump(d,open(P+'/scan.json','w'),indent=0)
print('matched',sum(1 for r in d.values() if 'mr' in r),'of',len(d))
