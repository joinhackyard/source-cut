#!/usr/bin/env bash
# new-film.sh <slug>: create films/<slug> from templates/film, with fonts, GSAP and sound effects in place.
set -euo pipefail
R="$(cd "$(dirname "$0")/.." && pwd)"; S=$1; F="$R/films/$S"
[ -e "$F" ] && { echo "films/$S already exists"; exit 1; }
[ -s "$R/engine/assets/gsap-3.14.2.min.js" ] || "$R/scripts/setup-assets.sh"
mkdir -p "$R/films"
cp -R "$R/templates/film" "$F"
for p in film short thumbnail; do
  mkdir -p "$F/$p/assets/fonts" "$F/$p/assets/lib" "$F/$p/renders"
  cp "$R/engine/assets/"*.woff2 "$F/$p/assets/fonts/"; cp "$R/engine/assets/gsap-3.14.2.min.js" "$F/$p/assets/lib/"
done
mkdir -p "$F/media/"{voice,footage,images,cutouts,artifacts,bgm,sfx,raw}
cp "$R/engine/assets/sfx/"*.wav "$F/media/sfx/"
echo "films/$S ready. Next: write RESEARCH.md and SCRIPT.md (skill: source-cut-research, source-cut-script)."
