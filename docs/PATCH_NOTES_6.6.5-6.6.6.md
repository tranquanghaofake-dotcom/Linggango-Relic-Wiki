# Pack patch notes 6.6.5b1 to 6.6.6: wiki backlog

Source: Discord #updates posts by Chibi Misa, 9/5/2026 to 10/23/2026, pasted by the user on 2026-10-30.
Status of everything below: **not started**. Nothing on the site has changed for these notes.

The notes are the author's words. Wiki numbers must come from the pack jars or the game export first (the wiki's rule), and the notes are only a pointer to what changed.

## Versions

| Version | Date | Theme |
|---|---|---|
| 6.6.5b1 | 9/5/2026 | Apex abilities, Apex fixes, gun reforges, slot machines, automation branch |
| 6.6.5b2 | 9/5/2026 | Terramity curio overlap (gradual nerf), cursed scroll back, performance |
| 6.6.5b3 | 9/30/2026 | Combat and balance overhaul: world gen, 6 classes, difficulty modifiers, The Path, parry and roll rebuilt, Hostility, food, summoner |
| 6.6.5b4 | 10/5/2026 | Performance, combat element combos, Combat stats tab, structures, main menu, boss arena and Pit fixes |
| 6.6.6 (The Goety Update) | 10/23/2026 | Goety, Apollyon, necromancer, sabbath engine, Summonity expansion, new Goety questline, farm recipes, home treats, quest cards |

Reminder from the notes: "Next update is 6.6.6" (10/5). The pack instance on disk is 6.6.6hf (`D:\CurseForge\Instances\Linggango [6.6.6 - Goety Update]`). Check that the jar set matches the 6.6.6 notes before using any number from them. The local `summonity-0.1.7.jar` matches the notes.

## 1. Gear (the user's priority)

- **Equipment pages are outdated.** They still rank with the pre-6.6.5 stats. Rebuild the tier data from the new jars.
- **Class sets view (requested).** One set per class per Act: the strongest armor set and the strongest weapon obtainable at that Act, by the existing tier ranking. Inventory-tab layout. Classes: melee, ranged, magic, summon. Include every mod's type (Iron's Spells, Ars Nouveau, and the other ranged, magic and summon mods).
- **Gear page per class: "best loadout" strip (proposed, not approved).**
- **Armor sets (6.6.6 b3 section 51).** About 200 sets now do something. Each piece has its own stats. New attributes: Dodge Window, Dodge Damage, Parry Window, Parry Recovery, Stun Duration, Technique Recharge Speed, Technique Range. New armor reforges: Evasive, Vengeful, Duelist, Tempest. Armor pen and lethality removed from armor. Armor toughness no longer matters. Needs a dedicated armor-set page section.
- **Tier weapon damage covers every mod now.** Mining tools excluded. Meka-Tool moved onto the progression ladder. Unique weapons from Simply Swords and Simply More are on the ladder by ability strength (diamond to helionite).
- **Apex abilities (b1).** 18 abilities: 8 melee, 5 shield, 5 tool. Activated keybinds J (main hand), K (armor), L (offhand). Apex needs the full Mythic to 5 stars. Needs an Apex page.
- **Apex fixes (b1).** Guns, bows, crossbows, tridents, shields, elytra and rods could not be starred or Apexed (wrong repair material check). Cleansing now keeps stars and Apex, with a double click before it touches invested items.
- **Gun reforges (b1).** 96 gun-only modifiers (16 per rarity). Each gun has its own reforge material (42 mapped; example: Flintlock uses Iron Ingot, Requiem uses Iridium). Five reforges have real behaviour: Ricochet, Executioner, Suppressing, Opening Shot, Marksman. One reforge per gun. Gun damage scales on a curve now.
- **Damage types (b4 / 6.6.6 section 52).** Eleven types: Slash, Pierce, Blunt, Fire, Frost, Lightning, Holy, Dark, Blood, Nature, Arcane. About 1900 weapons sorted. About 780 mobs have weaknesses and resistances (plus 25%/-25%). Weather boosts types. Wiki already has a Damage types section; compare against it.
- **Imbuements (section 53).** Eight elements, 90 seconds each. Status meters: Blood hemorrhage, Frost slow, Lightning chain and stun, Fire scorch, Holy beam and stop healing, Dark soften, Nature root and rot, Arcane explosion and mana. The wiki's Status and combos section (in the workspace notes, not yet on main) covers part of this. Check it against the new numbers.
- **Element combos (b4).** Two elements on the same mob react: fire and frost shatter, fire and lightning explode, holy and dark ignore resistances (plus 10 more). Bosses take half.
- **Reforge stats (b1).** Stat line fixes, reforge explanations on the tooltip, offhand gun reforges count.

## 2. Combat (Parry, roll, crowds, hits)

- **Parry is a swing now (b3, section 41).** Base parry 2-tick window, 1-tick perfect window, 1-second lockout on a miss (up to 5 seconds). Lectern Parry tab: 14 skills, costs rise with rank, refundable at sell-back.
- **Exposed status.** Parried mobs stay Exposed for a few seconds and take 20% more damage.
- **Red attacks (section 42).** Cannot be parried, must be rolled through. Cause parry cooldown plus weakness and slowness. Only Deflector with max Unbinding can parry them.
- **Blue attacks (section 43).** Cannot be dodged, must be parried or outranged. Cause the loss of all dodge charges.
- **Crowds (section 44).** Only 2 mobs can wind up at once (`maxAttackers` in `hit_indicator-common.toml`, `[crowd]`).
- **Hitstop (section 45).** Every melee hit now.
- **Roll (section 46 onward).** Dash and roll rebuilt. Base dodge is deliberately weak: 3 safe ticks on dash, 4 on roll, 1.3 s and 3.2 s cooldowns, no air dodge.
- **Lectern Tumble tab (section 48).** 16 roll skills, including Bash, Thunderclap, Flashstep, Shadowstep, Featherfall, Geppo (Air Step), Last Straw, Counter, Shake Off.
- **Late parry removed (b3 fixes).** Parry must be pressed before the hit.
- **Floor on incoming damage (section 50).** About 13% of any hit always reaches you.

## 3. Classes (section 54 onward)

- **Every class rebuilt.** Civilian is still the default and the only class without a skill.
- **Class growth.** Each keeper beaten makes class bonuses 6% stronger. Downsides never grow.
- **Damage type per class.** Vanguard holy, Pathfinder frost, Machinist lightning, Vampire blood, Miner dark, Berserker and Gunner fire, Scum nature, Monk lightning.
- **New classes:** Saint (healer), Dragon Rider, The Chosen One (Chaos only), Puppeteer (summoner), Deflector, Mule, Necromancer (6.6.6).
- **Changed:** Vanguard, Pathfinder, Ironclad, North Mage, South Mage, Machinist, Mule, Vampire, Miner, Berserker, Gambler, Gunner, Scum, Deflector and Puppeteer, Monk. Each has new numbers and skills. Check the wiki's class page against them.

## 4. Summoning (section 55 and 6.6.6)

- **Summon damage works on everything now.** Summonity, Goety, Ars and tamed wolves all read it (b3 fixes and 6.6.6 Summonity changes).
- **Minion slots.** Start with 2.
- **Summonity expansion (6.6.6).** Summonity 0.1.7: Psy Fly, Constellation whip, 10 summoner accessories, 3 whip enchants, Magic Mirror, Prismatic Lantern, Miniature Sun, Hollow Mask, Ember Locket, Combustion Chamber, Brimstone Singularity, whistles (Copper, War, Stygian, Spectral; only one worn at a time).
- **Stack flags.** Summonity unique curios: fixed in commit `ee82bf194` (Metronome and others now "One per player").

## 5. Food

- **Infinity Ham** lost its potion infusion. Feeds 1 hunger per bite.
- **Buffs (b3).** Well Fed (5%), Plenty Satisfied (10%), Exquisitely Stuffed (15%) all damage types plus movement speed and mining speed, lasting 10, 15 and 20 minutes. The wiki already has these.
- **Cooking for Blockheads, Spice of Life, Farmers Delight** kitchen integration. ME Kitchen Station.

## 6. The Path (b3 and 6.6.6)

- **11 acts, one per boss**, with 6.6.6 adding optional base-building quests and home quests.
- **Act 0 rebuilt:** rocks, twigs, flint, stone axe, straw, no wooden tools. Wiki's Act 0 page needs updating.
- **Locked tech and magic.** Boss locks, padlock icons, JEI hides locked items, Classic Locks option on the difficulty screen (6.6.6).
- **Crossroads quests** and per-act teaching quests.
- **Crowds, Hardmode after the Ender Dragon, predators, cave-ins, gas pockets** in the world.
- **Path curio tiles and particle layer (our fix in progress).** Path side-panel particles hidden (uncommitted). Lazy panel build (uncommitted).

## 7. Bosses, invasions and Hostility

- **Boss death screen (section 57).** Per boss notes.
- **Boss mercy.** Each death gives the boss 8% less health and damage, up to 40%.
- **Boss one-shot ceiling.** A boss loses at most 1/30 of its health per second. Beat a boss once and the ceiling is gone for you.
- **Invasions (section 58):** Goblin Army, Night of Chaos, Krampus Night, Blood Moon, plus Illager Crusade and Black Sabbath (6.6.6).
- **Hostility traits.** Hostile Remnants, Hostile Cores, Trait Lures, Hunt Mastery, Curse of Envy changes (section 59). 6.6.6 adds 12 Fallen traits and 13 relics; about 60 bosses now carry a trait.
- **Nightmare Altar.** Summon any beaten boss with trait items. Chesed and Malkuth moved off it (6.6.5b4 changes).
- **Boss damage and gear.** Boss damage ladder reordered (bloody and helionite swapped). Nyxaris, Sanghor, Vaedric, Zoranth and Eldorath hit harder. Elvenite Paladin hits about half as hard.
- **Sky Arena and Ice Arena** mobs follow the Path (section 60).

## 8. Slot machines (section 10 to 13)

- Odds redone: every machine takes more than it gives back. Jackpot is rare and pays more. Luck items now help.
- Machines reject enchanted, damaged or filled items.
- Wiki may have a slot-machine section. Check it.

## 9. Automation (section 15 to 20)

- **Six devices** do six tech-mod crafting tables: Enchanting Forge (Enchanting Apparatus, 130 recipes), Sanguine Alembic (Alchemy Table, 130), Tartaric Foundry (Hellfire Forge, 108 of 123), Source Crucible (Imbuement Chamber, 47 of 49), Verdant Font (Natural Altar, 43), Coven Retort (Mixing Cauldron, 40 of 43).
- Aura paid in time. Multiblock structures.

## 10. Mechanics and stats pages

- **Combat tab in the stats menu (b4).** Shows weapon damage types and every combo.
- **Stats menu redone (b4).** Class, skills, difficulty, ring and attributes.
- **How Stats Work chapter (6.6.5b3 section 35 and additions).** Exists in the wiki. Compare with the new numbers.

## 11. Changes page

- The wiki's Changes page has entries up to 2026-10-30. Add entries for each version above. Keep the Changes page short per version.

## 12. Removed mods (wiki text to clean up)

Mods removed in the notes (check whether any wiki page still mentions them): Combat Roll, Companions, KnightLib, Animights, Create Hypertubes, Create Pattern Schematics, Create Contraption Terminals, Create Bells and Whistles, Sophisticated Storage Create, Create Fantasizing Again, Create Interiors, Create Stock Bridge, Create Ultimate Factory, Create Deco, Sophisticated Backpacks Create, Faunify, Regions Unexplored, Tome of Wonders, Dungeon Revival, Simply Swords Overhaul, Mowzie's Cataclysm, Long NBT Killer, Biomancy, Dark Doppelganger, Sky Villages, dodo's mobs, Snad, Torchmaster, Configured, Controlling, Searchables, Better Climbing, Powah, Thermal Cultivation, Too Many Glyphs, Alex's Delight, L2 Backpack, Block Pack, Storage Drawers, Streams Reflowing.

## 13. Open questions for the user

- Confirm the 6.6.6 jar set (and whether the local instance is the 6.6.6 release).
- Which section comes first after the pack check (see the proposed order in the conversation).
- Whether the Changes page should have one entry per version or one per patch post.
