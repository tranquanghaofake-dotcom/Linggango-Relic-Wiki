import json,sys,os,re,zipfile,hashlib,collections
P=sys.argv[1]; m=json.load(open(P+'/src/manifest.json')); out={}
LICN=re.compile(r'(^|/)(licen[cs]e|copying|credits|terms|readme|notice|permission)[^/]*$',re.I)
FXW=re.compile(r'(fx|effect|spell|magic|vfx|slash|beam|aura|ring|circle|rune|glyph|spark|flame|soul|lightning|shock|wave|blast|explos|portal|orb|trail|swirl|glow|halo)',re.I)
def cat(n):
    l=n.lower()
    if not l.endswith('.png'): return None
    if '/textures/particle' in l: return 'particle'
    if '/textures/mob_effect' in l: return 'mob_effect'
    if '/textures/gui' in l: return 'gui'
    if '/textures/entity' in l: return 'entity_fx' if FXW.search(l.split('/textures/entity',1)[1]) else 'entity'
    if '/textures/block' in l: return 'block'
    if '/textures/item' in l: return 'item'
    if '/textures/' in l: return 'other_fx' if FXW.search(l) else 'other'
    return 'png_misc'
for f in m['files']:
    pid=f['projectID']; d=json.load(open(f'{P}/cf/{pid}.json')); name=d['files'][0]['name']; fp=f'{P}/files/{pid}/{name}'
    b=open(fp,'rb').read(); r={'pid':pid,'fid':f['fileID'],'title':d['title'].strip(),'type':d['type'],'file':name,'sha1':hashlib.sha1(b).hexdigest(),
       'size':len(b),'authors':[x['username'] for x in d.get('members',[])],'cf_url':d['urls'].get('curseforge')}
    try: z=zipfile.ZipFile(fp)
    except Exception as e: r['err']=str(e); out[pid]=r; continue
    names=z.namelist(); c=collections.Counter(); ns=collections.Counter(); anim=0; pj=0
    for n in names:
        k=cat(n)
        if k: c[k]+=1; mm=re.match(r'(?:.*?/)?assets/([^/]+)/',n); ns[mm.group(1) if mm else '?']+=1
        if n.endswith('.png.mcmeta'): anim+=1
        if re.search(r'assets/[^/]+/particles/[^/]+\.json$',n): pj+=1
    r['counts']=dict(c); r['anim']=anim; r['particle_json']=pj; r['namespaces']=dict(ns.most_common(6))
    toml=[n for n in names if n.endswith('META-INF/mods.toml')]
    if toml:
        t=z.read(toml[0]).decode('utf8','replace')
        g=lambda k: (re.search(r'^\s*'+k+r'\s*=\s*["\']{1,3}(.*?)["\']{1,3}',t,re.M|re.S) or [None,None])[1]
        r['toml_license']=g('license'); r['modids']=re.findall(r'^\s*modId\s*=\s*"([^"]+)"',t,re.M)
        r['toml_url']=g('displayURL'); r['toml_issues']=g('issueTrackerURL'); r['toml_authors']=g('authors')
    pm=[n for n in names if n=='pack.mcmeta']
    if pm:
        try: r['pack_desc']=str(json.loads(z.read(pm[0]).decode('utf8','replace')).get('pack',{}).get('description'))[:300]
        except Exception: r['pack_desc']='?'
    lf={}
    for n in names:
        if LICN.search(n) and not n.endswith('/') and z.getinfo(n).file_size<200000 and not n.endswith(('.class','.png','.ogg')):
            lf[n]=z.read(n).decode('utf8','replace')[:4000]
            if len(lf)>=6: break
    r['license_files']=lf; out[pid]=r
json.dump(out,open(P+'/scan.json','w'),indent=0)
print(len(out))
