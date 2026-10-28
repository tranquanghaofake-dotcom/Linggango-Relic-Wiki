# build/: how the wiki is made

```
pack jars + configs ──(pack_audit/*, gear/*: run on demand, need the CurseForge pack)──► patches/*.json, gear_table.json
patches/*.json ──► patches/*.py (data patches, idempotent) ──► src/data.js, src/gear_data.js, src/wiki_data.js
src/*.js, v5.css, style.game.css, template.html ──► build.py ──► index.html + static/ (site), dist/*.html (offline)
```

## Daily loop
1. Edit a source: `src/app.js`, `src/gear.js`, `src/ux.js`, `src/template.html`, `src/v5.css`, `style.game.css`, or a data file in `patches/`.
2. `bash build/patches/apply_all.sh`: runs every patch in order, then `build.py`.
3. `bash build/check.sh`: patches idempotent and build reproducible, no script errors, every gear page and set page renders, every Path boss card has a background. Needs Chromium via `playwright` (`NODE_PATH=$(npm root -g)`).
4. Commit `index.html` with `static/` (and `dist/`), push to `main`. The session note goes to `NOTES.md` on the `workspace` branch.

## What is source and what is generated
| File | Kind |
|---|---|
| `src/app.js`, `src/gear.js`, `src/ux.js`, `src/template.html`, `src/v5.css`, `style.game.css` | hand-written |
| `patches/*.json`, `patches/gear_*.py`, `patches/gearlib.py` | gear facts and the rules that combine them; edit these to change facts |
| `src/gear_data.js`, `src/wiki_data.js` | generated in one pass from JSON (`gear_pipeline.py`, `wiki_data.py`); nothing reads them back |
| `src/data.js` (curios) | **source**, hand-maintained (it cannot be regenerated). `boss_stats.py` and `boss_order.py` derive values into it in place; the one-time edits that shaped it are kept on the `workspace` branch (`build/migrations/`) |
| `src/fx3d.js` | bundle of `fx3d.src.js` + `geo2three.js` + three.js r169: `bash build/fx3d_build.sh` (esbuild, reproduces it byte for byte; `--check` verifies) |
| `index.html`, `static/`, `dist/` | build output, never edited |
See `ARCHITECTURE.md` for how the pieces fit and why.

## Rules
- Every patch is idempotent (`check.sh` runs the chain twice and compares bytes).
- Order lives in one place: `patches/apply_all.sh` (boss_stats, boss_order, gear_pipeline, wiki_data), and the stage list at the top of `patches/gear_pipeline.py` for gear.
- Gear is built in memory from `gear_table.json` + overlays and written once. Do not add a patch that reads `gear_data.js` back: add a stage function `apply(st)` to the pipeline.
- Scoring exists once, in `src/gear.js`. Python only produces facts (`patches/gearlib.py`: `off_of`, `set_facts`).
- `check.js` has invariants (Acts in `ORDER`, finite scores, enough options per playstyle and Act, nothing listed before its Act). A bug found in the data gets an invariant there.

## Adding or changing a page
Detail pages (curio `#iN`, gear `#gN`, set `#gsN`, Keeper `#boss/k`, side boss `#side/name`) are one call to `article()` in `src/app.js`, then `wireArticle()`:
```js
el("main").innerHTML=article({crumb, title, lead, meta,             // header: breadcrumb, h1, one-sentence lead, chips
  secs:[["get","How to get",html], ["stats","Stats",html], …],      // falsy entries are skipped; ids feed "On this page"
  art, box:{head, rows:[["Act",html], …], foot},                    // infobox: picture, key facts, id + Copy (idBox(id))
  after, nav:wikiNav({act, boss}, [[label, [[href,text,current], …]]])});  // under the sections; navbox groups first, then the wiki-wide ones
wireArticle();
```
- Section order follows the game wikis: how you get it, then what it does (stats, attacks, levels), then how it compares (tier by Act, what it opens), then related items.
- A new feature on a page is a new entry in `secs` (it gets its heading, its anchor and its line in "On this page"); a new fact is a new infobox row.
- A new kind of page uses `article()` too; `check.js` fails a detail page that does not (title, infobox, navbox, a heading on every section).
- Ready-made `<section class="s"><h2>…</h2>…</section>` html (such as `summonHtml`) converts with `secsOf(html)`.
- List and tool pages (The Path, Equipment tier list, Bosses, Build planner, Mechanics) keep their own layouts.

## Rooms (the wiki's own interior)
The headers of The Path, Equipment, the Build planner, Bosses and Mechanics, and the Equipment and Must-Have blocks of the home page, are rooms: `room(kind, items, {head, min, cols, label})` in `src/rooms.js`. A room is a cross-section of a build six blocks tall (beam, four blocks of wall, floor), drawn into one canvas at 16 px per block and shown at x3, and lit the way the game lights it: each light gives a level that drops by one per block, the dark is stepped per texel, torches, lava and soul fire add their colour. Item frames on the right hold real items of the page (links with tooltips: the planner's frames are your build, Equipment's the best gear at the chosen Act); the title sits in the shade on the left.
- Each room has its own scene in the middle, written as a small function in `ROOMK` (rooms.js): library and enchanting table with glyphs flying to the book (Curios), forge with a lava fall behind iron bars (Equipment), crypt with a spawner and soul braziers (Bosses), armour stands (Build planner), a ritual altar with the page's items on pedestals (Mechanics), ME controller and drives (storage), beacons and amethyst (Must-Have). The scene keeps the middle; shelves, pillars, chains and lamps repeat to fill any width, and the room repaints when its width changes.
- Moving parts are the game's own frame strips at the game's frame times (lava, fire, soul fire, blast furnace, AE2 lights) and vanilla particles; all stop under reduced motion.
- Textures are `ROOMT`: `src/scenes.js` (`pack_audit/scenes.py`) and `src/uiicons.js` (`pack_audit/uiicons.py`: `rm_*` blocks and `ri_*` items of vanilla 1.20.1, `rg_*` Goety's crypt from the asset library). A scene falls back to a vanilla block when a third-party texture is missing.
- Licence rules for new textures: vanilla is fine (fan content, footer disclaimer); a mod or resource pack only when its licence covers its textures (MIT, CC BY, CC BY-NC, LGPL with no asset exception…), credited in the footer's Art column; ShareAlike textures (AE2's CC BY-NC-SA) stay byte for byte unchanged; nothing All Rights Reserved or NoDerivatives (Iron's Spellbooks, Terramity, Ars Nouveau, Relics, L_Ender's Cataclysm, Dark/Modded Coffee GUI, Vanilla Experience+, Lanterns with Candles, Brush & Juice, Fresh Waystones). Misanthropy's own packs (Linggango Textures, Linggango – FTB Quests Theme) are used with the author's permission; credit Coquet by jekaloic with them. Keep 16 px textures: 32 px packs (Faithful 32x) break the pixel grid next to the 16 px item icons.
- Detail pages carry the same idea in the infobox: the item in its rarity frame on its Act's wall (`.ip-icon.framed`).

## Pixel rules (checked by `style_check.js`, run by `check.sh`)
- Square corners only; pixel art at a whole-number scale (or 1/n of a larger source); one frame per thing, never a frame inside a frame; icons are sprites, never emoji. `style_check.js` fails the build on the first three kinds it can measure and lists frames inside frames to look at.
- New icons and particles go through `pack_audit/uiicons.py <vanilla 1.20.1 textures> <asset library>` (writes `src/uiicons.js`, merged into `ROOMT`, so each is a `--rt-*` variable); `ui(k)` in app.js draws one at 16 px, `ui(k,1)` at x2. The asset library is `assets/` on the `workspace` branch (`catalog.csv` gives each file's source, version and licence; only tiers A, A-SA and A-perm may be used).
- Rarity frames: `pack_audit/rarity_frames.py` (own work): an inventory slot with a thin rim (one ink texel, one bevelled colour texel), ornament growing with rarity; 32 px at x2 on curio tiles, 64 px at x3 in the infobox. Colours are muted material tones sampled from vanilla items (iron, raw gold, prismarine, amethyst, copper, redstone, gold), the same as `--r0 … --r6`.
- Slot badges: `pack_audit/slot_badges.py` (own work), a 9x9 sign per slot family and for the two ring requirements, x2 in the tile corner.
- Mob faces for drop cards: `pack_audit/mob_faces.py`, the front of each vanilla mob's head cut from its entity texture.
- The page background is a deepslate cave wall with ore veins, painted once by app.js from `bg_*` textures (`#cave`).
- Display face: Monocraft (`fonts/`, OFL), embedded by build.py; body text Be Vietnam Pro.
- Icons whose source is not a multiple of 16 px are fitted by `ux.js` (largest k x source or source / k that fits the box).

## Game effects
The game's own effects, each where it means something, each off under reduced motion:
- Enchantment glint (`misc/enchanted_glint_item.png`) scrolls over Mythic and Must-Have items, masked to the item's own pixels: `glint(d)` in app.js.
- The sweep attack (`particle/sweep_0..7`, joined into one strip) plays once when the pointer reaches a weapon: gear tiles and the gear infobox get `wpn` in gear.js, the forge room's frames get it from CSS.
- Each Act's air: `envFx(a, k)` drops eight particles into a picture, chosen from the Act's block (`PENV`): petals on the surface, drips in caves, embers and ash in the Nether, souls by soul sand, sculk souls in the deep dark, portal motes in the End, glitter on gilded blackstone. A boss can bring its own arena (`BENV`, `BTEX`: the Warden's sculk, the Wither's soul sand, the Dragon's end stone). Used in infobox pictures, The Path's side-boss column and the Bosses cards (which only animate on hover).

## The GUI skin
The last block of `style.game.css` dresses the controls in the pack's and the game's own textures (all from `ROOMT`): buttons are vanilla `gui/widgets.png` as a 9-slice border-image (the selected one keeps the green); search fields, the infobox and the navbox use Linggango Textures' slate-metal frame; range sliders use its track, cyan fill (`--rv`, set by `setRv` in app.js) and gem knob; Legendary items wear its silver ornate frame and Mythic / Must-Have its gold one (infobox at ×10, Path tiles at ×2); the boss bar is vanilla `gui/bars.png` (purple for the Wither); progression pages (`body.qbg`) sit on the FTB Quests Theme background; Keeper locks, the beaten-Act check and section markers are the packs' sprites. Integer scales only: these are pixel art.

## How gear is ranked (src/gear.js)
Four playstyles: Melee, Ranged, Mage, Summon (Tank was retired in v22.11; defense is part of every score). Rules read from the pack's jars:
Better Combat `allow_fast_attacks` (default on) clears hurt cooldowns, so melee DPS = hit × speed with no cap; Apothic Attributes armor is
damage × a/(a+armor), a = 10 under 20 damage, 10+(dmg−20)/2 above, and toughness only weakens armor shred/pierce.
Base stats: `patches/gear_runtime.py` lays the pack's in-game dump (`gear_runtime.json`, from `kubejs/server_scripts/dump_gear.js`) over the jar reading for 1760 items; re-run `/kubejs custom_command dump_gear` and convert `kubejs/gear_dump.json` when the pack updates.
Melee weapons: DPS (`gMelee`); any weapon with readable melee damage (staves, spears) is also a Melee candidate. Ranged / Mage / Summon weapons
have no readable damage, so `gEstScore` puts them on the power curve `GSTEP^rung` (GSTEP fitted at load time on the top-10 melee DPS per Act,
≈1.20), + up to 10% for how hard they are to get, × their role bonus (`GOFF`). Armor sets: score(set, role, Act) = `GOFF[role]` × EHP^k
(k: Melee 1, Ranged .7, Mage .6, Summon .6), EHP against the Act's Keeper hit (`GHIT`, from entitybalance.json) on top of 20 + 4 HP per Act;
so set scores depend on the Act (`gScore`). Sets with unreadable armor get the median armor/toughness/HP of their Act. Tiers are the ratio to
the best item at the Act (S ≥85%, A ≥70%, B ≥55%, C ≥40%); under 25% is not listed; creative-only items are hidden.
`patches/gear_extra.json` (made by `gear/extra.py` from `gear/extra_ids.json`) adds plain-Item weapons the extraction skips; Iron's armor material
attributes come from `pack_audit/iss_armor.py` (javap on `ExtendedArmorMaterials`) via `gear_stats.json`; icons that need a 3D render come from `pack_audit/weapon_icons/`.

## Regenerating from the pack
`gear/` (see `gear/wide/README.md`) and `pack_audit/` (see its README) read the pack's jars (6.6.6hf: the 383 server jars plus the client zip's overrides) and write the JSON in `patches/`. They need the pack downloaded (`gear/dl.py`) and are not part of the daily loop.
Run those scripts from a folder that has no file named like a stdlib module (`enum.py` used to shadow `enum` and break `import json`; it is now `boss_audit/enum_jars.py`).
`original/` is the v5 wiki the first `data.js` came from; `gear/prep.py` still reads it. The one-off `transform.py` that did the conversion is on the `workspace` branch.

## Known weak spots
- `data.js` is source but two derived passes (`boss_stats`, `boss_order` curio part) still edit it in place; moving those into overlay JSON like gear would finish the job. Its 5 MB of embedded icons make diffs unreadable.
- `app.js` is one 900-line file with globals; `gear.js` now plugs in through `EXT` (route and tooltip hooks), so load order only needs `app.js` first.
- The Act, mod and slot pages are gone (they redirect to #home); some CSS for them (`.gbest`, `.gstrip`) is dead.
- The data files are 5 MB each of JS; the site loads them as cached static files, but the first visit is heavy.
