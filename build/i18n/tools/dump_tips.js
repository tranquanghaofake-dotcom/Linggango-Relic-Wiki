// node build/i18n/tools/dump_tips.js <index.html> <out.json>: the tooltip HTML of a spread of curios (plain, Keeper-gated, ring-gated, Must-Have, evolving, relic)
const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
(async () => {
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  await p.goto('file://' + path.resolve(process.argv[2]), { waitUntil: 'load' }); await p.waitForTimeout(1500);
  const out = await p.evaluate(() => {
    const pick = [];
    const add = f => { const d = D.find(f); if (d && !pick.includes(d)) pick.push(d); };
    add(d => true); add(d => d.gk); add(d => d.rq); add(d => isMust(d)); add(d => evo().from[d.id]); add(d => (evo().to[d.id] || []).length); add(d => RL[d.id]); add(d => d.pe); add(d => d.a !== d.t); add(d => d.g === 'Loot');
    for (const d of D.slice(0, 40)) if (pick.length < 40) pick.push(d);
    const r = {};
    for (const d of pick) { const n = document.createElement('a'); n.dataset.t = String(d.ix); document.body.appendChild(n); TIPC.clear(); showTipBase(n);
      r[d.ix] = document.getElementById('tip').innerHTML.replace(/data:image\/[a-z]+;base64,[A-Za-z0-9+\/=]+/g, 'DATA').replace(/blob:null\/[0-9a-f-]+/g, 'BLOB').replace(/ style="[^"]*"/g, ''); n.remove(); }
    return r;
  });
  fs.writeFileSync(process.argv[3], JSON.stringify(out)); console.log('tooltips dumped:', Object.keys(out).length); await b.close();
})();
