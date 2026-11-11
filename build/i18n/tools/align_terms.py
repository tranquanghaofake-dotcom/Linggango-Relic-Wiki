#!/usr/bin/env python3
"""Say the game's words the way the game says them: python3 build/i18n/tools/align_terms.py [--dry] [--lang vi] [--show 20]

Two kinds of rule, per language:
  english   an effect, attribute, enchantment or mob (entity) still written in English in a translation ("Cho Speed II", "+1 Looting") becomes the game's own word (official/vanilla_terms.json). The English word must stand
            alone: not followed or preceded by another capitalised word (Speed Potion, Looting Charm are names), and the ambiguous ones are left (Luck, Wither, Flame, Power, Protection, Armor, Infinity, Piercing, Knockback).
  variant   our own wording of a game word becomes the game's (rules below, found by terms.py: pt "Super Pulo" => "Supersalto", es "Salto mejorado" => "Supersalto", ru "стойкость брони" => "твёрдость брони").
A changed entry keeps its state `llm`; --dry only lists the changes (count per rule and examples). docs/I18N.md: the game's word wins over ours for a word the player sees in the game."""
import sys, os, re, json, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tmlib

V = json.load(open(os.path.join(tmlib.HERE, 'official', 'vanilla_terms.json'), encoding='utf-8'))
AMBIGUOUS = {'Luck', 'Wither', 'Flame', 'Power', 'Protection', 'Armor', 'Infinity', 'Piercing', 'Knockback', 'Strength', 'Resistance', 'Speed'}
VI_OK = {'Strength', 'Resistance', 'Speed', 'Protection', 'Knockback'}   # a Vietnamese sentence that still has the English word in capitals means the effect
VARIANTS = {
 'pt': [('Super Pulo', 'Supersalto'), ('super pulo', 'supersalto'), ('Fadiga de Mineração', 'Exaustão'), ('Fadiga de mineração', 'Exaustão'), ('Graça do Golfinho', 'Dádiva Marinha'),
        ('Poder do Conduíte', 'Proteção do Mar'), ('Pilhagem', 'Saque'), ('pilhagem', 'saque'), ('Impulso de Pulo', 'Supersalto'), ('Aumento de Vida', 'Vida Extra')],
 'es': [('Salto mejorado', 'Supersalto'), ('Fatiga de minería', 'Fatiga minera'), ('Poder del canalizador', 'Canalización'), ('Gracia del delfín', 'Gracia delfina'), ('Resplandor', 'Luminiscencia'),
        ('nivel de botín', 'nivel de saqueo'), ('dureza de armadura', 'resistencia de armadura'), ('Dureza de armadura', 'Resistencia de armadura'), ('daño de ataque', 'daño por golpe'), ('Daño de ataque', 'Daño por golpe'),
        (r'\bPrisa(?! minera)\b', 'Prisa minera'), ('Aumento de salud', 'Salud mejorada'), ('Resistencia al retroceso', 'Resistencia al empuje')],
 'ru': [('Огнеупорност', 'Огнестойкост'), ('огнеупорност', 'огнестойкост'), ('Сопротивление огню', 'Огнестойкость'), ('сопротивление огню', 'огнестойкость'),
        ('сильной Усталостью', 'сильным Утомлением'), ('к Усталости', 'к Утомлению'), ('Усталостью', 'Утомлением'), ('Усталость', 'Утомление'), ('Усталости', 'Утомления'),
        ('Медленное падение', 'Плавное падение'), ('Медленного падения', 'Плавного падения'), ('Медленному падению', 'Плавному падению'), ('Медленным падением', 'Плавным падением'),
        ('Насыщение', 'Насыщенность'), ('Насыщения', 'Насыщенности'),
        ('стойкость брони', 'твёрдость брони'), ('стойкости брони', 'твёрдости брони'), ('стойкостью брони', 'твёрдостью брони'), ('Стойкость брони', 'Твёрдость брони'),
        ('урона атаки', 'урона при атаке'), ('урон атаки', 'урон при атаке'), ('урону атаки', 'урону при атаке'), ('Урон атаки', 'Урон при атаке'),
        (r'(опротивлени\w*) отбрасыванию', r'\1 к отбрасыванию'), (r'(опротивлени\w*) отбрасывания', r'\1 к отбрасыванию'),
        ('Дурное знамение', 'Дурной знак'), ('Дурного знамения', 'Дурного знака'), ('Дурному знамению', 'Дурному знаку'),
        ('Силы проводника', 'Силы источника'), ('Сила проводника', 'Сила источника'), ('Силу проводника', 'Силу источника'),
        ('уровень Looting', 'уровень Добычи'), ('уровней Fortune', 'уровней Удачи'), ('уровень Fortune', 'уровень Удачи'), ('+ Looting', '+ Добыча'), ('к Looting', 'к Добыче'), ('Даёт Haste', 'Даёт Спешку'), ('+1 Luck of the Sea и +1 Lure', '+1 Везучий рыбак и +1 Приманка'), ('Морской удачи', 'Везучего рыбака'), ('Морская удача', 'Везучий рыбак'), ('Морскую удачу', 'Везучего рыбака')],
 'vi': [],
}

def english_rules(lang):
    rules = []
    for en, per in sorted(V.items(), key=lambda kv: -len(kv[0])):
        if per.get('_c') not in ('effect', 'attribute', 'enchantment', 'entity') or (en in AMBIGUOUS and not (lang == 'vi' and en in VI_OK)) or lang not in per or lang == 'ru': continue
        rules.append((re.compile(r"(?<![^\W\d_'’\-])" + re.escape(en) + r"(?![^\W\d_'’\-])(?! [A-Z][a-z])"), per[lang], True))   # whole word, accented letters count as letters
    return rules

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--dry', action='store_true'); ap.add_argument('--lang'); ap.add_argument('--show', type=int, default=0); a = ap.parse_args()
    for lang in ([a.lang] if a.lang else ['vi', 'ru', 'pt', 'es']):
        tm = tmlib.load_tm(lang); rules = [(re.compile(p) if p.startswith('(') or '\\' in p else re.compile(re.escape(p)), r, False) for p, r in VARIANTS[lang]] + english_rules(lang)
        changed = collections.Counter(); shown = 0; n = 0
        for k, e in tm.items():
            if e.get('s') in ('official', 'human') or e['d'] == 'names': continue
            forms = {None: e['t']} if isinstance(e['t'], str) else dict(e['t']); new = {}
            for f, t in forms.items():
                t2 = t
                for rx, rep, guard in rules:
                    t3 = rx.sub((lambda m, rep=rep: m.group(0) if re.search(r"([A-Z][a-z]+|\b[Oo]f( the)?|\bthe|\bThe) $", m.string[:m.start()]) else rep) if guard else rep, t2)   # an English word after another capitalised word is part of a name
                    if t3 != t2: changed[rx.pattern[:40]] += 1; t2 = t3
                new[f] = t2
            if new != forms:
                n += 1
                if shown < a.show: shown += 1; print('  %s | %s\n      => %s' % (e['en'][:70].replace('\u0001', ' | '), (e['t'] if isinstance(e['t'], str) else json.dumps(e['t'], ensure_ascii=False))[:110], (new[None] if None in new else json.dumps(new, ensure_ascii=False))[:110]))
                if not a.dry: e['t'] = new[None] if None in new else new
        print('%s: %d entries %s; by rule: %s' % (lang, n, 'would change' if a.dry else 'changed', dict(changed.most_common(8))))
        if not a.dry and n: tmlib.write_tm(lang, tm)

if __name__ == '__main__': main()
