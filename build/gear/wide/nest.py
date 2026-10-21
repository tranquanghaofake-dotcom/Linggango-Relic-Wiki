# extract jar-in-jar mods that are not also shipped as top-level jars -> W/gx/nested/*.jar
import zipfile,glob,sys,os,io,re
G=sys.argv[1]; os.makedirs(G+'/nested',exist_ok=True)
def modids(z):
    try: t=z.read('META-INF/mods.toml').decode('utf8','ignore')
    except KeyError: return set()
    return {m.group(1) for b in re.split(r'\[\[mods\]\]',t)[1:] for m in [re.search(r'modId\s*=\s*"([^"]+)"',b.split('[[dependencies')[0])] if m}
top=set(); tops=[]
for j in sorted(glob.glob(G+'/pack/mods/*.jar')):
    try: z=zipfile.ZipFile(j)
    except Exception: continue
    top|=modids(z); tops.append((j,z))
seen=set(); out=[]; best={}
def ver(fn):
    m=re.findall(r'(\d+(?:\.\d+)+)',fn)
    return tuple(int(x) for x in m[-1].split('.')) if m else ()
def walk(z,label,d=0):
    for n in z.namelist():
        if n.startswith('META-INF/jarjar/') and n.endswith('.jar'):
            b=z.read(n)
            try: zz=zipfile.ZipFile(io.BytesIO(b))
            except Exception: continue
            ids=modids(zz); nc=sum(1 for x in zz.namelist() if x.endswith('.class'))
            if ids and not (ids&top) and nc:
                key=tuple(sorted(ids)); v=ver(n.split('/')[-1])
                if key not in best or v>best[key][0]: best[key]=(v,label+'__'+n.split('/')[-1],b,nc)
            if d<2: walk(zz,label,d+1)
for j,z in tops: walk(z,os.path.basename(j)[:-4])
for key,(v,fn,b,nc) in sorted(best.items()):
    open(G+'/nested/'+fn,'wb').write(b); print(fn,key,v,nc)
