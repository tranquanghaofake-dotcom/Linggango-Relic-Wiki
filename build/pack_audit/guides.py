import zipfile,glob,sys,re,json,os
W=sys.argv[1]; R='/home/user/Linggango-Relic-Wiki/build/src/'
def ld(f):
  s=open(R+f).read(); return json.JSONDecoder().raw_decode(s[s.index('['):])[0]
ids={}
for f in ('data.js','gear_data.js'):
  for e in ld(f):
    if isinstance(e,dict) and e.get('id'): ids[e['id']]=e.get('n','')
def strip(t):
  t=re.sub(r'\$\((br2?|p)\)',' ',t)
  t=re.sub(r'\$\(l:[^)]*\)|\$\([^)]*\)','',t); t=re.sub(r'\s+',' ',t).strip(); return t
def short(t):
  ss=re.split(r'(?<=[.!?])\s+',t); o=''
  for s in ss[:3]:
    if len(o)+len(s)>295: break
    o+=(' ' if o else '')+s
  return o or t[:295]
srcs=[]  # (jarname, files dict path->bytes getter)
for j in sorted(glob.glob(W+'/pack/mods/*.jar')):
  try: z=zipfile.ZipFile(j)
  except: continue
  srcs.append((os.path.basename(j),z,[n for n in z.namelist() if '/patchouli_books/' in n]))
ov=W+'/pack/src/overrides/kubejs'
class D:
  def __init__(s,root): s.root=root
  def read(s,n): return open(os.path.join(s.root,n),'rb').read()
ofs=[os.path.relpath(os.path.join(d,f),ov) for d,_,fs in os.walk(ov) for f in fs if '/patchouli_books/' in os.path.join(d,f)]
srcs.append(('overrides:kubejs',D(ov),ofs))
titles={};entries=[]
lang={}
for jar,z,ns in srcs:
  for n in ns:
    if n.endswith('lang/en_us.json'): pass
  for n in ns:
    m=re.match(r'(assets|data)/([^/]+)/patchouli_books/([^/]+)/(.*)',n)
    if not m: continue
    bk=m.group(2)+':'+m.group(3); rest=m.group(4)
    try: d=json.loads(z.read(n).decode('utf-8','ignore'))
    except: continue
    if rest=='book.json': titles[bk]=d.get('name',m.group(3))
    elif rest.startswith('en_us/entries/') and isinstance(d,dict): entries.append((jar,bk,n,d))
# lang files for translation keys
for jar,z,ns in srcs[:-1]:
  for n in z.namelist():
    if re.match(r'assets/[^/]+/lang/en_us\.json$',n):
      try: lang.update(json.loads(z.read(n).decode('utf-8','ignore')))
      except: pass
L=lambda s: lang.get(s,s) if isinstance(s,str) else ''
def bkname(bk):
  t=L(titles.get(bk,bk.split(':')[1])); return bk.split(':')[0]+': '+t
LORE=re.compile(r'lore|story|legend|histor|journal|diary',re.I)
out={};best={}
for jar,bk,path,d in entries:
  title=strip(L(d.get('name','')))
  pages=d.get('pages',[]) or []
  text=' '.join(strip(L(p.get('text',''))) for p in pages if isinstance(p,dict) and p.get('text'))
  if not text: continue
  items=set()
  ic=d.get('icon')
  if isinstance(ic,str): items.add(ic.split('{')[0])
  for k in (d.get('extra_recipe_mappings') or {}): items.add(k)
  img=''
  for p in pages:
    if not isinstance(p,dict): continue
    for f in ('item','recipe','recipe2'):
      v=p.get(f)
      if isinstance(v,str):
        for x in v.split(','): items.add(x.split('{')[0].strip())
    if not img and p.get('images'): img=p['images'][0]
    if not img and p.get('image'): img=p['image']
  if img and ':' in img: a,b=img.split(':',1); img=f'assets/{a}/{b}'
  cat=str(d.get('category',''))
  score=len(text)+(-5000 if LORE.search(cat+title) else 0)+(800 if re.search(r'obtain|craft|found|drop|equip|wear|right.click|use',text,re.I) else 0)
  for it in items:
    if it in ids:
      if score>best.get(it,-1e9):
        best[it]=score
        out[it]={'book':bkname(bk),'entry':title,'text':short(text),'img':img,'jar':jar}
# bosses
BOSS=re.compile(r'\b(boss|summon|altar|ritual|apostle|wither|dragon|wraith|warden|leviathan|harbinger|ignis|scylla|lich|king|queen|lord)\b',re.I)
bosses={}
for jar,bk,path,d in entries:
  title=strip(L(d.get('name',''))); cat=str(d.get('category',''))
  pages=d.get('pages',[]) or []
  ent=[p.get('entity') for p in pages if isinstance(p,dict) and p.get('type','').endswith('entity') and p.get('entity')]
  text=' '.join(strip(L(p.get('text',''))) for p in pages if isinstance(p,dict) and p.get('text'))
  if not text or LORE.search(title): continue
  if ent or re.search(r'boss|mob|entit|servant|creature',cat,re.I) or re.search(r'\bboss\b',text,re.I):
    if not (re.search(r'boss',cat+title+text,re.I) or ent): continue
    img=next((p['images'][0] for p in pages if isinstance(p,dict) and p.get('images')),'')
    if img and ':' in img: a,b=img.split(':',1); img=f'assets/{a}/{b}'
    key=title or (ent[0] if ent else path)
    if key in bosses and len(bosses[key]['text'])>=len(short(text)): continue
    bosses[key]={'text':short(text),'img':img,'jar':jar,'book':bkname(bk),'entity':(ent[0].split('{')[0] if ent else '')}
# keep only boss-ish
bosses={k:v for k,v in bosses.items() if (re.search(r'\bboss',v['text']+k,re.I) or (v['entity'] and BOSS.search(k+' '+v['text']))) and not re.search(r'servant|charm|upgrade|familiar|support|multiplayer|sigil|cloth|vines|leaves|sniffer|bartering',k,re.I)}
json.dump(out,open(W+'/guides.json','w'),indent=1,ensure_ascii=False)
json.dump(bosses,open(W+'/guides_bosses.json','w'),indent=1,ensure_ascii=False)
from collections import Counter
print(len(ids),len(out),len(bosses),len(entries)); print(Counter(v['book'] for v in out.values()))
print(sorted(bosses)[:80])
