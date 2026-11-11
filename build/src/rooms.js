/* ---------- rooms: the interior at the top of each main page ----------
   A room is a cross-section of a Minecraft build, six blocks tall (beam, four blocks of wall, floor), as wide as the
   page. Its blocks are drawn into one canvas at 16 px per block and shown at x3 (one block = 48 px), lit the way the game
   lights a room: a room has its own light level and each lamp raises the level around it by one per block less, the
   dark stepped per texel. Few lamps, few props: the title on the left, one scene in the middle that says what the page is
   (library and enchanting table, forge and lava fall, crypt and spawner, armour stands, ritual altar, ME storage, beacon),
   plain wall with pillars around it. Lava, fire, the AE2 lights and the particles move as in game (the blocks' own frame
   strips at the game's frame times); everything moving stops under reduced motion.
     room(kind, items, o)  items: the page's own things ({t: index in D} for curios); a scene may show a few of them
                           o {head: html for the title}
   Textures: ROOMT (scenes.js, uiicons.js: rm_* blocks, ri_* items, rg_* Goety's crypt). Painted when the room is in the
   page, and again when its width changes. */
const RB=48,RR=6;
function room(kind,items,o={}){const ids=(items||[]).map(x=>x&&x.t!=null&&typeof D!=="undefined"&&D[+x.t]&&D[+x.t].id).filter(Boolean).slice(0,6);
 return `<div class="room3${o.head?" rhd":""}" data-room="${kind}" data-ids="${esc(ids.join(" "))}">
<canvas class="rcv" aria-hidden="true"></canvas><div class="rfx" aria-hidden="true"></div>${o.head?`<div class="rhead">${o.head}</div>`:""}</div>`}
const RIMG={};
const rImg=k=>{if(RIMG[k])return RIMG[k];const b=typeof ROOMT!=="undefined"&&ROOMT[k];const im=new Image();RIMG[k]=im;
 im.ready=b?new Promise(r=>{im.onload=im.onerror=()=>r(im)}):Promise.resolve(im);if(b)im.src="data:image/png;base64,"+b;return im};
const rIcon=k=>{const s=typeof IC!=="undefined"&&IC[k];if(!s)return null;if(RIMG["ic:"+k])return RIMG["ic:"+k];const im=new Image();RIMG["ic:"+k]=im;
 im.ready=new Promise(r=>{im.onload=im.onerror=()=>r(im)});im.src=typeof icu==="function"?icu(k):"data:image/png;base64,"+s;return im};
const rt=k=>typeof ROOMT!=="undefined"&&ROOMT[k]?k:null;
/* the scenes. g: C cols, T first col right of the title, cx the scene's centre, R(n) a seeded random;
   wall(f, per, off)/beam/floor fill (per, off: a pillar every per columns, the first off columns right of the title: the
   page's wall below goes on in that rhythm), put(x, y, texture) a block or item on the canvas, anim a frame strip, lamp a
   light, pt particles */
const ROOMK={
 library:g=>{g.amb=10;
  g.wall((x,y)=>x>=g.T&&(x-g.T)%8===4?"rm_stripped_oak_log":"rm_oak_planks",8,4);g.beam("rm_dark_oak_log");g.floor("rm_spruce_planks");
  const c=g.cx,sh=["rm_bookshelf","rm_bookshelf","rm_chiseled_bookshelf_occupied"];
  for(let x=c-4;x<=c+4;x++)if(x>=g.T)g.put(x,1,sh[g.R(3)]);
  [[-2,3],[-2,4],[2,3],[2,4]].forEach(([dx,y])=>g.put(c+dx,y,sh[g.R(3)]));
  g.put(c,4,"rm_enchanting_table_side");g.anim(c,3,"ri_enchanted_book",1,0,{cls:"bob"});g.lamp(c,3,9,[150,110,255]);
  [[-2,3],[2,3],[-2,4],[2,4]].forEach(([dx,y],i)=>g.pt(c+dx,y,"glyph",{to:[c,3],k:i}));
  g.hang(c-6,"ri_lantern",2);g.lamp(c-6,2,8,[255,180,100]);g.hang(c+6,"ri_lantern",2);g.lamp(c+6,2,8,[255,180,100])},
 forge:g=>{g.amb=9;
  g.wall((x,y)=>x>=g.T&&(x-g.T)%9===4?"rm_polished_deepslate":g.R(6)?"rm_stone_bricks":"rm_cracked_stone_bricks",9,4);g.beam("rm_deepslate_tiles");g.floor("rm_polished_blackstone");
  const c=g.cx;
  for(let y=1;y<=4;y++){g.anim(c,y,"rm_lava_still",20,2000,{alt:1});g.anim(c+1,y,"rm_lava_still",20,2000,{alt:1,delay:-700})}
  for(let y=1;y<=3;y++){g.over(c,y,"rm_iron_bars");g.over(c+1,y,"rm_iron_bars")}
  g.lamp(c,3,10,[255,120,30]);g.lamp(c+1,3,10,[255,120,30]);g.pt(c+1,4,"lava",{dx:.3});
  g.anim(c-2,4,"rm_blast_furnace_front_on",2,1000,{alt:1});g.put(c+3,4,"rm_cauldron_side");g.pt(c+3,3,"spark",{dy:.8});g.put(c+4,4,"rm_smithing_table_front");
  g.put(c-3,2,"ri_iron_sword");g.put(c+4,2,"ri_netherite_sword")},
 crypt:g=>{g.amb=10;const br=rt("rg_crypt_bricks")||"rm_polished_blackstone_bricks",pl=rt("rg_crypt_plinth")||"rm_chiseled_polished_blackstone";
  g.wall((x,y)=>x>=g.T&&(x-g.T)%8===4?(rt("rg_crypt_pillar")||"rm_polished_basalt_side"):br,8,4);g.beam("rm_polished_blackstone");g.floor(rt("rg_crypt_tiles")||"rm_polished_blackstone");
  const c=g.cx;g.put(c,4,"mf_skeleton",{s:.5});g.put(c,4,"rm_spawner");g.pt(c,4,"flame",{dy:.4});
  [-3,3].forEach(dx=>{g.put(c+dx,4,"rm_soul_soil");g.anim(c+dx,3,rt("rg_brazier_soul")||"rm_soul_fire_0",rt("rg_brazier_soul")?4:32,rt("rg_brazier_soul")?600:1600,{});g.lamp(c+dx,3,8,[90,200,255]);g.pt(c+dx,3,"soul",{k:dx>0?1:0})});
  [-5,5].forEach(dx=>{g.put(c+dx,4,pl);g.put(c+dx,3,"ri_skeleton_skull",{dy:4})})},
 armory:g=>{g.amb=10;
  g.wall((x,y)=>x>=g.T&&(x-g.T)%7===3?"rm_stripped_spruce_log":"rm_spruce_planks",7,3);g.beam("rm_dark_oak_log");g.floor("rm_dark_oak_planks");
  const c=g.cx;["iron","diamond","netherite"].forEach((m,i)=>g.stand(c+(i-1)*3,m));
  g.put(c-5,4,"rm_crafting_table_front");g.put(c+5,4,"rm_barrel_side");g.put(c+5,3,"ri_lantern",{dy:5});g.lamp(c+5,3,8,[255,180,100])},
 ritual:g=>{g.amb=8;const pl=rt("goety_haunted_planks")||"rm_dark_oak_planks",lg=rt("goety_stripped_haunted_log")||"rm_stripped_dark_oak_log",pd=rt("rg_crypt_plinth")||"rm_chiseled_polished_blackstone";
  g.wall((x,y)=>x>=g.T&&(x-g.T)%8===4?lg:pl,8,4);g.beam("rm_dark_oak_log");g.floor(rt("rg_crypt_tiles")||"rm_polished_blackstone");
  const c=g.cx,pi=g.items.slice(0,4);g.put(c,4,pd);g.icon(c,3,"goety:dark_altar",{big:1});g.lamp(c,3,8,[170,110,255]);
  [-4,-2,2,4].forEach((dx,i)=>{g.put(c+dx,4,pd);if(pi[i])g.icon(c+dx,3,pi[i],{cls:"bob"});g.pt(c+dx,3,"glyph",{to:[c,3],k:i,pur:1})})},
 storage:g=>{g.amb=9;
  g.wall(()=>"ae2_sky_stone_brick");g.beam("ae2_smooth_sky_stone_block");g.floor("ae2_smooth_sky_stone_block");
  const c=g.cx;for(let y=1;y<=4;y++){g.put(c,y,"ae2_controller_powered");g.anim(c,y,"ae2_controller_lights",12,1800,{delay:-y*300})}g.lamp(c,2,8,[150,200,255]);
  for(let dx=1;dx<=3;dx++){g.put(c+dx,4,"ae2_drive_front");g.put(c-dx,4,"ae2_drive_front")}},
 vault:g=>{g.amb=9;
  g.wall(()=>g.R(9)?"rm_deepslate_bricks":"rm_cracked_deepslate_tiles");g.beam("rm_polished_deepslate");g.floor("rm_polished_deepslate");
  const c=g.cx;g.put(c,4,"rm_beacon");g.beamUp(c,4);g.lamp(c,4,9,[150,240,255]);g.put(c-1,4,"rm_gold_block");g.put(c+1,4,"rm_gold_block");
  [-4,4].forEach(dx=>{g.put(c+dx,4,"rm_amethyst_block");g.put(c+dx,3,"rm_amethyst_cluster");g.pt(c+dx,3,"glitter",{k:dx>0?1:0})})}
};
function rPaint(el){const k=el.dataset.room,spec=ROOMK[k];if(!spec||typeof ROOMT==="undefined")return;
 const W=el.clientWidth;if(!W)return;const C=Math.ceil(W/RB)+1,ox=-Math.floor((C*RB-W)/2);
 // the title takes at least 8 columns; a scene needs 7 more right of it. A room too narrow for both (under about 600 px)
 // is a bare wall: the title spans it and the scene's props are left out, as the older rooms leave theirs out on phones.
 const head=el.classList.contains("rhd");let T=head?Math.max(8,Math.ceil(Math.min(500,W*.36)/RB)):0;const bare=head&&C-T<7;if(bare)T=C;
 const cx=Math.max(T+6,Math.floor((T+C)/2));     // the scene: in the middle of the wall right of the title
 let sd=[...k].reduce((a,c)=>a*31+c.charCodeAt(0),7)>>>0;const R=m=>{sd=(sd*1103515245+12345)>>>0;return (sd>>>8)%m};
 // place the title first; the room grows by whole blocks until the title and lede sit above the floor, and the scene's
 // props move down with the floor (D extra rows)
 const hd=el.querySelector(".rhead");if(hd){const l=Math.max(16,RB+ox);hd.style.left=l+"px";hd.style.width=(bare?W-2*l:(T-1)*RB+ox-l)+"px"}
 const N=hd?Math.max(RR,Math.ceil((hd.offsetTop+hd.offsetHeight+8)/RB)+1):RR,D=N-RR;el.style.height=N>RR?N*RB+"px":"";
 const wall=[],deco=[],over=[],lights=[],anims=[],pts=[],icons=[];let wf=null,wper=0,woff=0,ft=null;
 const g={C,T,cx,R,amb:9,items:(el.dataset.ids||"").split(" ").filter(Boolean),
  wall:(f,per,off)=>{wf=f;wper=per||0;woff=off||0;for(let y=1;y<N-1;y++)for(let x=0;x<C;x++)wall.push([x,y,f(x,y)])},
  beam:t=>{for(let x=0;x<C;x++)wall.push([x,0,t,{rot:1}])},floor:t=>{ft=t;for(let x=0;x<C;x++)wall.push([x,N-1,t])},
  put:(x,y,t,o={})=>deco.push([x,y+D,t,o]),over:(x,y,t,o={})=>over.push([x,y+D,t,o]),icon:(x,y,id,o={})=>icons.push([x,y+D,id,o]),
  anim:(x,y,t,fr,ms,o={})=>anims.push([x,y+D,t,fr,ms,o]),lamp:(x,y,l,c)=>lights.push([x,y+D,l,c]),pt:(x,y,t,o={})=>pts.push([x,y+D,t,o]),
  hang:(x,t,len)=>{for(let y=1;y<=len+D;y++)deco.push([x,y,y<len+D?"ri_chain":t,{}])},
  stand:(x,m)=>deco.push([x,3+D,"as_"+m,{tall:1}]),     // an armor stand wearing the set: 1 block wide, 2 tall (armor_stand.py)
  beamUp:(x,y)=>anims.push([x,0,"beam",1,0,{h:y+D}])};
 if(bare)for(const f of ["put","over","icon","anim","lamp","pt","hang","stand","beamUp"])g[f]=()=>{};   // wall, beam and floor only
 spec(g);
 const keys=new Set([...wall,...deco,...over].map(e=>e[2]));
 Promise.all([...keys].map(t=>rImg(t).ready).concat(icons.map(e=>(rIcon(e[2])||{ready:Promise.resolve()}).ready))).then(()=>{
  if(!el.isConnected)return;const cv=el.querySelector(".rcv");cv.width=C*16;cv.height=N*16;cv.style.width=C*RB+"px";cv.style.height=N*RB+"px";cv.style.left=ox+"px";
  const x2=cv.getContext("2d");x2.imageSmoothingEnabled=false;x2.fillStyle="#141416";x2.fillRect(0,0,cv.width,cv.height);
  const draw=([x,y,t,o={}])=>{
   const im=RIMG[t];if(!im||!im.width)return;if(o.tall){x2.drawImage(im,0,0,16,32,x*16,y*16,16,32);return}const s=o.s||1,w=16*s,h=16*s;
   if(o.rot){x2.save();x2.translate(x*16+8,y*16+8);x2.rotate(Math.PI/2);x2.drawImage(im,0,0,16,16,-8,-8,16,16);x2.restore()}
   else x2.drawImage(im,0,0,16,16,Math.round(x*16+(16-w)/2),Math.round(y*16+(o.dy||0)+(16-h)/2),w,h)};
  wall.forEach(draw);
  for(let x=0;x<C;x++){x2.fillStyle="rgba(0,0,0,.3)";x2.fillRect(x*16,16,16,2);x2.fillRect(x*16,(N-1)*16-2,16,2)}   // shade under the beam and above the floor
  deco.forEach(draw);over.forEach(draw);
  /* light: the room's level, raised near lamps by (lamp level − blocks away), per texel blended between block centres */
  const L=[];for(let y=0;y<N;y++){L[y]=[];for(let x=0;x<C;x++){let l=g.amb;for(const[lx,ly,lv]of lights)l=Math.max(l,lv-Math.abs(lx-x)-Math.abs(ly-y));L[y][x]=l}}
  const at=(x,y)=>L[Math.max(0,Math.min(N-1,y))][Math.max(0,Math.min(C-1,x))];
  // one shade value per 2x2 texels, written into an image half the canvas size and drawn at x2 without smoothing (one draw call)
  const sw=C*8,sh=N*8,sh_=document.createElement("canvas");sh_.width=sw;sh_.height=sh;const sx=sh_.getContext("2d"),id=sx.createImageData(sw,sh),A=[];
  for(let l=0;l<=15;l++)A[l]=Math.round(255*.8*Math.pow(1-l/15,1.6));
  for(let ty=0;ty<sh;ty++)for(let tx=0;tx<sw;tx++){const fx=tx/8-.5,fy=ty/8-.5,x0=Math.floor(fx),y0=Math.floor(fy),ax=fx-x0,ay=fy-y0;
   const l=Math.round(at(x0,y0)*(1-ax)*(1-ay)+at(x0+1,y0)*ax*(1-ay)+at(x0,y0+1)*(1-ax)*ay+at(x0+1,y0+1)*ax*ay),o=(ty*sw+tx)*4;
   id.data[o]=8;id.data[o+1]=7;id.data[o+2]=12;id.data[o+3]=A[Math.max(0,Math.min(15,l))]}
  sx.putImageData(id,0,0);x2.drawImage(sh_,0,0,sw,sh,0,0,C*16,N*16);
  x2.globalCompositeOperation="lighter";
  for(const[lx,ly,lv,c]of lights){const gx=lx*16+8,gy=ly*16+8,r=lv*7,gr=x2.createRadialGradient(gx,gy,0,gx,gy,r);gr.addColorStop(0,`rgba(${c},.14)`);gr.addColorStop(1,`rgba(${c},0)`);x2.fillStyle=gr;x2.fillRect(gx-r,gy-r,2*r,2*r)}
  x2.globalCompositeOperation="source-over";
  if(T){const gr=x2.createLinearGradient(0,0,T*16,0);gr.addColorStop(0,"rgba(8,7,12,.55)");gr.addColorStop(1,"rgba(8,7,12,0)");x2.fillStyle=gr;x2.fillRect(0,16,T*16,(N-2)*16)}   // the title's corner a little darker
  /* moving parts, in page pixels */
  const fx=el.querySelector(".rfx"),P=(x,y)=>`left:${x*RB+ox}px;top:${y*RB}px`;let h="";
  anims.forEach(([x,y,t,fr,ms,o])=>{if(t==="beam"){h+=`<i class="rbeam" style="left:${x*RB+ox+18}px;top:0;height:${o.h*RB+RB/2}px"></i>`;return}
   // a frame strip moves inside its block by transform (the compositor plays it; no repaint per frame); one frame does not move
   h+=fr>1?`<i class="ranim${o.cls?" "+o.cls:""}" style="${P(x,y)};--tex:var(--rt-${t});--fr:${fr};--ms:${ms}ms;${o.alt?"--dir:alternate;":""}${o.delay?`--dl:${o.delay}ms;`:""}"><b></b></i>`
    :`<i class="rstill${o.cls?" "+o.cls:""}" style="${P(x,y)};--tex:var(--rt-${t})"></i>`});
  over.filter(e=>anims.some(a=>a[0]===e[0]&&a[1]===e[1])).forEach(([x,y,t])=>h+=`<i class="rover" style="${P(x,y)};--tex:var(--rt-${t})"></i>`);
  icons.forEach(([x,y,id,o])=>{if(RIMG["ic:"+id])h+=`<i class="ricon${o.cls?" "+o.cls:""}${o.big?" big":""}" style="${P(x,y)};--tex:url(${RIMG["ic:"+id].src})"></i>`});
  const PT={flame:"p_flame",lava:"p_lava",spark:"p_spark_0",soul:"p_soul_5",glitter:"p_glitter_3"};
  pts.forEach(([x,y,t,o])=>{const k=o.k||0;
   if(t==="glyph"){const dx=(o.to[0]-x)*RB,dy=(o.to[1]-y)*RB;h+=`<i class="rglyph${o.pur?" pur":""}" style="${P(x,y)};--dx:${dx}px;--dy:${dy}px;--sp:var(--v-p_sga_${"aekrxz"[k%6]});animation-delay:${-(k*.8).toFixed(1)}s"></i>`;return}
   for(let i=0;i<2;i++)h+=`<i class="rpt ${t}" style="left:${x*RB+ox+(o.dx!=null?o.dx*RB:16+i*8)}px;top:${y*RB+(o.dy||0)*RB}px;--sp:var(--v-${PT[t]||"p_flame"});animation-delay:${-((k*1.3+i*1.4)%3).toFixed(1)}s"></i>`});
  fx.innerHTML=h;
  rWall(el,wf,wper,woff,ft,T,ox,lights[0]&&lights[0][3]);
  el.dataset.p=W})}
/* The room spreads over the page: its wall goes on behind the whole page (.rwall, put first in <main>, as wide as the window),
   block for block in the columns of the room above, and its floor lies at the foot of the page. The wall is one tile, two pillar gaps wide
   and WQ blocks tall, repeated: the room's own wall blocks, darker than in the room (the panels and the text on the wall
   must read), with a lantern on a pillar in each half, one high and one low, that lights the blocks around it as the room's
   lamps do. Left of the title the pillars go on in the same rhythm. A page without a room has no wall. */
const WQ=12,WAMB=3,WLAMP=8,WTILE={};
function rWall(el,wf,per,off,ft,T,ox,lc){const main=el.closest("main");if(!main||!wf)return;
 const P=per||8,W2=2*P,p1=(((T+off)%P)+P)%P,lamps=[[per?p1:3,3],[(per?p1:3)+P,9]],lt=rt("ri_lantern"),col=lc||[255,180,100],key=el.dataset.room+":"+T;
 let w=main.querySelector(":scope>.rwall");if(!w){w=document.createElement("div");w.className="rwall";w.setAttribute("aria-hidden","true");w.innerHTML="<i></i>";main.prepend(w)}
 // the wall is as wide as the window and starts at the top of the page (under the header), so it also lies behind the side
 // panel and in the page's margins; it is placed from the room's own columns and rows
 const place=()=>{const m=main.getBoundingClientRect(),r=el.getBoundingClientRect(),x=Math.round(r.left+el.clientLeft+ox),y=Math.round(r.top+scrollY+el.clientTop);
  w.style.cssText=`left:${-Math.round(m.left)}px;width:${document.documentElement.clientWidth}px;top:${-Math.round(m.top+scrollY)}px;background-image:url(${WTILE[key]});background-size:${W2*RB}px ${WQ*RB}px;background-position:${x}px ${y}px;--fx:${x}px;--ft:var(--rt-${ft||"rm_polished_blackstone"})`};
 if(WTILE[key]){place();return}
 // 504 = 7*8*9: a column left of the title is drawn as the one 504 further right, so the pillars keep their rhythm (they are 7, 8 or 9 apart)
 const cells=[];for(let y=0;y<WQ;y++)for(let x=0;x<W2;x++)cells.push([x,y,wf(x<T?x+504:x,y%4+1)]);
 const keys=[...new Set(cells.map(c=>c[2]))];if(lt)keys.push(lt);
 Promise.all(keys.map(t=>rImg(t).ready)).then(()=>{if(!w.isConnected)return;
  const cv=document.createElement("canvas");cv.width=W2*16;cv.height=WQ*16;const x2=cv.getContext("2d");x2.imageSmoothingEnabled=false;
  cells.forEach(([x,y,t])=>{const im=RIMG[t];if(im&&im.width)x2.drawImage(im,0,0,16,16,x*16,y*16,16,16)});
  if(lt)lamps.forEach(([x,y])=>x2.drawImage(RIMG[lt],0,0,16,16,x*16,y*16,16,16));
  // light per block, the distance measured round the tile's edges so the tile repeats without a seam; shaded per 2x2 texels as in the room
  const d=(a,b,n)=>{const v=Math.abs(a-b);return Math.min(v,n-v)},lv=(x,y)=>{x=((x%W2)+W2)%W2;y=((y%WQ)+WQ)%WQ;let l=WAMB;for(const[lx,ly]of lamps)l=Math.max(l,WLAMP-d(lx,x,W2)-d(ly,y,WQ));return l};
  const sw=W2*8,sh=WQ*8,sc=document.createElement("canvas");sc.width=sw;sc.height=sh;const sx=sc.getContext("2d"),id=sx.createImageData(sw,sh);
  for(let ty=0;ty<sh;ty++)for(let tx=0;tx<sw;tx++){const fx=tx/8-.5,fy=ty/8-.5,x0=Math.floor(fx),y0=Math.floor(fy),ax=fx-x0,ay=fy-y0;
   const l=lv(x0,y0)*(1-ax)*(1-ay)+lv(x0+1,y0)*ax*(1-ay)+lv(x0,y0+1)*(1-ax)*ay+lv(x0+1,y0+1)*ax*ay,o=(ty*sw+tx)*4;
   id.data[o]=8;id.data[o+1]=7;id.data[o+2]=12;id.data[o+3]=Math.round(255*(.84-.44*Math.max(0,l-WAMB)/(WLAMP-WAMB)))}
  sx.putImageData(id,0,0);x2.drawImage(sc,0,0,sw,sh,0,0,cv.width,cv.height);
  x2.globalCompositeOperation="lighter";
  for(const[lx,ly]of lamps)for(const wx of [-1,0,1]){const gx=lx*16+8+wx*cv.width,gy=ly*16+8,r=44,gr=x2.createRadialGradient(gx,gy,0,gx,gy,r);gr.addColorStop(0,`rgba(${col},.2)`);gr.addColorStop(1,`rgba(${col},0)`);x2.fillStyle=gr;x2.fillRect(gx-r,gy-r,2*r,2*r)}
  WTILE[key]=cv.toDataURL();place()})}
// painted from a ResizeObserver, which reports the room's width after the page's own layout: asking for it earlier would
// force that layout (~0.15 s on the Curios page) before the first paint. The first report paints at once, later ones after 120 ms.
{const ro=typeof ResizeObserver!=="undefined"&&new ResizeObserver(es=>es.forEach(e=>{const el=e.target,w=Math.round(e.contentRect.width);if(+el.dataset.p===w)return;
  if(!el.dataset.p)rPaint(el);else{clearTimeout(el._rt);el._rt=setTimeout(()=>rPaint(el),120)}}));
 const scan=()=>document.querySelectorAll(".room3:not([data-w])").forEach(el=>{el.dataset.w=1;if(ro)ro.observe(el);else rPaint(el)});
 if(document.fonts)document.fonts.ready.then(()=>document.querySelectorAll(".room3[data-w]").forEach(el=>el.isConnected&&rPaint(el)));
 new MutationObserver(ms=>{for(const m of ms)for(const n of m.addedNodes)if(n.nodeType===1&&(n.matches(".room3")||n.querySelector(".room3"))){scan();return}}).observe(document.documentElement,{childList:true,subtree:true})}
