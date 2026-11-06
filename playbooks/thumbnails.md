# Thumbnail playbook (series documentaries)

Researched 5 Nov 2026, when the producer asked for "very attractive, best of the best thumbnails". Sources: Paddy
Galloway's three-element rule (MrBeast's packaging consultant), the leaked MrBeast production handbook (CTR, curiosity,
"the thumbnail sets the expectation"), AmpiFire's 2026 thumbnail study, Mark Studios' source-checked CTR statistics
(Netflix artwork research, Lingnan University's 16,215-video study), YouTube Help on Test & Compare, and a contact sheet
of 30 current thumbnails from ColdFusion, Johnny Harris, ModernMBA, MagnatesMedia and Company Man.

## What the evidence says

| Rule                                                                                                     | Evidence                                                                                                                                                                                     |
| -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Three elements or fewer**: one dominant subject, one line of text, one supporting object.              | Galloway: "you shouldn't really have more than 3 things the viewer is focusing on". AmpiFire: more than three elements, about 23% lower CTR. Netflix: artwork with more than 3 people loses. |
| **One focal point**, big and bright. Faces lit and never under-exposed.                                  | Galloway: "ensure faces and subjects are bright and not under exposed". Eye-tracking studies cited by AmpiFire.                                                                              |
| **A real human face with emotion** beats objects when we have one. Single person, not a group.           | Lingnan: thumbnails with faces associated with more viewers. Netflix: single-person portraits beat multi-person images.                                                                      |
| **0–3 words, about 12 characters or fewer.** Text adds what the image can't; it never repeats the title. | AmpiFire: 0–3 words performs best and 7+ words underperforms. Lingnan: long text, fewer clicks. MrBeast handbook: text only adds context.                                                    |
| **Before/after or contrast** (two numbers, then and now).                                                | AmpiFire: before/after framing about +35% CTR.                                                                                                                                               |
| **High contrast, readable at 1 inch.** Over 70% of viewing is on mobile.                                 | Check every thumbnail at 168 px wide.                                                                                                                                                        |
| **Honest packaging.** The thumbnail is a promise the first 30 seconds must keep.                         | MrBeast handbook ("expectations"). YouTube's test picks the winner by **watch time share, not CTR**, so clickbait loses.                                                                     |
| **Consistent channel style.**                                                                            | AmpiFire: consistent styling, 15–20% higher subscriber CTR.                                                                                                                                  |

## House style

This is the style used by Hackyard; swap in your own brand. The honesty rules are not optional.

- **Look:** cinematic and premium, in the ColdFusion / Johnny Harris lane: a real photo, full-bleed, cut tight. Never the
  MagnatesMedia lane (AI-painted faces, money piles, fire, arrows). That is off-brand and fakes people.
- **Colours:** brand palette only: surface `#090c13`, ink `#e7f0fb`, white, blue `#2b5ce4` (the highlight box), light
  blue `#9cbdff`. Contrast comes from the photo and the blue box, never from new hues.
- **Type:** Space Grotesk 700, two lines at most. Line 1 is white; line 2 is the punch word in the blue box. Size it
  152–176 px on a 1280×720 canvas.
- **Layout:** the subject fills 55–70% of the frame on one side. Text sits on the other side, over a gradient from the
  brand surface. **Text never touches a face.**
- **The third element is proof:** a crop of the real document from the film, with the blue marker on the exact line.
  It is tilted 3° and shadowed. This is our signature and keeps the promise honest.
- **Brand:** the small brand mark, top left. Nothing else.
- **Photos:** Commons or other licensed images only, credited in the description. No frames from other broadcasters'
  footage, and no AI-generated people.

## Every video ships three variants (for YouTube Test & Compare)

| Variant             | Build                                                   | Why                                                     |
| ------------------- | ------------------------------------------------------- | ------------------------------------------------------- |
| **A. Face + punch** | The person, large; 1–3 words; a small proof card.       | Faces lead CTR.                                         |
| **B. Proof**        | The document card, large, with the marker; 1–3 words.   | Curiosity plus credibility; it suits our evidence edit. |
| **C. Contrast**     | Two numbers or then-versus-now, over the subject photo. | Before/after framing.                                   |

Upload all three to Test & Compare. YouTube keeps the one with the most **watch time**. Record the winner in `UPLOAD.md`
and reuse that pattern.

## Checklist before export

1. Three elements or fewer? Is the subject the brightest thing in the frame?
2. Is the text 3 words or fewer and about 12 characters or fewer? Does it avoid repeating the title?
3. Is any text over a face? (It must not be.)
4. At 168 px wide, can you still read the words and tell what the picture is? (`thumbs-mobile.jpg`)
5. Is it true? Does the film deliver this within its first minute?

The HTML builder is `tools/thumbnails/html_thumbs.py <project>`. It reads `thumbnail/spec.json`, writes
`thumbnail/index.html` (one composition, three variants), snapshots it on the render VM and writes
`thumbnail/renders/<proj>-thumb-{a,b,c}.jpg` plus a mobile check sheet.

## v2 design (5 Nov 2026): what Pinterest taught us

The producer's verdict on v1 was "good in concepts but design wise isn't good". The concepts (A face, B proof, C contrast)
stay. The design changed after a Pinterest study with the `pinmuse` moodboard tool. Four boards, 24 pins each: "business
documentary youtube thumbnail", "cinematic documentary youtube thumbnail", "dark documentary youtube thumbnail" and
"startup failure youtube thumbnail".

```bash
export SSL_CERT_FILE=$(python3 -c "import certifi;print(certifi.where())")
pinmuse moodboard "dark documentary youtube thumbnail" -n 24 -o ./pins
```

**What the strongest pins share, and how we use it:**

| Pattern on Pinterest                                                                  | Our version                                                                                                                                         |
| ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| The person is **cut out** from the background, not a rectangle photo with a gradient. | Remove the background on the render VM with a Docker image running `rembg` and the `birefnet-portrait` model. Cut-outs go in `media/cutouts/`.      |
| **Black-and-white** subject with **one accent colour**.                               | `grayscale(1) contrast(1.28)`. The only colour is brand blue `#2b5ce4` (glow, box, marker, strike). Never red.                                      |
| **Huge word behind the head**: the subject overlaps the type, which gives depth.      | A 340–370 px word (the company or subject) behind the cut-out. Text still never covers a face, but a face may cover text.                           |
| A serious face, never a grin, for failure stories.                                    | Search Commons for a neutral or serious photo before using a smiling one. A smile is allowed only when it is the irony (for example C, "the hype"). |
| **Collage texture**: clippings, torn paper, grain.                                    | Real clippings from the film at about 4% opacity behind everything, an SVG grain overlay, and torn-paper edges on proof.                            |
| Proof is **magnified**, not shown as a small card.                                    | One line of the real document, cropped and enlarged to 75–90 px text on a torn strip, marked in blue, over the full page (darkened and blurred).    |
| Contrast numbers as a **crossed-out price**.                                          | The before number struck with a blue bar; the after number in the blue box; small uppercase labels in `#9cbdff`.                                    |

Layer order (back to front): clippings, vignette, glow, shade, giant word, cut-out, bottom fade, text, grain, brand mark.
The reference build was the thumbnail set for The Fall: Quibi.

### gpt-image-2.5 as a second builder (Quibi test, 5 Nov 2026)

The producer picked a mixed set: HTML for A, `gpt-image-2.5` for B (proof) and C (contrast). To use the model, call the
Azure OpenAI image **edits** endpoint (`AZURE_OPENAI_ENDPOINT`, your image deployment) at 1536×1024 with the real
cut-out photo (and the real document for B) as references, then crop the middle to 1280×720. Keep every word and face
inside the central 84% of the height. Before shipping a generated image, check:

1. **Background text:** the model invents headlines ("Quibi Dies After Six Months", "Media Giant"). Blur or remove all of
   them. An invented headline is a fabricated source.
2. **Document text:** compare every visible line with the real document.
3. **Face:** put it side by side with the source photo. Fidelity is close but redrawn, so record that in `UPLOAD.md`.
4. **Brand:** the model drops the brand mark and softens the palette. Add the mark, and reject heavy coloured halos.

## Default builder from 6 Nov 2026: gpt-image-2.5

From 6 Nov 2026 the producer switched every film's set to `gpt-image-2.5`. `tools/thumbnails/gpt_thumbs.py <film>`
does the work. It reads `<film>/thumbnail/gpt.json` (the giant word for A, the photo and two-line hook for A, the proof
card plus the exact strip words and a photo for B, the photo and before/after lines for C), sends the real photo and
document as references to the image edits endpoint (1536×1024, quality high, about one call every 6.5 s), retries once if
output moderation blocks a job, and crops each result to `thumbnail/renders/<film>-thumb-{a,b,c}.jpg` (1280×720).
Re-run one variant with `gpt_thumbs.py <film> b`.

Then write the `UPLOAD.md` thumbnail section with the photo and document credits, and say that the people and documents
are redrawn by the model.

Review every image before shipping:

- exact spelling;
- no invented background text or objects (compare any surprising detail with the source photo);
- document text faithful to the original, line by line;
- likeness checked against the credited source photo.

If Azure's output moderation blocks a job, retry once, then change the reference. (A New York Times page about Qwikster
was blocked three times; Netflix's own letter passed.)
