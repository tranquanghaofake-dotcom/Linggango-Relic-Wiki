/* Curio power tiers for the Curios page, from the in-game measurement (patches/curio_measure.json).
   Run after a build (apply_all.sh does): opens the built site in Chromium and reads, for every curio that Equipment -> Curios
   tiers, its best tier over the four playstyles at its own Act (gTierOf in gear.js: how much it adds to a typical build of that
   Act, next to the fifth best curio). S..D become the Curios page tiers Mythic..Uncommon. The scores do not depend on these
   tiers, so a second run writes the same file. A curio measured to help, under the floor of every tier, whose text is only attribute numbers (gPlain) gets Common (0); one with a mechanic the test cannot see keeps its text rating. Curios the test cannot see (a condition, a chance, loot) keep the tier data.js gives them (from their text).
   Usage: NODE_PATH=$(npm root -g) node patches/curio_tiers.js */
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const root = path.resolve(__dirname, '..', '..'), out = path.join(__dirname, 'curio_tiers.json')
  const b = await chromium.launch(); const p = await b.newPage()
  await p.goto('file://' + root + '/index.html#gear'); await p.waitForFunction(() => typeof gTierOf === 'function' && typeof CM !== 'undefined', null, { timeout: 60000 })
  const r = await p.evaluate(() => {
    const L = { S: 5, A: 4, B: 3, C: 2, D: 1 }, o = {}
    for (const d of D) {
      if (d.r === 6 || !CM[d.id] || gCtx(d)) continue
      let best = 0, role = ''
      for (const r of ['ME', 'RA', 'MA', 'SU']) { const t = gTierOf(d, d.t, r, 'c'); if (t && L[t] > best) { best = L[t]; role = r } }
      if (best) o[d.id] = [best, role]
      else {   // measured to help, under the floor of every tier (GFLOOR of the fifth best) and with a text of plain attribute numbers (gPlain): the lowest rank, Common (0), by the playstyle it helps most
        let g = 0; for (const r of ['ME', 'RA', 'MA', 'SU']) { const v = gCurioScore(d, r, d.t) - 1; if (v > g) { g = v; role = r } }
        if (g > .005 && gPlain(d)) o[d.id] = [0, role] }
    }
    return o })
  await b.close()
  const s = JSON.stringify(r, Object.keys(r).sort(), 0).replace(/\],/g, '],\n')
  const old = fs.existsSync(out) ? fs.readFileSync(out, 'utf8') : ''
  if (old !== s) fs.writeFileSync(out, s)
  console.log('curio_tiers:', Object.keys(r).length, 'curios tiered from the measurement' + (old === s ? ' (unchanged)' : ' (changed)'))
  process.exit(old === s ? 0 : 3)
})()
