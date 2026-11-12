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
  // --figs: the figures of The climb (the home page's staircase) -> build/patches/boss_figs.json {key: {src, w, h, bw, n, ms, z, fly?}}
  // and build/patches/boss_walks.json {key: {src, w, h, n, ms}}: per Keeper of The Path (app.js NEXTB) a strip of its idle loop
  // and one of its walk loop (boss_portraits.html figure: same centre line and ground, each cut to its own pixels), drawn at
  // twice the size it is shown (z = shown px per strip px), every boss from the same view (YAW: a boss turned further looks
  // askew beside the others). bw is the body's width (the page keeps bodies, not sword tips, over their own step).
  // Size rule: a boss of MED blocks is CSSH px tall on the page; the others follow the square root of their in-game height
  // (so Arion at 3.1 blocks and Sanghor at 6.8 differ, but not by 2.2 times), within LO..HI, and no frame is wider than MAXW.
  // OPT: the Ender Dragon flies (the page lifts it behind its neighbours; no ground, its frame is its lowest pixel) and is seen from
  // its own side (yaw 210: head to the right, as if climbing the stairs; seen from the front it is a flat black wedge).
  // The last Act has no Keeper: its step shows the Act's end-game boss from STILL (a finished side-boss picture, no loop).
  if (a.includes('--figs')) {
    const PATH = ['iron_colossus', 'goblin_lord', 'arion', 'eldorath', 'zoranth_forgotten', 'ender_dragon', 'elvenite_paladin', 'vaedric', 'discord', 'sanghor', 'zoranth_newborn', 'nyxaris'];
    const OPT = { ender_dragon: { fly: 1, size: 1.2, maxw: 350, yaw: 210, pitch: 15 } };
    const STILL = { apollyon: ['side_imgs.json', 'Apollyon'] }, SRC = 2, CSSH = 176, MED = 4.8, LO = 0.95, HI = 1.2, MAXW = 520, PPU = 40, YAW = 0, ANIMS = ['idle', 'walk'], figs = {}, walks = {};
    const fig = (rec, o) => page.evaluate(([r, o]) => figure(r, o), [rec, { ppu: PPU, yaw: YAW, anims: ANIMS, type: 'image/webp', ...o }]);
    for (const k of PATH) { const rec = M[k], o = OPT[k] || {}; if (!rec) { console.log(k, 'has no model'); process.exitCode = 1; continue; }
      const v = { fly: !!o.fly, ...(o.yaw != null && { yaw: o.yaw }), ...(o.pitch != null && { pitch: o.pitch }) }, m = await fig(rec, { ...v, frames: 6, measure: true }), mw = o.maxw || MAXW;
      let fit = (o.size || 1) * SRC * CSSH * Math.min(HI, Math.max(LO, Math.sqrt(m.blocks / MED))) / (m.blocks * PPU); if (m.strips.idle.w * fit > mw) fit = mw / m.strips.idle.w;
      const r = await fig(rec, { ...v, fit }), i = r.strips.idle, w = r.strips.walk;
      figs[k] = { src: 'data:image/webp;base64,' + i.png, w: i.w, h: i.h, bw: i.bw, n: i.n, ms: i.ms, z: 1 / SRC }; if (o.fly) figs[k].fly = 1;
      if (w) walks[k] = { src: 'data:image/webp;base64,' + w.png, w: w.w, h: w.h, n: w.n, ms: w.ms };
      console.log(k.padEnd(18), `idle ${i.w}x${i.h} body ${i.bw} ${(i.png.length / 1024).toFixed(0)} kB`, w ? `walk ${w.w}x${w.h} ${(w.png.length / 1024).toFixed(0)} kB` : 'no walk', `${m.blocks} blocks`); }
    for (const [k, [f, name]] of Object.entries(STILL)) { const r = await page.evaluate(u => still(u), JSON.parse(fs.readFileSync(path.join(P, f)))[name]);
      figs[k] = { src: 'data:image/png;base64,' + r.png, w: r.w, h: r.h, bw: r.w, n: 1, ms: 0, z: +(CSSH / r.h).toFixed(3) }; console.log(k.padEnd(18), `${r.w}x${r.h} still`); }
    for (const [f, o] of [['boss_figs.json', figs], ['boss_walks.json', walks]]) { fs.writeFileSync(path.join(P, f), JSON.stringify(o)); console.log(f, Object.keys(o).length, 'records,', (fs.statSync(path.join(P, f)).size / 1e6).toFixed(2), 'MB'); }
    await close(); return;
  }
  for (const [k, rec] of Object.entries(M)) {
    if (only && !only.includes(k)) continue;
    try { out[k] = (await page.evaluate(r => portrait(r), rec)).split(',')[1]; } catch (e) { console.log(k, e.message); }
  }
  fs.writeFileSync(F, JSON.stringify(out, Object.keys(out).sort()));
  console.log(Object.keys(out).length, 'portraits'); await close();
})();
