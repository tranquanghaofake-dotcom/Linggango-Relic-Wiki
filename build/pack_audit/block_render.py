#!/usr/bin/env python3
"""Inventory pictures for blocks that have no flat item texture, only a block model made of cubes (a station such as
Blood Magic's Blood Altar or Somake Spells' Upgrade Forge). Draws the model the way the game's inventory draws a block:
an isometric view of each cube's top, south and east faces, textures sampled texel by texel (nearest), the sides shaded
like the game's directional light (top 100 %, south 80 %, east 60 %), painted back to front. Element rotations are
ignored (the stations draw fine without them). Output: 64x64, shown at 32 px (1/2, a whole-number ratio).

render(model_id, rd) -> PIL image or None; rd(path) reads a file from the jars (see name_icons.py)."""
import json, io, math
from PIL import Image, ImageDraw
N = 64
def _model(x, rd, d=0):
    ns, p = x.split(":", 1) if ":" in x else ("minecraft", x)
    b = rd(f"assets/{ns}/models/{p}.json")
    if not b or d > 8: return {}
    m = json.loads(b); tex, el = {}, None
    if isinstance(m.get("parent"), str) and not m["parent"].startswith("builtin"):
        pm = _model(m["parent"], rd, d + 1); tex.update(pm.get("textures", {})); el = pm.get("elements")
    tex.update(m.get("textures", {})); m["textures"] = tex
    if "elements" not in m and el: m["elements"] = el
    return m
def render(mid, rd):
    m = _model(mid, rd); els = m.get("elements"); T = m.get("textures", {})
    if not els: return None
    cache = {}
    def tex(ref):
        while isinstance(ref, str) and ref.startswith("#"): ref = T.get(ref[1:])
        if not isinstance(ref, str): return None
        if ref not in cache:
            ns, p = ref.split(":", 1) if ":" in ref else ("minecraft", ref)
            b = rd(f"assets/{ns}/textures/{p}.png")
            if not b: cache[ref] = None
            else:
                im = Image.open(io.BytesIO(b)).convert("RGBA"); w, h = im.size
                cache[ref] = im.crop((0, 0, w, w)) if h > w and h % w == 0 else im
        return cache[ref]
    c, s = math.cos(math.radians(30)), math.sin(math.radians(30))
    raw = lambda x, y, z: ((x - z) * c, (x + z) * s - y)
    pts = [raw(x, y, z) for e in els for x in (e["from"][0], e["to"][0]) for y in (e["from"][1], e["to"][1]) for z in (e["from"][2], e["to"][2])]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts); y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    k = (N - 4) / max(x1 - x0, y1 - y0)            # fit the whole model, two pixels of air around it
    ox, oy = (N - (x1 - x0) * k) / 2 - x0 * k, (N - (y1 - y0) * k) / 2 - y0 * k
    P = lambda x, y, z: (ox + raw(x, y, z)[0] * k, oy + raw(x, y, z)[1] * k)
    out = Image.new("RGBA", (N, N))
    def face(im, uv, p0, p1, p2, shade):
        if im is None: return
        w, h = im.size; u1, v1, u2, v2 = [t * w / 16 if i % 2 == 0 else t * h / 16 for i, t in enumerate(uv)]
        # destination → source affine: solve for (a,b,c,d,e,f) with p0→(u1,v1), p1→(u2,v1), p2→(u1,v2)
        (x0, y0), (x1, y1), (x2, y2) = p0, p1, p2
        det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if abs(det) < 1e-6: return
        ia, ib = (y2 - y0) / det, -(x2 - x0) / det; ic, id_ = -(y1 - y0) / det, (x1 - x0) / det
        A = ((u2 - u1) * ia, (u2 - u1) * ib); D = ((v2 - v1) * ic, (v2 - v1) * id_)
        a, b = A[0], A[1]; dd, e = D[0], D[1]
        # (u,v) = (u1,v1) + (u2-u1)*s + (v2-v1)*t, where (s,t) are the point's coordinates along p0→p1 and p0→p2
        a, b = (u2 - u1) * ia, (u2 - u1) * ib; dd, e = (v2 - v1) * ic, (v2 - v1) * id_
        cc = u1 - a * x0 - b * y0; f = v1 - dd * x0 - e * y0
        layer = im.transform((N, N), Image.AFFINE, (a, b, cc, dd, e, f), resample=Image.NEAREST)
        mask = Image.new("L", (N, N)); p3 = (x1 + x2 - x0, y1 + y2 - y0)
        ImageDraw.Draw(mask).polygon([p0, p1, p3, p2], fill=255)
        if shade < 1:
            r, g, bch, al = layer.split(); f2 = lambda ch: ch.point(lambda v: int(v * shade))
            layer = Image.merge("RGBA", (f2(r), f2(g), f2(bch), al))
        alpha = Image.composite(layer.split()[3], Image.new("L", (N, N)), mask)
        layer.putalpha(alpha); out.alpha_composite(layer)
    for e in sorted(els, key=lambda e: (e["from"][1] + e["to"][1], e["from"][0] + e["from"][2])):
        (x1, y1, z1), (x2, y2, z2) = e["from"], e["to"]; F = e.get("faces", {})
        def fa(name, p0, p1, p2, sh):
            f = F.get(name)
            if f: face(tex(f.get("texture")), f.get("uv") or [0, 0, 16, 16], p0, p1, p2, sh)
        fa("up", P(x1, y2, z1), P(x2, y2, z1), P(x1, y2, z2), 1.0)
        fa("south", P(x1, y2, z2), P(x2, y2, z2), P(x1, y1, z2), .8)
        fa("east", P(x2, y2, z2), P(x2, y2, z1), P(x2, y1, z2), .6)
    return out if out.getbbox() else None

def render_obj(obj_path, tex_path, rd, flip_v=True):
    """the same view for a Forge OBJ model (Blood Magic draws its altar with one): every triangle textured and shaded by
    how much it faces the light, painted back to front"""
    b, t = rd(obj_path), rd(tex_path)
    if not b or not t: return None
    im = Image.open(io.BytesIO(t)).convert("RGBA"); W, H = im.size
    V, VT, F = [], [], []
    for line in b.decode("utf-8", "replace").splitlines():
        p = line.split()
        if not p: continue
        if p[0] == "v": V.append(tuple(float(x) for x in p[1:4]))
        elif p[0] == "vt": VT.append(tuple(float(x) for x in p[1:3]))
        elif p[0] == "f":
            idx = [tuple(int(q) if q else 0 for q in (w.split("/") + ["", ""])[:2]) for w in p[1:]]
            for i in range(1, len(idx) - 1): F.append((idx[0], idx[i], idx[i + 1]))
    c, s = math.cos(math.radians(30)), math.sin(math.radians(30))
    raw = lambda v: ((v[0] - v[2]) * c, (v[0] + v[2]) * s - v[1])
    pts = [raw(v) for v in V]; x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts); y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    k = (N - 4) / max(x1 - x0, y1 - y0); ox, oy = (N - (x1 - x0) * k) / 2 - x0 * k, (N - (y1 - y0) * k) / 2 - y0 * k
    P = lambda v: (ox + raw(v)[0] * k, oy + raw(v)[1] * k)
    out = Image.new("RGBA", (N, N)); L = (-.45, .8, .4)   # light from above, a little from the front left
    depth = lambda tri: sum(V[a[0] - 1][0] + V[a[0] - 1][2] + V[a[0] - 1][1] * .1 for a in tri)
    for tri in sorted(F, key=depth):
        a, b2, cc = [V[q[0] - 1] for q in tri]
        n = [(b2[1] - a[1]) * (cc[2] - a[2]) - (b2[2] - a[2]) * (cc[1] - a[1]), (b2[2] - a[2]) * (cc[0] - a[0]) - (b2[0] - a[0]) * (cc[2] - a[2]),
             (b2[0] - a[0]) * (cc[1] - a[1]) - (b2[1] - a[1]) * (cc[0] - a[0])]
        ln = math.sqrt(sum(x * x for x in n)) or 1; n = [x / ln for x in n]
        if n[0] + n[2] - n[1] * 0 < -0.05 and n[1] < 0.2: continue          # facing away from the viewer
        sh = max(.45, min(1, .6 + .5 * (n[0] * L[0] + n[1] * L[1] + n[2] * L[2])))
        d = [P(v) for v in (a, b2, cc)]
        uv = [VT[q[1] - 1] if q[1] else (0, 0) for q in tri]; uv = [(u * W, ((1 - v) if flip_v else v) * H) for u, v in uv]
        (X0, Y0), (X1, Y1), (X2, Y2) = d; det = (X1 - X0) * (Y2 - Y0) - (X2 - X0) * (Y1 - Y0)
        if abs(det) < 1e-6: continue
        # destination → source affine through the three corners
        m = [[(Y2 - Y0) / det, -(X2 - X0) / det], [-(Y1 - Y0) / det, (X1 - X0) / det]]
        du = (uv[1][0] - uv[0][0], uv[2][0] - uv[0][0]); dv = (uv[1][1] - uv[0][1], uv[2][1] - uv[0][1])
        A_ = du[0] * m[0][0] + du[1] * m[1][0]; B_ = du[0] * m[0][1] + du[1] * m[1][1]
        D_ = dv[0] * m[0][0] + dv[1] * m[1][0]; E_ = dv[0] * m[0][1] + dv[1] * m[1][1]
        C_ = uv[0][0] - A_ * X0 - B_ * Y0; F_ = uv[0][1] - D_ * X0 - E_ * Y0
        layer = im.transform((N, N), Image.AFFINE, (A_, B_, C_, D_, E_, F_), resample=Image.NEAREST)
        r, g, bl, al = layer.split(); f2 = lambda ch: ch.point(lambda v: int(v * sh)); layer = Image.merge("RGBA", (f2(r), f2(g), f2(bl), al))
        mask = Image.new("L", (N, N)); ImageDraw.Draw(mask).polygon(d, fill=255)
        layer.putalpha(Image.composite(layer.split()[3], Image.new("L", (N, N)), mask)); out.alpha_composite(layer)
    return out if out.getbbox() else None
