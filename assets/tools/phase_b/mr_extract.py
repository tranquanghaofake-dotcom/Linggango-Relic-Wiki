"""Phase B (outside the pack): copy the art of kept Modrinth projects into <assets>/lib/mr-<slug>/ and write sources_external rows.
Mods: own namespaces (+ minecraft). Resource packs: minecraft and realms namespaces only (a retexture of another mod is not the pack author's to license).
Usage: python3 -I mr_extract.py <work dir> <assets>"""
import json,sys,os,re,zipfile,hashlib,csv
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from assetlib import kind,img_info,append
W,A=sys.argv[1:3]; F=json.load(open(W+'/mr_fetched.json')); RC=json.load(open(W+'/mr_repocheck.json'))
OVR={'aerial-hell':('A-SA','high','repo README: CC BY-NC-SA 4.0'),'lr-tactical':('B','high','repo readme: art assets All Rights Reserved'),
     'betternether':('A-SA','high','repo LICENSE: some assets CC BY-NC-SA 4.0 (LICENSE.ASSETS); whole mod treated as ShareAlike'),
     'mythicmetals':('B','high','repo README: assets (textures) All Rights Reserved'),
     'immersive-weapons':('A-SA','high','repo README: code MIT, assets CC BY-NC-SA (assets/immersiveweapons/LICENSE)')}
SA=re.compile(r'SA'); rows_src=[]; rows=[]
for pid,v in F.items():
    if 'skip' in v:
        rows_src.append({'slug':v.get('slug',pid),'status':'skipped: '+v['skip']}); continue
    lic=v['license']; rc=RC.get(v['slug'])
    if v['slug'] in OVR: tier,conf,note=OVR[v['slug']]
    else:
        tier='A-SA' if '-SA' in lic else 'A'
        if rc and not rc['exceptions'] and any(not f.lower().startswith('readme') for f in rc['files']): conf,note='high',f"repo {rc['repo']} licence read at HEAD (automatic scan, no asset exception)"
        else: conf,note='medium','licence from Modrinth only'+('' if rc else ' (no GitHub repo)')
    status='kept' if 'drop' not in v and tier!='B' else ('coordinates only' if tier=='B' else 'dropped: '+v['drop'])
    if 'drop' in v and v['drop'].startswith(('X','B')): tier=v['drop'][0]; note=v['drop']; status='coordinates only' if tier=='B' else 'excluded'
    rows_src.append({'slug':v['slug'],'title':v['title'],'type':v['type'],'url':v['url'],'version':v['version'],'file':v['file'],'sha1':v['sha1'],
                     'team':v['team'],'downloads':v['downloads'],'license':lic,'source':v.get('source') or '','tier':tier,'confidence':conf,'fx_score':round(v['fx']),
                     'counts':json.dumps(v['counts']),'status':status,'note':note})
    if status!='kept': continue
    z=zipfile.ZipFile(f"{W}/mr/{v['slug']}/{v['file']}"); names=set(z.namelist()); ids=set(v['ids'])
    for n in sorted(names):
        m=re.match(r'assets/([^/]+)/(textures/.+\.png|particles/[^/]+\.json)$',n)
        if not m: continue
        ns=m.group(1)
        if v['type']=='mod' and ids and ns not in ids and ns!='minecraft': continue
        if v['type']=='resourcepack' and ns not in('minecraft','realms'): continue
        b=z.read(n); out=os.path.join(A,'lib','mr-'+v['slug'],n); os.makedirs(os.path.dirname(out),exist_ok=True); open(out,'wb').write(b)
        meta=z.read(n+'.mcmeta') if n+'.mcmeta' in names else None
        if meta is not None: open(out+'.mcmeta','wb').write(meta)
        row=dict(id=f"mr-{v['slug']}:{n}",tier=tier,confidence=conf,kind=kind(n),namespace=ns,source=v['title']+' (Modrinth)',version=f"{v['file']} ({v['version']})",
                 src_path=n,out_path=os.path.relpath(out,A),author=v['team'],license=lic,derivative_ok=int(tier!='A-SA' and 'ND' not in lic),
                 sharealike=int(tier=='A-SA'),noncommercial=int('NC' in lic),sha256=hashlib.sha256(b).hexdigest(),score_lic={'high':3,'medium':2}.get(conf,1),status='new')
        if n.endswith('.png'):
            try: row.update(img_info(b,meta))
            except Exception: row['note']='unreadable png'
        rows.append(row)
append(A,rows)
K=['slug','title','type','url','version','file','sha1','team','downloads','license','source','tier','confidence','fx_score','counts','status','note']
with open(os.path.join(A,'sources_modrinth.csv'),'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=K,extrasaction='ignore'); w.writeheader(); w.writerows(sorted(rows_src,key=lambda r:(r.get('status',''),-int(r.get('fx_score') or 0))))
import collections; print(len(rows),'catalog rows'); print(collections.Counter(r['status'][:16] for r in rows_src))
