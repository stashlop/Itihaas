#!/usr/bin/env bash
# Re-download the self-hosted front-end libraries into itihaas/static/vendor.
# Requires Node.js/npm (only the registry is used; nothing is installed globally).
#
#   ./scripts/vendor.sh
#
# Bump a version below, run the script, then run the test-suite and click
# through the pages that use the library before committing.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/itihaas/static/vendor"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

BOOTSTRAP=4.6.2      # stay on v4: templates use v4 data-* APIs and utility classes
JQUERY=3.7.1
FONTAWESOME=5.15.4
SWIPER=8.4.7
CHARTJS=4.4.7
LEAFLET=1.9.4
SPLITTING=1.0.6

fetch() {  # fetch <npm-spec> <dir-name>
  (cd "$TMP" && npm pack --silent "$1" >/dev/null)
  mkdir -p "$TMP/$2" && tar -xzf "$TMP"/*.tgz -C "$TMP/$2" --strip-components=1 && rm "$TMP"/*.tgz
}

rm -rf "$DEST" && mkdir -p "$DEST"

fetch "bootstrap@$BOOTSTRAP" bootstrap
mkdir -p "$DEST/bootstrap"
cp "$TMP/bootstrap/dist/css/bootstrap.min.css" "$TMP/bootstrap/dist/js/bootstrap.bundle.min.js" "$DEST/bootstrap/"

fetch "jquery@$JQUERY" jquery
mkdir -p "$DEST/jquery" && cp "$TMP/jquery/dist/jquery.min.js" "$DEST/jquery/"

fetch "@fortawesome/fontawesome-free@$FONTAWESOME" fontawesome
mkdir -p "$DEST/fontawesome/css"
cp "$TMP/fontawesome/css/all.min.css" "$DEST/fontawesome/css/"
cp -r "$TMP/fontawesome/webfonts" "$DEST/fontawesome/"
# Modern browsers only need woff2/woff; drop legacy eot/svg/ttf to keep the repo small.
rm -f "$DEST"/fontawesome/webfonts/*.eot "$DEST"/fontawesome/webfonts/*.svg "$DEST"/fontawesome/webfonts/*.ttf

fetch "swiper@$SWIPER" swiper
mkdir -p "$DEST/swiper" && cp "$TMP/swiper/swiper-bundle.min.css" "$TMP/swiper/swiper-bundle.min.js" "$DEST/swiper/"

fetch "chart.js@$CHARTJS" chartjs
mkdir -p "$DEST/chartjs" && cp "$TMP/chartjs/dist/chart.umd.js" "$DEST/chartjs/chart.umd.min.js"

fetch "leaflet@$LEAFLET" leaflet
mkdir -p "$DEST/leaflet" && cp -r "$TMP/leaflet/dist/leaflet.css" "$TMP/leaflet/dist/leaflet.js" "$TMP/leaflet/dist/images" "$DEST/leaflet/"

fetch "splitting@$SPLITTING" splitting
mkdir -p "$DEST/splitting" && cp "$TMP/splitting/dist/splitting.min.js" "$DEST/splitting/"

cat > "$DEST/VERSIONS.txt" <<VERSIONS
bootstrap $BOOTSTRAP
jquery $JQUERY
@fortawesome/fontawesome-free $FONTAWESOME
swiper $SWIPER
chart.js $CHARTJS
leaflet $LEAFLET
splitting $SPLITTING
VERSIONS
echo "Vendored libraries written to $DEST"
