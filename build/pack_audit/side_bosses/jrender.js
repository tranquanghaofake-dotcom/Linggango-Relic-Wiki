// Drives jrender.html: renders every model in IN (jmodel.py output joined with its texture: {name: {model, tex, yaw?}})
// and writes OUT {name: base64 png}. Usage: node jrender.js DIR IN OUT  (DIR holds jrender.html and node_modules/three)
const { chromium } = require('playwright'), fs = require('fs'), path = require('path');
(async () => {
  const [dir, inp, outp] = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--allow-file-access-from-files', '--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage(); p.on('pageerror', e => console.log('E', e.message));
  await p.goto('file://' + path.resolve(dir, 'jrender.html')); await p.waitForFunction('window.ready');
  const IN = JSON.parse(fs.readFileSync(inp)), out = {};
  for (const [k, v] of Object.entries(IN)) {
    try { out[k] = (await p.evaluate(([m, t, y]) => renderJava(m, t, y), [v.model, v.tex, v.yaw ?? -0.55])).split(',')[1]; }
    catch (e) { console.log(k, e.message); }
  }
  fs.writeFileSync(outp, JSON.stringify(out)); console.log(Object.keys(out).length, 'rendered'); await b.close();
})();
