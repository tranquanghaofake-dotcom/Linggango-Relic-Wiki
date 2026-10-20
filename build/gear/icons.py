"""Item icons for gear ids: item model -> layer textures (composited, first animation frame).
Search order: kubejs assets, pack resource zips, mod jars. Writes icons.json id -> base64 png."""
import sys, json, glob, zipfile, io, base64, os, re
from PIL import Image
S = sys.argv[1]; ids = json.load(open(sys.argv[2])); outp = sys.argv[3]
srcs = []
class Dir:
    def __init__(s, root): s.root = root
    def read(s, p):
        f = os.path.join(s.root, p)
        return open(f, 'rb').read() if os.path.isfile(f) else None
class Zip:
    def __init__(s, f):
        s.z = zipfile.ZipFile(f); s.n = set(s.z.namelist())
    def read(s, p): return s.z.read(p) if p in s.n else None
srcs.append(Dir(S + '/pack/src/overrides/kubejs'))
for f in glob.glob(S + '/pack/mods/*.zip') + glob.glob(S + '/pack/src/overrides/resourcepacks/*.zip'):
    try: srcs.append(Zip(f))
    except Exception: pass
for f in sorted(glob.glob(S + '/pack/mods/*.jar')):
    try: srcs.append(Zip(f))
    except Exception: pass
srcs.append(Zip(S + '/pack/mods/zz_client-1.20.1.jar.bak'))
def rd(p):
    for s in srcs:
        b = s.read(p)
        if b is not None: return b
def rl(x, kind):
    ns, p = (x.split(':', 1) if ':' in x else ('minecraft', x))
    return 'assets/%s/%s/%s' % (ns, kind, p)
def model(x, d=0):
    b = rd(rl(x, 'models') + '.json')
    if not b or d > 8: return {}
    try: m = json.loads(b)
    except Exception: return {}
    tex = {}
    if 'parent' in m and not str(m['parent']).startswith('builtin'):
        tex.update(model(m['parent'], d + 1).get('textures', {}))
    tex.update(m.get('textures', {}))
    m['textures'] = tex
    return m
def frame(b):
    im = Image.open(io.BytesIO(b)).convert('RGBA')
    w, h = im.size
    if h > w and h % w == 0: im = im.crop((0, 0, w, w))
    return im
out = {}
for i in ids:
    ns, n = i.split(':', 1)
    m = model(ns + ':item/' + n); t = m.get('textures', {})
    layers = [t[k] for k in sorted(t) if re.match(r'layer\d+$', k)]
    if not layers and t: layers = [t.get('particle') or list(t.values())[0]]
    if not layers: layers = [ns + ':item/' + n]
    im = None
    for L in layers:
        while isinstance(L, str) and L.startswith('#'): L = t.get(L[1:])
        if not isinstance(L, str): continue
        b = rd(rl(L, 'textures') + '.png')
        if not b: continue
        try: f = frame(b)
        except Exception: continue
        if im is None: im = f
        else:
            if f.size != im.size: f = f.resize(im.size, Image.NEAREST)
            im.alpha_composite(f)
    if im is None:
        b = rd('assets/%s/textures/item/%s.png' % (ns, n))
        if b:
            try: im = frame(b)
            except Exception: im = None
    if im is None: continue
    if im.size[0] > 64: im = im.resize((64, 64), Image.NEAREST)
    bo = io.BytesIO(); im.save(bo, 'PNG', optimize=True); out[i] = base64.b64encode(bo.getvalue()).decode()
json.dump(out, open(outp, 'w'))
print(len(ids), 'icons', len(out))
