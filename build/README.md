# build/: how the wiki is made

```
pack jars + configs ──(pack_audit/*, gear/*: run on demand, need the CurseForge pack)──► patches/*.json, gear_table.json
patches/*.json ──► patches/*.py (data patches, idempotent) ──► src/data.js, src/gear_data.js, src/wiki_data.js
src/*.js, v5.css, style.game.css, template.html ──► build.py ──► index.html + static/ (site), dist/*.html (offline)
```

## Daily loop
1. Edit a source: `src/app.js`, `src/gear.js`, `src/template.html`, `src/v5.css`, `style.game.css`, or a data file in `patches/`.
2. `bash build/patches/apply_all.sh`: runs every patch in order, then `build.py`.
3. `bash build/check.sh`: patches idempotent and build reproducible, no script errors, every gear page and set page renders, every Path boss card has a background. Needs Chromium via `playwright` (`NODE_PATH=$(npm root -g)`).
4. Add a line to `NOTES.md`, commit `index.html` with `static/` (and `dist/`), push.

## What is source and what is generated
| File | Kind |
|---|---|
| `src/app.js`, `src/gear.js`, `src/template.html`, `src/v5.css`, `style.game.css` | hand-written |
| `patches/*.json`, `patches/gear_*.py`, `patches/gearlib.py` | gear facts and the rules that combine them; edit these to change facts |
| `src/gear_data.js`, `src/wiki_data.js` | generated in one pass from JSON (`gear_pipeline.py`, `wiki_data.py`); nothing reads them back |
| `src/data.js` (curios) | **source**, hand-maintained (it cannot be regenerated: `transform.py` gives a different file). `boss_stats.py` and `boss_order.py` derive values into it in place; the nine one-time edits that shaped it are kept in `migrations/` |
| `src/fx3d.js` | bundle of `fx3d.src.js` + `geo2three.js` + three.js r169: `bash build/fx3d_build.sh` (esbuild, reproduces it byte for byte; `--check` verifies) |
| `index.html`, `static/`, `dist/` | build output, never edited |
See `ARCHITECTURE.md` for how the pieces fit and why.

## Rules
- Every patch is idempotent (`check.sh` runs the chain twice and compares bytes).
- Order lives in one place: `patches/apply_all.sh` (boss_stats, boss_order, gear_pipeline, wiki_data), and the stage list at the top of `patches/gear_pipeline.py` for gear.
- Gear is built in memory from `gear_table.json` + overlays and written once. Do not add a patch that reads `gear_data.js` back: add a stage function `apply(st)` to the pipeline.
- Scoring exists once, in `src/gear.js`. Python only produces facts (`patches/gearlib.py`: `off_of`, `set_facts`).
- `check.js` has invariants (Acts in `ORDER`, finite scores, enough options per playstyle and Act, nothing listed before its Act). A bug found in the data gets an invariant there.

## How gear is ranked (src/gear.js)
Melee: DPS from the pack data (`gMelee`). Ranged / Mage / Summon weapons have no readable damage, so `gEstScore` ranks them by unlock rung (+13% per Act),
+ up to 10% for how hard they are to get (boss drop, recipe size) and their readable bonuses (saturating at +100%). Armor sets: every set is a
candidate in every role, score = defense × role fit (Melee 1, Ranged .9, Summon .8, Mage .65) × (1 + saturated role bonus); sets with unreadable
armor get the median defense of their Act. Tiers are the ratio to the best item at the Act (S ≥85%, A ≥70%, B ≥55%, C ≥40%); under 25% is not listed.
`patches/gear_extra.json` (made by `gear/extra.py` from `gear/extra_ids.json`) adds plain-Item weapons the extraction skips; Iron's armor material
attributes come from `pack_audit/iss_armor.py` (javap on `ExtendedArmorMaterials`) via `gear_stats.json`; icons that need a 3D render come from `pack_audit/weapon_icons/`.

## Regenerating from the pack
`gear/` (see `gear/wide/README.md`) and `pack_audit/` (see its README) read the pack's 476 jars and write the JSON in `patches/`. They need the pack downloaded (`gear/dl.py`) and are not part of the daily loop.
Run those scripts from a folder that has no file named like a stdlib module (`enum.py` used to shadow `enum` and break `import json`; it is now `boss_audit/enum_jars.py`).
`transform.py` is the one-off that turned `original/` into the first `data.js`; it is kept for history, not for rebuilding.

## Known weak spots
- `data.js` is source but two derived passes (`boss_stats`, `boss_order` curio part) still edit it in place; moving those into overlay JSON like gear would finish the job. Its 5 MB of embedded icons make diffs unreadable.
- `app.js` is one 900-line file with globals; `gear.js` now plugs in through `EXT` (route and tooltip hooks), so load order only needs `app.js` first.
- The Act, mod and slot pages are gone (they redirect to #home); some CSS for them (`.gbest`, `.gstrip`) is dead.
- The data files are 5 MB each of JS; the site loads them as cached static files, but the first visit is heavy.
