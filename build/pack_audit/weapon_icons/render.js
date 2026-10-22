const {chromium}=require('/opt/node22/lib/node_modules/playwright');const fs=require('fs');(async()=>{
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--allow-file-access-from-files','--use-gl=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage();p.on('pageerror',e=>console.log('E',e.message));
await p.goto('file://'+__dirname+'/r.html');await p.waitForFunction('window.ready');
const P=JSON.parse(fs.readFileSync(__dirname+'/../plan.json'));const out={};let n=0;
for(const [id,g] of Object.entries(P)){try{
 if(g.kind==='geo')out[id]=(await p.evaluate(([a,t])=>render(a,t),[g.geo,g.tex])).split(',')[1];
 else if(g.kind==='el')out[id]=(await p.evaluate(([a,t,u])=>renderJava(a,t,u),[g.el,g.tex,g.gui])).split(',')[1];
 n++}catch(e){console.log(id,e.message.slice(0,120))}}
fs.writeFileSync(__dirname+'/../rendered.json',JSON.stringify(out));console.log(Object.keys(out).length,n);await b.close()})();
