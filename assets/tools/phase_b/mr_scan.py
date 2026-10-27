"""Count effect-related art in each downloaded Modrinth file, read its own mod ids and licence files. Executes nothing.
Usage: python3 -I mr_scan.py <work dir>"""
import json,sys,os,re,zipfile,collections
W=sys.argv[1]; F=json.load(open(W+'/mr_fetched.json'))
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from assetlib import kind
EXC=re.compile(r'[^\n.]*\b(assets?|textures?|art(?:work)?|sprites?|models?|sounds?)\b[^\n.]{0,200}(all rights reserved|not (?:covered|included|licensed)|proprietary|without (?:explicit )?permission|may not)[^\n.]*',re.I)
for pid,v in F.items():
    if 'skip' in v: continue
    fp=f"{W}/mr/{v['slug']}/{v['file']}"
    try: z=zipfile.ZipFile(fp)
    except Exception as e: v['skip']='not a zip'; continue
    names=z.namelist(); ids=set()
    for n in names:
        if n.endswith(('META-INF/mods.toml','META-INF/neoforge.mods.toml')): ids|=set(re.findall(r'^\s*modId\s*=\s*"([^"]+)"',z.read(n).decode('utf8','replace'),re.M))
        if n in('fabric.mod.json','quilt.mod.json'):
            try:
                j=json.loads(z.read(n).decode('utf8','replace'),strict=False); ids.add(j.get('id') or j.get('quilt_loader',{}).get('id'))
            except Exception: pass
    ids-={None,'forge','minecraft','fabricloader','neoforge'}
    c=collections.Counter(); an=0
    for n in names:
        m=re.match(r'assets/([^/]+)/(textures/.+\.png|particles/[^/]+\.json)$',n)
        if not m: continue
        ns=m.group(1)
        if v['type']=='mod' and ids and ns not in ids and ns!='minecraft': continue
        if v['type']=='resourcepack' and ns not in('minecraft','realms'): continue
        c[kind(n)]+=1
        if n+'.mcmeta' in names: an+=1
    exc=[]
    for n in names:
        if re.search(r'(^|/)(licen[cs]e|copying|credits|readme|notice)[^/]*$',n,re.I) and not n.endswith('/'):
            t=z.read(n)[:20000].decode('utf8','replace')
            exc+= [f"{n}: {' '.join(m.group(0).split())[:200]}" for m in EXC.finditer(t)]
    v['ids']=sorted(ids); v['counts']=dict(c); v['anim']=an; v['jar_exc']=exc[:3]
    v['fx']=3*c['particle']+2*c['entity_fx']+2*c['other_fx']+c['mob_effect']+0.5*c['gui']+an
json.dump(F,open(W+'/mr_fetched.json','w'),indent=0)
ok=[v for v in F.values() if 'skip' not in v]
print(len(ok),'scanned;',sum(1 for v in ok if v['fx']>=15),'with fx>=15;',sum(1 for v in ok if v['jar_exc']),'with asset-exception sentences')
