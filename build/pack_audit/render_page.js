// Opens one of the three.js render pages in pack_audit/ (geo_icon_render.html, armor_render.html,
// side_bosses/jrender.html) in headless Chromium where it lies: the pages import build/geo2three.js and
// build/node_modules/three by relative path, so run `npm install --no-package-lock --prefix build` once (three@0.169.0, build/package.json)
// and nothing has to be copied next to them. WebGL runs on SwiftShader (no GPU in CI or a cloud session).
// Chromium: Playwright's own, or the binary named by PW_CHROMIUM.
//   const open = require('./render_page'); const { page, close } = await open('geo_icon_render.html');
const path = require('path'), fs = require('fs');
const { chromium } = (() => { try { return require('playwright'); } catch {
  return require(path.join(require('child_process').execSync('npm root -g').toString().trim(), 'playwright')); } })();
module.exports = async function open(html) {
  const f = path.resolve(__dirname, html), three = path.resolve(__dirname, '..', 'node_modules', 'three', 'build', 'three.module.js');
  if (!fs.existsSync(three)) throw new Error('three.js missing: run npm install --no-package-lock --prefix ' + path.resolve(__dirname, '..'));
  const b = await chromium.launch({ executablePath: process.env.PW_CHROMIUM || undefined,
    args: ['--allow-file-access-from-files', '--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await b.newPage();
  page.on('pageerror', e => console.log('page error:', e.message));
  await page.goto('file://' + f); await page.waitForFunction('window.ready');
  return { page, close: () => b.close() };
};
