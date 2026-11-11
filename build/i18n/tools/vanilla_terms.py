#!/usr/bin/env python3
"""Minecraft's own words in the four languages, as {English: {vi, ru, pt, es}} (official/vanilla_terms.json): effects, attributes, mobs, enchantments, biomes, dimensions, blocks, items.

  python3 build/i18n/tools/vanilla_terms.py <harvest cache dir>      (the dir holds vanilla/{en_us,vi_vn,ru_ru,pt_br,es_mx,es_es}.json: python3 build/i18n/harvest.py vanilla <cache dir>)

The file is the reference for the glossary (qa.py, terms.py) and for composing the name of a modded item out of vanilla words. A word the game leaves in English in a language is left out of that language.
Where one English word has several keys (Stone the block and the item) the first of this order wins: effect, attribute, entity, enchantment, biome, dimension, block, item; es_mx before es_es (D2 in docs/plans/2026-11-08-multilingual.md)."""
import sys, os, json, re
D = os.path.join(sys.argv[1], 'vanilla'); L = {k: json.load(open(os.path.join(D, f + '.json'), encoding='utf-8')) for k, f in [('en', 'en_us'), ('vi', 'vi_vn'), ('ru', 'ru_ru'), ('pt', 'pt_br'), ('es', 'es_mx'), ('es2', 'es_es')]}
PRE = ['effect.minecraft.', 'attribute.name.generic.', 'attribute.name.', 'entity.minecraft.', 'enchantment.minecraft.', 'biome.minecraft.', 'dimension.minecraft.', 'block.minecraft.', 'item.minecraft.']
out = {}
for pre in PRE:
    for k, en in L['en'].items():
        if not k.startswith(pre) or not isinstance(en, str) or k.count('.') > pre.count('.') or len(en) > 40 or '%' in en: continue
        row = out.setdefault(en, {'_c': pre.split('.')[0] if pre != 'attribute.name.' else 'attribute'})   # _c: effect, attribute, entity, enchantment, biome, dimension, block, item
        for lg, src in (('vi', 'vi'), ('ru', 'ru'), ('pt', 'pt'), ('es', 'es'), ('es', 'es2')):
            t = L[src].get(k)
            if lg not in row and isinstance(t, str) and t.strip() and t != en: row[lg] = t
out = {k: v for k, v in sorted(out.items()) if len(v) > 1}
json.dump(out, open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'official', 'vanilla_terms.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
print(len(out), 'terms;', {l: sum(1 for v in out.values() if l in v) for l in ('vi', 'ru', 'pt', 'es')})
