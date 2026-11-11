// What is still English: node build/i18n/tools/todo.js <out.json> [lang ...]   (run from the repo root after apply_all.sh; default: all four languages)
// For each language and domain (see domains.js) the strings with no translation in the pack and not in the glossary's names. Prints the counts and writes {lang: {domain: [English...]}}.
//   fx, boss, guide, gear, relic, names  a string with no pack entry
//   st                                   a stat line that stT leaves as it is and that has no pack entry
//   src                                  a source line that srcT leaves as it is
// Lines without a word of three letters ("?/?", "+2") and boss strings of fewer than three words (names) are not listed. Feed the lists to a translation batch, then tools/merge.py.
const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
(async () => {
  const [, , out, ...langs] = process.argv; const L = langs.length ? langs : ['vi', 'ru', 'pt', 'es'];
  const b = await chromium.launch(), p = await b.newPage();
  await p.goto('file://' + path.resolve('dist/Linggango_Relic_Wiki.html'), { waitUntil: 'load' }); await p.waitForTimeout(1200);
  const dom = JSON.parse(fs.readFileSync(path.join(path.dirname(out), 'domains.json'), 'utf8'));
  const res = await p.evaluate(([dom, L]) => { const R = {};
    for (const c of L) { useLang(c); const keep = new Set(I18N[c].keep || []); R[c] = {};
      for (const d in dom) { R[c][d] = dom[d].filter(s => /[A-Za-z]{3}/.test(s) && !keep.has(s) && I18N[c].tr[hsh(s)] === undefined && (d !== 'boss' || s.trim().split(/\s+/).length >= 3)
        && (d !== 'st' || stT(s) === s) && (d !== 'src' || srcT(s) === s)); } }
    useLang('en'); return R; }, [dom, L]);
  fs.writeFileSync(out, JSON.stringify(res)); for (const c of L) console.log(c, Object.entries(res[c]).map(([d, v]) => d + ' ' + v.length).join(', ')); await b.close();
})();
