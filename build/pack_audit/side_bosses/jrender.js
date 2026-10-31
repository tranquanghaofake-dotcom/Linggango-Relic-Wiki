// Drives jrender.html: renders every model in IN (jmodel.py output joined with its texture: {name: {model, tex, yaw?}})
// and writes OUT {name: base64 png}. Usage: node jrender.js IN OUT   (npm install --no-package-lock --prefix build first; see ../render_page.js)
const fs = require('fs'), open = require('../render_page');
(async () => {
  const [inp, outp] = process.argv.slice(2).slice(-2);   // an older call passed a DIR first: ignored, the page is opened in place
  const { page, close } = await open('side_bosses/jrender.html');
  const IN = JSON.parse(fs.readFileSync(inp)), out = {};
  for (const [k, v] of Object.entries(IN)) {
    try { out[k] = (await page.evaluate(([m, t, y]) => renderJava(m, t, y), [v.model, v.tex, v.yaw ?? -0.55])).split(',')[1]; }
    catch (e) { console.log(k, e.message); }
  }
  fs.writeFileSync(outp, JSON.stringify(out)); console.log(Object.keys(out).length, 'of', Object.keys(IN).length, 'rendered'); await close();
})();
