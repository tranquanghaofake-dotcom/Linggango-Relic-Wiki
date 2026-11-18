// Stated percent ranking and the coverage table (2026-11-18): curios without a measured tier ranked by the percents their text states; every curio accounted for.
{ const s = statRank(), by = n => D.find(d => d.n === n), pts = (n, c) => { const d = by(n), o = d && statOf(d); return o && o[c] ? o[c].pts : null; };
  // the uptime table: shares between 0 and 1, every row has a reason and a valid pattern
  for (const x of UPTIME.items) { if (!(x.share > 0 && x.share < 1)) bad.push('stated: share of ' + x.id + ' is ' + x.share); if (!x.why) bad.push('stated: ' + x.id + ' has no reason'); try { new RegExp(x.re, 'i'); } catch (e) { bad.push('stated: pattern of ' + x.id + ' is not valid'); } }
  // a bonus counted once, a conditional one at its share, a cost leaves the curio out, a measured curio is not ranked twice
  if (pts('Crown of Tyranny', 'offence') !== 75) bad.push('stated: Crown of Tyranny should read 75, got ' + pts('Crown of Tyranny', 'offence'));
  if (pts('Bruteskin Belt', 'offence') !== 70) bad.push('stated: Bruteskin Belt (+50% crit damage, +20% crit chance) should read 70, got ' + pts('Bruteskin Belt', 'offence') + ' (a bonus counted twice?)');
  if (statOf(by('Divine Immolation'))) bad.push('stated: Divine Immolation names a cost ("but max health") and must not be ranked on its gain alone');
  if (statOf(by('Venerated Locket'))) bad.push('stated: Venerated Locket names a cost and must not be ranked on its gain alone');
  for (const d of D) if (CTIER[d.id] && statOf(d)) bad.push('stated: ' + d.n + ' has a measured tier and is also ranked by its text');
  const L = 'SABCD'; for (const c of Object.keys(s)) { let prev = Infinity, pt = 0; s[c].forEach((d, i) => { const p = statOf(d)[c].pts; if (p > prev) bad.push('stated: ' + d.n + ' out of order in ' + c); prev = p; if (d._sr[c].k !== i + 1) bad.push('stated: rank number of ' + d.n); if (L.indexOf(d._sr[c].t) < pt) bad.push('stated: tier of ' + d.n + ' higher than one above it'); pt = Math.max(pt, L.indexOf(d._sr[c].t)); if (!(p > 0)) bad.push('stated: ' + d.n + ' ranked with no points'); }); }
  if (s.summon.some(d => statOf(d).summon.parts.some(p => /range|duration/i.test(p.t)))) bad.push('stated: minion range or duration counted as power');
  // coverage: every curio but the Looting Charms is somewhere, and the rows add up
  const cv = coverage(), n = cv.rows.reduce((a, r) => a + r[1], 0) + cv.rest.reduce((a, r) => a + r[1], 0);
  if (n !== cv.total) bad.push('stated: coverage adds up to ' + n + ' of ' + cv.total);
  if (cv.total !== D.filter(d => d.r !== 6).length) bad.push('stated: coverage total is not every curio but the Looting Charms');
  if (!cv.rest.length || cv.rest.some(r => !r[0])) bad.push('stated: a coverage row without a reason'); }
