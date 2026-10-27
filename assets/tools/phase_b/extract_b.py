"""Tier B, for private reference only: copy the art of every tier B source into a LOCAL folder (never into this repository)
and write catalog_b.csv: coordinates only (where to download, path inside the archive, sha256, size, frames) — no pixels.
Sources: tier B rows of sources.csv (CurseForge files), the pack's own quest images (overrides/kubejs/assets), Modrinth projects
marked "coordinates only" in sources_modrinth.csv. Mods: own namespaces + minecraft; resource packs and overrides: everything.
Usage: python3 -I extract_b.py <work dir> <assets dir> <local out dir>"""
import sys,os,re,csv,json,zipfile,hashlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from assetlib import kind,img_info
W,A,OUT=sys.argv[1:4]
if os.path.realpath(OUT).startswith(os.path.realpath(os.path.join(A,'..'))): sys.exit('refusing: the local folder must be outside the repository')
d=json.load(open(W+'/pack/scan.json')); rows=[]
def take(z,names,own,keep_all,src,coord,author,lic,slug):
    for n in sorted(names):
        m=re.match(r'(?:overrides/kubejs/)?assets/([^/]+)/(textures/.+\.png|particles/[^/]+\.json)$',n)
        if not m and n.startswith('overrides/kubejs/assets/') and n.endswith('.png'): ns=n.split('/')[3]   # quest images sit outside textures/
        elif not m: continue
        else: ns=m.group(1)
        if not keep_all and own and ns not in own and ns!='minecraft': continue
        b=z.read(n); p=os.path.join(OUT,slug,n); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'wb').write(b)
        meta=z.read(n+'.mcmeta') if n+'.mcmeta' in names else None
        if meta is not None: open(p+'.mcmeta','wb').write(meta)
        r=dict(id=f'{slug}:{n}',kind='quest_image' if '/customtextures/' in n else kind(n),namespace=ns,source=src,**coord,src_path=n,author=author,license=lic,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
        if n.endswith('.png'):
            try: r.update({k:v for k,v in img_info(b,meta).items() if k in('w','h','frame_w','frame_h','frames','frametime')})
            except Exception: pass
        rows.append(r)
for s in csv.DictReader(open(os.path.join(A,'sources.csv'))):
    if s['tier']!='B' or not s['cf_project']: continue
    sc=d[s['cf_project']]; fp=f"{W}/pack/files/{s['cf_project']}/{s['file']}"
    try: z=zipfile.ZipFile(fp)
    except Exception: continue
    slug=s['cf_url'].rstrip('/').rsplit('/',1)[-1] if s['cf_url'] else 'cf'+s['cf_project']
    take(z,set(z.namelist()),set(sc.get('modids') or [])-{'forge','minecraft'},s['type']!='Mods',s['title'],
         {'download':f"curseforge {s['cf_project']}/{s['cf_file']}",'archive':s['file']},s['authors'],s['lic_class'],slug)
z=zipfile.ZipFile(W+'/pack/pack.zip')   # the pack's own quest images and KubeJS textures
take(z,{n for n in z.namelist() if n.startswith('overrides/kubejs/assets/')},set(),True,'Linggango V6.6.6hf overrides (KubeJS assets, quest images)',
     {'download':'curseforge 1343057/9304214','archive':'Linggango-V6.6.6hf.zip'},'Misanthropy','none (all rights reserved)','linggango-overrides')
for s in csv.DictReader(open(os.path.join(A,'sources_modrinth.csv'))):
    if s['status']!='coordinates only': continue
    fp=f"{W}/mr/{s['slug']}/{s['file']}"
    if not os.path.exists(fp): continue
    z=zipfile.ZipFile(fp); F=json.load(open(W+'/mr_fetched.json')); v=next((x for x in F.values() if x.get('slug')==s['slug']),{})
    take(z,set(z.namelist()),set(v.get('ids') or []),s['type']!='mod',s['title']+' (Modrinth)',{'download':s['url']+' '+s['version'],'archive':s['file']},s['team'],s['license']+' — '+s['note'],'mr-'+s['slug'])
K=['id','kind','namespace','source','download','archive','src_path','author','license','w','h','frame_w','frame_h','frames','frametime','bytes','sha256']
with open(os.path.join(A,'catalog_b.csv'),'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=K,extrasaction='ignore'); w.writeheader(); w.writerows(rows)
import collections; print(len(rows),'files,',round(sum(r['bytes'] for r in rows)/1e6),'MB'); print(collections.Counter(r['kind'] for r in rows).most_common())
