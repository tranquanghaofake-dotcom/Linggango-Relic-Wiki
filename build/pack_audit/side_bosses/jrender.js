// Drives jrender.html: renders every model in IN (renders.py's jm_in.json: {name: {model, tex, alpha}}) at 256 px with the
// Keepers' framing and writes OUT {name: base64 png}. Usage: node jrender.js IN OUT [name|name...] (names hold commas)
// (npm install --no-package-lock --prefix build first; see ../render_page.js)
const fs = require('fs'), open = require('../render_page');
(async () => {
  const [inp, outp, only] = process.argv.slice(2);
  const { page, close } = await open('side_bosses/jrender.html');
  const IN = JSON.parse(fs.readFileSync(inp)), out = {}, sel = only ? only.split('|') : null;
  for (const [k, v] of Object.entries(IN)) {
    if (sel && !sel.includes(k)) continue;
    try { out[k] = (await page.evaluate(([m, t, a]) => renderJava(m, t, a), [v.model, v.tex, v.alpha])).split(',')[1]; }
    catch (e) { console.log(k, e.message); }
  }
  fs.writeFileSync(outp, JSON.stringify(out)); console.log(Object.keys(out).length, 'of', Object.keys(IN).length, 'rendered'); await close();
})();
