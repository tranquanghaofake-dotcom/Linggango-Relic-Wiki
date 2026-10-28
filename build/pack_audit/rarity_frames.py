#!/usr/bin/env python3
"""Rarity frames, drawn for the wiki (own work, no third-party pixels).

A frame is an inventory slot with a thin rarity rim: one ink texel, one bevelled colour texel (light top-left,
dark bottom-right, like every Minecraft button and slot), then the dark slot with its own inset shadow.
Ornament stays inside that 2-texel band or just inside the slot, and grows with rarity:
  r0 Common  plain rim            r1 Uncommon  plain rim           r2 Rare  bright corner texels
  r3 Epic    + a stud on each side                r4 Legendary + corner brackets inside the slot
  r5 Mythic  + a crest at the top and bottom      r6 Must-Have + a white star in the top crest
Colours are muted material colours sampled from vanilla 1.20.1 items (iron ingot, raw gold, prismarine, amethyst
shard, copper ingot, redstone, gold ingot), not the game's bright chat colours.

frame(r, n): an n×n frame (n = 32 for tiles at ×2, 64 for the infobox picture at ×3). The window for a 16 px icon at
×2 (tile) sits exactly in the centre. frames() returns the seven 32 px frames, frames(64) the big ones.
Usage: python3 rarity_frames.py <out dir>   writes rf_N.png and rfb_N.png for a look."""
import sys, pathlib
from PIL import Image
H = lambda s: tuple(int(s[i:i+2], 16) for i in (1, 3, 5)) + (255,)
# dark → light ramps. Mid tones (index 2) are the --r0 … --r6 colours in style.game.css.
RAMP = {
 0: ["#3d3c40", "#6e6c72", "#a9a7ad", "#d6d4d8"],   # iron
 1: ["#4a4120", "#8a7a36", "#c9b45a", "#e8dc98"],   # raw gold / straw
 2: ["#1d3f3b", "#2f7a71", "#5fb3a7", "#a7dcd2"],   # prismarine
 3: ["#33264a", "#5f4790", "#9a7bcf", "#cdb6ee"],   # amethyst
 4: ["#4a2814", "#8f4e24", "#d07f3c", "#efb886"],   # copper
 5: ["#46140f", "#86271f", "#c4483c", "#e79a8e"],   # redstone
 6: ["#4f3a0c", "#9a7417", "#e3b440", "#f8e3a0"],   # gold ingot
}
INK, SLOT, SLOT_LO, SLOT_HI = H("#0d0d0f"), H("#1c1c20"), H("#0c0c0e"), H("#34343a")
def frame(r, n=32):
    k = [H(c) for c in RAMP[r]]; e = n - 1
    mix = lambda a, b, t: tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3)) + (255,)
    fill = mix(SLOT, k[0], .45)                          # the slot takes a breath of the rarity colour, so rows scan by colour
    im = Image.new("RGBA", (n, n), fill); px = im.load()
    def put(x, y, c):
        if 0 <= x < n and 0 <= y < n: px[x, y] = c
    for i in range(n):                                   # ink line
        put(i, 0, INK); put(i, e, INK); put(0, i, INK); put(e, i, INK)
    for i in range(1, e):                                # bevelled colour rim
        put(i, 1, k[3] if i < e - 1 else k[2]); put(1, i, k[3] if i < e - 1 else k[2])
        put(i, e - 1, k[1]); put(e - 1, i, k[1])
    put(1, 1, k[3]); put(e - 1, 1, k[2]); put(1, e - 1, k[2])
    for i in range(2, e - 1):                            # the slot's own inset: shadow top-left, light bottom-right
        put(i, 2, SLOT_LO); put(2, i, SLOT_LO); put(i, e - 2, SLOT_HI); put(e - 2, i, SLOT_HI)
    put(2, e - 2, fill); put(e - 2, 2, fill)
    m = n // 2
    if r >= 2:                                           # bright corner texels
        for x, y in ((1, 1), (e - 1, 1), (1, e - 1), (e - 1, e - 1)): put(x, y, k[3])
    if r >= 3:                                           # a stud in the middle of each side
        for d in (-1, 0):
            put(m + d, 1, k[3]); put(m + d, e - 1, k[2]); put(1, m + d, k[3]); put(e - 1, m + d, k[2])
            put(m + d, 2, k[1]); put(2, m + d, k[1]); put(m + d, e - 2, k[0]); put(e - 2, m + d, k[0])
    if r >= 4:                                           # corner brackets just inside the slot
        L = 3 if n <= 32 else 5
        for (x, y, sx, sy) in ((3, 3, 1, 1), (e - 3, 3, -1, 1), (3, e - 3, 1, -1), (e - 3, e - 3, -1, -1)):
            for i in range(L): put(x + sx * i, y, k[2]); put(x, y + sy * i, k[2])
    if r >= 5:                                           # crest: a small step that breaks the top and bottom edge inward
        for (y, d) in ((2, 1), (e - 2, -1)):
            for x in range(m - 3, m + 3): put(x, y, k[2])
            for x in range(m - 2, m + 2): put(x, y + d, k[1])
    if r == 6:                                           # Must-Have: a white star on the top crest
        W = H("#fff6d8")
        for x, y in ((m - 1, 1), (m, 1), (m - 2, 2), (m + 1, 2), (m - 1, 2), (m, 2), (m - 1, 3), (m, 3)): put(x, y, W)
    return im
def frames(n=32): return [frame(r, n) for r in range(7)]
if __name__ == "__main__":
    OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
    for r in range(7):
        frame(r).save(OUT / f"rf_{r}.png", optimize=True); frame(r, 64).save(OUT / f"rfb_{r}.png", optimize=True)
