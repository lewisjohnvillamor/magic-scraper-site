#!/usr/bin/env bash
# Build the short-form product cuts with Hyperframes.
#
#   tools/brag/build.sh            both cuts
#   tools/brag/build.sh cut1       just the general one
#   tools/brag/build.sh drill      just the drill-down one
#   CHECK_ONLY=1 tools/brag/build.sh   lint/runtime/layout gate, no render
#
# What is tracked and what is not, on the same rule as tools/tiktok/*.webm:
# the sources here are the artefact, and brag-output/ is a build directory that
# is gitignored and disposable. Everything it needs is assembled from files
# that already live in this repo or in the extension repo beside it, so a
# fresh clone can rebuild the videos without hunting for a missing asset.
#
# Renders locally. Hyperframes can render on HeyGen's cloud instead, but the
# default path needs no account: it downloads its own Chrome Headless Shell on
# first run (~114MB, cached in ~/.cache/hyperframes) and uses system ffmpeg.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SITE="$(cd "$HERE/../.." && pwd)"
OUT="$SITE/brag-output"
EXT="${EXT_REPO:-$SITE/../Magic-Data-Scraper-}"
HF_VERSION="0.8.55"

# Pinned so a cut re-renders identically months later. Kept out of the repo's
# own package.json: this is video tooling, not a site dependency.
HF_HOME="$OUT/.hyperframes"
HF="$HF_HOME/node_modules/.bin/hyperframes"
if [ ! -x "$HF" ]; then
  echo "→ installing hyperframes@$HF_VERSION (one-off, into $HF_HOME)"
  mkdir -p "$HF_HOME"
  (cd "$HF_HOME" && npm init -y >/dev/null 2>&1 && npm install --silent "hyperframes@$HF_VERSION")
  "$HF" telemetry disable >/dev/null 2>&1 || true   # this product ships none; neither does its marketing
fi

[ -f "$OUT/sfx/tick.wav" ] || "$HERE/make-sfx.sh" "$OUT/sfx" >/dev/null

# The beds, trimmed onto each cut's grid. The trim is never arbitrary: each
# track's beats start a little way in, so cutting there puts every beat on an
# exact multiple of video time -- and a strong cue then lands on the reveal.
#   cut1  vol-1  120.19 BPM  trim 3.02  cue 17.02 -> t=14.00
#   drill vol-12 109.96 BPM  trim 8.74  cue 22.93 -> t=14.19
# Both CC BY 4.0, Sascha Ende / ende.app. Credit them wherever a cut is posted.
trim_music() {           # <source> <start> <length> <out>
  local src="$1" start="$2" len="$3" dst="$4"
  [ -f "$dst" ] && return 0
  if [ ! -f "$src" ]; then
    echo "!! need the source track at $src (ende.app, CC BY 4.0)" >&2; exit 1
  fi
  ffmpeg -hide_banner -v error -y -ss "$start" -i "$src" -t "$len" \
    -af "afade=t=in:st=0:d=0.4,afade=t=out:st=$(awk -v l="$len" 'BEGIN{printf "%.3f", l-1.3}'):d=1.3" \
    -c:a libmp3lame -q:a 3 "$dst"
}
trim_music "${MUSIC_SRC:-$OUT/.music-source.mp3}"             3.02 20.5  "$OUT/music.mp3"
trim_music "${MUSIC_SRC_DRILL:-$OUT/.music-source-drill.mp3}" 8.74 20.74 "$OUT/music-drill.mp3"
trim_music "${MUSIC_SRC_LONG:-$OUT/.music-source-long.mp3}"   1.60 35.8  "$OUT/music-long.mp3"

build_one() {
  local name="$1" src="$HERE/src/$1" proj="$OUT/$1" out="$2" poster_at="$3"
  echo "── $name"
  mkdir -p "$proj/compositions" "$proj/assets"

  cp "$src/index.html" "$proj/"
  cp "$src/compositions/"*.html "$proj/compositions/"

  # meta/config: written rather than copied, so the project is self-describing.
  cat > "$proj/hyperframes.json" <<JSON
{ "\$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
  "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
  "paths": { "blocks": "compositions", "components": "compositions/components", "assets": "assets" },
  "media": { "autoProxy": true } }
JSON
  printf '{ "id": "magic-scraper-%s", "name": "magic-scraper-%s" }\n' "$name" "$name" > "$proj/meta.json"

  cp "$SITE/assets/fonts/fraunces-var.woff2" "$SITE/assets/fonts/archivo-var.woff2" "$proj/assets/"
  cp "$OUT/music.mp3" "$OUT/music-drill.mp3" "$OUT/music-long.mp3" "$OUT/sfx/"*.wav "$proj/assets/"

  # GSAP vendored: a composition must make no network request at render time.
  [ -f "$OUT/gsap.min.js" ] || curl -sSfL -o "$OUT/gsap.min.js" \
    "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
  cp "$OUT/gsap.min.js" "$proj/assets/"

  # Real captures of the real popup, from the extension repo. The drill cut
  # uses chain-builder.png -- the panel where the chain is configured, rebuilt
  # there by tools/shoot_chain.mjs.
  cp "$EXT/docs/store/cws-screenshot-2-crawl.png" "$proj/assets/s2-crawl.png"
  cp "$EXT/docs/store/cws-screenshot-4-changes.png" "$proj/assets/s4-changes.png"
  cp "$EXT/docs/store/chain-builder.png" "$proj/assets/chain-builder.png"

  # Each cut drifts the page it is arguing about: cut1 the table, the others
  # the catalogue. Built from a live capture, pre-blurred so the drift is free.
  cp "$OUT/backdrop-${name}.png" "$proj/assets/backdrop.png" 2>/dev/null \
    || cp "$OUT/backdrop.png" "$proj/assets/backdrop.png"
  cp "$OUT/grain.png" "$proj/assets/grain.png"

  (cd "$proj" && "$HF" check)
  [ -n "${CHECK_ONLY:-}" ] && return 0

  # CRF 20, not the default 16. The default is near-lossless, which was free
  # while the frames were flat paper and cost 26 Mbps the moment a grain layer
  # and a drifting backdrop arrived -- the same cut went 4.7MB -> 68MB. Every
  # platform re-encodes on upload, so those bits are spent twice and kept
  # never.
  (cd "$proj" && "$HF" render --output "$out" --crf "${CRF:-20}")

  # Poster baked as frame 0 so the idle thumbnail is a chosen frame everywhere.
  ffmpeg -hide_banner -v error -y -ss "$poster_at" -i "$out" -frames:v 1 -q:v 2 "${out%.mp4}.jpg"
  ffmpeg -hide_banner -v error -y -i "$out" -i "${out%.mp4}.jpg" -map 0 -map 1 -c copy \
    -c:v:1 mjpeg -disposition:v:1 attached_pic "${out%.mp4}.tmp.mp4"
  mv "${out%.mp4}.tmp.mp4" "$out"

  # Audio is the thing that fails silently: an <audio> without an id renders
  # mute and nothing warns at playback. Assert it carries signal.
  local mean
  mean=$(ffmpeg -hide_banner -i "$out" -map 0:a -af volumedetect -f null /dev/null 2>&1 \
         | sed -n 's/.*mean_volume: \(-\?[0-9.]*\) dB.*/\1/p')
  if [ -z "$mean" ] || [ "${mean%.*}" -lt -60 ] 2>/dev/null; then
    echo "!! $out has no audible audio (mean=${mean:-none})" >&2; exit 1
  fi
  echo "   $out  mean ${mean} dB"
}

case "${1:-all}" in
  cut1)  build_one cut1  "$OUT/brag.mp4"       15.4 ;;
  drill) build_one drill "$OUT/brag-drill.mp4" 15.6 ;;
  long)  build_one long  "$OUT/brag-long.mp4"  19.5 ;;
  all)   build_one cut1  "$OUT/brag.mp4"       15.4
         build_one drill "$OUT/brag-drill.mp4" 15.6
         build_one long  "$OUT/brag-long.mp4"  19.5 ;;
  *) echo "usage: $0 [cut1|drill|long|all]" >&2; exit 2 ;;
esac
