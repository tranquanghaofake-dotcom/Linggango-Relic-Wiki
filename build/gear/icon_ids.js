// gear ids + recipe ingredients that the v5 wiki has no icon for
const fs=require("fs"),W=process.argv[2];
const s=fs.readFileSync(__dirname+"/../../original/Linggango_Relic_Wiki.v5.html","utf8");
const data=s.match(/<script>([\s\S]*?)<\/script>/)[1].replace("window.B3=B3;","");
const IC=new Function(data+";return IC")();
const g=JSON.parse(fs.readFileSync(W+"/gear.json","utf8")),ids=new Set();
g.GE.forEach(x=>{ids.add(x.id);x.rc.forEach(r=>r.i.forEach(i=>{if(!i.startsWith("#"))ids.add(i)}))});
const need=[...ids].filter(i=>!IC[i]);fs.writeFileSync(W+"/icon_ids.json",JSON.stringify(need));console.log("icons needed",need.length);
