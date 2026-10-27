import sys,urllib.request,re,os,concurrent.futures as cf
O=sys.argv[1]; repos=sys.argv[2:]
def get(u):
    try: return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'lgw'}),timeout=30).read().decode('utf8','replace')
    except Exception as e: return None
EXC=re.compile(r'[^.\n]*(asset|texture|art|model|sprite|sound|resource)s?[^.\n]*(licen|rights|reserved|cc[ -]?by|creative commons|permission|not (?:covered|included))[^.\n]*',re.I)
def job(rp):
    out=[]
    for f in ['LICENSE','LICENSE.md','LICENSE.txt','LICENCE','COPYING','LICENSE-ASSETS','LICENSE_ASSETS.md','ASSETS_LICENSE','README.md','README']:
        t=get(f'https://raw.githubusercontent.com/{rp}/HEAD/{f}')
        if t:
            open(f"{O}/{rp.replace('/','__')}__{f}",'w').write(t)
            head=' '.join(t[:160].split())
            ex=[' '.join(m.group(0).split())[:220] for m in EXC.finditer(t)][:4] if f.startswith('README') or 'ASSET' in f.upper() or True else []
            out.append((f,head,ex))
    return rp,out
with cf.ThreadPoolExecutor(8) as ex:
    for rp,out in ex.map(job,repos):
        print('##',rp)
        for f,h,e in out:
            print('  ',f,'::',h[:130]); [print('      !',x) for x in e if not x.lower().startswith(('the software is provided','this program is free','you should have received'))]
