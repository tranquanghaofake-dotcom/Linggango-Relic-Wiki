// Routes: every detail page's text, odd and bad routes, titles, the Filters column, Start here and the Act pages. Ported from the
// audit fix pass of 2026-10-31 (pending invariants, groups gear-js, curio-data, wiki-patches, app-js, template and docs); each
// block names the finding it guards. Runs in the page (check.js: `bad` and `acts` in scope). Routes are drawn with
// replaceState + render(), so no hashchange is queued behind the loop.
const go = h => { history.replaceState(null, '', h || location.pathname); render(); }, main = () => document.getElementById('main');
const ST = JSON.stringify(st);   // the filter state: '#slot/Ring' sets a slot filter, restored before Start here and at the end
// The per-page text checks (data-t, raw game text, ids in recipe lists, gear-page leads, curio raw ids, side links) run inside
// check.js's own pass over every detail page (PAGE), so each page is drawn once.
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
// ui-desktop-15 / app-logic-11: with each Act as 'I'm here', the open panel on the home page is that Act's and its "See N curios"
// button leads to a page that lists exactly that Act's curios (the Start-here squares that first carried this are gone: the
// panel answers the same question); the run line counts stops on The Path, not Acts
{ Object.assign(st, JSON.parse(ST)); let keep = null; try { keep = localStorage.getItem('lgw-here'); } catch (e) {}
  for (const a of ORDER.filter(x => x >= 0)) { try { localStorage.setItem('lgw-here', String(a)); } catch (e) { break; }
    go(''); const run = document.getElementById('prun')?.textContent || '', s = document.querySelector('#pmap .ppanel:not([hidden]) .pbtn a[href^="#act/"]'), href = s && s.getAttribute('href'), txt = s ? s.innerText : '';
    if (href) go(href); const m = (document.getElementById('bc')?.innerText || '').match(/of ([\d,]+) curios?/), n = m ? +m[1].replace(/,/g, '') : -1, want = D.filter(d => d.t === a).length;
    if (href !== '#act/' + a || !txt.includes(String(want)) || n !== want) bad.push(`open panel ${a}: "${txt}" ${href} shows ${n} of ${want}`);
    if (!/^Your run: .+ \(\d+ of \d+ on The Path\)$/.test(run)) bad.push(`run line ${a}: ${run}`); }
  try { keep === null ? localStorage.removeItem('lgw-here') : localStorage.setItem('lgw-here', keep); } catch (e) {} }
// a11y-perf-12: heading levels never rise by more than one (the footer's h4 under an h1/h2), and exactly one visible h1 per page
for (const h of ['#', '#home', '#gear', '#i536', '#boss/nyxaris']) { go(h);
  const vis = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6,[role=heading]')].filter(e => e.checkVisibility({checkVisibilityCSS: true}) && e.getClientRects().length);
  const lvl = e => { const a = parseInt(e.getAttribute('aria-level'), 10); return a >= 1 ? a : +e.tagName[1] || 2; }; let prev = 0;
  for (const e of vis) { const l = lvl(e); if (prev && l > prev + 1) bad.push(`headings ${h}: h${prev} -> h${l} "${e.textContent.trim().slice(0, 30)}"`); prev = l; }
  const n1 = vis.filter(e => lvl(e) === 1).length; if (n1 !== 1) bad.push(`headings ${h}: ${n1} h1`); }
Object.assign(st, JSON.parse(ST)); go('#home');
