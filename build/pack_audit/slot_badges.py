#!/usr/bin/env python3
"""Slot badges, drawn for the wiki (own work): the small sign in the corner of a curio tile that says which slot it
goes in, plus the two ring requirements (Seven Curses, Seven Virtues). Each badge is a 5x5 drawing in the colours of
the rarity frames' bone and metal, with a one-texel ink outline added around it, so it is 7x7 and shows at x2 (14 px),
the same texel size as the item and the frame it sits on. Shapes follow the Curios slot pictures, filled in.

badges() returns {name: image}; SLOT maps the pack's slot names to a badge. Usage: python3 slot_badges.py <out dir>"""
import sys, pathlib
from PIL import Image
H = lambda s: tuple(int(s[i:i+2], 16) for i in (1, 3, 5)) + (255,)
INK = H("#0d0d0f")
BONE = {"a": H("#ddd5c2"), "b": H("#9a917e")}
GEM = {"t": H("#5fb3a7"), "T": H("#2f7a71"), "r": H("#c4483c"), "R": H("#86271f"), "g": H("#e3b440"), "G": H("#9a7417"),
       "p": H("#9a7bcf"), "P": H("#5f4790"), "w": H("#fff6d8"), "k": H("#5b4e66"), "K": H("#3a3242"), "o": H("#a8744a"), "O": H("#6e4a2c")}
D = {  # 5 rows of 5: a/b bone light/shade, gem letters from GEM (capital = darker), "." empty
 "ring":     [".ata.", "a...b", "a...b", "a...b", ".bbb."],
 "necklace": ["a...a", ".a.a.", "..r..", ".rRr.", "..R.."],
 "charm":    ["..a..", ".ggg.", "gtttG", "gtTtG", ".GGG."],
 "curio":    ["..a..", "..a..", "aatbb", "..b..", "..b.."],
 "anklet":   [".aaa.", "a...b", ".bbb.", "..g..", "..G.."],
 "bracelet": [".aaa.", "a...b", "a...b", ".btb.", "....."],
 "head":     [".aaa.", "aaaaa", "abbba", "a...a", "....."],
 "hands":    ["a.a.a", "aaaaa", "aaaab", ".aab.", ".ooo."],
 "feet":     ["aa...", "aa...", "aab..", "aabba", "OOOOO"],
 "body":     ["aa.aa", "aaaaa", ".aba.", ".aaa.", ".bbb."],
 "back":     ["rrrrr", "aaaaa", "aaaaa", "abbba", "b.b.b"],
 "belt":     [".....", "aagaa", "bg.gb", "aagaa", "....."],
 "heart":    ["rr.rr", "rwrrr", "rrrrR", ".rrR.", "..R.."],
 "book":     [".pppp", "Ppaap", "Ppppp", "Ppppp", ".aaaa"],
 "scroll":   ["bbbbb", ".aaa.", ".aba.", ".aaa.", "bbbbb"],
 "talent":   ["..g..", ".ggg.", "ggwgg", ".gGg.", "g...G"],
 "orb":      [".ttt.", "twttt", "ttttT", "tttTT", ".TTT."],
 "skull":    [".aaa.", "aaaaa", "a.a.a", "aaaaa", ".a.a."],
 "chalice":  ["ggggg", "gwggG", ".gGG.", "..G..", ".gGG."],
 "living":   ["aa.aa", "aaaaa", ".rRa.", ".aRa.", ".aaa."],
 "elytra":   ["aa.aa", "aa.aa", "ab.ba", ".b.b.", "....."],
 "key":      ["gg...", "g.ggg", "gg.g.", ".....", "....."],
 "magnet":   ["r...r", "a...a", "a...a", "a...b", ".abb."],
 "bundle":   ["..O..", ".oOo.", "ooooo", "ooooO", ".oOO."],
 "rq_curses":  [".kRk.", "k...K", "k...K", "k...K", ".KKK."],
 "rq_virtues": [".gwg.", "g...G", "g...G", "g...G", ".GGG."],
}
SLOT = {"Charm": "charm", "Accessory": "curio", "Curio": "curio", "Anklet": "anklet", "Blasphemy": "skull", "Scroll": "scroll",
        "Ring": "ring", "Head": "head", "Hands": "hands", "Glove": "hands", "Focus": "orb", "Spellbook": "book", "Back": "back",
        "Spellstone": "orb", "Heart": "heart", "Necklace": "necklace", "Belt": "belt", "Living Armour": "living",
        "Hostility Curse": "skull", "Elytra": "elytra", "Binding Key": "key", "Feet": "feet", "Body": "body",
        "Bracelet": "bracelet", "Talent": "talent", "Magnetizer": "magnet", "Bundle": "bundle", "Sacrament": "chalice"}
def badge(rows):
    N = len(rows) + 2; im = Image.new("RGBA", (N, N)); px = im.load(); pal = {**BONE, **GEM}
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".": px[x + 1, y + 1] = pal[ch]
    fill = {(x, y) for y in range(N) for x in range(N) if px[x, y][3]}
    for y in range(N):                                   # one-texel ink outline, 4-neighbours
        for x in range(N):
            if (x, y) not in fill and any((x + dx, y + dy) in fill for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))): px[x, y] = INK
    return im
def badges(): return {k: badge(v) for k, v in D.items()}
if __name__ == "__main__":
    OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
    for k, im in badges().items(): im.save(OUT / f"sb_{k}.png", optimize=True)
