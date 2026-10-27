import json,sys,re,collections
P=sys.argv[1]; d=json.load(open(P+'/scan.json'))
def norm(s):
    if not s: return None
    l=s.lower().replace('_',' ')
    if re.search(r'all.?rights.?reserved|\barr\b',l): return 'ARR'
    if 'nd' in re.findall(r'\b(nd)\b',l) or 'noderiv' in l: return 'CC-ND'
    if re.search(r'cc.?by.?nc.?sa|by-nc-sa',l): return 'CC-BY-NC-SA'
    if re.search(r'cc.?by.?sa|by-sa',l): return 'CC-BY-SA'
    if re.search(r'cc.?by.?nc|by-nc',l): return 'CC-BY-NC'
    if re.search(r'cc0|c0-1|unlicense|public domain',l): return 'CC0'
    if re.search(r'cc.?by|creative commons attribution',l): return 'CC-BY'
    if re.search(r'lesser|lgpl',l): return 'LGPL'
    if re.search(r'\bgpl|general public',l): return 'GPL'
    if 'mpl' in l or 'mozilla' in l: return 'MPL'
    if 'mit' in re.findall(r'\b(mit)\b',l): return 'MIT'
    if 'apache' in l: return 'Apache'
    if 'bsd' in l: return 'BSD'
    if 'academic free' in l or 'mmpl' in l or 'minecraft mod public' in l: return 'OSS-other'
    if 'licenseref' in l or 'custom' in l or 'license' in l or 'cofh' in l or 'dsmsl' in l: return 'custom'
    return None
EXC=re.compile(r'(asset|texture|model|sprite|sound|art)s?[^.\n]{0,160}(all rights reserved|not (?:covered|included|licensed)|separate|proprietary|cc[ -]by|creative commons|exclud)',re.I)
for r in d.values():
    src=[]
    a=norm(r.get('toml_license')); b=norm((r.get('mr') or {}).get('license'))
    if a: src.append(('toml',a))
    if b: src.append(('modrinth',b))
    for n,t in r.get('license_files',{}).items():
        if re.search(r'licen|copying',n,re.I):
            c=norm(t[:600])
            if c: src.append(('file:'+n,c))
    exc=[]
    for n,t in r.get('license_files',{}).items():
        for mm in EXC.finditer(t): exc.append((n,t[max(0,mm.start()-80):mm.end()+80].replace('\n',' ')))
    if 'Assets: ARR' in (r.get('toml_license') or ''): exc.append(('toml',r['toml_license']))
    r['lic_sources']=src; r['asset_exc']=exc[:3]
    cls=[c for _,c in src]
    r['lic']= 'none' if not cls else ('ARR' if 'ARR' in cls else ('CC-ND' if 'CC-ND' in cls else (cls[0] if len(set(cls))==1 else '/'.join(sorted(set(cls))))))
json.dump(d,open(P+'/scan.json','w'),indent=0)
c=collections.Counter((r['type'],r['lic']) for r in d.values())
for k,v in sorted(c.items(),key=lambda x:-x[1]): print(v,k)
