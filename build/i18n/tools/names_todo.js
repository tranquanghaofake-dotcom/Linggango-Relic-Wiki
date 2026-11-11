// node build/i18n/tools/names_todo.js [dist.html] [out.json]: the item names (curios, gear, sets, and every item a recipe, ritual or table names) that have no entry in the translation memory of some language.
// Writes the English names as a JSON array (the "list" merge.py takes) and prints the counts per language; a name decided to stay English has an entry too ("=" in a batch file), so it is not listed.
// After a game or pack update: build, run this, then adopt_vanilla.py (the game's own names), then translate the rest in batches:  python3 build/i18n/tools/names_show.py <list> <from> <to>,
// write `index|vi|ru|pt|es` lines and  python3 build/i18n/tools/merge.py --domain names <list> <batch.txt>  (docs/I18N.md).
const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
(async () => {
  const html = process.argv[2] || 'dist/Linggango_Relic_Wiki.html', out = process.argv[3] || '/tmp/i18n-status/names_todo.json';
  const b = await chromium.launch(), p = await b.newPage(); await p.goto('file://' + path.resolve(html), { waitUntil: 'load' }); await p.waitForTimeout(1500);
  const r = await p.evaluate(() => { const all = new Set([...D.map(d => d.n), ...(typeof GE !== 'undefined' ? GE.map(g => g.n) : []), ...(typeof GS !== 'undefined' ? GS.map(s => s.n) : []), ...Object.values(NM)]);
    const per = {}; for (const c of ['vi', 'ru', 'pt', 'es']) per[c] = [...all].filter(n => !/creative only/i.test(n) && I18N[c].tr[hsh(n)] === undefined && !(I18N[c].keep || []).includes(n));
    return { total: all.size, per }; });
  const union = [...new Set(Object.values(r.per).flat())].sort();
  fs.mkdirSync(path.dirname(out), { recursive: true }); fs.writeFileSync(out, JSON.stringify(union));
  console.log(r.total + ' names; with no entry: ' + Object.entries(r.per).map(([c, v]) => c + ' ' + v.length).join(', ') + '; ' + union.length + ' different names -> ' + out);
  await b.close();
})();
