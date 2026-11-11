// Equipment: scoring, stats, sets, tier lists and the gear pages' own text. Ported from the audit fix pass of 2026-10-31
// (pending invariants, groups gear-js and gear-pipeline); each block names the finding it guards. Runs in the page
// (check.js: `bad`, `acts` and `await patchJSON(file)` in scope).
const ALL = [...GE, ...GS], nm = g => g.id || g.k;
// gear-logic-combat-07: worn Resistance follows Linggango Fixes' curve (0.2 + 0.04444 a level) on gear too, not only on curios
for (let L = 1; L <= 5; L++) { const e = 0.2 + (L - 1) * 0.04444, a = gFxAt({fx: [{effect: 'minecraft:resistance', level: L, when: 'worn', who: 'self'}]}).resistance[1];
  if (Math.abs(a - e) > 1e-9) bad.push('worn resistance L' + L + ' ' + a); }
// gear-logic-combat-01: a measured curio's Goety attribute keeps its namespace (it was read as Iron's spell power)
for (const id in CM) for (const k in CM[id].d || {}) if (/^(goety|goety_revelation|goetyawaken|goety_cataclysm|bosgoety):/.test(k) && !GCK(k).includes('.')) bad.push('curio Goety key lost its namespace ' + id + ' ' + k);
// gear-logic-combat-02: every measured curio attribute has a display unit, and no percent change is beyond ±1000%
for (const id in CM) for (const k in CM[id].d || {}) { const u = gUnit(GCK(k));
  if (!['flat', 'pct', 'base', 'x10'].includes(u)) bad.push('curio unit missing ' + id + ' ' + k);
  if (u === 'pct' && Math.abs(CM[id].d[k]) > 10) bad.push('curio pct row beyond 1000% ' + id + ' ' + k); }
// gear-logic-combat-02: known 'Measured in game' rows print in the game's units (flat stays flat, percent stays percent)
for (const [id, want] of [['brutality:chocolate_bar', '+15% Movement Speed'], ['ars_elemental:summon_bangle', '+2 Summon Power']]) {
  const t = document.createElement('div'); t.innerHTML = BYID[id] ? gCurioMs(BYID[id]) : '';
  if (![...t.querySelectorAll('li')].some(li => li.textContent.trim().startsWith(want))) bad.push('curio measured row: ' + id + ' lacks ' + want + ' (' + t.textContent.trim().slice(0, 80) + ')'); }
// gear-logic-combat-06 / copy-docs-12: attribute units in gMod (dodge window in seconds, knockback resistance x10, percents)
for (const [k, v, w] of [['dodge_window', .5, '+0.5 Dodge Window'], ['overheal', .05, '+5% Overheal'], ['experience_gained', .1, '+10% XP Gained'], ['knockback_resistance', .1, '+1 Knockback Resistance']]) {
  const g = gMod(k, v, 0)[0]; if (g !== w) bad.push('gMod ' + k + ' = ' + g + ', want ' + w); }
// gear-logic-combat-06: a set page's knockback resistance is the sum of its pieces' rows
for (const s of GS) { if (!s.kbr) continue; const pc = s.ps.reduce((n, p) => n + +((gStats(p).find(r => r[1] === 'Knockback Resistance') || [0, 0, 0])[2]), 0);
  if (Math.abs(pc - gSetKbr(s)) > .05) bad.push('set kbr ' + s.n + ' ' + gSetKbr(s) + ' vs pieces ' + pc); }
// detail-pages-checks-12: mod names are trimmed (a trailing space put a space before the lead's comma)
for (const [k, v] of Object.entries(GNS)) if (v !== v.trim()) bad.push('GNS untrimmed ' + k);
// gated tooltips name the boss and the Act in full ('until  falls', 'Act Dragon')
{ const t = document.createElement('a'); document.body.appendChild(t);
  for (const g of ALL) if (g.ga) { t.dataset.t = (g.ps ? 's' : 'g') + g.ix; gearTip(t); const x = tip.textContent;
    if (/until\s+falls/.test(x)) bad.push('tip lock without boss: ' + g.n);
    if (/\bActs? Dragon\b|Outclassed from (?:Dragon|[IVX0])/.test(x)) bad.push('tip short Act: ' + g.n); }
  t.remove(); hideTip(); }
// gear-logic-combat-10: the verdict's span ends before the Act where the tier strip cuts the item
for (const g of ALL) { const v = gVerdict(g); if (!v) continue;
  const r = gMain(g), w = g.ps ? 'a' : 'w', as = acts.filter(x => oiA(x) >= oiA(g.a)), ts = as.map(x => gTierOf(g, x, r, w)), k = ts.findIndex((t, i) => i > 0 && (!t || t === 'D'));
  if (k > 0) { const body = v.split('Replace it by')[0];
    if (as.slice(k).some(x => [' ', '.', ' ('].some(e => body.includes(' ' + actL(x) + e)))) bad.push('verdict span past the strip: ' + g.n); } }
// data-gear-01: no disabled item and no set of disabled pieces in a tier list
{ const o = new Set(); for (const a of acts) for (const r of Object.keys(GROLE)) for (const w of ['w', 'a']) for (const [, xs] of gTiers(a, r, w)) for (const g of xs)
  if (gHidden(g) || (g.ps && g.ps.every(p => p.ob && p.ob[0] === '!'))) o.add('hidden item listed: ' + g.n + ' Act ' + a + ' ' + r); bad.push(...o); }
// data-gear-01: the pack disables Mystical Agriculture armor: every piece carries a '!' note and none is listed
{ const MA = new Set(['inferium', 'prudentium', 'tertium', 'imperium', 'supremium', 'awakened_supremium'].flatMap(m => ['helmet', 'chestplate', 'leggings', 'boots'].map(s => 'mysticalagriculture:' + m + '_' + s))), o = new Set();
  for (const id of MA) { const g = GBY[id]; if (!g || !(g.ob || '').startsWith('!')) o.add('MA armor without a ! note: ' + id); }
  for (const a of acts) for (const r of Object.keys(GROLE)) for (const [, xs] of gTiers(a, r, 'a')) for (const x of xs) if ((x.ps ? x.p : [x.id]).some(i => MA.has(i))) o.add('pack-disabled MA armor listed: ' + x.n);
  bad.push(...o); }
// ui-desktop-09: the gear search marks later-Act items, lists the usable ones first, prints the count, offers Show more when cut
{ const keep = GALL; GALL = false;
  for (const q of ['sword', 'bow']) for (const a of acts) { const xs = gMatch(q, a), t = document.createElement('template'); t.innerHTML = gSearch(xs, a, 'ME');
    let late = false; [...t.content.querySelectorAll('.gsr>a')].forEach((n, i) => { const L = oiA(xs[i].a) > oiA(a);
      if (L !== !!n.querySelector('.glater')) bad.push(`search ${q} Act ${a}: ${xs[i].n} later-Act mark ${!L}`);
      if (L) late = true; else if (late) bad.push(`search ${q} Act ${a}: usable ${xs[i].n} after a later one`); });
    if (!(t.content.querySelector('.gsn')?.textContent || '').includes(String(xs.length))) bad.push(`search ${q} Act ${a}: no match count`);
    if (xs.length > 80 && !t.content.querySelector('[data-gall]')) bad.push(`search ${q} Act ${a}: cut at 80 with no Show more`); }
  GALL = keep; }
// phone-10: a curio tile in the gear Curios tab is one frame (no .slot inside .gtl)
{ history.replaceState(null, '', '#gear/0/ME/c'); render(); if (document.querySelector('#main .gtl>.slot')) bad.push('curio tile frame inside a frame (.gtl>.slot)'); }
// data-gear-04: a single-recipe gear piece never sits before a gear ingredient of its recipe
for (const g of GE) if (g.rc && g.rc.length === 1 && !g.lt) for (const y of g.rc[0].i || [])
  if (typeof y === 'string' && y !== g.rc[0].t && y !== g.id && GBY[y] && oiA(GBY[y].a) > oiA(g.a)) bad.push(`${g.n} at Act ${g.a} needs ${GBY[y].n} from Act ${GBY[y].a}`);
// data-gear-04 / data-curios-03: an item only a boss drops (boss_only_items.json, at the Act of the earliest boss that drops it) bounds the
// single-recipe gear and the crafted curios made from it; and none of those items also drops from a vanilla mob
{ const ONLY = await patchJSON('boss_only_items.json'), out = new Set(), ok = a => a === 6.1 || a === 6.2 ? ORDER.indexOf(6) + Math.round((a - 6) * 10) / 10 * 3 : ORDER.indexOf(a);
  const dep = BGRAPH.dep, DROP = {}, put = (it, a) => { if (it in ONLY && !/treasure_pouch/.test(it) && (DROP[it] === undefined || ok(a) < ok(DROP[it]))) DROP[it] = a; };
  BOSSR.forEach(r => { if (r[0] in BACT && r[0] in dep) (r[4] || []).forEach(it => put(it, BACT[r[0]])); });
  Object.entries(SIDEB).forEach(([n, s]) => { if (n in BACT && n in dep) (s.drops || []).forEach(x => put(x.id, BACT[n])); });
  BEXTRA.forEach(x => { if (x[0] in BACT) (x[4] || []).forEach(it => put(it, BACT[x[0]])); });
  Object.entries(ONLY).forEach(([it, ts]) => { if (ts.some(t => t.startsWith('minecraft:entities/'))) out.add(`boss_only_items.json: ${it} also drops from a vanilla mob`); });
  D.forEach(d => { if (d.g === 'Craft' && d.gr) d.gr.c.forEach(c => { if (c && !c[1] && c[0] in DROP && ok(d.t) < ok(DROP[c[0]])) out.add(`${d.n} at Act ${d.t} needs ${c[0]}, only a boss at Act ${DROP[c[0]]} drops it`); }); });
  GE.forEach(g => { if (g.rc && g.rc.length === 1 && !g.lt) (g.rc[0].i || []).forEach(y => { if (typeof y === 'string' && y !== g.rc[0].t && y in DROP && ORDER.indexOf(g.a) < ok(DROP[y])) out.add(`${g.n} at Act ${g.a} needs ${y}, only a boss at Act ${DROP[y]} drops it`); }); });
  bad.push(...out); }
// data-gear-02 / ui-desktop-05: armor families are one set each with all their pieces, with no split leftovers; set keys are unique;
// no two one-piece sets of a mod share a stem
{ const fam = {'mowziesmobs:geomancer': 4, 'mekanism:mekasuit': 4, 'ad_astra:space_suit': 4, 'ad_astra:netherite_space_suit': 4, 'mekanism:hazmat': 4, 'mekanism:scuba': 2, 'alexscaves:darkness': 2, 'create:copper_diving': 3, 'create:netherite_diving': 3, 'immersive_armors:robe': 4, 'bloodmagic:living': 4};
  const left = {'mowziesmobs:geomancer': ['mowziesmobs:geomancer_'], 'mekanism:mekasuit': ['mekanism:mekasuit_'], 'ad_astra:space_suit': ['ad_astra:space'], 'ad_astra:netherite_space_suit': ['ad_astra:netherite_space'], 'mekanism:hazmat': ['mekanism:hazmat_'], 'mekanism:scuba': ['mekanism:scuba_'], 'alexscaves:darkness': ['alexscaves:of_darkness', 'alexscaves:cloak_of_darkness', 'alexscaves:hood_of_darkness'], 'create:copper_diving': ['create:copper_backtank', 'create:copper_diving_'], 'create:netherite_diving': ['create:netherite_backtank', 'create:netherite_diving_'], 'immersive_armors:robe': ['immersive_armors:robe_'], 'bloodmagic:living': ['bloodmagic:living']};
  for (const [k, n] of Object.entries(fam)) { const s = GS.filter(x => x.k === k);
    if (s.length !== 1 || s[0].p.length !== n) bad.push('armor family ' + k + ': ' + s.length + ' sets, ' + (s[0] ? s[0].p.length : 0) + ' pieces, want 1 set of ' + n);
    for (const st of left[k]) for (const x of GS) if (x.k !== k && x.k.startsWith(st)) bad.push('split leftover of ' + k + ': ' + x.k); }
  if (new Set(GS.map(s => s.k)).size !== GS.length) bad.push('GS keys not unique');
  const SW = /^(helmet|chestplate|leggings|boots|hood|robe|robes|cap|tunic|pants|crown|mask|greaves|sabatons|hat|chest|legs|feet|head|armor|armour|helm|plate|leggins|shoes|gown|tank|bodyarmor|suit|backtank|beads|belt|sandals|cloak|of)$/;
  const stem = i => { const [ns, n] = i.split(':'); return ns + ':' + n.split('_').filter(t => !SW.test(t)).join('_').replace(/(helmet|plate|leggings|boots)$/, ''); }, st = {};
  for (const s of GS.filter(x => x.p.length === 1)) { const q = stem(s.p[0]); if (st[q]) bad.push('one-piece sets with one stem: ' + st[q] + ' / ' + s.k); st[q] = s.k; } }
// data-gear-03: no visible gear shows a recipe with an item from a mod the pack lacks; never-loaded recipes stay hidden
{ const OK = new Set(['minecraft', 'forge', 'c', 'kubejs']);
  for (const g of GE) { if (gHidden(g)) continue; for (const r of g.rc || []) for (const x of r.i.slice(1)) if (typeof x === 'string' && !x.startsWith('#')) { const ns = x.split(':')[0]; if (!OK.has(ns) && !(ns in GNS)) bad.push(g.id + ' recipe needs ' + x + ' (mod not in the pack)'); } }
  for (const id of ['somakespells:tide_piercer', 'somakespells:trumpet_axe', 'animus:hand_of_death']) if (!GBY[id] || !(GBY[id].ob || '').startsWith('!')) bad.push(id + ' needs an absent mod but is not marked !');
  for (const id of ['minecraft:wooden_sword', 'minecraft:wooden_axe']) if (GBY[id] && (GBY[id].rc || []).length) bad.push(id + " shows the pack's forge:false stub recipe"); }
// data-gear-07: the Stats show what the held weapon reads in game: (base + added) x (1 + multiplier) against the measured hit and speed
for (const g of GE) { const m = g.ms; if (!m || m.st || !(m.ad > 1)) continue; const at = g.at || {}, A = at.attack_damage || [0, 0], S = at.attack_speed || [0, 0];
  if (g.dmg != null && Math.abs(m.hit - m.ad) <= .15 * m.ad && Math.abs((g.dmg + A[0]) * (1 + A[1]) - m.ad) > .05 * m.ad) bad.push('Stats differ from the measured attack damage: ' + g.id);
  if (g.spd != null && m.as && Math.abs((g.spd + S[0]) * (1 + S[1]) - m.as) > .05 * m.as) bad.push('Stats differ from the measured attack speed: ' + g.id); }
// data-gear-08: fire on release is an enchantment's (Flame on the arrow, Fire Aspect), never the item's
for (const g of GE) if ((g.fx || []).some(r => r.when === 'release' && r.fire !== undefined)) bad.push('release row with a fire value: ' + g.id);
// data-gear-09 / copy-docs-06: gear names follow the pack's renameItem names (renames.json), sets included
{ const RN = await patchJSON('renames.json');
  for (const id in RN) { const g = GBY[id]; if (g && g.n.replace(/ \(Lv \d+\)$/, '') !== RN[id]) bad.push('gear name ignores the pack rename: ' + id + ' ' + g.n); }
  for (const [id, n] of [['quark:forgotten_hat', 'Stinky Hat'], ['minecraft:leather_chestplate', 'Animal Leather Chestplate'], ['mekanismtools:bronze_sword', 'Concentrated Bronze Sword']]) if (GBY[id]?.n !== n) bad.push('rename ' + id + ' ' + GBY[id]?.n);
  for (const [k, n] of [['minecraft:leather', 'Animal Leather'], ['mekanismtools:bronze', 'Concentrated Bronze']]) { const s = GS.find(x => x.k === k); if (!s || !s.n.startsWith(n)) bad.push('set rename ' + k + ' ' + s?.n); } }
// data-gear-10: every armor piece is a piece of exactly one set
{ const c = {}; GS.forEach(s => s.p.forEach(i => c[i] = (c[i] || 0) + 1)); for (const g of GE) if (g.k === 'armor' && c[g.id] !== 1) bad.push('armor piece in ' + (c[g.id] || 0) + ' sets: ' + g.id); }
// copy-docs-04 / detail-pages-checks-09: no printf token in a gear tooltip line
for (const g of ALL) for (const t of g.tip || []) if (/%\d*\$?[sd]\b|%%/.test(t)) bad.push('gear tooltip with a raw format token: ' + nm(g) + ': ' + t);
// copy-docs-12: no attribute label shows a raw namespace (Goety's keys keep theirs since the audit; gAttr strips it)
for (const g of [...GE, ...GS]) for (const k in g.at || {}) if (/\./.test(gAttr(k))) bad.push('attribute label with a dot: ' + gAttr(k) + ' on ' + (g.id || g.k));
// equip-groups: the finer groups of Equipment (gear.js GSUB, gSubOf, gOwn). Every ranged weapon is in exactly one of the four
// ranged groups (a gun by its name, never the blowgun or Gungnir; crossbows and bows by class) and a summon weapon is Summonity
// or Goety by its mod; a group's page shows only its own items, each under the tier the whole playstyle gives it, and the
// counts on the buttons add up; the Curios tab shows the playstyle's own curios unless asked for the others, the two views
// split the tiered curios in two, and a curio is "own" exactly when it raises the playstyle's output by GOWN or more
{ const ra = GE.filter(g => g.k !== 'armor' && g.sc.RA != null && !gHidden(g)), keys = GSUB.RA.map(x => x[0]), of = n => ra.filter(g => g.n === n).map(g => gSubOf(g, 'RA'));
  for (const g of ra) if (!keys.includes(gSubOf(g, 'RA'))) bad.push('equip-groups: ' + g.n + ' is in no ranged group');
  if (!of('Railgun').length || of('Railgun').some(k => k !== 'gun') || of('Blowgun').includes('gun') || of('Gungnir').includes('gun') || of('Crossbow')[0] !== 'xbow' || of('Bow')[0] !== 'bow')
    bad.push('equip-groups: Railgun, Blowgun, Gungnir, Crossbow or Bow is in the wrong ranged group');
  for (const g of GE.filter(g => g.k === 'summon')) if (gSubOf(g, 'SU') !== (g.ns === 'summonity' ? 'summonity' : /^goety/.test(g.ns) ? 'goety' : null)) bad.push('equip-groups: ' + g.n + ' is in the wrong summon group');
  const a = acts[acts.length - 1], go = async h => { location.hash = h; await new Promise(r => setTimeout(r, 80)); render(); }, rows = () => [...document.querySelectorAll('#main .gtl-list .grow')];
  await go(`#gear/${a}/RA/w/gun`); let n = 0;
  for (const row of rows()) for (const t of row.querySelectorAll('a.gtl')) { const g = GE[+t.getAttribute('href').slice(2)]; n++;
    if (gSubOf(g, 'RA') !== 'gun' || gTierOf(g, a, 'RA', 'w') !== row.querySelector('.glet').textContent.trim()) bad.push('equip-groups: ' + g.n + ' on the Guns page is not a gun, or stands under another tier than the playstyle gives it'); }
  const cs = [...document.querySelectorAll('#main .gseg.subs a .n')].map(x => +x.textContent);
  if (!n || cs.length !== 5 || cs[0] !== cs.slice(1).reduce((x, y) => x + y, 0)) bad.push(`equip-groups: ${n} guns shown; the ranged group counts are ${cs.join(', ')}`);
  const cur = async h => { await go(h); return rows().flatMap(r => [...r.querySelectorAll('a.gtl')]).map(t => D[+t.dataset.t]); };
  const own = await cur(`#gear/${a}/MA/c`), any = await cur(`#gear/${a}/MA/c/any`), all = gTiers(a, 'MA', 'c').flatMap(x => x[1]);
  if (!own.length || !any.length || own.length + any.length !== all.length || own.some(d => !gOwn(d, 'MA', a)) || any.some(d => gOwn(d, 'MA', a)))
    bad.push(`equip-groups: Mage curios: ${own.length} own + ${any.length} others of ${all.length} tiered, or one on the wrong side`);
  await go('#gear'); }
