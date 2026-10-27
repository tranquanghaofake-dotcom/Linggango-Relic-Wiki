import re
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
        if c=='"':
            i+=1;b=[]
            while s[i]!='"':
                if s[i]=='\\': i+=1
                b.append(s[i]);i+=1
            i+=1;return ''.join(b)
        m=re.compile(r'[^,\s\]\}:]+').match(s,i); t=m.group(0); i=m.end()
        if t in('true','false'): return t=='true'
        mm=re.fullmatch(r'(-?[0-9.]+(?:[eE]-?[0-9]+)?)([bBsSlLfFdD]?)',t)
        if mm: return float(mm.group(1)) if ('.' in mm.group(1) or mm.group(2) in 'fFdD' and mm.group(2)) else int(float(mm.group(1)))
        return t
    def key():
        nonlocal i
        if s[i]=='"': return val()
        m=re.compile(r'[^:\s]+').match(s,i); i=m.end(); return m.group(0)
    return val()
def clean(t):
    t=re.sub(r'<[^>]*>','',t or ''); t=re.sub(r'&[0-9a-fk-or]','',t); return t.replace('‌','').strip()
