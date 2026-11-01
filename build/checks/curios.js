// Curios: recipes, sources, drop chances, names and the curio text. Ported from the audit fix pass of 2026-10-31 (pending
// invariants, groups curio-data and app-js); each block names the finding it guards. Runs in the page (check.js: `bad`,
// `acts` and `await patchJSON(file)` in scope).
const E = await patchJSON('curio_eff_recipes.json');
// data-curios-05/06: every curio grid is one of the pack's recipes for it (curio_eff_recipes.json, from pack_audit/curio_recipes.py),
// unless allowed with a reason; an allow entry names a curio that has a recipe
for (const d of D) if (d.gr && E.sets[d.id] && !E.allow[d.id]) { const k = [...new Set(d.gr.c.filter(c => c && (c[1] || c[0])).map(c => c[1] || c[0]))].sort().join(' ');
  if (!E.sets[d.id].some(s => s.join(' ') === k)) bad.push(`grid not the pack's recipe: ${d.id} [${k}]`); }
for (const id of Object.keys(E.allow)) if (!E.sets[id]) bad.push('curio_eff_recipes allow entry with no recipe: ' + id);
// ui-desktop-21: every grid ingredient has a picture or is declared without one (curio_recipes.json nopic), and no tooltip grid
// draws the two-letter placeholder for an undeclared id
{ const NP = (await patchJSON('curio_recipes.json')).nopic || {};
  for (const d of D) if (d.gr) { const miss = d.gr.c.filter(c => c && c[0] && !IC[c[0]] && !BIMG[c[0]] && !NP[c[0]]);
    for (const c of miss) bad.push(`grid ingredient without a picture: ${c[0]} in ${d.id}`);
    if (miss.length && /class="ph" data-id/.test(tipRecipe(d))) bad.push('tooltip grid draws a placeholder: ' + d.id); } }
// ui-desktop-21: Ring of Ultimate Luxury is the KubeJS recipe: Fortune books in both C cells, the Tau Oil corners empty
{ const c = (BYID['enigmaticaddons:avarice_ring']?.gr?.c || []).map(x => x && x[0]);
  if (c[3] !== 'minecraft:enchanted_book' || c[5] !== 'minecraft:enchanted_book' || c[0] || c[2]) bad.push('avarice_ring grid ' + JSON.stringify(c)); }
// data-curios-01: Brutality's automatic attribute lines name the attribute the modifier changes (CM, measured), with its sign; no '+-'
{ const DYN = {'brutality:eye_of_the_dragon': 1, 'brutality:fury_band': 1, 'brutality:heart_of_wrath': 1};
  for (const d of D) { if (d.st.some(x => typeof x === 'string' && x.includes('+-'))) bad.push('stat line with +-: ' + d.id);
    if (!d.id.startsWith('brutality:') || !CM[d.id] || !CM[d.id].d || !d.st.some((x, i) => d.tg[i] === 'auto' && /^[+-]/.test(x))) continue;
    for (const [k, v] of Object.entries(CM[d.id].d)) { const n = k.split(':')[1].replace('generic.', '').replace(/_/g, ' ').toLowerCase(), hit = d.st.filter(x => typeof x === 'string' && x.toLowerCase().includes(n));
      if (!hit.length) { bad.push('brutality attr not named: ' + d.id + ' ' + k); continue; }
      if (!DYN[d.id] && !hit.some(x => x.replace(/^Up to /, '').startsWith('-') === (v < 0))) bad.push('brutality attr sign: ' + d.id + ' ' + k); } } }
// data-curios-02/07: every drop, chest and brush chance in a curio's sources equals curio_drops.json within 0.1 point ('Since 6.6.6'
// sentences describe another mod's replaced item and are skipped, except Tabi and Tool Belt)
{ const T = await patchJSON('curio_drops.json'), esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), OK = {'confluence:tabi': 1, 'uniqueaccessories:tool_belt': 1};
  for (const d of D) { const t = T[d.id]; if (!Array.isArray(t)) continue;
    const txt = d.src.join(' ').split(/(?<=\.) /).filter(x => !x.startsWith('Since 6.6.6') || OK[d.id]).join(' ');
    for (const e of t) { if (e.kind === 'chest' && e.mod !== 'confluence') continue; const n = esc(e.name);
      const re = new RegExp({mob: '(?:[Dd]ropped by|and) ' + n + ' \\(([\\d.]+)%\\)', brush: 'at ' + n + ' \\(([\\d.]+)%\\)', chest: '\\b' + n + ' ([\\d.]+)%'}[e.kind], 'g');
      for (const m of txt.matchAll(re)) if (Math.abs(+m[1] - e.p) > 0.1) bad.push('drop chance ' + d.id + ' ' + e.name + ' wiki ' + m[1] + ' pack ' + e.p); } } }
// data-curios-02: Withered Heart's chest source names the Nether Fortress (the pack's 'Nether Bridge')
if (!/Nether Fortress/.test((BYID['uniqueaccessories:withered_heart']?.src || []).join(' '))) bad.push('withered_heart lacks Nether Fortress');
// data-curios-09: Terra Curio's dungeon modifier injects into a with-table the jar lacks: no 'Dungeon' clause from it
for (const d of D) if (/Terra Curio adds it\)[^.]*\bDungeon\b/.test(d.src.join(' '))) bad.push('dead Dungeon clause: ' + d.id);
// data-curios-10: relic point costs follow config/relics/relics/*.yaml (Drowned Belt slots: requiredPoints 4)
{ const a = RL['relics:drowned_belt']?.ab.find(x => x.k === 'slots'); if (!a || a.pt !== 4) bad.push('drowned_belt slots pt ' + (a && a.pt) + ' (yaml requiredPoints 4)'); }
// data-curios-13: every Terra Curio item sits in the Accessory slot
for (const d of D) if (d.id.startsWith('confluence:') && !(d.sl.length === 1 && d.sl[0] === 'Accessory')) bad.push('confluence slot not Accessory: ' + d.id + ' ' + d.sl.join('/'));
// ui-desktop-04: every curio slot icon is one 16x16 frame (talent_slot.png is a 2-frame strip)
{ const dim = s => { const t = atob(s.replace(/^data:[^,]*,/, '').slice(0, 44)), u = i => (t.charCodeAt(i) << 24 | t.charCodeAt(i + 1) << 16 | t.charCodeAt(i + 2) << 8 | t.charCodeAt(i + 3)) >>> 0; return [u(16), u(20)]; };
  for (const t of ['cslot', 'cslotT']) for (const [k, v] of Object.entries(UI[t] || {})) { const [w, h] = dim(v); if (w !== 16 || h !== 16) bad.push('slot icon ' + t + '.' + k + ' ' + w + 'x' + h); } }
// detail-pages-checks-05: every stat line has its tag
for (const d of D) if (d.tg.length !== d.st.length) bad.push('tg/st ' + d.id + ' ' + d.tg.length + '/' + d.st.length);
// copy-docs-05 / detail-pages-checks-09: no markup, empty key slots, printf escapes, SRG names or raw JSON lists in curio text
{ const RX = /<\/?[a-z][a-z0-9]*\/?>|\[\s*\]|%%|\bwith ,|\b[mf]_\d{3,}_|\["[a-z_]+:/;
  for (const d of D) for (const x of [d.fx, ...d.st]) if (typeof x === 'string' && RX.test(x)) bad.push('raw text ' + d.id + ': ' + x.slice(0, 60)); }
// copy-docs-14: 'an' before a vowel-initial proper name in curio sources and summaries
{ const AN = /\b[Aa] [AEIOU][a-z]+ [A-Z]/, OK = /\ba Uniquely? /;
  for (const d of D) for (const x of [...d.src, d.fx]) if (AN.test(x) && !OK.test(x)) bad.push('a/an ' + d.id + ': ' + x.match(/.{0,20}\b[Aa] [AEIOU][a-z]+ [A-Z].{0,15}/)[0]); }
// data-curios-04: items Summonity 0.1.7 removed are nowhere: not a curio, not a grid cell, not a 'used in' link, no icon or name
{ const REMOVED = ['summonity:war_horn'];
  for (const d of D) { if (REMOVED.includes(d.id)) bad.push('removed item listed as a curio: ' + d.id);
    for (const c of d.gr ? d.gr.c : []) if (c && REMOVED.includes(c[0])) bad.push(`removed item in the grid of ${d.id}: ${c[0]}`);
    for (const u of d.uid || []) if (REMOVED.includes(u)) bad.push(`removed item in the 'used in' links of ${d.id}: ${u}`); }
  for (const id of REMOVED) if (IC[id] || NM[id]) bad.push('removed item still has an icon or name: ' + id); }
// data-curios-04 / -11: the 0.1.7 recipes and Pocket Universe's KubeJS recipe; a crafted curio never sits before a curio in its grid
{ const has = (id, x) => !!BYID[id]?.gr && BYID[id].gr.c.some(c => c && c[0] === x);
  for (const [id, x] of [['summonity:warlords_standard', 'summonity:war_whistle'], ['summonity:conductive_battery', 'terramity:circuit_board'], ['summonity:necromantic_scroll', 'minecraft:wither_skeleton_skull'], ['terramity:pocket_universe', 'linggango_tweaks:linggangoonium_ingot'], ['terramity:pocket_universe', 'brutality:timekeepers_clock']])
    if (!has(id, x)) bad.push(`${id}: grid lacks ${x}`);
  const oi = a => a === 6.1 || a === 6.2 ? ORDER.indexOf(6) + (a - 6) * 3 : ORDER.indexOf(a);
  for (const d of D) if (d.g === 'Craft' && d.gr) for (const c of d.gr.c) { const e = c && !c[1] && BYID[c[0]]; if (e && e !== d && oi(e.t) > oi(d.t)) bad.push(`${d.id} (Act ${d.t}) is before its ingredient ${e.id} (Act ${e.t})`); }
  if (BYID['terramity:pocket_universe'] && BYID['terramity:pocket_universe'].g !== 'Craft') bad.push('terramity:pocket_universe is not Craft'); }
// data-curios-08 / -11: Sweetheart Necklace, Vanir Mask and Pocket Universe are curios, not unobtainable; no id is both; an unobtainable
// reason never blames a curio the wiki lists as obtainable; a U id the pack has a recipe for names that recipe's missing ingredient
{ const uid = new Set(U.map(u => u.id));
  for (const id of ['confluence:sweetheart_necklace', 'moreartifacts:vanir_mask', 'terramity:pocket_universe']) { if (!BYID[id]) bad.push('missing curio: ' + id); if (uid.has(id)) bad.push('on the unobtainable list: ' + id); }
  for (const u of U) { if (BYID[u.id]) bad.push('both a curio and unobtainable: ' + u.id); const w = u.why.toLowerCase();
    if (!/instead|duplicate/.test(w)) for (const d of D) if (d.n.length > 3 && new RegExp('\\b' + d.n.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b').test(w)) bad.push(`unobtainable ${u.id} blames ${d.id}, which the wiki lists at Act ${d.t}`);
    const sets = E.sets[u.id]; if (!sets) continue;
    const nm = x => x.startsWith('#') ? x.split('/').pop() : (NM[x] || (BYID[x] || {}).n || x.split(':')[1].replace(/_/g, ' '));
    if (!sets.some(s => s.some(x => w.includes(nm(x).toLowerCase())))) bad.push(`unobtainable ${u.id} has a pack recipe its reason does not name: ${u.why}`); } }
// gear-logic-combat-11: no conditional line is summed in the planner's Stat totals
for (const d of D) for (const s of statsOf(d)) if (/\b(to|against|for each|per|when|while)\b/i.test(s.k)) bad.push(d.n + ': conditional stat "' + s.k + '" summed in Stat totals');
// copy-docs-01: the tooltip of an estimated curio says so
{ const d = D.find(d => d.pe); if (d) { const n = document.createElement('a'); n.dataset.t = d.ix; document.body.append(n); showTipBase(n);
  if (!/estimate/.test(document.querySelector('#tip .trt')?.textContent || '')) bad.push(d.n + ': tooltip tier lacks the estimate label'); hideTip(); n.remove(); } }
// app-logic-07 / app-logic-06: 'act:<roman>' matches that Act only ('act viii' contains 'iii' and 'vii'); a pill's x removes only its own token
{ const keep = JSON.stringify(st); Object.assign(st, {c: [], g: [], r: [], x: [], m: '', s: '', a: '', nw: false});
  for (const a of ORDER.concat(-1)) { st.q = 'act:' + ACT[a][0];
    if (D.filter(d => pass(d)).map(d => d.id).join() !== D.filter(d => d.t === a).map(d => d.id).join()) bad.push(`act:${ACT[a][0]} does not give exactly the Act's curios`); }
  const raws = q => { const P = parseQ(q); return [...P.t, ...Object.values(P.k).flat()].map(e => e.raw).sort().join('|'); };
  for (const q of ['ring slot:ring', 'sword swordsman', 'fire -mod:fire', 'mod:"a b" a']) { const all = q.match(/-?[a-z]+:"[^"]*"?|-?"[^"]*"?|\S+/gi);
    for (const r of all) { st.q = q; const left = qDrop(r), want = all.slice(); want.splice(want.indexOf(r), 1); if (raws(left) !== want.sort().join('|')) bad.push(`qDrop('${r}') on '${q}' leaves '${left}'`); } }
  Object.assign(st, JSON.parse(keep)); }
