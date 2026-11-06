# Production playbook

Everything Hackyard used to make its films in November 2026, step by step: the tech stack, the exact commands, the
files, and the mistakes not to repeat. Three formats were proven:

- **A. Editorial reel** (55.6 s, 16:9). Real founders in their own words, real footage, every spoken word on screen.
  Producer feedback: _"you literally edited the video in cinematic style."_ Style rules: `editorial-reel.md`.
- **B. 3D brand film** (38.6 s). A Three.js world of builder blocks that assembles into the H monogram. Kept here for
  reference; it is not a documentary format and the producer did not take it forward.
- **C. Artifact reel** (approved 2 Nov 2026, the current reel format; ~62 s, 9:16). Founders in their own clips plus
  real artifacts (archived pages, documents, slides, the product app) with a marker on the key sentence. No stock, no
  3D. Recipe: `artifact-reel.md`.

This file is the _how_. For reels, start from format C: stock-b-roll reels and the 3D world were rejected (2 Nov 2026).
For the daily long-form films, follow `series-documentary.md`.

---

## 1. Tech stack

| Layer                      | Tool                                                                                                                                                     | Where it runs                                         |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| Composition (video = HTML) | **HyperFrames** 0.8.223 (`npx hyperframes`), GSAP 3.14.2 (vendored in `assets/lib/`), CSS                                                                | authored on your workstation, rendered on the VM      |
| 3D (format B)              | Three.js r0.184 (jsDelivr ESM), RoundedBoxGeometry, EffectComposer + BokehPass + a custom grain pass                                                     | inside the HyperFrames page                           |
| Edit generator             | a per-project `build.py` + `engine/build_lib.py` + `engine/template.html` → `index.html`                                                                 | workstation                                           |
| Footage grade              | HyperFrames `media-treatment` → `data-color-grading` attribute on every `<video>`/`<img>` (`engine/grade.json`)                                          | render time                                           |
| Render                     | Docker image `hyperframes-runner` (Node 22 + Chromium + FFmpeg + hyperframes, `tools/render/Dockerfile`) on a 32 vCPU cloud VM (Azure Standard_D32as_v5) | your render VM; ~6 min for 38–56 s of 1080p           |
| Narration                  | **Azure Speech** HD voice `en-US-Andrew:DragonHDLatestNeural` (REST, mp3 48 kHz), `tools/voice/azure_tts.py`                                             | anywhere the Speech key is available (see §2, rule 2) |
| Word timings / transcripts | **Azure Speech fast transcription** (`speechtotext/transcriptions:transcribe?api-version=2024-11-15`), `tools/voice/azure_stt.py`                        | same                                                  |
| Video understanding        | A vision-capable **Azure OpenAI** chat model (Hackyard used `gpt-6-astra`)                                                                               | same                                                  |
| Generated textures         | **Azure OpenAI `gpt-image-2`** (1536×1024, quality high)                                                                                                 | same                                                  |
| Stock footage/photos       | **Pexels API** (key passed per job as an env var, never written to files). Not used in formats C or the series.                                          | workstation (curl)                                    |
| Founder/archival clips     | **yt-dlp** in a scratch venv + certifi, `--js-runtimes node` (`tools/sources/yt_sections.sh`)                                                            | workstation only (YouTube blocks cloud IPs)           |
| Music + SFX                | **HeyGen audio catalog** (via the `media-use` skill's HeyGen helper); Openverse CC0 for the split-flap sound                                             | workstation (API)                                     |
| Analysis                   | ffmpeg / ffprobe (scene detect, contact sheets, silencedetect, ebur128 loudness)                                                                         | workstation (analysis only)                           |
| Brand                      | Hackyard house style (see below)                                                                                                                         | fonts copied into `assets/fonts/`                     |

Claude Code skills used for this: `hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use`, `gsap`,
`motion-video`, `saas-motion-video`, `showreel`, plus the ElevenLabs and Remotion skills during exploration.

Accounts that did **not** work: ElevenLabs (free tier disabled on the account) and HeyGen voices (needs HyperFrames
Pro). Azure Speech replaced both.

**House style.** This is the style used by Hackyard; swap in your own brand. Palette: surface `#090c13`, ink `#e7f0fb`,
white, blue `#2b5ce4`, light blue `#9cbdff`. Type: Space Grotesk (display), with Inter Tight and IBM Plex Mono as
supporting faces and EB Garamond as the caption serif. The H monogram sits on a 114×128 grid. CTA: "Find your people.
hackyard.org". The early reels used an older ground (`#07080b`), ink (`#f1f4f7`) and primary (`#6fb5fc`); the engine's
marker colour still derives from that light blue.

---

## 2. House rules

1. **Never render or test on your workstation.** It only authors files, downloads media and runs ffmpeg analysis.
   Everything HyperFrames runs on the render VM. (Parallel renders and encodes froze a laptop once.)
2. **Keys never leave the servers.** Run Azure calls where the keys already live (a server, a container, or a CI secret)
   and pipe scripts in over stdin, for example `docker exec -i <container> python - < tools/voice/azure_tts.py`. If you
   must fetch a key, pipe it from `az cognitiveservices account keys list` over stdin; never write it to disk. Pexels is
   passed only as a header env var.
3. **Never delete or stop the render VM** without a fresh, explicit yes from its owner. Hackyard's was deleted once by
   mistake.
4. **Never reuse an outdated product walkthrough.** Record the current app.
5. Brand colours only; no product comparisons; quiet, premium copy; an international voice.
6. **Rights for third-party founder clips are the publisher's call.** Hackyard made its own decision (1 Nov 2026). Make
   yours before you publish, credit every clip, and never imply endorsement.

---

## 2b. Reel length (every short-form format)

Decide the length before writing the script, then write to it (about 2.5 spoken words per second: 15 s ≈ 35–40 words,
30 s ≈ 75, 60 s ≈ 150). Default **30–45 s; never past 60 s**.

| Reel                            | Length  | Why                                                                                                                         |
| ------------------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------- |
| One idea, one artifact or story | 15–25 s | Best Instagram completion (7–15 s reels reported at 60–80%); the top faceless reels in one 50-reel analysis averaged 8–11 s |
| Short list (3 points)           | 30–40 s | Hook + ~8 s per point + end card; the default for most posts                                                                |
| Full list (5 points)            | 45–60 s | Upper limit; YouTube Shorts holds 73–76% completion at 50–60 s                                                              |

Instagram Reels favours ≤30 s (completion and rewatches drive reach); YouTube Shorts is comfortable at 45–60 s. Anything
longer belongs in a YouTube video. Each artifact or b-roll beat needs 2–3 s so the viewer can read it. Sources: Virvid
Shorts retention breakdown (2026), OpusClip Reels length guide, Vireuoess "I analyzed my top 50 faceless Reels" (2026).
Also in `artifact-reel.md` §2b.

## 3. Format A: the editorial reel, step by step

### Step 1. Study the reference with Azure AI (≈10 min)

```bash
# shots: scene cuts + 0.5 s frames → 10 contact sheets of 6 s each (4×3)
ffmpeg -i ref.mp4 -vf "select='gt(scene,0.28)',showinfo" -vsync vfr -f null - 2>&1 | rg -o "pts_time:[0-9.]+"
ffmpeg -i ref.mp4 -vf "fps=2,scale=480:-1" frames/f_%03d.jpg
for k in $(seq 0 9); do
  ffmpeg -start_number $((k*12+1)) -i frames/f_%03d.jpg -vf tile=4x3:padding=4 -frames:v 1 sheets/sheet_$k.jpg   # -frames:v 1, not 12
done
```

- **Transcript with word timings:** send 16 kHz mono wav to Azure fast transcription (`tools/voice/azure_stt.py`).
- **Shot-by-shot breakdown:** send all sheets + the cut list + the transcript to a vision model on Azure OpenAI:
  ```python
  import os
  from openai import AzureOpenAI
  client = AzureOpenAI(azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                       api_key=os.environ["AZURE_OPENAI_API_KEY"], api_version="2024-10-21")
  r = client.chat.completions.create(model=os.environ["AZURE_OPENAI_VISION_DEPLOYMENT"],
      messages=[{"role": "user", "content": [text_prompt, *image_url_parts]}], max_completion_tokens=16000)
  ```
  Ask for a shot list, structure, editing grammar, typography, look, sound and a recipe.
- Save the output next to the project (`reference/<name>/`) so the next edit can reuse it.

### Step 2. Script in 8 beats (`SCRIPT.md`)

Belief → proof story (two people + the missing third) → mechanism (founder quote) → obstacle on black → brand turn →
roles → 3-speed montage + "Don't build alone. Find your people. Build something real." → 4 s end card. Use real
founders' own words for belief and mechanism; the narrator carries the brand's lines.

### Step 3. Source everything in parallel (3 helper agents, ≈20 min)

- **Founder clips:** a yt-dlp venv in a scratch folder.
  ```bash
  python3 -m venv ytenv && ytenv/bin/pip install yt-dlp certifi
  export SSL_CERT_FILE=$(ytenv/bin/python -c "import certifi;print(certifi.where())")
  ytenv/bin/yt-dlp --js-runtimes node "ytsearch5:<quote>"                       # find
  ytenv/bin/yt-dlp --write-auto-subs --sub-langs en --skip-download <url>        # locate the quote's timestamps
  ytenv/bin/yt-dlp -f "bv*[height<=1080]+ba/b" --download-sections "*00:01:10-00:01:20" <url>
  ```
  Trim with ffmpeg to the exact sentence + 0.4 s handles, scale to 1920 and crop logos away. Record the source URL and
  in/out times in `assets/footage/SOURCES.md`. Watch for false starts (one 60 Minutes quote needed a `-tight` cut).
- **Pexels b-roll (format A only):** a shot list per beat (hands typing at night, hostel desk, small town, team at
  whiteboard, workbench, soldering, sketching, maths board, rocket, sprinters, hackathon, celebration, triumph, city at
  night). API `api.pexels.com/videos/search`. Take the 1920 file, trim 3–5 s, no audio, CRF 18. Credits go in
  `assets/stock/CREDITS.md`.
- **Public-domain stills:** Wikimedia Commons (_Creation of Adam_, Edison patent, a locomotive plan). Use
  `tools/sources/commons_fetch.py` and keep the author and licence for the credit.
- **gpt-image-2 textures (no slop):** prompt for _photographed/scanned physical media_ (paper, graphite, ink, cyanotype,
  film grain, natural imperfections, muted colour) and ban glossy renders, neon, glow, readable fake text, faces, logos
  and extra fingers. Review every image and regenerate once if it fails. Throttle to ≤10 images per minute. Textures
  only: never generate people.
- **Your own brand visuals:** Hackyard used its 3D yard rendered **without text**. Copy the project, hide the type layers
  (`.ty, .pin, #wm, #wm-sub, #wm-url, #leaders, #dim`), strip `<audio>`, then `render --start a --end b`.

### Step 4. Voice and word timings

- Narration: one mp3 per sentence (`tools/voice/azure_tts.py`, Andrew HD).
- Word timings for every narration file and every founder clip: `tools/voice/azure_stt.py` (narration) and
  `tools/edit/clip_words.sh` (clips) → `assets/voice/words.jsonl`, `assets/footage/words-jobs.jsonl`.
- When you tar files on macOS to send them to a server, use `COPYFILE_DISABLE=1 tar` so `._` files don't sneak in.

### Step 5. Music and SFX

- Search the HeyGen catalog for ≥62 s tracks; measure 1 s RMS envelopes with `ffmpeg astats`. Pick the track whose
  **break and re-entry** can land on the brand turn and whose **decay** lands on the end card. For the reference reel,
  track `m-fa9fddde`: file 30.0 s → film 29.85 s.
- Two music clips from the same file: a quiet bed under the founders (vol 0.09), full from the turn (vol 0.2, 2.5 s
  fade-out).
- SFX only at pivots: whoosh into cuts, tick on highlights, impact on the turn, riser into the montage, soft impact on
  the end card.

### Step 6. Build the edit (`build.py`)

- `VOICE`: (id, src, film start, volume, caption groups). Groups are `(word count, style)`; the script asserts they add up
  to the transcript.
- `SHOTS`: (src, start, end, media_start, kind). Kinds: `v` full video, `i` still with slow push, `L`/`R` split panels,
  `k` black card (`collage` = floating paper drawings).
- Caption styles: `r` serif word(s), `a` serif line that builds, `E` Space Grotesk emphasis, `H` hero word, `S`
  blue selection highlight, `P` brand pill. Every word fades in at its own spoken time (opacity only, no blur: blur is
  too heavy).
- `PIVOTS`: 2-frame negative patch (`mix-blend-mode: difference` white box) on turning words, plus one full-frame flash
  on the cut into the brand turn.
- Grade: `engine/grade.json` (−0.6 EV, −32% sat, vignette 0.5, grain 0.22) and a bright variant (−1.05 EV) for known-bright
  sources; stamped onto every `<video>`/`<img>`.
- End card: the real monogram drawn from grid percentages + the wordmark in Space Grotesk.
- Run `python3 build.py` → `index.html`.

### Step 7. Check, look, fix (on the render VM)

```bash
export SOURCE_CUT_RENDER_HOST=<user>@<your-render-vm>
tools/render/vm.sh <project> check --json                       # fix every error
tools/render/vm.sh <project> snapshot --at 0.8,4,7.9,11.9,13.4,…  # 15–20 key frames
tools/render/vm.sh <project> --pull .hyperframes/artifacts/snapshots/<id>/contact-sheet-1.jpg
```

Look at every sheet: is text readable on bright frames? Is old text burned into reused footage? Is the grade consistent?

### Step 8. Render, master, deliver

```bash
tools/render/vm.sh <project> render --quality delivery --output renders/<name>-16x9.mp4
# loudness to social level, picture untouched
tools/render/loudness.sh in.mp4 out-final.mp4
# one-pass equivalent:
ffmpeg -i in.mp4 -c:v copy -af loudnorm=I=-15:TP=-1.5:LRA=11 -c:a aac -b:a 192k -movflags +faststart out-final.mp4
```

Verify with `ebur128` (≈ −15 LUFS, peak ≤ −1 dBFS) and a 16-frame contact sheet of the real file before sending.

---

## 4. Format B: the 3D brand film (short version)

1. `index.html`: a full-frame `<canvas>`, DOM kinetic type and audio. One GSAP linear clock tween with
   `onUpdate → world.render(t)`, plus `window.__hf.buildReady`.
2. `world.js` (Three.js):
   - Lighting: a PMREM softbox environment, key and rim lights that follow the look target, and PCF shadows.
   - Fog density = 0.42 / subject distance.
   - Camera: a keyframe list (t, pos, look, fov, aperture, ease).
   - Pinned type: labels and the wordmark are placed each frame by projecting 3D points to the screen.
   - Grain shader: hash on `floor(uv*res)`, otherwise it draws stripes.
3. Portrait: the same file with `if (V)` overrides (narrower horizontal view, reframed shots, wordmark pulled back, labels
   kept inside the safe band 168–1330 px).
4. Voice phrases are separate `<audio data-media-start>` clips, each placed on the frame where its picture lands.

---

## 5. Infrastructure cheat sheet

| What         | Value                                                                                                                                                                                                          |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Render VM    | One Azure Standard_D32as_v5 (32 vCPU, about $0.89/h while running). Restrict inbound SSH to your own IP range in the network security group. Set `SOURCE_CUT_RENDER_HOST=<user>@<host>`.                       |
| Create it    | Provision the VM with `tools/render/cloud-init.yaml` as custom data, then build `tools/render/Dockerfile` on it as `hyperframes-runner`.                                                                       |
| Run anything | `tools/render/vm.sh <project> <hyperframes args>` syncs the project and runs HyperFrames in the container; `--pull <path>` copies a file back (it chowns first).                                               |
| Azure AI     | Your Azure Speech resource (`SPEECH_KEY`, `SPEECH_REGION`) and your Azure OpenAI resource (`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, deployment names in env vars). Keep keys server-side (§2, rule 2). |
| Quotas       | No GPU is needed. 64-core sizes had no capacity in the regions Hackyard tried; a 32-core size worked.                                                                                                          |

---

## 6. Gotchas we hit (don't repeat)

- **YouTube** blocks cloud IPs ("confirm you're not a bot"), so download on your workstation. python.org Python needs
  `certifi` for TLS.
- **The code formatter** rewrites `{{TWEENS}}` inside `<script>` into JS blocks. Use the `/*TWEENS*/` comment placeholder.
- **Only one root HTML per project:** keep templates outside the project root (`engine/`).
- **CDN timeouts on the VM** break renders, so vendor GSAP into `assets/lib/`.
- **Audio clip slots** must not exceed the media length, and overlapping voice clips alternate between two tracks.
- **Blur filters on 130+ caption spans** trip the heavy-overlay warning: fade on opacity only.
- **Reused footage** can carry burned-in text from its old film. Re-render clean.
- **A `div` that scales a group** needs a real box (`inset: 0`) or it scales from the top edge.
- **Split-flap/label text** from formatted HTML needs `.trim()`, or the leading spaces become letters.
- **A tool call that shows as "rejected" may still have run.** Check the Azure activity log after any destructive command.
- **Loudness:** renders come out around −18 to −21 LUFS, so always run loudnorm to −15 for social.
- **Low-resolution archive:** one 1994 Jobs source was 854×470. Grade and grain hide it, but look for a better master.

---

## 7. Time and cost for one reel

- **Sourcing agents:** ≈ 20 min in parallel. **Build and fixes:** ≈ 30 min. **Render:** ≈ 6 min, plus 1 min for clean
  3D inserts.
- **Azure:** Speech and gpt-image-2 cost cents; the render VM costs about $0.89/h while it runs. **Music:** HeyGen
  catalog, free. **Stock:** Pexels, free.
