#!/usr/bin/env bash
# Derived data, then build. curio_recipes, boss_stats and boss_order edit src/data.js in place (idempotent); gear_pipeline and wiki_data write their files from JSON.
# The one-time curio edits are in build/migrations (applied already; not run here).
set -e; H=$(cd "$(dirname "$0")" && pwd)
for p in curio_recipes boss_stats boss_order gear_pipeline wiki_data; do python3 "$H/$p.py"; done
python3 "$H/../build.py"
