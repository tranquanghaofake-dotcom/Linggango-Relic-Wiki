#!/usr/bin/env python3
"""An armor stand wearing a full set, seen from the front, for the Build planner's room: the game's own armor textures
(models/armor/<material>_layer_1 and _2 of 1.20.1) cut at the player model's front faces (head 8,8; body 20,20; arms 44,20;
legs 4,20) and stacked like the model (legs, boots, waist, chest and arms, helmet) over a wooden stand drawn in the colours
of entity/armorstand/wood.png. 16x32 px: one block wide, two tall, like the stand in game.

stand(V, material) -> image; V = assets/minecraft/textures of InventivetalentDev/minecraft-assets@1.20.1."""
from PIL import Image
def stand(V, m):
    L1 = Image.open(V / f"models/armor/{m}_layer_1.png").convert("RGBA"); L2 = Image.open(V / f"models/armor/{m}_layer_2.png").convert("RGBA")
    wood = Image.open(V / "entity/armorstand/wood.png").convert("RGBA")
    px = sorted((c for c in wood.getdata() if c[3] > 200), key=lambda c: sum(c[:3])); lo, mid, hi = px[len(px) // 5], px[len(px) // 2], px[len(px) * 4 // 5]
    im = Image.new("RGBA", (16, 32)); p = im.load()
    def rect(x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): p[x, y] = c
    rect(7, 2, 8, 30, mid); rect(7, 2, 7, 30, hi)           # the pole, lit on the left
    rect(2, 8, 13, 9, mid); rect(2, 8, 13, 8, hi)           # shoulder bar
    rect(5, 19, 10, 19, lo)                                 # hip bar
    rect(1, 30, 14, 31, lo); rect(1, 30, 14, 30, mid)       # base plate
    put = lambda src, box, at: im.alpha_composite(src.crop(box), at)
    put(L2, (4, 20, 8, 32), (4, 20)); put(L2, (4, 20, 8, 32), (8, 20))      # leggings, both legs
    put(L1, (4, 26, 8, 32), (4, 26)); put(L1, (4, 26, 8, 32), (8, 26))      # boots: the lower part of the leg box
    put(L2, (20, 20, 28, 32), (4, 8))                                       # leggings' waist
    put(L1, (20, 20, 28, 32), (4, 8))                                       # chestplate
    put(L1, (44, 20, 48, 32), (0, 8)); put(L1, (44, 20, 48, 32), (12, 8))        # arms
    put(L1, (8, 8, 16, 16), (4, 0))                                         # helmet
    return im
