#!/usr/bin/env python3
"""GUI panels, drawn for the wiki (own work): the two shapes every Minecraft screen is made of, in the wiki's dark tones,
as 6x6 nine-slice textures (slice 2, shown at x2 as a 4 px border):
  gp_panel  a raised container: one ink texel with the corner texel cut away (the game's rounded-by-one-pixel GUI edge),
            then a light texel top and left, a dark texel bottom and right, then the fill
  gp_inset  a sunken well (inventory slot, text area): dark texel top and left, light bottom and right, darker fill
  gp_card   a raised panel one step lighter, for cards that sit on a panel
panels() returns {name: image}."""
from PIL import Image
H = lambda s: tuple(int(s[i:i+2], 16) for i in (1, 3, 5)) + (255,)
INK = H("#0b0b0d")
def raised(fill, hi, lo):
    im = Image.new("RGBA", (6, 6), fill); px = im.load()
    for i in range(6): px[i, 0] = px[i, 5] = px[0, i] = px[5, i] = INK
    for i in range(1, 5): px[i, 1] = hi; px[1, i] = hi; px[i, 4] = lo; px[4, i] = lo
    px[4, 1] = px[1, 4] = fill                       # the bevel meets at the other two corners
    for x, y in ((0, 0), (5, 0), (0, 5), (5, 5)): px[x, y] = (0, 0, 0, 0)
    return im
def sunken(fill, lo, hi):
    im = Image.new("RGBA", (6, 6), fill); px = im.load()
    for i in range(6): px[i, 0] = lo; px[0, i] = lo; px[i, 5] = hi; px[5, i] = hi
    px[5, 0] = px[0, 5] = fill
    return im
def panels():
    return {"gp_panel": raised(H("#242428"), H("#45454d"), H("#151518")),
            "gp_card": raised(H("#2c2c31"), H("#4f4f58"), H("#18181b")),
            "gp_inset": sunken(H("#18181b"), H("#0c0c0e"), H("#3a3a41"))}
