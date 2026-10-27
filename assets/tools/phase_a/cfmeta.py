import json,sys,os,urllib.request,time,concurrent.futures as cf
P=sys.argv[1]; m=json.load(open(P+'/src/manifest.json'))
def get(u,t=60):
    err=None
    for i in range(5):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'lgw-asset-audit'}),timeout=t).read()
        except Exception as e: err=e; time.sleep(2**i)
    raise err
def job(f):
    pid=f['projectID']; out=f'{P}/cf/{pid}.json'
    if os.path.exists(out): return pid,'have'
    try:
        d=json.loads(get(f'https://api.cfwidget.com/{pid}'))
        fn=[x for x in d.get('files',[]) if x['id']==f['fileID']]
        d.pop('description',None); d['files']=fn; d.pop('versions',None)
        json.dump(d,open(out,'w')); return pid,'ok'
    except Exception as e: return pid,'ERR '+str(e)[:80]
with cf.ThreadPoolExecutor(6) as ex:
    bad=[r for r in ex.map(job,m['files']) if r[1] not in('ok','have')]
print('bad',bad)
