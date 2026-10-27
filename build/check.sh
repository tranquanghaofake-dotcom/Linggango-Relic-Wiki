#!/usr/bin/env bash
# Verify the build: (1) every data patch is idempotent and the committed src/ and outputs are what the patches produce,
# (2) the built pages load without script errors (build/check.js). Run before every commit.
set -e; H=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$H"); cd "$R"
bash "$H/patches/apply_all.sh" >/dev/null
bash "$H/patches/apply_all.sh" >/dev/null
sum() { sha1sum "$H"/src/*.js index.html static/* | sha1sum; }
a=$(sum); bash "$H/patches/apply_all.sh" >/dev/null; b=$(sum)
[ "$a" = "$b" ] && echo "patches: idempotent, build reproducible" || { echo "patches: NOT idempotent (a patch changes src/ when run again)"; exit 1; }
NODE_PATH=$(npm root -g) node "$H/check.js" dist/Linggango_Relic_Wiki.html
NODE_PATH=$(npm root -g) node "$H/style_check.js" dist/Linggango_Relic_Wiki.html
