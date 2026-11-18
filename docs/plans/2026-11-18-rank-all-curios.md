# Rank every curio (2026-11-18)

**Why**: of 1,321 curios only 255 had a tier (counted 2026-11-18): the game test, a bare player hitting a pig, sees nothing for 692 of them (a condition, a chance, an active key, loot), 64 are held back for a condition the test hid, 94 helped but fell under the floor of every tier, 17 are Looting Charms (rarity 6).

**Rule**: every curio gets a place, and the page says what kind of evidence put it there. Three layers, each shipped and looked at before the next:
1. **Measured** (done 2026-11-18, 277 curios: 255 + 22): the existing score (gear.js `gCurioScore`, against the fifth best of the Act). A curio measured to help but under every tier's floor is Common (0) only when its text is plain attribute numbers (`gPlain`): 22 curios. The other 72 under the floor have a mechanic the test cannot see (Ankh Aegis: +5 armor measured, but its value is immunity to nine effects); ranking them Common would be wrong, so they wait for layers 2 and 3.
2. **Expected value from its own text** (started 2026-11-18 with Lucky Dice, Fateful Coin, Nullifying Dice: `GHITCODE`/`GTKCODE`): odds x size from the item's own text, times an uptime for a condition. The assumption is written on the item's page and here, and the tier carries the "estimate" label.
3. **Utility** (loot, mining, movement, comfort): ranked among its own kind by that kind's number, not mixed with combat power.

**Done when**: every curio has a tier or a stated reason it has none; `d.pe` ("estimate") only on layers 2 and 3; an invariant per layer; pages of each layer looked at; `check.sh` green.

**Assumptions for layer 2** (added here as they are made; a number with no source in the pack's files is not used): none yet beyond the three items above. The rule "each Luck point = +2% damage, +2.5% attack speed, +2% dodge" is in a hand-written table in app.js with no source in the pack's files, so it is not used.
