import re
# SNBT as FTB Quests writes it: entries may be split by newlines instead of commas, keys may be bare. The number and quoted-string
# patterns are adapted from nbtlib (nbtlib/literal/parser.py, MIT licence, Copyright (c) 2019 Valentin Berlier): signed mantissa,
# optional signed exponent, type suffix; strings in either quote.
NUM = re.compile(r"([+-]?(?:[0-9]*\.[0-9]+|[0-9]+\.[0-9]*|[0-9]+)(?:[eE][+-]?[0-9]+)?)([bslfdBSLFD]?)(?![a-zA-Z0-9._+-])")
QUOTED = re.compile(r'"(?:\\.|[^\\"])*"|\'(?:\\.|[^\\\'])*\'', re.S)
ESC = {'n': '\n', 't': '\t', 'r': '\r', 'b': '\b', 'f': '\f', 's': ' '}
def unquote(q):
    return re.sub(r'\\(u[0-9a-fA-F]{4}|.)', lambda m: chr(int(m.group(1)[1:], 16)) if len(m.group(1)) == 5 else ESC.get(m.group(1), m.group(1)), q[1:-1], flags=re.S)
def number(t):
    """a bare token as a number (int for b/s/l or no suffix without a point or exponent, else float), or None"""
    m = NUM.fullmatch(t)
    if not m: return None
    v, suf = m.groups(); suf = suf.lower()
    if suf in ('f', 'd') or (not suf and re.search(r'[.eE]', v)): return float(v)
    return int(v) if re.fullmatch(r'[+-]?[0-9]+', v) else int(float(v))
def parse(s):
    i=0;n=len(s)
    def ws():
        nonlocal i
        while i<n and (s[i] in ' \t\r\n,'): i+=1
    def val():
        nonlocal i
        ws(); c=s[i]
        if c=='{':
            i+=1;d={}
            while True:
                ws()
                if s[i]=='}': i+=1;return d
                k=key(); ws(); assert s[i]==':',(i,s[i-20:i+20]); i+=1; d[k]=val()
        if c=='[':
            i+=1;l=[]
            ws()
            if re.match(r'[BIL];',s[i:i+2]): i+=2
            while True:
                ws()
                if s[i]==']': i+=1;return l
                l.append(val())
        if c in '"\'':
            m=QUOTED.match(s,i); assert m,(i,s[i:i+40]); i=m.end(); return unquote(m.group(0))
        m=re.compile(r'[^,\s\]\}:]+').match(s,i); t=m.group(0); i=m.end()
        if t in('true','false'): return t=='true'
        v=number(t)
        return t if v is None else v
    def key():
        nonlocal i
        if s[i] in '"\'': return val()
        m=re.compile(r'[^:\s]+').match(s,i); i=m.end(); return m.group(0)
    return val()
def clean(t):
    t=re.sub(r'<[^>]*>','',t or ''); t=re.sub(r'&[0-9a-fk-or]','',t); return t.replace('‌','').strip()
