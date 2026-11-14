#!/usr/bin/env python3
"""Record a short clip of every spell, from the real game, into OUT_DIR/<ns>__<spell>.mp4 (resumable: an existing clip is kept).
Usage: python3 -I spell_clips.py SERVER_DIR OUT_DIR [--only ns:spell,...] [--limit N] [--display :99]
Needs, running: a Forge 1.20.1 dedicated server in SERVER_DIR with a flat world, offline mode, `cmd.fifo` as its stdin (`tail -f cmd.fifo | java ... nogui`),
the same mods as the client, and a client joined as RenderBot on an Xvfb display, GUI hidden (F1) and the camera over the shoulder (F5 twice from first person, a second apart: first person, front, shoulder),
all drawn by software GL (LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe MESA_GL_VERSION_OVERRIDE=4.6). docs/plans/2026-11-14-mechanics-effects-spells.md has the recipe.
For each spell: a fresh stage 64 blocks along x (changes the last spell made to the ground stay behind), an iron golem (no AI, silent; a living target that targeted spells accept, an armour stand is not) 14 blocks ahead as the target, the camera over the caster's right shoulder (Shoulder Surfing Reloaded 5.3.1: the caster stands left of the frame, the target and the spell show beside him), then
`/cast RenderBot <spell> <max level>` (the player casts, so cast bars, animations and continuous spells run as in play), ffmpeg x11grab records the display,
and the clip is re-encoded to H.264, 480 px wide, 15 fps, no sound. Length: instant 5.5 s; long = cast time + 5.5 s; continuous = its duration + 4.5 s; at most 10 s (the game answers a command a moment late and a projectile needs time to arrive).
Only spells whose mod the render client has are cast (SPELLS: the namespaces in the client's mods folder, MODS_NS)."""
import sys, os, io, json, time, subprocess, shutil, argparse
H = os.path.dirname(os.path.abspath(__file__))
OUTJ = os.path.join(H, '..', 'patches', 'spells.json')


def where(display):
    """(share of dark-purple outfit pixels, their mean x) of a screenshot: none = first person; mean x near the middle = the front or the back view; left of it = over the shoulder"""
    from PIL import Image
    im = Image.open(io.BytesIO(subprocess.run(['import', '-window', 'root', 'png:-'], env=dict(os.environ, DISPLAY=display), capture_output=True).stdout)).convert('RGB'); w, h = im.size
    xs = [x for y in range(h // 3, h, 2) for x in range(0, w, 2) if (lambda p: p[2] > p[1] + 6 and p[0] < 90 and p[2] < 110 and p[0] + p[1] + p[2] < 190)(im.getpixel((x, y)))]
    return len(xs), (sum(xs) / len(xs) / w if xs else None)


def gui_open(display):
    """a container screen (the Ender Chest spell opens one and it stays) is mostly light grey (198,198,198)"""
    from PIL import Image
    im = Image.open(io.BytesIO(subprocess.run(['import', '-window', 'root', 'png:-'], env=dict(os.environ, DISPLAY=display), capture_output=True).stdout)).convert('RGB')
    px = [im.getpixel((x, y)) for y in range(0, im.size[1], 4) for x in range(0, im.size[0], 4)]
    return sum(1 for p in px if abs(p[0] - 198) < 8 and abs(p[1] - 198) < 8 and abs(p[2] - 198) < 8) / len(px) > 0.04


def motion(path):
    """largest mean change of a clip's picture from its first frame (0 to 255): a clip where nothing but noise changes is near 0.1"""
    import numpy as np
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vf', 'scale=96:54,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, 54, 96).astype(np.int16)
    return float(np.abs(a - a[0]).mean(axis=(1, 2)).max()) if len(a) else 0.0


def shoulder(display, cmd, press):
    """press F5 until the caster stands left of the frame (the over-the-shoulder view); the key sometimes goes missing or twice, so look every time"""
    for _ in range(9):
        n, mx = where(display)
        if n > 100 and mx is not None and mx < 0.475: return True
        press('F5'); time.sleep(1.6); cmd('tp RenderBot 64 -60 0 0 3', 1.2)
    return False


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('server'); ap.add_argument('out'); ap.add_argument('--only', default=''); ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--display', default=':99'); ap.add_argument('--min-motion', type=float, default=0.3); ap.add_argument('--ns', default='irons_spellbooks'); ap.add_argument('--size', default='854x480')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    fifo = os.path.join(a.server, 'cmd.fifo'); tmp = os.path.join(a.out, '_tmp.mkv')
    def cmd(c, wait=0.35):
        with open(fifo, 'w') as f: f.write(c + '\n')
        time.sleep(wait)
    spells = [s for s in json.load(open(OUTJ, encoding='utf-8'))['spells'] if s['enabled'] and s['ns'] in a.ns.split(',')]
    if a.only: spells = [s for s in spells if s['id'] in a.only.split(',')]
    if a.limit: spells = spells[:a.limit]
    for g in ('sendCommandFeedback', 'logAdminCommands', 'mobGriefing', 'doDaylightCycle', 'doWeatherCycle'): cmd('gamerule %s false' % g, 0.2)
    cmd('time set 6000'); cmd('op RenderBot')
    from Xlib import X, XK, display as xd
    from Xlib.ext import xtest
    xdisp = xd.Display(a.display)
    def press(name):   # no pointer move: the game grabs the cursor and a jump would turn the camera
        kc = xdisp.keysym_to_keycode(XK.string_to_keysym(name)); xtest.fake_input(xdisp, X.KeyPress, kc); xdisp.sync(); time.sleep(0.05); xtest.fake_input(xdisp, X.KeyRelease, kc); xdisp.sync()
    cmd('tp RenderBot 64 -60 0 0 3', 2.5); cmd('summon minecraft:iron_golem 64 -60 14 {NoAI:1b,Silent:1b,PersistenceRequired:1b}', 1.5)
    if not shoulder(a.display, cmd, press): sys.exit('the camera never reached the over-the-shoulder view (client joined? GUI hidden with F1?)')
    for i, s in enumerate(spells):
        name = s['id'].replace(':', '__'); dst = os.path.join(a.out, name + '.mp4')
        if os.path.exists(dst): continue
        x = 64 * (i + 1); lvl = s.get('maxLevel') or 1; t = (s.get('castTime') or 0) / 20
        dur = 5.5 if s.get('cast') == 'INSTANT' else min(10, t + 5.5) if s.get('cast') == 'LONG' else min(10, t + 4.5)
        cmd('kill @e[type=!player]', 0.2); cmd('effect clear RenderBot', 0.2)
        cmd('tp RenderBot %d -60 0 0 3' % x, 0.2); cmd('summon minecraft:iron_golem %d -60 14 {NoAI:1b,Silent:1b,PersistenceRequired:1b}' % x, 2.5)   # the stage; the client loads its chunks
        for attempt in (1, 2):   # a clip where nothing changes (the cast did not start, a screen covered the game) is recorded once more
            for _ in range(3):
                if not gui_open(a.display): break
                press('Escape'); time.sleep(1.0)
            if not shoulder(a.display, lambda c, w=0.3: cmd(c.replace('tp RenderBot 64 ', 'tp RenderBot %d ' % x), w), press): print('   camera lost', s['id'], flush=True)
            rec = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'x11grab', '-framerate', '20', '-video_size', a.size, '-i', a.display, '-t', '%.1f' % dur, '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '18', tmp])
            time.sleep(0.5); cmd('cast RenderBot %s %d' % (s['id'], lvl), 0.1); rec.wait()
            r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-vf', 'fps=15,scale=480:-2', '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '30', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', dst])
            mo = motion(dst)
            if mo >= a.min_motion or attempt == 2: break
            cmd('kill @e[type=!player]', 0.2); cmd('summon minecraft:iron_golem %d -60 14 {NoAI:1b,Silent:1b,PersistenceRequired:1b}' % x, 1.0)
        print('%3d/%d %-48s level %d %.1fs %6d B motion %.2f%s%s' % (i + 1, len(spells), s['id'], lvl, dur, os.path.getsize(dst) if os.path.exists(dst) else 0, mo, '  LOW' if mo < a.min_motion else '', '' if r.returncode == 0 else '  FAILED'), flush=True)
    if os.path.exists(tmp): os.remove(tmp)


if __name__ == '__main__': main()
