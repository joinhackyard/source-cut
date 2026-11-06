---
name: source-cut-setup
description: One-time setup for Source Cut - create the render VM, build the hyperframes-runner Docker image, configure .env with Azure Speech and Azure OpenAI keys, and fetch fonts, GSAP and sound effects. Use when a user clones Source Cut, when a tool says a setting is missing, or when the render VM is new.
---

# Source Cut setup

## 1. Render VM

Any Linux VM with Docker works. A 16–32 core VM renders a 7-minute film in about 25 minutes; stop it when idle.

1. Create an Ubuntu VM with `tools/render/cloud-init.yaml` as user data (change the user name in it).
2. Restrict inbound SSH to your own IP.
3. Copy the repo's `tools/render/Dockerfile` to the VM and build the image:
   `docker build -t hyperframes-runner -f Dockerfile .`
4. Test: `ssh <host> 'docker run --rm hyperframes-runner hyperframes --version'`.

## 2. `.env`

`cp .env.example .env`, then fill in:

| Key | What |
| --- | --- |
| `SOURCE_CUT_RENDER_HOST`, `SOURCE_CUT_SSH_KEY`, `SOURCE_CUT_REMOTE_ROOT` | ssh target, key, and the project root on the VM |
| `SPEECH_KEY`, `SPEECH_REGION`, `SPEECH_VOICE` | Azure AI Speech resource (narration and word timings) |
| `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_IMAGE_DEPLOYMENT` | Azure OpenAI image deployment (thumbnails) |
| `SOURCE_CUT_USER_AGENT` | a descriptive User-Agent for Wikimedia Commons (no personal email) |

Never commit `.env`; it is git-ignored. Never echo keys into logs or chat.

## 3. Local tools

Python 3.10+, ffmpeg/ffprobe, Node.js (for yt-dlp's JS challenges), `yt-dlp`, `pip install pillow certifi`.
Then `scripts/setup-assets.sh` fetches Space Grotesk and Inter Tight (SIL OFL), GSAP 3.14.2, and synthesises the sound
effects the engine uses.

## 4. Check

`scripts/new-film.sh test`, then follow `source-cut-voice` for one line and `source-cut-edit` for one shot, and
snapshot it with `tools/render/vm.sh films/test/film snapshot --at 1`. Delete `films/test` afterwards.

## Troubleshooting

- `SSL: CERTIFICATE_VERIFY_FAILED` on macOS: `export SSL_CERT_FILE=$(python3 -c "import certifi;print(certifi.where())")`.
- Files on the VM owned by root: the container writes as root; `vm.sh --pull` chowns before copying.
- Snapshots time out while a render runs: queue renders (see `source-cut-render`), never run two at once.
