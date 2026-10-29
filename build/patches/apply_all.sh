#!/usr/bin/env bash
# Derived data, then build. curio_recipes, boss_stats and boss_order edit src/data.js in place (idempotent); gear_pipeline and wiki_data write their files from JSON.
# The one-time curio edits are in build/migrations (applied already; not run here).
set -e; H=$(cd "$(dirname "$0")" && pwd)
for p in curio_recipes boss_stats boss_order gear_pipeline wiki_data; do python3 "$H/$p.py"; done
python3 "$H/../build.py"
# curio power tiers come from the built site's measured curio scores (gear.js); when they change, write them in and build again
[ -f "$H/curio_tiers.json" ] || echo '{}' > "$H/curio_tiers.json"
if ! NODE_PATH=${NODE_PATH:-$(npm root -g)} node "$H/curio_tiers.js"; then python3 "$H/wiki_data.py"; python3 "$H/../build.py"; fi
