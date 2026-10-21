import urllib.request,re,json,sys,collections
base='https://www.minecraft-guides.com/wiki/'
seen=set();q=collections.deque([(base,0)]);out={}
def get(u):
  r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
  return urllib.request.urlopen(r,timeout=30).read().decode('utf8','ignore')
while q and len(seen)<400:
  u,d=q.popleft()
  if u in seen: continue
  seen.add(u)
  try: h=get(u)
  except Exception as e: continue
  imgs=sorted(set(re.findall(r'https://www\.minecraft-guides\.com/wp-content/uploads/\d{4}/\d\d/[A-Za-z0-9_\-]+\.(?:png|jpg|jpeg|webp)',h)))
  imgs=[i for i in imgs if not re.search(r'-\d+x\d+\.',i)]
  t=re.search(r'<title>(.*?)</title>',h,re.S)
  out[u]={'title':t.group(1).strip() if t else '','imgs':imgs}
  if d<3:
    for l in set(re.findall(r'href="(https://www\.minecraft-guides\.com/wiki/[a-z0-9\-/]+)"',h)):
      if l not in seen: q.append((l,d+1))
json.dump(out,open(sys.argv[1],'w'),indent=0)
print(len(out))
