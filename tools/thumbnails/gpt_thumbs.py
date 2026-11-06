#!/usr/bin/env python3
"""gpt_thumbs.py <film> [a|b|c ...]: three thumbnails (A face + punch, B proof, C contrast) with an Azure image model.

Reads <film>/thumbnail/gpt.json:
  {"word": "WEWORK",                                   # giant word behind the subject in A
   "a": {"photo": "i-neumann-2015.jpg", "l1": "$47B", "l2": "IPO?"},
   "b": {"card": "c-s1-lease.png", "strip": "$47.2 billion", "photo": "i-neumann-2015b.jpg",
         "label": "IN RENT IT HAD PROMISED TO PAY"},    # label is optional
   "c": {"photo": "i-wework-ny.jpg", "l1": "$47B.", "l2": "$8B.", "strike": true}}
Photos come from media/images, cards from media/artifacts. The strip must be words that appear on the card exactly.

Writes thumbnail/renders/<film>-thumb-{a,b,c}.jpg (1280x720, centre crop of the model's 1536x1024 frame; keep words and
faces in the middle 80% of the height). Review every output before you ship it: spelling, invented background text or
objects (compare any surprising detail with the source photo), the document's text, and the likeness.
"""
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gen_image import generate  # noqa: E402

STYLE = ("Style: premium cinematic business-documentary YouTube thumbnail, clean, one clear focal point, generous dark "
         "negative space, Netflix documentary key-art quality. Background near-black navy #090c13 with one soft royal-blue "
         "#2b5ce4 glow, fine film grain, gentle vignette. Photographs in high-contrast black and white with a thin cool blue "
         "rim light, cleanly cut out, sharp, faces well lit. Headline typography: bold modern geometric grotesk sans-serif "
         "(like Space Grotesk Bold), tight letter spacing, crisp, perfectly spelled. Only these colours: near-black navy, "
         "white, royal blue #2b5ce4, light blue #9cbdff, and off-white paper. No red, no yellow, no orange, no fire, no "
         "arrows, no emojis, no logos, no watermarks, no heavy glow halos. The background must contain NO readable words, NO "
         "headlines, NO newspaper clippings, NO extra objects. Do not add any words other than the ones specified. Wide 3:2 "
         "frame that will be cropped to 16:9: keep every word and every face inside the central 80% of the height. Nothing "
         "overlaps a face or the headline.")
KEEP = ("The subject in the reference photo is real: keep it exactly as it is (same face, features, hair, glasses, age and "
        "expression for a person; same shape and details for a building or object). Do not beautify, redraw, restyle or "
        "change the identity; only cut out, place and convert to black and white. ")


def prompts(g):
    a, b, c = g["a"], g["b"], g["c"]
    label = f"Above the strip, a small light-blue uppercase label: {b['label']}. " if b.get("label") else ""
    strike = "struck through by a thick tilted royal-blue bar" if c.get("strike") else "in white"
    return {
        "a": (f"Design a YouTube thumbnail (face + punch) with exactly three elements. {KEEP}(1) The subject of the reference "
              f"photo on the right 45% of the frame, large, head and shoulders if it is a person. (2) Behind it, huge white "
              f"bold letters spelling {g['word']} across the upper half of the frame, partly hidden behind the subject so it "
              f"stands in front of the type. (3) Lower left, the headline in two lines: '{a['l1']}' in white, and "
              f"'{a['l2']}' in white on a solid royal-blue rectangle. {STYLE}", ["images/" + a["photo"]]),
        "b": (f"Design a YouTube thumbnail (proof) with exactly three elements. Image 1 is a real document; image 2 is a real "
              f"photo. {KEEP.replace('reference photo', 'image 2')}(1) Left 60%: the document from image 1 as a slightly "
              f"tilted sheet of off-white paper with torn right and bottom edges, darkened and softly out of focus, its text "
              f"faithful to the original. (2) Across the middle-left, a torn paper strip lifted off the page in sharp focus, "
              f"magnifying exactly these words from the document in the same typeface: “{b['strip']}” with a translucent "
              f"royal-blue highlighter over them and a solid royal-blue underline. {label}(3) Right 35%: the subject of "
              f"image 2, black and white, not overlapped by anything. {STYLE}", ["artifacts/" + b["card"], "images/" + b["photo"]]),
        "c": (f"Design a YouTube thumbnail (contrast) with exactly three elements. {KEEP}(1) The subject of the reference photo "
              f"on the right 45% of the frame, large and dramatic. (2) Left side, the first line '{c['l1']}' huge, {strike}. "
              f"(3) Under it, '{c['l2']}' even bigger, in white on a solid royal-blue rectangle. Exactly those words, spelled "
              f"exactly. {STYLE}", ["images/" + c["photo"]]),
    }


if __name__ == "__main__":
    film = pathlib.Path(sys.argv[1])
    which = sys.argv[2:] or ["a", "b", "c"]
    g = json.loads((film / "thumbnail" / "gpt.json").read_text())
    R = film / "thumbnail" / "renders"
    R.mkdir(parents=True, exist_ok=True)
    for v, (prompt, refs) in prompts(g).items():
        if v not in which:
            continue
        raw = R / f"{film.name}-gpt-{v}.png"
        for attempt in (1, 2):  # output moderation sometimes blocks a real-person image once, then passes
            ok, msg = generate(prompt, raw, [film / "media" / r for r in refs])
            if ok:
                break
            print(v, "attempt", attempt, "failed:", msg[:160])
        if not ok:
            print(v, "BLOCKED: change the reference photo or document and run again with only this variant")
            continue
        out = R / f"{film.name}-thumb-{v}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-vf", "scale=1280:-1,crop=1280:720", "-q:v", "2", str(out)], check=True)
        print(v, "->", out)
