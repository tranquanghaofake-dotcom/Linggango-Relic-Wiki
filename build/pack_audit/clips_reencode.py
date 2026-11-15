#!/usr/bin/env python3
"""Re-encode spell clips to the encoding spell_clips.py now writes (H.264 CRF 28, preset slow, tune animation, 1280x720, 60 fps, yuv420p, faststart).
Usage: python3 -I clips_reencode.py SRC_DIR OUT_DIR [--jobs 2]
Every SRC_DIR/*.mp4 whose x264 settings (the encoder's SEI text in the file) are not crf=28.0 is re-encoded into OUT_DIR under the same name; the clips
already at CRF 28 and every poster (.webp) are copied as they are, so OUT_DIR is a complete set. Resumable: a file already in OUT_DIR is kept.
Why CRF 28: 52% of the size of the CRF 23 medium encode with SSIM 0.98 against it on four sample clips (2026-11-15), which keeps all four spell
systems' clips under GitHub Pages' 1 GB."""
import os, re, sys, shutil, subprocess, argparse
from concurrent.futures import ThreadPoolExecutor
ARGS = ['-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '28', '-tune', 'animation', '-pix_fmt', 'yuv420p', '-movflags', '+faststart']


def crf_of(path):
    with open(path, 'rb') as f: head = f.read(1 << 20) + f.read()[-(1 << 20):]   # the SEI is near the start (faststart) or after the mdat
    m = re.search(rb'crf=([0-9.]+)', head); return float(m.group(1)) if m else None


def one(src, out):
    name = os.path.basename(src); dst = os.path.join(out, name)
    if os.path.exists(dst): return name, 'kept'
    if crf_of(src) == 28.0: shutil.copy2(src, dst); return name, 'copied'
    part = dst[:-4] + '.part.mp4'
    r = subprocess.run(['nice', '-n', '10', 'ffmpeg', '-y', '-loglevel', 'error', '-i', src] + ARGS + [part])
    if r.returncode: return name, 'FAILED'
    os.replace(part, dst); return name, 'encoded %d -> %d' % (os.path.getsize(src), os.path.getsize(dst))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('--jobs', type=int, default=2); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for w in sorted(f for f in os.listdir(a.src) if f.endswith('.webp')):
        if not os.path.exists(os.path.join(a.out, w)): shutil.copy2(os.path.join(a.src, w), os.path.join(a.out, w))
    mp4 = sorted(os.path.join(a.src, f) for f in os.listdir(a.src) if f.endswith('.mp4') and not f.endswith('.part.mp4'))
    with ThreadPoolExecutor(a.jobs) as ex:
        for k, (name, what) in enumerate(ex.map(lambda p: one(p, a.out), mp4), 1): print('%4d/%d %s %s' % (k, len(mp4), name, what), flush=True)


if __name__ == '__main__': main()
