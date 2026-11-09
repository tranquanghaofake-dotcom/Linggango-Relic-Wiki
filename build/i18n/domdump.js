// Proof that English did not change: <main> and sidebar HTML, tab title and title-screen buttons of 17 routes in three states (plain, "I'm here" at Act 3, filters on).
// Build the commit before your change in a scratch copy (git archive <commit> | tar -x -C <dir>; run its build/patches/apply_all.sh), then:
//   NODE_PATH=$(npm root -g) node build/i18n/domdump.js <dir>/index.html /tmp/before.json ; NODE_PATH=$(npm root -g) node build/i18n/domdump.js index.html /tmp/after.json ; python3 build/i18n/domcmp.py /tmp/before.json /tmp/after.json
const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
const ROUTES = ['#', '#act/0', '#act/2', '#act/5', '#act/6', '#act/12', '#act/-1', '#act/99', '#i5', '#i700', '#g12', '#gs3', '#boss/iron_colossus', '#bosses', '#mechanics', '#changes', '#home'];
const FILT = '{"c":["ME"],"r":["4","5"],"x":[],"g":[],"m":"","s":"Ring","a":"","q":"role:melee -mod:brutality","nw":false,"sort":"a","dir":1,"cl":[],"op":null,"rl":3,"rq":-1}';
const norm = h => h.replace(/data:image\/[a-z]+;base64,[A-Za-z0-9+\/=]+/g, 'DATA').replace(/blob:null\/[0-9a-f-]+/g, 'BLOB').replace(/class="([^"]*)"/g, (m, c) => 'class="' + c.split(/\s+/).filter(x => !/^(seen|seen2|in)$/.test(x)).sort().join(' ') + '"');
(async () => {
  const [, , html, out, lang] = process.argv; const b = await chromium.launch(), res = {};
  for (const [name, here, lgw2] of [['', null, null], ['here3 ', 3, null], ['filt ', null, FILT]]) {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' }), p = await ctx.newPage();
    await p.addInitScript(([h, f]) => { try { localStorage.clear(); if (h !== null) localStorage.setItem('lgw-here', String(h)); if (f) localStorage.setItem('lgw2', f); } catch (e) {} }, [here, lgw2]);
    await p.goto('file://' + path.resolve(html) + (lang ? '?lang=' + lang : ''), { waitUntil: 'load' }); await p.waitForTimeout(1500);
    for (const r of ROUTES) {
      await p.evaluate(h => { location.hash = h; render(); }, r); await p.waitForTimeout(500);
      const o = await p.evaluate(() => ({ title: document.title, main: document.getElementById('main').innerHTML, side: document.getElementById('side').innerHTML, tbtns: (document.querySelector('.tbtns') || {}).innerHTML || '' }));
      res[name + r] = { title: o.title, main: norm(o.main), side: norm(o.side), tbtns: o.tbtns };
    }
    await ctx.close();
  }
  fs.writeFileSync(out, JSON.stringify(res)); console.log('route states dumped:', Object.keys(res).length); await b.close();
})();
