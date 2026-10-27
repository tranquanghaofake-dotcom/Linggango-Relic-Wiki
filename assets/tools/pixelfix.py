"""Force an image onto a true pixel grid with a short palette (own implementation; same idea as the MIT tools listed in
assets/TOOLS.md: proper-pixel-art, unfake, spritegrid, pixel-snapper).
1. scale: --size N (target longest side) or auto: the period of the edge energy along rows and columns
   (an upscaled pixel image changes colour only every k pixels).
2. downscale by block: each output pixel takes the dominant opaque colour of its block (not an average: no new in-between colours).
3. alpha: hard (≥ --alpha, default 128 → opaque, else transparent).
4. palette: --ramp theme (from fxgen.THEMES), --palette file.png (its colours), or --colors N (median cut).
   Soft sources (glows, smoke) map brightness onto the ramp, so dark → light follows the ramp order.
5. clean: drop opaque pixels with no opaque neighbour (stray dots).
Usage: python3 -I pixelfix.py in.png out.png [--size N] [--ramp name | --palette p.png | --colors N] [--alpha 128] [--soft]"""
import sys,argparse,collections,math,os
from PIL import Image
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
ap=argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('dst'); ap.add_argument('--size',type=int); ap.add_argument('--ramp')
ap.add_argument('--palette'); ap.add_argument('--colors',type=int,default=0); ap.add_argument('--alpha',type=int,default=128); ap.add_argument('--soft',action='store_true')
a=ap.parse_args(); im=Image.open(a.src).convert('RGBA'); W,H=im.size; px=im.load()
def runs():
    # grid period from edge energy: an upscaled pixel image changes colour only on block borders, so the column (row)
    # edge profile peaks every k pixels. Pick the smallest k whose best phase gathers ≥90% of the best score.
    def lum(c): return 0.3*c[0]+0.59*c[1]+0.11*c[2]+c[3]
    ex=[0.0]*W; ey=[0.0]*H
    for y in range(H):
        for x in range(1,W): ex[x]+=abs(lum(px[x,y])-lum(px[x-1,y]))
    for x in range(W):
        for y in range(1,H): ey[y]+=abs(lum(px[x,y])-lum(px[x,y-1]))
    def smooth(e): return [sum(e[max(0,i-1):i+2]) for i in range(len(e))]   # blur moves an edge by a pixel
    ex,ey=smooth(ex),smooth(ey)
    def score(e,k):
        n=len(e); mean=sum(e)/max(1,n)
        if mean==0 or n<6*k: return 0   # need at least 6 blocks to call it a period
        return max(sum(e[i] for i in range(p,n,k))/len(range(p,n,k)) for p in range(k))/mean
    sc={k:score(ex,k)+score(ey,k) for k in range(2,65)}
    if not sc or max(sc.values())<2.5: return 1   # no grid found
    top=max(sc.values())
    return min(k for k,v in sc.items() if v>=0.9*top)
k=(max(W,H)/a.size) if a.size else runs()
ow,oh=max(1,round(W/k)),max(1,round(H/k)); out=Image.new('RGBA',(ow,oh)); op=out.load()
for oy in range(oh):
    for ox in range(ow):
        x0,x1=int(ox*W/ow),max(int(ox*W/ow)+1,int((ox+1)*W/ow)); y0,y1=int(oy*H/oh),max(int(oy*H/oh)+1,int((oy+1)*H/oh))
        cs=collections.Counter(); al=0; tot=0; lum=0
        for y in range(y0,y1,max(1,(y1-y0)//6)):
            for x in range(x0,x1,max(1,(x1-x0)//6)):
                r,g,b,A=px[x,y]; tot+=1; al+=A
                if A>=a.alpha: cs[(r>>3<<3,g>>3<<3,b>>3<<3)]+=1
                lum+=A*(0.3*r+0.59*g+0.11*b)/255
        if not tot: continue
        if a.soft:
            m=al/tot
            if m>=a.alpha*0.6: v=int(min(255,lum/tot)); op[ox,oy]=(v,v,v,255)
        elif cs and sum(cs.values())*2>=tot*0.5: op[ox,oy]=cs.most_common(1)[0][0]+(255,)
if a.ramp or a.palette or a.colors:
    if a.ramp:
        from palettes import THEMES; pal=[tuple(int(h[i:i+2],16) for i in (1,3,5)) for h in THEMES[a.ramp]]
    elif a.palette: pal=list({c[:3] for c in Image.open(a.palette).convert('RGBA').get_flattened_data() if c[3]>=128})
    else:
        q=out.convert('RGB').quantize(a.colors,method=Image.Quantize.MEDIANCUT); pr=q.getpalette()[:a.colors*3]; pal=[tuple(pr[i:i+3]) for i in range(0,len(pr),3)]
    if a.ramp or a.soft:
        ys=sorted(set(0.3*c[0]+0.59*c[1]+0.11*c[2] for c in (out.get_flattened_data() if hasattr(out,'get_flattened_data') else out.getdata()) if c[3]))
        lo,hi=(ys[0],ys[-1]) if ys else (0,1)
        for y in range(oh):
            for x in range(ow):
                c=op[x,y]
                if c[3]:
                    v=(0.3*c[0]+0.59*c[1]+0.11*c[2]-lo)/max(1,hi-lo); op[x,y]=pal[min(len(pal)-1,int(v*len(pal)))]+(255,)
    else:
        for y in range(oh):
            for x in range(ow):
                c=op[x,y]
                if c[3]: op[x,y]=min(pal,key=lambda p:(p[0]-c[0])**2+(p[1]-c[1])**2+(p[2]-c[2])**2)+(255,)
for y in range(oh):
    for x in range(ow):
        if op[x,y][3] and not any(0<=x+dx<ow and 0<=y+dy<oh and op[x+dx,y+dy][3] for dx,dy in ((1,0),(-1,0),(0,1),(0,-1))): op[x,y]=(0,0,0,0)
out.save(a.dst,optimize=True); print(a.src,'→',a.dst,f'{W}x{H} → {ow}x{oh} (block {k:.2f})')
