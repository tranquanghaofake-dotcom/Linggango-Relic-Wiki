const {chromium}=require('playwright'),path=require('path'),fs=require('fs');
(async()=>{const b=await chromium.launch(),css=fs.readFileSync(process.argv[3],'utf8');
for(const [mode,inject] of [['before',false],['after',true]]){const p=await b.newPage({viewport:{width:1440,height:900}});
 await p.goto('file://'+path.resolve(process.argv[2]));await p.waitForTimeout(2500);if(inject)await p.addStyleTag({content:css});
 for(const r of ['#gear','#i76','#']){await p.evaluate(h=>location.hash=h,r);await p.waitForTimeout(3000);await p.screenshot({path:process.argv[4]+'/'+mode+(r.replace(/[#\/]/g,'_')||'_hub')+'.png'})}
 await p.close()}
await b.close()})()
