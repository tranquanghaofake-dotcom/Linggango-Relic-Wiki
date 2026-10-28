#!/usr/bin/env python3
"""UI icons and Act particles for the wiki, from vanilla 1.20.1 and the asset library (workspace branch, assets/).
Writes build/src/uiicons.js: Object.assign(ROOMT,{...}), so each texture is a CSS variable --rt-<name> like the room textures.
Replaces the emoji and text glyphs the pages used as icons (lock, star, check, attack types, armor slots, sources), and gives
four Acts' air a particle from the pack's own mods instead of a vanilla stand-in.

Usage: python3 build/pack_audit/uiicons.py <vanilla textures> <asset library>
  vanilla  assets/minecraft/textures of InventivetalentDev/minecraft-assets@1.20.1 (af628ec0e7)   Minecraft Usage Guidelines
  library  assets/lib of the workspace branch (see assets/catalog.csv for each file's source, version and licence)
    goety/…/particle/*            Goety - The Dark Arts (Polarice3), jar in Linggango 6.6.6hf      MIT
    hexerei/…/particle/*          Hexerei (JoeFoxe), jar in Linggango 6.6.6hf                       MIT (mods.toml) / LGPL-3.0 (Modrinth); credited
Every library file is 16 px (or an 8 px particle) and goes in byte for byte. rf_0 … rf_6: rarity frames from rarity_frames.py.
"""
import base64, io, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import rarity_frames   # own work: one frame per rarity (rf_0 … rf_6, big rfb_0 … rfb_6)
import slot_badges     # own work: slot and ring-requirement badges (sb_*)
import mob_faces       # mob faces cut from vanilla entity textures (mf_*)
V, L = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
OUT = pathlib.Path(__file__).resolve().parents[1] / "src" / "uiicons.js"
VANILLA = {  # key: item texture
    "ui_sword": "item/iron_sword", "ui_bow": "item/bow", "ui_arrow": "item/arrow", "ui_fire_charge": "item/fire_charge",
    "ui_bone": "item/bone", "ui_feather": "item/feather", "ui_glowstone": "item/glowstone_dust", "ui_star": "item/nether_star",
    "ui_helmet": "item/iron_helmet", "ui_chestplate": "item/iron_chestplate", "ui_leggings": "item/iron_leggings", "ui_boots": "item/iron_boots",
}
# the page background: a deepslate cave wall with ore veins (app.js paints it once into a canvas)
CAVE = ["deepslate", "cobbled_deepslate", "tuff", "deepslate_coal_ore", "deepslate_iron_ore", "deepslate_copper_ore",
        "deepslate_gold_ore", "deepslate_redstone_ore", "deepslate_lapis_ore", "deepslate_diamond_ore", "deepslate_emerald_ore",
        "smooth_basalt", "calcite", "amethyst_block"]
VANILLA.update({"bg_" + b: "block/" + b for b in CAVE})
# element and damage-type signs, and the pictures of where a curio comes from (Stats, How to get it)
VANILLA.update({"el_fire": "item/blaze_powder", "el_ice": "item/snowball", "el_water": "item/heart_of_the_sea", "el_lightning": "block/lightning_rod",
    "el_dark": "block/wither_rose", "el_holy": "item/glowstone_dust", "el_blood": "item/redstone", "el_ender": "item/ender_pearl", "el_nature": "item/spider_eye",
    "dt_pierce": "item/trident", "dt_blunt": "item/iron_axe", "dt_magic": "item/enchanted_book", "lt_brush": "item/brush", "lt_sand": "block/suspicious_sand_0",
    "lt_emerald": "item/emerald", "lt_bundle": "item/bundle"})
# the rooms at the top of the main pages (rooms.js): blocks drawn into a canvas at 16 px per block, lit by their lights.
# Animated ones (lava, fire, lanterns' glow …) keep their whole frame strip; rooms.js plays it.
ROOM_BLOCKS = ["lava_still", "fire_0", "soul_fire_0", "iron_bars", "glass", "cobweb", "oak_log", "dark_oak_log", "spruce_log",
    "stripped_oak_log", "stripped_spruce_log", "stripped_dark_oak_log", "stone_bricks", "cracked_stone_bricks", "mossy_stone_bricks",
    "chiseled_stone_bricks", "polished_deepslate", "deepslate_tiles", "cracked_deepslate_tiles", "deepslate_bricks", "polished_blackstone_bricks",
    "cracked_polished_blackstone_bricks", "chiseled_polished_blackstone", "polished_blackstone", "polished_basalt_side", "soul_soil", "soul_sand",
    "blast_furnace_front_on", "blast_furnace_side", "furnace_front_on", "anvil", "smithing_table_front", "grindstone_side", "enchanting_table_side",
    "crafting_table_front", "barrel_side", "gold_block", "beacon", "amethyst_cluster", "sea_lantern", "oak_planks", "spruce_planks", "dark_oak_planks",
    "bookshelf", "chiseled_bookshelf_occupied", "torch", "soul_torch", "spawner", "cauldron_side", "brewing_stand", "red_wool", "purple_wool",
    "obsidian", "crying_obsidian", "lectern_sides", "campfire_fire", "soul_campfire_fire", "campfire_log_lit", "magma", "nether_bricks", "amethyst_block",
    "budding_amethyst", "glowstone", "redstone_lamp_on", "end_rod"]
ROOM_ITEMS = ["netherite_helmet", "netherite_chestplate", "netherite_leggings", "netherite_boots", "golden_helmet", "golden_chestplate", "lantern", "soul_lantern", "chain", "candle", "purple_candle", "enchanted_book", "flower_pot", "iron_helmet", "iron_chestplate",
    "iron_leggings", "iron_boots", "diamond_helmet", "diamond_chestplate", "diamond_leggings", "diamond_boots", "netherite_sword", "diamond_sword",
    "iron_sword", "bow", "crossbow", "shield", "book", "writable_book", "potion", "experience_bottle", "skeleton_skull", "item_frame", "glow_item_frame"]
VANILLA.update({"rm_" + b: "block/" + b for b in ROOM_BLOCKS})
VANILLA.update({"ri_" + b: "item/" + b for b in ROOM_ITEMS if (V / f"item/{b}.png").exists()})
LIBRARY = {  # key: file in the library
    "pt_goety_fire": "goety/assets/goety/textures/particle/big_fire_4.png",
    "pt_goety_soul": "goety/assets/goety/textures/particle/big_soul_fire_drop_3.png",
    "pt_goety_end": "goety/assets/goety/textures/particle/end_fire_3.png",
    "pt_hexerei_star": "hexerei/assets/hexerei/textures/particle/star_brush_3.png",
    # Goety's crypt for the Bosses and Mechanics rooms
    "rg_crypt_bricks": "goety/assets/goety/textures/block/crypt_bricks.png", "rg_crypt_pillar": "goety/assets/goety/textures/block/crypt_pillar.png",
    "rg_crypt_bookshelf": "goety/assets/goety/textures/block/crypt_bookshelf.png", "rg_crypt_plinth": "goety/assets/goety/textures/block/crypt_plinth.png",
    "rg_crypt_tiles": "goety/assets/goety/textures/block/crypt_tiles.png", "rg_crypt_chiseled": "goety/assets/goety/textures/block/crypt_stone_chiseled.png",
    "rg_haunted_bookshelf": "goety/assets/goety/textures/block/haunted_bookshelf.png", "rg_brazier_soul": "goety/assets/goety/textures/block/brazier_soul_fire.png",
    "rg_brazier": "goety/assets/goety/textures/block/brazier_fire.png", "rg_soul_candlestick": "goety/assets/goety/textures/block/soul_candlestick.png",
}
b64 = lambda p: base64.b64encode(p.read_bytes()).decode()
items = {k: b64(V / f"{v}.png") for k, v in VANILLA.items()}
items.update({k: b64(L / v) for k, v in LIBRARY.items()})
def png(im):
    buf = io.BytesIO(); im.save(buf, "PNG", optimize=True); return base64.b64encode(buf.getvalue()).decode()
for r, im in enumerate(rarity_frames.frames()): items[f"rf_{r}"] = png(im)
for r, im in enumerate(rarity_frames.frames(64)): items[f"rfb_{r}"] = png(im)
for k, im in slot_badges.badges().items(): items[f"sb_{k}"] = png(im)
for k, im in mob_faces.faces(V).items(): items["mf_" + k.lower().replace(" ", "_")] = png(im)
OUT.write_text("Object.assign(ROOMT," + "{" + ",".join(f'"{k}":"{v}"' for k, v in items.items()) + "});\n")
print(OUT, len(items), "textures")
