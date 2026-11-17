# Spells: one library page for all 709 spells, and the missing clips

Approved 2026-11-17 by the owner: the "library, three columns" layout (option 1 of three shown as sketches); clips for every spell that can
have one, a stated reason on the card for every one that cannot.

## What the reader sees
One Spells page for all four systems (Iron's Spells 306, Goety 209, Ars Nouveau 168, Brutality 26; the pack turns off 10 more).
- Top: one search box over every system, and the system chips with their counts (All, Iron's, Goety, Ars, Brutality).
- Left: filters as chips with live counts: school (Iron's), spell type (Goety), kind and tier (Ars), school (Brutality), how it is cast,
  rarity, mod, "has a clip"; and a sort (name, cost, cooldown).
- Middle: one compact row per spell: its icon in an inventory slot, name, school/type in its colour, the system, cost and cooldown, a play
  mark when it has a clip. Rows load as you scroll (the page stays under 5000 nodes).
- Right: the selected spell: the clip (plays muted, loops), name, school, every number the system has, description, the effects it applies,
  and, when there is no clip, why. On phones the detail opens full screen with a back button.
- Every spell has its own link (`#spells/<id>`); `#spells/<system>` opens a system; the Effects page's `#spells/<id>` links keep working.
The look stays the wiki's Minecraft GUI: bevelled panels, inset slots, stone buttons, the vanilla tooltip.

## Data
`app.js` turns the four lists (window.SPL, GSPL, ASPL, BSPL) into one shape (id, system, name, icon, group, colour, cast, cost, cooldown,
the system's own numbers, description, clip, reason). `build/clips/noclip.json` holds the reason for every enabled spell without a clip,
from the clip reviews in docs/NOTES.md.

## Clips
The 74 that can still be made get new stage setups (a different approach from the two that failed: a fall from height for Glide, Slowfall
and Bounce, several targets for Pierce and Split, a pond for Watery Grave and Evaporate, a servant saved to the focus for Goety's Command,
Order, Troop and Call, and so on), recorded in the background while the page is built. Seven cannot have a clip (five Goety Revelation
focuses that hold an empty spell, Paralyzing Skreech without Alex's Mobs, Piercing Moonlight crashes the client).

## Done when
Every enabled spell has an approved clip or a reason in noclip.json (checks/spells.js); any spell is found in two actions; the page reads
well at 1440 and 375 px; `bash build/check.sh` green; the site run green and `/build.txt` names the commit.

## Progress
- 2026-11-17: the library page is built (`app.js spellsPage`, CSS in `style.game.css` "spells: the library"); `build/clips/noclip.json` gives the
  reason for each of the 81 spells without a clip, and `patches/wiki_data.py` asserts every spell the pack leaves on has a clip or a reason;
  `checks/spells.js` checks the counts, the chips, the links and the reasons; `site_check.js` looks for the clip in the detail panel.
- Clips: Linggango Tweaks needs a third library chain (Enigmatic Legacy after L2 Hostility): stopped, its 6 focuses keep their reason. Five Goety
  Awaken focuses (Chip, Chip Rain, Ghost Missile, Fate Dice, Swamp Mine) throw entities of Meet Your Fight, which the pack has and the recording
  stage lacked: added to the stage and recorded again.
- 2026-11-17, second session part: a reader asked what spell power changes in each spell. Approved scope: Iron's spells from the running game (which
  tooltip lines the school's power and the level change, with the base numbers at the lowest and highest level), one rule each for the other three
  systems read from their code (Brutality's school level adds levels for damage only and Spell Damage multiplies it; Ars's own Spell Power adds to
  damage, augments do the rest; a Goety focus grows with its enchantments, and Goety Revelation adds its own Spell Power attributes). The export also
  corrected four spells' data (three schools, one turned off) and gave a school and levels to the 95 spells the config does not list.
- Clips, second stage round: 3 more (Glide, Knockback, Heal); the rest of the round showed nothing new and keeps its reason (three tries each).

