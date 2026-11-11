#!/usr/bin/env python3
"""Merges a batch of translations into the translation memory (docs/I18N.md).

  python3 build/i18n/tools/merge.py --domain fx list.json batch.txt [--dry] [--state llm]
  python3 build/i18n/tools/merge.py --domain names --pairs batch.json [--dry]

list.json   a JSON array of English strings; batch.txt has one line per string: `index|vi|ru|pt|es` (index = position in list.json; a line break inside a text is written \\n).
--pairs     instead of a list: batch.json = {english: [vi, ru, pt, es]} (plural sentences: key "<one>\\u0001<other>" and value {lang: {form: text}}).

A text written `=` is the English itself (a proper noun that stays). For `--domain names` a language that already has the game's own name for that English (official/<lang>.json) is skipped: the game's name wins.
Every text is checked against its English (the numbers must be the same digits, {placeholders} equal, tags equal); the ones that differ are listed and still written unless --strict.
--dry only reports. A new entry gets state --state (default llm = machine translation, awaiting a human) and goes in the domain file tm/<lang>/<domain>.json.
"""
import sys, json, re, argparse, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tmlib

LANGS = ['vi', 'ru', 'pt', 'es']
num = lambda t: sorted(re.findall(r'\d+', re.sub(r'(?<=\d)[.,  ](?=\d{3}\b)', '', re.sub(r'(?<=\d)[.,](?=\d)', '', t))))
ph = lambda x: sorted(re.findall(r'\{\w+\}', x)); tg = lambda x: sorted(set(re.findall(r'</?[A-Za-z]\w*|href="[^"]*"', x)))

def official_names(lang):
    """The English names that the game's own translation covers (official/<lang>.json names are by id; the English of an id is read from the built data)."""
    import json as J
    en_of = {}
    for f in ('data.js', 'gear_data.js'):
        t = open(os.path.join(tmlib.SRC, f), encoding='utf-8').read()
        for m in re.finditer(r'\{"id":"([^"]+)","n":"((?:[^"\\]|\\.)*)"', t): en_of[m.group(1)] = J.loads('"' + m.group(2) + '"')
    o = J.load(open(os.path.join(tmlib.HERE, 'official', lang + '.json'), encoding='utf-8'))['names']
    return {en_of[i] for i in o if i in en_of}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--domain', required=True); ap.add_argument('--dry', action='store_true'); ap.add_argument('--strict', action='store_true')
    ap.add_argument('--state', default='llm'); ap.add_argument('--pairs', action='store_true'); ap.add_argument('src'); ap.add_argument('batch', nargs='?')
    a = ap.parse_args(); got = {}; bad = []
    if a.pairs:
        for en, forms in json.load(open(a.src, encoding='utf-8')).items(): got[en] = forms
    else:
        lst = json.load(open(a.src, encoding='utf-8'))
        for ln, line in enumerate(open(a.batch, encoding='utf-8').read().split('\n'), 1):
            if not line.strip(): continue
            parts = line.rstrip('|').split('|')
            if len(parts) != 5 or not parts[0].isdigit() or int(parts[0]) >= len(lst): bad.append((ln, 'format', line[:80])); continue
            got[lst[int(parts[0])]] = [p.replace('\\n', '\n') for p in parts[1:]]
    for en, forms in got.items():
        forms[:] = [en if f == '=' else f for f in forms]
        for lang, t in zip(LANGS, forms):
            for f in ([t] if isinstance(t, str) else list(t.values())):
                if not f.strip(): bad.append((en[:50], 'empty ' + lang, '')); continue
                src = en.split('\u0001')[0] if isinstance(t, dict) else en
                if not isinstance(t, dict) and num(src) != num(f): bad.append((en[:60], 'numbers ' + lang, f[:70]))
                if ph(f) != ph(src) and not isinstance(t, dict): bad.append((en[:60], 'placeholders ' + lang, f[:70]))
                if tg(f) != tg(src) and not isinstance(t, dict): bad.append((en[:60], 'tags ' + lang, f[:70]))
    print(len(got), 'strings;', len(bad), 'to look at')
    for b in bad[:60]: print('  ', b)
    if a.dry or (a.strict and bad): return 1 if bad and a.strict else 0
    for k, lang in enumerate(LANGS):
        tm = tmlib.load_tm(lang); new = 0; skip = official_names(lang) if a.domain == 'names' else set(); skipped = 0
        for en, forms in got.items():
            if en in skip: skipped += 1; continue
            h = tmlib.hsh(en); new += h not in tm
            old = tm.get(h, {}); tm[h] = {"en": en, "t": forms[k], "s": a.state, "d": old.get("d", a.domain)}
        tmlib.write_tm(lang, tm); print(lang, 'written', len(got) - skipped, '(%d new)' % new, '' if not skipped else '; %d left to the game\'s own name' % skipped)
    return 0

if __name__ == '__main__': sys.exit(main())
