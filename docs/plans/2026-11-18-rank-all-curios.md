# Rank every curio (2026-11-18)

**Why**: of 1,321 curios only 255 had a tier (counted 2026-11-18): the game test, a bare player hitting a pig, sees nothing for 692 of them (a condition, a chance, an active key, loot), 64 are held back for a condition the test hid, 94 helped but fell under the floor of every tier, 17 are Looting Charms (rarity 6).

**Rule**: every curio gets a place, and the page says what kind of evidence put it there. Three layers, each shipped and looked at before the next:
1. **Measured** (done 2026-11-18, 277 curios: 255 + 22): the existing score (gear.js `gCurioScore`, against the fifth best of the Act). A curio measured to help but under every tier's floor is Common (0) only when its text is plain attribute numbers (`gPlain`): 22 curios. The other 72 under the floor have a mechanic the test cannot see (Ankh Aegis: +5 armor measured, but its value is immunity to nine effects); ranking them Common would be wrong, so they wait for layers 2 and 3.
2. **Expected value from its own text** (started 2026-11-18 with Lucky Dice, Fateful Coin, Nullifying Dice: `GHITCODE`/`GTKCODE`): odds x size from the item's own text, times an uptime for a condition. The assumption is written on the item's page and here, and the tier carries the "estimate" label.
3. **Utility** (loot, mining, movement, comfort): ranked among its own kind by that kind's number, not mixed with combat power.

**Done when**: every curio has a tier or a stated reason it has none; `d.pe` ("estimate") only on layers 2 and 3; an invariant per layer; pages of each layer looked at; `check.sh` green.

**Assumptions for layer 2** (added here as they are made; a number with no source in the pack's files is not used): none yet beyond the three items above. The rule "each Luck point = +2% damage, +2.5% attack speed, +2% dodge" is in a hand-written table in app.js with no source in the pack's files, so it is not used.

## Result of layer 2 (2026-11-18, same day)
A strict reader (every clause of the text must be a stat the model knows) was tried on the 1,027 curios still without a measured tier: it fully reads 7, and those 6 Brutality crit curios were already measured (their attributes are in `curio_measure.json`), so nothing new came from it. The rest are too different (immunities, activated abilities, movement, loot, spells and minions, conditions) for one number per curio that is not invented. Decision: no invented numbers. What was done instead:
- the lower rank (Common) now also covers the curios whose only text is crit chance, crit damage or lifesteal (`gPlain` no longer counts "crit chance" as a chance of something): 282 tiered, up from 277;
- every curio still rated from its text says what its text is about (`gUnrKind`: immunity, an activated ability, a chance the text does not size, loot/mining/luck, movement, a spell or minion effect, a condition), so the reader sees why it has no measured tier.
Layer 3 (utility ranked among its own kind) and a per-curio expected value for single items remain open; each needs a number from the pack's files.

## Layer 3, first part: immunity (2026-11-18)
The owner chose how to rank immunity curios: by how strong the effects they block are and how many. `patches/effect_threat.json` weights each effect or hazard 1 to 3 (3 damages you or can kill, 2 cripples what you do or see, 1 a nuisance; a judgement, labelled as an estimate: the export has no strength per effect, `effects.json` gives Weakness an amount of 0 and Wither nothing). Per curio: the distinct things its text says it is immune to, summed (`reduced X` half, `most` three quarters, `all effects` every status effect in the table, `N harmful effects` N times their mean weight), then tiered S to D against the fifth best like the rest. The pack's own files were not available in the repo, so no number comes from them. Only the blocking is scored; the page says so and lists what it did not count.
