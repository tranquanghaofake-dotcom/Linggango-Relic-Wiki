# Weapon icons that are not a flat texture

`plan.py` resolves each gear id's item model through `../mcassets.py`, the way the game stacks resources (kubejs assets, the
resource packs the pack's `options.txt` enables, top first, the mod jars, the vanilla client jar; `NO_PACKS=1` leaves the resource
packs out), parents merged, the `gui` perspective of `forge:separate_transforms`, and draws the icon by the game's rules:
- `flat`: the model reaches `builtin/generated`: its layers at their own resolution (first animation frame).
- `el`: a JSON element model (Blockbench cubes: Goety/Iron's staffs, most Too Many Bows bows) is drawn by `../block_render.py`
  `render_model` at 32 px (one slot at GUI scale 2): the model's own `display.gui` (none = no transform, as vanilla), its `gui_light`
  (no `gui_light` = "side", the 3D light, so a face-on model shows at 51 % brightness, as in game), BlockElement uv defaults, rescale.
- `geo`: `builtin/entity` with a GeckoLib geo: geometry, the texture the mod's GeoModel class names (string constants of the class
  that names the geo; else found by file name) and `display.gui` go to `render.js`, which draws them with `../geo_icon_render.html`
  at 32 px as GeckoLib 4.8.4's `GeoItemRenderer` does in the GUI (read with javap): display.gui, ItemRenderer's −0.5, GeckoLib's
  +(0.5, 0.51, 0.5), the flat-item light (`renderInGui` → `Lighting.setupForFlatItems`), no culling, quads in GeckoLib's order,
  `fixInvertedFlatCube` normals, orthographic, no antialiasing. Muzzle-flash bones and arm-shaped `left`/`right` bones (the player
  arms MCreator's renderers hide) are dropped; `GEOX` also hides the spell-book tier bones Ars Nouveau's renderer hides.
`render.js` copies the flat and element icons through and adds the GeckoLib ones → `rendered.json` (id → base64 PNG). A model bigger
than the slot is cut at the slot edge (in game it spills over the neighbouring slots). Output goes to `patches/gear_icons.json` (a
`null` value removes an icon: items whose only art is a model atlas, like Brutality's phasesabers, show a letter tile instead).
Setup: work dir `W` (`W/pack/mods/*.jar` and resource zips, `W/pack/src` = the unzipped pack, `W/mc_client.jar` = client-1.20.1.jar;
see `pack_audit/README.md`), run from a folder holding `W` (or `W=<dir>`): `python3 build/pack_audit/weapon_icons/plan.py && node
build/pack_audit/weapon_icons/render.js` → `plan.json`, `rendered.json` (`ld.py` reads the table out of `src/gear_data.js`).

2026-10-31: the 181 icons drawn at 128 px with an invented diagonal pose and fitted to the canvas (shown at 32 or 16 px by dropping
pixels, so shafts broke into dots) were redrawn this way: 104 element models, 62 GeckoLib models, 13 items that the pack's resource
packs (Waffy's ISS / T.O Magic / Cataclysm Reimagined) turn into flat GUI textures, and 2 flat 128 px textures (Frostmourne,
Skofnung) left as they were. The old name-only bone drop had removed parts of Comet Spear, Mjolnir, Soul Reaper and Draconic
Splitter, and Comet Spear took a texture its renderer does not use.

2026-10-28: the 86 pieces added from the 6.6.6hf dump (`gear_new.json`) were run through the same plan/render (`ONLY=dump python3 plan.py`):
6 drawn from models; Spectralibur uses its first frame `spectralibur_0`; four Cataclysm weapons (The Incinerator, The Immolator, Soul Render,
Gauntlet of Maelstrom) draw their model in Java code, so they keep the placeholder tile.

Same day, the gear still without an icon: `ONLY=<id,id,…>` runs a list. `GEOX`/`FLATX` in `plan.py` name models whose file has
another name than the item: Ars Nouveau's three spell books (`spellbook_closed` geo, the default purple cover), Mahou Tsukai's Bow of
Weapon Projectiles (its resting `_standby` texture). Flat textures found for Mossy Hammer, Stiff Chainsword, Soaked Gorescythe and
Resonator were merged. Left as placeholders: the four Cataclysm weapons and Potatiesh (models in Java code), Enchanter's Bow (its geo
renders only the gold trim), the two Nether Exploration shotguns (their jar is not in the pack download).
