#!/usr/bin/env python3
"""Minecraft assets read the way the game resolves them, shared by the icon tools (name_icons.py, gear/icons.py, the
weapon and armor renders) instead of each keeping its own jar index and model walk.

  A = Assets(["pack/src/overrides/kubejs", "pack/mods/res.zip", "pack/mods/a.jar", ..., "client-1.20.1.jar"])
  A.read("assets/minecraft/models/block/furnace.json")   # bytes or None; the first source that has the file wins,
                                                         # so list them like the game stacks resource packs: top first
  m = A.model("minecraft:item/furnace")                  # parent chain merged as vanilla BlockModel does
  A.texture("minecraft:block/furnace_front")             # RGBA, the frame the game shows first (.mcmeta aware)
  A.icon("minecraft:furnace")                            # the inventory picture: flat layers, or block_render's 3D view
  png_b64(im)                                            # smallest lossless PNG of an image, base64

Merge rules (vanilla 1.20.1 BlockModel / ItemTransforms): textures child over parent; elements are the nearest model's
whole list; display per context, the nearest model that defines that context; gui_light the nearest that sets it
(default "side"), and Forge's render_type the same way. A chain that reaches builtin/generated is a flat item (layer0..n); builtin/entity is drawn by code
(chests, shields, banners) and has no picture here.
Animated textures: frame size from the .mcmeta (width/height, else min(w, h) square), frames laid out left to right
then top to bottom, the first entry of "frames" first (it is not always index 0). Without a .mcmeta a tall texture is
not an animation and is returned whole."""
import base64, io, json, os, zipfile
from PIL import Image


class Assets:
    def __init__(s, sources=(), rd=None):
        """sources: directories, .jar / .zip files, or both; rd: an extra reader function path -> bytes|None, asked last"""
        s.src, s.extra, s._m, s._t = [], rd, {}, {}
        for p in sources:
            if os.path.isdir(p): s.src.append(("d", p))
            else:
                try: z = zipfile.ZipFile(p)
                except (OSError, zipfile.BadZipFile): continue
                s.src.append(("z", (z, set(z.namelist()))))

    def read(s, path):
        for k, v in s.src:
            if k == "d":
                f = os.path.join(v, path)
                if os.path.isfile(f):
                    with open(f, "rb") as fh: return fh.read()
            elif path in v[1]: return v[0].read(path)
        return s.extra(path) if s.extra else None

    def json(s, path):
        b = s.read(path)
        if b is None: return None
        try: return json.loads(b.decode("utf-8", "replace"))
        except ValueError: return None

    # ---- models ----
    def model(s, ref, _d=0):
        """merged model dict {textures, elements, display, gui_light, render_type, generated, entity, loader, raw,
        chain} or None"""
        ns, p = rl(ref)
        key = f"{ns}:{p}"
        if key not in s._m:
            s._m[key] = None   # a parent loop ends here instead of recursing
            raw = s.json(f"assets/{ns}/models/{p}.json")
            s._m[key] = s.merge(raw, key, _d) if isinstance(raw, dict) and _d <= 16 else None
        return s._m[key]

    def merge(s, m, key="inline", _d=0):
        """one model JSON (a file, or an inline model such as a forge:separate_transforms perspective) over its parents"""
        out = {"textures": {}, "elements": None, "display": {}, "gui_light": None, "generated": False, "entity": False,
               "loader": None, "render_type": None, "raw": m, "chain": []}
        par = m.get("parent")
        if isinstance(par, str):
            pn = rl(par)
            if pn == ("minecraft", "builtin/generated"): out["generated"] = True
            elif pn == ("minecraft", "builtin/entity"): out["entity"] = True
            else:
                pm = s.model(par, _d + 1)
                if pm:
                    out.update({k: (dict(v) if isinstance(v, dict) else v) for k, v in pm.items() if k not in ("raw", "loader")})
                    out["chain"] = list(pm["chain"])
        out["chain"].insert(0, key)
        out["textures"].update(m.get("textures") or {})
        if m.get("elements") is not None: out["elements"] = m["elements"]
        for ctx, t in (m.get("display") or {}).items(): out["display"][ctx] = t
        if m.get("gui_light"): out["gui_light"] = m["gui_light"]
        if m.get("render_type"): out["render_type"] = m["render_type"]   # Forge 1.20.1: solid / cutout / translucent
        if m.get("loader"): out["loader"] = m["loader"]               # forge:obj, forge:separate_transforms, ...
        return out

    def resolve(s, m, ref):
        """'#side' -> 'ns:block/x' through the model's texture variables (None when it ends nowhere)"""
        seen = 0
        while isinstance(ref, str) and ref.startswith("#") and seen < 16:
            ref = m["textures"].get(ref[1:]); seen += 1
        return ref if isinstance(ref, str) and not ref.startswith("#") else None

    # ---- textures ----
    def texture(s, ref):
        if ref is None: return None
        ns, p = rl(ref)
        key = f"{ns}:{p}"
        if key not in s._t:
            b = s.read(f"assets/{ns}/textures/{p}.png")
            im = None
            if b:
                try:
                    im = Image.open(io.BytesIO(b)).convert("RGBA")
                    meta = s.json(f"assets/{ns}/textures/{p}.png.mcmeta")
                    if isinstance(meta, dict) and isinstance(meta.get("animation"), dict): im = first_frame(im, meta["animation"])
                except (OSError, ValueError): im = None
            s._t[key] = im
        return s._t[key]

    # ---- the inventory picture ----
    def icon(s, item_id, size=64, tint=None):
        """what the inventory slot shows: flat items at their own resolution (layers stacked, as the GUI draws
        item/generated face-on at full light), block models through block_render at `size` px for a 16 px slot.
        tint {tintindex: 0xRRGGBB}: the ItemColors the game multiplies in (layerN has tintindex N): spawn eggs take
        their two colours from SpawnEggItem's constructor, leather from its dye, grass and leaves from the biome
        default. Without it tinted layers keep their grey base texture."""
        ns, n = rl(item_id)
        return s.draw(s.model(f"{ns}:item/{n}"), size, tint=tint)

    def draw(s, m, size=64, _d=0, tint=None):
        if m is None or _d > 4: return None
        if (m["loader"] or "").endswith("separate_transforms"):   # the GUI shows the "gui" perspective, else "base"
            g = (m["raw"].get("perspectives") or {}).get("gui") or m["raw"].get("base")
            g = s.model(g) if isinstance(g, str) else s.merge(g) if isinstance(g, dict) else None
            return s.draw(g, size, _d + 1, tint)
        if m["generated"]:
            im = None
            for i in range(16):
                t = s.texture(s.resolve(m, m["textures"].get(f"layer{i}")))
                if t is None: break
                if tint and i in tint: t = tinted(t, tint[i])
                if im is None: im = t.copy()
                else: im.alpha_composite(t if t.size == im.size else t.resize(im.size, Image.NEAREST))
            return im
        if m["elements"]:
            import block_render
            return block_render.render_model(m, lambda r: s.texture(s.resolve(m, r)), size, tint)
        return None


def rl(ref):
    """'ns:path' / 'path' -> (ns, path) the way ResourceLocation reads it"""
    ref = ref.lstrip("#") if isinstance(ref, str) else ""
    ns, p = ref.split(":", 1) if ":" in ref else ("minecraft", ref)
    return ns, p


def first_frame(im, anim):
    W, H = im.size
    fw, fh = anim.get("width"), anim.get("height")
    if fw is None and fh is None: fw = fh = min(W, H)
    elif fw is None: fw = W
    elif fh is None: fh = H
    fr = anim.get("frames") or [0]
    i = fr[0]["index"] if isinstance(fr[0], dict) else fr[0]
    cols = max(1, W // fw)
    x, y = (i % cols) * fw, (i // cols) * fh
    if x + fw > W or y + fh > H: x = y = 0
    return im.crop((x, y, x + fw, y + fh))


def tinted(im, rgb):
    """texel × colour, as the item shader multiplies the vertex colour (alpha kept)"""
    r, g, b = (rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255
    R, G, B, A = im.split()
    return Image.merge("RGBA", (R.point(lambda v: v * r // 255), G.point(lambda v: v * g // 255), B.point(lambda v: v * b // 255), A))


def png_bytes(im):
    """the smallest lossless PNG of `im`: RGBA, or an indexed image with a per-entry alpha table when it has 256 colours
    or fewer (most pixel art), each checked to decode to the same pixels"""
    import numpy as np
    im = im.convert("RGBA")
    best = io.BytesIO(); im.save(best, "PNG", optimize=True); best = best.getvalue()
    px = np.asarray(im).reshape(-1, 4)
    cols, inv = np.unique(px, axis=0, return_inverse=True)
    if len(cols) <= 256:
        P = Image.fromarray(inv.reshape(im.size[1], im.size[0]).astype(np.uint8), "P")
        P.putpalette(cols[:, :3].ravel().tolist())
        o = io.BytesIO(); P.save(o, "PNG", optimize=True, transparency=bytes(cols[:, 3].tolist())); o = o.getvalue()
        if len(o) < len(best) and Image.open(io.BytesIO(o)).convert("RGBA").tobytes() == im.tobytes(): best = o
    return best


def png_b64(im): return base64.b64encode(png_bytes(im)).decode()


def repack_b64(b64):
    """an embedded base64 PNG re-encoded by png_bytes when that is smaller and decodes to the same pixels; anything
    else (animated, 16-bit, not a PNG) comes back unchanged"""
    try:
        raw = base64.b64decode(b64)
        im = Image.open(io.BytesIO(raw))
        if getattr(im, "n_frames", 1) > 1 or im.mode in ("I", "I;16", "I;16B", "F"): return b64
        a = im.convert("RGBA")
        o = png_bytes(a)
        if len(o) >= len(raw) or Image.open(io.BytesIO(o)).convert("RGBA").tobytes() != a.tobytes(): return b64
        return base64.b64encode(o).decode()
    except Exception:
        return b64


if __name__ == "__main__":
    # python3 -I mcassets.py --repack FILE [--skip ns1,ns2]: losslessly recompress every embedded base64 PNG in a JSON
    # or JS source in place ("iVBORw0KGgo..." strings, with or without a data: prefix); --skip leaves the icons of those
    # namespaces untouched when FILE is a JSON object keyed by item id. Prints bytes before and after.
    import re, sys
    a = sys.argv[1:]
    if not a or a[0] != "--repack": sys.exit(__doc__)
    skip = set()
    if "--skip" in a: i = a.index("--skip"); skip = set(a[i + 1].split(",")); del a[i:i + 2]
    pat = re.compile(r'("?)([a-z0-9_.-]+:[a-z0-9_/.-]+)?("?\s*:\s*"(?:data:image/png;base64,)?)?(iVBORw0KGgo[A-Za-z0-9+/=]+)')
    for f in a[1:]:
        t = open(f, encoding="utf-8").read(); n0 = len(t)
        def sub(mm):
            if mm.group(2) and mm.group(2).split(":")[0] in skip: return mm.group(0)
            return mm.group(0)[:mm.start(4) - mm.start(0)] + repack_b64(mm.group(4))
        t = pat.sub(sub, t)
        open(f, "w", encoding="utf-8").write(t)
        print(f, n0, "->", len(t), "characters")
