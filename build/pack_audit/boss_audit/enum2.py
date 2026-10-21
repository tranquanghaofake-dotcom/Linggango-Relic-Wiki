import zipfile,glob,os,sys,re
W=sys.argv[1]
keys=[b'LMBossInfoServer',b'CMBossInfoServer',b'ModServerBossInfo',b'MMBossInfoServer',b'ModBossInfoServer',b'ACBossEvent',b'TravelopticsBossInfo',b'ExtendedServerBossEvent',b'ServerBossEvent']
for j in glob.glob(W+'/pack/mods/*.jar'):
  try: z=zipfile.ZipFile(j)
  except: continue
  out=[]
  for n in z.namelist():
    if n.endswith('.class') and 'Entity' in n or n.endswith('.class') and '/entity/' in n:
      d=z.read(n)
      if any(k in d for k in keys) and not any(os.path.basename(n)[:-6].encode()==k for k in keys):
        out.append(os.path.basename(n)[:-6])
  if out: print(os.path.basename(j)[:30],sorted(set(out)))
