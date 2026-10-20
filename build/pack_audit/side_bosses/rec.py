import json,zipfile,glob,sys,re
W=sys.argv[1];T=sys.argv[2].split(',')
for j in glob.glob(W+'/pack/mods/*.jar'):
  try:z=zipfile.ZipFile(j)
  except:continue
  for n in z.namelist():
    if '/recipes/' in n and n.endswith('.json'):
      try:r=json.loads(z.read(n))
      except:continue
      res=r.get('result');rid=res if isinstance(res,str) else (res or {}).get('item') if isinstance(res,dict) else None
      if rid in T:
        s=json.dumps({k:r[k] for k in r if k in('type','pattern','key','ingredients')})
        print(rid,'|',n.split('/')[-1],'|',s[:500])
