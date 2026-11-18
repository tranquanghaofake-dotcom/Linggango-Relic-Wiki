// Movement and loot ranking (2026-11-18): by the percent the curio's own text states, a conditional bonus not counted.
{ const u = utilRank(), by = n => D.find(d => d.n === n), pct = (n, c) => { const d = by(n), o = d && utilOf(d); return o && o[c] ? o[c].pct : null; };
  if (u.move.length < 20) bad.push('util: only ' + u.move.length + ' movement curios ranked');
  if (pct('Feyweight', 'move') !== 100) bad.push('util: Feyweight should read +100% movement speed, got ' + pct('Feyweight', 'move'));
  if (pct('Pegasus Boots', 'move') !== 10) bad.push('util: Pegasus Boots should read +10%');
  if (pct('Dr. Binty', 'move') !== 25) bad.push('util: Dr. Binty (+0.025, +25% of base walking speed) should read 25');
  // conditions are not counted: per kill, on sand, after a dodge, a penalty
  for (const n of ['Baby', 'Black Belt', 'Dumbbell']) if (pct(n, 'move')) bad.push('util: ' + n + ' counted a conditional or negative movement bonus: ' + pct(n, 'move'));
  if (pct('Dune Treads', 'move') !== 5) bad.push('util: Dune Treads should count its plain +5% and not the +10% on sand');
  if (pct('Emerald Stoneplate Ring', 'loot') !== 25) bad.push('util: Emerald Stoneplate Ring should read +25% XP');
  if (pct('Emblem of Monster Slayer', 'loot') !== 100) bad.push('util: "double XP" should read +100%');
  // order and tiers never go up down the list; a Looting or Fortune level is not a percent
  const L = 'SABCD'; for (const c of ['move', 'loot']) { let prev = Infinity, pt = 0; u[c].forEach((d, i) => { const p = utilOf(d)[c].pct; if (p > prev) bad.push('util: ' + d.n + ' out of order in ' + c); prev = p; if (d._ur[c].k !== i + 1) bad.push('util: rank number of ' + d.n); if (L.indexOf(d._ur[c].t) < pt) bad.push('util: tier of ' + d.n + ' higher than one above it'); pt = Math.max(pt, L.indexOf(d._ur[c].t)); if (!(p > 0)) bad.push('util: ' + d.n + ' ranked with no percent'); }); }
  if (utilOf(by('Superstitious Hat'))) bad.push('util: a Looting level (+1 Looting) is not a percent but Superstitious Hat is ranked');
  if (!/Movement speed rank/.test(utilHtml(by('Pegasus Boots')))) bad.push('util: the page block misses the rank'); }
