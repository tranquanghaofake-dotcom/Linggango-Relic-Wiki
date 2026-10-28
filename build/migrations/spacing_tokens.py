"""One-off migration: every margin / padding / gap length in the stylesheets onto the spacing scale.
Scale (px): 4 8 12 16 24 32 48 64 as var(--s1)..var(--s8); 0, 1 and 2 px stay literal (hairline nudges);
negative values (border overlaps), em, %, calc() and env() are left alone; values above 64 px are layout sizes, left alone.
A value between two steps goes to the nearer one; an exact tie goes up (more room, never less)."""
import re, sys, collections
SC = [0, 2, 4, 8, 12, 16, 24, 32, 48, 64]; TOK = {4: 1, 8: 2, 12: 3, 16: 4, 24: 5, 32: 6, 48: 7, 64: 8}
def snap(v):
    if v <= 1 or v > 64: return None
    best = min(SC, key=lambda s: (abs(s - v), -s))
    return best
stats = collections.Counter()
def fix_val(val):
    if re.search(r'calc\(|env\(|var\(', val): return val
    def rep(m):
        neg, num = m.group(1), float(m.group(2))
        if neg: return m.group(0)
        s = snap(num)
        if s is None: return m.group(0)
        stats[(num, s)] += 1
        return '2px' if s == 2 else ('0' if s == 0 else f'var(--s{TOK[s]})')
    return re.sub(r'(?<![\w.-])(-)?(\d*\.?\d+)px\b', rep, val)
PROP = re.compile(r'(?<![\w-])((?:margin|padding)(?:-(?:top|bottom|left|right|inline|block)(?:-(?:start|end))?)?|gap|row-gap|column-gap|grid-gap)(\s*:\s*)([^;}]*)')
for f in sys.argv[1:]:
    s = open(f, encoding='utf-8').read()
    n = PROP.sub(lambda m: m.group(1) + m.group(2) + fix_val(m.group(3)), s)
    open(f, 'w', encoding='utf-8').write(n)
for (a, b), n in sorted(stats.items()): print(f'{a:g}px -> {b}px  x{n}')
