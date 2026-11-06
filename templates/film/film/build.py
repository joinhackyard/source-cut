#!/usr/bin/env python3
"""The 16:9 film (1920x1080). Run `python3 build.py`, review contact sheets (tools/qc/check.sh), then render on the VM.

The edit is a sequence on a cursor: each vo() places a narration line and the shots under it; quote() places a clip;
chapter() a card. Marks are (phrase index in rects.json, word index) so the marker sweeps as the word is said.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2] / "engine"))
from build_lib import Edit  # noqa: E402
from film_helpers import H  # noqa: E402

E = Edit(ROOT, 1920, 1080)
E.caps_all, E.drift, E.cap_mode = True, True, "line"
E.hero = {"w0a": "fortyseven"}  # one emphasis word per line, lower case, no punctuation
H.setup(E, chapters=5)
vo, art, photo, band, wi, chapter, M = H.vo, H.art, H.photo, H.band, H.wi, H.chapter, H.M

SRC = "Outlet · Document, date"

# ---- cold open ----
E.pause(0.7, ["black"])
s = vo("w0a", [art("example", SRC, marks=[(0, wi("w0a", "forty-seven"))])], gap=0.4)
E.stamp("January 2019", s, E.t - 0.1)
M["title"] = E.chapter("SERIES NAME", "Film title", 4.6)

# ---- 1/5 ----
chapter(1, "Chapter title")
# vo("w1a", [photo("i-example.jpg", "Person, year · photo: author")], gap=0.3)
# E.quote("q-example", "Speaker · Programme, date", "auto:emphasis", gap=0.4, low="full")

# ---- the lesson + close ----
# E.checklist("What to take from it", ["One.", "Two.", "Three."], 4.4)
E.endcard(4.6, "Find your people. hackyard.org")

# ---- music (files in media/bgm) ----
# E.music("track.mp3", 0.0, E.t, 0.0, 0.11, fade_in=2.0, fade_out=4.0)
E.write("Film title", vertical=False)
E.write_srt(ROOT / "renders" / "film.en.srt")
print("end", round(E.t, 2))
