// Routes: every detail page's text, odd and bad routes, titles, the Filters column, Start here and the Act pages. Ported from the
// audit fix pass of 2026-10-31 (pending invariants, groups gear-js, curio-data, wiki-patches, app-js, template and docs); each
// block names the finding it guards. Runs in the page (check.js: `bad` and `acts` in scope). Routes are drawn with
// replaceState + render(), so no hashchange is queued behind the loop.
const go = h => { history.replaceState(null, '', h || location.pathname); render(); }, main = () => document.getElementById('main');
const ST = JSON.stringify(st);   // the filter state: '#slot/Ring' sets a slot filter, restored before Start here and at the end
// data-t on a page resolves to a curio, a gear item or a set (app-logic-13)
const dataT = h => { for (const n of main().querySelectorAll('[data-t]')) { const t = n.dataset.t;
  if (!(/^\d+$/.test(t) ? D[+t] : /^g\d+$/.test(t) ? GE[+t.slice(1)] : /^s\d+$/.test(t) ? GS[+t.slice(1)] : 0)) bad.push(h + ': data-t "' + t + '" resolves to nothing'); } };
// detail-pages-checks-05 / -09 / phone-17: no 'undefined' or NaN (closed <details> included), no raw game template, key placeholder,
// SRG name or JSON list, and no 'the The' ('Crafting the The Corrupted Tear')
const RAW = /%\d*\$?[sd]\b|%%|\[\]|\+-\d|\b[mf]_\d{3,}_|\["[a-z_]+: ?[a-z_]+"/;
const text = (h, grp) => { const t = main().textContent, m = t.match(RAW);
  if (/\bundefined\b|\bNaN\b/.test(t)) bad.push(h + ': prints undefined or NaN');
  if (m) bad.push(h + ': raw game text ' + JSON.stringify(t.slice(Math.max(0, m.index - 30), m.index + 30)));
  if (/\b(the|The)\s+(the|The)\b/.test(t)) bad.push(h + ': "the The"'); };
// detail-pages-checks-07/08: no namespaced item id in a recipe list (.mcl) or a summon table
const ID = /\b[a-z][a-z0-9_]{2,}:[a-z0-9_]/;
const recipeIds = h => { for (const c of main().querySelectorAll('.mcl, table.sumings')) { const w = document.createTreeWalker(c, NodeFilter.SHOW_TEXT);
  for (let n; (n = w.nextNode());) if (ID.test(n.data)) { bad.push(h + ': namespaced id in a recipe list: ' + n.data.trim().slice(0, 60)); return; } } };
// gear and set pages: no empty infobox value, no broken lock sentence or short Act label, no '#mod/' link to a mod with no curios,
// no space before a comma or full stop in the lead (detail-pages-checks-02 / -12, app-logic-01)
const SHORT = /\bActs? Dragon\b|–Dragon\b|Dragon–|\b0–I–[IVX]|Outclassed from (?:Dragon|[IVX0])|(?:until|once)\s{2,}falls/;
for (const [pre, xs] of [['#g', GE], ['#gs', GS]]) for (let i = 0; i < xs.length; i++) { const h = pre + i; go(h); const m = main();
  if ([...m.querySelectorAll('.ip-info dd')].some(d => !d.textContent.trim())) bad.push(h + ': empty infobox value');
  const x = m.textContent.match(SHORT); if (x) bad.push(h + ': ' + x[0]);
  for (const a of m.querySelectorAll('a[href^="#mod/"]')) { const n = decodeURIComponent(a.getAttribute('href').slice(5)); if (!(MODS.some(([y]) => y === n) && D.some(d => d.m === n))) bad.push(h + ': #mod link to a mod with no curios: ' + n); }
  if (/\s[,.]/.test(m.querySelector('.ip-lead')?.textContent || '')) bad.push(h + ': lead with a space before punctuation');
  text(h); dataT(h); }
// curio pages: also no raw item id anywhere in the text outside the id box, code and tag labels (detail-pages-checks-08), and the
// sibling box ('More ... curios') is never empty (app-logic-09)
for (const d of D) { const h = '#i' + d.ix; go(h); text(h); dataT(h); recipeIds(h);
  const w = document.createTreeWalker(main(), NodeFilter.SHOW_TEXT);
  for (let n; (n = w.nextNode());) { if (n.parentElement.closest('.ip-id,code,.tg,script,style')) continue; if (ID.test(n.textContent)) { bad.push(`${h}: raw id ${n.textContent.trim().slice(0, 60)}`); break; } }
  const s = main().querySelector('.sib'); if (s && !s.querySelector('.gridc > *')) bad.push('empty .sib on ' + h); }
// Keeper and side-boss pages; a side page's external links are web addresses (app-logic-09)
for (const k of KEEPERS().concat('ender_dragon')) { const h = '#boss/' + k; go(h); text(h); dataT(h); recipeIds(h); }
for (const n of Object.keys(SIDEB)) { const h = '#side/' + encodeURIComponent(n); go(h); text(h); dataT(h);
  for (const a of main().querySelectorAll('a[target=_blank]')) if (!/^https?:/.test(a.getAttribute('href'))) bad.push('non-URL link on ' + h); }
// app-logic-09 / detail-pages-checks-14: odd and bad routes draw a page with a title, never throw and never print undefined or NaN;
// '#gear/6.1/...' lands on Act VI; an unknown item says so instead of falling back silently
for (const h of ['#act/abc', '#act/1', '#act/6.1', '#act/6.2', '#act/13', '#i', '#i99999', '#iabc', '#g99999', '#gs99999', '#gear/6.1/ME/w', '#gear/6.2/RA/a', '#gear/99/XX/z', '#boss/nobody', '#side/Nobody', ...Object.keys(ACT).map(a => '#act/' + a)]) {
  try { go(h); } catch (e) { bad.push(h + ' throws ' + e.message); continue; }
  const m = main(); if (!m.querySelector('h1')?.textContent.trim()) bad.push('no h1 on ' + h);
  if (/\bundefined\b|\bNaN\b/.test(m.innerText)) bad.push('undefined/NaN on ' + h);
  if (/^#gear\/6\./.test(h) && document.querySelector('.gacts a[aria-current]')?.textContent !== 'VI') bad.push(h + ' not on Act VI');
  if (/^#gs?9/.test(h) && !/No page called/.test(m.textContent)) bad.push(h + ' falls back silently'); }
// docs-1: the Act pages are live (the hub, The Path, the navbox and the breadcrumbs link them): each has a title and curio cards (.gc)
for (const a of acts) { go('#act/' + a); const m = main(); if (!m.querySelector('h1')?.textContent.trim()) bad.push('#act/' + a + ' no title'); else if (!m.querySelector('.gc')) bad.push('#act/' + a + ' no curio cards'); }
// phone-18: a page's title starts with its nav label; 'Tier list' only on the Equipment pages
for (const a of document.querySelectorAll('nav.nav a')) { const t = a.textContent.trim(); go(a.getAttribute('href')); if (!document.title.startsWith(t)) bad.push(`nav ${t}: title ${document.title}`); }
for (const h of ['#home', '#slot/Ring', '#mods', '#bosses', '#mechanics', '#changes', '#nonsense']) { go(h); if (/Tier list/i.test(document.title)) bad.push(h + ': title ' + document.title); }
// ui-desktop-17: the Filters column shows next to the curio list only
for (const h of ['#build', '#gear', '#bosses', '#mechanics', '#changes', '#i5', '#g5', '#boss/arion', '#home']) { go(h);
  const none = getComputedStyle(document.getElementById('side')).display === 'none'; if (none !== (h !== '#home')) bad.push(h + ': #side display ' + (none ? 'none' : 'shown')); }
// ui-desktop-15 / app-logic-11: with each Act as 'I'm here', the first Start-here square says 'open at' and its page lists exactly that
// Act's curios; the run line counts stops on The Path, not Acts
{ Object.assign(st, JSON.parse(ST)); let keep = null; try { keep = localStorage.getItem('lgw-here'); } catch (e) {}
  for (const a of ORDER.filter(x => x >= 0)) { try { localStorage.setItem('lgw-here', String(a)); } catch (e) { break; }
    go(''); const run = document.getElementById('prun')?.textContent || '', s = document.querySelector('.sqs .sq'), href = s && s.getAttribute('href'), txt = s ? s.innerText : '';
    if (href) go(href); const m = (document.getElementById('bc')?.innerText || '').match(/of ([\d,]+) curios?/), n = m ? +m[1].replace(/,/g, '') : -1, want = D.filter(d => d.t === a).length;
    if (!/open at/.test(txt) || n !== want) bad.push(`start-here ${a}: "${txt}" ${href} shows ${n} of ${want}`);
    if (!/^Your run: .+ \(\d+ of \d+ on The Path\)$/.test(run)) bad.push(`run line ${a}: ${run}`); }
  try { keep === null ? localStorage.removeItem('lgw-here') : localStorage.setItem('lgw-here', keep); } catch (e) {} }
// a11y-perf-12: heading levels never rise by more than one (the footer's h4 under an h1/h2), and exactly one visible h1 per page
for (const h of ['#', '#home', '#gear', '#i536', '#boss/nyxaris']) { go(h);
  const vis = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6,[role=heading]')].filter(e => e.checkVisibility({checkVisibilityCSS: true}) && e.getClientRects().length);
  const lvl = e => { const a = parseInt(e.getAttribute('aria-level'), 10); return a >= 1 ? a : +e.tagName[1] || 2; }; let prev = 0;
  for (const e of vis) { const l = lvl(e); if (prev && l > prev + 1) bad.push(`headings ${h}: h${prev} -> h${l} "${e.textContent.trim().slice(0, 30)}"`); prev = l; }
  const n1 = vis.filter(e => lvl(e) === 1).length; if (n1 !== 1) bad.push(`headings ${h}: ${n1} h1`); }
Object.assign(st, JSON.parse(ST)); go('#home');
