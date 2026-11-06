# Editorial reel playbook

How to make reels in the style of the reference reel "The hard part was never the idea" (Instagram, by Narrative Media,
60 s): real people, found footage and images, every spoken word on screen, and the brand at the end.

Built from Azure Speech fast transcription (word timings), ffmpeg scene detection (82 cuts), and a frame-by-frame
breakdown of 120 frames by an Azure OpenAI vision model, checked against our own review. The method is in
`production.md` §3, step 1.

The typography and colours below are the house style used by Hackyard; swap in your own brand.

---

## 1. The formula in one line

A spoken argument (interview audio + narrator) carried by **every word on screen**, over **dark, graded real footage**
that cuts on meaning, with a short **bright brand world** in the middle and a **silent logo card** at the end.

## 2. Story structure (60 s)

| Time      | Beat                     | What it does                                                      | Original example                                                   |
| --------- | ------------------------ | ----------------------------------------------------------------- | ------------------------------------------------------------------ |
| 0–7 s     | Challenge a belief       | Abstract imagery that "forms"                                     | "Ideas don't come out fully formed… you just have to get started." |
| 7–16 s    | Proof with a real story  | Two people + the missing third person → outcome                   | Brian and Joe had the idea and the design… Nathan joined… Airbnb   |
| 16–28 s   | The human mechanism      | One interview anchor + scenes that act out each phrase            | Whiteboard, smart people, objections, solutions, back and forth    |
| 28–32 s   | The obstacle             | Cut to black, words alone                                         | "…the right ones are always somewhere else."                       |
| 32–36.5 s | Brand turn               | Bright, open brand world, 3 icons                                 | "That's what Hackyard is for."                                     |
| 36.5–47 s | Make it human            | Roles on screen: engineer, designer, the one who gets the problem | "Bring an idea, a skill…"                                          |
| 47–56 s   | Reframe + three commands | Fast achievement montage, then people at work                     | "Don't build alone. Find your people. Build something real."       |
| 56–60 s   | Brand memory             | Black, small logo, nothing else                                   | H Hackyard                                                         |

The proof comes ~16 s **before** the brand. The brand answers a problem the viewer has already watched.

## 3. Editing grammar

- **Meaning drives the big cuts.** "Engineer" gets its own black card; "Nathan" fills the empty middle panel;
  "whiteboard" shows a whiteboard; "objections" shows an argument.
- **Type carries the fine timing; picture holds longer.** A shot holds 1–2 s while 4–6 words replace each other on top.
- **Two caption modes alternate:** _replacement_ (one word swaps for the next) and _accumulation_ (a line builds: "What
  they didn't have", "Don't build alone.").
- **Shot lengths:** ~0.7–1.2 s in the hook and proof; ~1.7 s in the mechanism; 1–2 s for people/roles; the brand world is
  one ~4.4 s scene made of animated reframes.
- **The climax (47–56 s) has three speeds**, not one ramp: 2–6-frame achievement cuts → slow down to people working
  (~1 s) → 4-frame launch burst → a 1 s breath on "Find your people." → 2-frame racing burst → one triumph image with the
  huge final word → black.
- **Keep the CTA text locked** above the fastest montage so the sentence stays readable while pictures fly.
- **End with restraint:** the logo resolves in 0.3–0.5 s and holds ~4 s on black. No extra copy.

## 4. Typography system

The original uses an editorial serif for narration and a clean sans for emphasis. Hackyard's version:

| Role                | Spec (1080×1920 / 1920×1080)                                                                                                                             | Behaviour                                                                                                            |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Narration word      | Editorial serif (**EB Garamond**, bundled in HyperFrames; get brand-owner sign-off as a second brand voice), 44–56 px landscape / 56–64 px vertical, ink | Centre of frame, one word or short phrase; land on the spoken word; hold function words 4–10 frames, key words 10–22 |
| Accumulating line   | Same serif; words spaced across 45–70% of width                                                                                                          | Build word by word; replace the whole line at the next phrase                                                        |
| Emphasis word       | **Space Grotesk 600**, 110–150 px, ink, tracking −0.05em                                                                                                 | Nouns and commands: names, roles, "started", "engineer", "your friends."                                             |
| Hero word           | Space Grotesk 600, 190–260 px (fit to width)                                                                                                             | One per section; may sit behind the subject (matte)                                                                  |
| Italic accent       | Serif italic, 65–110 px, stacked beside a speaker                                                                                                        | "There's really / nothing / more fun"                                                                                |
| Selection highlight | Brand blue box behind the word, dark text                                                                                                                | Reveals letter by letter like selected text ("idea", "engineer")                                                     |
| Halo                | Duplicate text blurred 8–18 px at 15–35%                                                                                                                 | Soft, never a neon glow (film type only, never UI)                                                                   |
| End card            | The real monogram + the wordmark in Space Grotesk 500, ~23% of frame width                                                                               | Centred on the dark brand ground, 4 s hold                                                                           |

Hackyard's palette: surface `#090c13`, ink `#e7f0fb`, blue `#2b5ce4`, light blue `#9cbdff`. (The first editorial reels
used an older ground `#07080b`, ink `#f1f4f7` and a lighter primary `#6fb5fc` with text `#070d18` on the highlight box.)

## 5. Graphic interruptions (use at phrase pivots, not everywhere)

1. **Negative patch:** a rectangle (250–470 × 100–250 px at 720p) showing the footage inverted, 1–3 frames.
2. **Selection highlight:** a blue box tracking a word as it types in.
3. **Bold flash:** the word appears 1–2 frames heavier/brighter, then settles to serif.
4. **Slice displacement:** 2–4 horizontal bands offset for 2–6 frames.
5. **Full-frame invert:** 1 frame on a hard turn ("to the").
6. **Split panels:** 2-up and 3-up vertical panels for people who belong together.

## 6. Look

- Grade every source first: −0.5 to −1 stop on bright footage, −15–30% saturation, olive/teal shadows with natural skin,
  soft rolled highlights, vignette 0.3–0.7 stop.
- Black-and-white archive stays black-and-white; unify it by exposure, softness and the type.
- Colour is a reward: flowers, the brand world and the climax (fire, sport) are the only saturated moments.
- Fine grain over everything (HyperFrames `media-treatment`, never CSS filters on footage).
- The principle: **subdued picture, luminous words, occasional bursts of colour.**

## 7. Sound

- Real interview audio where the story is someone's own words; a narrator (Azure `en-US-Andrew` HD) for the brand's
  lines.
- Restrained music under speech, a reset at the black cards (28–32 s), a lift at the brand world, one clear build into the
  47 s montage, a held tail under the logo.
- Ticks/impacts only on major type reveals and cuts in the bursts, never one per word.

## 8. Sourcing real people, footage and images

| Need                                                           | Source                                                                               | Notes                                                                                                                                         |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Your own community                                             | Your own event photos and video, founder sessions, members, team                     | Best: real builders from your community as the proof story. Get consent from everyone shown.                                                  |
| Founder proof stories (Airbnb-type)                            | Licensed interview clips, or the founders' own public talks used per your legal call | The original uses famous founders and film clips. Clearing rights is the publisher's decision; credit every clip and never imply endorsement. |
| B-roll (hands typing, whiteboards, workshops, launches, sport) | Free stock: Pexels / Pixabay video (free licence)                                    | Avoid copyrighted film scenes and sponsor logos unless licensed. Format C and the series use no stock.                                        |
| Textures, sketches, blueprints, "creation" hands               | Azure OpenAI `gpt-image-2` (≤10 images/min)                                          | Textures only, never people. Generate in the brand palette; animate with slow push and grain.                                                 |
| Brand world beat                                               | Your own brand world (Hackyard used its 3D yard) or real product screens             | Don't borrow another product's imagery (the original's Windows-XP-style hills are not ours to use).                                           |

## 9. Production pipeline (what we run)

1. **Script** the 8 beats (§2); write every on-screen word.
2. **Voice:** narrator lines via Azure Speech (`tools/voice/azure_tts.py`); interview clips cut from licensed sources.
3. **Word timings:** Azure Speech fast transcription of the final audio (`tools/voice/azure_stt.py`,
   `tools/edit/clip_words.sh`) → every caption keyed to its word.
4. **Footage pull + grade:** download, trim, `npx hyperframes media-treatment` for the look; split-panel layouts as HTML.
5. **Compose in HyperFrames:** footage track, caption system (serif/sans/hero/highlight presets), interruption
   components, brand-world scene, end card. Check the registry first for named effects (`npx hyperframes catalog`).
6. **Review:** `snapshot --review` on the render VM; check every hero frame and the 47–56 s bursts frame by frame.
7. **Render** both 16:9 and 9:16 on the render VM (`tools/render/vm.sh <project> render`).

## 10. Do / don't

- Do: one idea per beat, every word on screen, a real story as proof, a bright brand moment, a silent logo end.
- Don't: bottom subtitles, a sound on every word, glow that washes the frame, extra CTA copy on the end card, compare
  your brand to other products, or use colours outside the brand palette for type and UI.
