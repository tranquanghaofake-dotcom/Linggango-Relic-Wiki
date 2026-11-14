#!/usr/bin/env python3
"""Record a short clip of every spell, from the real game, into OUT_DIR/<ns>__<spell>.mp4 plus a poster OUT_DIR/<ns>__<spell>.jpg (resumable: an existing clip is kept).
Usage: python3 -I spell_clips.py SERVER_DIR OUT_DIR --log SERVER_LOG [--only ns:spell,...] [--ns irons_spellbooks,...] [--limit N]
Needs, running (docs/plans/2026-11-14-mechanics-effects-spells.md, "Clip: the recipe"): a Forge 1.20.1 dedicated server in SERVER_DIR, flat world,
offline mode, `cmd.fifo` as its stdin (`tail -f cmd.fifo | java ... nogui > SERVER_LOG`), the client's mods plus CMDCam 2.2.1 and CreativeCore on both sides;
a client joined as RenderBot on Xvfb :99 with a 960x540 window (portablemc --resolution 960x540; the window sits at +160,90 on a 1280x720 screen),
GUI hidden (F1), Oculus with the Potato Lite shader, drawn by software GL (LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe MESA_GL_VERSION_OVERRIDE=4.6).
Checked on 2026-11-14 (8 spells): at 960x540 the game draws 42-50 frames a second, so a 30 fps clip has no repeated frames (1280x720 drew 18-24).
For each spell, on a fresh stage 100 blocks along z (forceloaded, so the floor is placed before anything is drawn):
- a polished deepslate floor, time 12300 (a pink dusk sky with the figures still lit), no mob spawning;
- the caster at x-3.5 and a Target Dummy at x+3.5 (the dummy shows the damage numbers), with an invisible barrier column just behind the dummy:
  spells cast at the block the caster looks at (Black Hole, Starfall) then land on the dummy instead of 40 blocks away and under the floor;
- the caster aimed at the dummy's chest (its eye height is odd: aiming at its eyes sends projectiles over it);
- the caster in his school's robes and a staff, with every spell power brought back to its base by one multiply-total modifier per attribute
  (the robes add spell power even with an empty AttributeModifiers tag; without this the damage numbers would be 20-40% too high);
- a camera that is not the player (CMDCam outside mode, driven by /cam-server): side on from 6.5 blocks, field of view 50, a slow dolly over the clip;
- `/cast RenderBot <spell> <max level>`, recorded with ffmpeg x11grab at 30 fps, then H.264 960x540 CRF 24 (about 100 KB a second);
- the poster is the frame that differs most from the first one (the spell at its height).
Length: instant 6 s; long and continuous = cast time + 6 s, at most 11 s. Only the namespaces in --ns are cast (the render client has to have the mod)."""
import os, re, json, time, subprocess, argparse
H = os.path.dirname(os.path.abspath(__file__))
SPELLS = os.path.join(H, '..', 'patches', 'spells.json')
ROBE = {'fire': 'pyromancer', 'ice': 'cryomancer', 'lightning': 'electromancer', 'holy': 'priest', 'blood': 'cultist', 'ender': 'shadowwalker', 'evocation': 'archevoker', 'nature': 'plagued'}
ATTR = ['spell_power', 'cast_time_reduction', 'cooldown_reduction'] + [k + '_spell_power' for k in ('fire', 'ice', 'lightning', 'holy', 'ender', 'blood', 'evocation', 'nature', 'eldritch')]


def gui_open(display):
    """a container screen (the Pocket Dimension spell opens an Ender Chest and it stays) is mostly light grey (198,198,198)"""
    import io
    from PIL import Image
    im = Image.open(io.BytesIO(subprocess.run(['import', '-window', 'root', 'png:-'], env=dict(os.environ, DISPLAY=display), capture_output=True).stdout)).convert('RGB')
    px = [im.getpixel((x, y)) for y in range(0, im.size[1], 4) for x in range(0, im.size[0], 4)]
    return sum(1 for p in px if abs(p[0] - 198) < 8 and abs(p[1] - 198) < 8 and abs(p[2] - 198) < 8) / len(px) > 0.04


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('server'); ap.add_argument('out'); ap.add_argument('--log', required=True); ap.add_argument('--only', default=''); ap.add_argument('--ns', default='irons_spellbooks')
    ap.add_argument('--limit', type=int, default=0); ap.add_argument('--display', default=':99'); ap.add_argument('--at', default=':99+160,90'); ap.add_argument('--size', default='960x540')
    ap.add_argument('--time', default='12300'); ap.add_argument('--z0', type=int, default=1000)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    fifo = os.path.join(a.server, 'cmd.fifo'); raw = os.path.join(a.out, '_raw.mkv')

    def c(s, w=0.35):
        with open(fifo, 'w') as f: f.write(s + '\n')
        time.sleep(w)

    def ask(cmd):
        """a command's answer, read from the server log: the number in its newest 'Value of attribute ... is N' line"""
        n0 = os.path.getsize(a.log); c(cmd, 0.35)
        with open(a.log, encoding='utf-8', errors='replace') as f: f.seek(n0); t = f.read()
        m = re.findall(r'(?:Value|Base value) of attribute .* is (-?[0-9.Ee-]+)', t); return float(m[-1]) if m else None

    def neutral():
        for k, at in enumerate(ATTR):
            uid = '0-0-0-77-%d' % (k + 1); c('attribute RenderBot irons_spellbooks:%s modifier remove %s' % (at, uid), 0.15)
            v, b = ask('attribute RenderBot irons_spellbooks:%s get' % at), ask('attribute RenderBot irons_spellbooks:%s base get' % at)
            if v and b is not None and abs(v - b) > 1e-6: c('attribute RenderBot irons_spellbooks:%s modifier add %s lgw_neutral %.8f multiply' % (at, uid, b / v - 1), 0.15)
        off = [at for at in ATTR if abs((ask('attribute RenderBot irons_spellbooks:%s get' % at) or 0) - 1) > 0.005]
        return off   # attributes still not at 1.0 (their base is 1.0 for a bare player)

    spells = [s for s in json.load(open(SPELLS, encoding='utf-8'))['spells'] if s['enabled'] and s['ns'] in a.ns.split(',')]
    if a.only: spells = [s for s in spells if s['id'] in a.only.split(',')]
    if a.limit: spells = spells[:a.limit]
    for g in ('sendCommandFeedback', 'logAdminCommands', 'mobGriefing', 'doDaylightCycle', 'doWeatherCycle', 'doMobSpawning'): c('gamerule %s false' % g, 0.2)
    c('time set ' + a.time); c('op RenderBot')
    from Xlib import X, XK, display as xd
    from Xlib.ext import xtest
    xdisp = xd.Display(a.display)

    def press(name):   # no pointer move: the game grabs the cursor and a jump would turn the camera
        kc = xdisp.keysym_to_keycode(XK.string_to_keysym(name)); xtest.fake_input(xdisp, X.KeyPress, kc); xdisp.sync(); time.sleep(0.05); xtest.fake_input(xdisp, X.KeyRelease, kc); xdisp.sync()
    import numpy as np
    for i, s in enumerate(spells):
        name = s['id'].replace(':', '__'); dst = os.path.join(a.out, name + '.mp4')
        if os.path.exists(dst): continue
        X0, Z = 4000, a.z0 + 100 * i; g = 3.5; lvl = s.get('maxLevel') or 1; t = (s.get('castTime') or 0) / 20
        dur = 6.0 if s.get('cast') == 'INSTANT' else min(11, t + 6.0)
        c('cam-server stop RenderBot', 0.3); c('effect clear RenderBot', 0.2)
        c('forceload remove all', 0.3); c('forceload add %d %d %d %d' % (X0 - 24, Z - 24, X0 + 24, Z + 24), 1.5); c('tp RenderBot %.1f -60 %d' % (X0 - g, Z), 0.3)
        c('fill %d -61 %d %d -61 %d minecraft:polished_deepslate' % (X0 - 24, Z - 24, X0 + 24, Z + 24), 0.6)
        c('fill %d -60 %d %d -56 %d minecraft:barrier' % (int(X0 + g + 1.5), Z - 1, int(X0 + g + 1.5), Z + 1), 0.3)
        c('kill @e[type=!player]', 0.3); c('summon dummmmmmy:target_dummy %.1f -60 %.1f' % (X0 + g, Z + 0.5), 1.2)
        robe = ROBE.get((s.get('school') or '').split(':')[-1], 'wandering_magician')
        for slot, part in (('head', 'helmet'), ('chest', 'chestplate'), ('legs', 'leggings'), ('feet', 'boots')):
            c('item replace entity RenderBot armor.%s with irons_spellbooks:%s_%s' % (slot, robe, part), 0.15)
        c('item replace entity RenderBot weapon.mainhand with irons_spellbooks:graybeard_staff', 0.15)
        off = neutral()
        c('tp RenderBot %.1f -60 %.1f facing %.1f -58.9 %.1f' % (X0 - g + 0.5, Z + 0.5, X0 + g + 0.5, Z + 0.5), 0.8)
        n = 'clip'; c('cam-server remove ' + n, 0.2); c('cam-server create ' + n, 0.2); c('cam-server get %s mode outside' % n, 0.2)
        cx, cy, cz = X0 + 0.5, -58.6, Z + 7.0   # side on, 6.5 blocks from the line between caster and dummy, looking north (yaw 180), 5 degrees down
        c('cam-server get %s add %.2f %.2f %.2f 180 5 0 50' % (n, cx - 0.4, cy, cz), 0.2); c('cam-server get %s add %.2f %.2f %.2f 180 5 0 50' % (n, cx + 0.4, cy - 0.05, cz - 0.5), 0.2)
        c('cam-server get %s interpolation hermite' % n, 0.2); c('cam-server get %s duration %ds' % (n, int(dur + 3)), 0.2)
        for _ in range(3):
            if not gui_open(a.display): break
            press('Escape'); time.sleep(1.0)
        c('cam-server start %s RenderBot' % n, 1.8)
        rec = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'x11grab', '-framerate', '30', '-video_size', a.size, '-i', a.at, '-t', '%.1f' % dur, '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '14', raw])
        time.sleep(0.6); c('cast RenderBot %s %d' % (s['id'], lvl), 0.1); rec.wait()
        r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-vf', 'fps=30', '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '24', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', dst])
        pix = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', dst, '-vf', 'scale=96:54,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout, np.uint8).reshape(-1, 54, 96).astype(np.int16)
        k = int(np.abs(pix - pix[0]).mean(axis=(1, 2)).argmax()) if len(pix) else 0
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', dst, '-vf', 'select=eq(n\\,%d)' % k, '-frames:v', '1', '-q:v', '3', dst[:-4] + '.jpg'])
        time.sleep(max(0.0, t + 1.5 - dur))   # a /cast while the player is still casting cancels that cast (AbstractSpell.attemptInitiateCast): wait for a long cast to end
        print('%3d/%d %-48s level %d %.1fs %7d B%s%s' % (i + 1, len(spells), s['id'], lvl, dur, os.path.getsize(dst) if os.path.exists(dst) else 0,
              '' if r.returncode == 0 else '  FAILED', ('  spell power not neutral: ' + ','.join(off)) if off else ''), flush=True)
    c('cam-server stop RenderBot')
    if os.path.exists(raw): os.remove(raw)


if __name__ == '__main__': main()
