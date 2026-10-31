#!/usr/bin/env python3
"""Inventory pictures of block models (stations such as Blood Magic's Blood Altar or Somake Spells' Upgrade Forge, and
any item whose model is made of cubes), drawn the way the 1.20.1 GUI draws an item in a slot. Every step is the game's:
  - view: the model's `display.gui` transform (block/block.json: rotation [30, 225, 0], scale 0.625; stairs and walls
    [30, 135, 0]; chests [30, 45, 0]), applied as ItemTransform does (translate, rotate X·Y·Z, scale, then -0.5 to the
    centre) inside GuiGraphics.renderItem's 16 px slot with y flipped; orthographic. So a full block shows its top,
    its east face on the left and its north face on the right, the top a 2:1 rhombus, and a half-height model stays
    half height in the slot instead of being stretched to fit.
  - light: GlStateManager.setupGui3DDiffuseLighting (Lighting DIFFUSE_LIGHT_0 (0.2, 1, -0.7), DIFFUSE_LIGHT_1
    (-0.2, 1, 0.7) turned by rotationYXZ(1.0821041, 3.2375858, 0).rotateYXZ(-pi/8, 3pi/4, 0)) for gui_light "side",
    setupGuiFlatDiffuseLighting for "front"; per face min(1, 0.6 (max(0, L0.n) + max(0, L1.n)) + 0.4) (light.glsl).
    The normal is turned by the item's rotations only: PoseStack.mulPoseMatrix, which applies the slot's y flip,
    leaves the normal matrix alone. A full block comes out top 100 %, left (east) 65 %, right (north) 40 %.
  - faces: BlockElement's default uv per face, FaceInfo's corner order, BlockFaceUV rotation, element rotation about
    its origin with `rescale` (1/cos 22.5 deg or 1/cos 45 deg on the two other axes, FaceBakery), cutout at alpha 0.1
    (opaque above it, as the cutout sheet writes it), faces with partial alpha blended back to front.
  - pixels: one z-buffer, nearest texel at each pixel centre, no smoothing.
Checked against these constants read from client-1.20.1.jar (GlStateManager, Lighting, PoseStack bytecode, light.glsl).
Tint: only when the caller passes the item's colours ({tintindex: 0xRRGGBB}); not drawn: Forge's root "transform",
builtin/entity models.
`size` is the picture of one 16 px slot (64 = the GUI at scale 4; the wiki shows it at 32 px, a whole-number ratio).

render_model(m, tex, size, tint) -> PIL image or None   m: a merged model (mcassets.Assets.model), tex(ref) -> RGBA image
render(model_id, rd) -> PIL image or None          rd(path) reads a file from the jars (see name_icons.py)
render_obj(obj_path, tex_path, rd, flip_v=True)    a Forge OBJ model (Blood Magic draws its altar with one)"""
import io, math
import numpy as np
from PIL import Image

BLOCK_GUI = {"rotation": [30, 225, 0], "translation": [0, 0, 0], "scale": [0.625, 0.625, 0.625]}   # block/block.json


def _rx(a): c, s = math.cos(a), math.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def _ry(a): c, s = math.cos(a), math.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def _rz(a): c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
def _n(v): v = np.array(v, float); return v / np.linalg.norm(v)

_L0, _L1 = _n([0.2, 1, -0.7]), _n([-0.2, 1, 0.7])
_M3D = _ry(1.0821041) @ _rx(3.2375858) @ _ry(-math.pi / 8) @ _rx(2.3561945)       # JOML rotationYXZ then rotateYXZ
_MFLAT = np.diag([1., -1, 1]) @ _ry(-math.pi / 8) @ _rx(2.3561945)
LIGHTS = {"side": (_M3D @ _L0, _M3D @ _L1), "front": (_MFLAT @ _L0, _MFLAT @ _L1)}

# FaceInfo corner order (x, y, z: 0 = from, 1 = to) and BlockElement.uvsByFace defaults, per direction
CORNERS = {"down": ((0, 0, 1), (0, 0, 0), (1, 0, 0), (1, 0, 1)), "up": ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)),
           "north": ((1, 1, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0)), "south": ((0, 1, 1), (0, 0, 1), (1, 0, 1), (1, 1, 1)),
           "west": ((0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1)), "east": ((1, 1, 1), (1, 0, 1), (1, 0, 0), (1, 1, 0))}
NORMAL = {"down": (0, -1, 0), "up": (0, 1, 0), "north": (0, 0, -1), "south": (0, 0, 1), "west": (-1, 0, 0), "east": (1, 0, 0)}
def _uv_default(face, f, t):
    return {"down": (f[0], 16 - t[2], t[0], 16 - f[2]), "up": (f[0], f[2], t[0], t[2]),
            "north": (16 - t[0], 16 - t[1], 16 - f[0], 16 - f[1]), "south": (f[0], 16 - t[1], t[0], 16 - f[1]),
            "west": (f[2], 16 - t[1], t[2], 16 - f[1]), "east": (16 - t[2], 16 - t[1], 16 - f[2], 16 - f[1])}[face]


def _gui_matrix(display):
    """model px (0..16) -> slot px (x right, y down, z toward the viewer), and the 3x3 that turns normals"""
    g = display or {}
    rot = [math.radians(a) for a in (g.get("rotation") or [0, 0, 0])]
    tr = [min(5, max(-5, v * 0.0625)) for v in (g.get("translation") or [0, 0, 0])]   # ItemTransform.Deserializer
    sc = [min(4, max(-4, v)) for v in (g.get("scale") or [1, 1, 1])]
    R = _rx(rot[0]) @ _ry(rot[1]) @ _rz(rot[2])
    A = np.diag([16., -16, 16]) @ R @ np.diag(sc) / 16       # slot: scale(16) with y flipped (GuiGraphics.renderItem)
    off = np.diag([16., -16, 16]) @ (np.array(tr) - R @ np.diag(sc) @ np.full(3, 0.5)) + np.array([8., 8, 0])
    N = R @ np.diag([1 / v if v else 0 for v in sc])          # PoseStack normal matrix: rotation, inverse scale
    return A, off, N


def _quads_of(m, tex, tint=None):
    """[(corners 4x3 model px, uv 4x2 in 0..16, image, normal)] for every face of every element"""
    out = []
    for e in m.get("elements") or []:
        f, t = e.get("from"), e.get("to")
        if not f or not t: continue
        rot = e.get("rotation") or {}
        Rm, org, resc = None, np.array(rot.get("origin") or [8, 8, 8], float), None
        ang = float(rot.get("angle") or 0)
        if ang:
            ax = rot.get("axis", "y"); a = math.radians(ang)
            Rm = {"x": _rx, "y": _ry, "z": _rz}[ax](a)
            if rot.get("rescale"):
                k = 1 / math.cos(math.pi / 8) if abs(ang) == 22.5 else 1 / math.cos(math.pi / 4)
                resc = np.array([1 if ax == "x" else k, 1 if ax == "y" else k, 1 if ax == "z" else k])
        for face, spec in (e.get("faces") or {}).items():
            if face not in CORNERS or not isinstance(spec, dict): continue
            im = tex(spec.get("texture"))
            if im is None: continue
            if tint and spec.get("tintindex") in tint:
                import mcassets
                im = mcassets.tinted(im, tint[spec["tintindex"]])
            c = np.array([[(t if b else f)[i] for i, b in enumerate(cr)] for cr in CORNERS[face]], float)
            n = np.array(NORMAL[face], float)
            if Rm is not None:
                c = (c - org) @ Rm.T
                if resc is not None: c = c * resc
                c = c + org; n = Rm @ n
            u0, v0, u1, v1 = spec.get("uv") or _uv_default(face, f, t)
            r = (int(spec.get("rotation") or 0) // 90) % 4
            uv = []
            for i in range(4):   # BlockFaceUV.getU/getV with the shifted index
                j = (i + r) % 4
                uv.append((u0 if j in (0, 1) else u1, v0 if j in (0, 3) else v1))
            out.append((c, np.array(uv, float), im, n))
    return out


def _raster(tris, size, A, off, N, light, blend=None):
    """tris: [(pos 3x3 model px, uv 3x2 in 0..16, image array, normal)] -> RGBA image (z-buffer, nearest texel).
    blend: None = texels with partial alpha are blended (no render_type given), False = cutout (opaque at alpha >= 0.1),
    True = translucent"""
    k = size / 16
    l0, l1 = LIGHTS.get(light, LIGHTS["side"])
    col = np.zeros((size, size, 4), np.float64); dep = np.full((size, size), -np.inf)
    later = []
    ys, xs = np.mgrid[0:size, 0:size] + 0.5
    for p, uv, arr, n in tris:
        s = (p @ A.T + off) * np.array([k, k, 1])
        nn = N @ n; ln = np.linalg.norm(nn)
        if not ln or nn[2] <= 1e-9: continue                   # back face: the item sheets cull (entityCutout)
        nn = nn / ln
        sh = min(1.0, 0.6 * (max(0, l0 @ nn) + max(0, l1 @ nn)) + 0.4)
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = s
        area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if abs(area) < 1e-9: continue
        bx0, bx1 = max(0, int(math.floor(min(x0, x1, x2)))), min(size, int(math.ceil(max(x0, x1, x2))))
        by0, by1 = max(0, int(math.floor(min(y0, y1, y2)))), min(size, int(math.ceil(max(y0, y1, y2))))
        if bx0 >= bx1 or by0 >= by1: continue
        X, Y = xs[by0:by1, bx0:bx1], ys[by0:by1, bx0:bx1]
        w0 = ((x1 - X) * (y2 - Y) - (x2 - X) * (y1 - Y)) / area
        w1 = ((x2 - X) * (y0 - Y) - (x0 - X) * (y2 - Y)) / area
        w2 = 1 - w0 - w1
        ins = (w0 >= -1e-7) & (w1 >= -1e-7) & (w2 >= -1e-7)
        if not ins.any(): continue
        z = w0 * z0 + w1 * z1 + w2 * z2
        h, w = arr.shape[:2]
        u = w0 * uv[0, 0] + w1 * uv[1, 0] + w2 * uv[2, 0]; v = w0 * uv[0, 1] + w1 * uv[1, 1] + w2 * uv[2, 1]
        tx = np.clip(np.floor(u * w / 16).astype(int), 0, w - 1); ty = np.clip(np.floor(v * h / 16).astype(int), 0, h - 1)
        tex = arr[ty, tx].astype(np.float64)
        a = tex[..., 3] / 255
        rgb = np.round(tex[..., :3] * sh)
        ok = ins & (a >= 0.1)
        cut = ok if blend is False else ok & (a >= 0.999)      # full alpha draws like an opaque texel either way
        sub = dep[by0:by1, bx0:bx1]
        win = cut & (z > sub)
        sub[win] = z[win]
        c = col[by0:by1, bx0:bx1]
        c[win, :3] = rgb[win]; c[win, 3] = 255
        part = ok & ~cut
        if part.any(): later.append((float(z[part].mean()), by0, bx0, part, z, rgb, a))
    for _, by0, bx0, part, z, rgb, a in sorted(later, key=lambda q: q[0]):   # translucent: far to near, over the opaque
        h, w = part.shape
        sub = dep[by0:by0 + h, bx0:bx0 + w]; c = col[by0:by0 + h, bx0:bx0 + w]
        vis = part & (z > sub)
        al = a[vis][:, None]; da = c[vis, 3:4] / 255
        oa = al + da * (1 - al)
        c[vis, :3] = np.where(oa > 0, (rgb[vis] * al + c[vis, :3] * da * (1 - al)) / np.maximum(oa, 1e-9), 0)
        c[vis, 3:4] = np.round(oa * 255)
    out = Image.fromarray(np.clip(np.round(col), 0, 255).astype(np.uint8), "RGBA")
    return out if out.getbbox() else None


def render_model(m, tex, size=64, tint=None):
    if not m or not m.get("elements"): return None
    disp = (m.get("display") or {}).get("gui")
    A, off, N = _gui_matrix(disp if disp is not None else {})
    arrs, tris = {}, []
    for c, uv, im, n in _quads_of(m, tex, tint):
        a = arrs.setdefault(id(im), np.asarray(im.convert("RGBA")))
        tris.append((c[[0, 1, 2]], uv[[0, 1, 2]], a, n)); tris.append((c[[0, 2, 3]], uv[[0, 2, 3]], a, n))
    rt = (m.get("render_type") or "").split(":")[-1]
    blend = True if rt.startswith("translucent") else False if rt in ("solid", "cutout", "cutout_mipped") else None
    return _raster(tris, size, A, off, N, m.get("gui_light") or "side", blend)


def render(mid, rd, size=64):
    import mcassets
    A = mcassets.Assets(rd=rd)
    m = A.model(mid)
    return render_model(m, lambda r: A.texture(A.resolve(m, r)), size) if m else None


def render_obj(obj_path, tex_path, rd, flip_v=True, size=64, display=None, fit=True):
    """A Forge OBJ model: every triangle with its own uv, lit and placed like a block model (display defaults to
    block/block.json's gui transform). OBJ positions are in blocks; fit=True scales and centres the model in the slot
    (the item JSON that wraps an OBJ usually carries its own display, which this tool is not given)."""
    b, t = rd(obj_path), rd(tex_path)
    if not b or not t: return None
    im = Image.open(io.BytesIO(t)).convert("RGBA")
    import mcassets
    if (meta := rd(tex_path + ".mcmeta")):
        try:
            import json
            an = json.loads(meta).get("animation")
            if isinstance(an, dict): im = mcassets.first_frame(im, an)
        except ValueError: pass
    arr = np.asarray(im); W, H = im.size
    V, VT, F = [], [], []
    for line in b.decode("utf-8", "replace").splitlines():
        p = line.split()
        if not p: continue
        if p[0] == "v": V.append([float(x) * 16 for x in p[1:4]])
        elif p[0] == "vt": VT.append([float(x) for x in p[1:3]])
        elif p[0] == "f":
            idx = []
            for w in p[1:]:
                q = (w.split("/") + ["", ""])[:2]
                vi = int(q[0]); ti = int(q[1]) if q[1] else 0
                idx.append((vi - 1 if vi > 0 else len(V) + vi, (ti - 1 if ti > 0 else len(VT) + ti) if ti else None))
            for i in range(1, len(idx) - 1): F.append((idx[0], idx[i], idx[i + 1]))
    if not F: return None
    Vn = np.array(V)
    if fit:   # centre on the slot and fill it the way a full block does (16 px across before the gui scale)
        lo, hi = Vn.min(0), Vn.max(0); Vn = (Vn - (lo + hi) / 2) * (16 / max(hi - lo)) + 8
    A, off, N = _gui_matrix(display if display is not None else BLOCK_GUI)
    tris = []
    for tri in F:
        p = Vn[[q[0] for q in tri]]
        n = np.cross(p[1] - p[0], p[2] - p[0])
        if not np.linalg.norm(n): continue
        uv = np.array([(VT[q[1]][0], (1 - VT[q[1]][1]) if flip_v else VT[q[1]][1]) if q[1] is not None else (0, 0) for q in tri]) * 16
        tris.append((p, uv, arr, n))
    return _raster(tris, size, A, off, N, "side")   # faces turned away are culled there, as the game does
