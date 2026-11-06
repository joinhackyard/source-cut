#!/usr/bin/env bash
# Sync a project folder to the render VM and run a hyperframes command there, inside the hyperframes-runner image.
#   tools/render/vm.sh <project-dir> <hyperframes args...>   e.g. tools/render/vm.sh films/my-film/film snapshot --at 2,9.5
#   tools/render/vm.sh <project-dir> --pull <remote-path>    copy one file back (e.g. renders/final.mp4)
set -euo pipefail
. "$(dirname "$0")/../lib/env.sh"
P=${1%/}; shift
R="$SOURCE_CUT_REMOTE_ROOT/$P"
if [ "${1:-}" = "--pull" ]; then
  mkdir -p "$P/$(dirname "$2")"
  # the container writes as root; hand the files back to the login user before copying
  "${SC_SSH[@]}" "docker run --rm -v \$(realpath $R):/work hyperframes-runner chown -R \$(id -u):\$(id -g) /work"
  scp -q -i "$SOURCE_CUT_SSH_KEY" "$SOURCE_CUT_RENDER_HOST:$R/$2" "$P/$2"
  exit 0
fi
"${SC_SSH[@]}" "mkdir -p $R"
rsync -az --delete -e "ssh -i $SOURCE_CUT_SSH_KEY" --exclude renders/ --exclude snapshots/ --exclude .hyperframes/ \
  "$P/" "$SOURCE_CUT_RENDER_HOST:$R/"
"${SC_SSH[@]}" "mkdir -p $SOURCE_CUT_REMOTE_ROOT/.cache && docker run --rm -v \$(realpath $R):/work \
  -v \$(realpath $SOURCE_CUT_REMOTE_ROOT/.cache):/root/.cache hyperframes-runner hyperframes $*"
