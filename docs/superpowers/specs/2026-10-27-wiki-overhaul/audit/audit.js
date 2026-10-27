// Read-only visual audit of the built wiki: pixel scales of images/backgrounds, colour shades, fonts, per route.
const {chromium}=require('playwright'),path=require('path'),fs=require('fs');
const FILE=process.argv[2],OUT=process.argv[3];
(async()=>{
 const b=await chromium.launch(),p=await b.newPage({viewport:{width:1440,height:900}}),errs=[];
 p.on('pageerror',e=>errs.push(e.message));
 await p.goto('file://'+path.resolve(FILE),{waitUntil:'load'}); await p.waitForTimeout(2500);
 const pick=await p.evaluate(()=>{const f=s=>{const a=[...document.querySelectorAll(`a[href^="${s}"]`)][0];return a?a.getAttribute('href'):null};return null});
 const routes=['#','#home','#gear','#build','#bosses','#mechanics','#mods'];
 const res={};
 for(const r of routes.concat(['DETAIL'])){
  let route=r;
  if(r==='DETAIL'){route=await p.evaluate(()=>{const a=[...document.querySelectorAll('a[href^="#i"]')].map(x=>x.getAttribute('href')).filter(h=>/^#i\d+$/.test(h));return a[0]||'#i1'})}
  await p.evaluate(h=>{location.hash=h},route); await p.waitForTimeout(1800);
  res[route]=await p.evaluate(async()=>{
   const vis=e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&r.bottom>0&&r.top<innerHeight*3};
   const els=[...document.querySelectorAll('body *')].filter(vis);
   const scales={},smooth=[],nat={};
   const load=u=>nat[u]||(nat[u]=new Promise(ok=>{const i=new Image();i.onload=()=>ok([i.naturalWidth,i.naturalHeight]);i.onerror=()=>ok(null);i.src=u}));
   for(const e of els){
     const cs=getComputedStyle(e),pix=/pixelated|crisp-edges/.test(cs.imageRendering);
     if(e.tagName==='IMG'&&e.naturalWidth){const s=+(e.getBoundingClientRect().width/e.naturalWidth).toFixed(2);const k=(e.naturalWidth<=64?'small ':'big ')+s;scales[k]=(scales[k]||0)+1;if(!pix&&e.naturalWidth<=64)smooth.push(e.className||e.tagName)}
     const bg=cs.backgroundImage.match(/url\("?([^")]+)"?\)/);
     if(bg&&cs.backgroundSize&&bg[1].startsWith('data:')){
       const n=await load(bg[1]); if(!n)continue;
       let bs=cs.backgroundSize.split(',')[0].trim().split(' ')[0];
       let s=bs==='auto'?1:bs.endsWith('px')?parseFloat(bs)/n[0]:bs==='cover'||bs==='contain'||bs.endsWith('%')?'fit':'?';
       if(typeof s==='number')s=+s.toFixed(2);
       const k=(n[0]<=64?'small-bg ':'big-bg ')+s;scales[k]=(scales[k]||0)+1;
       if(!pix&&n[0]<=64&&s!==1)smooth.push('bg:'+(e.className||e.tagName))}
   }
   const col={},fonts={};
   for(const e of els){const cs=getComputedStyle(e);for(const c of[cs.color,cs.backgroundColor,cs.borderTopColor]){if(c&&!/rgba\(0, 0, 0, 0\)/.test(c))col[c]=(col[c]||0)+1}
     fonts[cs.fontFamily.split(',')[0]+' '+cs.fontSize]=(fonts[cs.fontFamily.split(',')[0]+' '+cs.fontSize]||0)+1}
   const rgb=c=>c.match(/[\d.]+/g).slice(0,3).map(Number),cl=Object.keys(col);let near=0;const pairs=[];
   for(let i=0;i<cl.length;i++)for(let j=i+1;j<cl.length;j++){const a=rgb(cl[i]),b=rgb(cl[j]);const d=Math.hypot(a[0]-b[0],a[1]-b[1],a[2]-b[2]);if(d>0&&d<12){near++;if(pairs.length<12)pairs.push([cl[i],cl[j]])}}
   return {elements:els.length,scales,smoothSmallPixelArt:smooth.length,smoothSample:[...new Set(smooth)].slice(0,8),colours:cl.length,nearDuplicatePairs:near,nearSample:pairs,fonts:Object.keys(fonts).length,fontSample:Object.entries(fonts).sort((a,b)=>b[1]-a[1]).slice(0,10)}
  });
 }
 res.errors=errs.slice(0,10); fs.writeFileSync(OUT,JSON.stringify(res,null,1)); await b.close();
})();
