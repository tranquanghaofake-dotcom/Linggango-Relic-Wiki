// Page check for the built wiki (Chromium, no network).
// Usage: NODE_PATH=$(npm root -g) node build/check.js [dist/Linggango_Relic_Wiki.html]
// Fails (exit 1) on: a script error, an empty gear item or set page, a broken <img> on any detail page (curio, gear,
// set, boss, side boss: each picture is awaited with decode(), since a fresh <img> is not complete in the task that
// inserts it), a boss card on The Path (home page) with no landscape background, or a detail page that is not drawn
// with the shared article layout (title, infobox, navbox, a heading on every section).
const { chromium } = require('playwright'), path = require('path'), fs = require('fs');
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
  // text checks on each detail page, run right after the page is drawn (ported from checks/routes.js so each page is drawn
  // once): data-t resolves (app-logic-13); no undefined/NaN, raw game template, key placeholder, SRG name or JSON list, no
  // 'the The' (detail-pages-checks-05/-09, phone-17); no namespaced id in a recipe list or summon table (-07/-08); gear and set
  // pages: no empty infobox value, broken lock sentence, short Act label, '#mod/' link to a mod without curios, space before
  // punctuation in the lead (-02/-12, app-logic-01); curio pages: no raw id outside the id box, no empty sibling box (app-logic-09);
  // side pages: external links are web addresses
  const PAGE = h => {
    const out = [], m = document.getElementById('main'), t = m.textContent, rx = /%\d*\$?[sd]\b|%%|\[\]|\+-\d|\b[mf]_\d{3,}_|\["[a-z_]+: ?[a-z_]+"/, ID = /\b[a-z][a-z0-9_]{2,}:[a-z0-9_]/;
    for (const n of m.querySelectorAll('[data-t]')) { const v = n.dataset.t;
      if (!(/^\d+$/.test(v) ? D[+v] : /^g\d+$/.test(v) ? GE[+v.slice(1)] : /^s\d+$/.test(v) ? GS[+v.slice(1)] : 0)) out.push(h + ': data-t "' + v + '" resolves to nothing'); }
    if (/\bundefined\b|\bNaN\b/.test(t)) out.push(h + ': prints undefined or NaN');
    const r = t.match(rx); if (r) out.push(h + ': raw game text ' + JSON.stringify(t.slice(Math.max(0, r.index - 30), r.index + 30)));
    if (/\b(the|The)\s+(the|The)\b/.test(t)) out.push(h + ': "the The"');
    if (/^#(i|boss\/)/.test(h)) for (const c of m.querySelectorAll('.mcl, table.sumings')) { const w = document.createTreeWalker(c, NodeFilter.SHOW_TEXT);
      for (let n; (n = w.nextNode());) if (ID.test(n.data)) { out.push(h + ': namespaced id in a recipe list: ' + n.data.trim().slice(0, 60)); break; } }
    if (/^#gs?\d/.test(h)) {
      if ([...m.querySelectorAll('.ip-info dd')].some(d => !d.textContent.trim())) out.push(h + ': empty infobox value');
      const x = t.match(/\bActs? Dragon\b|–Dragon\b|Dragon–|\b0–I–[IVX]|Outclassed from (?:Dragon|[IVX0])|(?:until|once)\s{2,}falls/); if (x) out.push(h + ': ' + x[0]);
      for (const a of m.querySelectorAll('a[href^="#mod/"]')) { const n = decodeURIComponent(a.getAttribute('href').slice(5)); if (!(MODS.some(([y]) => y === n) && D.some(d => d.m === n))) out.push(h + ': #mod link to a mod with no curios: ' + n); }
      if (/\s[,.]/.test(m.querySelector('.ip-lead')?.textContent || '')) out.push(h + ': lead with a space before punctuation'); }
    if (/^#i\d/.test(h)) { const w = document.createTreeWalker(m, NodeFilter.SHOW_TEXT);
      for (let n; (n = w.nextNode());) { if (n.parentElement.closest('.ip-id,code,.tg,script,style')) continue; if (ID.test(n.textContent)) { out.push(h + ': raw id ' + n.textContent.trim().slice(0, 60)); break; } }
      const s = m.querySelector('.sib'); if (s && !s.querySelector('.gridc > *')) out.push('empty .sib on ' + h); }
    if (/^#side\//.test(h)) for (const a of m.querySelectorAll('a[target=_blank]')) if (!/^https?:/.test(a.getAttribute('href'))) out.push('non-URL link on ' + h);
    return out; };
  // render a route, then [text length, pictures that fail to decode]; a picture still loading after 2 s counts as fine
  const VIEW = async h => {
    location.hash = h; render(); const m = document.getElementById('main'), im = [...m.querySelectorAll('img')];
    im.forEach(i => { if (i.loading === 'lazy') i.loading = 'eager'; });
    const f = await Promise.all(im.map(i => Promise.race([i.decode().then(() => 0, () => 1), new Promise(r => setTimeout(() => r(0), 2000))])));
    return [m.innerText.length, f.reduce((s, x) => s + x, 0)];
  };
  const [ne, ns] = await p.evaluate(() => [GE.length, GS.length]);
  const lay = [], brokenImg = [], txt = [];
  for (const [pre, n] of [['#g', ne], ['#gs', ns]])
    for (let i = 0; i < n; i++) {
      const r = await p.evaluate(VIEW, pre + i);
      if (r[0] < 40 || r[1]) bad.push(pre + i);
      const l = await p.evaluate(LAYOUT); if (l) lay.push(pre + i + ' ' + l);
      txt.push(...await p.evaluate(PAGE, pre + i));
    }
  const others = await p.evaluate(() => [...D.map(d => '#i' + d.ix), ...KEEPERS().concat('ender_dragon').map(k => '#boss/' + k), ...Object.keys(SIDEB).map(n => '#side/' + encodeURIComponent(n))]);
  for (const h of others) {
    const r = await p.evaluate(VIEW, h); if (r[1]) brokenImg.push(h + ' ' + r[1]);
    const l = await p.evaluate(LAYOUT); if (l) lay.push(h + ' ' + l);
    txt.push(...await p.evaluate(PAGE, h));
  }
  // data and ranking invariants (each one is a bug that has happened)
  const inv = await p.evaluate(() => {
    const bad = [], acts = ORDER.filter(x => x != -1), A = new Set(ORDER);
    for (const g of [...GE, ...GS]) {
      const id = g.id || g.k;
      if (!A.has(g.a)) bad.push('act ' + id + ' ' + g.a);              // 6.1 sat at index -1: a battleaxe showed at Act 0
      if (g.ga && !A.has(g.ga)) bad.push('gate ' + id + ' ' + g.ga);
      for (const r in g.sc) if (g.sc[r] !== null && !Number.isFinite(g.sc[r])) bad.push('score ' + id + ' ' + r);   // null: not ranked (gUnr)
    }
    // a melee weapon has a damage score, unless the game showed it deals none (gNoMelee: Create's cardboard sword cancels its own hit)
    for (const g of GE) if (g.k === 'melee' && g.dmg != null && !(g.sc.ME > 0) && !gNoMelee(g)) bad.push('dps ' + g.id);
    if ('TA' in GROLE) bad.push('Tank role is back');                   // retired: four playstyles only
    // a set's score is a function of the Act it is judged at: finite and positive for every role and Act (a set with no numbers, s.f
    // null, is not ranked: null everywhere)
    for (const s of GS) for (const r in GROLE) for (const a of acts) { const v = gScore(s, r, a); if (s.f ? !(v > 0) : v !== null) bad.push(`set score ${s.k} ${r} ${a}`); }
    // every playstyle keeps real options at every Act (Ranged armor once stopped at Act V, Mage weapons had one pick at Act 0).
    // Ranged and Summon weapons are not ranked until their shots and minions are measured in game (checks/gear.js: tier-act)
    const need = {w: {ME: 3, RA: 0, MA: 3, SU: 0}, a: {ME: 5, RA: 5, MA: 5, SU: 5}};
    for (const w in need) for (const r in need[w]) for (const a of acts) {
      const n = gTiers(a, r, w).reduce((s, t) => s + t[1].length, 0), min = w === 'a' && r === 'SU' && a >= 2 ? 2 : need[w][r];
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
    return bad;
  });
  // more invariants, one file per topic in build/checks/: each is a function body run in the page with `bad` (an array to
  // push messages into) and `acts` (ORDER without -1) in scope; a new bug's invariant goes in a new or existing file there.
  // The body may `await`; `await patchJSON('x.json')` reads build/patches/x.json (so a check compares the page with the file itself)
  const CK = path.join(__dirname, 'checks');
  await p.exposeFunction('patchJSON', f => JSON.parse(fs.readFileSync(path.join(__dirname, 'patches', path.basename(f)), 'utf8')));
  for (const f of fs.readdirSync(CK).filter(x => x.endsWith('.js')).sort())
    inv.push(...(await p.evaluate(`(async () => { const bad = [], acts = ORDER.filter(x => x != -1);\n${fs.readFileSync(path.join(CK, f), 'utf8')}\nreturn bad; })()`)).map(x => f + ': ' + x));
  console.log(`invariants: ${inv.length} broken ${inv.slice(0, 8).join(' | ')}`);
  console.log(`path cards ${cards.length}, without background: ${noBg.length} ${noBg.join(', ')}`);
  console.log(`gear pages ${ne}, sets ${ns}, empty or broken: ${bad.length} ${bad.slice(0, 10).join(' ')}`);
  console.log(`curio, Keeper and side boss pages ${others.length}, with a broken picture: ${brokenImg.length} ${brokenImg.slice(0, 8).join(' | ')}`);
  console.log(`detail pages ${ne + ns + others.length}, off the shared layout: ${lay.length} ${lay.slice(0, 6).join(' | ')}`);
  console.log(`page text: ${txt.length} problems ${txt.slice(0, 6).join(' | ')}`);
  console.log(`script errors: ${errs.length} ${errs.slice(0, 3).join(' | ')}`);
  await b.close();
  process.exit(txt.length || errs.length || inv.length || bad.length || brokenImg.length || lay.length || noBg.length || !cards.length ? 1 : 0);
})();
