/* ---------- rooms: the interior at the top of each main page ----------
   A room is a cross-section of a Minecraft build, six blocks tall (beam, four blocks of wall, floor), as wide as the
   page. Its blocks are drawn into one canvas at 16 px per block and shown at x3 (one block = 48 px), then lit the way
   the game lights a room: every light source gives a light level that drops by one per block, the dark is quantised to
   those levels and stepped per texel, and torches, lava and soul fire add their own colour on top.
   The page's items hang in item frames on the right (real links with tooltips); the title sits in the shade on the left;
   the middle is the room's own scene, different for every room (library and enchanting table, forge and lava fall,
   crypt and spawner, wardrobe of armour stands, ritual altar, ME storage, beacon vault). Lava, fire, lanterns and the
   particles move as in game (frame strips from the block textures, at the game's frame times).
   The middle fills whatever width the page has: shelves, pillars, chains and lamps repeat, the scene stays centred.
     room(kind, items, o)  items [{h: href, i: icon html, t: data-t for the tooltip, n: name, l: label, g: glow frame}]
                           o {head: html for the title, min: frames to show even when empty, cols: frames per row, label}
   Textures: ROOMT (scenes.js, uiicons.js: rm_* blocks, ri_* items, rg_* Goety's crypt). Painted when the room is in the
   page, and again when its width changes. */
const RB=48,RR=6;
function room(kind,items,o={}){const n=Math.max(items.length,o.min||0),xs=[...items,...Array(n-items.length).fill(null)];
 return `<div class="room3${o.head?" rhd":""}" data-room="${kind}" data-cols="${o.cols||8}" data-n="${n}">
<canvas class="rcv" aria-hidden="true"></canvas><div class="rfx" aria-hidden="true"></div>${o.head?`<div class="rhead">${o.head}</div>`:""}
<nav class="rfrs" aria-label="${esc(o.label||"Items")}">${xs.map(x=>x?`<a class="rfr${x.g?" glow":""}" href="${x.h}"${x.t!=null?` data-t="${x.t}"`:` title="${esc(x.n)}"`} aria-label="${esc(x.n)}">${x.i}${x.l?`<small${x.l.length>3?' class="lg"':""}>${x.l}</small>`:""}</a>`:`<span class="rfr empty" aria-hidden="true"></span>`).join("")}</nav></div>`}
const RIMG={};
const rImg=k=>{if(RIMG[k])return RIMG[k];const b=typeof ROOMT!=="undefined"&&ROOMT[k];const im=new Image();RIMG[k]=im;
 im.ready=b?new Promise(r=>{im.onload=im.onerror=()=>r(im)}):Promise.resolve(im);if(b)im.src="data:image/png;base64,"+b;return im};
const rIcon=k=>{const s=typeof IC!=="undefined"&&IC[k];if(!s)return null;if(RIMG["ic:"+k])return RIMG["ic:"+k];const im=new Image();RIMG["ic:"+k]=im;
 im.ready=new Promise(r=>{im.onload=im.onerror=()=>r(im)});im.src=typeof icu==="function"?icu(k):"data:image/png;base64,"+s;return im};
/* the scenes. g: C cols, T first col after the title, F0..F1 frame columns, fy0..fy1 frame rows, cx middle of the free part,
   M0..M1 the free part; wall/put/anim/lamp/pt to build; R(n) a seeded random */
const ROOMK={
 library:g=>{g.amb=3;
  g.wall((x,y)=>x>=g.T&&(x-g.T)%8===0?"rm_stripped_oak_log":"rm_oak_planks");g.beam("rm_dark_oak_log");g.floor("rm_spruce_planks");
  const shelf=()=>["rm_bookshelf","rm_bookshelf","rm_chiseled_bookshelf_occupied","xali_bookshelf_1","xali_bookshelf_7","xali_bookshelf_12"][g.R(6)];
  for(let x=g.M0;x<=g.M1;x++)if((x-g.T)%8)g.put(x,1,shelf());
  const c=g.cx;if(g.wide){
   [[-2,3],[-2,4],[2,3],[2,4],[-3,4],[3,4]].forEach(([dx,y])=>g.put(c+dx,y,shelf()));
   g.put(c,4,"rm_enchanting_table_side");g.anim(c,3,"ri_enchanted_book",1,0,{cls:"bob"});g.lamp(c,4,7,[150,110,255]);
   [-2,2].forEach(dx=>{g.put(c+dx,2,"ri_candle",{dy:6});g.lamp(c+dx,2,12,[255,190,110]);g.pt(c+dx,2,"flame",{dy:.35})});
   [[-2,3],[2,3],[-3,4],[3,4],[-2,4],[2,4]].forEach(([dx,y],i)=>g.pt(c+dx,y,"glyph",{to:[c,3],k:i}));
   for(let x=1;x<c-4;x+=2+g.R(2))g.put(x,4,["rm_barrel_side","ri_flower_pot","rm_lectern_sides","rm_bookshelf"][g.R(4)]);
   for(let x=c+5;x<=g.M1;x+=2+g.R(2))g.put(x,4,["rm_barrel_side","rm_crafting_table_front","ri_flower_pot"][g.R(3)])}
  for(let x=g.M0+3;x<=g.M1-1;x+=8)if(Math.abs(x-c)>3){g.hang(x,"ri_lantern",2);g.lamp(x,2,11,[255,180,100])}
  g.lamp(g.F0+1,4,9,[255,180,100]);g.put(g.F0+1,4,"ri_candle",{dy:6})},
 forge:g=>{g.amb=2;
  g.wall((x,y)=>x>=g.T&&(x-g.T)%9===0?"rm_polished_deepslate":["rm_stone_bricks","rm_stone_bricks","rm_stone_bricks","rm_cracked_stone_bricks","rm_mossy_stone_bricks"][g.R(5)]);
  g.beam("rm_deepslate_tiles");g.floor("rm_polished_blackstone");
  const c=g.cx;if(g.wide){
   for(let y=1;y<=4;y++){g.anim(c,y,"rm_lava_still",20,2000,{alt:1});g.anim(c+1,y,"rm_lava_still",20,2000,{alt:1,delay:-700})}
   for(let y=1;y<=3;y++){g.over(c,y,"rm_iron_bars");g.over(c+1,y,"rm_iron_bars")}
   g.lamp(c,2,15,[255,120,30]);g.lamp(c+1,4,15,[255,120,30]);g.pt(c,4,"lava",{dx:.5});g.pt(c+1,4,"lava",{dx:.3,k:2});
   g.anim(c-2,4,"rm_blast_furnace_front_on",2,1000,{alt:1});g.lamp(c-2,4,13,[255,150,60]);g.put(c-3,4,"rm_blast_furnace_side");
   g.put(c+3,4,"rm_anvil");g.pt(c+3,3,"spark",{dy:.8});g.put(c+4,4,"rm_smithing_table_front");
   [["ri_iron_sword",-3],["ri_diamond_sword",-2],["ri_netherite_sword",3],["ri_bow",4]].forEach(([k,dx])=>g.put(c+dx,2,k))}
  for(let x=g.T;x<=g.F1;x++)if((x-g.T)%9===0&&Math.abs(x-g.cx)>4){g.put(x,2,"rm_torch");g.lamp(x,2,12,[255,170,80]);g.pt(x,2,"flame",{dy:.3})}
  for(let x=g.M0+2;x<=g.M1;x+=6)if(Math.abs(x-g.cx)>5)g.chain(x,1+g.R(2))},
 crypt:g=>{g.amb=2;const br=ROOMT.rg_crypt_bricks?"rg_crypt_bricks":"rm_polished_blackstone_bricks";
  g.wall((x,y)=>x>=g.T&&(x-g.T)%7===0?(ROOMT.rg_crypt_pillar?"rg_crypt_pillar":"rm_polished_basalt_side"):g.R(6)?br:"rm_cracked_polished_blackstone_bricks");
  g.beam("rm_polished_blackstone");g.floor(ROOMT.rg_crypt_tiles?"rg_crypt_tiles":"rm_polished_blackstone");
  const c=g.cx;if(g.wide){
   g.put(c,4,"mf_zombie",{dy:4,s:.5});g.put(c,4,"rm_spawner");g.lamp(c,4,5,[200,80,255]);g.pt(c,4,"flame",{dy:.4,k:1});g.pt(c,4,"smoke",{dy:.2});
   [-3,3].forEach(dx=>{g.put(c+dx,4,"rm_soul_soil");g.anim(c+dx,3,ROOMT.rg_brazier_soul?"rg_brazier_soul":"rm_soul_fire_0",ROOMT.rg_brazier_soul?4:32,ROOMT.rg_brazier_soul?600:1600,{});
    g.lamp(c+dx,3,12,[90,200,255]);g.pt(c+dx,3,"soul",{k:dx>0?1:0})});
   [-5,5].forEach(dx=>{g.put(c+dx,4,ROOMT.rg_crypt_plinth?"rg_crypt_plinth":"rm_chiseled_polished_blackstone");g.put(c+dx,3,"ri_skeleton_skull",{dy:3})});
   [-2,2].forEach(dx=>{g.put(c+dx,3,ROOMT.rg_crypt_bookshelf?"rg_crypt_bookshelf":"rm_bookshelf");g.put(c+dx,4,ROOMT.rg_crypt_bookshelf?"rg_crypt_bookshelf":"rm_bookshelf")})}
  g.over(g.M0,1,"rm_cobweb");g.over(g.M1,1,"rm_cobweb");
  for(let x=g.M0+2;x<=g.M1-1;x+=5)if(Math.abs(x-c)>1){g.chain(x,1+g.R(2))}
  for(let x=g.M0+4;x<=g.M1;x+=10){g.hang(x,"ri_soul_lantern",1);g.lamp(x,2,10,[90,200,255])}},
 armory:g=>{g.amb=3;
  g.wall((x,y)=>x>=g.T&&(x-g.T)%7===0?"rm_stripped_spruce_log":"rm_spruce_planks");g.beam("rm_dark_oak_log");g.floor("rm_dark_oak_planks");
  const c=g.cx,sets=[["iron"],["diamond"],["netherite"]];if(g.wide){
   sets.forEach(([m],i)=>{const x=c+(i-1)*3;g.stand(x,m)});
   g.put(c-5,4,"rm_crafting_table_front");g.put(c+5,4,"rm_barrel_side");g.put(c+5,3,"ri_lantern",{dy:5});g.lamp(c+5,3,12,[255,180,100]);g.put(c-6,4,"rm_bookshelf");g.put(c+6,4,"rm_crafting_table_front");
   g.put(c-5,3,"ri_shield",{dy:3})}
  for(let x=g.M0+1;x<=g.M1;x+=7)if(Math.abs(x-c)>6){g.hang(x,"ri_lantern",2);g.lamp(x,2,11,[255,180,100])}
  g.lamp(g.F0+1,4,8,[255,180,100])},
 ritual:g=>{g.amb=3;const pl=ROOMT.goety_haunted_planks?"goety_haunted_planks":"rm_dark_oak_planks",lg=ROOMT.goety_stripped_haunted_log?"goety_stripped_haunted_log":"rm_stripped_dark_oak_log";
  g.wall((x,y)=>x>=g.T&&(x-g.T)%8===0?lg:y===1&&x>=g.M0&&x<=g.M1&&ROOMT.rg_haunted_bookshelf&&g.R(2)?"rg_haunted_bookshelf":pl);g.beam("rm_dark_oak_log");g.floor(ROOMT.rg_crypt_tiles?"rg_crypt_tiles":"rm_polished_blackstone");
  const c=g.cx,pi=g.items.slice(0,4);if(g.wide){
   g.put(c,4,ROOMT.rg_crypt_plinth?"rg_crypt_plinth":"rm_chiseled_polished_blackstone");g.icon(c,3,"goety:dark_altar",{big:1});g.lamp(c,3,9,[170,110,255]);
   [-4,-2,2,4].forEach((dx,i)=>{g.put(c+dx,4,ROOMT.rg_crypt_plinth?"rg_crypt_plinth":"rm_chiseled_polished_blackstone");if(pi[i])g.icon(c+dx,3,pi[i],{cls:"bob"});g.pt(c+dx,3,"glyph",{to:[c,3],k:i,pur:1})});
   [-6,6].forEach(dx=>{g.put(c+dx,4,ROOMT.rg_soul_candlestick?"rg_soul_candlestick":"ri_purple_candle");g.lamp(c+dx,4,11,[90,200,255]);g.pt(c+dx,4,"soulflame",{dy:.25})})}
  for(let x=g.M0+1;x<=g.M1;x+=6)if(Math.abs(x-c)>7)g.chain(x,1)},
 storage:g=>{g.amb=4;
  g.wall((x,y)=>"ae2_sky_stone_brick");g.beam("ae2_smooth_sky_stone_block");g.floor("ae2_smooth_sky_stone_block");
  const c=g.cx;for(let y=1;y<=4;y++){g.put(c,y,"ae2_controller_powered");g.anim(c,y,"ae2_controller_lights",12,1800,{delay:-y*300})}g.lamp(c,2,12,[150,200,255]);
  for(let dx=1;dx<=4&&c+dx<=g.M1;dx++){g.put(c+dx,4,"ae2_drive_front");g.put(c-dx,4,"ae2_drive_front");if(dx%2){g.put(c+dx,3,"ae2_fluix_block");g.lamp(c+dx,3,10,[170,120,255])}}
  g.pt(c,2,"glitter",{});g.pt(c+1,3,"glitter",{k:1})},
 vault:g=>{g.amb=3;
  g.wall((x,y)=>g.R(9)?"rm_deepslate_bricks":"rm_cracked_deepslate_tiles");g.beam("rm_polished_deepslate");g.floor("rm_polished_deepslate");
  const xs=[2,g.M1-1].filter((x,i,a)=>x>=1&&x<g.F0-1&&a.indexOf(x)===i);
  xs.forEach(x=>{g.put(x,4,"rm_beacon");g.beamUp(x,4);g.lamp(x,4,14,[150,240,255]);g.put(x-1,4,"rm_gold_block");g.put(x+1,4,"rm_gold_block");g.pt(x,3,"glitter",{})});
  for(let x=5;x<g.M1-3;x+=4){g.put(x,4,"rm_amethyst_block");g.put(x,3,"rm_amethyst_cluster");g.lamp(x,3,6,[190,130,255]);g.pt(x,3,"glitter",{k:x%3})}
  for(let x=4;x<g.F0-1;x+=6){g.hang(x,"ri_soul_lantern",2);g.lamp(x,2,9,[90,200,255])}}
};
/* stepped light: light level per block from the sources (level − blocks away, Manhattan), the dark quantised per texel */
function rPaint(el){const k=el.dataset.room,spec=ROOMK[k];if(!spec||typeof ROOMT==="undefined")return;
 const W=el.clientWidth;if(!W)return;const C=Math.ceil(W/RB)+1,ox=-Math.floor((C*RB-W)/2),cols=+el.dataset.cols||8,n=+el.dataset.n||0;
 const head=el.classList.contains("rhd"),T=head?Math.min(Math.max(8,Math.ceil(Math.min(500,W*.36)/RB)),C-8):1;
 // frames: up to three rows on the wall, as few columns as that allows (the room's own cols is the most per row)
 const fc=Math.max(1,Math.min(cols,Math.ceil((n||1)/3),C-T-4)),frows=Math.ceil((n||1)/fc),F1=C-2,F0=F1-fc+1,fy0=frows>=3?1:frows===2?1:2,fy1=fy0+frows-1;
 let sd=[...k].reduce((a,c)=>a*31+c.charCodeAt(0),7)>>>0;const R=m=>{sd=(sd*1103515245+12345)>>>0;return (sd>>>8)%m};
 // the scene: the upper wall from T, the floor row from the left wall (props stand under the title), centred where it fits
 const M0=T,M1=F0-2,cx=Math.max(Math.min(Math.floor((T+M1)/2),M1-5),6);
 const wall=[],deco=[],over=[],lights=[],anims=[],pts=[],icons=[];
 const items=[...el.querySelectorAll(".rfr[data-t]")].map(a=>{const d=typeof D!=="undefined"&&D[+a.dataset.t];return d&&d.id}).filter(Boolean);
 const g={C,T,F0,F1,fy0,fy1,M0,M1,cx,R,amb:5,items,wide:M1-1>=12,
  wall:f=>{for(let y=1;y<RR-1;y++)for(let x=0;x<C;x++)wall.push([x,y,f(x,y)])},
  beam:t=>{for(let x=0;x<C;x++)wall.push([x,0,t,{rot:1}])},floor:t=>{for(let x=0;x<C;x++)wall.push([x,RR-1,t])},
  put:(x,y,t,o={})=>deco.push([x,y,t,o]),over:(x,y,t,o={})=>over.push([x,y,t,o]),icon:(x,y,id,o={})=>icons.push([x,y,id,o]),
  anim:(x,y,t,fr,ms,o={})=>anims.push([x,y,t,fr,ms,o]),lamp:(x,y,l,c)=>lights.push([x,y,l,c]),pt:(x,y,t,o={})=>pts.push([x,y,t,o]),
  hang:(x,t,len)=>{for(let y=1;y<=len;y++)deco.push([x,y,y<len?"ri_chain":t,{}])},
  chain:(x,len)=>{for(let y=1;y<=len;y++)deco.push([x,y,"ri_chain",{}])},
  stand:(x,m)=>{deco.push([x,4,"stand",{}]);[["helmet",2.45],["chestplate",3.05],["leggings",3.55],["boots",3.95]].forEach(([p,y])=>deco.push([x,y,`ri_${m}_${p}`,{fy:1}]))},
  beamUp:(x,y)=>anims.push([x,0,"beam",1,0,{h:y}])};
 spec(g);
 // nothing on the upper wall behind the title: props in rows 1–2 left of T are dropped (the floor row may run under it)
 if(head)for(const L of [deco,over,lights,pts,icons,anims])for(let i=L.length-1;i>=0;i--)if(L[i][1]<=2.9&&L[i][0]<T)L.splice(i,1);
 const keys=new Set([...wall,...deco,...over].map(e=>e[2]).filter(t=>t!=="stand"));
 Promise.all([...keys].map(t=>rImg(t).ready).concat(icons.map(e=>(rIcon(e[2])||{ready:Promise.resolve()}).ready))).then(()=>{
  if(!el.isConnected)return;const cv=el.querySelector(".rcv");cv.width=C*16;cv.height=RR*16;cv.style.width=C*RB+"px";cv.style.height=RR*RB+"px";cv.style.left=ox+"px";
  const x2=cv.getContext("2d");x2.imageSmoothingEnabled=false;x2.fillStyle="#141416";x2.fillRect(0,0,cv.width,cv.height);
  const draw=([x,y,t,o={}])=>{if(t==="stand"){x2.fillStyle="#6b4f2a";x2.fillRect(x*16+7,y*16-20,2,36);x2.fillRect(x*16+3,y*16+14,10,2);x2.fillRect(x*16+4,y*16-12,8,2);return}
   const im=RIMG[t];if(!im||!im.width)return;const s=o.s||1,w=16*s,h=16*s,px=x*16+(16-w)/2,py=Math.round((o.fy?y:y)*16+(o.dy||0)+(16-h)/2*(o.s?1:0));
   if(o.rot){x2.save();x2.translate(x*16+8,y*16+8);x2.rotate(Math.PI/2);x2.drawImage(im,0,0,16,16,-8,-8,16,16);x2.restore()}
   else x2.drawImage(im,0,0,16,16,Math.round(px),py,w,h)};
  wall.forEach(draw);
  for(let x=0;x<C;x++){x2.fillStyle="rgba(0,0,0,.35)";x2.fillRect(x*16,16,16,2);x2.fillRect(x*16,(RR-1)*16-2,16,2)}   // shade under the beam and above the floor
  deco.forEach(draw);
  over.forEach(draw);
  /* light: level per block, then per texel by bilinear blend of the four nearest block centres, rounded to a whole level */
  const L=[];for(let y=0;y<RR;y++){L[y]=[];for(let x=0;x<C;x++){let l=g.amb;for(const[lx,ly,lv]of lights)l=Math.max(l,lv-Math.abs(lx-x)-Math.abs(ly-y));L[y][x]=l}}
  const at=(x,y)=>L[Math.max(0,Math.min(RR-1,y))][Math.max(0,Math.min(C-1,x))];
  for(let ty=0;ty<RR*16;ty+=2)for(let tx=0;tx<C*16;tx+=2){const fx=tx/16-.5,fy=ty/16-.5,x0=Math.floor(fx),y0=Math.floor(fy),ax=fx-x0,ay=fy-y0;
   const l=Math.round(at(x0,y0)*(1-ax)*(1-ay)+at(x0+1,y0)*ax*(1-ay)+at(x0,y0+1)*(1-ax)*ay+at(x0+1,y0+1)*ax*ay),a=.86*Math.pow(1-l/15,1.5);
   if(a>.01){x2.fillStyle=`rgba(6,5,10,${a.toFixed(3)})`;x2.fillRect(tx,ty,2,2)}}
  x2.globalCompositeOperation="lighter";
  for(const[lx,ly,lv,c]of lights){const gx=lx*16+8,gy=ly*16+8,r=lv*9,gr=x2.createRadialGradient(gx,gy,0,gx,gy,r);gr.addColorStop(0,`rgba(${c},.28)`);gr.addColorStop(1,`rgba(${c},0)`);x2.fillStyle=gr;x2.fillRect(gx-r,gy-r,2*r,2*r)}
  x2.globalCompositeOperation="source-over";
  /* moving parts: frame strips, particles; positions in page pixels */
  const fx=el.querySelector(".rfx"),P=(x,y)=>`left:${x*RB+ox}px;top:${y*RB}px`;let h="";
  anims.forEach(([x,y,t,fr,ms,o])=>{if(t==="beam"){h+=`<i class="rbeam" style="left:${x*RB+ox+18}px;top:0;height:${o.h*RB+RB/2}px"></i>`;return}
   h+=`<i class="ranim${o.cls?" "+o.cls:""}" style="${P(x,y)};--tex:var(--rt-${t});--fr:${fr};--ms:${ms}ms;${o.alt?"animation-direction:alternate;":""}${o.delay?`animation-delay:${o.delay}ms;`:""}"></i>`});
  icons.forEach(([x,y,id,o])=>{if(RIMG["ic:"+id])h+=`<i class="ricon${o.cls?" "+o.cls:""}${o.big?" big":""}" style="${P(x,y)};--tex:url(${RIMG["ic:"+id].src})"></i>`});
  over.filter(e=>anims.some(a=>a[0]===e[0]&&a[1]===e[1])).forEach(([x,y,t])=>h+=`<i class="rover" style="${P(x,y)};--tex:var(--rt-${t})"></i>`);
  const PT={flame:"p_flame",soulflame:"p_soul_fire_flame",lava:"p_lava",spark:"p_spark_0",soul:"p_soul_5",smoke:"p_glitter_0",glitter:"p_glitter_3"};
  pts.forEach(([x,y,t,o])=>{const k=o.k||0;
   if(t==="glyph"){const dx=(o.to[0]-x)*RB,dy=(o.to[1]-y)*RB;for(let i=0;i<2;i++)h+=`<i class="rglyph${o.pur?" pur":""}" style="${P(x,y)};--dx:${dx}px;--dy:${dy}px;--sp:var(--v-p_sga_${"aekrxz"[(k*2+i)%6]});animation-delay:${-(k*.7+i*1.6).toFixed(1)}s"></i>`;return}
   for(let i=0;i<3;i++)h+=`<i class="rpt ${t}" style="left:${x*RB+ox+(o.dx!=null?o.dx*RB:16+i*6)}px;top:${y*RB+(o.dy||0)*RB}px;--sp:var(--v-${PT[t]||"p_flame"});animation-delay:${-((k*1.3+i*.9)%3).toFixed(1)}s"></i>`});
  fx.innerHTML=h;
  const nav=el.querySelector(".rfrs");nav.style.left=(F0*RB+ox)+"px";nav.style.top=(fy0*RB)+"px";nav.style.gridTemplateColumns=`repeat(${fc},${RB}px)`;
  const hd=el.querySelector(".rhead");if(hd){hd.style.left=Math.max(16,RB+ox)+"px";hd.style.width=((T-1)*RB+ox-Math.max(16,RB+ox))+"px"}
  el.dataset.p=W})}
{const ro=typeof ResizeObserver!=="undefined"&&new ResizeObserver(es=>es.forEach(e=>{const el=e.target;if(+el.dataset.p!==el.clientWidth){clearTimeout(el._rt);el._rt=setTimeout(()=>rPaint(el),120)}}));
 const scan=r=>(r.querySelectorAll?r:document).querySelectorAll(".room3:not([data-w])").forEach(el=>{el.dataset.w=1;rPaint(el);if(ro)ro.observe(el)});
 new MutationObserver(ms=>{for(const m of ms)for(const n of m.addedNodes)if(n.nodeType===1&&(n.matches(".room3")||n.querySelector(".room3"))){scan(document);return}}).observe(document.documentElement,{childList:true,subtree:true})}
