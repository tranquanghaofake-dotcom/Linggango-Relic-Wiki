// Drives armor_render.html: each armor set of armor_in.json (from armor_prep.py; "_steve" is the base skin) worn by a
// player model -> armor_out.json {id: base64 png}. Run from the work dir:
//   node build/pack_audit/armor_render.js [id,id,...] [armor_in.json] [armor_out.json]   (bash build/fx3d_build.sh --check first: it installs three)
const fs = require('fs'), open = require('./render_page');
(async () => {
  const [only, inp = 'armor_in.json', outp = 'armor_out.json'] = process.argv.slice(2);
  const { page, close } = await open('armor_render.html');
  const A = JSON.parse(fs.readFileSync(inp)), out = {};
  for (const [id, d] of Object.entries(A)) {
    if (id === '_steve' || (only && only !== '-' && !only.split(',').includes(id))) continue;
    try { out[id] = (await page.evaluate(([a, s]) => renderArmor(a, s), [d, A._steve])).split(',')[1]; } catch (e) { console.log(id, e.message); }
  }
  fs.writeFileSync(outp, JSON.stringify(out)); console.log(Object.keys(out).length, 'rendered'); await close();
})();
