#!/usr/bin/env python3
"""Mob faces for "Where it drops": the front of each vanilla mob's head, cut from its 1.20.1 entity texture at the
model's own UV (box at texOffs(u, v) with depth d: the front face starts at u+d, v+d; tall or wide heads keep their
central 8x8 square), with its overlay (hat, glowing
eyes) on top, and set in a 16x16 square at the largest whole scale that fits. Modded mobs have no face here; the page
shows a monster spawner for them instead.

faces(V) returns {name: image}, V = assets/minecraft/textures of InventivetalentDev/minecraft-assets@1.20.1."""
from PIL import Image
# name: [(texture, x, y, w, h), …] bottom to top; every layer of one face has the same size
F = {
 "Zombie": [("entity/zombie/zombie", 8, 8, 8, 8), ("entity/zombie/zombie", 40, 8, 8, 8)],
 "Husk": [("entity/zombie/husk", 8, 8, 8, 8), ("entity/zombie/husk", 40, 8, 8, 8)],
 "Drowned": [("entity/zombie/drowned", 8, 8, 8, 8), ("entity/zombie/drowned", 40, 8, 8, 8)],
 "Skeleton": [("entity/skeleton/skeleton", 8, 8, 8, 8)],
 "Stray": [("entity/skeleton/stray", 8, 8, 8, 8)],
 "Wither Skeleton": [("entity/skeleton/wither_skeleton", 8, 8, 8, 8)],
 "Zombie Villager": [("entity/zombie_villager/zombie_villager", 8, 9, 8, 8)],
 "Evoker": [("entity/illager/evoker", 8, 9, 8, 8)],
 "Vindicator": [("entity/illager/vindicator", 8, 9, 8, 8)],
 "Pillager": [("entity/illager/pillager", 8, 9, 8, 8)],
 "Witch": [("entity/witch", 8, 9, 8, 8)],
 "Enderman": [("entity/enderman/enderman", 8, 8, 8, 8), ("entity/enderman/enderman_eyes", 8, 8, 8, 8)],
 "Creeper": [("entity/creeper/creeper", 8, 8, 8, 8)],
 "Spider": [("entity/spider/spider", 40, 12, 8, 8), ("entity/spider_eyes", 40, 12, 8, 8)],
 "Cave Spider": [("entity/spider/cave_spider", 40, 12, 8, 8), ("entity/spider_eyes", 40, 12, 8, 8)],
 "Blaze": [("entity/blaze", 8, 8, 8, 8)],
 "Ghast": [("entity/ghast/ghast", 16, 16, 16, 16)],
 "Piglin Brute": [("entity/piglin/piglin_brute", 9, 8, 8, 8)],
 "Zombified Piglin": [("entity/piglin/zombified_piglin", 9, 8, 8, 8)],
 "Bat": [("entity/bat", 6, 6, 6, 6)],
 "Shulker": [("entity/shulker/shulker", 6, 58, 6, 6)],
 "Ravager": [("entity/illager/ravager", 16, 18, 16, 16)],
 "Elder Guardian": [("entity/guardian_elder", 16, 16, 12, 12)],
 "Bee": [("entity/bee/bee", 13, 13, 7, 7)],
 "Mooshroom": [("entity/cow/red_mooshroom", 6, 6, 8, 8)],
 "Warden": [("entity/warden/warden", 10, 42, 16, 16)],
 "Wither": [("entity/wither/wither", 8, 8, 8, 8)],
}
ALIAS = {"Ravagers": "Ravager"}
def face(V, layers):
    w, h = layers[0][3], layers[0][4]; im = Image.new("RGBA", (w, h))
    for t, x, y, lw, lh in layers:
        src = Image.open(V / f"{t}.png").convert("RGBA").crop((x, y, x + lw, y + lh))
        if (lw, lh) != (w, h):                            # a smaller inner layer (the slime's core) sits centred
            im.alpha_composite(src, ((w - lw) // 2, (h - lh) // 2))
        else: im.alpha_composite(src)
    k = max(1, 16 // max(w, h)); im = im.resize((w * k, h * k), Image.NEAREST)
    out = Image.new("RGBA", (16, 16)); out.alpha_composite(im, ((16 - im.width) // 2, (16 - im.height) // 2)); return out
def faces(V): return {n: face(V, l) for n, l in F.items()}
