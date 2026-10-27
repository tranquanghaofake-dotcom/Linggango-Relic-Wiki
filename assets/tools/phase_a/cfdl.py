import json,sys,os,urllib.request,urllib.parse,time,concurrent.futures as cf
P=sys.argv[1]; m=json.load(open(P+'/src/manifest.json'))
def get(u,t=300):
    err=None
    for i in range(5):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=t).read()
        except Exception as e: err=e; time.sleep(2**i)
    raise err
def job(f):
    pid,fid=f['projectID'],f['fileID']; d=json.load(open(f'{P}/cf/{pid}.json')); name=d['files'][0]['name']
    od=f'{P}/files/{pid}'; os.makedirs(od,exist_ok=True); out=f'{od}/{name}'
    if os.path.exists(out) and os.path.getsize(out)>0: return pid,'have'
    try:
        b=get(f'https://edge.forgecdn.net/files/{fid//1000}/{fid%1000}/'+urllib.parse.quote(name)); open(out,'wb').write(b); return pid,'ok'
    except Exception as e: return pid,'ERR '+str(e)[:80]
with cf.ThreadPoolExecutor(8) as ex:
    bad=[r for r in ex.map(job,m['files']) if r[1] not in('ok','have')]
print('bad',bad)
