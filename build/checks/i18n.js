// Languages (docs/plans/2026-11-08-multilingual.md). Runs in the page (check.js: `bad` in scope; the offline file has every pack inline).
// Every language draws the shell in its own words with nothing half-filled, English comes back untouched, a missing key shows English,
// and counted strings pick the language's CLDR plural form (Russian has four, Vietnamese one).
{ const en0 = [...document.querySelectorAll('[data-lg],[data-lgh]')].map(n => n.innerHTML).join('|'), at0 = [...document.querySelectorAll('[data-lga]')].map(n => n.outerHTML).join('|');
  for (const c of LANG_CODES.filter(x => x !== 'en')) {
    if (!I18N[c]) { bad.push('i18n: no pack for ' + c); continue; }
    useLang(c);
    const els = [...document.querySelectorAll('[data-lg],[data-lgh]')];
    for (const n of els) { const k = n.dataset.lg || n.dataset.lgh;
      if (!n.textContent.trim()) bad.push('i18n ' + c + ': empty ' + k);
      if (/\{\w+\}/.test(n.textContent)) bad.push('i18n ' + c + ': placeholder left in ' + k); }
    if (document.documentElement.lang !== c) bad.push('i18n: <html lang> is ' + document.documentElement.lang + ' for ' + c);
    if (els.map(n => n.innerHTML).join('|') === en0) bad.push('i18n ' + c + ': the shell is still English');
    if ([...document.querySelectorAll('[data-lga]')].map(n => n.outerHTML).join('|') === at0) bad.push('i18n ' + c + ': attributes (placeholder, aria-label) still English');
    if (document.getElementById('lang').value !== c) bad.push('i18n: the menu does not show ' + c);
  }
  useLang('en');
  if ([...document.querySelectorAll('[data-lg],[data-lgh]')].map(n => n.innerHTML).join('|') !== en0 || [...document.querySelectorAll('[data-lga]')].map(n => n.outerHTML).join('|') !== at0) bad.push('i18n: English did not come back after the languages');
  if (t('no.such.key', 'x {n}', { n: 2 }) !== 'x 2') bad.push('i18n: t() does not fall back to the English text');
  const f = { one: '{n} a', few: '{n} b', many: '{n} c', other: '{n} d' };
  useLang('ru'); const ru = [1, 2, 5, 21, 22, 25].map(n => tn('no.such.key', n, f)).join(',');
  if (ru !== '1 a,2 b,5 c,21 a,22 b,25 c') bad.push('i18n: Russian plural forms ' + ru);
  useLang('vi'); if (tn('no.such.key', 2, f) !== '2 d') bad.push('i18n: Vietnamese counted string ' + tn('no.such.key', 2, f));
  useLang('en'); if (tn('no.such.key', 1, f) !== '1 a' || tn('no.such.key', 2, f) !== '2 d') bad.push('i18n: English plural forms'); }
// Fonts: Russian draws in Monocraft's own Cyrillic faces and Vietnamese in VT323 (pixel faces, not the system fallback), and the Vietnamese page asks for VT323.
// A width test against the browser's default font does not work (Chromium picks a system face per missing glyph), so this asks which faces the text loads.
{ const ru = 'Путь испытаний Ёё', vi = 'Chế tạo bằng ấ ệ ử ữ Đường đi';
  const cyr = (fs, wt) => fs.some(f => f.status === 'loaded' && f.weight === wt && /U\+400/i.test(f.unicodeRange));
  if (!cyr(await document.fonts.load('32px Monocraft', ru), '400')) bad.push('fonts: no loaded Monocraft face for Cyrillic (regular)');
  if (!cyr(await document.fonts.load('700 32px Monocraft', ru), '700')) bad.push('fonts: no loaded Monocraft face for Cyrillic (bold)');
  if (!(await document.fonts.load('32px "VT323 vi"', vi)).some(f => f.family.includes('VT323') && f.status === 'loaded')) bad.push('fonts: VT323 not loaded for Vietnamese text');
  useLang('vi'); const lt = getComputedStyle(document.querySelector('.logo .lt')).fontFamily, h1 = getComputedStyle(document.querySelector('.top')).getPropertyValue('--title');
  if (!lt.includes('VT323 vi') || !h1.includes('VT323 vi')) bad.push('fonts: the Vietnamese page does not use VT323 for labels and titles: ' + lt + ' | ' + h1);
  useLang('ru'); if (getComputedStyle(document.querySelector('.logo .lt')).fontFamily.includes('VT323')) bad.push('fonts: VT323 leaked into the Russian page');
  useLang('en'); if (getComputedStyle(document.querySelector('.logo .lt')).fontFamily.includes('VT323')) bad.push('fonts: VT323 leaked into the English page'); }
// Pages drawn so far in the language (the hub, an Act page, an Act that does not exist): nothing half-filled, and every sentence they ask for
// is translated or kept in English on purpose (the pack's `keep`: proper names, rarity names). A sentence missing from tm/<lang>.json shows up here.
{ const h0 = location.hash;
  for (const c of LANG_CODES.filter(x => x !== 'en')) { useLang(c); window.__TRLOG = new Set();
    for (const h of ['#', '#act/2', '#act/99']) { location.hash = h; render();
      const t = document.getElementById('main').innerText; if (/\{\w+\}|\$\{|undefined|NaN|\[object/.test(t)) bad.push('i18n ' + c + ' ' + h + ': a placeholder or "undefined" shows on the page'); }
    const keep = new Set(I18N[c].keep || []);
    for (const en of window.__TRLOG) if (!trOf(en) && !keep.has(en)) bad.push('i18n ' + c + ': no translation for ' + JSON.stringify(en.replace('\u0001', ' | ')).slice(0, 80)); }
  window.__TRLOG = undefined; useLang('en'); location.hash = h0; render(); }

