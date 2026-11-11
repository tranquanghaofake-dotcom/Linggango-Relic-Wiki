#!/usr/bin/env python3
"""Does the wiki say Minecraft's words the way Minecraft does? python3 build/i18n/tools/terms.py [--lang ru] [--min 6] [--below 0.6] [--show 3]

For each word of official/vanilla_terms.json that occurs (as a whole, capitalised word or phrase) in at least --min English strings of the translation memory, the share of those strings
whose translation contains the game's own word (compared by stem, so Russian case endings do not matter). Words below --below are listed with a few examples: a word where the wiki says it differently
from the game is either a deliberate choice (put it in glossary.json "terms") or an inconsistency to fix."""
import sys, os, re, json, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tmlib
ap = argparse.ArgumentParser(); ap.add_argument('--lang'); ap.add_argument('--min', type=int, default=6); ap.add_argument('--below', type=float, default=0.6); ap.add_argument('--show', type=int, default=3); ap.add_argument('--json', help='write every string with a word not said as the game says it: [{lang, en, t, term, game}]'); a = ap.parse_args(); flagged = []
V = json.load(open(os.path.join(tmlib.HERE, 'official', 'vanilla_terms.json'), encoding='utf-8'))
G = json.load(open(os.path.join(tmlib.HERE, 'glossary.json'), encoding='utf-8')); chosen = G.get('terms', {})
def stems(t): return [w.lower()[:max(4, len(w) - (3 if re.search('[а-я]', w) else 2))] for w in re.findall(r'[^\W\d_]+', t) if len(w) > 2]
for lang in ([a.lang] if a.lang else ['vi', 'ru', 'pt', 'es']):
    tm = tmlib.load_tm(lang); rows = []
    for en, per in V.items():
        if lang not in per or len(en) < 4 or not en[0].isupper(): continue
        rx = re.compile(r'(?<![A-Za-z])' + re.escape(en) + r"(?![a-z])")
        hit = [e for e in tm.values() if isinstance(e['t'], str) and rx.search(e['en'].split('\u0001')[0])]
        if len(hit) < a.min: continue
        st = stems(per[lang]); ok = [e for e in hit if all(s in e['t'].lower() for s in st)]
        flagged += [{'lang': lang, 'en': e['en'], 't': e['t'], 'term': en, 'game': per[lang], 'domain': e['d']} for e in hit if e not in ok]
        if len(ok) / len(hit) < a.below: rows.append((len(hit), len(ok), en, per[lang], [e for e in hit if e not in ok][:a.show]))
    print('== %s: %d words below %.0f%% (of those that occur in %d or more English strings)' % (lang, len(rows), a.below * 100, a.min))
    for n, k, en, off, ex in sorted(rows, reverse=True):
        print('  %-26s game: %-24s used %2d of %3d%s' % (en, off, k, n, '   [glossary: %s]' % chosen[en][lang] if en in chosen and lang in chosen[en] else ''))
        for e in ex: print('        ', e['en'][:70].replace('\u0001', ' | '), '=>', e['t'][:70])

if a.json: json.dump(flagged, open(a.json, 'w', encoding='utf-8'), ensure_ascii=False); print(len(flagged), 'flagged (string, word) pairs written to', a.json)
