// Drives geo_icon_render.html: GeckoLib item models (IN_GEO {id: {geo, tex}}) and JSON element models
// (IN_JAVA {id: {el, tex, gui}}) drawn as inventory icons -> OUT {id: base64 png}. Run from the work dir:
//   node build/pack_audit/geo_icon_render.js [geo_icons.json] [java_icons.json] [geo_out.json]   (bash build/fx3d_build.sh --check first: it installs three)
const fs = require('fs'), open = require('./render_page');
(async () => {
  const [gi = 'geo_icons.json', ji = 'java_icons.json', outp = 'geo_out.json'] = process.argv.slice(2);
  const { page, close } = await open('geo_icon_render.html'); const out = {};
  const G = fs.existsSync(gi) ? JSON.parse(fs.readFileSync(gi)) : {}, J = fs.existsSync(ji) ? JSON.parse(fs.readFileSync(ji)) : {};
  for (const [id, g] of Object.entries(G)) { try { out[id] = (await page.evaluate(([a, t]) => render(a, t), [g.geo, g.tex])).split(',')[1]; } catch (e) { console.log(id, e.message); } }
  for (const [id, g] of Object.entries(J)) { try { out[id] = (await page.evaluate(([a, t, u]) => renderJava(a, t, u), [g.el, g.tex, g.gui])).split(',')[1]; } catch (e) { console.log(id, e.message); } }
  fs.writeFileSync(outp, JSON.stringify(out)); console.log(Object.keys(out).length, 'of', Object.keys(G).length + Object.keys(J).length, 'rendered'); await close();
})();
