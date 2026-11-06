# Artifact reel playbook (format C): real founders + real artifacts, no stock, no 3D

Approved 2 Nov 2026. Producer feedback: "I like the reel you made right now". It replaced a stock-b-roll reel the
producer rejected ("we shouldn't use the stock videos in the short") and a 3D world that didn't land.

- **Reference reel:** Hackyard's "5 signs a co-founder actually ships" (1080×1920, ~62 s).
- **Shared code:** `engine/build_lib.py`, `engine/template.html`, `tools/sources/capture_artifacts.mjs`,
  `tools/voice/azure_tts.py`, `tools/voice/azure_stt.py`, `tools/edit/clip_words.sh`.
- **The machinery** (Azure voice, render VM, keys, music, yt-dlp): `production.md`. This file is the recipe for this
  format.

---

## 1. The idea in one line

Every second shows something **real and specific**:

- a founder saying it in their own clip;
- archive footage of the moment;
- or the actual document, page, slide or object behind the claim, with a blue marker sweeping the exact sentence as
  the narrator says it.

The product (here, the Hackyard app) closes it, in a phone frame.

Why it works:

- **Originality.** Instagram's April 2026 originality rules rank original visuals above reposted or stock material, and
  stock slideshows are now the weakest faceless format.
- **Specificity holds attention.** The viewer reads a real 1973 job application, not "a person at a laptop".
- **The marker gives the eye a target** on every line.
- **It is honest.** Every claim is shown with its source on screen.

## 2. Structure (60 s, 9:16)

| Beat                | Time    | What's on screen                                                                                                                                                                                                                                                   |
| ------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Hook                | 0–2.5 s | **Frame 1 already has text and a real artifact**: an instant (no fade) title "Before you pick / a co-founder" over Jobs' 1973 job application. Narrator: "A co-founder's CV won't tell you if they ship." Marker on "Phone: none", then "Past Employment" (blank). |
| Promise / open loop | 2.5–5 s | "These five signals will." over a **teaser of the five artifacts ahead**, 0.5 s each, one soft tick per cut; title "5 signs a co-founder _actually ships_". Never a black screen here: producer review flagged the empty version.                                  |
| 5 signals × ~9 s    | 5–50 s  | Each: tick + title in the upper third + "n/5" counter top right. A founder quote in a **16:9 band** (never cover-cropped), then 1–2 narrator lines on **artifact cards** or archive bands.                                                                         |
| Close               | 50–56 s | The product app in a **phone frame**: a screen recording of the feed, then a screenshot ("Shipped this week"), then a builder's profile with **Connect** under "Find yours by _building_."                                                                         |
| Save trigger        | 56–59 s | "Before you commit" checklist of the five signals (rows stagger in). People screenshot and save it.                                                                                                                                                                |
| End card            | 59–61 s | H monogram + "Hackyard", "Find your people. **hackyard.org**". House rule: the CTA uses the landing page, never the logged-in app URL.                                                                                                                             |

Pacing: a visual change every 1.5–3 s; nothing static beyond ~4 s (artifact cards always have a slow camera move;
founder bands push in slowly).

## 2b. Length (decide before writing the script)

Default to **30–45 s; never past 60 s**. Pick the length first and write to it (≈2.5 spoken words per second: 15 s ≈
35–40 words, 30 s ≈ 75, 60 s ≈ 150); each artifact beat needs 2–3 s for the marker to land.

| Reel                                        | Length  | Notes                                                                                           |
| ------------------------------------------- | ------- | ----------------------------------------------------------------------------------------------- |
| One idea, one artifact                      | 15–25 s | Best Instagram completion (7–15 s reels reported at 60–80%); top faceless reels averaged 8–11 s |
| Short list (3 points)                       | 30–40 s | Hook + ~8 s per point + end card; the default for most posts                                    |
| Full list (5 points, like the signals reel) | 45–60 s | Upper limit; YouTube Shorts holds 73–76% completion at 50–60 s                                  |

Instagram Reels favours ≤30 s (completion and rewatches drive reach); YouTube Shorts is fine at 45–60 s. Longer belongs
in a YouTube video. Sources: Virvid Shorts retention breakdown (2026), OpusClip Reels length guide, Vireuoess "top 50
faceless Reels" (2026).

## 3. Visual system (9:16 frame, 1080×1920)

| Element                                    | Where                                                                             | Look                                                                                                                                                               |
| ------------------------------------------ | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Signal title (`key(..., "T")`)             | upper third (~y 420–500)                                                          | Space Grotesk 80 px, held for the whole signal, highlights with `*word*`                                                                                           |
| Counter                                    | top right                                                                         | "1/5" pill                                                                                                                                                         |
| Artifact card (`CARD = 60, 600, 960×740`)  | middle                                                                            | page on `#f4f1ea`, radius 6, deep shadow; camera move on the inner image; label above: blue bar + uppercase source ("LINUS TORVALDS · COMP.OS.MINIX, 25 AUG 1991") |
| Marker (`.mk`)                             | on the sentence                                                                   | `rgba(111,181,252,.55)` + `mix-blend-mode: multiply`, wipes left→right in 0.4 s **on the word that names it**                                                      |
| Founder / archive band                     | top 656, height 608                                                               | full-width 16:9, slow push-in, name tag under it                                                                                                                   |
| Phone frame (`PHONE = 220, 300, 640×1150`) | centre, taller                                                                    | radius 34, for app screens/recordings at about native size (no upscale smear)                                                                                      |
| Captions                                   | under the picture (`low=True`, `.cap.low`) or lower for the phone (`low="lower"`) | word-by-word kinetic, 1–3 words, serif (EB Garamond) with one big Space Grotesk emphasis word per line                                                             |
| Background                                 | everywhere                                                                        | the dark brand ground (`#07080b` in the reference reel; the house surface is `#090c13`)                                                                            |

Brand colours only (this is Hackyard's house style; swap in your own). No grade on artifacts (white pages stay crisp);
founder clips keep the editorial grade.

## 4. Sourcing real artifacts

Ask "what is the primary source behind this line?" The examples that worked:

| Line                        | Artifact                                                           | Where it came from                                               |
| --------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------- |
| CVs don't show shipping     | Steve Jobs' 1973 job application                                   | Goldin auction listing photo (`@2x` image), contrast-boosted     |
| A live link                 | AirBed&Breakfast homepage, Aug 2008                                | Wayback Machine                                                  |
| A repo                      | github.com/torvalds/linux                                          | live capture                                                     |
| A demo                      | Macintosh 1984 "hello"                                             | archive footage band                                             |
| Not a deck                  | AirBed&Breakfast 2008 deck, cover                                  | public deck reproduction                                         |
| Small, boring thing         | Linus Torvalds' 1991 "just a hobby" post                           | cs.cmu.edu history page                                          |
| Even ten users              | Airbnb deck "User Testimonials" slide                              | same deck                                                        |
| Drop features, not the date | Folklore.org "Real Artists Ship" (2007 capture), deadline sentence | Wayback Machine                                                  |
| Who it's for                | Bezos 1997 letter, "Obsess Over Customers"                         | SEC filing via Wayback (sec.gov itself blocks headless browsers) |
| Not which framework         | Amazon.com, Aug 1999                                               | Wayback Machine                                                  |
| Build together              | The Traf-O-Data computer                                           | Wikimedia Commons                                                |
| The product close           | the app's feed, home, a builder's profile                          | the team's own phone screenshots + screen recording              |

Record every source (URL, capture date, licence, credit line) in `media/artifacts/SOURCES.md`. Do the same each time.

**Finding archive pages.** Ask the Wayback CDX API for real capture timestamps (light enough for your workstation):

```bash
curl -s "https://web.archive.org/cdx/search/cdx?url=airbedandbreakfast.com&from=2008&to=2009&output=json&fl=timestamp,statuscode,length&filter=statuscode:200&collapse=timestamp:6"
```

Use the `if_` URL form (`/web/<timestamp>if_/<url>`) so the Wayback toolbar isn't in the shot. Prefer captures with a
larger `length`: early ones often have broken images (the Oct 2007 Airbnb page did).

**Capturing pages + finding the highlight.** Use `tools/sources/capture_artifacts.mjs`. It runs on the render VM inside
`hyperframes-runner` with the Puppeteer that ships with HyperFrames (loaded via `createRequire`). It:

- loads each page;
- scrolls the `anchor` sentence to ~18% down;
- screenshots at 2× (or a phone viewport at 3× with `mobile: true`);
- writes `rects.json`: the pixel boxes of each `marks` phrase.

Whitespace in phrases matches line breaks, so `<pre>` text works.

```bash
scp tools/sources/capture_artifacts.mjs artifacts.json "$SOURCE_CUT_RENDER_HOST":work/
ssh "$SOURCE_CUT_RENDER_HOST" 'cd ~/work && docker run --rm -v "$PWD":/w -w /w hyperframes-runner node capture_artifacts.mjs artifacts.json art'
```

If a page won't scroll (some archived pages), capture a tall viewport (for example 900×3200 CSS) and crop locally with
`ffmpeg -vf crop=W:H:0:Y`. Shift the rect `y` values by the same `Y`.

**Scans and photos.** Look at auction listings, museum pages and Wikimedia Commons for the original object. Faint scans
come up well with `eq=contrast=1.9:brightness=-0.12:saturation=0.6,unsharp=5:5:1.0` plus a crop to the paper.
Hand-place the marker rects after viewing the image.

**Your own product screens.** Use real phone screenshots and a 10–30 s screen recording from the team.

- Trim the best 3 s of scrolling, avoiding frames where an email-like handle shows. Crop off the status bar:
  `crop=576:1250:0:46,fps=30`.
- Show them in the phone frame at about native size.
- Real users' names appear, so get their consent; blur or crop around anything sensitive.

## 5. Building it (code)

Start from a finished reel's `build.py`. The pieces from `engine/build_lib.py`:

```python
E = Edit(ROOT, 1080, 1920, bright=set(), recon=set()); E.drift = True
band("apple1-4-system.mp4")                                   # archive/founder footage in the 16:9 band
art("a-linux-1991-cmu.png", "Linus Torvalds · comp.os.minix, 25 Aug 1991",
    [(0.19, 1.0), (0.21, 1.24)],                              # camera: (image y-fraction at card centre, zoom) start → end
    cx=0.32,                                                  # aim left so zoomed lines aren't cut off
    marks=[([626, 510, 470, 30], 3), ([16, 540, 360, 30], 4)])  # rect in image px, word index it lands on
art("app/app-home.jpg", "the Hackyard app", [(0.5, 1.0), (0.5, 1.04)], phone=True)
{"phone_video": A + "app/app-feed-scroll.mp4", "label": "Hackyard · shipped this week"}
E.vo("r2a", [art(...)], gap=0.15, low=True, caps="auto:boring")   # narrator line; captions under the picture
E.quote("hoffman-embarrassed", "Reid Hoffman", "auto:embarrassed")  # founder clip in the band, every word captioned
E.key("Before you pick|a *co-founder*", 0.0, t, "T", instant=True)  # frame-1 hook ("|" = line break)
E.checklist("Before you commit", [...5 rows...], 2.6)
E.endcard(2.2, "Find your people. hackyard.org")
```

**Hook placement (producer feedback, 3 Nov 2026):** the hook sits above the picture card on a dark plate, never over a
face. Use style `"O"` with `.vert .st-O { padding: 0 60px 1120px }` plus
`.vert .st-O .kl { background: rgba(7, 8, 11, 0.9) }`, as in `engine/template.html`.

Lessons from getting the camera and marks right:

- Zooming at `cx=0.5` cuts off the start of highlighted lines. Use `cx≈0.25–0.35` for left-aligned text.
- Keep zoom ≤ 1.3 so text stays sharp.
- Put the marker on the word the narrator uses to name the thing. The marker is the "look here".
- Voice, word timings, music and founder-clip sourcing are exactly as in `production.md` (Azure Andrew HD, Azure fast
  transcription, HeyGen music, yt-dlp on your workstation).

## 6. Review → render (always in this order)

1. `python3 build.py` → check clip count and duration.
2. Snapshot every artifact shot on the VM and look at the contact sheets: `tools/render/vm.sh <proj> snapshot --at t1,t2,...`.
   Check that marks land fully, labels are readable, and nothing is cut off.
3. **Show the producer the live edit before rendering:**
   - Run the HyperFrames Studio preview on the VM:
     `docker run -d --name hf-preview-reel --network host -v <proj>:/work hyperframes-runner hyperframes preview --port 3003 --no-open --foreground`.
   - Forward the port to your workstation, for example `ssh -N -L 3003:localhost:3003 "$SOURCE_CUT_RENDER_HOST"` in a
     reconnect loop. Open http://localhost:3003.
   - Wait for a yes.
4. Render: `tools/render/vm.sh <proj> render --quality delivery --output renders/<name>.mp4` (a 60 s reel takes ~10 min
   with the VM to itself). Pull it, then normalise (`tools/render/loudness.sh`, or the one-pass form):
   ```bash
   ffmpeg -i in.mp4 -c:v copy -af loudnorm=I=-15:TP=-1.5:LRA=11 -c:a aac -b:a 192k -ar 48000 -movflags +faststart out.mp4
   ```
   Check with `ebur128` (target about −16 to −15 LUFS, peak ≤ −1 dB), a 16-frame contact sheet of the real file, and
   `volumedetect` on each founder quote (speech must be there).

## 7. Gotchas met making this one

- **Sync blocked by a root-owned cache.** The preview server writes root-owned `.thumbnails/` into the project, so the
  rsync in `vm.sh` fails. `vm.sh` excludes `.thumbnails/`; if a sync still errors, `chown -R 1000:1000` the project
  through the runner container.
- **Studio crash.** HyperFrames Studio showed "Minified React error #185" after the project changed under it. Restart the
  preview container and clear the page's localStorage.
- **sec.gov blocks headless Chrome.** Use the Wayback copy of the filing.
- **Google Groups is a JS app.** It opened a later reply, not the post; use a static mirror of the text.
- **YouTube blocks cloud VMs ("sign in to confirm you're not a bot").** Run yt-dlp on your workstation in a scratch venv
  with `certifi` (`SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())")`).
- **Sora was unusable.** Our Azure `sora-2` deployment returned "Bad request for dependent service" for every request
  shape (2 Nov 2026). Test it before you plan on it.
- **Media files can be overwritten.** A founder clip was once found replaced by a silent copy of another shot. Before a
  render, `ffprobe` every `<audio>` source for an audio stream; HyperFrames fails with `ASSET_MEDIA_TYPE_MISMATCH` if one
  has none.
- **Credentials.** This format needs no stock key. Azure keys stay server-side and are piped over stdin, never written to
  disk (`production.md` §2).
