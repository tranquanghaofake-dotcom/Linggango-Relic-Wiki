#!/usr/bin/env bash
# Rebuild assets/lib and assets/catalog.csv from scratch. W = work dir (pack/, git/, ext/, mr/ as made by the phase A/B steps).
# Usage: bash build_library.sh <W> <assets dir>
# W must hold: pack/ (phase A: files/, scan.json), git/mcmeta @26.3-assets, git/bedrock, git/faithful32 (sparse, see specs/),
# git/v1201.txt, ext/kenney/*, ext/oga/oga_selected.json + files/ (oga.py fetch), mr/ + mr_fetched.json + mr_repocheck.json
# (mr_discover.py → mr_fetch.py → mr_scan.py → repocheck.py), gen/. Copies of the json inputs are in tools/data/.
set -euo pipefail
W=$1; A=$2; T=$(dirname "$(readlink -f "$0")")
rm -rf "$A/lib" "$A/catalog.csv"
python3 -I "$T/extract.py" "$W/pack" "$A/sources.csv" "$A"
python3 -I "$T/../fxgen.py" "$W/gen/out"
for s in vanilla bedrock faithful32 kenney_particles kenney_smoke gen; do python3 -I "$T/ingest.py" "$A" "$T/specs/$s.json" "$W"; done
cp "$W/gen/out/contact_sheet.png" "$A/lib/lgw-fxgen/contact_sheet.png"
python3 -I "$T/mr_extract.py" "$W" "$A"
python3 -I "$T/oga.py" ingest "$W" "$A"
python3 -I "$T/dedupe.py" "$A"
python3 -I "$T/sheets.py" "$A"
python3 -I "$T/shortlist.py" "$A"
python3 -I "$T/gallery.py" "$A"
