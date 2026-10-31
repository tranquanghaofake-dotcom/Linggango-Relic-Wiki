// Page check for the built wiki (Chromium, no network).
// Usage: NODE_PATH=$(npm root -g) node build/check.js [dist/Linggango_Relic_Wiki.html]
// Fails (exit 1) on: a script error, an empty gear item or set page, a broken <img> on any detail page (curio, gear,
// set, boss, side boss: each picture is awaited with decode(), since a fresh <img> is not complete in the task that
// inserts it), a boss card on The Path (home page) with no landscape background, or a detail page that is not drawn
// with the shared article layout (title, infobox, navbox, a heading on every section).
const { chromium } = require('playwright'), path = require('path');
(async () => {
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1400, height: 900 } });
  const errs = [], bad = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.resolve(process.argv[2] || 'dist/Linggango_Relic_Wiki.html'), { waitUntil: 'load' });
  await p.waitForTimeout(2500);
  const cards = await p.evaluate(() => { document.querySelectorAll('#pmap .pn').forEach(t => t.click()); return [...document.querySelectorAll('.pbc')].map(a => [a.querySelector('b')?.textContent, !!a.querySelector('img.bg') || /url/.test(a.getAttribute('style') || '')]); });
  const noBg = cards.filter(c => !c[1]).map(c => c[0]);
  // every detail page uses article() (app.js): one title, an infobox, a navbox, and a heading on every section
  const LAYOUT = `(() => { const m = document.getElementById('main'), a = m.querySelector('.ip.art');
    if (!a) return 'no article'; if (!(a.querySelector('h1.ip-title')?.textContent.trim())) return 'no title';
    if (!a.querySelector('.ip-info')) return 'no infobox'; if (!a.querySelector('.navbox')) return 'no navbox';
    if ([...a.querySelectorAll('.ip-sec')].some(x => !x.querySelector(':scope>h2')?.textContent.trim())) return 'untitled section';
    return ''; })()`;
  // render a route, then [text length, pictures that fail to decode]; a picture still loading after 2 s counts as fine
  const VIEW = async h => {
    location.hash = h; render(); const m = document.getElementById('main'), im = [...m.querySelectorAll('img')];
    im.forEach(i => { if (i.loading === 'lazy') i.loading = 'eager'; });
    const f = await Promise.all(im.map(i => Promise.race([i.decode().then(() => 0, () => 1), new Promise(r => setTimeout(() => r(0), 2000))])));
    return [m.innerText.length, f.reduce((s, x) => s + x, 0)];
  };
  const [ne, ns] = await p.evaluate(() => [GE.length, GS.length]);
  const lay = [], brokenImg = [];
  for (const [pre, n] of [['#g', ne], ['#gs', ns]])
    for (let i = 0; i < n; i++) {
      const r = await p.evaluate(VIEW, pre + i);
      if (r[0] < 40 || r[1]) bad.push(pre + i);
      const l = await p.evaluate(LAYOUT); if (l) lay.push(pre + i + ' ' + l);
    }
  const others = await p.evaluate(() => [...D.map(d => '#i' + d.ix), ...KEEPERS().concat('ender_dragon').map(k => '#boss/' + k), ...Object.keys(SIDEB).map(n => '#side/' + encodeURIComponent(n))]);
  for (const h of others) {
    const r = await p.evaluate(VIEW, h); if (r[1]) brokenImg.push(h + ' ' + r[1]);
    const l = await p.evaluate(LAYOUT); if (l) lay.push(h + ' ' + l);
  }
  // data and ranking invariants (each one is a bug that has happened)
  const inv = await p.evaluate(() => {
    const bad = [], acts = ORDER.filter(x => x != -1), A = new Set(ORDER);
    for (const g of [...GE, ...GS]) {
      const id = g.id || g.k;
      if (!A.has(g.a)) bad.push('act ' + id + ' ' + g.a);              // 6.1 sat at index -1: a battleaxe showed at Act 0
      if (g.ga && !A.has(g.ga)) bad.push('gate ' + id + ' ' + g.ga);
      for (const r in g.sc) if (!Number.isFinite(g.sc[r])) bad.push('score ' + id + ' ' + r);
    }
    // a melee weapon has a damage score, unless the game showed it deals none (gNoMelee: Create's cardboard sword cancels its own hit)
    for (const g of GE) if (g.k === 'melee' && g.dmg != null && !(g.sc.ME > 0) && !gNoMelee(g)) bad.push('dps ' + g.id);
    if ('TA' in GROLE) bad.push('Tank role is back');                   // retired: four playstyles only
    // a set's score is a function of the Act it is judged at: finite and positive for every role and Act
    for (const s of GS) for (const r in GROLE) for (const a of acts) if (!(gScore(s, r, a) > 0)) bad.push(`set score ${s.k} ${r} ${a}`);
    if (!(GSTEP > 1.05 && GSTEP < 1.3)) bad.push('power curve ' + GSTEP);
    // every playstyle keeps real options at every Act (Ranged armor once stopped at Act V, Mage weapons had one pick at Act 0)
    const need = {w: {ME: 3, RA: 3, MA: 3, SU: 0}, a: {ME: 5, RA: 5, MA: 5, SU: 5}};
    for (const w in need) for (const r in need[w]) for (const a of acts) {
      const n = gTiers(a, r, w).reduce((s, t) => s + t[1].length, 0), min = r === 'SU' && a >= 2 ? 2 : need[w][r];
      if (n < min) bad.push(`list ${w}/${r}/Act ${a}: ${n}`);
    }
    // an effect level over 10 or a duration under half a second read from code is a misread argument (Frostmourne's
    // Strength XXI for 3 ticks) unless the item's tooltip says it: gear_pipeline.fx_doubt drops such numbers
    const rom = n => [[50, 'L'], [40, 'XL'], [10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'], [1, 'I']].reduce((o, [v, s]) => { while (n >= v) { o += s; n -= v } return o }, '');
    const tipOf = id => (GE.find(x => x.id === id)?.tip || []).join(' ');
    for (const g of [...GE, ...GS]) for (const r of g.fx || []) {
      if (r.doubt || r.ms) continue;
      const t = tipOf(r.src || g.id);
      if (r.level > 10 && ![r.level, r.level - 1].some(l => new RegExp(`\\b${rom(l)}\\b`).test(t))) bad.push(`effect level ${g.id || g.k} ${r.effect} ${r.level}`);
      if (r.ticks > 0 && r.ticks < 10 && !new RegExp(`\\b${r.ticks} ticks?\\b`).test(t)) bad.push(`effect duration ${g.id || g.k} ${r.effect} ${r.ticks} ticks`);
    }
    // an item is never listed before its own Act
    for (const w of ['w', 'a']) for (const r of ['ME', 'RA', 'MA', 'SU']) for (const a of acts)
      for (const [, xs] of gTiers(a, r, w)) for (const g of xs) if (oiA(g.a) > oiA(a)) bad.push(`early ${g.id || g.k} at ${a}`);
    // audit of 2026-10-31: each line is a data or scoring bug that was live
    // Mage output counted Goety's spell_potency (+1 read as +100%) and casting_speed as Iron's stats: Goety keys keep their namespace
    if (GOFF.MA({spell_potency: [1, 0], casting_speed: [.03, 0]}, 5) !== 1) bad.push('GOFF.MA reads Goety spell_potency/casting_speed');
    for (const g of [...GE, ...GS]) { const at = g.at || {};
      if ((at.spell_power || [0])[0] !== 0) bad.push('additive spell_power (another mod folded into Iron\'s) ' + (g.id || g.k));
      for (const k of ['spell_potency', 'casting_speed', 'spell_power_multiplier', 'cast_duration', 'spell_cooldown', 'soul_discount']) if (k in at) bad.push('unprefixed Goety key ' + k + ' on ' + (g.id || g.k)); }
    { const d = GS.find(x => x.k === 'goety:dark'); if (d && !(gOff(d, 'MA', 5) < 1.5)) bad.push('Dark set Mage output ' + gOff(d, 'MA', 5)); }
    // Summoner's Bangle: a flat +2 Summon Power was scored as +100% (Mythic, #1 Summon curio); Summon Duration is not damage
    { const m = CM['ars_elemental:summon_bangle'], B = BYID['ars_elemental:summon_bangle'];
      if (!m || !m.d || m.d['ars_nouveau:ars_elemental.perk.summon_power'] !== 2) bad.push('summon_bangle summon_power ' + JSON.stringify(m && m.d));
      if (B && !(gCurioScore(B, 'SU', 7) < 1.2 && B.r < 4)) bad.push('summon_bangle scored as a multiplier');
      if (GOFF.SU({summon_duration: [0, .4]}, 7) !== 1) bad.push('summon_duration counted as summon damage'); }
    // Resistance follows Linggango Fixes' curve (0.2 + 0.04444 a level), not 20% a level
    for (let L = 1; L <= 5; L++) { const e = 0.2 + (L - 1) * 0.04444, a = gCurioAt({fx: [['minecraft:resistance', L, 100]]}).resistance[1];
      if (Math.abs(a - e) > 1e-9) bad.push('resistance L' + L + ' ' + a); }
    // curio 'Measured in game' rows: flat attributes printed as flat, nothing beyond ±1000%
    { const kp = BYID['brutality:knights_pendant']; if (kp && !gCurioMs(kp).includes('+4 Lethality')) bad.push("Knight's Pendant lethality not flat");
      for (const id in CM) for (const li of gCurioMs(BYID[id] || {id, fx: []}).match(/[+-][\d.]+%/g) || []) if (Math.abs(parseFloat(li)) > 1000) bad.push('measured row ' + id + ' ' + li); }
    // every lock names its boss (GATEN had no 6.3, 9 or 12); nothing sits below its own gate
    for (const g of [...GE, ...GS]) { if (g.ga && !GATEN[g.ga]) bad.push('gate without a name ' + (g.id || g.k) + ' ' + g.ga); if (oiA(g.a) < oiA(g.ga || 0)) bad.push('below its gate ' + (g.id || g.k)); }
    // armor families are one set each (Living, Robe, Geomancer... were four one-piece sets); no two sets share a name in a mod
    if (GS.filter(x => x.k.startsWith('mowziesmobs:geomancer')).length !== 1) bad.push('Geomancer split');
    { const seen = {}; for (const x of GS) { const k = x.n + '|' + x.k.split(':')[0]; if (seen[k]) bad.push('two sets named ' + k); seen[k] = 1; } }
    // the pack disables Mystical Agriculture armor and never loads Tide Piercer's recipe: not in any tier list
    { const tp = GBY['somakespells:tide_piercer']; if (tp && gTierOf(tp, 5, 'MA', 'w') !== null) bad.push('Tide Piercer tiered');
      const ma = GS.find(x => x.k === 'mysticalagriculture:awakened_supremium'); if (ma && gTierOf(ma, 8, 'RA', 'a') !== null) bad.push('MA armor tiered'); }
    // loadout grid: a missing pick is one cell (an empty Summon weapon once pushed Chainmail into the label column)
    for (const a of acts) { const t = document.createElement('template'); t.innerHTML = gLoadout(a);
      for (const row of t.content.querySelectorAll('.gld')) if (row.children.length !== 3) bad.push('loadout row with ' + row.children.length + ' cells at ' + a); }
    // bosses: Keepers, Wither and Ender Dragon are exempt from Hardmode (forge:armageddon_bosses); the Dragon is 600 HP / 30 armor
    if (typeof BST !== 'undefined') { if (!(BST.ender_dragon && BST.ender_dragon.effective.hp === 600 && BST.ender_dragon.effective.armor === 30)) bad.push('Ender Dragon stats');
      for (const k in BST) for (const ph of BST[k].phases || []) if (ph.hardmode) bad.push('Hardmode applied to ' + k); }
    // the pack's soul_bosses pin side-boss health and armor
    if (typeof SSTAT !== 'undefined') { const ig = (SSTAT.Ignis || [])[0]; if (!(ig && ig.hp === 3200 && ig.pinned)) bad.push('Ignis not pinned to the pack\'s 3200 HP'); }
    // the Keepers' names are the game's (The Discord, Fourth Calamity), not wiki-made
    if (document.documentElement.outerHTML.includes('Keeper of the Calamities')) bad.push('wiki-made Keeper name');
    return bad;
  });
  console.log(`invariants: ${inv.length} broken ${inv.slice(0, 8).join(' | ')}`);
  console.log(`path cards ${cards.length}, without background: ${noBg.length} ${noBg.join(', ')}`);
  console.log(`gear pages ${ne}, sets ${ns}, empty or broken: ${bad.length} ${bad.slice(0, 10).join(' ')}`);
  console.log(`curio, Keeper and side boss pages ${others.length}, with a broken picture: ${brokenImg.length} ${brokenImg.slice(0, 8).join(' | ')}`);
  console.log(`detail pages ${ne + ns + others.length}, off the shared layout: ${lay.length} ${lay.slice(0, 6).join(' | ')}`);
  console.log(`script errors: ${errs.length} ${errs.slice(0, 3).join(' | ')}`);
  await b.close();
  process.exit(errs.length || inv.length || bad.length || brokenImg.length || lay.length || noBg.length || !cards.length ? 1 : 0);
})();
