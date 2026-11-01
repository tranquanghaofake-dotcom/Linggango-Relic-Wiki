#!/usr/bin/env bash
# Build and verify the wiki — the same checks the site workflow runs before it deploys (about 5 minutes):
# (1) the patch chain is idempotent and the build reproducible (three runs, same bytes), and the curio tier run on that
#     build exits 0 (tiers unchanged; a crash or a change fails);
# (2) the offline file renders every detail page with the shared layout and keeps the data invariants (check.js)
#     and the pixel and spacing rules (style_check.js), and the checks that need fresh loads, other viewports, keys,
#     injected storage or timing (a11y_check.js);
# (3) the deployable site (index.html + static/) loads with every file found and no script errors (site_check.js).
set -e; H=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$H"); cd "$R"
export NODE_PATH=${NODE_PATH:-$(npm root -g)}
bash "$H/patches/apply_all.sh" >/dev/null
bash "$H/patches/apply_all.sh" >/dev/null
sum() { sha1sum "$H"/src/*.js index.html static/* | sha1sum; }
a=$(sum); bash "$H/patches/apply_all.sh" >/dev/null; b=$(sum)
[ "$a" = "$b" ] && echo "patches: idempotent, build reproducible" || { echo "patches: NOT idempotent (a patch changes src/ when run again)"; exit 1; }
# the tier run on the final build must agree with the committed tiers (exit 0, "unchanged"); a crash or a change fails here
node "$H/patches/curio_tiers.js" || { echo "curio_tiers: exit $? (3 = tiers changed, run apply_all.sh and commit; other = the tier run failed)"; exit 1; }
# check.js (the long one) runs beside the other three, which run one after another so a11y_check's timings are not measured
# against two other browsers; each prints its output when it ends, and any failure fails the whole run
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
node "$H/check.js" dist/Linggango_Relic_Wiki.html >"$T/check" 2>&1 & C=$!
rc=0
for s in style_check a11y_check site_check; do f=dist/Linggango_Relic_Wiki.html; [ $s = site_check ] && f=index.html
  node "$H/$s.js" "$f" >"$T/$s" 2>&1 || rc=1; done
wait $C || rc=1
cat "$T/check" "$T/style_check" "$T/a11y_check" "$T/site_check"; exit $rc
