#!/usr/bin/env python3
"""One-time edit of src/data.js for Linggango 6.6.6hf (from 6.6.5b4). Usage: v666_curios.py <repo> <work dir>
Work dir: pack/src = the unzipped 6.6.6hf client zip, pack/mods = the jars, rec.json and lang_all.json from the pack.
1. Curios of mods the pack removed (Powah, Dark Doppelganger) are deleted.
2. kubejs curio_dedupe.js: 33 duplicate accessories lose their recipes and every loot table hands out the kept copy
   (loot modifier linggango_integration:curio_dedupe). The removed copy goes to U (unobtainable); the kept copy takes over
   its loot sources (and its earlier Act when that came from loot). Recipe grids that used a removed copy use the kept one.
3. Keeper gates (linggango_tweaks:gated/*) were loosened: gk follows the 6.6.6 tags; an Act that only came from the old gate
   falls back to the item's other limits (6.6.6 gate of its ingredients, Act of curio ingredients); a higher gate raises it.
4. New curios (Fallen Traits, Summonity 0.1.7, Goety 2.5.58, Goety Awaken, Armageddon Ravager Horn, Ring of Ender)."""
import json, re, sys, os, glob, zipfile
R, W = sys.argv[1], sys.argv[2]
P = os.path.join(R, 'build', 'src', 'data.js')
s = open(P, encoding='utf-8').read()
dec = json.JSONDecoder()
def grab(name):
    i = s.index(name + '=') + len(name) + 1
    v, j = dec.raw_decode(s, i); return v, i, j
D, d0, d1 = grab('const D')
U, u0, u1 = grab(',U')
NM, n0, n1 = grab(',NM')
lang = json.load(open(W + '/lang_all.json')); rec = json.load(open(W + '/rec.json'))
nm = lambda i: NM.get(i) or re.sub(r'§.', '', lang.get('item.%s.%s' % tuple(i.split(':', 1)), lang.get('block.%s.%s' % tuple(i.split(':', 1)), i.split(':')[1].replace('_', ' ').title())))
BY = {d['id']: d for d in D}
log = []

# 1. removed mods
GONE = ('powah:', 'darkdoppelganger:')
n = len(D); D = [d for d in D if not d['id'].startswith(GONE)]; U = [u for u in U if not u['id'].startswith(GONE)]
log.append('removed-mod curios deleted: %d' % (n - len(D)))
BY = {d['id']: d for d in D}

# 2. dedupe
dd = open(W + '/pack/src/overrides/kubejs/server_scripts/mods/global/curio_dedupe.js', encoding='utf8').read()
SW = dict(re.findall(r'"([a-z0-9_]+:[a-z0-9_]+)":\s*"([a-z0-9_]+:[a-z0-9_]+)"', dd))
for a, b in SW.items():
    ra, kb = BY.get(a), BY.get(b)
    if kb is None and ra is not None:   # the kept copy was not on the wiki (Panic Necklace): take the entry over
        ui = next((u for u in U if u['id'] == b), None)
        kb = dict(ra, id=b, n=(ui or {}).get('n') or nm(b), m=(ui or {}).get('m') or ra['m'], gr=None, uid=[])
        kb['src'] = ['Since 6.6.6 every chest and mob that gave %s gives this instead: %s' % (ra['n'], ' '.join(ra['src']))]
        kb['src0'] = ra['src0'] + ' (replaces %s)' % ra['n']
        D.append(kb); BY[b] = kb; U = [u for u in U if u['id'] != b]
    elif kb is not None and ra is not None and ra.get('g') == 'Loot':
        kb['src'] = ['Since 6.6.6 the chests and mobs that gave %s give this instead: %s' % (ra['n'], ra['src'][0])] + kb['src']
        if ra['a'] < kb['a'] or (ra['a'] == kb['a'] and kb.get('g') != 'Loot'):
            kb['a'] = kb['t'] = kb['ac'] = ra['a']; kb['g'] = 'Loot'
            kb['why'] = [w for w in kb.get('why', []) if not w.startswith('Earliest at')]
            kb['src0'] = ra['src0'] + ' (replaces %s)' % ra['n']
    if ra is not None:
        D = [d for d in D if d['id'] != a]; BY.pop(a, None)
        U = [u for u in U if u['id'] != a]
        U.append({'id': a, 'n': ra['n'], 'm': ra['m'], 'why': 'Removed as a duplicate in 6.6.6: its recipes are gone and loot gives the %s %s instead' % ((kb or {}).get('m', b.split(':')[0]), nm(b)), 'i': 1})
    elif not any(u['id'] == a for u in U): pass
    else:
        for u in U:
            if u['id'] == a: u['why'] = 'Removed as a duplicate in 6.6.6: its recipes are gone and loot gives the %s %s instead' % ((kb or {}).get('m', b.split(':')[0]), nm(b))
for d in D:   # recipe grids use the kept copy
    for c in (d.get('gr') or {}).get('c') or []:
        if c and c[0] in SW: c[0] = SW[c[0]]
log.append('dedupe: %d removed copies to U' % len(SW))

# 3. gates
T = {'iron': 2, 'gold': 3, 'emerald': 4, 'diamond': 5, 'netherite': 6, 'elvenite': 7, 'voiderite': 8, 'cataclysm': 9, 'blood': 10, 'sun': 11}
TN = {2: 'Iron', 3: 'Gold', 4: 'Emerald', 5: 'Diamond', 6: 'Netherite', 7: 'Elvenite', 8: 'Voiderite', 9: 'Cataclysm', 10: 'Blood', 11: 'Sun'}
TB = {2: 'Iron Colossus', 3: 'the Goblin Lord', 4: 'Arion', 5: 'Eldorath', 6: 'Zoranth', 7: 'the Elvenite Paladin', 8: 'Vaedric', 9: 'The Calamities', 10: 'Sanghor', 11: 'Zoranth Newborn'}
G = {}
for t, a in T.items():
    for x in json.load(open(W + '/pack/src/overrides/kubejs/data/linggango_tweaks/tags/items/gated/%s.json' % t))['values']:
        i = x if isinstance(x, str) else x['id']
        if i not in G or G[i] > a: G[i] = a
ch = 0
for d in D:
    old, new = d.get('gk') or 0, G.get(d['id'], 0)
    if old == new: continue
    ch += 1
    ings = [c[0] for c in (d.get('gr') or {}).get('c') or [] if c]
    floor = max([new] + [G.get(i, 0) for i in ings] + [BY[i]['a'] for i in ings if i in BY and BY[i]['a'] != 6.3] + [6.3 for i in ings if i in BY and BY[i]['a'] == 6.3])
    gate_why = lambda w: w.startswith(('Locked behind the', 'Keeper-gated')) or 'is gated behind Act' in w
    if new > d['a']: d['a'] = d['t'] = d['ac'] = new
    elif old and d['a'] == old and new < old and not [w for w in d.get('why', []) if not gate_why(w)]:
        d['a'] = d['t'] = d['ac'] = floor
    d['why'] = [w for w in d.get('why', []) if not gate_why(w)]
    if new: d['gk'] = new; d['why'].append('Locked behind the %s gate (defeat %s)' % (TN[new], TB[new]))
    else: d.pop('gk', None)
    d['src'] = [x for x in d['src'] if not x.startswith('Key requirement: locked behind')]
    if new: d['src'].append('Key requirement: locked behind the %s gate until you defeat %s.' % (TN[new], TB[new]))
    d['src0'] = re.sub(r' · key item: gated \w+', ' · key item: gated %s' % TN[new] if new else '', d['src0'])
log.append('gate changes: %d curios' % ch)

# 4. new curios
JARS = {os.path.basename(j): j for j in glob.glob(W + '/pack/mods/*.jar')}
def rjson(r):
    ns, p = r['id'].split(':', 1)
    f = W + '/pack/src/overrides/kubejs/data/%s/recipes/%s.json' % (ns, p)
    if os.path.exists(f): return json.load(open(f))
    j = JARS.get(r.get('src'))
    if j:
        z = zipfile.ZipFile(j)
        try: return json.loads(z.read('data/%s/recipes/%s.json' % (ns, p)))
        except KeyError: return None
def cell(v):
    if isinstance(v, list): v = v[0] if v else None
    if not isinstance(v, dict): return None
    if v.get('item'): return [v['item'], '']
    if v.get('tag'):
        t = v['tag']; rep = {'forge:storage_blocks/iron': 'minecraft:iron_block', 'minecraft:boats': 'minecraft:oak_boat'}.get(t)
        return [rep or t, '#' + t]
STN = {'minecraft:crafting_shaped': 'Crafting Table', 'minecraft:crafting_shapeless': 'Crafting Table', 'goety:ritual': 'Ritual Goety (Dark Altar)'}
def grid(i):
    for r in rec['recipes'].get(i, []):
        o = rjson(r)
        if not o: continue
        t = o.get('type', '')
        if 'pattern' in o:
            pat = o['pattern']; w = max(len(x) for x in pat)
            c = [cell(o['key'].get(ch)) if ch != ' ' else None for row in pat for ch in row.ljust(w)]
            return {'w': w, 'h': len(pat), 'c': c, 'st': STN.get(t, t), 'n': 1, 'l': 0}
        ings = o.get('ingredients') or []
        c = [cell(x) for x in ings]; c = [x for x in c if x]
        if c: return {'w': 3, 'h': (len(c) + 2) // 3, 'c': c, 'st': STN.get(t, t), 'n': 1, 'l': 1}
def ingnames(g):
    seen = []
    for c in g['c'] if g else []:
        if c and nm(c[0]) not in seen: seen.append(nm(c[0]))
    return seen
RAR = {0: ('Common', '#FFFFFF'), 1: ('Uncommon', '#FFFF55'), 2: ('Rare', '#55FFFF'), 3: ('Epic', '#FF55FF'), 4: ('Legendary', '#FFAA00'), 5: ('Mythic', '#14CDFF'), 6: ('Legendary', '#FFAA00')}
SC = {0: .5, 1: 1.07, 2: 1.76, 3: 2.28, 4: 2.76, 5: 3.18, 6: 2.5}
FT = 'Fallen Traits'
# id: (mod, slots, act, rarity, roles, mech tags, effect line, stat lines, why, key item note, tag, config lines)
NEW = {
 'fallen_traits:rage_glove': (FT, ['Hands'], 6.3, 3, ['ME', 'RA', 'MA'], ['l:Trait L2'], '+25% damage per consecutive hit, up to 5× total; resets when you are hit or after 10 s',
   ['Attacks deal 25% more damage per consecutive hit, up to 5× total.', 'Resets on being hit or after 10 s without attacking.', 'Raises your difficulty by 50 levels and the legendary-trait chance by 2%.'],
   ['Needs a Chaos Ingot (its 6.6.6 recipe takes Shulkerate Ingot: shulkers, after the Ender Dragon)'], 'Chaos Ingot (L2 Hostility)', 'pack', ['furyDamageIncreasePerHit = 0.25', 'furyMaxDamageMultiplier = 5.0', 'furyExtraDifficulty = 50']),
 'fallen_traits:invulnerability_breaker': (FT, ['Hands'], 11, 4, ['ME', 'RA', 'MA', 'SU'], ['l:Trait L2'], 'Your hits cut the target\'s invulnerability frames by 5 ticks; +5 ticks of your own when hurt',
   ['Reduces hit targets\' i-frames by 5 ticks.', 'Increases your own i-frames by 5 ticks when hurt.', 'Raises your difficulty by 100 levels.'],
   ['Needs the Imagine Breaker (Helionite Block, Act XI)'], 'Imagine Breaker (L2 Hostility)', 'pack', ['invulnBreakerTargetInvulnReductionTicks = 5', 'invulnBreakerWearerInvulnBonusTicks = 5', 'invulnBreakerExtraDifficulty = 100']),
 'fallen_traits:phasewalkers_ring': (FT, ['Ring'], 6.3, 3, ['MO', 'TA'], ['l:Dodge'], 'A dodge teleports you behind the attacker instead of only negating the hit',
   ['Dodging attacks teleports you behind your attacker instead of negating damage.'], ['Needs a Chaos Ingot and a Shulkerate Ingot (shulkers, after the Ender Dragon)'], 'Shulkerate Ingot', 'tooltip', []),
 'fallen_traits:titans_heart': (FT, ['Charm'], 6.3, 3, ['TA', 'HE'], ['l:Trait L2'], '+50% size, +50% max health, +50% armor; raises difficulty by 300 levels',
   ['Gain +50% Size, +50% Max Health and +50% Armor.', 'Raises your difficulty by 300 levels and the legendary-trait chance by 50%.'], ['Needs a Miracle Ingot and a Warden Bone Shard'], 'Miracle Ingot (L2 Hostility)', 'pack', ['titansHeartSize = 0.5', 'titansHeartHealth = 0.5', 'titansHeartArmor = 0.5', 'titansHeartExtraDifficulty = 300']),
 'fallen_traits:feyweight': (FT, ['Charm'], 6.3, 3, ['MO'], ['l:Dodge'], '−50% size, +100% movement speed, +50% attack speed, +10% dodge; larger enemies deal 20% more damage to you',
   ['Gain −50% Size, +100% Movement Speed, +50% Attack Speed and +10% Dodge Chance.', 'Larger enemies deal 20% more damage to you.'], ['Needs a Miracle Ingot'], 'Miracle Ingot (L2 Hostility)', 'pack', ['feyweightSizeReduction = 0.5', 'feyweightMovementSpeed = 1.0', 'feyweightAttackSpeed = 0.5', 'feyweightDodgeChance = 0.1', 'feyweightLargerEnemyDamage = 0.2']),
 'fallen_traits:universal_point_of_discontinuity': (FT, ['Head', 'Back'], 6.3, 3, ['UT', 'TA'], [], 'Right-click to cycle: repel entities (8 blocks), slow them up to 90% (16 blocks) or pull them (8 blocks)',
   ['Repelling: pushes entities away within 8 blocks, strength 0.3.', 'Asymptote: slows entities by up to 90% within 16 blocks.', 'Pulling: attracts entities within 8 blocks, strength 0.15.', 'Right-click to cycle modes.'], ['Needs a Miracle Ingot, a Blackstone Core and a Wither Force Field'], 'Miracle Ingot (L2 Hostility)', 'pack', ['updRepellingRange = 8', 'updAsymptoteSlowStrength = 0.9', 'updPullingRange = 8']),
 'fallen_traits:divine_singularity': (FT, ['Charm', 'Hostility Curse'], 6.3, 3, ['UT'], ['l:Trait L2'], 'The Cleanse trait no longer clears your beneficial effects',
   ['Cleanse effect will not clear any beneficial effect.'], ['Needs a Transcendent Ingot (Miracle Ingot + Transcendent Dust from Hostile Cores)'], 'Transcendent Ingot (Fallen Traits)', 'tooltip', []),
 'fallen_traits:fury_of_infernal': (FT, ['Hostility Curse'], 6.3, 4, ['ME', 'RA', 'MA'], ['l:Trait L2', 'l:Crit'], '+3% damage per trait level of the target, +5% crit damage per legendary level; mob traits twice as frequent',
   ['Gain 3% Damage per Trait Level the attacked enemy has (legendary not counted).', 'Gain 5% Crit Damage per Legendary Trait level.', 'Mobs with 10+ trait levels grant 25% Attack Speed, with 20+ grant 25% Movement Speed (+5% per block from the enemy).', 'Mob traits are 100% more frequent; Infernal and Berserk can spawn together; raises difficulty by 500 levels.'],
   ['Needs a Transcendent Ingot and the Curse of Pride'], 'Transcendent Ingot (Fallen Traits)', 'pack', ['furyInfernalExtraLevel = 500', 'furyInfernalDamagePerTraitLevel = 0.03', 'furyInfernalCritDamagePerLegendaryLevel = 0.05']),
 'fallen_traits:law_of_scale': (FT, ['Hostility Curse'], 6.3, 4, ['ME', 'RA', 'MA'], ['l:Trait L2'], 'Up to 20% current-health damage to larger enemies, knockback through resistance on smaller ones; +5 random traits on mobs',
   ['Deal up to 20% current health damage to larger enemies, scaling with size difference.', 'Knock back smaller enemies on hit, ignoring knockback resistance.', '+10% Attack Speed for every 50% smaller you are than your target, +10% Damage for every 50% larger.', 'Mobs have 5 more random traits; raises difficulty by 500 levels.'],
   ['Crafted from Feyweight and Titan\'s Heart plus a Transcendent Ingot'], 'Transcendent Ingot (Fallen Traits)', 'pack', ['lawOfScaleMaxDamagePercent = 0.2', 'lawOfScaleExtraTraitCount = 5', 'lawOfScaleExtraDifficulty = 500']),
 'fallen_traits:wrath_of_fenrir': (FT, ['Hostility Curse'], 6.3, 4, ['ME', 'RA', 'MA'], ['l:Trait L2'], '+5% damage per difficulty level gap against stronger mobs; disables 1–3 traits of hit mobs for 60 s; doubles spawns',
   ['Gain 5% attack damage per difficulty level difference against mobs with a higher level than you.', 'Temporarily disables 1–3 traits of attacked mobs for 60 s.', 'Increases enemy spawn rate by 100%; raises difficulty by 400 levels.'],
   ['Needs the Curse of Wrath and a Transcendent Ingot'], 'Transcendent Ingot (Fallen Traits)', 'pack', ['wrathOfFenrirDamagePerLevelDiff = 0.05', 'wrathOfFenrirTraitDisableDuration = 60', 'wrathOfFenrirExtraDifficulty = 400']),
 'fallen_traits:yggdrasil_root': (FT, ['Charm', 'Back'], 6.3, 3, ['UT'], ['l:Trait L2'], 'Unseals up to 3 sealed items at once, at double speed',
   ['Unseals up to 3 items simultaneously at 2× speed.'], ['Needs a Transcendent Ingot and a Pocket of Restoration'], 'Transcendent Ingot (Fallen Traits)', 'pack', ['yggdrasilRootMaxUnsealSlots = 3', 'yggdrasilRootUnsealSpeedMultiplier = 2.0']),
 'fallen_traits:omniscient_looting_charm': (FT, ['Charm', 'Hostility Curse'], 11, 6, ['UT'], ['l:Trait L2', 'l:Luck'], 'All four Looting Charms in one slot; mobs cannot drop their equipment',
   ['Combines the power of all Looting Charms.', 'Mobs cannot drop their equipment.'], ['Crafted from the Unpolished, Magical, Chaotic and Miraculous Looting Charms (Miraculous: Act XI)'], 'Miraculous Looting Charm', 'tooltip', []),
 'fallen_traits:hand_of_creation': (FT, ['Hands', 'Hostility Curse'], 11, 5, ['ME', 'RA', 'MA', 'SU'], ['l:Trait L2'], 'Every glove effect in one: rage stacks to 5×, hits ignore i-frames, magic protection and dodge, DoTs tick every tick; all mobs spawn with max traits',
   ['Combines all effects of Gloves and improves them.', 'Attacks deal +25% per hit, up to 5×; resets after 10 s without attacking.', 'All your damage ignores I-Frames and bypasses Magical Protection and Dodge Chance; +5 ticks of your own i-frames when hurt.', 'Damage-over-time effects you inflict tick every game tick; each hit stacks Soul Flame one level higher.', 'Mobs you kill drop no Hostility loot; all mobs spawn with max-level traits and unlimited traits.'],
   ['Crafted from Invulnerability Breaker, Rage Glove, Flaming Thorn, Infinity Glove, Imagine Breaker and Platinum Star'], 'Imagine Breaker and Infinity Glove', 'tooltip', ['handOfCreationDamageIncreasePerHit = 0.25', 'handOfCreationMaxDamageMultiplier = 5.0']),
 'summonity:ember_locket': ('Summonity', ['Necklace'], 0, 1, ['SU'], ['e:Fire'], 'Every 4th minion hit sets the target on fire for 4 s; minions deal +10% damage to burning enemies',
   ['Every 4 Minion hits ignite the target for 4 seconds.', '+10% Minion Damage against burning enemies.'], [], '', 'pack', ['emberLocketRequiredHits = 4', 'emberLocketBurnDurationSeconds = 4', 'emberLocketBurningDamageBonus = 0.1']),
 'summonity:combustion_chamber': ('Summonity', ['Charm'], 5, 2, ['SU'], ['e:Fire'], 'Upgrade of the Ember Locket: minion hits on burning enemies build Heat, +2% damage per stack up to 10',
   ['Keeps the Ember Locket effects.', 'Minion hits against burning enemies build Heat: +2% damage per stack, up to 10 stacks.', 'Heat expires after 3 seconds without another hit.'], ['Needs a Blaze Rod (Nether)'], 'Blaze Rod', 'pack', ['combustionChamberMaxHeat = 10', 'combustionChamberDamagePerHeat = 0.02', 'combustionChamberHeatDurationTicks = 60']),
 'summonity:brimstone_singularity': ('Summonity', ['Charm'], 7, 3, ['SU'], ['e:Fire'], 'Upgrade of the Combustion Chamber: at full Heat the target erupts for 200% of the minion\'s damage in 4 blocks',
   ['Keeps the Combustion Chamber effects; +20% Minion Damage.', 'At 10 Heat the target explodes, dealing 200% of the triggering Minion\'s damage to every enemy within 4 blocks and igniting them.', 'Enemies killed at maximum Heat explode immediately. 3 second cooldown.'],
   ['Needs Profanum (Profaned Ore: Elvenite-tier pickaxe since 6.6.6)'], 'Profanum Ingot', 'pack', ['brimstoneSingularityMinionDamageBonus = 0.2', 'brimstoneSingularityEruptionDamage = 2.0', 'brimstoneSingularityEruptionRadius = 4.0']),
 'summonity:hollow_mask': ('Summonity', ['Head'], 6, 3, ['SU'], [], 'Minion hits fill a soul meter; when full your minions go berserk for 8 s (+35% damage and attack speed)',
   ['+12% Minion Damage, Attack Speed and Movement Speed.', 'Gain Soul on every 10th Minion hit; full Soul enrages Minions for 8 seconds: +35% Damage and +35% Attack Speed.', '30 second cooldown.'], ['Needs Empty Essence'], 'Empty Essence (Terramity)', 'pack', ['hollowMaskDamageBonus = 0.12', 'hollowMaskRageDamageBonus = 0.35', 'hollowMaskRageDurationTicks = 160']),
 'summonity:copper_whistle': ('Summonity', ['Charm'], 0, 1, ['SU'], [], 'Whip hits rally your minions: +10% minion attack speed for 4 s',
   ['Whip hits rally your Minions for 4 seconds: +10% Minion Attack Speed.', 'Only one whistle can be worn.'], [], '', 'pack', ['copperWhistleDurationTicks = 80', 'copperWhistleAttackSpeedBonus = 0.1']),
 'summonity:war_whistle': ('Summonity', ['Charm'], 5, 2, ['SU'], [], 'Marking an enemy with your whip rallies your minions: +25% attack speed and +10% damage for 5 s',
   ['Whip marking an enemy rallies your Minions for 5 seconds: +25% Minion Attack Speed, +10% Minion Damage.', 'Replaces the War Horn (old ones convert).'], ['Needs Netherite Scrap (Nether)'], 'Netherite Scrap', 'pack', ['warWhistleDurationTicks = 100', 'warWhistleAttackSpeedBonus = 0.25', 'warWhistleDamageBonus = 0.1']),
 'summonity:stygian_whistle': ('Summonity', ['Charm'], 5, 2, ['SU'], ['l:Lifesteal'], 'Whip hits empower your minions for 5 s: +5% minion lifesteal',
   ['Whip hits empower your Minions for 5 seconds: +5% Minion Lifesteal.', '30 second cooldown.'], ['Needs Chthonian Void (Chthonic Cathedral, Nether)'], 'Chthonian Void (Terramity)', 'pack', ['stygianWhistleDurationTicks = 100', 'stygianWhistleLifesteal = 0.05']),
 'summonity:spectral_whistle': ('Summonity', ['Charm'], 0, 2, ['SU'], [], 'Whip hits awaken restless spirits for 5 s: minion hits release homing souls for 50% damage',
   ['Whip hits awaken Restless Spirits for 5 seconds.', 'Minion hits release a homing soul that deals 50% damage to another enemy, or returns to its victim.'], [], 'Spectral Soul (Terramity)', 'pack', ['spectralWhistleDurationTicks = 100', 'spectralWhistleDamageMultiplier = 0.5']),
 'goety:ring_of_wrecking': ('Goety', ['Ring'], 3, 1, ['UT'], [], 'Mobs killed by you or your servants no longer drop damaged gear (bosses unaffected)',
   ['Mobs killed by the wearer or servants will no longer drop damageable equipment.'], [], '', 'tooltip', []),
 'goety:soul_healer': ('Goety', ['Charm'], 3, 2, ['HE', 'SU'], [], 'Heals you from soul energy on a key press; an illager servant can carry it, heal itself and give you half the souls it collects',
   ['Heals the user from a range of an amount. If equipped, press the ability key to use it.', 'Can be given to an Illager servant, which gains soul energy to use it.'], [], '', 'tooltip', []),
 'goetyawaken:assassin_glove': ('Goety Awaken', ['Hands'], 4, 2, ['ME'], [], '+100% back-stab damage with daggers and rapiers',
   ['When wielding daggers or rapiers, back stab damage is increased by 100%.'], [], '', 'tooltip', []),
 'goetyawaken:dauntless_gloves': ('Goety Awaken', ['Hands'], 4, 2, ['ME'], [], '+25% attack speed with claymores',
   ['Increases attack speed by 25% when using Claymore weapons.'], [], '', 'tooltip', []),
 'goetyawaken:detonation_ring': ('Goety Awaken', ['Ring'], 4, 2, ['RA'], ['e:Fire'], '25% of your arrows become explosive arrows',
   ['25% chance for arrows to become Explosive Arrows.'], [], '', 'tooltip', []),
 'goetyawaken:gatling_charm': ('Goety Awaken', ['Charm'], 4, 1, ['MA'], [], 'Sneak-casting Arrow Rain or Blizzard spawns every projectile in front of you',
   ['When casting Arrow Rain or Blizzard while sneaking, all projectiles spawn in front of the caster.'], [], '', 'tooltip', []),
 'goetyawaken:ripplewalk': ('Goety Awaken', ['Feet'], 4, 1, ['MO'], [], 'Run on the surface of water and other fluids',
   ['Allows running on fluid surfaces.'], [], '', 'tooltip', []),
 'goetyawaken:swelling_pendant': ('Goety Awaken', ['Necklace'], 3, 1, ['SU'], [], 'Stores slimeballs from your inventory to make your summoned slimes bigger and stronger',
   ['Absorbs slimeballs from your inventory, storing them to empower your summoned slimes with greater size and power.'], [], '', 'tooltip', []),
 'armageddon_mod:ravager_horn': ('Armageddon', ['Accessory'], 0, 1, ['ME', 'MO'], [], 'Strength I while sprinting',
   ['When worn and while sprinting: applies Strength I to the wearer.'], [], '', 'tooltip', []),
 'enigmaticlegacy:ender_ring': ('Enigmatic Legacy', ['Ring'], 5, 1, ['UT'], [], 'Open your Ender Chest from anywhere',
   ['Lets you open the contents of your Ender Chest anywhere, across distances and dimensions.'], [], '', 'tooltip', []),
}
SRC = {'armageddon_mod:ravager_horn': 'Dropped by Ravagers (Armageddon code drop, new in 6.6.6; chance not readable from data).'}
add = 0
for i, (mod, sl, a, r, ro, mt, fx, st, why, key, tg, sr) in NEW.items():
    if i in BY: continue
    g = grid(i); names = ingnames(g)
    if g: src = ['%s from %s.' % ('Perform a Goety ritual with' if g['st'].startswith('Ritual') else 'Craft at a Crafting Table', ', '.join(names[:-1]) + (' and ' + names[-1] if len(names) > 1 else names[0]))]
    else: src = [SRC.get(i, 'Source not found in the pack data.')]
    src[0] = src[0].replace('Craft at a Crafting Table from', 'Craft at a Crafting Table from') if g else src[0]
    if g and g['st'].startswith('Ritual'): src[0] = src[0].replace(' from ', ' ', 1)
    if G.get(i): src.append('Key requirement: locked behind the %s gate until you defeat %s.' % (TN[G[i]], TB[G[i]]))
    elif key: src.append('Hardest ingredient: %s.' % key)
    src0 = ('%s: %s' % ('Ritual Goety' if g and g['st'].startswith('Ritual') else 'Crafting Table', ', '.join(names)) if g else src[0].rstrip('.'))
    if G.get(i): src0 += ' · key item: gated %s' % TN[G[i]]
    elif key: src0 += ' · key item: %s' % key
    a = max(a, G.get(i, 0))
    e = {'id': i, 'n': nm(i), 'm': mod, 'sl': sl, 'a': a, 'g': 'Craft' if g else 'Loot', 'fx': fx, 'src': src, 'k': 1, 'st': st, 'nw': 1, 'tg': [tg] * len(st),
         'gr': g, 'uid': [], 't': a, 'r': r, 'sc': SC[r], 'ac': a, 'pw': 1.0, 'gp': None,
         'why': list(why) + (['Locked behind the %s gate (defeat %s)' % (TN[G[i]], TB[G[i]])] if G.get(i) else []),
         'pwy': [], 'ro': ro, 'mt': mt, 'br': min(r, 5), 'src0': src0, 'sr': ['; '.join(sr)] * len(st) if sr else [], 'pr': 0, 'sca': 0, 'ig': list(RAR[r])}
    if G.get(i): e['gk'] = G[i]
    if not g: e.pop('gr')
    D.append(e); BY[i] = e; add += 1
    NM.setdefault(i, e['n'])
    for c in (g or {}).get('c') or []:   # names for new ingredients (Transcendent Ingot, Hostile Core…)
        if c and ':' in c[0] and not c[1]: NM.setdefault(c[0], nm(c[0]))
log.append('new curios: %d' % add)

d = lambda x: json.dumps(x, ensure_ascii=False, separators=(',', ':'))
# splice back in reverse order of position
parts = sorted([(d0, d1, d(D)), (u0, u1, d(U)), (n0, n1, d(NM))], reverse=True)
for a, b, txt in parts: s = s[:a] + txt + s[b:]
open(P, 'w', encoding='utf-8').write(s)
print('\n'.join(log))
