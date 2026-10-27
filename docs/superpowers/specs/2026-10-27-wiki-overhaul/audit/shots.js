const {chromium}=require('playwright'),path=require('path');
(async()=>{const b=await chromium.launch(),p=await b.newPage({viewport:{width:1440,height:900}});
await p.goto('file://'+path.resolve(process.argv[2]),{waitUntil:'load'});await p.waitForTimeout(2500);
const det=await p.evaluate(()=>{const g=s=>[...document.querySelectorAll(`a[href^="${s}"]`)].map(a=>a.getAttribute('href'));return {i:g('#i').find(h=>/^#i\d+$/.test(h)),g:null}});
for(const r of ['#','#home','#gear','#build','#bosses','#mechanics',det.i]){await p.evaluate(h=>location.hash=h,r);await p.waitForTimeout(2000);
 await p.screenshot({path:process.argv[3]+'/'+(r.replace(/[#\/]/g,'_')||'_hub')+'.png'});}
// a gear page and a keeper page
for(const pre of ['#g','#boss/']){await p.evaluate(()=>location.hash='#gear');await p.waitForTimeout(1500);
 const h=await p.evaluate(pre=>{const a=[...document.querySelectorAll(`a[href^="${pre}"]`)].map(a=>a.getAttribute('href')).find(h=>pre==='#g'?/^#g\d+$/.test(h):true);return a},pre);
 if(h){await p.evaluate(h=>location.hash=h,h);await p.waitForTimeout(2000);await p.screenshot({path:process.argv[3]+'/'+h.replace(/[#\/]/g,'_')+'.png'})}}
await b.close()})()
