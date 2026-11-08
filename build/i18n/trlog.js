// Lists every sentence the pages ask T() / TN() for, so the ones built from variables (an Act's description, a boss's name in a sentence) are known too.
// Usage: NODE_PATH=$(npm root -g) node build/i18n/trlog.js [dist/Linggango_Relic_Wiki.html]   -> writes build/i18n/tr_log.json (build.py counts these as sentences to translate)
// Run it after a change to the pages it covers; it only adds what a visit shows, so a page that is not in ROUTES below is not listed.
const path = require('path'), fs = require('fs');
const { chromium } = (() => { try { return require('playwright'); } catch { return require(path.join(require('child_process').execSync('npm root -g').toString().trim(), 'playwright')); } })();
const ROUTES = ['#', '#act/99', '#i5', '#g12', '#gs3', '#boss/iron_colossus', '#bosses', '#mechanics', '#changes', '#home'];   // Acts are added from ORDER
(async () => {
  const b = await chromium.launch(), seen = new Set();
  for (const here of [null, 3]) {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' }), p = await ctx.newPage();
    await p.addInitScript(h => { window.__TRLOG = new Set(); try { localStorage.clear(); if (h !== null) localStorage.setItem('lgw-here', String(h)); } catch (e) {} }, here);
    await p.goto('file://' + path.resolve(process.argv[2] || 'dist/Linggango_Relic_Wiki.html'), { waitUntil: 'load' }); await p.waitForTimeout(1200);
    const acts = await p.evaluate(() => ORDER.filter(x => x !== -1 || D.some(d => d.t === -1)));
    for (const r of [...ROUTES, ...acts.map(a => '#act/' + a)]) { await p.evaluate(h => { location.hash = h; render(); }, r); await p.waitForTimeout(250); }
    await p.evaluate(() => { location.hash = ''; render(); }); await p.waitForTimeout(300);
    for (const n of await p.$$('#pmap .pn')) { await n.click(); await p.waitForTimeout(150); }   // every Act's panel on the hub
    for (const h of await p.$$('#pmap .phere')) { await h.click({ force: true }).catch(() => {}); }
    (await p.evaluate(() => [...window.__TRLOG])).forEach(x => seen.add(x));
    await ctx.close();
  }
  await b.close();
  const out = [...seen].sort();
  fs.writeFileSync(path.join(__dirname, 'tr_log.json'), '[\n' + out.map(x => JSON.stringify(x)).join(',\n') + '\n]\n');
  console.log(out.length + ' sentences written to build/i18n/tr_log.json');
})();
