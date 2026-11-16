#!/usr/bin/env python3
"""Record a short clip of every spell, from the real game, into OUT_DIR/<ns>__<spell>.mp4 plus a poster OUT_DIR/<ns>__<spell>.jpg (resumable: an existing clip is kept).
Usage: python3 -I spell_clips.py SERVER_DIR OUT_DIR --log SERVER_LOG --speed 0.25 [--only ns:spell,...] [--ns irons_spellbooks,...] [--limit N]
Recipe 3 (docs/plans/2026-11-14-mechanics-effects-spells.md, "Clip: the recipe"). Needs, running:
- a Forge 1.20.1 dedicated server in SERVER_DIR, flat world, offline mode, `cmd.fifo` as its stdin (`tail -f cmd.fifo | java ... nogui > SERVER_LOG`),
  the client's mods plus CMDCam 2.2.1 and CreativeCore on both sides; server.properties spawn-animals=true and spawn-npcs=true (false makes the server
  discard every animal and villager each tick, summoned ones too; natural spawning stays off through the doMobSpawning gamerule);
- a client joined as RenderBot on `Xvfb :99 -screen 0 1920x1080x24` with a 1920x1080 window (portablemc --resolution 1920x1080), GUI hidden (F1),
  options maxFps:260 and enableVsync:false, Oculus with the Potato Lite shader, drawn by software GL (LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe MESA_GL_VERSION_OVERRIDE=4.6);
- server AND client started under libfaketime at the same --speed: LD_PRELOAD=/usr/lib/x86_64-linux-gnu/faketime/libfaketimeMT.so.1 FAKETIME='+0 x0.25'.
  The whole game then runs at a quarter speed (ticks, cast times, particles, animations, the shader's clock), so the CPU has four times as long to draw
  each frame; the screen is grabbed in real time at 60 x speed frames a second and re-timed to game time: a 60 fps clip where (almost) every frame is new.
  Checked on 2026-11-14: Fireball leaves the staff at 2.75 s both at normal speed and at x0.25; the 1080p window draws 12-14 frames a real second.
For each spell, on a fresh stage 100 blocks along z (forceloaded): a polished deepslate floor, time 12300, no mob spawning; the caster at x-3.5 and a Target
Dummy at x+3.5 (its damage numbers), an invisible barrier column just behind the dummy (spells cast at the block the caster looks at land on the dummy);
the caster aimed at the dummy's chest, in his school's robes with a staff, every spell power brought back to its base (the robes add spell power even with an
empty AttributeModifiers tag); a camera that is not the player (CMDCam outside mode): side on from 6.5 blocks, field of view 50, a slow dolly;
`/cast RenderBot <spell> <max level>` (every spell learned first; SETUP below changes the stage for spells that need more); the 1080p recording is re-timed and scaled to 1280x720 (lanczos: the downscale also smooths the edges) at 60 fps, H.264 CRF 28, preset slow, tune animation
(2026-11-15, to keep every system's clips under GitHub Pages' 1 GB: 52% of the size of CRF 23 medium, SSIM 0.98 against it on four sample clips).
Poster: poster_frame() (the most spell colour while the caster is still in sight), 960x540 WebP.
QC: OUT_DIR/qc.jsonl, one line per clip (new frames a second by new_frames(), bytes, poster frame, robe); --redo-below N records again the clips under N fps; the run stops if the client is gone.
Length in game time: instant 6 s; long and continuous = cast time + 6 s, at most 11 s.
--system goety (patches/spells_goety.json): Goety has no cast command, so the caster casts as a player does, in creative mode (DarkWand.use skips the soul
energy check when Abilities.instabuild): a Dark Wand holding the focus (the focus lives in the wand's item capability, ForgeCaps.Parent, which an item
argument cannot set but a container's item NBT can: the wand is put in a barrel under the floor and copied into the hand with `item replace ... from block`), no armour,
then the right button clicked (instant spells), held for the cast time plus half a second (charged), or held 5 s (continuous, cast 72000).
--system ars (patches/spells_ars.json): Ars has no cast command either: a Creative Spell Book whose one spell is set by NBT ("ars_nouveau:caster",
the layout of SpellCaster.writeTag and Spell.serialize in the 1.20 source), the caster in creative mode (SpellResolver.enoughMana passes a creative
player), the right button clicked. A glyph is shown inside a small spell (ars_stage): a form with Harm, an effect after Projectile (Self for the
caster's own buffs, aimed at the floor for block effects, followed by Harm when it only passes the spell on), an augment cast twice in one clip,
without and then with it, on a base spell its effect shows on.
--system brutality (patches/spells_brutality.json): the school's tome holding the spell by NBT (SpellStorage: Spells[{SpellId, SpellLevel}],
SelectedSpellIndex), mana filled through the brutality:max_mana and brutality:mana_regen attributes (Brutality's mana check has no creative pass),
the right button clicked (instant), held for the cast time plus half a second (channelling) or 5 s (continuous)."""
import os, re, json, math, time, subprocess, argparse
H = os.path.dirname(os.path.abspath(__file__))
SPELLS = os.path.join(H, '..', 'patches', 'spells.json')
SYSTEMS = {'irons': SPELLS, 'goety': os.path.join(H, '..', 'patches', 'spells_goety.json'), 'ars': os.path.join(H, '..', 'patches', 'spells_ars.json'),
           'brutality': os.path.join(H, '..', 'patches', 'spells_brutality.json')}
BTOME = {'cosmic': 'cosmic_tome', 'brimwielder': 'brimwielder_tome', 'umbrancy': 'umbral_tome', 'voidwalker': 'void_tome', 'celestia': 'celestia_tome',
         'daemonic': 'daemonic_tome', 'darkist': 'darkist_tome', 'evergreen': 'evergreen_tome', 'exodic': 'exodic_tome'}
WAND = ['setblock %(X)d -62 %(Z)d minecraft:barrel{Items:[{Slot:0b,id:"%(wand)s",Count:1b,ForgeCaps:{Parent:{Items:[{Slot:0,id:"%(focus)s",Count:1b}],Size:1}}}]}',
        'item replace entity RenderBot weapon.mainhand from block %(X)d -62 %(Z)d container.0', 'setblock %(X)d -62 %(Z)d minecraft:dirt']   # Goety: a wand with its focus, by a barrel under the floor (1.20.1 has no item-entity slot)
# Goety stage by the spell's class (the export's `kind`); SETUP entries win: summons need a hostile mob for their minions to fight, block spells act on the
# block the eye meets (35 degrees down meets the floor 2.3 blocks ahead), touch spells on a creature within reach
GOETY_KIND = {'SummonSpell': {'target': 'husk'}, 'BlockSpell': {'pitch': 35}, 'TouchSpell': {'gap': 1.5}}
AN = 'ars_nouveau:glyph_'


def ars_book(parts, rgb=(255, 60, 200)):
    """a Creative Spell Book holding one spell of these glyph ids"""
    recipe = ','.join('part%d:"%s"' % (k, x) for k, x in enumerate(parts)) + ',size:%d' % len(parts)
    return ('ars_nouveau:creative_spell_book{"ars_nouveau:caster":{current_slot:0,flavor:"",is_hidden:0b,hidden_recipe:"",spell_count:1,spells:{spell0:{name:"lgw",'
            'spellColor:{r:%d,g:%d,b:%d,type:"ars_nouveau:constant"},recipe:{%s}}}}}' % (rgb + (recipe,)))


# glyphs by the name after the namespace (the same name never appears in two add-ons here)
ARS_SELF = {'glyph_glide', 'glyph_leap', 'glyph_slowfall', 'glyph_invisibility', 'glyph_bounce', 'glyph_bubble_shield', 'glyph_summon_steed', 'glyph_sense_magic',
            'glyph_summon_decoy', 'glyph_effectconjureblade', 'glyph_effectconjurearrow', 'glyph_ender_inventory', 'glyph_craft'}
ARS_FLOOR = {'glyph_break', 'glyph_place_block', 'glyph_conjure_terrain', 'glyph_conjure_water', 'glyph_crush', 'glyph_cut', 'glyph_fell', 'glyph_grow', 'glyph_harvest',
             'glyph_interact', 'glyph_phantom_block', 'glyph_redstone_signal', 'glyph_rotate', 'glyph_smelt', 'glyph_light', 'glyph_evaporate', 'glyph_exchange',
             'glyph_animate_block', 'glyph_rune', 'glyph_intangible', 'glyph_plow', 'glyph_flatten', 'glyph_effectraiseearth', 'glyph_effectdismantle', 'glyph_effecteruption'}
ARS_WRAP = {'burst', 'glyph_delay', 'glyph_linger', 'glyph_wall', 'glyph_propagator_arc', 'glyph_propagator_homing', 'reset', 'rewind',
            'glyph_propagate_projectile', 'glyph_propagate_self', 'glyph_propagate_underfoot', 'glyph_propagate_plane', 'glyph_chaining', 'glyph_reverse_direction',
            'glyph_propdetonate', 'glyph_filternotself', 'glyph_spellefficiency'}
# an augment's base spell: what it changes must show (damage numbers, speed, area, burning time, the dropped block)
ARS_AUG_BASE = {'aoe': ([AN + 'projectile', AN + 'conjure_terrain'], {'pitch': 30}), 'extend': ([AN + 'projectile', AN + 'ignite'], {'secs': 14, 'again': 90}),
                'duration': ([AN + 'projectile', AN + 'ignite'], {'secs': 14, 'again': 90}), 'extract': ([AN + 'projectile', AN + 'break'], {'pitch': 30}),
                'fortune': ([AN + 'projectile', AN + 'break'], {'pitch': 30})}


def ars_stage(s):
    """the spell that shows one glyph, and the stage it needs (merged under SETUP)"""
    g, k, n = s['id'], s.get('kind'), s['id'].split(':', 1)[1]
    if k == 'form': return {'hold': ars_book([g, AN + ('leap' if n == 'glyph_self' else 'break' if n == 'glyph_underfoot' else 'harm')]), 'gap': 1.5 if n == 'glyph_touch' else 3.5}
    if k == 'filter': return {'hold': ars_book([AN + 'projectile', g, AN + 'harm'])}
    if k == 'augment':
        fam = next((f for f in ARS_AUG_BASE if f in n.replace('extendtime', 'extend').replace('durationdown', 'duration').replace('duration_down', 'duration')), None)
        base, st = ARS_AUG_BASE.get(fam, ([AN + 'projectile', AN + 'harm'], {}))
        again = st.get('again', 50)   # ticks between the cast without the augment and the cast with it
        return dict({k2: v for k2, v in st.items() if k2 != 'again'}, hold=ars_book(base), secs=st.get('secs', 10),
                    after=[[again - 4, 'item replace entity RenderBot weapon.mainhand with ' + ars_book(base + [g], (60, 200, 255))], [again, 'click:3']])
    if n == 'wololo': return {'hold': ars_book([AN + 'projectile', g]), 'target': 'sheep'}   # turns a sheep's colour
    if n in ARS_SELF: return {'hold': ars_book([AN + 'self', g])}
    if n in ARS_FLOOR: return {'hold': ars_book([AN + 'projectile', g]), 'pitch': 30}
    if n in ARS_WRAP: return {'hold': ars_book([AN + 'projectile', g, AN + 'harm'])}
    return {'hold': ars_book([AN + 'projectile', g])}
ROBE = {'fire': 'pyromancer', 'ice': 'cryomancer', 'lightning': 'electromancer', 'holy': 'priest', 'blood': 'cultist', 'ender': 'shadowwalker', 'evocation': 'archevoker', 'nature': 'plagued'}
# what the spells are cast at: the Target Dummy (shows damage numbers), or a mob that stands still and does not burn, for spells that need a living target;
# the difficulty the stage needs (peaceful removes a hostile mob the tick it is summoned, so the husk needs easy; NoAI keeps it from attacking)
TARGETS = {'dummy': ('dummmmmmy:target_dummy', '', 'peaceful'),
           'husk': ('minecraft:husk', '{NoAI:1b,Silent:1b,PersistenceRequired:1b,Rotation:[90f,0f],Attributes:[{Name:"minecraft:generic.max_health",Base:1000d}],Health:1000f}', 'easy'),
           'sheep': ('minecraft:sheep', '{NoAI:1b,Silent:1b,PersistenceRequired:1b,Rotation:[90f,0f],Color:11b}', 'easy'),   # blue: Wololo turns it red
           'pig': ('minecraft:pig', '{Silent:1b,PersistenceRequired:1b,Rotation:[90f,0f]}', 'easy'),   # with AI, so a pull can move it
           'pyromancer': ('irons_spellbooks:pyromancer', '{PersistenceRequired:1b,Rotation:[90f,0f]}', 'easy'),   # casts at the caster: something to counter
           'husk_frozen': ('minecraft:husk', '{NoAI:1b,Silent:1b,PersistenceRequired:1b,Rotation:[90f,0f],TicksFrozen:1000}', 'easy'),   # fully frozen (140+ ticks): Frostbite
           'none': (None, '', 'peaceful'),
           'husk_ai': ('minecraft:husk', '{Silent:1b,PersistenceRequired:1b,Rotation:[90f,0f],Attributes:[{Name:"minecraft:generic.max_health",Base:1000d}],Health:1000f}', 'easy')}   # with AI (fear, madness); a husk, as a zombie burns in the evening sun
# camera keyframes (x, y, z offsets from the stage centre X, Z; yaw; pitch), a slow dolly from the first to the second; field of view 50
CAMS = {'side': ((0.1, -58.6, 7.0, 180, 5), (0.9, -58.65, 6.5, 180, 5)),          # the default: side on from 6.5 blocks
        'mid': ((0.1, -57.9, 10.0, 180, 7), (0.9, -57.95, 9.5, 180, 7)),           # a summon or two beside the caster
        'wide': ((0.1, -57.2, 13.0, 180, 8), (0.9, -57.25, 12.4, 180, 8)),         # summons and big areas that the side camera cuts or that walk into it
        'far': ((0.1, -55.0, 24.0, 180, 6), (0.9, -55.05, 23.2, 180, 6)),          # very big spells
        'farup': ((0.1, -58.0, 26.0, 180, -10), (0.9, -58.0, 25.2, 180, -10)),     # very big and high: floor to 18 blocks up (Black Hole)
        'close': ((-0.9, -58.9, 2.6, 135, 6), (-1.1, -58.92, 2.35, 135, 6)),       # three quarters in front of the caster, 3 blocks: buffs on the caster
        'tclose': ((1.4, -58.9, 2.6, -135, 6), (1.6, -58.92, 2.35, -135, 6)),      # the same in front of the target: a glow or a mark on it
        'sky': ((0.1, -59.2, 10.0, 180, -14), (0.9, -59.2, 9.6, 180, -14)),        # looking up: spells that change the sky
        'behind': ((-11.0, -57.4, 1.6, -95, 8), (-10.4, -57.42, 1.2, -95, 8)),     # behind the caster, looking at the target: a wall built across the line
        'vfar': ((0.1, -52.0, 45.0, 180, 4), (0.9, -52.0, 44.0, 180, 4)),         # 45 blocks out: Supernova's black hole is 30 blocks across
        'top': ((0.1, -49.0, 9.0, 180, 50), (0.6, -49.0, 8.6, 180, 50)),           # high, looking down: marks on the floor (Bloodmark)
        'jet': ((10.0, -38.0, 34.0, 180, -2), (11.0, -38.0, 33.0, 180, -2)),       # high and far: a flight above the stage
        'jetc': ((2.0, -37.5, 17.0, 180, 0), (7.0, -37.5, 16.0, 180, 0)),        # beside the flight path, panning with it
        'eyes': (None, None)}                                                      # the player's own view (spells that change what the player sees)
# what a spell needs that the plain stage lacks (2026-11-15: the 122 spells recipe 4 showed nothing for, sorted by cause; each was read from the spell's
# checkPreCastConditions or found by trying). Keys: hold (main hand item instead of the staff), target, difficulty, pitch, cam, gap (caster to target, default
# 3.5 each side of the centre), secs (clip length in game seconds), pre (commands after the stage is built), after ([ticks after the cast, command or 'cast' to
# (gear: commands after the robes and the held item; crop: an ffmpeg crop before the scale, a zoom on a small effect) cast again, or 'key:<keysym>:down|up|tap' / 'click:<button>' for real input], in order), lead ([ticks before the cast, command]), before (commands in
# the same tick as the cast); these commands may use %(X)d, %(Z)d (stage centre), %(Xt)s (the target's x),
# %(Zb)d (3 blocks behind the line, away from the camera), %(Xa)d..%(Xb)d and %(Za)d..%(Zc)d (a patch of floor around the target)
DAMAGE_ME = 'execute at RenderBot run damage RenderBot 2 minecraft:mob_attack by @e[type=minecraft:husk,limit=1,sort=nearest]'   # an attack, to set off a buff that reacts to one
HIT_TARGET = 'execute at RenderBot run damage @e[type=dummmmmmy:target_dummy,limit=1,sort=nearest] 2 minecraft:player_attack by RenderBot'   # the caster's attack
SECOND = 'summon minecraft:husk %(Xt)s -60 %(Zb)d.5 {NoAI:1b,Silent:1b,PersistenceRequired:1b,Rotation:[90f,0f],Tags:["t2"]}'   # a second creature for spells that link two
EXTINGUISH = 'execute at RenderBot run data merge entity @e[type=dummmmmmy:target_dummy,limit=1,sort=nearest] {Fire:0s}'   # a burning target takes less from the next hit
# with a weapon just put in hand, the first /cast of its spell does nothing and the second works (2026-11-15 console probe, twice): 'prime' casts once and
# waits that many ticks, more than the cast time, so the throwaway cast is over (a /cast during a cast cancels it) before the clip is recorded
SECOND_SIDE = 'summon minecraft:husk %(X)d.5 -60 %(Zm2)d.5 {NoAI:1b,Silent:1b,PersistenceRequired:1b,Rotation:[90f,0f],Tags:["t2"]}'   # beside the line, so a link between the two runs across the side camera's view (behind the target it ran away from the lens, end on)
FACE_SECOND = 'execute as RenderBot at @s anchored eyes run tp @s ~ ~ ~ facing entity @e[tag=t2,limit=1] eyes'
SETUP = {
    # Traveloptics weapon spells: checkPreCastConditions wants the weapon (any level) in the main hand
    'traveloptics:shear_of_the_stars': {'hold': 'traveloptics:stellothorn_level_three', 'cam': 'wide'},
    'traveloptics:skypiercer': {'hold': 'traveloptics:trident_of_the_eternal_maelstrom_level_three', 'cam': 'wide'},
    # summons of hostile mobs: peaceful removes them the tick they appear (summons of animals needed spawn-animals=true in server.properties: false
    # makes ServerLevel discard every Animal each tick, summoned or not)
    'darkermagic:summoned_warden': {'difficulty': 'easy', 'cam': 'wide'},
    'darkermagic:summoned_sculk_snapper': {'difficulty': 'easy', 'cam': 'mid'},
    'irons_spellbooks:summon_polar_bear': {'difficulty': 'easy', 'cam': 'wide'},
    'irons_spellbooks:summon_horse': {'cam': 'mid'},
    'refined_mod:summon_wolves': {'difficulty': 'easy', 'cam': 'mid'},
    'traveloptics:herald_of_acropolis': {'difficulty': 'easy', 'cam': 'wide'},
    'traveloptics:primal_pack': {'difficulty': 'easy', 'cam': 'mid'},
    'traveloptics:primordial_steed': {'difficulty': 'easy', 'cam': 'far'},
    'traveloptics:conjure_void_tomes': {'difficulty': 'easy', 'cam': 'wide'},
    # spells that change a living creature
    'irons_spellbooks:wololo': {'target': 'sheep'},
    'peyroscythe:young_for_you': {'target': 'sheep'},
    'irons_spellbooks:telekinesis': {'target': 'husk'},
    # spells that only touch hostile creatures (the dummy is not one)
    'traveloptics:nullflare': {'target': 'husk'}, 'traveloptics:shadowed_miasma': {'target': 'husk'},
    # melee spells: the target within reach
    'irons_spellbooks:flaming_strike': {'gap': 1.8},
    # spells that link two creatures: cast at the target, turn to a second one, cast again
    # Eldritch spells need learning (AbstractSpell.canBeCastedBy: requiresLearning and not isLearned): main() teaches every spell first
    'irons_spellbooks:eldritch_blast': {}, 'irons_spellbooks:sculk_tentacles': {'pitch': 14, 'cam': 'far'},
    # a buff on the caster: only the caster to look at
    # buffs that only raise numbers: a bolt of the same school before and after the buff, so the damage number grows on screen
    'somakespells:combustion': {'lead': [[45, 'cast RenderBot irons_spellbooks:firebolt 1']], 'after': [[38, EXTINGUISH], [50, 'cast RenderBot irons_spellbooks:firebolt 1']], 'secs': 7},
    # a buff that answers an attack
    'peyroscythe:sinfire_embrace': {'gap': 1.8, 'target': 'husk', 'after': [[20, 'click:1'], [45, 'click:1'], [70, 'click:1']]},   # real attacks (left click)
    # the sky
    'peyroscythe:made_in_heaven': {'cam': 'sky', 'pre': ['gamerule doDaylightCycle true', 'time set 11000'], 'secs': 11},   # the sun sets, then night
    'peyroscythe:crimson_moon': {'cam': 'sky', 'pre': ['time set 18000']},
    # cast at the floor near the dummy, not the barrier behind it
    'irons_spellbooks:black_hole': {'pitch': 14, 'cam': 'farup'},
    # --- 2026-11-15, third round: the rest of the 122 ---
    'traveloptics:apex_harvest': {'hold': 'traveloptics:cursed_wraithblade_level_three', 'gap': 1.8},
    'traveloptics:galena_shatter': {'hold': 'traveloptics:galenic_polarizer_level_three', 'target': 'husk'},
    # summons that the side camera cuts or that stand in front of it
    'traveloptics:axe_of_the_doomed': {'difficulty': 'easy', 'cam': 'wide'}, 'traveloptics:eternal_sentinel': {'difficulty': 'easy', 'cam': 'wide'},
    'traveloptics:sword_of_the_ancients': {'difficulty': 'easy', 'cam': 'wide'}, 'traveloptics:magnetron_deployment': {'difficulty': 'easy', 'cam': 'wide'},
    'traveloptics:sticky_steed_summon': {'difficulty': 'easy', 'cam': 'wide'}, 'gtbcs_geomancy_plus:solar_chorus': {'difficulty': 'easy', 'cam': 'wide'},
    # big things the side camera cuts
    'peyroscythe:glacier': {'cam': 'wide'}, 'gtbcs_geomancy_plus:weeping_wall': {'cam': 'behind'}, 'traveloptics:stele_cascade': {'cam': 'wide'},
    'somakespells:lightning_dance': {'target': 'husk', 'cam': 'mid'},
    # cast at the floor
    'irons_spellbooks:spectral_hammer': {'pitch': 14, 'pre': ['fill %(Xa)d -63 %(Za)d %(Xb)d -61 %(Zc)d minecraft:stone']},   # stone: ModTags.SPECTRAL_HAMMER_MINEABLE
    # several casts: Wall of Fire places an anchor per cast; Bloodmark marks four points, the fifth cast links them; Psychic Bolt picks targets, then fires
    'irons_spellbooks:wall_of_fire': {'pitch': 14, 'after': [[15, 'execute as RenderBot at @s run tp @s ~ ~ ~ -60 14'], [16, 'cast'], [31, 'execute as RenderBot at @s run tp @s ~ ~ ~ -120 14'], [32, 'cast']]},
    'traveloptics:psychic_bolt': {'target': 'husk', 'pre': [SECOND], 'after': [[20, FACE_SECOND], [22, 'cast']], 'secs': 11},
    # spells that need one of the caster's summons: a Vex first
    'traveloptics:vigor_siphon': {'pre': ['cast RenderBot irons_spellbooks:summon_vex 1'], 'cam': 'mid'},
    # fear and madness: a husk that moves (and a second creature for it to fight)
    # hostile targets
    'somakespells:lightning_strike': {'target': 'husk'}, 
    'traveloptics:flood_slash': {'target': 'husk'}, 'traveloptics:aqua_missiles': {'target': 'husk', 'cam': 'mid'}, 'peyroscythe:black_fireball': {'target': 'husk'},
    # a glow or a mark on the target
    'irons_spellbooks:blessing_of_life': {'cam': 'tclose'}, 'irons_spellbooks:blight': {'cam': 'tclose'},
    # buffs that answer an attack
    'peyroscythe:made_in_heaven_real': {'cam': 'sky', 'pre': ['gamerule doDaylightCycle true', 'time set 11000'], 'secs': 11},
    # spells about the player's own view or that take the player away: the player's eyes, or a spawn point beside the stage
    'irons_spellbooks:planar_sight': {'cam': 'eyes', 'target': 'husk', 'pre': ['fill %(X)d -60 %(Za)d %(X)d -57 %(Zc)d minecraft:stone'], 'secs': 6},
    'irons_spellbooks:pocket_dimension': {'cam': 'eyes', 'secs': 8},
    'irons_spellbooks:recall': {'pre': ['spawnpoint RenderBot %(X)d -60 %(Zb)d'], 'cam': 'eyes', 'secs': 9},   # CMDCam loses the stage when Recall moves the player
    # spells that need the player to move: real key input
    'gtbcs_geomancy_plus:tremor_step': {'target': 'husk', 'after': [[5, 'key:w:down'], [7, 'key:Control_L:down'], [40, 'key:w:up'], [41, 'key:Control_L:up']], 'secs': 6},
    'irons_spellbooks:frost_step': {'after': [[2, 'data merge entity @e[type=irons_spellbooks:frozen_humanoid,limit=1,sort=nearest] {CustomNameVisible:0b}'],
                                              [3, 'team join lgw_hide @e[type=irons_spellbooks:frozen_humanoid]']]},   # the ice copy shows the caster's name
    # --- 2026-11-15, fourth round, after reading each remaining spell's code (and the HUD's cast messages) ---
    'irons_spellbooks:abyssal_shroud': {'target': 'husk_ai', 'gap': 1.6, 'cam': 'mid', 'secs': 9, 'pre': ['effect give @e[type=minecraft:husk] minecraft:strength 60 5 true']},   # a real attacker: a husk with AI and Strength VI beside the caster (a /damage hit did not set the buff off visibly)
    'irons_spellbooks:evasion': {'target': 'husk', 'cam': 'wide', 'after': [[30, DAMAGE_ME], [70, DAMAGE_ME], [110, DAMAGE_ME]], 'secs': 8},   # each hit: a jump of up to 12 blocks
    'irons_spellbooks:sacrifice': {'pre': ['cast RenderBot irons_spellbooks:summon_vex 1'], 'cam': 'tclose',   # the Vex held still beside the target, then aimed at
                                   'lead': [[30, 'data merge entity @e[type=irons_spellbooks:summoned_vex,limit=1] {NoAI:1b}'], [28, 'tp @e[type=irons_spellbooks:summoned_vex,limit=1] %(Xn)s -59 %(Z)d.5']],
                                   'before': ['execute as RenderBot at @s anchored eyes run tp @s ~ ~ ~ facing entity @e[type=irons_spellbooks:summoned_vex,limit=1,sort=nearest] eyes']},
    'irons_spellbooks:sonic_boom': {'target': 'husk', 'cam': 'behind'},
    'irons_spellbooks:throw': {'hold': 'minecraft:trident', 'cam': 'mid'},
    'irons_spellbooks:thunderstorm': {'target': 'husk', 'cam': 'farup', 'secs': 9},   # a strike every 40 ticks on each living non-ally in sight
    'irons_spellbooks:touch_dig': {'target': 'none', 'pitch': 14, 'cam': 'tclose', 'pre': ['fill %(X4)d -61 %(Za)d %(X4)d -61 %(Zc)d minecraft:diamond_ore']},
    'irons_spellbooks:frostbite': {'target': 'husk_frozen', 'cam': 'mid', 'secs': 8,   # a fully frozen creature killed by the caster turns into an Ice Shadow
                                   'after': [[20, 'execute at RenderBot run damage @e[type=minecraft:husk,limit=1,sort=nearest] 5000 minecraft:player_attack by RenderBot']]},
    'irons_spellbooks:charge': {'lead': [[45, 'cast RenderBot irons_spellbooks:magic_missile 10']], 'after': [[45, 'cast RenderBot irons_spellbooks:magic_missile 10']], 'secs': 7},   # +15% spell power at level 3
    
    # only from a spellbook (canBeCastedBy refuses any other cast source): the book in the curio slot, the cast key (V) pressed
    'legendary_spellbooks:energy_beam': {'nocast': True, 'target': 'husk', 'cam': 'farup', 'secs': 9, 'after': [[0, 'key:v:tap']],
                                         'pre': ['curios replace spellbook 0 RenderBot with irons_spellbooks:netherite_spell_book{"irons_spellbooks:spell_container":{maxSpells:12,mustEquip:1b,spellWheel:1b,data:[{index:0,id:"legendary_spellbooks:energy_beam",locked:0b,level:1}]}}']},
    'legendary_spellbooks:annihilation_geyser': {'nocast': True, 'target': 'husk', 'cam': 'mid', 'secs': 14, 'after': [[0, 'key:v:tap']],   # and only from the Annihilator's Protocol
                                                 'pre': ['curios replace spellbook 0 RenderBot with legendary_spellbooks:annihilators_protocol{"irons_spellbooks:spell_container":{maxSpells:12,mustEquip:1b,spellWheel:1b,data:[{index:0,id:"legendary_spellbooks:annihilation_geyser",locked:0b,level:1}]}}']},
    
    'peyroscythe:illusion_crazy': {'target': 'husk_ai', 'cam': 'mid', 'secs': 10, 'pre': ['summon minecraft:sheep %(Xt)s -60 %(Zb)d.5 {PersistenceRequired:1b}']},   # the maddened husk turns on a sheep
    'refined_mod:frost_strike': {'gap': 1.8, 'hold': 'minecraft:netherite_sword', 'target': 'husk', 'cam': 'mid', 'after': [[14, 'cast'], [28, 'cast']]},
    'refined_mod:moon_slash': {'hold': 'minecraft:netherite_sword', 'cam': 'mid'},
    'refined_mod:storm_blade': {'hold': 'minecraft:netherite_sword', 'target': 'husk', 'cam': 'tclose', 'after': [[15, 'cast']]},
    'traveloptics:supernova': {'hold': 'traveloptics:wand_of_final_light', 'prime': 160, 'cam': 'vfar', 'secs': 20},   # explosion about 15.7 s after the cast   # explosion about 15.7 s after the cast
    'traveloptics:extinction': {'hold': 'traveloptics:gauntlet_of_extinction_level_three', 'prime': 100, 'cam': 'farup', 'secs': 10},   # the asteroid falls from 120 blocks up   # the asteroid falls from 120 blocks up
    'traveloptics:gyro_slash': {'hold': 'traveloptics:infernal_devastator_level_three', 'gap': 3, 'prime': 80},   # the slash projectile needs room
    'traveloptics:call_forth_the_dead_king': {'nocast': True, 'difficulty': 'easy', 'cam': 'wide', 'secs': 22, 'after': [[0, 'btn:3:down'], [320, 'btn:3:up']],   # scroll only (canBeCastedBy: CastSource.SCROLL); held through the 15 s cast
                                              'hold': 'irons_spellbooks:scroll{"irons_spellbooks:spell_container":{maxSpells:1,mustEquip:0b,spellWheel:0b,data:[{index:0,id:"traveloptics:call_forth_the_dead_king",locked:1b,level:1}]}}'},
    'traveloptics:despair': {'cam': 'behind', 'after': [[12, 'cast'], [24, 'cast']]},
    'traveloptics:echo_of_the_abyss': {'difficulty': 'easy', 'nogui': True, 'cam': 'far', 'secs': 12, 'pre': ['fill %(Xm3)d -61 %(Za)d %(Xa)d -56 %(Zc)d minecraft:water'],   # the caster's head under water
                                       'lead': [[20, 'tp RenderBot %(Xc)s -60 %(Z)d.5 -90 0']]},   # a tp in the cast's own tick: 'You must be underwater'
    'traveloptics:eek': {'target': 'husk', 'cam': 'eyes', 'secs': 6},
    'traveloptics:em_pulse': {'target': 'husk', 'gap': 1.75},
    'traveloptics:hydroshot': {'cam': 'tclose', 'after': [[12, 'cast'], [24, 'cast']]},
    'traveloptics:rainfall': {'target': 'husk', 'cam': 'farup', 'secs': 9},
    'traveloptics:astral_sense': {'target': 'husk_ai', 'cam': 'eyes', 'secs': 9},   # paths show for a mob that is walking
    'traveloptics:floodgate': {'target': 'husk_ai', 'gap': 1.6, 'cam': 'mid', 'secs': 9, 'pre': ['effect give @e[type=minecraft:husk] minecraft:strength 60 5 true']},   # a real attacker: a husk with AI and Strength VI beside the caster (a /damage hit did not set the buff off visibly)
    
    'traveloptics:spectral_blink': {'target': 'husk', 'cam': 'eyes', 'secs': 5, 'after': [[10, 'key:Shift_L:down'], [16, 'key:Shift_L:up']]},   # crouch to blink to what you look at
    
    'somakespells:bloodmark': {'cam': 'top', 'nogui': True, 'secs': 9, 'after': [[12, 'tp RenderBot %(Xm3)d -60 %(Zm3)d'], [13, 'cast'], [26, 'tp RenderBot %(Xp3)d -60 %(Zm3)d'], [27, 'cast'],   # marks the caster's feet
                                                     [40, 'tp RenderBot %(Xp3)d -60 %(Zp3)d'], [41, 'cast'], [54, 'tp RenderBot %(Xm3)d -60 %(Zp3)d'], [55, 'cast'], [68, 'cast']]},
    'somakespells:damned_demomans': {'target': 'husk_ai', 'gap': 1.6, 'cam': 'mid', 'secs': 5, 'pre': ['effect give @e[type=minecraft:husk] minecraft:strength 60 5 true']},   # the attacking husk brings the caster under 30% health: the caster explodes in flames (ends before the husk kills the caster)
    'somakespells:lightning_spear': {'cam': 'tclose', 'after': [[20, 'cast']]},
    'somakespells:resonant_pulse': {'cam': 'tclose', 'after': [[8, 'cast'], [16, 'cast']]},
    # school buffs (+15% at level 3, the config's top level): the school's bolt at level 10 before and after
    'somakespells:permafrost': {'level': 3, 'lead': [[45, 'cast RenderBot irons_spellbooks:icicle 10']], 'after': [[45, 'cast RenderBot irons_spellbooks:icicle 10']], 'secs': 7},
    'somakespells:blessing': {'level': 3, 'lead': [[45, 'cast RenderBot irons_spellbooks:guiding_bolt 10']], 'after': [[45, 'cast RenderBot irons_spellbooks:guiding_bolt 10']], 'secs': 7},
    'somakespells:blood_rush': {'level': 3, 'lead': [[45, 'cast RenderBot irons_spellbooks:blood_needles 10']], 'after': [[45, 'cast RenderBot irons_spellbooks:blood_needles 10']], 'secs': 7},
    'somakespells:earthbound': {'level': 3, 'lead': [[45, 'cast RenderBot gtbcs_geomancy_plus:dripstone_bolt 10']], 'after': [[45, 'cast RenderBot gtbcs_geomancy_plus:dripstone_bolt 10']], 'secs': 7},
    'somakespells:eldritch_gambit': {'level': 3, 'lead': [[45, 'cast RenderBot irons_spellbooks:eldritch_blast 5']], 'after': [[45, 'cast RenderBot irons_spellbooks:eldritch_blast 5']], 'secs': 7},
    'somakespells:ender_corruption': {'level': 10, 'lead': [[45, 'cast RenderBot irons_spellbooks:magic_missile 10']], 'after': [[45, 'cast RenderBot irons_spellbooks:magic_missile 10']], 'secs': 7},
    'somakespells:evocation_fortitude': {'level': 10, 'lead': [[45, 'cast RenderBot irons_spellbooks:firecracker 10']], 'after': [[45, 'cast RenderBot irons_spellbooks:firecracker 10']], 'secs': 7},
    'somakespells:submerge': {'level': 10, 'lead': [[45, 'cast RenderBot traveloptics:hydroshot 10']], 'after': [[45, 'cast RenderBot traveloptics:hydroshot 10']], 'secs': 7},
    # the effect is on the player's own bars: first person with the HUD on
    'irons_spellbooks:greater_heal': {'hud': True, 'cam': 'eyes', 'secs': 10, 'lead': [[20, 'damage RenderBot 16 minecraft:magic']]},   # the hearts refill (the damage after any throwaway cast)
    'irons_spellbooks:gluttony': {'hud': True, 'cam': 'eyes', 'secs': 9, 'hold': 'minecraft:golden_apple 16', 'pre': ['mana set RenderBot 0', 'effect give RenderBot minecraft:hunger 2 255 true', 'attribute RenderBot irons_spellbooks:mana_regen modifier add 0-0-0-78-1 lgw_noregen -1 multiply_base',
                                          'attribute RenderBot irons_spellbooks:max_mana modifier add 0-0-0-78-2 lgw_smallbar -0.92 multiply'], 'level': 10,   # no natural regen and a 48-point bar: the meal's mana (26 at level 10) reads at a glance
                                  'after': [[10, 'btn:3:down'], [60, 'btn:3:up']]},   # eating refills the mana bar
    'traveloptics:reversal': {'hold': 'minecraft:diamond_sword', 'target': 'husk_ai', 'gap': 1.6, 'cam': 'mid', 'secs': 8, 'pre': ['effect give @e[type=minecraft:husk] minecraft:strength 60 2 true'],
                              'after': [x for t in range(8, 140, 8) for x in ([t - 1, 'clearCooldowns player RenderBot'], [t, 'cast'])]},   # an 8-tick window, renewed until the attacking husk lands a blow
    
    'somakespells:blood_cut': {'gap': 1.8, 'hold': 'minecraft:netherite_sword', 'cam': 'tclose', 'after': [[15, 'click:1'], [27, 'click:1'], [39, 'click:1']]},   # real hits
    # --- 2026-11-15, round 8: the last 22 ---
    # spells that link two creatures: Iron's skips the target check on a recast, so the second cast had no target; cooldown and recast cleared in between
    'somakespells:chain_connection': {'target': 'husk', 'cam': 'mid', 'secs': 8, 'pre': [SECOND_SIDE], 'after': [[30, FACE_SECOND], [31, 'clearCooldowns player RenderBot'], [31, 'clearRecasts player RenderBot'], [32, 'cast']]},
    'somakespells:cursed_connection': {'target': 'husk', 'cam': 'mid', 'secs': 9, 'pre': [SECOND_SIDE], 'after': [[30, FACE_SECOND], [31, 'clearCooldowns player RenderBot'], [31, 'clearRecasts player RenderBot'], [32, 'cast'],
        [60, 'execute positioned %(Xt)s -60 %(Z)d.5 run damage @e[type=minecraft:husk,distance=..1,limit=1] 20 minecraft:generic'], [90, 'execute positioned %(Xt)s -60 %(Z)d.5 run damage @e[type=minecraft:husk,distance=..1,limit=1] 20 minecraft:generic']]},
    'somakespells:blessed_connection': {'target': 'husk', 'cam': 'mid', 'secs': 9, 'pre': [SECOND_SIDE], 'after': [[30, FACE_SECOND], [31, 'clearCooldowns player RenderBot'], [31, 'clearRecasts player RenderBot'], [32, 'cast'],
        [55, 'execute positioned %(Xt)s -60 %(Z)d.5 run damage @e[type=minecraft:husk,distance=..1,limit=1] 30'], [70, 'execute positioned %(Xt)s -60 %(Z)d.5 run effect give @e[type=minecraft:husk,distance=..1,limit=1] minecraft:instant_damage 1 2'],
        [85, 'execute positioned %(Xt)s -60 %(Z)d.5 run effect give @e[type=minecraft:husk,distance=..1,limit=1] minecraft:instant_damage 1 2']]},   # instant damage heals undead
    'irons_spellbooks:spider_aspect': {'level': 30, 'pre': ['effect give @e[type=dummmmmmy:target_dummy] minecraft:poison 60 0'],   # +5% a level against a poisoned target; the dummy keeps poison
                                       'lead': [[45, 'cast RenderBot irons_spellbooks:magic_missile 10']], 'after': [[45, 'cast RenderBot irons_spellbooks:magic_missile 10']], 'secs': 7},
    'somakespells:overgrowth': {'level': 10, 'hold': 'minecraft:bow', 'pre': ['give RenderBot minecraft:arrow 4'], 'secs': 12,   # a real bow shot before and after: the buff raises arrow damage
                                'lead': [[95, 'btn:3:down'], [70, 'btn:3:up']], 'after': [[25, 'btn:3:down'], [50, 'btn:3:up']]},
    'traveloptics:jet_steam': {'cam': 'jetc', 'secs': 6, 'gear': ['item replace entity RenderBot armor.chest with minecraft:elytra'],   # gliding (isFallFlying): high up, elytra opened, then the jet
                               'lead': [[34, 'tp RenderBot %(Xc)s -36 %(Z)d.5 -90 0'], [26, 'key:space:tap'], [22, 'key:space:tap']]},
    'irons_spellbooks:counterspell': {'cam': 'tclose', 'secs': 6, 'pre': ['cast @e[type=dummmmmmy:target_dummy,limit=1] irons_spellbooks:summon_vex 1'],   # a magic summon (the dummy's Vex) is dispelled
                                      'lead': [[40, 'data merge entity @e[type=irons_spellbooks:summoned_vex,limit=1] {NoAI:1b}'], [38, 'tp @e[type=irons_spellbooks:summoned_vex,limit=1] %(Xn)s -59.5 %(Z)d.5']],
                                      'before': ['execute as RenderBot at @s anchored eyes run tp @s ~ ~ ~ facing entity @e[type=irons_spellbooks:summoned_vex,limit=1,sort=nearest] eyes']},
    'legendary_spellbooks:fossilized_fury': {'difficulty': 'easy', 'target': 'husk', 'cam': 'close', 'secs': 14,   # once the 80-tick cast is over, the caster strikes the husk and the raptors join in
                                             'after': [[t, 'execute at RenderBot run damage @e[type=minecraft:husk,limit=1,sort=nearest] 1 minecraft:player_attack by RenderBot'] for t in (90, 130, 170)]},
    'legendary_spellbooks:annihilation_resonance': {'hold': 'minecraft:netherite_sword', 'prime': 60, 'gap': 1.8, 'target': 'husk', 'cam': 'mid', 'secs': 9,   # critical hits (a jump, a blow while falling) set off the annihilation blast
                                                    'after': [x for t in (45, 75, 105, 135) for x in ([t, 'key:space:down'], [t + 3, 'key:space:up'], [t + 8, 'click:1'])]},   # the jump key held 3 ticks (a 0.1 s tap is under a tick at quarter speed)
    'legendary_spellbooks:ambush_thorns': {'level': 10, 'secs': 9, 'after': [[t, 'execute at RenderBot run damage RenderBot 6 minecraft:mob_attack by @e[type=dummmmmmy:target_dummy,limit=1,sort=nearest]'] for t in range(40, 160, 15)]},   # after the 30-tick cast: a hit during it interrupts the cast
    'traveloptics:lingering_strain': {'nocast': True, 'secs': 7,   # the same 20 hit before (one number) and after (split in four)
                                      'lead': [[40, 'execute at RenderBot run damage @e[type=dummmmmmy:target_dummy,limit=1,sort=nearest] 20 minecraft:player_attack by RenderBot']],
                                      'before': ['cast @e[type=dummmmmmy:target_dummy,limit=1] traveloptics:lingering_strain 3'],
                                      'after': [[20, 'execute at RenderBot run damage @e[type=dummmmmmy:target_dummy,limit=1,sort=nearest] 20 minecraft:player_attack by RenderBot']]},
    'peyroscythe:illusion_fear': {'target': 'pig', 'cam': 'mid', 'secs': 10, 'level': 3, 'pre': ['attribute RenderBot irons_spellbooks:spell_power modifier add 0-0-0-78-3 lgw_power 9 multiply']},   # a pig (a hostile husk kept attacking); fear lasts 0.8 s per spell power
    'traveloptics:violent_skreech': {'cam': 'tclose', 'secs': 8},   # its particle comes from Alex's Mobs, absent: the damage is what shows
    'somakespells:ram_tchum': {'gap': 1.8, 'cam': 'mid', 'after': [[20, 'cast'], [40, 'cast']]},   # hits only within 3.5 blocks; its ring particle is from a mod the pack lacks
    # small effects that fly from the caster: first person, zoomed on the middle of the frame
    'irons_spellbooks:summon_ender_chest': {'cam': 'eyes', 'secs': 5, 'crop': 'crop=960:540:480:300', 'pre': ['item replace entity RenderBot enderchest.%d with minecraft:%s' % (k, it) for k, it in
                                            enumerate(('diamond 64', 'emerald 64', 'gold_ingot 64', 'ender_pearl 16', 'enchanted_golden_apple 8', 'netherite_ingot 4'))]},
}
for _k, _extra in (('irons_spellbooks:throw', {'hold': 'minecraft:trident'}), ('irons_spellbooks:sonic_boom', {'target': 'husk'}), ('somakespells:resonant_pulse', {'after': [[10, 'cast'], [20, 'cast']]}),
                   ('refined_mod:storm_blade', {'hold': 'minecraft:netherite_sword', 'target': 'husk'}), ('refined_mod:moon_slash', {'hold': 'minecraft:netherite_sword'}),
                   ('refined_mod:frost_strike', {'hold': 'minecraft:netherite_sword', 'target': 'husk', 'gap': 1.8, 'after': [[14, 'cast'], [28, 'cast']]}),
                   ('somakespells:blood_cut', {'hold': 'minecraft:netherite_sword', 'gap': 1.8, 'after': [[15, 'click:1'], [27, 'click:1'], [39, 'click:1']]})):
    SETUP[_k] = dict(_extra, cam='eyes', crop='crop=960:540:480:300')
# projectiles that fly from the caster's eyes: first person keeps them in view the whole way
for _k in ('traveloptics:despair', 'somakespells:lightning_spear', 'somakespells:resonant_pulse', 'irons_spellbooks:throw', 'irons_spellbooks:sonic_boom', 'refined_mod:storm_blade', 'refined_mod:moon_slash'):
    SETUP[_k] = dict(SETUP.get(_k, {}), cam='eyes')
# the eight Ars cross slots run an Ars Nouveau spell carried in an item's NBT (ArsCrossProxySpell.onCast looks in the spellbook curio slot, then the hands, for
# arsnspells:cross_spells with proxy_pool_id N); empty, they cast nothing. Each slot gets one example Ars spell on the staff; Ars mana is skipped in creative
ARS_EXAMPLES = {1: ('Fire Bolt', (255, 90, 0), ['projectile', 'ignite', 'explosion']), 2: ('Storm Bolt', (90, 160, 255), ['projectile', 'lightning']),
                3: ('Frost Bolt', (150, 230, 255), ['projectile', 'freeze', 'cold_snap']), 4: ('Wolf Pack', (230, 230, 230), ['projectile', 'summon_wolves']),
                5: ('Fang Line', (120, 120, 140), ['projectile', 'fangs']), 6: ('Grave Call', (120, 200, 120), ['projectile', 'summon_undead']),
                7: ('Fang Ring', (140, 140, 160), ['underfoot', 'fangs', 'aoe', 'aoe']), 8: ('Firestorm', (255, 140, 40), ['projectile', 'ignite', 'aoe', 'aoe'])}
def ars_staff(n):
    name, (r, g, b), parts = ARS_EXAMPLES[n]
    recipe = ','.join('part%d:"ars_nouveau:glyph_%s"' % (k, x) for k, x in enumerate(parts)) + ',size:%d' % len(parts)
    return ('irons_spellbooks:graybeard_staff{"arsnspells:schema_version":1,"arsnspells:cross_spell_index":0,"arsnspells:cross_spells":[{spell_id:"ars_nouveau:spell",'
            'spell_level:1,spell_type:"ARS_NOUVEAU",proxy_pool_id:%d,custom_name:"%s",ars_spell:{name:"%s",spellColor:{r:%d,g:%d,b:%d,type:"ars_nouveau:constant"},recipe:{%s}}}]}'
            % (n, name, name, r, g, b, recipe))
for _n in ARS_EXAMPLES:
    SETUP['ars_n_spells:ars_cross_%d' % _n] = {'hold': ars_staff(_n), 'pre': ['gamemode creative RenderBot'], 'cam': 'mid' if _n in (6, 7) else 'side', 'difficulty': 'easy'}
# Goety focuses that need more than the class default (review of 2026-11-15): touch spells on a mob (the dummy takes the click itself), a teleport
# and a ring of walls that leave the side camera's frame
SETUP.update({'goety:banish_focus': {'target': 'husk', 'gap': 1.5, 'cam': 'eyes'}, 'goety:charge_focus': {'target': 'husk', 'gap': 1.5, 'cam': 'eyes'},   # a right click ON a mob: the client picks it from the camera, so the player's own view (from the CMDCam camera the click met nothing, twice)
              'goety:blink_focus': {'cam': 'far'}, 'goety:barricade_focus': {'cam': 'wide'}, 'goety:ghastly_focus': {'cam': 'wide'}, 'goety:guardian_focus': {'cam': 'wide'},   # minions out of the side frame
              'goety:glow_light_focus': {'pitch': 30}, 'goety:soul_light_focus': {'pitch': 30},   # the light ball forms where the shot meets a block
              'goety:overgrowth_focus': {'cam': 'wide'}, 'goety:phantasm_focus': {'cam': 'wide', 'pre': ['time set 13800']},   # phantoms burn in the evening sun
              'goety:pulverize_focus': {'pre': ['fill %(Xm3)d -61 %(Zm2)d %(X)d -61 %(Zc)d minecraft:cobblestone']},   # cobblestone turns to gravel
              'goety:rotation_focus': {'pre': ['execute positioned %(X)d -60 %(Z)d run setblock ~-1 ~ ~ minecraft:oak_stairs[facing=east]']},   # a block that turns, where the 35-degree eye ray meets it
              'goety:shockwave_focus': {'target': 'husk', 'gap': 1.5}, 'goety:temblor_clap_focus': {'target': 'husk', 'gap': 1.5}, 'goety:trembling_focus': {'target': 'husk', 'gap': 1.5},
              'goety:sword_focus': {'gear': ['item replace entity RenderBot weapon.offhand with minecraft:diamond_sword']},   # throws a copy of the sword in the off hand
              'goety:telekinesis_focus': {'target': 'pig'}, 'goety:wind_blast_focus': {'target': 'pig'},   # moves a creature (the dummy stays put)
              'goety:water_whip_focus': {'gap': 1.5},   # a short tentacle
              'goety_cataclysm:sandstorm_focus': {'cam': 'wide'}, 'goety_revelation:heretic_focus': {'cam': 'wide'},   # big summons and storms through the side camera
              'goetyawaken:blood_rain_focus': {'cam': 'wide'},   # the hell cloud forms above the side frame
              'goetyawaken:chip_focus': {'target': 'husk'}, 'goetyawaken:chip_rain_focus': {'target': 'husk'},   # fire at a hostile target only
              'goetyawaken:ghost_havoc_focus': {'target': 'husk'}, 'goetyawaken:ghost_missile_focus': {'target': 'husk'},
              'goetyawaken:marble_focus': {'pitch': 30},   # places its block where the eye meets the floor
              'goetyawaken:swamp_mine_focus': {'target': 'husk'}, 'goetyawaken:wololo_focus': {'target': 'sheep'},
              'goetydelight:love_and_fertility_focus': {'target': 'pig'},
              # Goety Delight's farming focuses need the plants they act on, in front of the caster where the eye meets the floor
              'goetydelight:crop_growth_focus': {'pitch': 30, 'pre': ['fill %(Xm3)d -61 %(Zm2)d %(X)d -61 %(Za)d minecraft:farmland', 'fill %(Xm3)d -60 %(Zm2)d %(X)d -60 %(Za)d minecraft:wheat[age=0]']},
              'goetydelight:hoe_focus': {'pitch': 30, 'pre': ['fill %(Xm3)d -61 %(Zm2)d %(X)d -61 %(Za)d minecraft:farmland', 'fill %(Xm3)d -60 %(Zm2)d %(X)d -60 %(Za)d minecraft:wheat[age=7]']},
              'goetydelight:grass_cutting_focus': {'pre': ['fill %(Xm3)d -60 %(Zm2)d %(X)d -60 %(Za)d minecraft:grass']},
              'goetydelight:rich_soil_focus': {'pitch': 30, 'pre': ['fill %(Xm3)d -61 %(Zm2)d %(X)d -61 %(Za)d minecraft:dirt']},
              'goetydelight:tree_growth_focus': {'pre': ['execute positioned %(X)d -61 %(Z)d run setblock ~-1 ~ ~ minecraft:dirt', 'execute positioned %(X)d -60 %(Z)d run setblock ~-1 ~ ~ minecraft:oak_sapling']},
              'goetyawaken:desert_plagues_focus': {'secs': 16}, 'goetyawaken:great_meteor_focus': {'cam': 'far'},   # a 10 s cast; a blast whose smoke filled the side camera
              # only a lich casts it: lichdom from Goety's own command for this clip, taken back before the next (a lasting state, as Bulwark's shields were)
              'goetyawaken:champion_focus': {'pre': ['lichdom grant RenderBot'], 'after': [[310, 'lichdom revoke RenderBot']]},
              # the caster's own bars: survival (creative hides armour and hearts) with soul energy from the console, the player's view with the HUD
              'goety:iron_hide_focus': {'survival': 1, 'cam': 'eyes', 'hud': 1, 'pitch': 60},
              'goety:soul_heal_focus': {'survival': 1, 'cam': 'eyes', 'hud': 1, 'pitch': 60, 'pre': ['damage RenderBot 12 minecraft:generic']},
              'goety:fire_blast_focus': {'target': 'husk', 'gap': 1.5}, 'goety:frost_nova_focus': {'target': 'husk', 'gap': 1.5},   # a blast on the caster: a mob beside him
              # menus: the screen, enlarged (the menu is small at 1080p); the Ender Chest with something in it
              'goety:crafting_focus': {'cam': 'eyes', 'secs': 5, 'crop': 'crop=960:540:480:270'},
              'goety:ender_chest_focus': {'cam': 'eyes', 'secs': 5, 'crop': 'crop=960:540:480:270', 'pre': ['item replace entity RenderBot enderchest.%d with minecraft:%s' % (k, it) for k, it in
                                          enumerate(('diamond 12', 'emerald 30', 'golden_apple 4', 'ender_pearl 16', 'iron_ingot 64', 'book 8'))]}})
ATTR = ['spell_power', 'cast_time_reduction', 'cooldown_reduction'] + [k + '_spell_power' for k in ('fire', 'ice', 'lightning', 'holy', 'ender', 'blood', 'evocation', 'nature', 'eldritch')]


def gui_open(display):
    """a screen is open (Pocket Dimension and Summon Ender Chest open an Ender Chest and it stays; Escape on no screen opens the pause menu): every screen
    dims the world behind it, so the sky band at 30-40% of the height, pink at time 12300 (luminance 135 or more in every clip of 2026-11-14), falls to about 55"""
    import io
    from PIL import Image
    im = Image.open(io.BytesIO(subprocess.run(['import', '-window', 'root', 'png:-'], env=dict(os.environ, DISPLAY=display), capture_output=True).stdout)).convert('L')
    w, h = im.size; band = im.crop((0, int(h * .3), w, int(h * .4))).resize((64, 8))
    return sum(band.tobytes()) / 512 < 100


def xinput(display, spec):
    """real input to the client by XTEST, for spells that need the player to act: 'key:<keysym>:down|up|tap' (w, Control_L, space, Shift_L) or
    'click:<button>' (1 attacks what the crosshair is on, 3 uses). No pointer move: the game grabs the cursor and a move would turn the player"""
    from Xlib import X as XX, XK, display as xd
    from Xlib.ext import xtest
    d = xd.Display(display); kind, *rest = spec.split(':')
    if kind == 'btn':   # 'btn:3:down' ... 'btn:3:up': hold a mouse button (a scroll's long cast)
        xtest.fake_input(d, XX.ButtonPress if rest[1] == 'down' else XX.ButtonRelease, int(rest[0])); d.sync(); return
    if kind == 'click':
        b = int(rest[0]); xtest.fake_input(d, XX.ButtonPress, b); d.sync(); time.sleep(0.08); xtest.fake_input(d, XX.ButtonRelease, b); d.sync(); return
    kc = d.keysym_to_keycode(XK.string_to_keysym(rest[0]))
    if rest[1] in ('down', 'tap'): xtest.fake_input(d, XX.KeyPress, kc); d.sync()
    if rest[1] == 'tap': time.sleep(0.1)
    if rest[1] in ('up', 'tap'): xtest.fake_input(d, XX.KeyRelease, kc); d.sync()


def poster_frame(path):
    """the frame with the most spell colour (Hasler-Suesstrunk colourfulness above the first frame's) where the caster, in the left quarter, is not hidden
    and the clip has begun; grey spells (rocks, Vex) get an early frame and are picked by hand at review"""
    import numpy as np
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vf', 'scale=160:90', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, 90, 160, 3).astype(np.float32)
    if not len(f): return 0
    rg = f[..., 0] - f[..., 1]; yb = 0.5 * (f[..., 0] + f[..., 1]) - f[..., 2]
    c = np.sqrt(rg.std(axis=(1, 2)) ** 2 + yb.std(axis=(1, 2)) ** 2) + 0.3 * np.sqrt(rg.mean(axis=(1, 2)) ** 2 + yb.mean(axis=(1, 2)) ** 2); c = c - c[0]
    c[np.abs(f[:, :, :40] - f[0, :, :40]).mean(axis=(1, 2, 3)) > 28] = -1e9; c[: int(len(f) * 0.08)] = -1e9
    return int(c.argmax())


def new_frames(path, fps):
    """new frames a second of game time in an encoded clip: a frame within 0.02 grey levels (mean, 1280x720) of the one before is a copy x11grab took
    while the game had not drawn yet; a still scene under the slow dolly still changes by 0.03 or more (Telekinesis, Teleport), a stalled one by under 0.01"""
    import numpy as np
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE); n = copies = 0; prev = None
    while True:
        b = p.stdout.read(1280 * 720)
        if len(b) < 1280 * 720: break
        f = np.frombuffer(b, np.uint8).astype(np.int16)
        if prev is not None: copies += np.abs(f - prev).mean() < 0.02
        prev = f; n += 1
    p.wait()
    return fps * (1 - copies / max(1, n - 1))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('server'); ap.add_argument('out'); ap.add_argument('--log', required=True); ap.add_argument('--speed', type=float, required=True)
    ap.add_argument('--only', default=''); ap.add_argument('--ns', default='irons_spellbooks'); ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--size', default='1920x1080'); ap.add_argument('--at', default=':99+0,0'); ap.add_argument('--fps', type=int, default=60); ap.add_argument('--time', default='12300'); ap.add_argument('--z0', type=int, default=1000); ap.add_argument('--display', default=':99'); ap.add_argument('--redo-below', type=float, default=0); ap.add_argument('--target', choices=sorted(TARGETS), default='dummy'); ap.add_argument('--pitch', type=float); ap.add_argument('--difficulty', choices=('peaceful', 'easy')); ap.add_argument('--diag', default=''); ap.add_argument('--prime', action='store_true')
    ap.add_argument('--system', choices=sorted(SYSTEMS), default='irons')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    import numpy as np
    fifo = os.path.join(a.server, 'cmd.fifo'); raw = os.path.join(a.out, '_raw.mkv'); TICK = 0.05 / a.speed

    def c(cmds, ticks=2):
        """send commands to the server console (one batch runs in one tick), then wait `ticks` game ticks"""
        with open(fifo, 'w') as f: f.write(''.join(x + '\n' for x in ([cmds] if isinstance(cmds, str) else cmds)))
        time.sleep(ticks * TICK)

    def ask(cmd):
        n0 = os.path.getsize(a.log); c(cmd, 3)
        with open(a.log, encoding='utf-8', errors='replace') as f: f.seek(n0); t = f.read()
        m = re.findall(r'(?:Value|Base value) of attribute .* is (-?[0-9.Ee-]+)', t); return float(m[-1]) if m else None

    neutral_for = {}   # robe -> modifier amounts that bring each spell power back to 1.0

    def neutral(robe):
        c(['attribute RenderBot irons_spellbooks:%s modifier remove 0-0-0-77-%d' % (at, k + 1) for k, at in enumerate(ATTR)], 3)
        first = robe not in neutral_for   # robe here is robe|held item|spellbook: each changes the bonus
        if first:
            neutral_for[robe] = {at: 1 / v - 1 for at in ATTR for v in [ask('attribute RenderBot irons_spellbooks:%s get' % at)] if v and abs(v - 1) > 1e-6}
        c(['attribute RenderBot irons_spellbooks:%s modifier add 0-0-0-77-%d lgw_neutral %.8f multiply' % (at, ATTR.index(at) + 1, m) for at, m in neutral_for[robe].items()], 3)
        # read back once per robe (the same robe gives the same bonus); a robe that is still off is reported on every clip it wears
        if first: neutral_for[robe + '?'] = [at for at in ATTR if abs((ask('attribute RenderBot irons_spellbooks:%s get' % at) or 0) - 1) > 0.005]
        return neutral_for[robe + '?']

    goety, ars, brut = a.system == 'goety', a.system == 'ars', a.system == 'brutality'; player = goety or ars or brut   # player: cast by the player's right button, in creative mode
    spells = [s for s in json.load(open(SYSTEMS[a.system], encoding='utf-8'))['spells'] if player or (s['enabled'] and s['ns'] in a.ns.split(','))]
    if a.only: spells = [s for s in spells if s['id'] in a.only.split(',')]
    if a.limit: spells = spells[:a.limit]
    c(['gamerule %s false' % g for g in ('sendCommandFeedback', 'logAdminCommands', 'mobGriefing', 'doDaylightCycle', 'doWeatherCycle', 'doMobSpawning',
                                          'doInsomnia', 'doPatrolSpawning', 'doTraderSpawning')]
      + ['gamerule doImmediateRespawn true', 'gamerule keepInventory true', 'time set ' + a.time, 'difficulty ' + TARGETS[a.target][2], 'op RenderBot',
         'execute as RenderBot run learnSpell learn_all', 'team add lgw_hide', 'team modify lgw_hide nametagVisibility never', 'team join lgw_hide RenderBot'], 4)   # spells that need learning (the Eldritch school) cast nothing until learned
    qcp = os.path.join(a.out, 'qc.jsonl'); qc = {}
    if os.path.exists(qcp):
        for line in open(qcp, encoding='utf-8'): r = json.loads(line); qc[r['id']] = r
    for i, s in enumerate(spells):
        name = s['id'].replace(':', '__'); dst = os.path.join(a.out, name + '.mp4')
        if os.path.exists(dst) and not (a.redo_below and qc.get(s['id'], {}).get('fps', 99) < a.redo_below): continue
        if subprocess.run(['pgrep', '-f', 'java -Djava.net.preferIPv6Addresses'], capture_output=True).returncode:   # the client is gone (a spell crashed it): stop, a restart resumes here
            print('client not running: stopped before ' + s['id'], flush=True); raise SystemExit(2)
        st = dict(GOETY_KIND.get(s.get('kind'), {}) if goety else ars_stage(s) if ars else {}, **SETUP.get(s['id'], {})); tg = TARGETS[st.get('target', a.target)]
        X, Z = 4000, a.z0 + 100 * i; g = st.get('gap', 3.5); lvl = st.get('level') or s.get('maxLevel') or 1; t = (s.get('castTime') or 0) / 20
        if goety:   # cast ticks: 0 instant, 72000 held until let go, else a charge
            ct = s.get('cast') or 0; t = 5.0 if ct >= 72000 else ct / 20; lvl = 0
            if not st.get('nocast') and ct: st = dict(st, after=sorted(st.get('after', []) + [[100 if ct >= 72000 else ct + 10, 'btn:3:up']], key=lambda x: x[0]))
            if s.get('kind') == 'SummonSpell' and 'secs' not in st: st = dict(st, secs=min(16.0, t + 10))   # the minion rises seconds after the cast (Blasting, cast 3 s, stood up at about 9 s in an 11 s clip)
        if ars: t = 0; lvl = 0
        if brut:
            ct = s.get('castTicks') or 0; lvl = st.get('level', 1); t = ct / 20 if s.get('cast') == 'channelling' else 5.0 if s.get('cast') == 'continuous' else 0
            if not st.get('nocast') and s.get('cast') != 'instant': st = dict(st, after=sorted(st.get('after', []) + [[ct + 10 if s.get('cast') == 'channelling' else 100, 'btn:3:up']], key=lambda x: x[0]))
        var = {'X': X, 'Z': Z, 'Xt': '%.1f' % (X + g), 'Zb': Z - 3, 'Xa': X + 1, 'Xb': X + 6, 'Za': Z - 2, 'Zc': Z + 3, 'Xn': '%.1f' % (X + g - 1.2), 'X4': X + 4,
               'Zm2': Z - 2, 'Xm3': X - 3, 'Xp3': X + 3, 'Zm3': Z - 3, 'Zp3': Z + 3, 'Xc': '%.1f' % (X - g + 0.5)}
        dur = st.get('secs') or (6.0 if ars or s.get('cast') in ('INSTANT', 0, 'instant') else min(11, t + 6.0))
        c(['cam-server stop RenderBot', 'effect clear RenderBot', 'effect give RenderBot minecraft:instant_health 1 20 true', 'weather clear', 'time set ' + a.time,
           'gamerule doDaylightCycle false', 'difficulty ' + st.get('difficulty', a.difficulty or tg[2]), 'curios clear RenderBot spellbook',
           'clearCooldowns player RenderBot', 'clearRecasts player RenderBot', 'gamemode %s RenderBot' % ('creative' if player and not st.get('survival') else 'survival'), 'attribute RenderBot irons_spellbooks:mana_regen modifier remove 0-0-0-78-1', 'attribute RenderBot irons_spellbooks:max_mana modifier remove 0-0-0-78-2', 'attribute RenderBot irons_spellbooks:spell_power modifier remove 0-0-0-78-3',   # /cast still waits out a spell's cooldown (Supernova 180 s, Dead King 3600 s), so a second take of a spell cast nothing
           'forceload remove all', 'forceload add %d %d %d %d' % (X - 24, Z - 24, X + 24, Z + 24)], 15)
        c(['tp RenderBot %.1f -60 %d' % (X - g, Z), 'fill %d -61 %d %d -61 %d minecraft:polished_deepslate' % (X - 24, Z - 24, X + 24, Z + 24),
           'fill %d -60 %d %d -56 %d minecraft:barrier' % (int(X + g + 1.5), Z - 1, int(X + g + 1.5), Z + 1), 'kill @e[type=!player]',
           ('summon %s %.1f -60 %.1f %s' % (tg[0], X + g, Z + 0.5, tg[1])).rstrip() if tg[0] else 'time query gametime'] + [p % var for p in st.get('pre', [])], 10)   # a trailing space fails the command
        robe = ROBE.get((s.get('school') or '').split(':')[-1], 'wandering_magician')
        if goety:
            robe = None; off = []; var.update(wand=st.get('hold', 'goety:dark_wand'), focus=s['id'])
            if st.get('survival'): c(['goety soul set RenderBot 100000'], 2)   # soul energy for a survival cast
            c(['item replace entity RenderBot armor.%s with minecraft:air' % slot for slot in ('head', 'chest', 'legs', 'feet')] + ['setblock %(X)d -62 %(Z)d minecraft:air' % var, WAND[0] % var], 2)   # air first: setblock leaves a barrel left by an earlier run as it is
            c([w % var for w in WAND[1:]] + [x % var for x in st.get('gear', [])], 4)
        elif brut:
            robe = None; off = []; tome = 'brutality:%s{Spells:[{SpellId:"%s",SpellLevel:%d}],SelectedSpellIndex:0}' % (BTOME.get(s.get('school'), 'cosmic_tome'), s['id'], lvl)
            c(['item replace entity RenderBot armor.%s with minecraft:air' % slot for slot in ('head', 'chest', 'legs', 'feet')] + ['item replace entity RenderBot weapon.mainhand with ' + st.get('hold', tome),
               'attribute RenderBot brutality:max_mana base set 1000', 'attribute RenderBot brutality:mana_regen base set 1000'] + [x % var for x in st.get('gear', [])], 20)   # a second for the mana to fill
        elif ars:
            robe = None; off = []
            c(['item replace entity RenderBot armor.%s with minecraft:air' % slot for slot in ('head', 'chest', 'legs', 'feet')] + ['item replace entity RenderBot weapon.mainhand with ' + st['hold']] + [x % var for x in st.get('gear', [])], 4)
        else:
          c(['item replace entity RenderBot armor.%s with irons_spellbooks:%s_%s' % (slot, robe, part) for slot, part in (('head', 'helmet'), ('chest', 'chestplate'), ('legs', 'leggings'), ('feet', 'boots'))]
            + ['item replace entity RenderBot weapon.mainhand with ' + st.get('hold', 'irons_spellbooks:graybeard_staff')] + [x % var for x in st.get('gear', [])], 4)   # gear: after the robes and the held item
          off = neutral(robe + '|' + st.get('hold', '') + '|' + str(any('curios' in x for x in st.get('pre', []))))
        if a.prime and not player and not st.get('nocast') and not st.get('prime'): st = dict(st, prime=int(s.get('castTime') or 0) + 40)   # --prime: every spell gets the throwaway cast
        if st.get('prime'):   # a throwaway cast after the weapon is in hand, waited out before recording (the note above the weapon spells in SETUP)
            c(['cast RenderBot %s %d' % (s['id'], lvl)], st['prime']); c(['clearCooldowns player RenderBot', 'clearRecasts player RenderBot', 'kill @e[type=!player,type=!%s]' % tg[0]] if tg[0] else ['clearCooldowns player RenderBot'], 10)
        k1, k2 = CAMS['eyes' if a.diag else st.get('cam', 'side')]   # --diag: the player's view, as the CMDCam camera hides the HUD   # the side camera: 6.5 blocks from the line between caster and dummy, looking north (yaw 180), 5 degrees down
        # aim from the eyes (1.62 above the feet) at the target's chest (1.1 above its feet). Not `tp ... facing`: run from the console it turns the body
        # from its feet, so the caster looked 8.9 degrees up (Rotation [-90, -8.93] read back), every spell that ray-casts for a target found none and cast
        # nothing, and projectiles flew over the target (2026-11-14)
        # --pitch overrides it for spells that grow out of the first block the eye ray meets: at 4.6 degrees that is the barrier behind the dummy,
        # so their crystals stood cut at the right edge; 14 degrees meets the floor under the dummy
        pitch = a.pitch if a.pitch is not None else st.get('pitch', math.degrees(math.atan2(1.62 - 1.1, 2 * g - 0.5)))
        c(['tp RenderBot %.1f -60 %.1f -90 %.2f' % (X - g + 0.5, Z + 0.5, pitch)] + ([] if k1 is None else   # 'eyes': the player's own view, no CMDCam path
          ['cam-server remove clip', 'cam-server create clip', 'cam-server get clip mode outside']
          + ['cam-server get clip add %.2f %.2f %.2f %g %g 0 50' % (X + k[0], k[1], Z + k[2], k[3], k[4]) for k in (k1, k2)]
          + ['cam-server get clip interpolation hermite', 'cam-server get clip duration %ds' % int(dur + 3), 'cam-server start clip RenderBot']), 15)
        for _ in range(0 if st.get('nogui') or any(p.startswith('time set') for p in st.get('pre', [])) else 3):   # a night sky or a pool reads as a dimmed screen: Escape would open the pause menu
            if not gui_open(a.display): break
            from Xlib import X as XX, XK, display as xd   # Escape by XTEST, no pointer move (the game grabs the cursor; a jump would turn the camera)
            from Xlib.ext import xtest
            xdp = xd.Display(a.display); kc = xdp.keysym_to_keycode(XK.string_to_keysym('Escape'))
            xtest.fake_input(xdp, XX.KeyPress, kc); xdp.sync(); time.sleep(0.05); xtest.fake_input(xdp, XX.KeyRelease, kc); xdp.sync(); time.sleep(20 * TICK)
        if st.get('hud'): xinput(a.display, 'key:F1:tap'); time.sleep(4 * TICK)   # the HUD on for spells whose effect is the player's own bars (hearts, mana)
        if a.diag:   # no clip: the HUD is on (F1 pressed before the run) and the screen is grabbed after the cast, to read the cast's error message
            import threading
            def grabs(t0box, n=name, t=t):
                for k, w in enumerate((0.6, 2.5, t + 0.8, t + 3.0)):
                    while not t0box: time.sleep(0.05)
                    time.sleep(max(0.0, t0box[0] + w / a.speed - time.time()))
                    subprocess.run(['import', '-window', 'root', '-resize', '50%', os.path.join(a.diag, '%s_%d.jpg' % (n, k))], env=dict(os.environ, DISPLAY=a.display))
            os.makedirs(a.diag, exist_ok=True); t0box = []; rec = threading.Thread(target=grabs, args=(t0box,)); rec.start()
        else:
          t0box = []
          rec = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'x11grab', '-framerate', '%g' % (a.fps * a.speed), '-video_size', a.size, '-i', a.at, '-t', '%.2f' % (dur / a.speed),
                                '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '12', raw])
        time.sleep(12 * TICK); cast = 'click:3' if ars else ('btn:3:down' if s.get('cast') not in ('instant', None) else 'click:3') if brut else ('btn:3:down' if s.get('cast') else 'click:3') if goety else 'cast RenderBot %s %d' % (s['id'], lvl)
        do = lambda cmd: xinput(a.display, cmd) if cmd.split(':')[0] in ('key', 'click', 'btn') else (xinput(a.display, cast) if player and cmd == 'cast' else c(cast if cmd == 'cast' else cmd % var, 0))
        lead = sorted(st.get('lead', []), key=lambda x: -x[0]); tl = time.time() + (lead[0][0] * TICK if lead else 0)
        for before, cmd in lead:   # commands this many ticks before the cast (a bolt before a buff, to compare the damage)
            time.sleep(max(0.0, tl - before * TICK - time.time())); do(cmd)
        time.sleep(max(0.0, tl - time.time()))
        if player:   # the cast is the player's right button, not a console command
            if st.get('before'): c([b % var for b in st['before']], 0)
            if not st.get('nocast'): do('cast')
        else: c([b % var for b in st.get('before', [])] + ([] if st.get('nocast') else [cast]), 0)
        t0 = time.time(); t0box.append(t0)
        for when, cmd in st.get('after', []):   # recasts, attacks and key presses while recording, at their tick after the first cast
            time.sleep(max(0.0, t0 + when * TICK - time.time())); do(cmd)
        for k in ('w', 'Control_L', 'space', 'Shift_L'): xinput(a.display, 'key:%s:up' % k)   # no key left held into the next clip
        xinput(a.display, 'btn:3:up')
        if a.diag:
            rec.join(); print(s['id'], flush=True); continue
        rec.wait()
        if st.get('hud'): xinput(a.display, 'key:F1:tap')
        # while it encodes, the client (it draws all the time, on every core) gives way; it gets its priority back before the next clip is recorded
        cl = subprocess.run(['pgrep', '-f', 'java -Djava.net.preferIPv6Addresses'], capture_output=True, text=True).stdout.split()
        renice = lambda n: [subprocess.run(['renice', '-n', str(n), '-p', t], capture_output=True) for p in cl if os.path.isdir('/proc/%s/task' % p) for t in os.listdir('/proc/%s/task' % p)]
        renice(19)
        part = dst[:-4] + '.part.mp4'   # written whole, then renamed: a run stopped half way leaves no clip that a resume would skip
        r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-vf', 'setpts=PTS*%g,%sscale=1280:720:flags=lanczos' % (a.speed, (st['crop'] + ',') if st.get('crop') else ''), '-r', str(a.fps), '-an', '-c:v', 'libx264', '-preset', 'slow',
                            '-crf', '28', '-tune', 'animation', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', part])
        k = poster_frame(part)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', part, '-vf', 'select=eq(n\\,%d),scale=960:540:flags=lanczos' % k, '-frames:v', '1', '-c:v', 'libwebp', '-quality', '80', dst[:-4] + '.webp'])
        # smoothness: new frames a second (new_frames); a clip under --redo-below is recorded again on the next run
        fps = new_frames(part, a.fps) if r.returncode == 0 else 0
        if r.returncode == 0: os.replace(part, dst)
        renice(-5)
        qc[s['id']] = {'id': s['id'], 'fps': round(fps, 1), 'bytes': os.path.getsize(dst) if os.path.exists(dst) else 0, 'poster': k, 'robe': robe, 'level': lvl, 'secs': dur, 'off': off}
        with open(qcp, 'w', encoding='utf-8') as f: f.write(''.join(json.dumps(r) + '\n' for r in qc.values()))
        time.sleep(max(0.0, t + 1.5 - dur) / a.speed)   # a /cast while the player is still casting cancels that cast (AbstractSpell.attemptInitiateCast)
        print('%3d/%d %-48s level %d %.1fs %8d B %4.1f fps%s%s' % (i + 1, len(spells), s['id'], lvl, dur, os.path.getsize(dst) if os.path.exists(dst) else 0, fps,
              '' if r.returncode == 0 else '  FAILED', ('  spell power not neutral: ' + ','.join(off)) if off else ''), flush=True)
    c('cam-server stop RenderBot', 2)
    for f in (raw,):
        if os.path.exists(f): os.remove(f)


if __name__ == '__main__': main()
