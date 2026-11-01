// Finishes the icons plan.py chose (plan.json: {id: {kind: 'flat' | 'el', png} | {kind: 'geo', geo, tex, gui, hide} |
// {kind: 'java', gui, light, draws}}): GeckoLib models and items drawn by Java renderers are drawn with
// ../geo_icon_render.html (render, renderJava) at 32 px (one slot at GUI scale 2), flat and element-model icons are
// already drawn by plan.py and copied through -> rendered.json {id: base64 png}.
// Run from the folder holding plan.json: node render.js [plan.json] [rendered.json] [size]
const fs = require('fs'), open = require('../render_page');
(async () => {
  const [inp = 'plan.json', outp = 'rendered.json', size = '32'] = process.argv.slice(2);
  const P = JSON.parse(fs.readFileSync(inp)), out = {};
  const page3d = Object.entries(P).filter(([, g]) => g.kind === 'geo' || g.kind === 'java');
  for (const [id, g] of Object.entries(P)) if (g.png) out[id] = g.png;
  if (page3d.length) {
    const { page, close } = await open('geo_icon_render.html');
    for (const [id, g] of page3d) {
      try {
        out[id] = (g.kind === 'java'
          ? await page.evaluate(([s, n]) => renderJava(s, n), [{ gui: g.gui || null, light: g.light, draws: g.draws }, +size])
          : await page.evaluate(([a, t, u, s, h]) => render(a, t, u, s, h), [g.geo, g.tex, g.gui || null, +size, g.hide || []])).split(',')[1];
      } catch (e) { console.log(id, e.message.slice(0, 160)); }
    }
    await close();
  }
  const n = k => page3d.filter(([, g]) => g.kind === k).length;
  fs.writeFileSync(outp, JSON.stringify(out)); console.log(Object.keys(out).length, 'of', Object.keys(P).length, 'drawn,', n('geo'), 'GeckoLib,', n('java'), 'Java renderers');
})();
