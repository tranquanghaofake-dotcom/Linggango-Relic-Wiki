"""Fetch LICENSE*/README of GitHub repos at HEAD and flag sentences that put art/assets under other terms.
Usage: python3 -I repocheck.py <in tsv: title\\trepo\\tfx> <out json>"""
import sys,json,re,urllib.request,concurrent.futures as cf
rows=[l.split('\t') for l in open(sys.argv[1]).read().splitlines() if l]
NAMES=['LICENSE','LICENSE.md','LICENSE.txt','LICENCE','LICENCE.md','COPYING','COPYING.md','COPYING.LESSER','LICENSE-ASSETS.md','ASSETS_LICENSE.md','README.md','readme.md','README.MD']
def get(u):
    try: return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'lgw'}),timeout=30).read().decode('utf8','replace')
    except Exception: return None
ART=r'(assets?|textures?|art(?:work)?|models?|sprites?|sounds?|images?|graphics?|resources?)'
TERMS=r'(all rights reserved|not (?:covered|included|licensed|part of)|separate(?:ly)? licen|proprietary|cc[ -]?by|creative commons|exclud|except|without (?:explicit )?permission|may not be (?:used|copied|redistributed))'
EXC=re.compile(r'[^\n.]*\b'+ART+r'\b[^\n.]{0,200}'+TERMS+r'[^\n.]*|[^\n.]*'+TERMS+r'[^\n.]{0,200}\b'+ART+r'\b[^\n.]*',re.I)
BOILER=('this program is free','you should have received','the software is provided','informational purposes','licensed material','copyright and similar','musical work','such as by intimate data')
def job(row):
    t,rp=row[0],row[1]; found={}
    for n in NAMES:
        x=get(f'https://raw.githubusercontent.com/{rp}/HEAD/{n}')
        if x: found[n]=x
    head={n:' '.join(x[:120].split()) for n,x in found.items() if not n.lower().startswith('readme')}
    exc=[]
    for n,x in found.items():
        for m in EXC.finditer(x):
            s=' '.join(m.group(0).split())
            if len(s)>12 and not any(b in s.lower() for b in BOILER): exc.append(f"{n}: {s[:260]}")
    return t,{'repo':rp,'files':list(found),'license_head':head,'exceptions':exc[:5]}
with cf.ThreadPoolExecutor(10) as ex: out=dict(ex.map(job,rows))
json.dump(out,open(sys.argv[2],'w'),indent=1)
print(len(out),'checked;',sum(1 for v in out.values() if not v['files']),'unreachable;',sum(1 for v in out.values() if v['exceptions']),'with flagged sentences')
