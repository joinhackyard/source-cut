#!/usr/bin/env bash
# setup-assets.sh: fetch the open-licence fonts and GSAP the templates use, and synthesise the engine's sound effects,
# into engine/assets/ (git-ignored). Run once after cloning. Fonts: SIL Open Font License. GSAP: standard no-charge licence.
set -euo pipefail
A="$(cd "$(dirname "$0")/.." && pwd)/engine/assets"
mkdir -p "$A/sfx"
get(){ [ -s "$A/$2" ] || curl -fsSL "$1" -o "$A/$2"; echo "  $2"; }
get https://cdn.jsdelivr.net/npm/@fontsource-variable/space-grotesk@5.1.0/files/space-grotesk-latin-wght-normal.woff2 SpaceGrotesk-latin.woff2
get https://cdn.jsdelivr.net/npm/@fontsource-variable/inter-tight@5.1.0/files/inter-tight-latin-wght-normal.woff2 InterTight-latin.woff2
get https://cdnjs.cloudflare.com/ajax/libs/gsap/3.14.2/gsap.min.js gsap-3.14.2.min.js
# Sound effects, made from scratch so there is nothing to license. Lengths match build_lib.SFX_LEN.
# Swap in your own files with the same names and lengths if you have better ones.
fx(){ [ -s "$A/sfx/$1" ] || ffmpeg -v error -y -f lavfi -i "$2" -t "$3" -ar 48000 -ac 2 "$A/sfx/$1"; echo "  sfx/$1"; }
fx tick.wav        "sine=f=2400:d=0.1,volume=0.6,afade=t=out:st=0.01:d=0.09" 0.1
fx lock.wav        "sine=f=880:d=0.28,volume=0.5,afade=t=out:st=0.02:d=0.26" 0.28
fx impact-low.wav  "sine=f=46:d=2.1,volume=1.4,afade=t=out:st=0.05:d=2.05" 2.1
fx whoosh-1.wav    "anoisesrc=d=0.7:c=pink:a=0.5,bandpass=f=900:w=600,afade=t=in:d=0.35,afade=t=out:st=0.35:d=0.35" 0.7
fx whoosh-2.wav    "anoisesrc=d=0.85:c=pink:a=0.5,bandpass=f=700:w=500,afade=t=in:d=0.4,afade=t=out:st=0.4:d=0.45" 0.85
fx whoosh-3.wav    "anoisesrc=d=0.9:c=brown:a=0.6,bandpass=f=500:w=400,afade=t=in:d=0.45,afade=t=out:st=0.45:d=0.45" 0.9
fx riser.wav       "anoisesrc=d=2.85:c=white:a=0.25,highpass=f=1200,afade=t=in:d=2.6,afade=t=out:st=2.6:d=0.25" 2.85
fx flap-clatter.wav "anoisesrc=d=0.6:c=white:a=0.4,bandpass=f=3000:w=1500,tremolo=f=28:d=0.9,afade=t=out:st=0.3:d=0.3" 0.6
echo "assets ready in $A"
