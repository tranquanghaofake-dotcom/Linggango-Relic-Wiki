#!/usr/bin/env python3
"""Record a short clip of every spell, from the real game, into OUT_DIR/<ns>__<spell>.mp4 plus a poster OUT_DIR/<ns>__<spell>.jpg (resumable: an existing clip is kept).
Usage: python3 -I spell_clips.py SERVER_DIR OUT_DIR --log SERVER_LOG --speed 0.25 [--only ns:spell,...] [--ns irons_spellbooks,...] [--limit N]
Recipe 3 (docs/plans/2026-11-14-mechanics-effects-spells.md, "Clip: the recipe"). Needs, running:
- a Forge 1.20.1 dedicated server in SERVER_DIR, flat world, offline mode, `cmd.fifo` as its stdin (`tail -f cmd.fifo | java ... nogui > SERVER_LOG`),
  the client's mods plus CMDCam 2.2.1 and CreativeCore on both sides;
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
`/cast RenderBot <spell> <max level>`; the 1080p recording is re-timed and scaled to 1280x720 (lanczos: the downscale also smooths the edges) at 60 fps, H.264 CRF 23 (preset medium).
Poster: poster_frame() (the most spell colour while the caster is still in sight), 960x540 WebP.
QC: OUT_DIR/qc.jsonl, one line per clip (new frames a second by new_frames(), bytes, poster frame, robe); --redo-below N records again the clips under N fps; the run stops if the client is gone.
Length in game time: instant 6 s; long and continuous = cast time + 6 s, at most 11 s."""
import os, re, json, time, subprocess, argparse
H = os.path.dirname(os.path.abspath(__file__))
SPELLS = os.path.join(H, '..', 'patches', 'spells.json')
ROBE = {'fire': 'pyromancer', 'ice': 'cryomancer', 'lightning': 'electromancer', 'holy': 'priest', 'blood': 'cultist', 'ender': 'shadowwalker', 'evocation': 'archevoker', 'nature': 'plagued'}
# what the spells are cast at: the Target Dummy (shows damage numbers), or a mob that stands still and does not burn, for spells that need a living target
TARGETS = {'dummy': ('dummmmmmy:target_dummy', ''),
           'husk': ('minecraft:husk', '{NoAI:1b,Silent:1b,PersistenceRequired:1b,Rotation:[90f,0f],Attributes:[{Name:"minecraft:generic.max_health",Base:1000d}],Health:1000f}')}
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
    ap.add_argument('--size', default='1920x1080'); ap.add_argument('--at', default=':99+0,0'); ap.add_argument('--fps', type=int, default=60); ap.add_argument('--time', default='12300'); ap.add_argument('--z0', type=int, default=1000); ap.add_argument('--display', default=':99'); ap.add_argument('--redo-below', type=float, default=0); ap.add_argument('--target', choices=sorted(TARGETS), default='dummy')
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
    c(['gamerule %s false' % g for g in ('sendCommandFeedback', 'logAdminCommands', 'mobGriefing', 'doDaylightCycle', 'doWeatherCycle', 'doMobSpawning')]
      + ['gamerule doImmediateRespawn true', 'gamerule keepInventory true', 'time set ' + a.time, 'op RenderBot'], 4)
    qcp = os.path.join(a.out, 'qc.jsonl'); qc = {}
    if os.path.exists(qcp):
        for line in open(qcp, encoding='utf-8'): r = json.loads(line); qc[r['id']] = r
    for i, s in enumerate(spells):
        name = s['id'].replace(':', '__'); dst = os.path.join(a.out, name + '.mp4')
        if os.path.exists(dst) and not (a.redo_below and qc.get(s['id'], {}).get('fps', 99) < a.redo_below): continue
        if subprocess.run(['pgrep', '-f', 'java -Djava.net.preferIPv6Addresses'], capture_output=True).returncode:   # the client is gone (a spell crashed it): stop, a restart resumes here
            print('client not running: stopped before ' + s['id'], flush=True); raise SystemExit(2)
        X, Z = 4000, a.z0 + 100 * i; g = 3.5; lvl = s.get('maxLevel') or 1; t = (s.get('castTime') or 0) / 20
        dur = 6.0 if s.get('cast') == 'INSTANT' else min(11, t + 6.0)
        c(['cam-server stop RenderBot', 'effect clear RenderBot', 'effect give RenderBot minecraft:instant_health 1 20 true', 'weather clear', 'time set ' + a.time,
           'forceload remove all', 'forceload add %d %d %d %d' % (X - 24, Z - 24, X + 24, Z + 24)], 15)
        c(['tp RenderBot %.1f -60 %d' % (X - g, Z), 'fill %d -61 %d %d -61 %d minecraft:polished_deepslate' % (X - 24, Z - 24, X + 24, Z + 24),
           'fill %d -60 %d %d -56 %d minecraft:barrier' % (int(X + g + 1.5), Z - 1, int(X + g + 1.5), Z + 1), 'kill @e[type=!player]',
           'summon %s %.1f -60 %.1f %s' % (TARGETS[a.target][0], X + g, Z + 0.5, TARGETS[a.target][1])], 10)
        robe = ROBE.get((s.get('school') or '').split(':')[-1], 'wandering_magician')
        c(['item replace entity RenderBot armor.%s with irons_spellbooks:%s_%s' % (slot, robe, part) for slot, part in (('head', 'helmet'), ('chest', 'chestplate'), ('legs', 'leggings'), ('feet', 'boots'))]
          + ['item replace entity RenderBot weapon.mainhand with irons_spellbooks:graybeard_staff'], 4)
        off = neutral(robe)
        cx, cy, cz = X + 0.5, -58.6, Z + 7.0   # side on, 6.5 blocks from the line between caster and dummy, looking north (yaw 180), 5 degrees down
        c(['tp RenderBot %.1f -60 %.1f facing %.1f -58.9 %.1f' % (X - g + 0.5, Z + 0.5, X + g + 0.5, Z + 0.5), 'cam-server remove clip', 'cam-server create clip', 'cam-server get clip mode outside',
           'cam-server get clip add %.2f %.2f %.2f 180 5 0 50' % (cx - 0.4, cy, cz), 'cam-server get clip add %.2f %.2f %.2f 180 5 0 50' % (cx + 0.4, cy - 0.05, cz - 0.5),
           'cam-server get clip interpolation hermite', 'cam-server get clip duration %ds' % int(dur + 3), 'cam-server start clip RenderBot'], 15)
        for _ in range(3):
            if not gui_open(a.display): break
            from Xlib import X as XX, XK, display as xd   # Escape by XTEST, no pointer move (the game grabs the cursor; a jump would turn the camera)
            from Xlib.ext import xtest
            xdp = xd.Display(a.display); kc = xdp.keysym_to_keycode(XK.string_to_keysym('Escape'))
            xtest.fake_input(xdp, XX.KeyPress, kc); xdp.sync(); time.sleep(0.05); xtest.fake_input(xdp, XX.KeyRelease, kc); xdp.sync(); time.sleep(20 * TICK)
        rec = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'x11grab', '-framerate', '%g' % (a.fps * a.speed), '-video_size', a.size, '-i', a.at, '-t', '%.2f' % (dur / a.speed),
                                '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '12', raw])
        time.sleep(12 * TICK); c('cast RenderBot %s %d' % (s['id'], lvl), 0); rec.wait()
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
