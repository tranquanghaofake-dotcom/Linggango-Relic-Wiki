import json,sys,os,urllib.request,concurrent.futures as cf,time
P=sys.argv[1]; m=json.load(open(P+'/src/manifest.json')); os.makedirs(P+'/mods',exist_ok=True)
meta={}
if os.path.exists(P+'/meta.json'): meta=json.load(open(P+'/meta.json'))
def get(u,t=60):
    for i in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=t).read()
        except Exception as e: err=e; time.sleep(2**i)
    raise err
def job(f):
    pid,fid=f['projectID'],f['fileID']; k=str(pid)
    try:
        if k not in meta or 'name' not in meta[k]:
            d=json.loads(get(f'https://api.cfwidget.com/{pid}'))
            fn=[x for x in d.get('files',[]) if x['id']==fid]
            name=fn[0]['name'] if fn else None
            meta[k]={'title':d.get('title'),'name':name,'fid':fid,'type':d.get('type'),'urls':d.get('urls',{}).get('curseforge')}
        name=meta[k]['name']
        if not name: return k,'NOFILE'
        out=P+'/mods/'+name
        if os.path.exists(out) and os.path.getsize(out)>0: return k,'have'
        data=get(f'https://edge.forgecdn.net/files/{fid//1000}/{fid%1000}/'+urllib.parse.quote(name),300)
        open(out,'wb').write(data); return k,'ok'
    except Exception as e: return k,'ERR '+str(e)[:80]
import urllib.parse
with cf.ThreadPoolExecutor(8) as ex:
    for k,r in ex.map(job,m['files']):
        if r not in('ok','have'): print(k,meta.get(k,{}).get('title'),r,flush=True)
json.dump(meta,open(P+'/meta.json','w'),indent=0)
print('done')
