#!/usr/bin/env python3
"""Textures for the wiki's rooms, from vanilla 1.20.1 (Mojang; allowed for fan content with the footer disclaimer).
Writes build/src/scenes.js (const ROOMT = {name: base64 16x16 png}).

A room (app.js room(), style.game.css .room) is a wall of these blocks with a floor, lanterns and item frames that hold
real items from the wiki. Each room's blocks are chosen in CSS ([data-room=forge] …); this script only supplies textures.

Usage: python3 build/pack_audit/scenes.py <vanilla textures> [<xali> <goety> <ae2>]
  vanilla  assets/minecraft/textures of InventivetalentDev/minecraft-assets@1.20.1 (block/, item/)
  xali     clone of github.com/xalixilax/xali-s-Enhanced-Vanilla-16x @248ddbcb40 (main)       CC BY-NC 4.0
  goety    clone of github.com/Polarice3/Goety-2 @02adbe7491 (1.20)                            MIT
  ae2      clone of github.com/AppliedEnergistics/Applied-Energistics-2 @1c2f96e70c (forge/1.20.1)  textures CC BY-NC-SA 3.0
Licences decide how each source is used (credits in the footer, template.html):
  - vanilla: Minecraft Usage Guidelines (fan content, with the disclaimer);
  - AE2 (CC BY-NC-SA 3.0) files are embedded byte for byte: no crop, no recolour (ShareAlike would put a changed
    texture under BY-NC-SA); Goety (MIT) pixels are unchanged too, re-encoded only to drop editor metadata;
    darkening and light are drawn by CSS on top;
  - Xali's variants (CC BY-NC 4.0, changes allowed with credit) are also arranged into a wall sheet with vanilla bricks.
Not used: Faithful 32x (licence allows it with credit, but 32 px textures next to 16 px item icons break the pixel
grid), the Linggango resource packs (LICENSE.txt says All Rights Reserved), and mods whose textures are All Rights
Reserved or NoDerivatives (Iron's Spellbooks, Terramity, Ars Nouveau, Relics, L_Ender's Cataclysm).
"""
import base64, io, pathlib, sys
from PIL import Image

T = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(__file__).resolve().parents[1] / "src" / "scenes.js"

# walls, pillars and floors
BLOCKS = ["oak_planks", "spruce_planks", "dark_oak_planks", "stripped_oak_log", "stripped_spruce_log", "stripped_dark_oak_log",
          "stone_bricks", "cracked_stone_bricks", "mossy_stone_bricks", "deepslate_tiles", "deepslate_bricks",
          "polished_blackstone_bricks", "cracked_polished_blackstone_bricks", "polished_blackstone", "blackstone",
          "crying_obsidian", "obsidian", "nether_bricks", "end_stone_bricks", "purpur_block",
          # furniture standing on the floor
          "bookshelf", "chiseled_bookshelf_occupied", "crafting_table_front", "barrel_side", "blast_furnace_front_on",
          "smithing_table_front", "enchanting_table_side", "lectern_front", "cobweb",
          # the frames items hang in
          "item_frame", "glow_item_frame"]
ITEMS = ["lantern", "soul_lantern"]


def tex(path):
    im = Image.open(T / f"{path}.png").convert("RGBA")
    return im.crop((0, 0, 16, 16))  # animated textures are strips: first frame


def anvil():
    # anvil profile (side view) cut from the anvil texture: wide face, narrow waist, base; 1-texel black outline
    body = tex("block/anvil")
    mask = Image.new("L", (16, 16), 0)
    rows = {0: (0, 16), 1: (0, 16), 2: (0, 16), 3: (1, 15), 4: (4, 12), 5: (5, 11), 6: (5, 11), 7: (5, 11),
            8: (5, 11), 9: (5, 11), 10: (4, 12), 11: (3, 13), 12: (2, 14), 13: (2, 14)}
    for r, (a, b) in rows.items():
        for c in range(a, b):
            mask.putpixel((c, r + 2), 255)
    lit = body.point(lambda v: min(255, int(v * 1.7)))
    shaded = Image.composite(lit, Image.new("RGBA", (16, 16)), mask)
    out = Image.new("RGBA", (16, 16)); op = out.load()
    for r in range(16):
        for c in range(16):
            if not mask.getpixel((c, r)) and any(0 <= c + a < 16 and 0 <= r + b < 16 and mask.getpixel((c + a, r + b))
                                                 for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                op[c, r] = (10, 10, 12, 255)
    out.alpha_composite(shaded)
    return out


def b64(im):
    b = io.BytesIO(); im.save(b, "PNG", optimize=True); return base64.b64encode(b.getvalue()).decode()


def raw(path):
    # third-party textures go in unchanged: the file's own bytes
    return base64.b64encode(pathlib.Path(path).read_bytes()).decode()


def sheet(tiles, cols, rows, seed):
    # a wall of mixed variants (fixed pattern, so the build is reproducible): breaks the grid of one repeated block
    im = Image.new("RGBA", (cols * 16, rows * 16))
    for y in range(rows):
        for x in range(cols):
            k = (x * 7 + y * 13 + seed) % len(tiles)
            im.alpha_composite(tiles[k], (x * 16, y * 16))
    return im


tx = {n: b64(tex("block/" + n)) for n in BLOCKS}
tx.update({n: b64(tex("item/" + n)) for n in ITEMS})
tx["anvil"] = b64(anvil())
if len(sys.argv) > 4:
    X = pathlib.Path(sys.argv[2]) / "src/assets/minecraft/textures/block"
    G = pathlib.Path(sys.argv[3]) / "src/main/resources/assets/goety/textures/block"
    A = pathlib.Path(sys.argv[4]) / "src/main/resources/assets/ae2/textures"
    # Xali's Enhanced Vanilla: book and lectern variants, and its five stone-brick variants mixed with vanilla
    # cracked and mossy bricks into one forge wall (4 x 3 blocks)
    for n in ["bookshelf/bookshelf_1", "bookshelf/bookshelf_7", "bookshelf/bookshelf_12", "lectern/lectern_front_2"]:
        tx["xali_" + n.split("/")[1]] = raw(X / f"{n}.png")
    bricks = [Image.open(X / f"stone_bricks/{i}.png").convert("RGBA") for i in range(1, 6)]
    bricks += [tex("block/stone_bricks"), tex("block/cracked_stone_bricks"), tex("block/stone_bricks"), tex("block/mossy_stone_bricks")]
    tx["forge_wall"] = b64(sheet(bricks, 4, 3, 2))
    # Goety: its crypt and haunted wood, the cursed cage and haunted bookshelf (the ritual setup the Mechanics page explains)
    for n in ["crypt_bricks", "crypt_tiles", "haunted_planks", "stripped_haunted_log", "haunted_bookshelf", "cursed_cage", "shade_stone_bricks"]:
        # MIT allows any change; the files carry ~25 KB of editor metadata, so they are re-encoded with identical pixels
        im = Image.open(G / f"{n}.png").convert("RGBA"); tx["goety_" + n] = b64(im)
    # AE2: sky stone, the controller and drive, fluix, and the storage cells the AE2 section compares
    for n in ["block/sky_stone_brick", "block/smooth_sky_stone_block", "block/controller", "block/drive/drive_front", "block/fluix_block",
              "item/item_storage_cell_1k", "item/item_storage_cell_4k", "item/item_storage_cell_16k", "item/item_storage_cell_64k", "item/item_storage_cell_256k"]:
        tx["ae2_" + n.split("/")[-1]] = raw(A / f"{n}.png")
OUT.write_text("/* generated by build/pack_audit/scenes.py from vanilla 1.20.1 textures; do not edit */\nconst ROOMT=" +
               "{" + ",".join(f'"{k}":"{v}"' for k, v in tx.items()) + "};\n", encoding="utf-8")
print(OUT, len(tx), "textures,", sum(len(v) for v in tx.values()), "bytes of base64")
