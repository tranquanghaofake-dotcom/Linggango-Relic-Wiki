"""The quest book's Bosses chapter as a dependency graph -> build/patches/boss_graph.json (read by patches/boss_order.py).
Usage: boss_graph.py <chapters dir> [out.json]   (the chapter .snbt files in plain text; the pack ships them as LGQ1)
dep: wiki boss name -> boss quests it depends on (only bosses, by wiki name), dim: 0 overworld, 5 Nether, 6.3 End,
soul: boss -> [Keeper summon item, Keeper] its Boss Soul goes into (6.6.6 quest text "Soul: ... can go into the X, the summon for Y").
Quests that only group others ("Goety's Bosses", "Soulslike Weaponry") pass their own dependencies through."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snbt import parse, clean
D = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '..', '..', 'patches', 'boss_graph.json')
# quest title -> wiki boss name(s); None = a grouping quest (dependencies pass through); missing = not a boss
NAME = {"The Dune Sentinel": "Dune Sentinel", "The Ancient Guardian": "Ancient Guardian", "Kill Overgrown Colossus": "Overgrown Colossus",
        "Frostbitten Golem": "Frostbitten Golem", "The Withered Abomination": "Withered Abomination", "Lava Eater": "Lava Eater",
        "The Frostmaw": "Frostmaw", "Umvuthi The Sunbird": "Umvuthi", "Ferrous Wroughtnaut": "Ferrous Wroughtnaut", "The Swampjaw": "Swampjaw",
        "Dame Fortuna": "Dame Fortuna", "The Bellringer": "Bellringer", "Kill Tongbi or Do his test": "Tongbi, the Sculptor",
        "Rosalyne, Blade of Dusk": "Rosalyne", "The Skeletosaurus": "Skeletosaurus", "The Corpse Warlock": "Corpse Warlock",
        "The Dead King": "Dead King", "The Wither": "Wither", "The Warden": "Warden", "The Possessed Paladin": "Possessed Paladin",
        "The Cumulonimbus": "Cumulonimbus", "Scylla": "Scylla", "The Nether Monstrosity": "Netherite Monstrosity",
        "The Lord Pumpkinhead": "Lord Pumpkinhead", "The Forsaken": "Forsaken", "The Luxtructosaurus": "Luxtructosaurus",
        "The Trial Guardian": "Trial Guardian", "Obsidilith": "Obsidilith", "Void Blossom": "Void Blossom", "The Night Lich": "Lich",
        "The Nether Gauntlet": "Gauntlet", "Underworld Knight": "Underworld Knight",
        "Void Entities": ["Endersent", "Chorusling", "Shulker Mimic", "Mutant Enderman"], "The Harbinger": "The Harbinger",
        "The Ender Guardian": "Ender Guardian", "Ancient Remnant": "Ancient Remnant", "The Leviathan": "The Leviathan", "Ignis": "Ignis",
        "Maledictus": "Maledictus", "The Nightwarden": "The Nightwarden", "The Chesed": "Chesed", "Malkuth": "Malkuth", "APOLLYON": "Apollyon",
        "The Immortal": "Immortal", "Redstone Monstrosity": "Redstone Monstrosity", "Redstone Golem": "Redstone Golem", "The Apostle": "Apostle",
        "The Shadow Wizards": "Gundalf, Circe, Merlin (Shadow Wizards)", "Echo of Tyros, First Flamebearer": "Tyros (fire boss)",
        "The Obliterator": "The Obliterator", "Geburah": "Geburah", "Relic Annihilator": "Relic Annihilator", "Realm Warden": "Realm Warden",
        "The Old Champion": "Draugr → Night Shade", "The Returning Knight": "Returning Knight", "The Monarch of Chaos": "Chaos Monarch",
        "The Decaying King": "Accursed Lord", "The Fallen Icon": "Moonknight", "Day Stalker and Night Prowler": ["Day Stalker", "Night Prowler"],
        "The Vizier": "Vizier", "The Minister": "Minister", "The Crone": "Crone", "The Heresiarch": "Heresiarch", "The Skull Lord": "Skull Lord",
        "Wither Necromancer": "Wither Necromancer", "Brood Mother": "Brood Mother", "The Wight": "Wight", "The Ender Keeper": "Ender Keeper",
        "Goety's Bosses": None, "Soulslike Weaponry": None}
DIM = {"Nether": 5, "End": 6.3}
DIMX = {"Wither Necromancer": 5, "Ender Keeper": 6.3}   # Goety boss quests have joke subtitles: Nether Fortress, Final Terminal (End)
c = parse(open(os.path.join(D, 'bosses.snbt'), encoding='utf8').read())
Q = {q['id']: q for q in c['quests']}
title = lambda q: clean(q.get('title', ''))
def names(qid, seen=()):
    q = Q.get(qid)
    if not q or qid in seen: return []
    n = NAME.get(title(q), '?')
    if n is None: return [x for d in q.get('dependencies', []) for x in names(d, seen + (qid,))]
    if n == '?': return []
    return n if isinstance(n, list) else [n]
dep, dim, soul, unknown = {}, {}, {}, []
for q in c['quests']:
    t = title(q); n = NAME.get(t, '?')
    if n == '?': unknown.append(t); continue
    if n is None: continue
    ps = sorted({x for d in q.get('dependencies', []) for x in names(d)})
    sub = clean(q.get('subtitle', '')); d = DIM.get(re.split(r'\s*/\s*', sub)[0].strip(), 0)
    s = next(([m.group(1).strip(), m.group(2).strip()] for x in q.get('description', []) for m in [re.search(r'can go into the (.+?), the summon for (?:the )?(.+?)\.?$', clean(x))] if m), None)
    for b in (n if isinstance(n, list) else [n]):
        dep[b] = [p for p in ps if p != b]; dim[b] = DIMX.get(b, d)
        if s: soul[b] = s
out = {"dep": dep, "dim": dim, "soul": soul}
json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=0)
print('bosses', len(dep), 'souls', len(soul), 'not bosses:', [u for u in unknown if u])
