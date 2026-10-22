// Page check for the built wiki (Chromium, no network).
// Usage: NODE_PATH=$(npm root -g) node build/check.js [dist/Linggango_Relic_Wiki.html]
// Fails (exit 1) on: a script error, an empty gear item or set page, a broken <img> on those pages,
// or a boss card on The Path (home page) with no landscape background.
const { chromium } = require('playwright'), path = require('path');
(async () => {
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1400, height: 900 } });
  const errs = [], bad = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.resolve(process.argv[2] || 'dist/Linggango_Relic_Wiki.html'), { waitUntil: 'load' });
  await p.waitForTimeout(2500);
  const cards = await p.evaluate(() => [...document.querySelectorAll('.pbc')].map(a => [a.querySelector('b')?.textContent, !!a.querySelector('img.bg') || /url/.test(a.getAttribute('style') || '')]));
  const noBg = cards.filter(c => !c[1]).map(c => c[0]);
  const [ne, ns] = await p.evaluate(() => [GE.length, GS.length]);
  for (const [pre, n] of [['#g', ne], ['#gs', ns]])
    for (let i = 0; i < n; i++) {
      const r = await p.evaluate(h => { location.hash = h; render(); const m = document.getElementById('main'); return [m.innerText.length, [...m.querySelectorAll('img')].filter(x => x.complete && x.naturalWidth === 0).length]; }, pre + i);
      if (r[0] < 40 || r[1]) bad.push(pre + i);
    }
  console.log(`path cards ${cards.length}, without background: ${noBg.length} ${noBg.join(', ')}`);
  console.log(`gear pages ${ne}, sets ${ns}, empty or broken: ${bad.length} ${bad.slice(0, 10).join(' ')}`);
  console.log(`script errors: ${errs.length} ${errs.slice(0, 3).join(' | ')}`);
  await b.close();
  process.exit(errs.length || bad.length || noBg.length || !cards.length ? 1 : 0);
})();
