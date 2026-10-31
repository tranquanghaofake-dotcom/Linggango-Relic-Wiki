// Draws the models plan.py chose (plan.json: {id: {kind: 'geo', geo, tex} | {kind: 'el', el, tex, gui}}) with
// ../geo_icon_render.html -> rendered.json. Run from the folder holding plan.json: node render.js [plan.json] [rendered.json]
const fs = require('fs'), open = require('../render_page');
(async () => {
  const [inp = 'plan.json', outp = 'rendered.json'] = process.argv.slice(2);
  const { page, close } = await open('geo_icon_render.html');
  const P = JSON.parse(fs.readFileSync(inp)), out = {};
  for (const [id, g] of Object.entries(P)) {
    try {
      if (g.kind === 'geo') out[id] = (await page.evaluate(([a, t]) => render(a, t), [g.geo, g.tex])).split(',')[1];
      else if (g.kind === 'el') out[id] = (await page.evaluate(([a, t, u]) => renderJava(a, t, u), [g.el, g.tex, g.gui])).split(',')[1];
    } catch (e) { console.log(id, e.message.slice(0, 120)); }
  }
  fs.writeFileSync(outp, JSON.stringify(out)); console.log(Object.keys(out).length, 'of', Object.keys(P).length, 'rendered'); await close();
})();
