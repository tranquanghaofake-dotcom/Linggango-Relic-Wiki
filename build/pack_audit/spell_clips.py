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
`/cast RenderBot <spell> <max level>` (every spell learned first; SETUP below changes the stage for spells that need more); the 1080p recording is re-timed and scaled to 1280x720 (lanczos: the downscale also smooths the edges) at 60 fps, H.264 CRF 23 (preset medium).
Poster: poster_frame() (the most spell colour while the caster is still in sight), 960x540 WebP.
QC: OUT_DIR/qc.jsonl, one line per clip (new frames a second by new_frames(), bytes, poster frame, robe); --redo-below N records again the clips under N fps; the run stops if the client is gone.
Length in game time: instant 6 s; long and continuous = cast time + 6 s, at most 11 s."""
import os, re, json, math, time, subprocess, argparse
H = os.path.dirname(os.path.abspath(__file__))
SPELLS = os.path.join(H, '..', 'patches', 'spells.json')
ROBE = {'fire': 'pyromancer', 'ice': 'cryomancer', 'lightning': 'electromancer', 'holy': 'priest', 'blood': 'cultist', 'ender': 'shadowwalker', 'evocation': 'archevoker', 'nature': 'plagued'}
# what the spells are cast at: the Target Dummy (shows damage numbers), or a mob that stands still and does not burn, for spells that need a living target;
# the difficulty the stage needs (peaceful removes a hostile mob the tick it is summoned, so the husk needs easy; NoAI keeps it from attacking)
TARGETS = {'dummy': ('dummmmmmy:target_dummy', '', 'peaceful'),
           'husk': ('minecraft:husk', '{NoAI:1b,Silent:1b,PersistenceRequired:1b,Rotation:[90f,0f],Attributes:[{Name:"minecraft:generic.max_health",Base:1000d}],Health:1000f}', 'easy'),
           'sheep': ('minecraft:sheep', '{NoAI:1b,Silent:1b,PersistenceRequired:1b,Rotation:[90f,0f],Color:11b}', 'easy'),   # blue: Wololo turns it red
           'pig': ('minecraft:pig', '{Silent:1b,PersistenceRequired:1b,Rotation:[90f,0f]}', 'easy'),   # with AI, so a pull can move it
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
        'behind': ((-11.0, -57.4, 1.6, -95, 8), (-10.4, -57.42, 1.2, -95, 8))}     # behind the caster, looking at the target: a wall built across the line
# what a spell needs that the plain stage lacks (2026-11-15: the 122 spells recipe 4 showed nothing for, sorted by cause; each was read from the spell's
# checkPreCastConditions or found by trying). Keys: hold (main hand item instead of the staff), target, difficulty, pitch, cam, gap (caster to target, default
# 3.5 each side of the centre), secs (clip length in game seconds), pre (commands after the stage is built), after ([ticks after the cast, command or 'cast' to
# cast again], in order), before (commands in the same tick as the cast); these commands may use %(X)d, %(Z)d (stage centre), %(Xt)s (the target's x),
# %(Zb)d (3 blocks behind the line, away from the camera), %(Xa)d..%(Xb)d and %(Za)d..%(Zc)d (a patch of floor around the target)
DAMAGE_ME = 'execute at RenderBot run damage RenderBot 2 minecraft:mob_attack by @e[type=minecraft:husk,limit=1,sort=nearest]'   # an attack, to set off a buff that reacts to one
HIT_TARGET = 'execute at RenderBot run damage @e[type=dummmmmmy:target_dummy,limit=1,sort=nearest] 2 minecraft:player_attack by RenderBot'   # the caster's attack
SECOND = 'summon minecraft:husk %(Xt)s -60 %(Zb)d.5 {NoAI:1b,Silent:1b,PersistenceRequired:1b,Rotation:[90f,0f],Tags:["t2"]}'   # a second creature for spells that link two
FACE_SECOND = 'execute as RenderBot at @s anchored eyes run tp @s ~ ~ ~ facing entity @e[tag=t2,limit=1] eyes'
SETUP = {
    # Traveloptics weapon spells: checkPreCastConditions wants the weapon (any level) in the main hand
    'traveloptics:extinction': {'hold': 'traveloptics:gauntlet_of_extinction_level_three', 'target': 'husk', 'cam': 'mid'},
    'traveloptics:shear_of_the_stars': {'hold': 'traveloptics:stellothorn_level_three', 'cam': 'wide'},
    'traveloptics:skypiercer': {'hold': 'traveloptics:trident_of_the_eternal_maelstrom_level_three', 'cam': 'wide'},
    'traveloptics:supernova': {'hold': 'traveloptics:wand_of_final_light', 'cam': 'sky', 'secs': 20},
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
    'traveloptics:call_forth_the_dead_king': {'difficulty': 'easy', 'cam': 'wide', 'secs': 20},
    'traveloptics:conjure_void_tomes': {'difficulty': 'easy', 'cam': 'wide'},
    'traveloptics:echo_of_the_abyss': {'difficulty': 'easy', 'cam': 'wide'},
    'legendary_spellbooks:fossilized_fury': {'difficulty': 'easy', 'cam': 'mid', 'secs': 14},
    # spells that change a living creature
    'irons_spellbooks:wololo': {'target': 'sheep'},
    'peyroscythe:young_for_you': {'target': 'sheep'},
    'irons_spellbooks:telekinesis': {'target': 'husk'},
    'traveloptics:eek': {'target': 'husk'},
    # spells that only touch hostile creatures (the dummy is not one)
    'traveloptics:nullflare': {'target': 'husk'}, 'traveloptics:em_pulse': {'target': 'husk'}, 'traveloptics:shadowed_miasma': {'target': 'husk'},
    # melee spells: the target within reach
    'traveloptics:gyro_slash': {'hold': 'traveloptics:infernal_devastator_level_three', 'gap': 1.8},
    'irons_spellbooks:flaming_strike': {'gap': 1.8}, 'refined_mod:moon_slash': {'gap': 1.8, 'hold': 'minecraft:netherite_sword'},
    # spells that link two creatures: cast at the target, turn to a second one, cast again
    'somakespells:chain_connection': {'target': 'husk', 'pre': [SECOND], 'after': [[30, FACE_SECOND], [32, 'cast']]},
    # Eldritch spells need learning (AbstractSpell.canBeCastedBy: requiresLearning and not isLearned): main() teaches every spell first
    'irons_spellbooks:eldritch_blast': {}, 'irons_spellbooks:sonic_boom': {}, 'irons_spellbooks:sculk_tentacles': {'pitch': 14, 'cam': 'far'},
    # a buff on the caster: only the caster to look at
    'somakespells:combustion': {'cam': 'close'},
    # a buff that answers an attack
    'irons_spellbooks:evasion': {'target': 'husk', 'after': [[30, DAMAGE_ME], [70, DAMAGE_ME]]},
    'traveloptics:reversal': {'hold': 'minecraft:diamond_sword', 'target': 'husk', 'after': [[30, DAMAGE_ME], [70, DAMAGE_ME]]},   # a sword: TravelopticsTags.CAN_CAST_REVERSAL
    'peyroscythe:sinfire_embrace': {'after': [[30, HIT_TARGET], [60, HIT_TARGET]]},
    # the sky
    'peyroscythe:made_in_heaven': {'cam': 'sky', 'pre': ['gamerule doDaylightCycle true', 'time set 11000'], 'secs': 11},   # the sun sets, then night
    'peyroscythe:crimson_moon': {'cam': 'sky', 'pre': ['time set 18000']},
    'legendary_spellbooks:energy_beam': {'cam': 'mid'},
    # cast at the floor near the dummy, not the barrier behind it
    'irons_spellbooks:black_hole': {'pitch': 14, 'cam': 'farup'},
    # --- 2026-11-15, third round: the rest of the 122 ---
    'traveloptics:apex_harvest': {'hold': 'traveloptics:cursed_wraithblade_level_three', 'gap': 1.8},
    'traveloptics:galena_shatter': {'hold': 'traveloptics:galenic_polarizer_level_three', 'target': 'husk'},
    'refined_mod:frost_strike': {'gap': 1.8, 'hold': 'minecraft:netherite_sword'}, 'refined_mod:storm_blade': {'gap': 1.8, 'hold': 'minecraft:netherite_sword'},   # 'from your blade'
    'irons_spellbooks:throw': {'hold': 'irons_spellbooks:keeper_flamberge'},
    # summons that the side camera cuts or that stand in front of it
    'traveloptics:axe_of_the_doomed': {'difficulty': 'easy', 'cam': 'wide'}, 'traveloptics:eternal_sentinel': {'difficulty': 'easy', 'cam': 'wide'},
    'traveloptics:sword_of_the_ancients': {'difficulty': 'easy', 'cam': 'wide'}, 'traveloptics:magnetron_deployment': {'difficulty': 'easy', 'cam': 'wide'},
    'traveloptics:sticky_steed_summon': {'difficulty': 'easy', 'cam': 'wide'}, 'gtbcs_geomancy_plus:solar_chorus': {'difficulty': 'easy', 'cam': 'wide'},
    # big things the side camera cuts
    'peyroscythe:glacier': {'cam': 'wide'}, 'gtbcs_geomancy_plus:weeping_wall': {'cam': 'behind'}, 'traveloptics:stele_cascade': {'cam': 'wide'},
    'somakespells:lightning_dance': {'target': 'husk', 'cam': 'mid'}, 'legendary_spellbooks:annihilation_geyser': {'cam': 'mid', 'secs': 14},
    # cast at the floor
    'irons_spellbooks:spectral_hammer': {'pitch': 14, 'pre': ['fill %(Xa)d -63 %(Za)d %(Xb)d -61 %(Zc)d minecraft:stone']},   # stone: ModTags.SPECTRAL_HAMMER_MINEABLE
    'irons_spellbooks:touch_dig': {'pitch': 14, 'cam': 'tclose'}, 'peyroscythe:chaos_cradle': {'pitch': 14}, 'traveloptics:overflow': {'pitch': 14, 'cam': 'mid'},
    # several casts: Wall of Fire places an anchor per cast; Bloodmark marks four points, the fifth cast links them; Psychic Bolt picks targets, then fires
    'irons_spellbooks:wall_of_fire': {'pitch': 14, 'after': [[15, 'execute as RenderBot at @s run tp @s ~ ~ ~ -60 14'], [16, 'cast'], [31, 'execute as RenderBot at @s run tp @s ~ ~ ~ -120 14'], [32, 'cast']]},
    'somakespells:bloodmark': {'pitch': 30, 'cam': 'mid', 'after': [[12, 'execute as RenderBot at @s run tp @s ~ ~ ~ -60 30'], [13, 'cast'], [25, 'execute as RenderBot at @s run tp @s ~ ~ ~ -30 30'], [26, 'cast'],
                                                                [38, 'execute as RenderBot at @s run tp @s ~ ~ ~ -120 30'], [39, 'cast'], [52, 'cast']]},
    'traveloptics:psychic_bolt': {'target': 'husk', 'pre': [SECOND], 'after': [[20, FACE_SECOND], [22, 'cast']], 'secs': 11},
    'somakespells:blessed_connection': {'target': 'husk', 'pre': [SECOND], 'after': [[30, FACE_SECOND], [32, 'cast']]},
    'somakespells:cursed_connection': {'target': 'husk', 'pre': [SECOND], 'after': [[30, FACE_SECOND], [32, 'cast']]},
    # spells that need one of the caster's summons: a Vex first
    'traveloptics:vigor_siphon': {'pre': ['cast RenderBot irons_spellbooks:summon_vex 1'], 'cam': 'mid'},
    'irons_spellbooks:sacrifice': {'pre': ['cast RenderBot irons_spellbooks:summon_vex 1'], 'cam': 'mid',
                                   'before': ['execute as RenderBot at @s anchored eyes run tp @s ~ ~ ~ facing entity @e[type=irons_spellbooks:summoned_vex,limit=1,sort=nearest] eyes']},
    # fear and madness: a husk that moves (and a second creature for it to fight)
    'peyroscythe:illusion_fear': {'target': 'husk_ai'}, 'peyroscythe:illusion_crazy': {'target': 'husk_ai', 'pre': [SECOND]},
    # hostile targets
    'somakespells:lightning_strike': {'target': 'husk'}, 'somakespells:lightning_spear': {'target': 'husk'}, 'somakespells:ram_tchum': {'target': 'husk'},
    'somakespells:resonant_pulse': {'target': 'husk'}, 'traveloptics:violent_skreech': {'target': 'husk'}, 'traveloptics:rainfall': {'target': 'husk', 'cam': 'mid'},
    'traveloptics:despair': {'target': 'husk'}, 'traveloptics:blood_howl': {'target': 'husk'}, 'traveloptics:hydroshot': {'target': 'husk'},
    'traveloptics:flood_slash': {'target': 'husk'}, 'traveloptics:aqua_missiles': {'target': 'husk', 'cam': 'mid'}, 'peyroscythe:black_fireball': {'target': 'husk'},
    # a glow or a mark on the target
    'irons_spellbooks:blessing_of_life': {'cam': 'tclose'}, 'irons_spellbooks:blight': {'cam': 'tclose'},
    # buffs that answer an attack
    'legendary_spellbooks:ambush_thorns': {'target': 'husk', 'after': [[30, DAMAGE_ME], [70, DAMAGE_ME]]},
    'irons_spellbooks:abyssal_shroud': {'target': 'husk', 'after': [[30, DAMAGE_ME], [70, DAMAGE_ME]]},
    'somakespells:damned_demomans': {'target': 'husk', 'after': [[30, DAMAGE_ME]]},
    'irons_spellbooks:greater_heal': {'pre': ['damage RenderBot 12 minecraft:magic'], 'cam': 'close'},
    'peyroscythe:made_in_heaven_real': {'cam': 'sky', 'pre': ['gamerule doDaylightCycle true', 'time set 11000'], 'secs': 11},
    'irons_spellbooks:frost_step': {'after': [[2, 'data merge entity @e[type=irons_spellbooks:frozen_humanoid,limit=1,sort=nearest] {CustomNameVisible:0b}'],
                                              [3, 'team join lgw_hide @e[type=irons_spellbooks:frozen_humanoid]']]},   # the ice copy shows the caster's name
}
ATTR = ['spell_power', 'cast_time_reduction', 'cooldown_reduction'] + [k + '_spell_power' for k in ('fire', 'ice', 'lightning', 'holy', 'ender', 'blood', 'evocation', 'nature', 'eldritch')]


def gui_open(display):
    """a screen is open (Pocket Dimension and Summon Ender Chest open an Ender Chest and it stays; Escape on no screen opens the pause menu): every screen
    dims the world behind it, so the sky band at 30-40% of the height, pink at time 12300 (luminance 135 or more in every clip of 2026-11-14), falls to about 55"""
    import io
    from PIL import Image
    im = Image.open(io.BytesIO(subprocess.run(['import', '-window', 'root', 'png:-'], env=dict(os.environ, DISPLAY=display), capture_output=True).stdout)).convert('L')
    w, h = im.size; band = im.crop((0, int(h * .3), w, int(h * .4))).resize((64, 8))
    return sum(band.tobytes()) / 512 < 100


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
    ap.add_argument('--size', default='1920x1080'); ap.add_argument('--at', default=':99+0,0'); ap.add_argument('--fps', type=int, default=60); ap.add_argument('--time', default='12300'); ap.add_argument('--z0', type=int, default=1000); ap.add_argument('--display', default=':99'); ap.add_argument('--redo-below', type=float, default=0); ap.add_argument('--target', choices=sorted(TARGETS), default='dummy'); ap.add_argument('--pitch', type=float)
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
        first = robe not in neutral_for
        if first:
            neutral_for[robe] = {at: 1 / v - 1 for at in ATTR for v in [ask('attribute RenderBot irons_spellbooks:%s get' % at)] if v and abs(v - 1) > 1e-6}
        c(['attribute RenderBot irons_spellbooks:%s modifier add 0-0-0-77-%d lgw_neutral %.8f multiply' % (at, ATTR.index(at) + 1, m) for at, m in neutral_for[robe].items()], 3)
        # read back once per robe (the same robe gives the same bonus); a robe that is still off is reported on every clip it wears
        if first: neutral_for[robe + '?'] = [at for at in ATTR if abs((ask('attribute RenderBot irons_spellbooks:%s get' % at) or 0) - 1) > 0.005]
        return neutral_for[robe + '?']

    spells = [s for s in json.load(open(SPELLS, encoding='utf-8'))['spells'] if s['enabled'] and s['ns'] in a.ns.split(',')]
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
        st = SETUP.get(s['id'], {}); tg = TARGETS[st.get('target', a.target)]
        X, Z = 4000, a.z0 + 100 * i; g = st.get('gap', 3.5); lvl = s.get('maxLevel') or 1; t = (s.get('castTime') or 0) / 20
        var = {'X': X, 'Z': Z, 'Xt': '%.1f' % (X + g), 'Zb': Z - 3, 'Xa': X + 1, 'Xb': X + 6, 'Za': Z - 2, 'Zc': Z + 3}
        dur = st.get('secs') or (6.0 if s.get('cast') == 'INSTANT' else min(11, t + 6.0))
        c(['cam-server stop RenderBot', 'effect clear RenderBot', 'effect give RenderBot minecraft:instant_health 1 20 true', 'weather clear', 'time set ' + a.time,
           'gamerule doDaylightCycle false', 'difficulty ' + st.get('difficulty', tg[2]),
           'forceload remove all', 'forceload add %d %d %d %d' % (X - 24, Z - 24, X + 24, Z + 24)], 15)
        c(['tp RenderBot %.1f -60 %d' % (X - g, Z), 'fill %d -61 %d %d -61 %d minecraft:polished_deepslate' % (X - 24, Z - 24, X + 24, Z + 24),
           'fill %d -60 %d %d -56 %d minecraft:barrier' % (int(X + g + 1.5), Z - 1, int(X + g + 1.5), Z + 1), 'kill @e[type=!player]',
           ('summon %s %.1f -60 %.1f %s' % (tg[0], X + g, Z + 0.5, tg[1])).rstrip()] + [p % var for p in st.get('pre', [])], 10)   # a trailing space fails the command
        robe = ROBE.get((s.get('school') or '').split(':')[-1], 'wandering_magician')
        c(['item replace entity RenderBot armor.%s with irons_spellbooks:%s_%s' % (slot, robe, part) for slot, part in (('head', 'helmet'), ('chest', 'chestplate'), ('legs', 'leggings'), ('feet', 'boots'))]
          + ['item replace entity RenderBot weapon.mainhand with ' + st.get('hold', 'irons_spellbooks:graybeard_staff')], 4)
        off = neutral(robe)
        k1, k2 = CAMS[st.get('cam', 'side')]   # the side camera: 6.5 blocks from the line between caster and dummy, looking north (yaw 180), 5 degrees down
        # aim from the eyes (1.62 above the feet) at the target's chest (1.1 above its feet). Not `tp ... facing`: run from the console it turns the body
        # from its feet, so the caster looked 8.9 degrees up (Rotation [-90, -8.93] read back), every spell that ray-casts for a target found none and cast
        # nothing, and projectiles flew over the target (2026-11-14)
        # --pitch overrides it for spells that grow out of the first block the eye ray meets: at 4.6 degrees that is the barrier behind the dummy,
        # so their crystals stood cut at the right edge; 14 degrees meets the floor under the dummy
        pitch = a.pitch if a.pitch is not None else st.get('pitch', math.degrees(math.atan2(1.62 - 1.1, 2 * g - 0.5)))
        c(['tp RenderBot %.1f -60 %.1f -90 %.2f' % (X - g + 0.5, Z + 0.5, pitch), 'cam-server remove clip', 'cam-server create clip', 'cam-server get clip mode outside']
          + ['cam-server get clip add %.2f %.2f %.2f %g %g 0 50' % (X + k[0], k[1], Z + k[2], k[3], k[4]) for k in (k1, k2)]
          + ['cam-server get clip interpolation hermite', 'cam-server get clip duration %ds' % int(dur + 3), 'cam-server start clip RenderBot'], 15)
        for _ in range(0 if any(p.startswith('time set') for p in st.get('pre', [])) else 3):   # a night sky reads as a dimmed screen: Escape would open the pause menu
            if not gui_open(a.display): break
            from Xlib import X as XX, XK, display as xd   # Escape by XTEST, no pointer move (the game grabs the cursor; a jump would turn the camera)
            from Xlib.ext import xtest
            xdp = xd.Display(a.display); kc = xdp.keysym_to_keycode(XK.string_to_keysym('Escape'))
            xtest.fake_input(xdp, XX.KeyPress, kc); xdp.sync(); time.sleep(0.05); xtest.fake_input(xdp, XX.KeyRelease, kc); xdp.sync(); time.sleep(20 * TICK)
        rec = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'x11grab', '-framerate', '%g' % (a.fps * a.speed), '-video_size', a.size, '-i', a.at, '-t', '%.2f' % (dur / a.speed),
                                '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '12', raw])
        time.sleep(12 * TICK); cast = 'cast RenderBot %s %d' % (s['id'], lvl); c([b % var for b in st.get('before', [])] + [cast], 0); t0 = time.time()
        for when, cmd in st.get('after', []):   # recasts and attacks while recording, at their tick after the first cast
            time.sleep(max(0.0, t0 + when * TICK - time.time())); c(cast if cmd == 'cast' else cmd % var, 0)
        rec.wait()
        # while it encodes, the client (it draws all the time, on every core) gives way; it gets its priority back before the next clip is recorded
        cl = subprocess.run(['pgrep', '-f', 'java -Djava.net.preferIPv6Addresses'], capture_output=True, text=True).stdout.split()
        renice = lambda n: [subprocess.run(['renice', '-n', str(n), '-p', t], capture_output=True) for p in cl if os.path.isdir('/proc/%s/task' % p) for t in os.listdir('/proc/%s/task' % p)]
        renice(19)
        part = dst[:-4] + '.part.mp4'   # written whole, then renamed: a run stopped half way leaves no clip that a resume would skip
        r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-vf', 'setpts=PTS*%g,scale=1280:720:flags=lanczos' % a.speed, '-r', str(a.fps), '-an', '-c:v', 'libx264', '-preset', 'medium',
                            '-crf', '23', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', part])
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
