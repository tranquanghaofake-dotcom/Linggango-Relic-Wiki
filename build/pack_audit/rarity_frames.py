#!/usr/bin/env python3
"""Rarity frames, drawn for the wiki (own work, no third-party pixels): one 32x32 frame per rarity with a 16x16 window
in the exact centre (8..23), so a 16 px icon at x2 sits in it on a 64 px tile, and at x6 in the infobox.
Ornament grows with rarity; colours are the game's own formatting colours as 4-step ramps, light from the top left.
frames() returns the seven images; run directly to write rf_0.png … rf_6.png.  Usage: python3 rarity_frames.py <out dir>"""
import sys, pathlib
from PIL import Image
H = lambda s: tuple(int(s[i:i+2], 16) for i in (1, 3, 5)) + (255,)
RAMP = {  # dark → light (rarity colours of the game: §f §e §b §d §6 §c, Must-Have gold)
 0: ["#2a2833", "#4a4658", "#8d89a0", "#d8d4e4"], 1: ["#3a3a08", "#8a8a1e", "#e0e04a", "#ffff9a"],
 2: ["#0b3a3a", "#1d8a8a", "#4ae0e0", "#b4ffff"], 3: ["#3a0b3a", "#8a1d8a", "#e04ae0", "#ffb4ff"],
 4: ["#4a2b05", "#a06c0e", "#efaa2e", "#ffe0a3"], 5: ["#4a0a0a", "#a01e1e", "#ef4a4a", "#ffb0a8"],
 6: ["#5a3a00", "#b88a10", "#ffd21f", "#fff3a0"]}
INK, FILL = H("#0c0b10"), H("#1d1b25")
def frame(r):
    k = [H(c) for c in RAMP[r]]; im = Image.new("RGBA", (32, 32)); px = im.load()
    def rect(x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): px[x, y] = c
    # same outer size for every rarity: ink edge, a 6-texel band with a dithered metal fill, bevel light top/left
    mix = lambda a, b, t: tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3)) + (255,)
    base, dith = mix(FILL, k[1], .38), mix(FILL, k[0], .55)    # dark metal tinted by the rarity; bright colour only on details
    rect(0, 0, 31, 31, INK)
    rect(1, 1, 30, 30, base)
    if r: [px.__setitem__((x, y), dith) for y in range(1, 31) for x in range(1, 31) if (x * 3 + y * 5) % 7 == 0]
    for i in range(1, 31): px[i, 1] = k[2]; px[1, i] = k[2]; px[i, 30] = k[0]; px[30, i] = k[0]
    px[1, 1] = k[3]
    rect(7, 7, 24, 24, INK)                                     # one dark line where the band meets the window
    rect(8, 8, 23, 23, (0, 0, 0, 0))                            # the window, exactly in the centre
    if r >= 1:                                                   # corner rivets
        for cx, cy in ((3, 3), (27, 3), (3, 27), (27, 27)):
            rect(cx, cy, cx + 1, cy + 1, k[3]); px[cx + 1, cy + 1] = k[2]
    if r >= 2:                                                   # a light inner line one texel from the window
        for i in range(6, 26): px[i, 6] = k[2]; px[6, i] = k[2]; px[i, 25] = k[0]; px[25, i] = k[0]
    if r >= 3:                                                   # gems in the middle of each side
        for (x, y) in ((15, 3), (15, 27), (3, 15), (27, 15)):
            for dx, dy, c in ((0, 0, k[3]), (1, 0, k[2]), (0, 1, k[2]), (1, 1, k[0])): px[x + dx, y + dy] = c
    if r >= 4:                                                   # corner brackets
        for (x, y, sx, sy) in ((2, 2, 1, 1), (29, 2, -1, 1), (2, 29, 1, -1), (29, 29, -1, -1)):
            for i in range(4): px[x + sx * i, y] = k[3]; px[x, y + sy * i] = k[3]
    if r >= 5:                                                   # crest top and bottom
        for (y, d) in ((0, 1), (31, -1)):
            for x in range(12, 20): px[x, y] = k[2]
            for x in range(13, 19): px[x, y + d] = k[3]
            for x in range(14, 18): px[x, y + 2 * d] = k[3]
    if r == 6:                                                   # Must-Have: a star in the top crest
        for x, y in ((15, 2), (16, 2), (15, 3), (16, 3), (14, 3), (17, 3), (15, 4), (16, 4), (15, 1), (16, 1)): px[x, y] = H("#ffffff")
    return im
def frames(): return [frame(r) for r in range(7)]
if __name__ == "__main__":
    OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
    for r, im in enumerate(frames()): im.save(OUT / f"rf_{r}.png", optimize=True)
