// Draws every Keeper in build/patches/boss_models.json with boss_portraits.html and writes build/patches/boss_portraits.json
// {key: base64 png}; then `python3 -I build/pack_audit/mcassets.py --repack build/patches/boss_portraits.json` and
// `bash build/patches/apply_all.sh`. Usage: node build/pack_audit/boss_portraits.js [key,key,...] [--in MODELS.json --out PICS.json]
// (--in/--out: other records of the same format, such as the GeckoLib side bosses from side_bosses/bgeo.py; the output is merged too)
// (npm install in build/ first: render_page.js says how). The models come from the boss model extraction (B3, moved out
// of data.js on 2026-10-31: the page shows these pictures and no longer carries the models or three.js).
const fs = require('fs'), path = require('path'), open = require('./render_page');
(async () => {
  const a = process.argv.slice(2), opt = f => { const i = a.indexOf(f); return i < 0 ? null : a.splice(i, 2)[1]; }, inF = opt('--in'), outF = opt('--out');
  const P = path.resolve(__dirname, '..', 'patches'), only = a[0] ? a[0].split(',') : null;
  const M = JSON.parse(fs.readFileSync(inF || path.join(P, 'boss_models.json'))), F = outF || path.join(P, 'boss_portraits.json');
  const out = fs.existsSync(F) ? JSON.parse(fs.readFileSync(F)) : {};
  const { page, close } = await open('boss_portraits.html');
  for (const [k, rec] of Object.entries(M)) {
    if (only && !only.includes(k)) continue;
    try { out[k] = (await page.evaluate(r => portrait(r), rec)).split(',')[1]; } catch (e) { console.log(k, e.message); }
  }
  fs.writeFileSync(F, JSON.stringify(out, Object.keys(out).sort()));
  console.log(Object.keys(out).length, 'portraits'); await close();
})();
