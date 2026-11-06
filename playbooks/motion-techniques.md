# Motion techniques: After Effects moves in HTML

Research notes (1 Nov 2026) on what After Effects editors do to make cuts feel cinematic, and how to get each effect in
our HTML → HyperFrames → VM render stack without opening AE. Read this with `production.md` (the how) and
`editorial-reel.md` (the style).

**Taste verdict (2 Nov 2026):** the producer preferred v1 over v2 ("i like the v1 mostly"). Everything below works
technically, but using all of it in one film is too much. Keep v1's clean editorial cuts as the default and add these
effects only where a moment earns one. The documentary series uses almost none of them.

Status (1 Nov 2026): **proven in the v2 world reel** (a 16:9 render). The tested items are:

- Whip pans: SVG `feGaussianBlur stdDeviation "X 0"` on an untimed wrapper.
- Zoom-through.
- Focus-pull opener.
- Blur cuts.
- Title slams with camera shake. Overscale `#cam` to 1.035 while it shakes, or the frame edge shows.
- Footage-filled type: multiply blend, and lift the shot to `brightness(2.3)` underneath it.
- Speed ramps: pre-rendered with ffmpeg (a small helper script; not included in this repo). Quote the `setpts`
  expression, because its commas break the filter graph.
- Depth parallax: a helper script run in a `python:3.12-slim` container on the VM (not included; see §4).
- One sound effect per transition.

Key rules:

- The runtime owns timed clips, so put every `<video>` inside an untimed `.wv` wrapper and animate only the wrapper.
- Reset each wrapper's `filter`/`x`/`scale` with `tl.set` right after its transition.
- Give `#cam` a `z-index: 0`.

Not yet tried: `@hyperframes/shader-transitions` and the catalog `motion-blur` block.

---

## 1. The big finding: most of AE is already in HyperFrames

HyperFrames ships about 450 catalog blocks, installed as editable source with `npx hyperframes add <name> --json`
(prints files + mount snippet). Search with `npx hyperframes catalog --query "<what the beat should do>" --json`. The
ones that map to AE moves:

| AE thing                                               | HyperFrames block                                               | Notes                                                                                                                                                                                                                      |
| ------------------------------------------------------ | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Layer Motion Blur switch (shutter angle/phase/samples) | `motion-blur`                                                   | Real temporal supersampling: seeks the GSAP timeline at sub-frame times and averages copies with `plus-lighter`. Add `data-hf-motion-blur` to any animated element. Works on transforms only, not on video content motion. |
| Whip pan with speed ramp                               | `whip-pan-cut` (CSS) / `whip-pan` (shader)                      | Both scenes ride one strip on a single `power3.inOut` tween so seam velocity matches; directional blur capped at 16px, peaking mid-whip.                                                                                   |
| Wiggle-expression camera shake                         | `camera-shake`                                                  | Nine measured profiles (handheld mild/strong/extreme, wide, tele, rig buzz/wobble). Seek-safe, so it renders deterministically.                                                                                            |
| Light leak / film burn                                 | `organic-light-leak-overlay`, `light-leak`, `transitions-light` | Screen-blended blurred radial gradients, oversized so edges never show.                                                                                                                                                    |
| Zoom transition / zoom blur                            | `zoom-through-transition`, `cinematic-zoom`                     | Cinematic zoom = radial zoom blur + chromatic fringing.                                                                                                                                                                    |
| Flash frame                                            | `flash-through-white`                                           | Use for hits, max 1–2 per film.                                                                                                                                                                                            |
| Glitch / RGB split                                     | `glitch`, `rgb-glitch-text`, `caption-glitch-rgb`               | Off-brand for the house style except as a single "interruption".                                                                                                                                                           |
| 2.5D parallax                                          | `parallax-zoom`, `parallax-unzoom`, `camera-rig-depth-stack`    | Layer-based; for single photos see §4.                                                                                                                                                                                     |
| Rack focus                                             | `focus-blur-resolve`, `soft-blur-in`                            |                                                                                                                                                                                                                            |
| Grain                                                  | `grain-overlay`, `grain-field`                                  | We already grade with `data-color-grading`; use one, not both.                                                                                                                                                             |
| Beat sync                                              | `npx hyperframes beats --json`                                  | Gives beat times from the music; cut on them.                                                                                                                                                                              |

The `@hyperframes/shader-transitions` package adds GPU transitions driven from our GSAP timeline: `domain-warp`,
`ridged-burn`, `whip-pan`, `sdf-iris`, `ripple-waves`, `gravitational-lens`, `cinematic-zoom`, `chromatic-split`,
`glitch`, `swirl-vortex`, `thermal-distortion`, `flash-through-white`, `cross-warp-morph`, `light-leak`.

```js
init({
  bgColor: "#07080b",
  scenes: ["s1", "s2", "s3"],
  transitions: [
    { time: 9.0, shader: "whip-pan", duration: 0.35 },
    { time: 29.5, shader: "cinematic-zoom", duration: 0.5 },
  ],
  timeline: tl,
});
```

Shader caveats (from the HyperFrames transition guide):

- Scenes must be `.scene` divs with an explicit `background-color` equal to `bgColor`.
- No `var()`, no `transparent` in gradients, no gradients on elements under 4px inside captured scenes.
- Don't mix CSS and shader transitions in one composition.
- **Unknown for us:** whether scene capture picks up `<video>` frames. Our reels are almost all video, so test one shader
  transition between two video scenes on the VM before planning around it. If it fails, use the CSS blocks or the ffmpeg
  route in §5.

## 2. Transition grammar (what each cut _means_)

From the HyperFrames transition guide and the editing references (Adobe, StudioBinder):

- **Hard cut** = "wake up". It is still the default between related shots.
- **Crossfade** = "this continues". **Slow dissolve** = "drift with me".
- **Whip pan** = energy and change of place. **Match cut** = "these two things are the same idea".
- **Pick one primary transition** for 60–70% of the scene changes, plus one or two accents. Never use a different effect
  on every cut.
- **Placement:** the opening cut gets the most distinctive transition (0.4–0.6 s). Related points get the primary
  (~0.3 s). A topic change gets something different. The climax gets the boldest accent. The outro gets the slowest and
  simplest (dip to black, 0.6–1.0 s).
- **Premium energy** (the house style): focus pull, blur crossfade, dip to black, and in shader form cross-warp morph or
  thermal distortion. Use `power1`/`sine.inOut` eases at 0.5–0.8 s. Avoid grids, tiles and repeating geometric patterns:
  they read cheap.

For the editorial reel:

- **Primary:** hard cut with a 2-frame directional blur on fast montage beats.
- **Accent 1:** whip pan on place changes ("hostels → small towns → side projects").
- **Accent 2:** cinematic zoom-through into the brand world at the Turn (29.5 s), the one big move.
- **Outro:** dip to black into the logo card.

## 3. Motion craft that separates AE work from "web animation"

These come from Derek Lieu's motion-graphics list, Adobe's graph-editor docs and HyperFrames' motion principles.

1. **Graph-editor easing.** AE editors drag one bezier handle all the way over, so the move is "super fast then slow". In
   GSAP that is `expo.out`, `power4.out` or a `CustomEase`. Rules:
   - Entrances use `.out`, exits use `.in`, moves between positions use `.inOut`.
   - Don't give more than two tweens in a scene the same ease.
   - Make the slowest move about 3× the fastest.
2. **Motion blur on anything that moves fast** (`motion-blur` block). This is the biggest single "it looks like AE"
   switch.
3. **Speed ramps.** Footage goes fast into the cut, then decelerates into the catch. HyperFrames can't change a `<video>`
   element's playback rate per frame, so pre-render ramped clips with ffmpeg (`setpts` with a curve, or `minterpolate`
   for smooth slow-mo) on the VM, then drop them in.
4. **Title slams in Z, not scale.** Animate a 3D-transformed title's `translateZ` (with `perspective` on the parent) from
   past the camera to rest. Add a 4–6 frame `camera-shake` on impact and a hit SFX.
5. **Camera on everything.** Stills and cards need a slow push, a drift or a slight roll. Vary it per scene (push, then
   pan, then stillness), because the same Ken Burns everywhere looks templated.
6. **Add "flaws".** Use gradients instead of flat fills, a vignette, a paper or texture matte on type, a subtle S-curve
   contrast, grain, and occasional gate weave. Clean = looks like a computer made it.
7. **Track mattes.** These are text filled with footage, and shapes or ink-bleed wipes revealing the next shot. CSS
   `mask-image`/`background-clip: text` with a `<video>` behind gives text-as-window, which works well for "Find your
   people."
8. **Glow done the AE way.** Duplicate the element, blur the copy, set it to `mix-blend-mode: screen` (AE "Add"), and
   lower its opacity.
9. **Light sweep** across the monogram on the end card: a narrow white gradient bar masked to the mark, moving once.
10. **Build / breathe / resolve.**
    - In each scene, elements enter in the first 30%.
    - One ambient motion carries the middle.
    - The exit is decisive.
    - Total stagger stays under 500 ms.

## 4. 2.5D parallax from a single photo

This is the documentary look (Vox, Johnny Harris): a flat archival photo where the person stands in front of the
background and the camera slowly moves. Hackyard used it on archive stills of Jobs, Wozniak and the garage.

1. Generate a depth map with **Depth Anything V2/3** (Hugging Face spaces, or the model on the VM). Output: greyscale,
   white = near, same aspect ratio as the photo, saved as PNG (not JPEG: its artefacts ripple). Half resolution is
   enough.
2. Render the move with one of:
   - **DepthFlow** (Python, `pip install depthflow`): a ray-marched GLSL parallax renderer that pipes to ffmpeg. It runs
     headless on the render VM and outputs an MP4 clip you drop into the reel like any other footage. It is AGPL; we
     only use it as a tool, and the rendered videos are ours. Check the licence terms for your own use.
   - **In-page Three.js:** a plane with the photo, displaced in the fragment shader by `depth × camera offset` and driven
     by the GSAP clock (the same pattern as the 3D brand film's `world.js`). Scale up about 6% so the edges never
     reveal.
3. Keep the move small: about 2–4% lateral, slow push in, 3–5 s. Big moves tear at the depth edges.

Parallax moves pixels, not facts: never use it to fake a scene or combine people who weren't photographed together.

## 5. Fallback route: transitions in ffmpeg

If shader transitions can't capture video in-page, cut the reel as separate clips and join them on the VM:

- `ffmpeg … -filter_complex "[0][1]xfade=transition=hblur:duration=0.3:offset=8.7"`
- Built-in `xfade` transitions worth using: `hblur`, `zoomin`, `fadeblack`, `fadewhite`, `smoothleft`/`smoothright`,
  `circleopen`, `radial`, `distance`.
- For anything else, the **gl-transitions** collection (GLSL, MIT) is the reference: `gl-transition-scripts` renders them
  from the command line.

## 6. Sound is half the transition

- **Every visual transition gets a matching sound.** Whip = whoosh, zoom-through = riser into a hit, flash = impact, dip
  to black = reverse swell. Silent transitions feel fake. Pull SFX from the HeyGen catalog (the `media-use` skill), as in
  the world reel.
- **J-cuts and L-cuts.**
  - J-cut: the next scene's audio starts under the current picture. For example, the Jobs 2003 voice can start 0.3 s
    before his face appears.
  - L-cut: the previous audio carries over the new picture.
  - Both are just offsetting the audio clip's `data-start` against the video clip.
- **Cut on the beat.** Run `npx hyperframes beats --json` on the music, then snap montage cuts and title slams to beats.
  Spoken-word beats stay on Azure word timings.
- **Duck the music under the voice,** and let it swell in the gaps.

## 7. Worked example: upgrade map for the world reel (v2)

Applying the above to the editorial world reel (timings from its `SCRIPT.md`):

| Beat               | Now                          | v2                                                                                                                          |
| ------------------ | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| 1 Belief 0–6.5     | Jobs clip, grade             | 2.5D parallax on the _Creation of Adam_ opener; motion-blurred title slam on "smarter" with micro shake + hit               |
| 2 Claim 6.5–9      | fast b-roll cuts             | speed-ramped clips (ffmpeg), cuts snapped to beats, 2-frame directional blur on each cut                                    |
| 3 Proof 9–17       | Jobs panel → card → Woz 2-up | parallax on the Jobs/Woz stills; **match cut** Jobs face → Woz face, same eye line; slide the Woz panel in with motion blur |
| 4 Mechanism 17–23  | Jobs 2003                    | J-cut his voice 0.3 s early; team inserts on beats                                                                          |
| 5 Obstacle 23–29.5 | black card + 3 shots         | **whip pan** chain hostel → small town → laptop, whoosh on each                                                             |
| 6 Turn 29.5–35     | 3D yard                      | the one big move: **zoom-through** (cinematic zoom + riser + hit) from the laptop screen into the yard                      |
| 7 Roles 35–46      | b-roll + sketch collage      | collage pieces fly in on Z with motion blur; light sweep on "Show your work"                                                |
| 8 Reframe 46–56    | 3-speed montage              | beat-synced montage with ramps; "Find your people" as footage-filled text (track matte)                                     |
| 9 Brand 56–60      | H card                       | dip to black, then light sweep across the H monogram                                                                        |

Order of work, cheapest win first:

1. Motion blur + easing pass.
2. SFX on every transition.
3. Whip pans.
4. Zoom-through at the Turn.
5. Speed ramps.
6. 2.5D parallax.
7. Shader transitions, only if the video-capture test passes.

## Sources

- HyperFrames shader transitions: https://hyperframes.heygen.com/packages/shader-transitions
- HyperFrames catalog (motion-blur, whip-pan-cut, camera-shake, light-leak blocks):
  https://hyperframes.heygen.com/catalog/components/motion-blur.md and siblings
- HyperFrames transition guide and motion principles (shipped with the HyperFrames agent skill: `references/transitions.md`,
  `transitions/*.md`, `motion-principles.md`)
- GL Transitions (open GLSL transition collection): https://gl-transitions.com/
- Derek Lieu, "25 Simple Tricks for Better Motion Graphics":
  https://www.derek-lieu.com/blog/2014/04/26/25-simple-tricks-for-better-motion-graphics
- Adobe, After Effects speed graph / easy ease:
  https://helpx.adobe.com/after-effects/desktop/animate-in-after-effects/speed-between-keyframes/speed.html
- Adobe, video transition types + J/L cuts: https://www.adobe.com/creativecloud/video/post-production/transitions.html
- Codrops, animating WebGL shaders with GSAP (Kawase blur, reveals):
  https://tympanus.net/codrops/2025/10/08/how-to-animate-webgl-shaders-with-gsap-ripples-reveals-and-dynamic-blur-effects/
- 2.5D parallax from depth maps: https://www.sygnal.com/kb/image-25d-parallax-effects
- DepthFlow: https://github.com/BrokenSource/DepthFlow
