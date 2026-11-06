#!/usr/bin/env python3
"""The 9:16 Short (1080x1920, ~50 s): frame one is the hook on a real document, every line sits on a card with the
marker, quote clips sit in a 16:9 band, and the last line runs back into the first so the loop is seamless."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2] / "engine"))
from build_lib import Edit  # noqa: E402
from film_helpers import H  # noqa: E402

E = Edit(ROOT, 1080, 1920)
E.drift = True
H.setup(E, chapters=3)
wi = H.wi
SRC = "Outlet · Document, date"
F1 = {"art": "artifacts/c-example.png", "label": SRC, "view": [(0.42, 1.0), (0.43, 1.06)], "marks": [], "cx": 0.5}

# frame one: the hook is on screen at t=0, above the card, never over a face
E.vo("v0a", [F1], gap=0.2, caps="auto:billion", low=True)
E.key("*$47B.*|Then the filing.", 0.0, E.t + 1.2, "O", instant=True)

# ... 3 short chapters: E.counter("1/3", a, b) + E.key(title, a, b, "T") over their lines ...

# the loop line returns to frame one's card
a = E.t
E.vo("v0g", [dict(F1, view=F1["view"][::-1])], gap=0.25, caps="auto:worth", low=True)
E.mark("hackyard.org", a - 1.0, E.t)
E.write("Short title", vertical=True)
E.write_srt(ROOT / "renders" / "short.en.srt")
print("end", round(E.t, 2))
