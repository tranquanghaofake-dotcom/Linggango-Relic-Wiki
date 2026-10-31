// Drives geo_icon_render.html: GeckoLib item models (IN {id: {geo, tex, gui, hide}}: tex a base64 PNG, gui the item JSON's
// display.gui) drawn as the inventory slot shows them -> OUT {id: base64 png}. JSON element models are drawn by
// block_render.py (render_model) instead. Run from the work dir:
//   node build/pack_audit/geo_icon_render.js [geo_icons.json] [geo_out.json] [size=32]   (npm install --no-package-lock --prefix build first: it installs three)
const fs = require('fs'), open = require('./render_page');
(async () => {
  const [gi = 'geo_icons.json', outp = 'geo_out.json', size = '32'] = process.argv.slice(2);
  const { page, close } = await open('geo_icon_render.html'); const out = {};
  const G = JSON.parse(fs.readFileSync(gi));
  for (const [id, g] of Object.entries(G)) {
    try { out[id] = (await page.evaluate(([a, t, u, s, h]) => render(a, t, u, s, h), [g.geo, g.tex, g.gui || null, +size, g.hide || []])).split(',')[1]; }
    catch (e) { console.log(id, e.message); }
  }
  fs.writeFileSync(outp, JSON.stringify(out)); console.log(Object.keys(out).length, 'of', Object.keys(G).length, 'rendered'); await close();
})();
