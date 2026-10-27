// Which elements draw pixel art at a non-integer scale, grouped by selector path, per route.
const {chromium}=require('playwright'),path=require('path');
(async()=>{const b=await chromium.launch(),p=await b.newPage({viewport:{width:1440,height:900}});
await p.goto('file://'+path.resolve(process.argv[2]),{waitUntil:'load'});await p.waitForTimeout(2500);
for(const r of process.argv.slice(3)){await p.evaluate(h=>location.hash=h,r);await p.waitForTimeout(2500);
 const out=await p.evaluate(async()=>{const sel=e=>{let s=[];for(let n=e,i=0;n&&i<3&&n!==document.body;n=n.parentElement,i++){s.unshift(n.tagName.toLowerCase()+(n.classList.length?'.'+[...n.classList].slice(0,2).join('.'):''))}return s.join('>')};
  const g={};const nat={};const load=u=>nat[u]||(nat[u]=new Promise(ok=>{const i=new Image();i.onload=()=>ok([i.naturalWidth,i.naturalHeight]);i.onerror=()=>ok(null);i.src=u}));
  for(const e of document.querySelectorAll('body *')){const rc=e.getBoundingClientRect();if(!rc.width||rc.bottom<0||rc.top>2700)continue;let s=null,nw=0;
   if(e.tagName==='IMG'&&e.naturalWidth&&e.naturalWidth<=64){nw=e.naturalWidth;s=rc.width/nw}
   else{const cs=getComputedStyle(e);const m=cs.backgroundImage.match(/url\("?(data:[^")]+)"?\)/);if(m){const n=await load(m[1]);if(n&&n[0]<=64){nw=n[0];const bs=cs.backgroundSize.split(',')[0].trim().split(' ')[0];s=bs==='auto'?1:bs.endsWith('px')?parseFloat(bs)/n[0]:bs}}}
   if(s===null)continue;const ok=typeof s==='number'&&Math.abs(s-Math.round(s))<0.02;if(ok)continue;
   const k=sel(e)+' ['+(typeof s==='number'?s.toFixed(2):s)+' of '+nw+'px]';g[k]=(g[k]||0)+1}
  return Object.entries(g).sort((a,b)=>b[1]-a[1]).slice(0,14)});
 console.log('== '+r);for(const [k,n] of out)console.log('  '+n+'  '+k)}
await b.close()})()
