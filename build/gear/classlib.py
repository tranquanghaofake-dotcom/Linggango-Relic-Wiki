"""The one class layer: how every bytecode tool here finds, parses and reads mod classes (jawa underneath).
ClassPath(jars): an index of every class in the jars, the first jar holding a class wins; jars are taken sorted (sort=False keeps
the order given, for callers that put a namespace's own jars first). It parses each class once (cf), walks superclasses and
interfaces, finds a method the way invokevirtual does (find_method), reads META-INF/services and mods.toml.
Module functions read one parsed class: desc() (a method descriptor's arguments, local slots, return type), const() (a constant
with its type), ref() (a field or method reference), code() (a method's instructions, decoded once), bootstrap() (an
invokedynamic's bootstrap method and arguments) and constant-pool scans (strings, class_refs, field_refs, method_refs).
Used by mjvm.py (gear scan, side-boss producers, tints) and pack_audit/iss_armor.py; build/tests/bytecode/run.py tests it."""
import io, os, zipfile, tomllib
from jawa.cf import ClassFile
import jawa.constants as C

# ---------------------------------------------------------------- descriptors
class Desc:
    """a method descriptor: args (each argument's type descriptor), kinds (one letter per argument: objects and arrays 'A'),
    slots (local variable slots the arguments take: long and double take two), ret (the return type descriptor)"""
    __slots__ = ('args', 'kinds', 'slots', 'ret')
    def __repr__(s): return 'Desc(%s)%s' % (','.join(s.args), s.ret)

_DESC = {}
def desc(d):
    r = _DESC.get(d)
    if r is None:
        a = d[1:d.index(')')]; args = []; i = 0
        while i < len(a):
            j = i
            while a[i] == '[': i += 1
            if a[i] == 'L': i = a.index(';', i)
            i += 1; args.append(a[j:i])
        r = Desc(); r.args = args; r.ret = d[d.index(')') + 1:]
        r.kinds = ''.join('A' if t[0] in '[L' else t for t in args)
        r.slots = sum(2 if t in 'JD' else 1 for t in r.kinds)
        _DESC[d] = r
    return r
def argc(d): return len(desc(d).args)
def dtypes(d): return desc(d).kinds
def rettype(d): return d[d.index(')') + 1:]

# ---------------------------------------------------------------- constants
class ClassRef:
    __slots__ = ('name',)
    def __init__(s, name): s.name = name
    def __repr__(s): return 'Class(%s)' % s.name

class Handle:
    """a CONSTANT_MethodHandle: kind (1-9, JVMS 4.4.8; 6 invokestatic, 8 newInvokeSpecial) and the member it points at"""
    __slots__ = ('kind', 'owner', 'name', 'desc')
    def __init__(s, kind, owner, name, desc): s.kind, s.owner, s.name, s.desc = kind, owner, name, desc
    def __repr__(s): return 'Handle(%d %s.%s%s)' % (s.kind, s.owner, s.name, s.desc)

class MethodType:
    __slots__ = ('desc',)
    def __init__(s, desc): s.desc = desc
    def __repr__(s): return 'MethodType(%s)' % s.desc

def const(k, ix):
    """(type, value) of a loadable constant: 'I' and 'J' ints, 'F' and 'D' floats (a float is exactly its 32-bit value),
    'S' a str, 'C' a ClassRef, 'H' a Handle, 'T' a MethodType; (None, the raw jawa constant) for anything else"""
    c = k.constants.get(ix)
    if isinstance(c, C.Integer): return 'I', c.value
    if isinstance(c, C.Float): return 'F', c.value
    if isinstance(c, C.Long): return 'J', c.value
    if isinstance(c, C.Double): return 'D', c.value
    if isinstance(c, C.String): return 'S', c.string.value
    if isinstance(c, C.ConstantClass): return 'C', ClassRef(c.name.value)
    if isinstance(c, C.MethodHandle):
        r = c.reference; return 'H', Handle(c.reference_kind, r.class_.name.value, r.name_and_type.name.value, r.name_and_type.descriptor.value)
    if isinstance(c, C.MethodType): return 'T', MethodType(c.descriptor.value)
    return None, c

def ref(k, ix):
    """(owner, name, descriptor) of a field, method or interface-method reference; cached per class"""
    t = k.__dict__.setdefault('_cl_ref', {})
    r = t.get(ix)
    if r is None:
        c = k.constants.get(ix); nt = c.name_and_type
        r = t[ix] = (c.class_.name.value, nt.name.value, nt.descriptor.value)
    return r

def class_name(k, ix): return k.constants.get(ix).name.value

def code(k, m):
    """(instructions, {byte offset: instruction index}) of method m, decoded once per class file"""
    t = k.__dict__.setdefault('_cl_code', {})
    key = id(m)
    if key not in t:
        ins = list(m.code.disassemble()); t[key] = (ins, {x.pos: i for i, x in enumerate(ins)})
    return t[key]

def bootstrap(k, ix):
    """the invokedynamic constant at ix: (name, descriptor, bootstrap Handle, [(type, value) of each static argument])"""
    idy = k.constants.get(ix); nt = idy.name_and_type
    b = k.bootstrap_methods[idy.method_attr_index]
    return nt.name.value, nt.descriptor.value, const(k, b.method_ref)[1], [const(k, q) for q in b.bootstrap_args]

def strings(k): return [c.string.value for c in k.constants if isinstance(c, C.String)]
def class_refs(k): return [c.name.value for c in k.constants if isinstance(c, C.ConstantClass)]
def field_refs(k): return [ref(k, c.index) for c in k.constants if isinstance(c, C.FieldReference)]
def method_refs(k): return [ref(k, c.index) for c in k.constants if isinstance(c, (C.MethodReference, C.InterfaceMethodRef))]

def method(k, name, desc=None):
    for m in k.methods:
        if m.name.value == name and (desc is None or m.descriptor.value == desc): return m
    return None

def is_static(m): return bool(m.access_flags.get('acc_static'))

# ---------------------------------------------------------------- jars
def mods_toml(z):
    """META-INF/mods.toml of a jar (a path or an open ZipFile) as a dict; {} when it has none or it does not parse"""
    try:
        if not isinstance(z, zipfile.ZipFile): z = zipfile.ZipFile(z)
        return tomllib.loads(z.read('META-INF/mods.toml').decode('utf8', 'ignore'))
    except Exception: return {}
def mod_ids(z):
    """the mod ids a jar's mods.toml declares"""
    try: return {m.get('modId') for m in mods_toml(z).get('mods', [])}
    except Exception: return set()

class ClassPath:
    def __init__(s, jars=(), sort=True):
        s.zips = []  # (path, ZipFile) in class path order; jars that do not open are left out
        s.idx = {}   # internal class name -> (ZipFile, entry name)
        for j in (sorted(jars) if sort else jars):
            try: z = zipfile.ZipFile(j)
            except Exception: continue
            s.zips.append((j, z))
            for n in z.namelist():
                if n.endswith('.class') and not n.startswith('META-INF'): s.idx.setdefault(n[:-6], (z, n))
        s.cache = {}; s._svc = {}

    def over(s, zips):
        """a copy whose classes from zips (open ZipFiles) replace the ones indexed, the later zip winning (a namespace's own jars
        over the whole pack); it parses classes again (its own cache)"""
        r = ClassPath.__new__(ClassPath)
        r.idx = dict(s.idx); r.cache = {}; r._svc = {}
        for z in zips:
            for n in z.namelist():
                if n.endswith('.class') and not n.startswith('META-INF'): r.idx[n[:-6]] = (z, n)
        mine = {id(z) for z in zips}
        r.zips = [(z.filename, z) for z in zips] + [e for e in s.zips if id(e[1]) not in mine]
        return r

    def __contains__(s, cls): return cls in s.idx
    def jar(s, cls):
        e = s.idx.get(cls); return e[0].filename if e else None
    def bytes(s, cls):
        e = s.idx.get(cls); return e[0].read(e[1]) if e else None

    def cf(s, cls):
        """the parsed class (jawa ClassFile), or None when no jar has it or it does not parse"""
        if cls in s.cache: return s.cache[cls]
        e = s.idx.get(cls); r = None
        if e:
            try: r = ClassFile(io.BytesIO(e[0].read(e[1])))
            except Exception: r = None
        s.cache[cls] = r; return r

    def supers(s, cls, limit=20):
        """cls and its superclasses, nearest first, as far as the class path has them (the last may be missing)"""
        out = []
        while cls and len(out) < limit:
            out.append(cls); c = s.cf(cls)
            if not c or not c.super_: break
            cls = c.super_.name.value
        return out

    def interfaces(s, cls, limit=64):
        """every interface cls and its superclasses implement, breadth first (direct ones first)"""
        todo = []; seen = []
        for c in s.supers(cls):
            k = s.cf(c)
            if k: todo += [i.name.value for i in k.interfaces]
        while todo and len(seen) < limit:
            c = todo.pop(0)
            if c in seen: continue
            seen.append(c); k = s.cf(c)
            if k: todo += [i.name.value for i in k.interfaces]
        return seen

    def find_method(s, cls, name, desc=None):
        """(declaring class, ClassFile, method) the way invokevirtual resolves it: the class and its superclasses, then the
        default methods (with code) of the interfaces, breadth first; None when nothing matches"""
        chain = s.supers(cls)
        for c in chain:
            k = s.cf(c)
            if not k: continue
            m = method(k, name, desc)
            if m: return c, k, m
        for c in s.interfaces(cls):
            k = s.cf(c)
            if not k: continue
            for m in k.methods:
                if m.name.value == name and (desc is None or m.descriptor.value == desc) and m.code: return c, k, m
        return None

    def services(s, iface):
        """implementations META-INF/services lists for iface (internal name), in class path order"""
        if iface in s._svc: return s._svc[iface]
        r = []
        for _, z in s.zips:
            try: t = z.read('META-INF/services/' + iface.replace('/', '.')).decode('utf8', 'ignore')
            except Exception: continue
            for line in t.splitlines():
                line = line.split('#')[0].strip()
                if line: r.append(line.replace('.', '/'))
        s._svc[iface] = r; return r
