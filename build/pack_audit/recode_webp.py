#!/usr/bin/env python3
"""Make the WebP pictures inside patch JSON files smaller without changing a single pixel.

    python3 build/pack_audit/recode_webp.py build/patches/boss_figs.json build/patches/boss_walks.json

Every "data:image/webp;base64,..." in the file is decoded and encoded again as lossless WebP at the highest effort
(method 6, exact: colours under transparent pixels kept, the embedded colour profile kept). The new picture replaces the
old one only if it is smaller AND decodes to exactly the same RGBA pixels and carries the same profile; otherwise the
old one stays. The rest of the file is not touched (the replacement is textual), and running it twice changes nothing.
Chromium's own WebP encoder, which boss_portraits.js draws with, uses a low effort: the strips came out 25-40% larger
than they need to be (2.25 MB -> 1.37 MB for boss_figs.json, 2.25 MB -> 1.56 MB for boss_walks.json).
Needs Pillow with WebP support. Used by boss_portraits.js --figs after it writes its files.
"""
import base64, io, re, sys
import numpy as np
from PIL import Image

PAT = re.compile(r'data:image/webp;base64,([A-Za-z0-9+/=]+)')


def recode(raw):
    """The smallest equivalent lossless WebP for `raw`, or None if it is not smaller or not identical."""
    im = Image.open(io.BytesIO(raw)); im.load()
    rgba = im.convert('RGBA'); icc = im.info.get('icc_profile')
    out = io.BytesIO()
    kw = {'icc_profile': icc} if icc else {}
    rgba.save(out, 'WEBP', lossless=True, quality=100, method=6, exact=True, **kw)
    new = out.getvalue()
    if len(new) >= len(raw):
        return None
    back = Image.open(io.BytesIO(new)); back.load()
    if back.size != im.size or not np.array_equal(np.array(rgba), np.array(back.convert('RGBA'))) or back.info.get('icc_profile') != icc:
        return None
    return new


def main(paths):
    total_old = total_new = 0
    for p in paths:
        text = open(p, encoding='utf-8').read()
        cache = {}

        def sub(m):
            b64 = m.group(1)
            if b64 not in cache:
                raw = base64.b64decode(b64)
                new = recode(raw)
                cache[b64] = (base64.b64encode(new).decode() if new else b64, len(raw), len(new) if new else len(raw))
            return 'data:image/webp;base64,' + cache[b64][0]

        out = PAT.sub(sub, text)
        old = sum(v[1] for v in cache.values()); new = sum(v[2] for v in cache.values())
        total_old += old; total_new += new
        if out != text:
            open(p, 'w', encoding='utf-8').write(out)
        print('%s: %d pictures, %.2f MB -> %.2f MB%s' % (p, len(cache), old / 1048576, new / 1048576, '' if out != text else ' (already as small as it gets)'))
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
