# Spells: the pack's other spell systems (Goety, Ars Nouveau, Brutality)

Approved 2026-11-15 by the owner: all three, Goety first; each system in its own sub-tab of Spells.

## What the reader sees
The Spells page gets sub-tabs: Iron's Spells (today's page), Goety, Ars Nouveau, Brutality. Each sub-tab lists every spell the running
pack registers for that system, with its numbers after the pack's config, and a clip recorded in the game where one could be made (or the
reason there is none).

## Facts (source order of CLAUDE.md)
1. The game export: `build/pack_audit/kubejs/server_scripts/lgw_registry.js`, run in the full 383-mod server, now also writes
   `goety` (every item with `getSpell()`: focus id, spell class, soul cost, cast ticks, cooldown ticks, spell type), `ars` (GlyphRegistry: glyph id,
   type, tier, cost, enabled, description) and `brutality` (its SpellRegistry: mana, damage, cooldown, cast time and their per-level scaling,
   school, categories). Copied into `build/patches/game_registry.json`.
2. Names, descriptions and icons from the jars' lang files and textures (as `spells.py` does for Iron's).

Counted from the jars before the export (lang files): Goety 125 focus items (one is the empty focus), Goety Awaken 34, Goety Cataclysm 28,
Goety Revelation 9; Ars Nouveau 81 glyphs, Ars Elemental 27, Adam's Ars Plus 36, Tome of Blood 2, Ars Additions 3; Brutality 30 spells.
The export is the list; these counts are only the expectation.

## Steps, one system at a time (each ends live: build, look, check.sh, NOTES, main, green run)
1. Data: `pack_audit/spell_systems.py` reads the export and the jars into `patches/spells_goety.json` (later `_ars`, `_brutality`).
   `checks/spells.js` gains the same two-way check against the export for each system.
2. Page: `app.js` `spellsPage` gets the sub-tab row (the Mechanics page's sub-tab pattern) and a card per spell with the system's own numbers.
3. Clips: the recording stage (`pack_audit/spell_clips.py`) gets each system's way of casting: Goety, the focus in a wand with soul energy;
   Ars, a spell book or a carrier item with a composed spell (augments shown as with/without); Brutality, its own casting item. Clips go to
   the workspace branch like the Iron's ones; `build/clips/approved.json` lists every approved id.

## Done when
Every exported spell of the system has a card; every card has an approved clip or a stated reason; `bash build/check.sh` green; the site run
green and `/build.txt` names the commit.

## Progress
- Goety: data and tab live (2026-11-15, 209 focuses); clips (2026-11-16): 178 approved, 14 cannot be shown (reasons in NOTES), 11 cause unknown, 6 Linggango Tweaks focuses waiting for the stage's new jars. Every clip now H.264 CRF 28 (`clips_reencode.py`).
- Ars Nouveau: data and tab (170 glyphs; tier from the pack's config, checked one to one against the export's SpellTier objects); clips (2026-11-17): 123 approved, 45 without a clip and the reason for each (NOTES), 2 turned off by the pack.
- Brutality: data and tab (26 spells); clips (2026-11-17): 23 approved, 3 without a clip and the reason for each (NOTES).
