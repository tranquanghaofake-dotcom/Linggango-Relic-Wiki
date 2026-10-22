# Weapon icons that are not a flat texture

`plan.py` reads the jars and decides, per gear id, how its inventory icon is drawn: a flat `layer0` (or the `gui` perspective of a
`forge:separate_transforms` model), a Java element model (Blockbench cubes: Goety/Iron's staffs, most Too Many Bows bows) or a GeckoLib model
(`builtin/entity` parent, geo + texture). `render.js` draws the last two with the three.js page `pack_audit/geo_icon_render.html`
(copy it as `r.html` next to `geo2three.js`, `npm i three@0.169.0`). Player-arm bones and muzzle flashes of GeckoLib guns are dropped.
Before this, those items showed their raw UV texture sheet as the icon. Output goes to `patches/gear_icons.json` (a `null` value removes an
icon: items whose only art is a model atlas, like Brutality's phasesabers, show a letter tile instead of a texture sheet).
Setup: work dir `W` with `W/pack/mods/*.jar` (see `pack_audit/README.md`), run from the folder holding `plan.py`, `ld.py`, `render.js`
(`ld.py` reads the table out of `src/gear_data.js`): `python3 plan.py && node render.js` → `plan.json`, `rendered.json`.
