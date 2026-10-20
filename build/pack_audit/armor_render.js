const {chromium}=require('playwright');const fs=require('fs');(async()=>{
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--allow-file-access-from-files','--use-gl=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage();p.on('pageerror',e=>console.log('E',e.message));
await p.goto('file://'+__dirname+'/armor.html');await p.waitForFunction('window.ready');
const A=JSON.parse(fs.readFileSync(__dirname+'/../armor_in.json'));const out={};const only=process.argv[2];
for(const [id,d] of Object.entries(A)){if(id==='_steve'||(only&&!only.split(',').includes(id)))continue;try{out[id]=(await p.evaluate(([a,s])=>renderArmor(a,s),[d,A._steve])).split(',')[1]}catch(e){console.log(id,e.message)}}
fs.writeFileSync(__dirname+'/../armor_out.json',JSON.stringify(out));console.log(Object.keys(out).length);await b.close()})();
