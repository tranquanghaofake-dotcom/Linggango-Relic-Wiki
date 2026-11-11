// node build/i18n/tools/dump_gear.js <index.html> <out.json> [lang]: <main> HTML of the Equipment list in several states, a spread of weapon, armor and set pages, curio pages with a measured-in-game section, and gear tooltips (inline style attributes are dropped: a timing effect adds or removes them)
const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
const norm = h => h.replace(/data:image\/[a-z]+;base64,[A-Za-z0-9+\/=]+/g, 'DATA').replace(/blob:null\/[0-9a-f-]+/g, 'BLOB').replace(/ style="[^"]*"/g, '').replace(/(<img alt="[^"]*" decoding="async" src="DATA")[^>]*>/g, '$1>').replace(/<canvas class="rcv"[^>]*><\/canvas><div class="rfx" aria-hidden="true">[\s\S]*?<\/div>/g, 'ROOMFX').replace(/ data-px="\d+"/g, '').replace(/ data-p="\d+"/g, '').replace(/(<canvas class="rcv" aria-hidden="true")( width="\d+" height="\d+")?/g, '$1').replace(/class="([^"]*)"/g, (x, c) => 'class="' + c.split(/\s+/).filter(y => !/^(seen|seen2|in|on)$/.test(y)).sort().join(' ') + '"');
(async () => {
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  await p.goto('file://' + path.resolve(process.argv[2]) + (process.argv[4] ? '?lang=' + process.argv[4] : ''), { waitUntil: 'load' }); await p.waitForTimeout(1500);
  const picks = await p.evaluate(() => {
    const pickG = [], pickS = [], pickC = [];
    const addG = f => { const l = GE.filter(g => { try { return f(g) } catch (e) { return false } }); for (const g of l.slice(0, 3)) if (!pickG.includes(g.ix)) pickG.push(g.ix) };
    const addS = f => { const l = GS.filter(g => { try { return f(g) } catch (e) { return false } }); for (const g of l.slice(0, 2)) if (!pickS.includes(g.ix)) pickS.push(g.ix) };
    addG(g => g.ms && g.ms.sw && !g.ms.st); addG(g => g.ms && g.ms.st === 'nodmg'); addG(g => g.ms && g.ms.st === 'nomelee'); addG(g => g.ms && g.ms.st === 'cond'); addG(g => g.ms && g.ms.st === 'dull'); addG(g => g.ms && g.ms.st === 'once'); addG(g => g.ms && g.ms.pct); addG(g => g.ms && g.ms.st === 'grows'); addG(g => g.ms && g.ms.swx);
    addG(g => g.fx && g.fx.some(r => r.fire !== undefined)); addG(g => g.fx && g.fx.some(r => r.heal !== undefined)); addG(g => g.fx && g.fx.some(r => r.ms)); addG(g => g.fx && g.fx.some(r => r.unseen)); addG(g => g.fx && g.fx.some(r => r.doubt)); addG(g => g.fx && g.fx.some(r => r.src)); addG(g => g.fx && g.fx.some(r => r.maybe)); addG(g => g.fx && g.fx.some(r => r.chance && r.chance < 1)); addG(g => g.tip && g.tip.length);
    addG(g => g.ga); addG(g => g.est); addG(g => g.lv && g.lv.length); addG(g => g.mg); addG(g => g.k === 'ranged'); addG(g => g.k === 'magic'); addG(g => g.k === 'summon'); addG(g => g.k === 'armor'); addG(g => g.ob); addG(g => g.ms && g.ms.dumpad != null); addG(g => !g.rc || !g.rc.length);
    for (let i = 0; i < 10; i++) if (GE[i * 150] && !pickG.includes(i * 150)) pickG.push(i * 150);
    addS(g => g.ms && g.ms.bonus); addS(g => g.ms && g.ms.evr); addS(g => !g.kn); addS(g => g.fx && g.fx.length); addS(g => g.dtk); addS(g => g.hp);
    for (let i = 0; i < 6; i++) if (GS[i * 50] && !pickS.includes(i * 50)) pickS.push(i * 50);
    for (const d of D) { if (typeof CM !== 'undefined' && CM[d.id] && pickC.length < 24 && (pickC.length < 8 || Math.random() < 0)) pickC.push(d.ix) }
    const cm = D.filter(d => typeof CM !== 'undefined' && CM[d.id]); const f = x => cm.find(d => { try { return x(CM[d.id]) } catch (e) { return false } });
    for (const x of [m => !(Object.keys(m.d || {}).length || m.hit || Object.keys(m.tk || {}).length || (m.fx || []).length || (m.tfx || []).length || m.hp || m.fire || m.heal || (m.neg || []).length || m.blk), m => m.blk, m => (m.neg || []).some(k => k !== 'fall'), m => (m.neg || []).includes('fall'), m => m.fire, m => m.heal, m => (m.tfx || []).length, m => (m.fx || []).length, m => m.hit, m => m.hp]) { const d = f(x); if (d && !pickC.includes(d.ix)) pickC.push(d.ix) }
    return { g: pickG, s: pickS, c: pickC };
  });
  const out = {};
  const grab = async h => { await p.evaluate(h => { location.hash = h }, h); await p.waitForTimeout(220); return p.evaluate(n => n, null).then(() => p.evaluate(() => document.querySelector('main').innerHTML)) };
  for (const h of ['#gear', '#gear/0/ME/w', '#gear/5/RA/a', '#gear/9/MA/c', '#gear/3/SU/w', '#gear/6.1/ME/a', '#gear/99', '#gear/12/ME/c']) out[h] = norm(await grab(h));
  await p.evaluate(() => { GSTATE.q = 'sword'; gearPage('#gear/0/ME/w') }); out['search sword'] = norm(await p.evaluate(() => document.querySelector('main').innerHTML));
  await p.evaluate(() => { GSTATE.q = 'zzzz'; gearPage('#gear/0/ME/w') }); out['search none'] = norm(await p.evaluate(() => document.querySelector('main').innerHTML));
  await p.evaluate(() => { GSTATE.q = ''; GALL = true; gearPage('#gear/12/ME/w'); }); out['all'] = norm(await p.evaluate(() => document.querySelector('main').innerHTML)); await p.evaluate(() => { GALL = false });
  for (const ix of picks.g) out['g' + ix] = norm(await grab('#g' + ix));
  for (const ix of picks.s) out['gs' + ix] = norm(await grab('#gs' + ix));
  for (const ix of picks.c) out['i' + ix] = norm((await grab('#i' + ix)).replace(/<details class="tipx">[\s\S]*?<\/details>/g, 'TIPX'));
  out.tips = await p.evaluate(([gs, ss]) => { const r = {}; for (const k of [...gs.map(i => 'g' + i), ...ss.map(i => 's' + i)]) { const n = document.createElement('a'); n.dataset.t = k; document.body.appendChild(n); try { gearTip(n); r[k] = document.getElementById('tip').innerHTML.replace(/data:image\/[a-z]+;base64,[A-Za-z0-9+\/=]+/g, 'DATA').replace(/blob:null\/[0-9a-f-]+/g, 'BLOB').replace(/ style="[^"]*"/g, '').replace(/(<img alt="[^"]*" decoding="async" src="DATA")[^>]*>/g, '$1>').replace(/<canvas class="rcv"[^>]*><\/canvas><div class="rfx" aria-hidden="true">[\s\S]*?<\/div>/g, 'ROOMFX').replace(/ data-px="\d+"/g, '').replace(/ data-p="\d+"/g, '').replace(/(<canvas class="rcv" aria-hidden="true")( width="\d+" height="\d+")?/g, '$1') } catch (e) { r[k] = 'ERR ' + e.message } n.remove() } return r }, [picks.g, picks.s]);
  fs.writeFileSync(process.argv[3], JSON.stringify(out)); console.log('gear pages dumped:', Object.keys(out).length, '| weapons', picks.g.length, 'sets', picks.s.length, 'curios', picks.c.length); await b.close();
})();
