import zipfile,glob,json,sys,os,re
W=sys.argv[1]; ids=sys.argv[2].split(',')
G=json.load(open(W+'/gated_items.json'))
want={}
for e in ids:
  ns,i=e.split(':'); want[f'data/{ns}/loot_tables/entities/{i}.json']=e
res={}
def items(o,acc):
  if isinstance(o,dict):
    if o.get('type') in('minecraft:item','item') and 'name' in o: acc.append(o['name'])
    for v in o.values(): items(v,acc)
  elif isinstance(o,list):
    for v in o: items(v,acc)
paths=glob.glob(W+'/pack/mods/*.jar')
ov=W+'/pack/src/overrides/kubejs/'
for j in paths:
  try: z=zipfile.ZipFile(j)
  except: continue
  for n in z.namelist():
    if n in want:
      a=[];items(json.loads(z.read(n)),a);res[want[n]]=a
for p,e in want.items():
  f=ov+p
  if os.path.exists(f):
    a=[];items(json.load(open(f)),a);res[e]=a
for e in ids:
  a=sorted(set(res.get(e,[])));print(e,'|',[(x,G.get(x)) for x in a])
