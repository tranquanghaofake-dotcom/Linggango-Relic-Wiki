#!/usr/bin/env python3
"""Textures for the wiki's rooms, from vanilla 1.20.1 (Mojang; allowed for fan content with the footer disclaimer).
Writes build/src/scenes.js (const ROOMT = {name: base64 16x16 png}).

A room (app.js room(), style.game.css .room) is a wall of these blocks with a floor, lanterns and item frames that hold
real items from the wiki. Each room's blocks are chosen in CSS ([data-room=forge] …); this script only supplies textures.

Usage: python3 build/pack_audit/scenes.py <vanilla textures> [<xali> <goety> <ae2> [<linggango textures> <ftb theme>]]
  vanilla  assets/minecraft/textures of InventivetalentDev/minecraft-assets@1.20.1 (block/, item/)
  xali     clone of github.com/xalixilax/xali-s-Enhanced-Vanilla-16x @248ddbcb40 (main)       CC BY-NC 4.0
  goety    clone of github.com/Polarice3/Goety-2 @02adbe7491 (1.20)                            MIT
  ae2      clone of github.com/AppliedEnergistics/Applied-Energistics-2 @1c2f96e70c (forge/1.20.1)  textures CC BY-NC-SA 3.0
  linggango  unzipped LinggangoTextures.zip (CurseForge 1381088, file 8994067) by Misanthropy   used with the author's consent
  ftb        unzipped "Linggango FTB Quest Theme.zip" (CurseForge 1583288, file 8520681) by Misanthropy   same
Licences decide how each source is used (credits in the footer, template.html):
  - vanilla: Minecraft Usage Guidelines (fan content, with the disclaimer);
  - AE2 (CC BY-NC-SA 3.0) files are embedded byte for byte: no crop, no recolour (ShareAlike would put a changed
    texture under BY-NC-SA); Goety (MIT) pixels are unchanged too, re-encoded only to drop editor metadata;
    darkening and light are drawn by CSS on top;
  - Xali's variants (CC BY-NC 4.0, changes allowed with credit) are also arranged into a wall sheet with vanilla bricks.
  - Misanthropy's packs: sprites are cut out of their sheets (frames, bars, the gem knob, slots, lock, check).
Not used: Faithful 32x (licence allows it with credit, but 32 px textures next to 16 px item icons break the pixel
grid), and packs or mods whose textures are All Rights Reserved or NoDerivatives (Iron's Spellbooks, Terramity,
Ars Nouveau, Relics, L_Ender's Cataclysm, Dark/Modded Coffee GUI, Vanilla Experience+, Lanterns with Candles,
Brush & Juice, Fresh Waystones). Misanthropy's packs are used with the author's permission; Linggango Textures
includes textures from Coquet by jekaloic, credited with it.
"""
import base64, io, pathlib, sys
from PIL import Image

T = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(__file__).resolve().parents[1] / "src" / "scenes.js"

# walls, pillars and floors
BLOCKS = ["oak_planks", "spruce_planks", "dark_oak_planks", "stripped_oak_log", "stripped_spruce_log", "stripped_dark_oak_log",
          "stone_bricks", "deepslate_tiles", "deepslate_bricks",
          "polished_blackstone_bricks", "polished_blackstone", "blackstone",
          # furniture standing on the floor
          "bookshelf", "chiseled_bookshelf_occupied", "crafting_table_front", "barrel_side", "blast_furnace_front_on",
          "smithing_table_front", "enchanting_table_side", "lectern_front",
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
if len(sys.argv) > 6:
    L = pathlib.Path(sys.argv[5]) / "assets"
    F = pathlib.Path(sys.argv[6]) / "assets"
    # Linggango Textures: the Iron's Spellbooks GUI sheet holds the pack's slate-metal frames, bars, gem knob, slots,
    # lock and the silver/gold ornate frames; boxes found from the sheet's alpha
    ic = Image.open(L / "irons_spellbooks/textures/gui/icons.png").convert("RGBA")
    cut = {"lg_panel": (0, 43, 54, 62), "lg_slot_tan": (23, 85, 43, 105), "lg_slot_black": (66, 84, 88, 106),
           "lg_lock": (116, 88, 126, 102), "lg_frame_silver": (0, 106, 28, 135), "lg_frame_gold": (36, 107, 60, 135)}
    for k, b in cut.items():
        tx[k] = b64(ic.crop(b))
    # the long bars carry a knob in the middle: drop those columns and join the halves
    def splice(box, x0, x1):
        c = ic.crop(box); out = Image.new("RGBA", (c.width - (x1 - x0), c.height))
        out.paste(c.crop((0, 0, x0, c.height)), (0, 0)); out.paste(c.crop((x1, 0, c.width, c.height)), (x0, 0))
        return out.crop(out.getbbox())
    tx["lg_track"] = b64(splice((69, 40, 245, 57), 88, 98))
    tx["lg_fill"] = b64(splice((71, 60, 245, 76), 86, 96))
    # the gem knob sits on a cyan bar in the sheet: keep its grey/white pixels only
    kn = ic.crop((43, 21, 57, 34)); px = kn.load()
    for y in range(kn.height):
        for x in range(kn.width):
            r, g, b_, a = px[x, y]
            if a and b_ > r + 25: px[x, y] = (0, 0, 0, 0)
    tx["lg_knob"] = b64(kn.crop(kn.getbbox()))
    tx["lg_check"] = b64(Image.open(L / "minecraft/textures/gui/checkmark.png").convert("RGBA"))
    tx["lg_sep"] = b64(Image.open(L / "minecraft/textures/gui/header_separator.png").convert("RGBA"))
    # Linggango FTB Quests Theme: the quest book's background tile and its icons
    tx["ftb_squares"] = b64(Image.open(F / "ftblibrary/textures/gui/background_squares.png").convert("RGBA"))
    for n in ["alert", "chest", "info"]:
        tx["ftb_" + n] = b64(Image.open(F / f"ftblibrary/textures/icons/{n}.png").convert("RGBA"))
    for n in ["gear"]:
        tx["ftb_shape_" + n] = b64(Image.open(F / f"ftbquests/textures/shapes/{n}/outline.png").convert("RGBA"))

# more vanilla: light sources, furniture and decor, so rooms are not all lanterns; paintings; the GUI button
LIGHTS = ["block/soul_torch", "block/torch", "block/chain", "block/amethyst_cluster", "item/candle", "item/purple_candle", "item/writable_book"]
for n in LIGHTS:
    tx[n.split("/")[1]] = b64(tex(n))
# animated strips stay strips (CSS steps through them): flames and the sea lantern
for n in ["block/sea_lantern"]:
    tx[n.split("/")[1]] = b64(Image.open(T / f"{n}.png").convert("RGBA"))
for n in ["wanderer", "graham", "skull_and_roses", "burning_skull", "fighters"]:
    tx["painting_" + n] = b64(Image.open(T / f"painting/{n}.png").convert("RGBA"))
# the boss bar: pink (most bosses) and purple (the Wither), with the 10-notch overlay
bars = Image.open(T / "gui/bars.png").convert("RGBA")
for k, y in {"bar_pink_bg": 0, "bar_pink": 5, "bar_purple_bg": 50, "bar_purple": 55, "bar_notch10": 90}.items():
    tx[k] = b64(bars.crop((0, y, 182, y + 5)))
w = Image.open(T / "gui/widgets.png").convert("RGBA")
tx["btn"] = b64(w.crop((0, 66, 200, 86))); tx["btn_hover"] = b64(w.crop((0, 86, 200, 106)))
for n in ["glow", "sga_m", "sga_t", "glitter_4"]:
    tx["pt_" + n] = b64(Image.open(T / f"particle/{n}.png").convert("RGBA"))
# ---- relevant decor and the game's own effects (v39): fewer lamps, more things that belong to each page ----
def head(path, face, hat=None):
    # a mob head as a trophy: the skin's front face (plus its hat layer), doubled, with a dark rim
    sk = Image.open(T / f"{path}.png").convert("RGBA")
    f = sk.crop(face)
    if hat: f.alpha_composite(sk.crop(hat))
    f = f.resize((f.width * 2, f.height * 2), Image.NEAREST)
    out = Image.new("RGBA", (f.width + 2, f.height + 2), (12, 10, 14, 255)); out.alpha_composite(f, (1, 1))
    return out
tx["head_skeleton"] = b64(head("entity/skeleton/skeleton", (8, 8, 16, 16), (40, 8, 48, 16)))
tx["head_wither_skeleton"] = b64(head("entity/skeleton/wither_skeleton", (8, 8, 16, 16), (40, 8, 48, 16)))
for n in ["block/gold_block", "block/beacon", "block/spawner", "block/grindstone_side", "block/cartography_table_side3",
          "item/armor_stand", "item/compass_16", "item/spyglass"]:
    tx[n.split("/")[1]] = b64(tex(n))
tx["map_paper"] = b64(Image.open(T / "map/map_background.png").convert("RGBA"))
# the enchantment glint, scrolled over Mythic and Must-Have items like in game
tx["glint"] = b64(Image.open(T / "misc/enchanted_glint_item.png").convert("RGBA"))
# animated: soul fire (32 frames), the sweep attack (8 frames joined into a strip)
for n in ["block/soul_fire_0"]:
    tx[n.split("/")[1]] = b64(Image.open(T / f"{n}.png").convert("RGBA"))
sw = Image.new("RGBA", (32 * 8, 32))
for i in range(8): sw.alpha_composite(Image.open(T / f"particle/sweep_{i}.png").convert("RGBA"), (32 * i, 0))
tx["sweep"] = b64(sw)
# particles of each Act's world; the game tints the generic sprite for portals and ash, done here the same way
def tint(path, rgb):
    im = Image.open(T / f"{path}.png").convert("RGBA"); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b_, a = px[x, y]; px[x, y] = (r * rgb[0] // 255, g * rgb[1] // 255, b_ * rgb[2] // 255, a)
    return im
tx["pt_portal"] = b64(tint("particle/generic_3", (190, 90, 255)))
tx["pt_ash"] = b64(tint("particle/generic_6", (120, 110, 110)))
for n in ["lava", "cherry_3", "sculk_soul_3"]:
    tx["pt_" + n] = b64(Image.open(T / f"particle/{n}.png").convert("RGBA"))
if len(sys.argv) > 4:
    tx["goety_soul_candlestick"] = b64(Image.open(G / "soul_candlestick.png").convert("RGBA"))
    for n in ["block/controller_powered", "block/controller_lights"]:
        tx["ae2_" + n.split("/")[-1]] = raw(A / f"{n}.png")
OUT.write_text("/* generated by build/pack_audit/scenes.py from vanilla 1.20.1 textures; do not edit */\nconst ROOMT=" +
               "{" + ",".join(f'"{k}":"{v}"' for k, v in tx.items()) + "};\n", encoding="utf-8")
print(OUT, len(tx), "textures,", sum(len(v) for v in tx.values()), "bytes of base64")
