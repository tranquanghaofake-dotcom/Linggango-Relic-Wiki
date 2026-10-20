import json,zipfile,glob,sys,re
W=sys.argv[1];M=json.load(open(W+'/tools2/map.json'))
F={}
for j in glob.glob(W+'/pack/mods/*.jar'):
  try:z=zipfile.ZipFile(j)
  except:continue
  for n in z.namelist():
    if n.startswith('assets/') and (n.endswith('.geo.json') or (n.endswith('.png') and 'entit' in n) or n.endswith('.json') and '/geo' in n):F.setdefault(n.split('/')[1],[]).append(n)
for b,ids in M.items():
  e=ids[0];ns,p=e.split(':');key=p.replace('_boss','').replace('the_','')
  g=[n for n in F.get(ns,[]) if 'geo' in n and key.split('_')[-1] in n.split('/')[-1]]
  t=[n for n in F.get(ns,[]) if n.endswith('.png') and key.split('_')[-1] in n.split('/')[-1]]
  print(b,'|',g[:4],'|',t[:5])
