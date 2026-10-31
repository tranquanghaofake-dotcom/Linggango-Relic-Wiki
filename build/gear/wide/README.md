# Wide gear scan (Oct 2026)

Replaces the gate-tag-only target list of `prep.py` with every weapon and armor in every jar.

Work dir `G` = a copy of `build/gear` holding the inputs of `build.sh`, plus `srv/` with the 1.20.1 server jar in Mojang class names and SRG member names: from the Forge 47.4.20 installer (`--installServer`), or without running it, `python3 -I srgjar.py <Mojang 1.20.1 server.jar> server.txt joined.tsrg G` (Mojang's server mappings + MCPConfig 1.20.1-20230612.114412; 4 s). `jawa` (MIT, `pip install jawa==2.2.0`) is needed by mjvm. `targets_wide.py` and `merge.py` also read `../../src/gear_data.js` and `targets_wide.py` reads `equip_missing.json` from G's parent: link them there (`pack_audit/eqa/equip_missing.json`).

1. `clsgraph.py G` builds the class hierarchy over all jars.
2. `targets_wide.py G` writes the targets by class (Sword/Axe/Digger/Trident/Bow/Crossbow/Armor…), by tag and from attributesetter. It drops curios and pure tools.
3. `vanilla.py G` reads vanilla gear values from the server jar.
4. `gear_extract_wide.py G` runs mjvm (`../mjvm.py`) per namespace and writes `ext_raw/<ns>.json`.
5. `merge.py G` writes `gear_base.json` and `extract_report.json`.
6. `../gear_data.py G gear.json` builds the gear table. It handles gates (including `linggango_tweaks:gated/*`), summon weapons, merges level/form variants and filters out non-weapons. Copy it to `build/patches/gear_table.json`, which `build/patches/gear_rebuild.py` applies.

Result: 2556 scanned items. 2524 have stats; 49 failed (see `extract_report.json`). The table has 2070 entries and 327 sets.
