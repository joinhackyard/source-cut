# Source this from any Source Cut shell tool: loads <repo>/.env and sets defaults.
SC_ROOT=${SC_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../.." && pwd)}
[ -f "$SC_ROOT/.env" ] && set -a && . "$SC_ROOT/.env" && set +a
: "${SOURCE_CUT_RENDER_HOST:?set SOURCE_CUT_RENDER_HOST in .env (user@host of your render VM)}"
SOURCE_CUT_SSH_KEY=${SOURCE_CUT_SSH_KEY:-$HOME/.ssh/id_ed25519}
SOURCE_CUT_SSH_KEY=${SOURCE_CUT_SSH_KEY/#\~/$HOME}
SOURCE_CUT_REMOTE_ROOT=${SOURCE_CUT_REMOTE_ROOT:-videos}
SC_SSH=(ssh -o ServerAliveInterval=15 -i "$SOURCE_CUT_SSH_KEY" "$SOURCE_CUT_RENDER_HOST")
