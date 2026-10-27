"""Add a downloaded source tree (at a recorded version) to the library: raw copy into <assets>/lib/<slug>/<rel>, one catalog row per file.
Usage: python3 -I ingest.py <assets> <spec.json> <work dir>   ("{W}" in the spec is replaced by the work dir)
spec keys: slug, root, title, version, author, license, tier, confidence, include [regex on rel path], exclude [regex],
           missing_in (file listing paths of a reference version), missing_flag (note for files not in it), note"""
import sys,os,re,json,hashlib,shutil
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from assetlib import kind,img_info,append
A=sys.argv[1]; sp={k:(v.replace('{W}',sys.argv[3]) if isinstance(v,str) else v) for k,v in json.load(open(sys.argv[2])).items()}
inc=[re.compile(x) for x in sp.get('include',['.'])]; exc=[re.compile(x) for x in sp.get('exclude',[])]
ref=set(open(sp['missing_in']).read().split('\n')) if sp.get('missing_in') else None
rows=[]
for dp,_,fs in os.walk(sp['root']):
    for f in sorted(fs):
        full=os.path.join(dp,f); rel=os.path.relpath(full,sp['root']).replace(os.sep,'/')
        if f.endswith('.mcmeta') or not any(x.search(rel) for x in inc) or any(x.search(rel) for x in exc): continue
        if not re.search(r'\.(png|json|tga|jpg)$',f,re.I): continue
        out=os.path.join(A,'lib',sp['slug'],rel); os.makedirs(os.path.dirname(out),exist_ok=True); shutil.copyfile(full,out)
        meta=None
        if os.path.exists(full+'.mcmeta'): meta=open(full+'.mcmeta','rb').read(); shutil.copyfile(full+'.mcmeta',out+'.mcmeta')
        b=open(full,'rb').read()
        k=('particle_def' if '/particles/' in '/'+rel and f.endswith('.json') else 'data') if f.endswith('.json') else kind('x/'+rel if 'textures/' in rel else 'x/textures/other/'+rel)
        lic=sp['license']
        row=dict(id=f"{sp['slug']}:{rel}",tier=sp['tier'],confidence=sp['confidence'],kind=k,namespace=sp.get('namespace',''),source=sp['title'],version=sp['version'],
                 src_path=rel,out_path=os.path.relpath(out,A),author=sp['author'],license=lic,derivative_ok=int(sp['tier']!='A-SA' and 'ND' not in lic),
                 sharealike=int(sp['tier']=='A-SA'),noncommercial=int('NC' in lic),sha256=hashlib.sha256(b).hexdigest(),
                 score_lic={'high':3,'medium':2,'low':1}.get(sp['confidence'],1),status='new',note=sp.get('note',''))
        if ref is not None and rel not in ref and (sp.get('ref_prefix','')+rel) not in ref: row['note']=(row['note']+'; ' if row['note'] else '')+sp['missing_flag']
        if f.lower().endswith('.png'):
            try: row.update(img_info(b,meta))
            except Exception as e: row['note']+='; unreadable png'
            sj=full[:-4]+'.json'   # fxgen strips: frames side by side, described by a sibling json
            if os.path.exists(sj):
                j=json.load(open(sj))
                if j.get('frames'): row.update(frames=j['frames'],frame_w=j['frame_w'],frame_h=j['frame_h'],frametime=j.get('frametime_ticks',''),score_anim=3 if j['frames']>=4 else 2)
        rows.append(row)
append(A,rows); print(sp['slug'],len(rows),'rows')
