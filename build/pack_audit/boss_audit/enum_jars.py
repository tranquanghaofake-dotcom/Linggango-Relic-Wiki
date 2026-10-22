import zipfile,glob,json,re,sys,os
W=sys.argv[1]
tags={};boss={};lang={}
for j in glob.glob(W+'/pack/mods/*.jar'):
  try: z=zipfile.ZipFile(j)
  except: continue
  jn=os.path.basename(j)
  for n in z.namelist():
    if re.search(r'tags/entity_types?/bosses?\.json$',n) or re.search(r'tags/entity_types?/.*boss.*\.json$',n):
      try: v=json.loads(z.read(n)).get('values',[])
      except: continue
      for x in v:
        x=x if isinstance(x,str) else x.get('id')
        tags.setdefault(x,[]).append(n.split('/')[1]+':'+n.split('/')[-1])
    elif n.endswith('.class'):
      d=z.read(n)
      if b'ServerBossEvent' in d or b'class_3213' in d:
        boss.setdefault(jn,[]).append(n)
    elif re.match(r'assets/[^/]+/lang/en_us\.json$',n):
      try: l=json.loads(z.read(n).decode('utf-8','ignore'))
      except: continue
      for k,v in l.items():
        if k.startswith('entity.') and k.count('.')==2: lang[k[7:].replace('.',':',1)]=(v,jn)
json.dump({'tags':tags,'bossclasses':boss,'lang':lang},open(W+'/enum.json','w'))
print(len(tags),len(boss))
for k in sorted(tags): print('T',k,lang.get(k,('?',))[0])
for jn,c in boss.items(): print('C',jn,[os.path.basename(x)[:-6] for x in c][:40])
