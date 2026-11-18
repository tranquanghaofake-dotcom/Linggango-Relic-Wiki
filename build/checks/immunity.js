// Immunity ranking (2026-11-18): curios that block effects or hazards, ranked by how many and how strong (patches/effect_threat.json, a judgement table).
{ const rk = immRank(), by = n => D.find(d => d.n === n);
  if (rk.length < 80) bad.push('immunity: only ' + rk.length + ' curios ranked');
  // the table: weights 1 to 3, no alias twice, every effect id a real effect of the pack
  const seen = new Map(); for (const x of THREAT.items) { if (![1, 2, 3].includes(x.w)) bad.push('immunity: weight of ' + x.id + ' is ' + x.w); if (!x.why) bad.push('immunity: ' + x.id + ' has no reason'); for (const nm of x.names) { if (seen.has(nm)) bad.push('immunity: alias "' + nm + '" in ' + x.id + ' and ' + seen.get(nm)); seen.set(nm, x.id); } }
  for (const x of THREAT.items) if (x.kind === 'effect' && x.id !== 'hex' && x.id !== 'voidflame' && !(window.EFX || []).some(e => e.i === 'minecraft:' + x.id)) bad.push('immunity: ' + x.id + ' is not a vanilla effect of the pack');
  // order: sorted by points, rank numbers 1..n, tier never rises down the list
  const L = 'SABCD'; let prev = Infinity, pt = 0;
  rk.forEach((d, i) => { const o = immOf(d); if (o.pts > prev) bad.push('immunity: ' + d.n + ' out of order'); prev = o.pts; if (d._immK !== i + 1) bad.push('immunity: rank number of ' + d.n); if (L.indexOf(d._immT) < pt) bad.push('immunity: tier of ' + d.n + ' is higher than one above it'); pt = Math.max(pt, L.indexOf(d._immT)); if (!o.hits.length) bad.push('immunity: ' + d.n + ' ranked with nothing it blocks'); });
  // the cases that must hold: more effects beat fewer, all effects beat a named few, strength counts
  const pts = n => { const d = by(n); return d && immOf(d) ? immOf(d).pts : -1; };
  if (!(pts('Ankh Aegis') > pts('Ankh Tablet'))) bad.push('immunity: Ankh Aegis (nine effects) should beat Ankh Tablet (eight)');
  if (!(pts('Ankh Tablet') > pts('Necrotoxic Shell'))) bad.push('immunity: eight effects should beat Wither and Poison');
  if (!(pts('Wither Shard') > pts('Hunter\'s Cloak'))) bad.push('immunity: Wither (3) should beat Hunger (1)');
  if (!(pts('Pearl of the Void') >= pts('Ankh Aegis'))) bad.push('immunity: "all effects" should not be worth less than nine named effects');
  // a curio with no immunity in its text is not ranked, and the page carries the block
  if (immOf(by('Stygian Chain'))) bad.push('immunity: Stygian Chain has no immunity but is ranked');
  if (!/Wither/.test(immHtml(by('Wither Shard'))) || !/Immunity rank/.test(immHtml(by('Wither Shard')))) bad.push('immunity: the page block misses its rank or effect'); }
