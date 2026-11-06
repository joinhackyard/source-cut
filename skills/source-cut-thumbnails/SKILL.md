---
name: source-cut-thumbnails
description: Make, review and score three YouTube thumbnails (A face + punch, B proof, C contrast) for a Source Cut film - Pinterest research with pinmuse, gpt-image-2.5 from real references (tools/thumbnails/gpt_thumbs.py) or the HTML builder, invented-content checks, phone-size check, and a strict viewer-psychology score. Use when a film is finished or a thumbnail needs a redesign.
---

# Thumbnails

Read `playbooks/thumbnails.md`. Three variants per film, all uploaded to YouTube Test & compare (it keeps the one with
the most watch time, so honesty wins):

| Variant | Build |
| --- | --- |
| **A, face + punch** | The person in black and white, cut out, in front of a giant word (the company); a 1–3 word hook, the second line in the blue box. |
| **B, proof** | The real document on torn paper, the key line lifted out on a strip with the blue marker, the person beside it. |
| **C, contrast** | Before and after: two short lines, the second in the blue box (strike the first only when it is a drop). |

## 1. Research the look (once per series, or when the user wants a redesign)

`pinmuse moodboard "<query>" -n 24 -o <dir>` (with `SSL_CERT_FILE` set to certifi on macOS); read the contact sheet and
note composition, type, colour and recurring devices. Good queries: "business documentary youtube thumbnail", "dark
documentary youtube thumbnail", "aviation documentary youtube thumbnail". Adapt what works to the brand: one accent
colour, black-and-white subjects, a huge word behind the head, torn paper, grain.

## 2. Make them

Write `thumbnail/gpt.json` (see `templates/film/thumbnail/gpt.json`) and run
`python3 tools/thumbnails/gpt_thumbs.py films/<slug>`. Re-run one variant with `... films/<slug> b`.
If moderation blocks a variant twice, change the reference (another photo, or the company's own document).
For exact likeness and no AI pixels, use `tools/thumbnails/html_thumbs.py` with `thumbnail/spec.json`, and cut people
out first with `tools/thumbnails/cutout.sh`.

## 3. Review every image (never skip)

- Spelling of every word, exactly as specified.
- **Invented content:** headlines in the background, extra aircraft or objects, logos. Compare any surprising detail
  with the source photo; if it is not in the source, regenerate or blur it.
- Document text faithful, line by line, where readable.
- Likeness: side by side with the source photo. The model redraws faces; say so in `UPLOAD.md`.
- Text never over a face; the whole subject inside the frame after the 16:9 crop.
- Phone check: every variant at 168 px wide must still read.

## 4. Score strictly (viewer psychology, a half-second glance on a phone)

| Criterion | Points |
| --- | --- |
| Glance read | 20 |
| Curiosity gap (a question only the film answers) | 25 |
| Title pairing (adds to the title, never repeats it) | 15 |
| Human hook (a face, ideally with eye contact or emotion) | 15 |
| Clarity (one focal point, three elements or fewer) | 15 |
| Trust (real, credited, no invented content) | 10 |

Aim for 90+. Report scores honestly: a plane-only or building-only image rarely passes 90 on the human hook, and that
is a reason to test it, not to inflate it.
