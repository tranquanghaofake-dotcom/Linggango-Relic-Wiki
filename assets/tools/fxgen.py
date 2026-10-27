"""Pixel effect generator for the Linggango Relic Wiki asset library (own work, no third-party pixels).
Every effect is drawn on an integer grid with a short colour ramp (dark → light) and hard alpha, light from the top left,
so it sits next to vanilla 16 px textures. Deterministic: same seed, same bytes.
Writes <out>/<theme>/<effect>.png (frames side by side) + <effect>.json (frames, frametime, size, ramp) and a contact sheet.
Usage: python3 -I fxgen.py <out dir>"""
import sys,os,math,json,random
from PIL import Image
H=lambda s:tuple(int(s[i:i+2],16) for i in (1,3,5))
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from palettes import THEMES
def ramp(t): return [H(c) for c in THEMES[t]]
def put(im,x,y,c,a=255):
    if 0<=x<im.width and 0<=y<im.height: im.putpixel((int(x),int(y)),c+(a,))
def lvl(r,v):  # v in 0..1 → ramp colour
    return r[max(0,min(len(r)-1,int(v*len(r)-1e-9)))]
def strip(frames): 
    w,h=frames[0].size; s=Image.new('RGBA',(w*len(frames),h))
    for i,f in enumerate(frames): s.alpha_composite(f,(i*w,0))
    return s
def slash(r,n=8,S=32):
    fr=[]
    for k in range(n):
        im=Image.new('RGBA',(S,S)); t=k/(n-1); head=-110+250*min(1,(t+0.08)**0.6); tail=head-(40+120*min(1,t*1.8))*(1-0.7*max(0,t-0.6)/0.4)
        for y in range(S):
            for x in range(S):
                dx,dy=x-S/2+.5,y-S*0.62+.5; d=math.hypot(dx,dy); ang=math.degrees(math.atan2(dy,dx))+90
                band=S*0.40-S*0.06*t
                if tail<=ang<=head and band-2.2<=d<=band+1.2 and t<1.01:
                    v=(ang-tail)/max(1,head-tail)  # bright at the leading edge
                    v=v*(1-0.55*t)+(0.25 if d>band-.5 else 0)
                    put(im,x,y,lvl(r,v))
        fr.append(im)
    return fr
def circle(r,n=8,S=48,seed=1):
    rnd=random.Random(seed); ticks=[rnd.random()<0.55 for _ in range(32)]; fr=[]
    for k in range(n):
        im=Image.new('RGBA',(S,S)); c=S/2-.5; rot=k/n*(2*math.pi/8)
        for y in range(S):
            for x in range(S):
                d=math.hypot(x-c,y-c); a=math.atan2(y-c,x-c)
                if abs(d-(S/2-2))<.6: put(im,x,y,r[2])
                elif abs(d-(S/2-6))<.6: put(im,x,y,r[1])
                elif S/2-5.5<d<S/2-2.5:
                    i=int(((a+rot)%(2*math.pi))/(2*math.pi)*32)
                    if ticks[i] and int(d)%2==0: put(im,x,y,r[3] if (k+i)%5==0 else r[2])
        R=S/2-8; pts=[(c+R*math.cos(-rot*1.5+i*4*math.pi/5-math.pi/2),c+R*math.sin(-rot*1.5+i*4*math.pi/5-math.pi/2)) for i in range(6)]
        for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
            m=int(max(abs(x1-x0),abs(y1-y0)))+1
            for j in range(m+1): put(im,round(x0+(x1-x0)*j/m),round(y0+(y1-y0)*j/m),r[-1] if j%7==0 else r[2])
        fr.append(im)
    return fr
def shockwave(r,n=6,S=32):
    fr=[]
    for k in range(n):
        im=Image.new('RGBA',(S,S)); t=(k+1)/n; R=2+t*(S/2-3); w=max(1,2.5*(1-t)+.6)
        for y in range(S):
            for x in range(S):
                d=math.hypot(x-S/2+.5,y-S/2+.5)
                if R-w<=d<=R+.5:
                    v=(1-t)*0.9+0.1+(0.2 if (x+y)%2==0 else 0)*(1-t)
                    put(im,x,y,lvl(r,v))
        fr.append(im)
    return fr
def sparkle(r,n=4,S=8):
    fr=[]
    for k,L in enumerate([1,2,3,2][:n]):
        im=Image.new('RGBA',(S,S)); c=S//2-1
        for i in range(-L,L+1): put(im,c+i,c,r[-1] if i==0 else r[2]); put(im,c,c+i,r[-1] if i==0 else r[2])
        if L==3: put(im,c-1,c-1,r[1]); put(im,c+1,c+1,r[1]); put(im,c+1,c-1,r[1]); put(im,c-1,c+1,r[1])
        fr.append(im)
    return fr
def burst(r,n=6,S=16,seed=2):
    rnd=random.Random(seed); rays=[(i*math.pi/4+rnd.uniform(-.2,.2),rnd.uniform(.7,1)) for i in range(8)]; fr=[]
    for k in range(n):
        im=Image.new('RGBA',(S,S)); t=k/(n-1); c=S/2-.5
        for a,l in rays:
            for j in range(S):
                d=j*0.5
                if (2.5+t*4)<=d<=(2+l*(S/2-2)*min(1,0.4+t)) and t<0.98 and k>0:
                    put(im,round(c+math.cos(a)*d),round(c+math.sin(a)*d),lvl(r,1-t*0.8-d/S))
        if t<0.4:
            for dx,dy in ((0,0),(1,0),(0,1),(1,1),(-1,0),(2,0),(0,-1),(0,2),(1,-1),(1,2),(-1,1),(2,1)): put(im,round(c)+dx,round(c)+dy,r[-1] if abs(dx-.5)+abs(dy-.5)<1.5 else r[2])
        fr.append(im)
    return fr
def beam(r,n=4,W=16,Hh=64):
    fr=[]
    for k in range(n):
        im=Image.new('RGBA',(W,Hh)); core=1+(k%2)
        for y in range(Hh):
            wob=round(math.sin((y+k*3)/3.0))
            for x in range(W):
                d=abs(x-(W/2-.5)-wob*0.5)
                if d<=core: put(im,x,y,r[-1])
                elif d<=core+1.5: put(im,x,y,r[2])
                elif d<=core+3 and (x+y+k)%3==0: put(im,x,y,r[1])
        fr.append(im)
    return fr
def orb(r,n=6,S=16):
    fr=[]
    for k in range(n):
        im=Image.new('RGBA',(S,S)); R=4.6+0.8*math.sin(k/n*2*math.pi); c=S/2-.5
        for y in range(S):
            for x in range(S):
                d=math.hypot(x-c,y-c)
                if d<=R:
                    lx,ly=x-(c-R*0.4),y-(c-R*0.4); v=1-math.hypot(lx,ly)/(R*1.6)
                    put(im,x,y,lvl(r,0.2+v*0.8))
                elif d<=R+1.2 and (x+y+k)%2==0: put(im,x,y,r[0],170)
        fr.append(im)
    return fr
def embers(r,n=8,S=16,seed=3):
    rnd=random.Random(seed); ps=[(rnd.randrange(2,S-2),rnd.randrange(S),rnd.choice([1,1,2])) for _ in range(6)]; fr=[]
    for k in range(n):
        im=Image.new('RGBA',(S,S))
        for x,y,sz in ps:
            yy=(y-k*2)%S; v=yy/S
            for dx in range(sz):
                for dy in range(sz): put(im,x+dx+round(math.sin((yy+x)/3)),yy+dy,lvl(r,0.35+0.65*v))
        fr.append(im)
    return fr
def runes(r,count=16,G=(7,9),seed=4):
    rnd=random.Random(seed); out=[]
    for g in range(count):
        im=Image.new('RGBA',G); w,h=G; x,y=rnd.randrange(1,w-1),rnd.randrange(1,h-1)
        for _ in range(rnd.randint(3,5)):  # strokes on the grid, mirrored for half the glyphs
            dx,dy=rnd.choice([(1,0),(0,1),(1,1),(1,-1),(-1,0),(0,-1)]); L=rnd.randint(2,5)
            for _ in range(L):
                put(im,x,y,r[-1]); 
                if g%2==0: put(im,w-1-x,y,r[-1])
                x=max(0,min(w-1,x+dx)); y=max(0,min(h-1,y+dy))
        out.append(im)
    return out
def main(OUT):
    EFFECTS={'slash':(slash,1),'magic_circle':(circle,2),'shockwave':(shockwave,1),'sparkle':(sparkle,3),'burst':(burst,1),'beam':(beam,2),'orb':(orb,2),'embers':(embers,2)}
    rows=[]
    for t in THEMES:
        r=ramp(t); os.makedirs(f'{OUT}/{t}',exist_ok=True)
        for name,(fn,ft) in EFFECTS.items():
            fr=fn(r); s=strip(fr); p=f'{OUT}/{t}/{name}.png'; s.save(p,optimize=True)
            json.dump({'frames':len(fr),'frametime_ticks':ft,'frame_w':fr[0].width,'frame_h':fr[0].height,'ramp':THEMES[t]},open(p[:-4]+'.json','w'))
        g=runes(r); s=strip(g); s.save(f'{OUT}/{t}/runes.png',optimize=True)
        json.dump({'glyphs':len(g),'glyph_w':7,'glyph_h':9,'ramp':THEMES[t]},open(f'{OUT}/{t}/runes.json','w'))
    # contact sheet: each theme a row, first frame of each effect at x2
    cell=100; sheet=Image.new('RGBA',(cell*(len(EFFECTS)+1),cell*len(THEMES)),(28,28,32,255))
    for i,t in enumerate(THEMES):
        for j,name in enumerate(list(EFFECTS)+['runes']):
            s=Image.open(f'{OUT}/{t}/{name}.png'); fw=json.load(open(f'{OUT}/{t}/{name}.json')).get('frame_w',s.width)
            f=s.crop((0,0,fw if name!='runes' else min(s.width,49),s.height)) if name!='slash' else s.crop((fw*3,0,fw*4,s.height))
            if name in('magic_circle',): f=s.crop((0,0,fw,s.height))
            k=max(1,min(int((cell-8)/max(f.size)),4)); f=f.resize((f.width*k,f.height*k),Image.NEAREST)
            sheet.alpha_composite(f,(j*cell+(cell-f.width)//2,i*cell+(cell-f.height)//2))
    sheet.save(f'{OUT}/contact_sheet.png',optimize=True); print('ok',len(THEMES),'themes ×',len(EFFECTS)+1,'effects')
if __name__=='__main__': main(sys.argv[1])
