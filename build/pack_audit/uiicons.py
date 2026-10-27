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
import rarity_frames   # own work: one frame per rarity (rf_0 … rf_6)
V, L = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
OUT = pathlib.Path(__file__).resolve().parents[1] / "src" / "uiicons.js"
VANILLA = {  # key: item texture
    "ui_sword": "item/iron_sword", "ui_bow": "item/bow", "ui_arrow": "item/arrow", "ui_fire_charge": "item/fire_charge",
    "ui_bone": "item/bone", "ui_feather": "item/feather", "ui_glowstone": "item/glowstone_dust", "ui_star": "item/nether_star",
    "ui_helmet": "item/iron_helmet", "ui_chestplate": "item/iron_chestplate", "ui_leggings": "item/iron_leggings", "ui_boots": "item/iron_boots",
}
LIBRARY = {  # key: file in the library
    "pt_goety_fire": "goety/assets/goety/textures/particle/big_fire_4.png",
    "pt_goety_soul": "goety/assets/goety/textures/particle/big_soul_fire_drop_3.png",
    "pt_goety_end": "goety/assets/goety/textures/particle/end_fire_3.png",
    "pt_hexerei_star": "hexerei/assets/hexerei/textures/particle/star_brush_3.png",
}
b64 = lambda p: base64.b64encode(p.read_bytes()).decode()
items = {k: b64(V / f"{v}.png") for k, v in VANILLA.items()}
items.update({k: b64(L / v) for k, v in LIBRARY.items()})
for r, im in enumerate(rarity_frames.frames()):
    buf = io.BytesIO(); im.save(buf, "PNG", optimize=True); items[f"rf_{r}"] = base64.b64encode(buf.getvalue()).decode()
OUT.write_text("Object.assign(ROOMT," + "{" + ",".join(f'"{k}":"{v}"' for k, v in items.items()) + "});\n")
print(OUT, len(items), "textures")
