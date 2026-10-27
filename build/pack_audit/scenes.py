#!/usr/bin/env python3
"""Section scenes for Equipment and the Build planner, composed from vanilla 1.20.1 textures (Mojang; allowed for
fan content with the footer disclaimer). Writes build/src/scenes.js (const SCENES = {name: base64 png}).

Usage: python3 build/pack_audit/scenes.py <textures dir>
The textures dir is assets/minecraft/textures of InventivetalentDev/minecraft-assets@1.20.1 (block/, item/).
Each scene is 12 x 4 blocks (192 x 64 px) at 1 px per texel, shown scaled with image-rendering: pixelated.
"""
import base64, io, math, pathlib, sys
from PIL import Image

T = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(__file__).resolve().parents[1] / "src" / "scenes.js"
W, H = 12, 4

def tex(name):
    im = Image.open(T / f"{name}.png").convert("RGBA")
    return im.crop((0, 0, 16, 16))  # animated textures are strips: first frame

def wall(img, pick, k=.58):
    # the backdrop is darkened so the objects in front read first, as in a dim room
    for y in range(H):
        for x in range(W):
            t = tex(pick(x, y)); px = t.load()
            for i in range(16):
                for j in range(16):
                    p = px[i, j]; px[i, j] = (int(p[0] * k), int(p[1] * k), int(p[2] * k), p[3])
            img.alpha_composite(t, (x * 16, y * 16))

def put(img, name, x, y, dx=0, dy=0):
    img.alpha_composite(tex(name), (x * 16 + dx, y * 16 + dy))

def framed(img, item, x, y):
    # an item frame hung on the wall: the frame's wood border, then the item on it
    put(img, "block/item_frame", x, y)
    put(img, item, x, y)

def anvil(img, x, y):
    # anvil profile (side view) cut from the anvil texture: wide face, narrow waist, base
    body = tex("block/anvil")
    mask = Image.new("L", (16, 16), 0)
    rows = {0: (0, 16), 1: (0, 16), 2: (0, 16), 3: (1, 15), 4: (4, 12), 5: (5, 11), 6: (5, 11), 7: (5, 11),
            8: (5, 11), 9: (5, 11), 10: (4, 12), 11: (3, 13), 12: (2, 14), 13: (2, 14)}
    for r, (a, b) in rows.items():
        for c in range(a, b):
            mask.putpixel((c, r + 2), 255)
    lit = body.point(lambda v: min(255, int(v * 1.7)))
    shaded = Image.composite(lit, Image.new("RGBA", (16, 16)), mask)
    # 1-texel black outline so the iron reads against the dark wall
    out = Image.new("RGBA", (16, 16)); op = out.load()
    for r in range(16):
        for c in range(16):
            if not mask.getpixel((c, r)) and any(0 <= c + a < 16 and 0 <= r + b < 16 and mask.getpixel((c + a, r + b)) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                op[c, r] = (10, 10, 12, 255)
    img.alpha_composite(out, (x * 16, y * 16))
    img.alpha_composite(shaded, (x * 16, y * 16))

def light(img, cx, cy, r, rgb, k):
    # warm or cold glow, added to the pixels (keeps the pixel grid: one value per texel)
    px = img.load()
    for yy in range(img.height):
        for xx in range(img.width):
            d = math.hypot(xx - cx, yy - cy)
            if d < r:
                f = (1 - d / r) ** 2 * k
                p = px[xx, yy]
                px[xx, yy] = tuple(min(255, int(p[i] + rgb[i] * f)) for i in range(3)) + (p[3],)

def vignette(img, k=.55):
    px = img.load()
    for yy in range(img.height):
        for xx in range(img.width):
            dx = (xx - img.width / 2) / (img.width / 2); dy = (yy - img.height / 2) / (img.height / 2)
            f = 1 - k * min(1, (dx * dx * .6 + dy * dy * .8))
            p = px[xx, yy]
            px[xx, yy] = (int(p[0] * f), int(p[1] * f), int(p[2] * f), p[3])

def forge():
    im = Image.new("RGBA", (W * 16, H * 16))
    wall(im, lambda x, y: "block/deepslate_tiles" if y == 3 else ("block/cracked_stone_bricks" if (x * 7 + y * 3) % 5 == 0 else "block/stone_bricks"))
    put(im, "block/blast_furnace_front_on", 1, 2)
    put(im, "block/blast_furnace_side", 1, 1)
    put(im, "block/smithing_table_front", 3, 2)
    anvil(im, 4, 2)
    for i, it in enumerate(["item/iron_sword", "item/golden_sword", "item/diamond_sword", "item/netherite_sword", "item/netherite_axe", "item/bow"]):
        framed(im, it, 6 + i, 1)
    put(im, "item/lantern", 6, 0, dy=4)
    put(im, "item/lantern", 11, 0, dy=4)
    light(im, 24, 44, 46, (255, 140, 40), .55)
    light(im, 104, 10, 26, (255, 200, 110), .35)
    light(im, 184, 10, 26, (255, 200, 110), .35)
    vignette(im)
    return im

def armory():
    im = Image.new("RGBA", (W * 16, H * 16))
    wall(im, lambda x, y: "block/dark_oak_planks" if y == 3 else ("block/stripped_spruce_log" if x in (0, 5, 11) else "block/spruce_planks"))
    put(im, "block/crafting_table_front", 1, 2)
    put(im, "block/barrel_side", 2, 2)
    put(im, "block/barrel_top", 2, 1)
    put(im, "block/bookshelf", 3, 2)
    put(im, "block/chiseled_bookshelf_occupied", 4, 2)
    put(im, "item/armor_stand", 3, 1)
    for i, it in enumerate(["item/totem_of_undying", "item/heart_of_the_sea", "item/nether_star", "item/ender_eye", "item/amethyst_shard"]):
        framed(im, it, 6 + i, 1)
    for i, it in enumerate(["item/emerald", "item/elytra", "item/iron_helmet", "item/diamond_chestplate", "item/netherite_helmet"]):
        framed(im, it, 6 + i, 2)
    put(im, "item/lantern", 5, 0, dy=4)
    put(im, "item/lantern", 11, 0, dy=4)
    light(im, 88, 10, 40, (255, 190, 100), .4)
    light(im, 184, 10, 34, (255, 190, 100), .35)
    vignette(im)
    return im

def b64(im):
    b = io.BytesIO(); im.save(b, "PNG", optimize=True); return base64.b64encode(b.getvalue()).decode()

scenes = {"gear": b64(forge()), "build": b64(armory())}
OUT.write_text("/* generated by build/pack_audit/scenes.py from vanilla 1.20.1 textures; do not edit */\nconst SCENES=" +
               "{" + ",".join(f'"{k}":"{v}"' for k, v in scenes.items()) + "};\n", encoding="utf-8")
print(OUT, {k: len(v) for k, v in scenes.items()})
