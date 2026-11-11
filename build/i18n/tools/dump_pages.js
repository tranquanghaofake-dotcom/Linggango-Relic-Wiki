// node build/i18n/tools/dump_pages.js <index.html> <out.json> [lang]: <main> HTML of a spread of curio pages (relic, stacking tags, ladder, elements, damage types, config values), incl. the relic panel opened
const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
(async () => {
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  await p.goto('file://' + path.resolve(process.argv[2]) + (process.argv[4] ? '?lang=' + process.argv[4] : ''), { waitUntil: 'load' }); await p.waitForTimeout(1500);
  const picks = await p.evaluate(() => {
    const pick = [], add = f => { const l = D.filter(d => { try { return f(d) } catch (e) { return false } }); for (const d of l.slice(0, 3)) if (!pick.includes(d.ix)) pick.push(d.ix); };
    add(d => RL[d.id]); add(d => SK.i[d.id] && SK.i[d.id].s === 'y'); add(d => SK.i[d.id] && SK.i[d.id].s === 'n'); add(d => SK.i[d.id] && SK.i[d.id].s === 'u'); add(d => SK.i[d.id] && SK.i[d.id].s === 'p');
    add(d => SK.i[d.id] && SK.i[d.id].l); add(d => SK.i[d.id] && SK.i[d.id].l && SK.i[d.id].l[2]); add(d => KP && 0); add(d => d.gk); add(d => d.rq); add(d => isMust(d)); add(d => evo().from[d.id]); add(d => (evo().to[d.id] || []).length); add(d => d.g === 'Loot'); add(d => d.pe);
    for (let i = 0; i < 12; i++) if (D[i * 20] && !pick.includes(D[i * 20].ix)) pick.push(D[i * 20].ix);
    return pick;
  });
  const out = {};
  for (const ix of picks) {
    await p.evaluate(h => { location.hash = h }, '#i' + ix); await p.waitForTimeout(250);
    out['i' + ix] = await p.evaluate(() => { const m = document.querySelector('main'); return m.innerHTML.replace(/data:image\/[a-z]+;base64,[A-Za-z0-9+\/=]+/g, 'DATA').replace(/blob:null\/[0-9a-f-]+/g, 'BLOB').replace(/class="([^"]*)"/g, (x, c) => 'class="' + c.split(/\s+/).filter(y => !/^(seen|seen2|in)$/.test(y)).sort().join(' ') + '"') });
    // relic panel: open it and move the sliders once so the interactive HTML is covered
    const has = await p.evaluate(() => { const r = document.querySelector('[data-rlv]'); return !!r });
    if (has) { await p.evaluate(() => { const r = document.querySelector('[data-rlv]'); r.value = Math.max(1, Math.floor(r.max / 2)); r.dispatchEvent(new Event('input', { bubbles: true })) }); await p.waitForTimeout(200);
      out['i' + ix + 'rl'] = await p.evaluate(() => document.querySelector('main').innerHTML.replace(/data:image\/[a-z]+;base64,[A-Za-z0-9+\/=]+/g, 'DATA').replace(/blob:null\/[0-9a-f-]+/g, 'BLOB').replace(/class="([^"]*)"/g, (x, c) => 'class="' + c.split(/\s+/).filter(y => !/^(seen|seen2|in)$/.test(y)).sort().join(' ') + '"')) }
  }
  fs.writeFileSync(process.argv[3], JSON.stringify(out)); console.log('pages dumped:', Object.keys(out).length, '(relic panels:', Object.keys(out).filter(k => k.endsWith('rl')).length + ')'); await b.close();
})();
