// The i18n invariants (build/checks/i18n.js) on the built offline file in about 15 seconds, instead of the 6 minutes of check.js. Run from the repo root after apply_all.sh:
//   NODE_PATH=$(npm root -g) node build/i18n/tools/inv.js            prints the problems (an empty list is clean) and exits 1 if any
//   NODE_PATH=$(npm root -g) node build/i18n/tools/inv.js --faults   also checks that the invariants catch deleted translations (they should print problems)
const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
(async () => {
  const body = fs.readFileSync('build/checks/i18n.js', 'utf8');
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1400, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.resolve('dist/Linggango_Relic_Wiki.html'), { waitUntil: 'load' }); await p.waitForTimeout(1500);
  const run = () => p.evaluate(async b => { const bad = []; const AF = Object.getPrototypeOf(async function () {}).constructor; await new AF('bad', b)(bad); return bad; }, body);
  const bad = await run(); console.log('i18n invariants ->', bad.length ? bad.join('\n  ') : 'clean');
  if (process.argv.includes('--faults')) {
    await p.evaluate(() => { delete I18N.ru.tr[hsh('Melee')]; }); const f1 = await run(); console.log('fault 1 (a deleted translation) caught:', f1.length > 0);
    await p.evaluate(() => { delete I18N.es.tr[hsh('Hardest ingredient: {a}')]; }); const f2 = await run(); console.log('fault 2 (a deleted source template) caught:', f2.some(x => /source line/.test(x)));
  }
  console.log('script errors:', errs.length); await b.close(); process.exit(bad.length || errs.length ? 1 : 0);
})();
