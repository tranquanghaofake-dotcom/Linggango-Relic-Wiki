import json,zipfile,glob,re,sys
W=sys.argv[1]
ents={};geo={};loot={};jar={}
for j in glob.glob(W+'/pack/mods/*.jar'):
  try:z=zipfile.ZipFile(j)
  except:continue
  for n in z.namelist():
    m=re.match(r'assets/(\w+)/lang/en_us.json$',n)
    if m:
      try:L=json.loads(z.read(n).decode('utf8','ignore'))
      except Exception:
        continue
      for k,v in L.items():
        if k.startswith('entity.') and isinstance(v,str):ents[k[7:]]=v;jar[k[7:].split('.')[0]]=j.split('/')[-1]
    m=re.match(r'data/(\w+)/loot_tables/entities/(.+)\.json$',n)
    if m:loot[m[1]+':'+m[2]]=(j,n)
    if n.endswith('.geo.json') and '/entity/' in n or (n.endswith('.geo.json') and 'geo/' in n):geo.setdefault(n.split('/')[1],[]).append(n)
json.dump({'ents':ents,'loot':{k:list(v) for k,v in loot.items()},'jar':jar},open(W+'/sb_idx.json','w'))
print(len(ents),len(loot))
