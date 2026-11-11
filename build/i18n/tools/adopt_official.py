#!/usr/bin/env python3
"""Use the game's own translation where our entry is a name, a title or a short label, or is still English: python3 build/i18n/tools/adopt_official.py [--dry] [--words 5] [--lang ru]

A player sees the mods' text in the game's language, so a short text that the mod's own translation covers should read the same on the wiki ("Bone Lord" => "Властелин костей", not "Bone Lord"; "Burden of Desolation" => "Бремя Опустошения").
An official text is taken when official/<lang>.json has it for the same English, tmlib.official_text_ok accepts it (same numbers and placeholders, not another English string of the file), it is not mostly English itself,
and ours is the same as the English, or ours has at most --words words (default 5). Longer sentences stay ours (a sentence of ours wins over the game's). The entry becomes state `official`. --dry only lists."""
import sys, os, json, re, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tmlib
ap = argparse.ArgumentParser(); ap.add_argument('--dry', action='store_true'); ap.add_argument('--words', type=int, default=5); ap.add_argument('--lang'); ap.add_argument('--show', type=int, default=0); a = ap.parse_args()
latin = lambda t: len([w for w in re.findall(r'[A-Za-z]{4,}', t)])
for lang in ([a.lang] if a.lang else ['vi', 'ru', 'pt', 'es']):
    o = json.load(open(os.path.join(tmlib.HERE, 'official', lang + '.json'), encoding='utf-8'))['text']; eng = set(o); tm = tmlib.load_tm(lang); n = 0; shown = 0; same = 0
    for k, e in tm.items():
        if not isinstance(e['t'], str) or e['en'] not in o or e.get('s') == 'human': continue
        off = o[e['en']].strip(); mine = e['t'].strip()
        if off == mine or not tmlib.official_text_ok(e['en'], off, eng): continue
        short = len(e['en'].split()) <= a.words and not re.search(r'[.!?]\s*$', e['en'])
        if not (mine == e['en'] or short): continue
        if lang in ('ru', 'vi') and latin(off) > max(latin(e['en']), latin(mine)): continue   # the mod left English in it
        if not re.search(r'[^\x00-\x7f]', off) and lang in ('ru', 'vi') and off != mine and mine != e['en']: continue
        if mine != e['en'] and (len(off) > 1.5 * len(mine) + 4 or len(off) < 0.5 * len(mine) - 4): continue   # the same English can be two keys of a mod with different texts: a very different length is such a mix-up
        n += 1
        if shown < a.show: shown += 1; print('  %-32s | ours: %-28s | game: %s [%s]' % (e['en'][:32], mine[:28], off[:46], e['d']))
        if not a.dry: e['t'] = off; e['s'] = 'official'
    print(lang, 'adopted' if not a.dry else 'would adopt', n)
    if not a.dry: tmlib.write_tm(lang, tm)
