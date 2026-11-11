// The English strings of every translatable area, read from the built offline file: node build/i18n/tools/domains.js <out.json>   (run from the repo root after apply_all.sh)
// Output {domain: [English...]}; todo.js, status.py and split_tm.py read it. Domains:
//   fx (a curio's effect line), src (its "how to get it" lines), st (its raw tooltip stat lines), boss (attacks, drops, summon texts), guide (the guide book), gear (attribute names the gear tables produce),
//   relic (stat names and value formats of the relic panel), names (curio, gear and boss names), ui (T() sentences are found by build/i18n/tmlib.py, not here).
const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
(async () => {
  const b = await chromium.launch(), p = await b.newPage();
  await p.goto('file://' + path.resolve('dist/Linggango_Relic_Wiki.html'), { waitUntil: 'load' }); await p.waitForTimeout(1200);
  const r = await p.evaluate(() => {
    const S = {}; const add = (d, x) => { if (typeof x === 'string' && x.trim()) (S[d] = S[d] || new Set()).add(x); };
    const walk = (d, o, n = 0) => { if (n > 8 || o == null) return; if (typeof o === 'string') add(d, o); else if (Array.isArray(o)) o.forEach(x => walk(d, x, n + 1)); else if (typeof o === 'object') Object.values(o).forEach(x => walk(d, x, n + 1)); };
    for (const d of D) { add('fx', d.fx); (d.st || []).forEach(x => add('st', x)); add('names', d.n);
      (d.src || []).forEach(x => { if (!(d.gr && RCV.test(x)) && !/^Key requirement: locked behind/i.test(x)) add('src', x); }); (d.gr ? (d.src || []).filter(x => !RCV.test(x)) : d.src || []).slice(0, 2).forEach(x => add('src', x)); }   // the lines the pages print as text (recipes are drawn as pictures)
    walk('boss', BINFO); walk('boss', SIDEB); walk('boss', SUM);
    for (const k in GUIDE) add('guide', GUIDE[k].t);
    for (const g of GE) { for (const x of gBonus(g)) { const m = x.match(/^([+\-−]?\d[\d.,]*)(%?) (.+)$/); if (m) add('gear', m[3]); } for (const [, n] of gStats(g)) add('gear', n); add('names', typeof gName === 'function' ? gName(g) : g.n || g.name); }
    for (const id in RL) for (const a of RL[id].ab) { add('relic', a.n); for (const t of a.st) { add('relic', t.n); add('relic', t.f); } }
    const o = {}; for (const k in S) o[k] = [...S[k]]; return o;
  });
  fs.writeFileSync(process.argv[2], JSON.stringify(r)); console.log(Object.entries(r).map(([k, v]) => k + ' ' + v.length).join(', ')); await b.close();
})();
