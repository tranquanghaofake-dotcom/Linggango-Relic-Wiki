#!/usr/bin/env python3
"""Slot badges, drawn for the wiki (own work): the small sign in the corner of a curio tile that says which slot it
goes in, plus the two ring requirements (Seven Curses, Seven Virtues). Each badge is a 7x7 drawing in the colours of
the rarity frames' bone and metal, with a one-texel ink outline added around it, so it is 9x9 and shows at x2 (18 px),
the same texel size as the item and the frame it sits on. Shapes follow the Curios slot pictures, filled in.

badges() returns {name: image}; SLOT maps the pack's slot names to a badge. Usage: python3 slot_badges.py <out dir>"""
import sys, pathlib
from PIL import Image
H = lambda s: tuple(int(s[i:i+2], 16) for i in (1, 3, 5)) + (255,)
INK = H("#0d0d0f")
BONE = {"a": H("#ddd5c2"), "b": H("#9a917e")}
GEM = {"t": H("#5fb3a7"), "T": H("#2f7a71"), "r": H("#c4483c"), "R": H("#86271f"), "g": H("#e3b440"), "G": H("#9a7417"),
       "p": H("#9a7bcf"), "P": H("#5f4790"), "w": H("#fff6d8"), "k": H("#5b4e66"), "K": H("#3a3242"), "o": H("#a8744a"), "O": H("#6e4a2c")}
D = {  # 7 rows of 7: a/b bone light/shade, gem letters from GEM (capital = darker), "." empty
 "ring":     ["...t...", "..aTa..", ".a...b.", "a.....b", "a.....b", ".a...b.", "..bbb.."],
 "necklace": ["a.....a", ".a...a.", "..a.a..", "...b...", "..rrr..", "..rRr..", "...R..."],
 "charm":    ["...a...", "..a.b..", "...b...", ".ggggg.", ".gtttG.", ".gtTtG.", "..GGG.."],
 "curio":    ["...a...", "...a...", "..aba..", "aabtbaa", "..aba..", "...b...", "...b..."],
 "anklet":   [".......", ".aaaaa.", "a.....b", ".bbbbb.", "...g...", "..gGg..", "......."],
 "bracelet": [".......", ".aaaaa.", "a.....b", "a.....b", ".btbtb.", "......."  , "......."],
 "head":     [".......", "..aaa..", ".aaaaa.", "aabbbaa", "ab...ba", "ab...bb", "......."],
 "hands":    ["..a.a..", ".aaaaa.", ".aaaaa.", "aaaaab.", ".aaabb.", "..bbb..", "..ooo.."],
 "feet":     [".aaa...", ".aaa...", ".aab...", ".aab...", ".aabbaa", ".abbbbb", ".OOOOO."],
 "body":     ["aa...aa", "aaaaaaa", ".abbba.", ".aaaaa.", ".abbba.", ".aaaaa.", "......."],
 "back":     [".rrrrr.", ".aaaaa.", ".aaaaa.", "aaaaaaa", "aabbbaa", "abbbbbb", "b.b.b.b"],
 "belt":     [".......", ".......", "aagggaa", "bbg.gbb", "aagggaa", ".......", "......."],
 "heart":    [".rr.rr.", "rwrrrrr", "rrrrrrR", ".rrrrR.", "..rRR..", "...R...", "......."],
 "book":     [".pppppp", "Ppppppp", "Ppaaapp", "Ppppppp", "Ppppppp", "PpppppP", ".aaaaaa"],
 "scroll":   ["bbbbbbb", ".aaaaa.", ".abbba.", ".aaaaa.", ".abba..", ".aaaaa.", "bbbbbbb"],
 "talent":   ["...g...", "..ggg..", "gggwggg", ".ggggG.", ".gG.gG.", ".G...G.", "......."],
 "orb":      ["..ttt..", ".twttt.", "ttwtttt", "tttttTt", ".tttTT.", "..TTT..", "......."],
 "skull":    [".aaaaa.", "aaaaaaa", "a..a..a", "aaaaaaa", ".ab.ba.", ".a.b.a.", "......."],
 "chalice":  ["ggggggg", ".gwgggG", "..gggG.", "...G...", "...G...", "..gGG..", "......."],
 "living":   ["aa...aa", "aaaaaaa", ".arrRa.", ".arRRa.", ".abRba.", ".aaaaa.", "......."],
 "elytra":   ["aa...aa", "aaa.aaa", "aaa.aaa", "bab.bab", ".bb.bb.", ".b...b.", "......."],
 "key":      [".......", ".gg....", "g..gggg", "g..g.g.", ".gg..g.", ".......", "......."],
 "magnet":   ["rr...aa", "rr...aa", "aa...aa", "aa...aa", "aa...ab", ".aaabb.", "..bbb.."],
 "bundle":   ["...O...", "..OoO..", ".ooooo.", "ooooooo", "ooooooO", ".ooOOO.", "......."],
 "rq_curses":  ["...r...", "..kRk..", ".k...K.", "k.....K", "k.....K", ".k...K.", "..KKK.."],
 "rq_virtues": ["...w...", "..gwg..", ".g...G.", "g.....G", "g.....G", ".g...G.", "..GGG.."],
}
SLOT = {"Charm": "charm", "Accessory": "curio", "Curio": "curio", "Anklet": "anklet", "Blasphemy": "skull", "Scroll": "scroll",
        "Ring": "ring", "Head": "head", "Hands": "hands", "Glove": "hands", "Focus": "orb", "Spellbook": "book", "Back": "back",
        "Spellstone": "orb", "Heart": "heart", "Necklace": "necklace", "Belt": "belt", "Living Armour": "living",
        "Hostility Curse": "skull", "Elytra": "elytra", "Binding Key": "key", "Feet": "feet", "Body": "body",
        "Bracelet": "bracelet", "Talent": "talent", "Magnetizer": "magnet", "Bundle": "bundle", "Sacrament": "chalice"}
def badge(rows):
    im = Image.new("RGBA", (9, 9)); px = im.load(); pal = {**BONE, **GEM}
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".": px[x + 1, y + 1] = pal[ch]
    fill = {(x, y) for y in range(9) for x in range(9) if px[x, y][3]}
    for y in range(9):                                   # one-texel ink outline, 4-neighbours
        for x in range(9):
            if (x, y) not in fill and any((x + dx, y + dy) in fill for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))): px[x, y] = INK
    return im
def badges(): return {k: badge(v) for k, v in D.items()}
if __name__ == "__main__":
    OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
    for k, im in badges().items(): im.save(OUT / f"sb_{k}.png", optimize=True)
