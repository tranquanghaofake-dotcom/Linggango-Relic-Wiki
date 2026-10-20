"""Icons for gear whose item model icons.py can't read: forge:separate_transforms (GUI perspective),
GeckoLib items with a flat *_gui / *_inventory / *_tiny / *_icon texture, or plain textures/item/<path>.png.
Usage: gui_icons.py W ids.json out.json"""
import sys,json,glob,zipfile,io,base64,re
from PIL import Image
W,ids,out=sys.argv[1],json.load(open(sys.argv[2])),sys.argv[3]
Z=[]
for f in sorted(glob.glob(W+'/pack/mods/*.jar')):
    try: z=zipfile.ZipFile(f); Z.append((z,set(z.namelist())))
    except Exception: pass
def rd(p):
    for z,n in Z:
        if p in n: return z.read(p)
def names(prefix):
    return [p for z,n in Z for p in n if p.startswith(prefix)]
def tex_of_model(m,d=0):
    if not isinstance(m,dict) or d>6: return None
    if m.get('loader','').endswith('separate_transforms'):
        g=(m.get('perspectives') or {}).get('gui')
        t=tex_of_model(g,d+1) if g else None
        if t: return t
        return tex_of_model(m.get('base'),d+1)
    t=(m.get('textures') or {}).get('layer0')
    if t: return t
    if m.get('parent') and not str(m['parent']).startswith(('builtin','item/','minecraft:item/')):
        ns,p=(m['parent'].split(':',1)+[''])[:2] if ':' in m['parent'] else ('minecraft',m['parent'])
        b=rd(f'assets/{ns}/models/{p}.json')
        if b:
            try: return tex_of_model(json.loads(b),d+1)
            except Exception: pass
def png(t):
    ns,p=t.split(':',1) if ':' in t else ('minecraft',t)
    return rd(f'assets/{ns}/textures/{p}.png')
res={}
for i in ids:
    ns,p=i.split(':',1); b=None
    mj=rd(f'assets/{ns}/models/item/{p}.json')
    if mj:
        try:
            t=tex_of_model(json.loads(mj))
            if t: b=png(t)
        except Exception: pass
    if not b:
        for suf in ['_gui','_inventory','_icon','_tiny','_item','']:
            b=rd(f'assets/{ns}/textures/item/{p}{suf}.png')
            if b: break
    if not b: continue
    im=Image.open(io.BytesIO(b)).convert('RGBA')
    w,h=im.size
    if h>w and h%w==0: im=im.crop((0,0,w,w))
    if max(im.size)>64: im=im.resize((64,64),Image.NEAREST)
    o=io.BytesIO(); im.save(o,'PNG'); res[i]=base64.b64encode(o.getvalue()).decode()
json.dump(res,open(out,'w')); print(len(res),'of',len(ids))
print([i for i in ids if i not in res])
