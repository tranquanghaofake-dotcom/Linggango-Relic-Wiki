const {chromium}=require('playwright');const fs=require('fs');(async()=>{
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--allow-file-access-from-files','--use-gl=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage();p.on('pageerror',e=>console.log('E',e.message));
await p.goto('file://'+__dirname+'/r.html');await p.waitForFunction('window.ready');
const G=JSON.parse(fs.readFileSync(__dirname+'/../geo_icons.json'));const out={};
for(const [id,g] of Object.entries(G)){try{out[id]=(await p.evaluate(([a,t])=>render(a,t),[g.geo,g.tex])).split(',')[1]}catch(e){console.log(id,e.message)}}
const J=JSON.parse(fs.readFileSync(__dirname+'/../java_icons.json'));for(const [id,g] of Object.entries(J)){try{out[id]=(await p.evaluate(([a,t,u])=>renderJava(a,t,u),[g.el,g.tex,g.gui])).split(',')[1]}catch(e){console.log(id,e.message)}}
fs.writeFileSync(__dirname+'/../geo_out.json',JSON.stringify(out));console.log(Object.keys(out).length);await b.close()})();
