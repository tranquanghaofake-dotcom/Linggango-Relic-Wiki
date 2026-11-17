# In-game measurement run by Claude, not the owner (2026-11-17)

## Why
The Equipment page cannot rank what it has no number for: 144 Ranged and 24 Summon weapons stand in the "?" row, and four
curio readings are suspect (a ×1.5 hit nothing explains; 69 damage-taken readings at the 20-health tester's hit cap). Reading
the mods' code cannot settle these: every Too Many Bows bow has its own firing code, and a minion's damage is set when it
attacks. The owner asked for a way that needs no time in the game from them. Earlier sessions ran the full server pack in this
container (Forge 47.4.20, Java 21, 4 CPUs, 15 GB): `lgw_registry.js` and `lgw_spellpower.js` exports, the spell clip stage.

## The server
- `serverpack-slim-6.6.6hf.zip` from the owner's Drive link (877,854,222 bytes, SHA-1 4f74fb7b…, 383 jars), with
  `linggango_fixes-2.16.jar` replaced by `linggango_fixes-2.16-leakfix.jar` (6.6.6cf, file 9623489). Checked on 2026-11-17:
  6.6.6cf differs from 6.6.6hf only in that jar (one added mixin, `ScheduledRandomTickDedupeMixin`, a BWG random-tick
  leak fix), Punchy! (client only) and five `defaultconfigs` it drops, whose values are the mods' defaults. So the result is a
  6.6.6cf server and the wiki's numbers stay valid for cf.
- Forge 47.4.20 libraries from the installer (maven.creeperhost.net mirror, SHA-1 checked, as before); offline mode; a
  `kubejs/lgw_*_auto.json` marker starts each script when the server has loaded; a harness-watched background task stays
  running the whole time (the container is reclaimed when the session goes quiet).

## What is measured, in order
1. **Shots (Ranged).** `lgw_measure_third_test` first: the probe of six shooters (Bow, Crossbow, Trident, Sun Bow, Frostbite,
   Cavendish) prepared since 2026-10-29 and never run. Calibration: the vanilla Bow must read about 6 a shot at full draw
   (velocity 3 × base 2) and the Crossbow about 9; if not, fix the shot before the full run. Then the full third run on every
   bow, crossbow and thrown weapon: damage a shot, draw or reload time, shots a second. `import.py` / `import_third.py` →
   `patches/gear_measure.json`; `gear.js` scores Ranged by shot damage × shots a second, like melee DPS.
2. **Curio re-measure.** The four unexplained ×1.5 hits (Gob's Mask, Chronicles Of The Firelord, Amplifier Stone, Charged
   Redstone Piece) with the tester held on the ground (fall distance 0); the 69 capped damage-taken readings with the tester's
   max health raised so the half-health cap cannot bind; lethality curios against a dummy with 10 and 20 armor.
3. **Minions (Summon).** New script: each summon weapon used by the tester, the minions it spawns counted, each minion's damage
   to a dummy over a fixed time. If a FakePlayer's minions do not attack (likely for some mods), the fallback is a number read
   from the running game: the spawned entity's attack damage attribute and attack interval. Weapons with neither stay unranked.

## Done when
The Ranged tab has tiers from shots (the Bow and Crossbow read their known values), Summon has tiers where a number exists,
the curio suspects are settled one way or the other, each with an invariant in `build/checks/`, `check.sh` passes and the
`site` run is green.

## Risks
- Running the server is external code: once before the session's safety classifier blocked it; a later session ran it. If it is
  blocked, the owner is told and nothing else changes.
- Shots may not register as the tester's (the probe exists for that: it notes each projectile's owner and the pig's last
  damage source).
- Hours of wall time; each step is committed as it lands, so a stop loses at most the step in progress.
