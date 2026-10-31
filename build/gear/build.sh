#!/usr/bin/env bash
# Rebuild the gear data and the wiki. $1 = work dir holding:
#   pack/src (unzipped Linggango-V6.6.5b4.zip), pack/mods/*.jar (the 476 mods of its manifest, see dl.py),
#   srv/libraries/.../server-1.20.1-*-srg.jar (from the Forge 47.4.20 installer, --installServer)
set -euo pipefail
W=$(cd "$1" && pwd); H=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$W/scripts" && cp "$H"/{mjvm.py,gear_extract.py,gear_data.py,recipes.py,icons.py} "$H"/../patches/gearlib.py "$H"/../pack_audit/{mcassets.py,block_render.py,tints.py} "$W/scripts/"
cd "$W"
python3 "$H/prep.py" "$W"                      # gates.json, ns2jar.json, lang.json, targets.json, gns.json, relic_acts.json
python3 scripts/recipes.py "$W"                # rec.json
python3 scripts/gear_extract.py "$W"           # gear_base.json (mini JVM over the mods' registration code)
python3 scripts/gear_data.py "$W" gear.json    # GE / GS
node "$H/icon_ids.js" "$W"                     # icon_ids.json: gear + ingredients the wiki has no icon for
python3 scripts/icons.py "$W" icon_ids.json gear_icons.json
python3 "$H/patch_wiki.py" gear.json gear_icons.json gns.json
