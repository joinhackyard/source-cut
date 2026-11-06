#!/usr/bin/env bash
# cutout.sh <image> [<image> ...]: remove the background from photos on the render VM (rembg, birefnet-portrait for
# people; set MODEL=isnet-general-use for aircraft, buildings and objects). Writes <name>.png with alpha next to each
# input, under media/cutouts/ if the input sits in media/images/.
# First run builds a small rembg image on the VM and downloads the model (~1 GB).
set -euo pipefail
. "$(dirname "$0")/../lib/env.sh"
MODEL=${MODEL:-birefnet-portrait}
"${SC_SSH[@]}" 'mkdir -p ~/cut/in ~/cut/out ~/.rembg && rm -f ~/cut/in/* ~/cut/out/* && cd ~/cut && \
  (docker image inspect rembg-runner >/dev/null 2>&1 || (printf "FROM python:3.12-slim\nRUN pip install --no-cache-dir \"rembg[cpu,cli]\"\nENTRYPOINT [\"rembg\"]\n" > Dockerfile && docker build -q -t rembg-runner .))'
scp -q -i "$SOURCE_CUT_SSH_KEY" "$@" "$SOURCE_CUT_RENDER_HOST:cut/in/"
"${SC_SSH[@]}" "docker run --rm -v ~/cut:/w -v ~/.rembg:/root/.rembg rembg-runner p -m $MODEL /w/in /w/out >/dev/null 2>&1; ls ~/cut/out"
for f in "$@"; do
  d=$(dirname "$f"); d=${d/media\/images/media\/cutouts}; mkdir -p "$d"
  scp -q -i "$SOURCE_CUT_SSH_KEY" "$SOURCE_CUT_RENDER_HOST:cut/out/$(basename "${f%.*}").png" "$d/"
  echo "$d/$(basename "${f%.*}").png"
done
