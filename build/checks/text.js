// Text and copy: stat icons, guide and ritual text, plurals, names, the footer date. Ported from the audit fix pass of 2026-10-31
// (pending invariants, groups app-js, wiki-patches and template); each block names the finding it guards. Runs in the page
// (check.js: `bad` and `acts` in scope).
const main = () => document.getElementById('main');
// ui-desktop-02: fmt() gives one icon per stat phrase (a later pattern re-matched inside a phrase an earlier one had claimed:
// 'Attack [haste]Speed', two icons before 'Armor Toughness')
{ const L = [];
  GE.forEach(g => { gStats(g).forEach(([, n, v]) => L.push(`${v} ${n}`)); gBonus(g).forEach(t => L.push(t)); });
  GS.forEach(s => { if (s.kn) L.push(`${gRound(s.arm)} Armor`, `${gRound(s.tough)} Armor Toughness`); if (s.hp) L.push(`+${gRound(s.hp)} Max Health`); });
  D.forEach(d => { L.push(d.fx); d.st.forEach(x => L.push(String(x))); });
  const two = L.filter(t => /<\/i><i class="ai"/.test(fmt(t)) || /<\/i><i class="ai"/.test(statLine(t)));
  two.slice(0, 5).forEach(t => bad.push('fmt two icons side by side: ' + t)); if (two.length > 5) bad.push(`fmt two icons side by side on ${two.length} lines`);
  for (const t of ['0.8 Attack Speed', '8 Armor Toughness', '+13% Arrow Damage']) { const c = (fmt(t).match(/<i class="ai"/g) || []).length; if (c !== 1) bad.push(`fmt('${t}') draws ${c} icons, not 1`); } }
// copy-docs-05: guide text carries no book markup ($( codes, tags, empty key slots)
for (const [k, v] of Object.entries(GUIDE)) if (/<\/?[a-z][a-z0-9]*\/?>|\[\s*\]|%%|\bwith ,|\$\(/.test(v.t || '')) bad.push('guide text with book markup: ' + k);
// Goety ritual types carry their JEI names ('... Ritual', not 'Te Magic', 'The-End' or 'Rituals')
for (const [k, v] of Object.entries(GOETY.types)) if (!/ Ritual( \(Goety Revelation\))?$/.test(v.name) || /Te Magic|The-End|Rituals/.test(v.name)) bad.push('ritual type name not the JEI name: ' + k + '=' + v.name);
// the Culinary ritual's example layout is the whole 200x199 picture (it was cropped: the right column and the bottom row black)
{ const s = GOETY.types.culinary?.img; if (!s) bad.push('culinary ritual has no picture'); else {
  const i = new Image(); i.src = 'data:image/webp;base64,' + s; await i.decode().catch(() => {});
  if (i.naturalWidth !== 200 || i.naturalHeight !== 199) bad.push('culinary picture ' + i.naturalWidth + 'x' + i.naturalHeight); else {
    const c = new OffscreenCanvas(200, 199).getContext('2d'); c.drawImage(i, 0, 0); const px = (x, y) => [...c.getImageData(x, y, 1, 1).data.slice(0, 3)].some(v => v > 8);
    if (!px(199, 100)) bad.push('culinary picture: right column black');
    if (![...Array(200).keys()].some(x => px(x, 198))) bad.push('culinary picture: bottom row black'); } } }
// ui-desktop-20: the footer's 'Last checked' date is never older than the newest entry of the Changes page
{ const mon = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];
  const f = document.querySelector('footer.sfoot')?.textContent.match(/Last checked (\d{1,2}) ([A-Z][a-z]{2}) (\d{4})/);
  history.replaceState(null, '', '#changes'); render();
  const ds = [...main().querySelectorAll('section.s > h2')].map(h => (h.querySelector('.chtog') || h).textContent.trim().match(/^([A-Z][a-z]+) (\d{1,2}), (\d{4})$/)).filter(Boolean).map(m => Date.UTC(+m[3], mon.indexOf(m[1].slice(0, 3).toLowerCase()), +m[2]));
  if (!f) bad.push('footer: no "Last checked D Mon YYYY"'); else if (!ds.length) bad.push('Changes page: no dated section');
  else if (Date.UTC(+f[3], mon.indexOf(f[2].toLowerCase()), +f[1]) < Math.max(...ds)) bad.push(`footer "Last checked ${f[1]} ${f[2]} ${f[3]}" is older than the newest Changes entry ${new Date(Math.max(...ds)).toISOString().slice(0, 10)}`); }
// copy-docs-14 / app-logic-10: plurals, the last Act, the Ender Dragon as a required boss (pages, quick search, The Path's Act VI panel)
{ for (const h of ['#mechanics', '#bosses', '#act/12', '#home', '#gear']) { history.replaceState(null, '', h); render(); const t = main().innerText;
    if (/\b1 (curios|rituals|pieces)\b/.test(t)) bad.push(h + ': singular count with a plural noun'); if (/Next boss: the end|next: the end/i.test(t)) bad.push(h + ': next boss "the end"'); }
  history.replaceState(null, '', location.pathname); render(); const i = document.getElementById('q');
  for (const q of ['chainmail', 'echo of tyros', 'ender dragon']) { i.value = q; i.dispatchEvent(new Event('input', {bubbles: true})); await new Promise(r => setTimeout(r, 400));
    const t = document.getElementById('qs').innerText; if (/\b1 (curios|rituals|pieces)\b|\bArmors\b/.test(t)) bad.push('quick search ' + q + ': plural slip');
    if (q === 'ender dragon') { const r = document.querySelector('#qs a[href="#boss/ender_dragon"] small'); if (!r || !/^Required boss, opens /.test(r.textContent)) bad.push('ender dragon called ' + (r && r.textContent)); } }
  i.value = ''; i.dispatchEvent(new Event('input', {bubbles: true}));
  if (!/Boss to beat next/.test(pPanelInner(6))) bad.push('Act VI panel calls the Ender Dragon a Keeper');
  if (Object.values(ACT).some(a => /Keeper of the Calamities/.test(a[1]))) bad.push('wiki-made Keeper of the Calamities');
  if (D.some(d => d.m === 'Covenant of the Seven') || !minfo('Sanctified Legacy')) bad.push('Sanctified Legacy mod label/MINFO'); }
// copy-docs-07: one id, one name across the boss drop lists and summon ingredients (Redstone vs Redstone Dust)
{ const nm = {}; const see = (id, n, w) => { if (!id || !n) return; (nm[id] = nm[id] || new Map()).set(n, w); };
  for (const b in SIDEB) for (const x of SIDEB[b].drops || []) see(x.id, x.n, 'SIDEB ' + b);
  for (const k in SUM) for (const x of SUM[k].ings || []) see(x.id, x.n, 'SUM ' + k);
  for (const id in nm) if (nm[id].size > 1) bad.push('two names ' + id + ': ' + [...nm[id]].map(([n, w]) => n + ' (' + w + ')').join(' / ')); }
// copy-docs-10: every mod in MINFO is a mod some curio carries
for (const m in MINFO) if (!D.some(d => d.m === m)) bad.push('MINFO entry for a mod no curio carries: ' + m);
