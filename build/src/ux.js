/* ux.js: site-wide interaction layer, loaded after app.js and gear.js.
   - quick search: one result list for curios, weapons, armor, sets, Keepers, side bosses and pages, under the header and hero search boxes
   - the header nav marks the section you are in
   - header turns to glass once the page scrolls
   - Equipment tiles deal in when the Act, playstyle or weapons/armor switch changes
   Page transitions themselves live in app.js (hashchange). */
(()=>{
const RMQ=matchMedia("(prefers-reduced-motion:reduce)");

/* ---------- section marker in the header nav ---------- */
const SEC=[[/^#(home|i\d|act\/|slot\/|mod)/,"#home"],[/^#(gear|gs?\d)/,"#gear"],[/^#build/,"#build"],[/^#(bosses|boss\/|side\/)/,"#bosses"],[/^#mechanics/,"#mechanics"],[/^#changes/,"#changes"]];
function markNav(){const h=decodeURIComponent(location.hash),s=(SEC.find(x=>x[0].test(h))||[])[1];
 document.querySelectorAll(".top .nav a").forEach(a=>a.getAttribute("href")===s?a.setAttribute("aria-current","page"):a.removeAttribute("aria-current"))}

/* ---------- header glass on scroll ---------- */
let scq=0;addEventListener("scroll",()=>{if(!scq)scq=requestAnimationFrame(()=>{scq=0;document.body.classList.toggle("scrolled",scrollY>8);if(QS.open)place()})},{passive:true});

/* ---------- Equipment: tiles deal in on a switch ---------- */
let lastGear="";
function dealGear(){const h=location.hash;if(!/^#gear/.test(h)){lastGear="";return}
 const was=lastGear;lastGear=h;if(!was||RMQ.matches)return;
 const L=document.querySelector(".gtl-list,.gtiles.gsr");if(!L)return;
 let n=0;L.querySelectorAll(".gtiles>a").forEach(t=>t.style.setProperty("--n",Math.min(n++,28)));
 L.classList.add("deal");setTimeout(()=>L.classList.remove("deal"),900)}

/* ---------- quick search ---------- */
const QS={open:false,inp:null,items:[],sel:0,idx:null};
const box=document.createElement("div");box.id="qs";box.setAttribute("role","listbox");box.setAttribute("aria-label","Search results");box.hidden=true;document.body.appendChild(box);
const PAGES=[["Curios","#home","Every curio by the Act you can get it in"],["Equipment","#gear","Weapon and armor tier lists"],["Build planner","#build","Plan curio slots and see stat totals"],["Bosses","#bosses","Keepers in fight order, with summon guides"],["Mechanics","#mechanics","Goety rituals and AE2 storage"],["Changes","#changes","What's new on the wiki"]];
function index(){if(QS.idx)return QS.idx;const o=[];
 const add=(n,h,ic,meta,kind,w,c,t)=>o.push({n,l:n.toLowerCase(),h,ic,meta,kind,w,c,t});
 PAGES.forEach(([n,h,m])=>add(n,h,()=>'<span class="qpg" aria-hidden="true">'+n[0]+"</span>",m,"Page",3));
 const ks=ORDER.map(a=>PB[a]).filter(Boolean);ks.splice(ks.indexOf("zoranth_forgotten")+1,0,"warden","wither");
 ks.forEach(k=>{const a=bossPath(k);add(bossName(k),"#boss/"+k,()=>emblem(a,"xs"),SIDEV[k]!=null?"Side boss at "+actL(a):"Keeper, opens "+actL(a),"Boss",2.5)});
 if(typeof SIDEB!=="undefined")Object.keys(SIDEB).forEach(n=>{const b=SIDEB[n];add(n,"#side/"+enc(n),()=>b.img?`<img alt="" src="${b.img}">`:`<span class="qpg" aria-hidden="true">${esc(n[0])}</span>`,(b.mod?b.mod+" side boss":"Side boss"),"Boss",2)});
 D.forEach(d=>add(d.n,"#i"+d.ix,()=>img(d.id),d.m+", "+actL(d.t),"Curio",1+d.r/6,RC[d.r],String(d.ix)));
 if(typeof GE!=="undefined"){
  GE.forEach(g=>{if(/creative only/i.test(g.n))return;const ar=g.k==="armor";add(g.n,"#g"+g.ix,()=>gImg(g),(ar?"Armor":"Weapon")+", "+actL(g.a),ar?"Armor":"Weapon",1.2,null,"g"+g.ix)});
  GS.forEach(s=>add(s.n+" set","#gs"+s.ix,()=>gImg(s),s.ps.length+(s.ps.length>1?" pieces, ":" piece, ")+actL(s.a),"Armor set",1.3,null,"s"+s.ix))}
 return QS.idx=o}
const GROUPS=[["Page",3],["Boss",5],["Curio",6],["Weapon",5],["Armor set",4],["Armor",4]];
function search(q){q=q.toLowerCase().trim();if(!q)return[];const ws=q.split(/\s+/);
 const hits=[];for(const e of index()){const l=e.l;let s=0;
  if(l===q)s=100;else if(l.startsWith(q))s=80;else{const i=l.indexOf(q);if(i>0&&!/[a-z0-9]/.test(l[i-1]))s=60;else if(i>0)s=40;else if(ws.length>1&&ws.every(w=>l.includes(w)))s=30}
  if(s)hits.push([s+e.w-l.length/100,e])}
 hits.sort((a,b)=>b[0]-a[0]);
 const by={};hits.forEach(([s,e])=>{(by[e.kind]=by[e.kind]||{s,xs:[]}).xs.push(e)});
 return GROUPS.filter(([k])=>by[k]).sort((a,b)=>by[b[0]].s-by[a[0]].s).map(([k,n])=>[k,by[k].xs.slice(0,n),by[k].xs.length])}
const hl=(n,q)=>{const i=n.toLowerCase().indexOf(q.toLowerCase().trim());return i<0||!q.trim()?esc(n):esc(n.slice(0,i))+"<mark>"+esc(n.slice(i,i+q.trim().length))+"</mark>"+esc(n.slice(i+q.trim().length))};
/* recently opened pages: shown when the search box is focused empty (this browser only) */
const RKEY="lgw-recent";let recent=[];try{recent=JSON.parse(localStorage.getItem(RKEY)||"[]")}catch(e){}
function remember(){const h=decodeURIComponent(location.hash);if(!/^#(i\d|gs?\d|boss\/|side\/)/.test(h))return;
 recent=[h,...recent.filter(x=>x!==h)].slice(0,8);try{localStorage.setItem(RKEY,JSON.stringify(recent))}catch(e){}}
function drawRecent(){const by=new Map(index().map(e=>[decodeURIComponent(e.h),e]));const xs=recent.map(h=>by.get(h)).filter(Boolean);if(!xs.length)return false;
 QS.items=xs;box.innerHTML=`<div class="qg" role="presentation"><span>Recently opened</span></div>`+xs.map((e,i)=>row(e,i,"")).join("")+KEYS;QS.sel=0;mark();return true}
const KEYS=`<p class="qkeys" aria-hidden="true"><span><kbd>↑</kbd><kbd>↓</kbd> move</span><span><kbd>Enter</kbd> open</span><span><kbd>Esc</kbd> close</span></p>`;
const row=(e,i,q)=>`<a class="qr" role="option" id="qr${i}" href="${e.h}"${e.t?` data-t="${e.t}"`:""} data-i="${i}"><span class="qic">${e.ic()}</span><span class="qtx"><b${e.c?` style="color:${e.c}"`:""}>${hl(e.n,q)}</b><small>${esc(e.meta)}</small></span></a>`;
function draw(q){const gs=search(q);QS.items=[];let html="";
 gs.forEach(([k,xs,all])=>{html+=`<div class="qg" role="presentation"><span>${k==="Boss"?"Bosses":k==="Curio"?"Curios":k+"s"}</span>${all>xs.length?`<em>${xs.length} of ${all}</em>`:""}</div>`;
  xs.forEach(e=>{const i=QS.items.length;QS.items.push(e);html+=row(e,i,q)})});
 const nc=D.filter(d=>{const s=st.q;st.q=q.trim();const r=qMatch(d);st.q=s;return r}).length;
 const i=QS.items.length;QS.items.push({h:"#home",path:true});
 html+=`<a class="qr qall" role="option" id="qr${i}" href="#home" data-i="${i}"><span class="qic"><span class="qpg" aria-hidden="true">⌕</span></span><span class="qtx"><b>${nc?`Show the ${nc} curios that mention “${esc(q.trim())}” in Curios`:`Filter Curios by “${esc(q.trim())}”`}</b><small>Keeps the search as a filter you can refine</small></span></a>`;
 if(gs.length===0)html=`<p class="qnone">Nothing is called “${esc(q.trim())}”. Try part of a name, a mod, or a stat.</p>`+html;
 html+=KEYS;
 box.innerHTML=html;QS.sel=0;mark()}
function mark(){box.querySelectorAll(".qr").forEach(r=>r.classList.toggle("on",+r.dataset.i===QS.sel));const r=el("qr"+QS.sel);
 if(QS.inp)QS.inp.setAttribute("aria-activedescendant",r?r.id:"");if(r)r.scrollIntoView({block:"nearest"})}
function place(){const r=QS.inp.getBoundingClientRect(),w=Math.min(Math.max(r.width,460),innerWidth-24),x=Math.min(Math.max(12,r.left),innerWidth-w-12);
 box.style.cssText=`left:${x}px;top:${r.bottom+6}px;width:${w}px;max-height:${Math.max(220,innerHeight-r.bottom-24)}px`}
function open(inp){QS.inp=inp;inp.setAttribute("role","combobox");inp.setAttribute("aria-expanded","true");inp.setAttribute("aria-controls","qs");place();if(!QS.open){QS.open=true;box.hidden=false;box.classList.remove("in");void box.offsetWidth;box.classList.add("in")}}
function close(){if(!QS.open)return;QS.open=false;box.hidden=true;hideTip();if(QS.inp){QS.inp.setAttribute("aria-expanded","false");QS.inp.removeAttribute("aria-activedescendant")}}
function go(e,inp){if(!e)return;const v=inp.value.trim();close();
 if(e.path){st.q=v;el("q").value=v;const f=el("fq");if(f)f.value=v;location.hash==="#home"?refresh():location.hash="#home";return}
 inp.value="";location.hash=e.h;inp.blur()}
const onPath=()=>{const h=decodeURIComponent(location.hash);return h==="#home"||/^#(slot|act|mod)\//.test(h)};
const isQ=t=>t&&(t.id==="q"||t.id==="hq");
const hq=el("q"),oldInput=hq.oninput;hq.oninput=null;
hq.setAttribute("aria-autocomplete","list");hq.setAttribute("aria-expanded","false");
document.addEventListener("input",e=>{const t=e.target;if(!isQ(t))return;
 // on Curios (#home) the header box filters the grid in place, as before; elsewhere it looks things up
 if(t.id==="q"&&onPath()){close();oldInput&&oldInput.call(t,e);return}
 if(!t.value.trim()){if(recent.length){open(t);if(drawRecent())return}close();return}
 open(t);draw(t.value)});
document.addEventListener("focusin",e=>{const t=e.target;if(!isQ(t)||t.id==="q"&&onPath())return;if(t.value.trim()){open(t);draw(t.value)}else if(recent.length){open(t);if(!drawRecent())close()}});
document.addEventListener("keydown",e=>{
 if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="k"){e.preventDefault();const t=el("hq")&&el("hq").offsetParent?el("hq"):el("q");t.focus();t.select();return}
 if(!QS.open||e.target!==QS.inp)return;const n=QS.items.length;
 if(e.key==="ArrowDown"){e.preventDefault();QS.sel=(QS.sel+1)%n;mark()}
 else if(e.key==="ArrowUp"){e.preventDefault();QS.sel=(QS.sel-1+n)%n;mark()}
 else if(e.key==="Enter"){e.preventDefault();e.stopImmediatePropagation();go(QS.items[QS.sel],QS.inp)}
 else if(e.key==="Escape"){e.preventDefault();e.stopImmediatePropagation();close()}},true);
box.addEventListener("mousedown",e=>e.preventDefault());
box.addEventListener("mousemove",e=>{const r=e.target.closest(".qr");if(r&&+r.dataset.i!==QS.sel){QS.sel=+r.dataset.i;box.querySelectorAll(".qr").forEach(x=>x.classList.toggle("on",x===r))}},{passive:true});
box.addEventListener("click",e=>{const r=e.target.closest(".qr");if(!r)return;e.preventDefault();go(QS.items[+r.dataset.i],QS.inp)});
document.addEventListener("focusout",e=>{if(e.target===QS.inp)setTimeout(()=>{if(document.activeElement!==QS.inp)close()},120)});
addEventListener("resize",()=>QS.open&&place());

/* skip link: focus the page content without touching the hash (the hash is the router) */
document.addEventListener("click",e=>{if(e.target.closest(".skip")){e.preventDefault();const m=el("main");m.focus();m.scrollIntoView()}});

/* ---------- wiring ---------- */
addEventListener("hashchange",()=>{close();markNav();dealGear();remember();
 // the header box shows the curio filter, not a lookup typed on another page
 if(document.activeElement!==hq&&!onPath())hq.value=st.q});
document.addEventListener("DOMContentLoaded",()=>{markNav();remember();lastGear=/^#gear/.test(location.hash)?location.hash:""});
})();
/* pixel art at a whole-number scale: an icon whose source does not divide its box (renders of 23, 24, 48 or 128 px) is drawn at
   the largest k x source, or source / k, that fits the box, centred in it, instead of being stretched to a fraction */
{const fit=i=>{if(i.dataset.px)return;const c=getComputedStyle(i);
  if(!/pixelated|crisp/.test(c.imageRendering))return;const n=i.naturalWidth,bw=parseFloat(c.width),bh=parseFloat(c.height);if(!bw||!bh)return;
  const s=bw/n,ok=x=>Math.abs(x-Math.round(x))<.02&&Math.round(x)>=1;if(ok(s)||ok(1/s)){i.dataset.px=0;return}
  const w=s>=1?Math.floor(s)*n:n/Math.ceil(1/s),h=w*i.naturalHeight/n;i.dataset.px=1;
  return ()=>{i.style.setProperty("width",w+"px","important");i.style.setProperty("height",h+"px","important");i.style.setProperty("margin",`${(bh-h)/2}px ${(bw-w)/2}px`,"important")}};
 // batched: all reads in one frame, then all writes, so the page lays out once, not once per image
 let q=[],raf=0;const flush=()=>{raf=0;const xs=q;q=[];xs.map(fit).forEach(f=>f&&f())};
 const fitPx=i=>{if(i.tagName!=="IMG"||!i.naturalWidth||i.naturalWidth>256||i.dataset.px)return;q.push(i);if(!raf)raf=requestAnimationFrame(flush)};
 document.addEventListener("load",e=>fitPx(e.target),true);[...document.images].forEach(i=>i.complete&&fitPx(i))}
/* motion that says something and then stops (see style.game.css v47):
   - .zz pauses everything inside a room, an Act's tiles or a picture while it is off screen
   - an Act's tiles rise in once when the Act first comes into view (.seen2)
   - article sections, cards and drop cards rise in once as they reach the screen (.rv → .in), a few at a time
   - the experience bar at the bottom fills as you read a long page, and flashes once at the end */
{const RMo=matchMedia("(prefers-reduced-motion:reduce)").matches;
 const vis=new IntersectionObserver(es=>es.forEach(e=>{const t=e.target;t.classList.toggle("zz",!e.isIntersecting);if(e.isIntersecting&&t.classList.contains("tier"))t.classList.add("seen2")}),{rootMargin:"200px 0px"});
 const rv=new IntersectionObserver(es=>{let k=0;es.forEach(e=>{if(!e.isIntersecting)return;e.target.style.setProperty("--rvi",k++);e.target.classList.add("in");rv.unobserve(e.target)})},{rootMargin:"0px 0px -40px 0px"});
 const watch=r=>{if(!r.querySelectorAll)return;
  r.querySelectorAll(".tier:not([data-zo]),.room3:not([data-zo]),.ip-art:not([data-zo]),.bcard:not([data-zo])").forEach(x=>{x.dataset.zo=1;vis.observe(x)});
  if(!RMo)r.querySelectorAll(".ip-sec:not(.rv),.gc:not(.rv),.lcard:not(.rv),.mcwin:not(.rv),.bcard:not(.rv),.navbox:not(.rv)").forEach(x=>{x.classList.add("rv");rv.observe(x)})};
 new MutationObserver(ms=>{for(const m of ms)if(m.addedNodes.length){watch(document);return}}).observe(document.documentElement,{childList:true,subtree:true});watch(document);
 const xb=document.createElement("div");xb.id="xpb";xb.setAttribute("aria-hidden","true");xb.innerHTML="<i></i>";document.body.appendChild(xb);let full=false,q=0;
 const xp=()=>{q=0;const art=document.querySelector(".ip.art"),H=document.documentElement.scrollHeight-innerHeight;
  if(!art||H<innerHeight*.5){xb.classList.remove("on");return}const f=Math.min(1,Math.max(0,scrollY/H));xb.classList.toggle("on",scrollY>40);xb.style.setProperty("--xp",f.toFixed(3));
  if(f>.995&&!full){full=true;xb.classList.remove("full");void xb.offsetWidth;xb.classList.add("full")}else if(f<.98)full=false};
 addEventListener("scroll",()=>{if(!q)q=requestAnimationFrame(xp)},{passive:true});addEventListener("hashchange",()=>setTimeout(xp,300));
 document.addEventListener("visibilitychange",()=>document.documentElement.classList.toggle("zz",document.hidden))}
