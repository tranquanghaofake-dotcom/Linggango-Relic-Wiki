# Weapon icons that are not a flat texture

`plan.py` reads the jars and decides, per gear id, how its inventory icon is drawn: a flat `layer0` (or the `gui` perspective of a
`forge:separate_transforms` model), a Java element model (Blockbench cubes: Goety/Iron's staffs, most Too Many Bows bows) or a GeckoLib model
(`builtin/entity` parent, geo + texture). `render.js` draws the last two with the three.js page `pack_audit/geo_icon_render.html`
(copy it as `r.html` next to `geo2three.js`, `npm i three@0.169.0`). Player-arm bones and muzzle flashes of GeckoLib guns are dropped.
Before this, those items showed their raw UV texture sheet as the icon. Output goes to `patches/gear_icons.json` (a `null` value removes an
icon: items whose only art is a model atlas, like Brutality's phasesabers, show a letter tile instead of a texture sheet).
Setup: work dir `W` with `W/pack/mods/*.jar` (see `pack_audit/README.md`), run from the folder holding `plan.py`, `ld.py`, `render.js`
(`ld.py` reads the table out of `src/gear_data.js`): `python3 plan.py && node render.js` → `plan.json`, `rendered.json`.

2026-10-28: the 86 pieces added from the 6.6.6hf dump (`gear_new.json`) were run through the same plan/render (`ONLY=dump python3 plan.py`):
6 drawn from models; Spectralibur uses its first frame `spectralibur_0`; four Cataclysm weapons (The Incinerator, The Immolator, Soul Render,
Gauntlet of Maelstrom) draw their model in Java code, so they keep the placeholder tile.

Same day, the gear still without an icon: `ONLY=<id,id,…>` runs a list. `GEOX`/`FLATX` in `plan.py` name models whose file has
another name than the item: Ars Nouveau's three spell books (`spellbook_closed` geo, the default purple cover), Mahou Tsukai's Bow of
Weapon Projectiles (its resting `_standby` texture). Flat textures found for Mossy Hammer, Stiff Chainsword, Soaked Gorescythe and
Resonator were merged. Left as placeholders: the four Cataclysm weapons and Potatiesh (models in Java code), Enchanter's Bow (its geo
renders only the gold trim), the two Nether Exploration shotguns (their jar is not in the pack download).
