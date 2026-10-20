# Pack audit (reads the modpack directly, no game run)
Work dir W holds `pack/src` (unzipped Linggango-V6.6.5b4.zip from CurseForge file 9071626) and `pack/mods` (the 476 jars, `python3 build/gear/dl.py W`).
1. `python3 build/gear/prep.py W` and `python3 build/gear/recipes.py W` → lang.json, ns2jar.json, gates.json, rec.json
2. `audit.py W REPO [n]` names / recipes / loot vs the wiki; `recheck.py W` recipes the pack's KubeJS removes or adds;
   `drops.py W` mob drop chances from the jars' loot tables; `tips.py W` lang tooltips for effects still without numbers.
