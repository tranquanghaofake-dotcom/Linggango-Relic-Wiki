// Draws every Keeper in build/patches/boss_models.json with boss_portraits.html and writes build/patches/boss_portraits.json
// {key: base64 png}; then `python3 -I build/pack_audit/mcassets.py --repack build/patches/boss_portraits.json` and
// `bash build/patches/apply_all.sh`. Usage: node build/pack_audit/boss_portraits.js [key,key,...] [--in MODELS.json --out PICS.json]
// (--in/--out: other records of the same format, such as the GeckoLib side bosses from side_bosses/bgeo.py; the output is merged too)
// --figs draws the home page's staircase figures instead (boss_figs.json; see below).
// (npm install in build/ first: render_page.js says how). The models come from the boss model extraction (B3, moved out
// of data.js on 2026-10-31: the page shows these pictures and no longer carries the models or three.js).
const fs = require('fs'), path = require('path'), open = require('./render_page');
(async () => {
  const a = process.argv.slice(2), opt = f => { const i = a.indexOf(f); return i < 0 ? null : a.splice(i, 2)[1]; }, inF = opt('--in'), outF = opt('--out');
  const P = path.resolve(__dirname, '..', 'patches'), only = a[0] ? a[0].split(',') : null;
  const M = JSON.parse(fs.readFileSync(inF || path.join(P, 'boss_models.json'))), F = outF || path.join(P, 'boss_portraits.json');
  const out = fs.existsSync(F) ? JSON.parse(fs.readFileSync(F)) : {};
  const { page, close } = await open('boss_portraits.html');
  // --figs: the figures of The climb (the home page's staircase) -> build/patches/boss_figs.json {key: {src, w, h, n, ms, z}}:
  // a strip of the idle loop per Keeper of The Path (app.js NEXTB), framed on the feet (boss_portraits.html figure), drawn
  // at twice the size it is shown (z = shown px per strip px). Size rule: a boss of MED blocks is CSSH px tall on the page;
  // the others follow the square root of their in-game height (so Arion at 3.1 blocks and Sanghor at 6.8 differ, but not by
  // 2.2 times), within LO..HI, and no frame is wider than MAXW (the Ender Dragon's wings). The last Act has no Keeper: its
  // step shows the Act's end-game boss from STILL (a finished side-boss picture, no loop).
  if (a.includes('--figs')) {
    const PATH = ['iron_colossus', 'goblin_lord', 'arion', 'eldorath', 'zoranth_forgotten', 'ender_dragon', 'elvenite_paladin', 'vaedric', 'discord', 'sanghor', 'zoranth_newborn', 'nyxaris'];
    const STILL = { apollyon: ['side_imgs.json', 'Apollyon'] }, SRC = 2, CSSH = 176, MED = 4.8, LO = 0.8, HI = 1.25, MAXW = 520, PPU = 40, figs = {};
    for (const k of PATH) { const rec = M[k]; if (!rec) { console.log(k, 'has no model'); process.exitCode = 1; continue; }
      const m = await page.evaluate(([r, o]) => figure(r, o), [rec, { ppu: PPU, type: 'image/webp' }]);
      let fit = SRC * CSSH * Math.min(HI, Math.max(LO, Math.sqrt(m.blocks / MED))) / (m.blocks * PPU); if (m.w * fit > MAXW) fit = MAXW / m.w;
      const r = await page.evaluate(([r, o]) => figure(r, o), [rec, { ppu: PPU, fit, type: 'image/webp' }]);
      figs[k] = { src: 'data:image/webp;base64,' + r.png, w: r.w, h: r.h, n: r.n, ms: r.ms, z: 1 / SRC };
      console.log(k.padEnd(18), `${r.w}x${r.h} x${r.n}`, `${m.blocks} blocks`, (r.png.length / 1024).toFixed(0) + ' kB'); }
    for (const [k, [f, name]] of Object.entries(STILL)) { const r = await page.evaluate(u => still(u), JSON.parse(fs.readFileSync(path.join(P, f)))[name]);
      figs[k] = { src: 'data:image/png;base64,' + r.png, w: r.w, h: r.h, n: 1, ms: 0, z: +(CSSH / r.h).toFixed(3) }; console.log(k.padEnd(18), `${r.w}x${r.h} still`); }
    fs.writeFileSync(path.join(P, 'boss_figs.json'), JSON.stringify(figs)); console.log(Object.keys(figs).length, 'figures,', (fs.statSync(path.join(P, 'boss_figs.json')).size / 1e6).toFixed(2), 'MB'); await close(); return;
  }
  for (const [k, rec] of Object.entries(M)) {
    if (only && !only.includes(k)) continue;
    try { out[k] = (await page.evaluate(r => portrait(r), rec)).split(',')[1]; } catch (e) { console.log(k, e.message); }
  }
  fs.writeFileSync(F, JSON.stringify(out, Object.keys(out).sort()));
  console.log(Object.keys(out).length, 'portraits'); await close();
})();
