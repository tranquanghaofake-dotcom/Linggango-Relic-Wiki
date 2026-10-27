"""Remap the obfuscated 1.20.1 server jar to Forge's runtime names (Mojang class names, SRG member names), the
same naming as Forge's server-1.20.1-*-srg.jar. Inputs: obf jar, Mojang server.txt, MCPConfig joined.tsrg."""
import sys, struct, zipfile, re
OBF, MOJ, TSRG, OUT = sys.argv[1:5]
cls = {}
for l in open(MOJ, encoding='utf8'):
    if l and not l[0].isspace() and '->' in l and not l.startswith('#'):
        a, b = l.rstrip(':\n').split(' -> '); cls[b.replace('.', '/')] = a.replace('.', '/')
fld, mth = {}, {}   # obf class -> {name: srg} / {(name, desc): srg}
cur = None
for l in open(TSRG, encoding='utf8'):
    if l.startswith('tsrg2'): continue
    if not l.startswith('\t'): cur = l.split()[0]; continue
    if l.startswith('\t\t'): continue
    p = l.split()
    if len(p) == 3: fld.setdefault(cur, {})[p[0]] = p[1]
    elif len(p) == 4 and p[1].startswith('('): mth.setdefault(cur, {})[(p[0], p[1])] = p[2]
DRX = re.compile(r'L([^;<>]+);')
def mc(n):
    if n.startswith('['): return md(n)
    return cls.get(n, n)
def md(d): return DRX.sub(lambda m: 'L' + cls.get(m.group(1), m.group(1)) + ';', d)
zin = zipfile.ZipFile(OBF)
sup = {}
def hdr(b):
    # returns (cp, offset after cp)
    n = struct.unpack('>H', b[8:10])[0]; i = 10; cp = [None] * n; k = 1
    while k < n:
        t = b[i]
        if t == 1: l = struct.unpack('>H', b[i+1:i+3])[0]; cp[k] = [1, b[i+3:i+3+l].decode('utf8', 'surrogatepass') if True else None]; i += 3 + l
        elif t in (7, 8, 16, 19, 20): cp[k] = [t, struct.unpack('>H', b[i+1:i+3])[0]]; i += 3
        elif t == 15: cp[k] = [t, b[i+1], struct.unpack('>H', b[i+2:i+4])[0]]; i += 4
        elif t in (9, 10, 11, 12, 17, 18): cp[k] = [t] + list(struct.unpack('>HH', b[i+1:i+5])); i += 5
        elif t in (3, 4): cp[k] = [t, b[i+1:i+5]]; i += 5
        elif t in (5, 6): cp[k] = [t, b[i+1:i+9]]; i += 9; k += 1
        else: raise ValueError(t)
        k += 1
    return cp, i
def mutf8(s):
    out = bytearray()
    for ch in s.encode('utf-16-be', 'surrogatepass').decode('utf-16-be', 'surrogatepass'):
        c = ord(ch)
        if c == 0: out += b'\xc0\x80'
        elif c < 0x80: out.append(c)
        elif c < 0x800: out += bytes([0xc0 | c >> 6, 0x80 | c & 63])
        elif c < 0x10000: out += bytes([0xe0 | c >> 12, 0x80 | (c >> 6) & 63, 0x80 | c & 63])
        else:
            c -= 0x10000; hi, lo = 0xd800 | c >> 10, 0xdc00 | c & 1023
            for x in (hi, lo): out += bytes([0xe0 | x >> 12, 0x80 | (x >> 6) & 63, 0x80 | x & 63])
    return bytes(out)
def dmutf8(b):
    # decode modified utf8 loosely
    try: return b.decode('utf8')
    except UnicodeDecodeError: return b.replace(b'\xc0\x80', b'\x00').decode('utf8', 'replace')
classes = {}
for n in zin.namelist():
    if n.endswith('.class'):
        classes[n[:-6]] = zin.read(n)
# hierarchy (obf)
def hdr2(b):
    n = struct.unpack('>H', b[8:10])[0]; i = 10; cp = [None] * n; k = 1
    while k < n:
        t = b[i]
        if t == 1: l = struct.unpack('>H', b[i+1:i+3])[0]; cp[k] = [1, dmutf8(b[i+3:i+3+l])]; i += 3 + l
        elif t in (7, 8, 16, 19, 20): cp[k] = [t, struct.unpack('>H', b[i+1:i+3])[0]]; i += 3
        elif t == 15: cp[k] = [t, b[i+1], struct.unpack('>H', b[i+2:i+4])[0]]; i += 4
        elif t in (9, 10, 11, 12, 17, 18): cp[k] = [t] + list(struct.unpack('>HH', b[i+1:i+5])); i += 5
        elif t in (3, 4): cp[k] = [t, b[i+1:i+5]]; i += 5
        elif t in (5, 6): cp[k] = [t, b[i+1:i+9]]; i += 9; k += 1
        else: raise ValueError(t)
        k += 1
    return cp, i
parsed = {}
for c, b in classes.items():
    cp, i = hdr2(b); acc, th, su = struct.unpack('>HHH', b[i:i+6]); ni = struct.unpack('>H', b[i+6:i+8])[0]
    ifs = [cp[cp[struct.unpack('>H', b[i+8+2*q:i+10+2*q])[0]][1]][1] for q in range(ni)]
    s = cp[cp[su][1]][1] if su else None
    sup[c] = [s] + ifs; parsed[c] = (cp, i)
def find(owner, key, table):
    seen = set(); st = [owner]
    while st:
        c = st.pop(0)
        if c in seen or c is None: continue
        seen.add(c)
        t = table.get(c)
        if t and key in t: return t[key]
        st += sup.get(c, [])
    return None
zout = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
for c, b in classes.items():
    cp, i = parsed[c]
    orig = cp; cp = [list(x) if x else None for x in cp]
    extra = []; base = len(cp)
    def utf(s):
        extra.append([1, s]); return base + len(extra) - 1
    def nat(n, d):
        extra.append([12, utf(n), utf(d)]); return base + len(extra) - 1
    def U(k): return orig[k][1]
    for k, e in enumerate(cp):
        if not e: continue
        if e[0] == 7:
            e[1] = utf(mc(U(e[1])))
        elif e[0] in (9, 10, 11):
            owner = U(orig[e[1]][1]); n0 = orig[e[2]]; name, desc = U(n0[1]), U(n0[2])
            o = owner if not owner.startswith('[') else 'java/lang/Object'
            new = find(o, name, fld) if e[0] == 9 else find(o, (name, desc), mth)
            e[2] = nat(new or name, md(desc))
        elif e[0] == 16:
            e[1] = utf(md(U(e[1])))
        elif e[0] in (17, 18):
            n0 = orig[e[2]]; e[2] = nat(U(n0[1]), md(U(n0[2])))
    # class body
    rest = bytearray(b[i:])
    acc, th, su = struct.unpack('>HHH', rest[:6]); ni = struct.unpack('>H', rest[6:8])[0]; j = 8 + 2 * ni
    out = bytearray(rest[:j])
    for kind in ('f', 'm'):
        cnt = struct.unpack('>H', rest[j:j+2])[0]; out += rest[j:j+2]; j += 2
        for _ in range(cnt):
            ma, mn, mdsc, ac = struct.unpack('>HHHH', rest[j:j+8])
            name, desc = U(mn), U(mdsc)
            if kind == 'f': nn = (fld.get(c) or {}).get(name, name)
            else: nn = (mth.get(c) or {}).get((name, desc)) or find(c, (name, desc), mth) if not name.startswith('<') else name
            nn = nn or name
            out += struct.pack('>HHHH', ma, utf(nn), utf(md(desc)), ac); j += 8
            for _ in range(ac):
                l = struct.unpack('>I', rest[j+2:j+6])[0]; out += rest[j:j+6+l]; j += 6 + l
    out += rest[j:]
    allcp = cp + extra
    pool = bytearray(struct.pack('>H', len(allcp)))
    k = 1
    while k < len(allcp):
        e = allcp[k]
        if e is None: k += 1; continue
        t = e[0]
        if t == 1: s = mutf8(e[1]); pool += struct.pack('>BH', 1, len(s)) + s
        elif t in (7, 8, 16, 19, 20): pool += struct.pack('>BH', t, e[1])
        elif t == 15: pool += struct.pack('>BBH', 15, e[1], e[2])
        elif t in (9, 10, 11, 12, 17, 18): pool += struct.pack('>BHH', t, e[1], e[2])
        elif t in (3, 4, 5, 6): pool += bytes([t]) + e[1]
        k += 1
    assert len(allcp) < 65535, c
    zout.writestr(mc(c) + '.class', bytes(b[:8]) + bytes(pool) + bytes(out))
for n in zin.namelist():
    if not n.endswith('.class') and not n.endswith('/'): zout.writestr(n, zin.read(n))
zout.close(); print('classes', len(classes))
