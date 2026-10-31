// Finishes the icons plan.py chose (plan.json: {id: {kind: 'flat' | 'el', png} | {kind: 'geo', geo, tex, gui, hide}}):
// GeckoLib models are drawn with ../geo_icon_render.html at 32 px (one slot at GUI scale 2), flat and element-model
// icons are already drawn by plan.py and copied through -> rendered.json {id: base64 png}.
// Run from the folder holding plan.json: node render.js [plan.json] [rendered.json] [size]
const fs = require('fs'), open = require('../render_page');
(async () => {
  const [inp = 'plan.json', outp = 'rendered.json', size = '32'] = process.argv.slice(2);
  const P = JSON.parse(fs.readFileSync(inp)), out = {};
  const geo = Object.entries(P).filter(([, g]) => g.kind === 'geo');
  for (const [id, g] of Object.entries(P)) if (g.png) out[id] = g.png;
  if (geo.length) {
    const { page, close } = await open('geo_icon_render.html');
    for (const [id, g] of geo) {
      try { out[id] = (await page.evaluate(([a, t, u, s, h]) => render(a, t, u, s, h), [g.geo, g.tex, g.gui || null, +size, g.hide || []])).split(',')[1]; }
      catch (e) { console.log(id, e.message.slice(0, 160)); }
    }
    await close();
  }
  fs.writeFileSync(outp, JSON.stringify(out)); console.log(Object.keys(out).length, 'of', Object.keys(P).length, 'drawn,', geo.length, 'GeckoLib');
})();
