#!/usr/bin/env bash
# Build and verify the wiki — the same checks the site workflow runs before it deploys (about 5 minutes):
# (1) the patch chain is idempotent and the build reproducible (three runs, same bytes);
# (2) the offline file renders every detail page with the shared layout and keeps the data invariants (check.js)
#     and the pixel and spacing rules (style_check.js);
# (3) the deployable site (index.html + static/) loads with every file found and no script errors (site_check.js).
set -e; H=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$H"); cd "$R"
export NODE_PATH=${NODE_PATH:-$(npm root -g)}
bash "$H/patches/apply_all.sh" >/dev/null
bash "$H/patches/apply_all.sh" >/dev/null
sum() { sha1sum "$H"/src/*.js index.html static/* | sha1sum; }
a=$(sum); bash "$H/patches/apply_all.sh" >/dev/null; b=$(sum)
[ "$a" = "$b" ] && echo "patches: idempotent, build reproducible" || { echo "patches: NOT idempotent (a patch changes src/ when run again)"; exit 1; }
node "$H/check.js" dist/Linggango_Relic_Wiki.html
node "$H/style_check.js" dist/Linggango_Relic_Wiki.html
node "$H/site_check.js" index.html
