#!/usr/bin/env python3
"""The 1.20.1 server jar the wide scan reads (Mojang class names, SRG member names), built without running Forge's
installer: Mojang's own server jar remapped with Mojang's server.txt (class names) and MCPConfig's joined.tsrg (field
and method names), the two mappings the installer combines.
Usage: srgjar.py SERVER_JAR server.txt joined.tsrg G
  SERVER_JAR  the 1.20.1 server jar from Mojang's version manifest (a bundler: the real jar is under META-INF/versions)
  writes G/srv/libraries/net/minecraft/server/1.20.1-20230612.114412/server-1.20.1-20230612.114412-srg.jar
What it rewrites, in each class file: Class entries (and the class names inside every field and method descriptor,
NameAndType and MethodType), the names of declared fields and methods, and the member name of every Fieldref / Methodref
/ InterfaceMethodref, looked up on its owner and then up the owner's superclasses and interfaces (a call names the class
it is made on, not the one that declares the member). New strings and NameAndType entries are appended to the constant
pool, so no existing index moves. Generic signatures, local variable names and other attributes keep their obfuscated
text: the scan reads descriptors only. Mojang's mappings may not be redistributed whole; the jar stays in the work dir."""
import io, re, struct, sys, zipfile, os

def load_mojang(path):
    cls = {}
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or line.startswith(" "): continue
        m = re.match(r"(\S+) -> (\S+):", line)
        if m: cls[m.group(2).replace(".", "/")] = m.group(1).replace(".", "/")   # a few obfuscated names keep their package
    return cls

def load_tsrg(path):
    fields, methods, cur = {}, {}, None
    for line in open(path, encoding="utf-8"):
        if line.startswith("tsrg2") or line.startswith("\t\t"): continue
        if not line.startswith("\t"): cur = line.split()[0]; continue
        p = line.split()
        if len(p) == 3: fields.setdefault(cur, {})[p[0]] = p[1]
        elif len(p) == 4: methods.setdefault(cur, {})[(p[0], p[1])] = p[2]
    return fields, methods

DESC = re.compile(r"L([^;<]+);")

class CF:
    """the parts of a class file this needs, with the byte offsets to patch"""
    def __init__(s, b):
        s.b = bytearray(b); i = 10; n = struct.unpack(">H", b[8:10])[0]; s.cp = [None] * n; k = 1
        while k < n:
            t = b[i]
            if t == 1: l = struct.unpack(">H", b[i + 1:i + 3])[0]; s.cp[k] = (1, b[i + 3:i + 3 + l].replace(b"\xc0\x80", b"\x00").decode("utf-8", "surrogatepass"), i); i += 3 + l   # Java's modified UTF-8
            elif t in (7, 8, 16, 19, 20): s.cp[k] = (t, struct.unpack(">H", b[i + 1:i + 3])[0], i); i += 3
            elif t in (3, 4): s.cp[k] = (t, None, i); i += 5
            elif t in (5, 6): s.cp[k] = (t, None, i); i += 9; k += 1
            elif t in (9, 10, 11, 12, 17, 18): s.cp[k] = (t, struct.unpack(">HH", b[i + 1:i + 5]), i); i += 5
            elif t == 15: s.cp[k] = (t, struct.unpack(">BH", b[i + 1:i + 4]), i); i += 4
            else: raise ValueError("constant tag %d" % t)
            k += 1
        s.end = i
        s.this, s.super = struct.unpack(">HH", b[i + 2:i + 6]); i += 6
        ni = struct.unpack(">H", b[i:i + 2])[0]; s.ifaces = [struct.unpack(">H", b[i + 2 + 2 * j:i + 4 + 2 * j])[0] for j in range(ni)]; i += 2 + 2 * ni
        s.members = []   # (kind, offset of name_index, name_index, descriptor_index)
        for kind in ("f", "m"):
            cnt = struct.unpack(">H", b[i:i + 2])[0]; i += 2
            for _ in range(cnt):
                ni_, di = struct.unpack(">HH", b[i + 2:i + 6]); s.members.append((kind, i + 2, ni_, di)); i += 6
                ac = struct.unpack(">H", b[i:i + 2])[0]; i += 2
                for _ in range(ac): i += 6 + struct.unpack(">I", b[i + 2:i + 6])[0]
    def utf(s, k): return s.cp[k][1]
    def cname(s, k): return s.utf(s.cp[k][1]) if k else None

def main(server, mtxt, tsrg, G):
    z = zipfile.ZipFile(server)
    inner = [n for n in z.namelist() if re.match(r"META-INF/versions/[^/]+/server-[^/]+\.jar$", n)]
    if inner: z = zipfile.ZipFile(io.BytesIO(z.read(inner[0])))
    cmap = load_mojang(mtxt); fmap, mmap = load_tsrg(tsrg)
    files = {n: z.read(n) for n in z.namelist() if n.endswith(".class")}
    parsed = {n[:-6]: CF(b) for n, b in files.items()}
    sup = {c: [cf.cname(cf.super)] + [cf.cname(x) for x in cf.ifaces] for c, cf in parsed.items()}
    cls = lambda n: cmap.get(n, n)
    desc = lambda d: DESC.sub(lambda m: "L" + cls(m.group(1)) + ";", d)
    def member(owner, name, d, kind, seen=None):
        """the SRG name of owner.name(d), looked up the hierarchy (obfuscated names)"""
        seen = seen or set()
        if owner in seen or owner is None: return None
        seen.add(owner)
        hit = fmap.get(owner, {}).get(name) if kind == "f" else mmap.get(owner, {}).get((name, d))
        if hit: return hit
        for p in sup.get(owner, []):
            h = member(p, name, d, kind, seen)
            if h: return h
        return None
    out_path = os.path.join(G, "srv/libraries/net/minecraft/server/1.20.1-20230612.114412/server-1.20.1-20230612.114412-srg.jar")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    zo = zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED)
    stats = {"classes": 0, "members": 0, "refs": 0}
    for c, cf in parsed.items():
        b, extra = cf.b, []
        count = len(cf.cp)
        def new_utf(text):
            nonlocal count
            raw = text.encode("utf-8", "surrogatepass"); extra.append(b"\x01" + struct.pack(">H", len(raw)) + raw); count += 1; return count - 1
        def new_nat(n, d):
            nonlocal count
            extra.append(b"\x0c" + struct.pack(">HH", n, d)); count += 1; return count - 1
        put = lambda off, v: b.__setitem__(slice(off, off + 2), struct.pack(">H", v))
        for k, e in enumerate(cf.cp):
            if not e: continue
            t, v, off = e
            if t == 7:   # class names, arrays included
                nm = cf.utf(v); nn = desc(nm) if nm.startswith("[") else cls(nm)
                if nn != nm: put(off + 1, new_utf(nn))
            elif t == 16:
                d = cf.utf(v); nd = desc(d)
                if nd != d: put(off + 1, new_utf(nd))
            elif t in (9, 10, 11):   # a member reference: its own NameAndType, renamed on the owner's hierarchy
                ci, nat = v; owner = cf.cname(ci); ni, di = cf.cp[nat][1]; name, d = cf.utf(ni), cf.utf(di)
                srg = member(owner, name, d, "f" if t == 9 else "m") if not owner.startswith("[") else None
                nd = desc(d)
                if srg or nd != d:
                    put(off + 3, new_nat(new_utf(srg) if srg else ni, new_utf(nd) if nd != d else di)); stats["refs"] += 1
            elif t in (12,):   # NameAndTypes used by invokedynamic keep their names; descriptors are remapped
                ni, di = v; d = cf.utf(di); nd = desc(d)
                if nd != d: put(off + 3, new_utf(nd))
        for kind, off, ni, di in cf.members:
            name, d = cf.utf(ni), cf.utf(di)
            srg = (fmap.get(c, {}).get(name) if kind == "f" else mmap.get(c, {}).get((name, d)))
            if srg: put(off, new_utf(srg)); stats["members"] += 1
            nd = desc(d)
            if nd != d: put(off + 2, new_utf(nd))
        b[8:10] = struct.pack(">H", count)
        data = bytes(b[:cf.end]) + b"".join(extra) + bytes(b[cf.end:])
        zo.writestr(cls(c) + ".class", data); stats["classes"] += 1
    zo.close()
    print(out_path, stats)

if __name__ == "__main__":
    if len(sys.argv) != 5: sys.exit(__doc__)
    main(*sys.argv[1:])
