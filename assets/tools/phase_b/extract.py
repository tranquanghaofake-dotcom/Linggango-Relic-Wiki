"""Phase B (pack): copy the art of every tier A / A-SA / A-perm source of the pack into <lib>/<slug>/, raw bytes, original paths,
and write one catalog row per texture (or particle definition).
Kept: assets/<ns>/textures/**.png (+ .png.mcmeta) and assets/<ns>/particles/*.json, for the mod's own namespaces and `minecraft`
(vanilla overrides). Namespaces of other mods in the pack are skipped (their art is not this author's to license); nested jars are not opened.
Usage: python3 -I extract.py <work dir> <sources.csv> <assets dir>"""
import csv,json,zipfile,re,sys,os,io,hashlib,collections
from PIL import Image
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from assetlib import kind,img_info,append
W,SRC,A=sys.argv[1:4]; LIB=os.path.join(A,'lib')
R=[r for r in csv.DictReader(open(SRC)) if r['tier'] in('A','A-SA','A-perm') and r['cf_project']]
d=json.load(open(W+'/scan.json'))
allmods=collections.defaultdict(set)
for k,r in d.items():
    for m in r.get('modids') or []: allmods[m].add(k)
rows=[]
for r in R:
    s=d[r['cf_project']]; own=set(s.get('modids') or [])-{'forge','minecraft'}
    slug=(r['cf_url'].rstrip('/').rsplit('/',1)[-1] if r['cf_url'] else 'cf'+r['cf_project'])
    z=zipfile.ZipFile(f"{W}/files/{r['cf_project']}/{r['file']}"); names=set(z.namelist())
    for i in z.infolist():
        m=re.match(r'assets/([^/]+)/(textures/.+\.png|particles/[^/]+\.json)$',i.filename)
        if not m: continue
        ns=m.group(1)
        if r['type']=='Mods' and ns not in own and ns!='minecraft' and ns in allmods: continue
        b=z.read(i); out=os.path.join(LIB,slug,i.filename); os.makedirs(os.path.dirname(out),exist_ok=True); open(out,'wb').write(b)
        meta=None
        if i.filename+'.mcmeta' in names:
            meta=z.read(i.filename+'.mcmeta'); open(out+'.mcmeta','wb').write(meta)
        row=dict(id=f"{slug}:{i.filename}",tier=r['tier'],confidence=r['confidence'],kind=kind(i.filename),namespace=ns,source=r['title'],
                 version=r['file'],src_path=i.filename,out_path=os.path.relpath(out,A),author=r['authors'],license=r['lic_class'],
                 derivative_ok=0 if r['tier']=='A-SA' or 'ND' in r['lic_class'] else 1,sharealike=int(r['tier']=='A-SA'),
                 noncommercial=int('NC' in r['lic_class'] or r['tier']=='A-SA'),sha256=hashlib.sha256(b).hexdigest(),
                 score_lic={'high':3,'medium':2,'low':1}.get(r['confidence'],1),status='new')
        if i.filename.endswith('.png'):
            try: row.update(img_info(b,meta))
            except Exception as e: row['note']='unreadable png: '+str(e)[:60]
        rows.append(row)
append(A,rows)
print(len(rows),'rows'); print(collections.Counter(x['kind'] for x in rows).most_common())
