#!/usr/bin/env python3
"""Takes the game's own names of Minecraft's items, blocks and mobs (official/vanilla_terms.json, made by vanilla_terms.py) into the names domain of every language.

  python3 build/i18n/tools/adopt_vanilla.py [--dry] [--cats item,block,entity]

An entry of ours is never replaced (our word wins, docs/I18N.md); what the game has no name for in a language stays English there. vi is written in Title Case like our own names.
Run it again after Minecraft's own translations were harvested again (vanilla_terms.py), or when a new vanilla name shows up in a recipe.
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tmlib

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--dry', action='store_true'); ap.add_argument('--cats', default='item,block,entity'); a = ap.parse_args()
    cats = set(a.cats.split(',')); v = json.load(open(os.path.join(tmlib.HERE, 'official', 'vanilla_terms.json'), encoding='utf-8'))
    tc = lambda s: ' '.join(w[:1].upper() + w[1:] for w in s.split(' '))
    keeps = json.load(open(os.path.join(tmlib.HERE, 'keep.json'), encoding='utf-8')); n = 0
    for lang in ('vi', 'ru', 'pt', 'es'):
        tm = tmlib.load_tm(lang); have = {e['en'] for e in tm.values()}; skip = set(keeps.get('all', [])) | set(keeps.get(lang, [])); add = 0
        for en, d in v.items():
            if d.get('_c') not in cats or en in have or en in skip: continue
            t = d.get(lang)
            t = (tc(t) if lang == 'vi' else t) if t else en
            tm[tmlib.hsh(en)] = {'en': en, 't': t, 's': 'official', 'd': 'names'}; add += 1
        print(lang, add, 'names added' + (' (dry)' if a.dry else ''))
        if not a.dry: tmlib.write_tm(lang, tm)

if __name__ == '__main__': main()
