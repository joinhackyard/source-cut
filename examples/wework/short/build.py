#!/usr/bin/env python3
"""Builds index.html for The Fall Short / Reel "$47 billion. Then it filed its paperwork." (1080x1920, ~50 s).

Artifact-reel format v3 (playbooks/artifact-reel.md, playbooks/series-documentary.md), no stock: every line sits on a real
document on a card (WeWork's release, the S-1, Form RW, CNBC, Reuters) with a blue marker on the words the narrator says;
Adam Neumann speaks in his own clips (TechCrunch 2017, DealBook 2021) in a 16:9 band. The last line ("On paper, it was
worth") runs into the first ("$47 billion."). No end card: a hackyard.org mark instead. Music is not included: put a track in media/bgm.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2] / "engine"))
import build_lib  # noqa: E402
from build_lib import Edit, _norm  # noqa: E402

F, I, A = "footage/", "images/", "artifacts/"
E = Edit(ROOT, 1080, 1920, bright=set())
E.focus = {}
E.drift = True
_vo = E.vo
E.vo = lambda vid, shots=(), **kw: _vo(vid, shots, **{**kw, "low": True})
RECTS = json.loads((build_lib.MEDIA / "artifacts" / "rects.json").read_text())


def wi(vid, word, n=1):
    return [i for i, w in enumerate(E.words[vid]) if _norm(w[0]) == _norm(word)][n - 1]


def art(name, label, view, marks=(), cx=0.3):
    """view=None centres on the marks and zooms no further than keeps every marked word on the card."""
    ms, xs, ys = [], [], []
    for k, w in marks:
        rects = [r for r in RECTS["c-" + name]["marks"][k]["rects"] if r[2] > 4]
        ms += [(r, w) for r in rects]
        xs += [v for r in rects for v in (r[0], r[0] + r[2])]
        ys += [v for r in rects for v in (r[1], r[1] + r[3])]
    if view is None:
        W, H = RECTS["c-" + name]["w"], RECTS["c-" + name]["h"]
        sx = 0.92 / ((max(xs) - min(xs)) / W)
        sy = 0.8 * 740 / (960 * (max(ys) - min(ys)) / W)
        s0 = round(max(1.0, min(1.45, sx, sy) / 1.06), 3)
        cy = round((min(ys) + max(ys)) / 2 / H, 3)
        view, cx = [(cy, s0), (cy + 0.01, round(s0 * 1.06, 3))], round((min(xs) + max(xs)) / 2 / W, 3)
    return {"art": A + "c-" + name + ".png", "label": label, "view": view, "marks": ms, "cx": cx}


def band(name, label, ms=0):
    return {"band": F + name + ".mp4", "label": label, "ms": ms}


def chapter(n, title, body):
    a = E.t
    body()
    E.counter(f"{n}/3", a, E.t)
    E.key(title, a, E.t - 0.1, "T")
    E.sfx("tick.wav", a + 0.02, 0.45)


BW = "WeWork press release · Business Wire, 8 January 2019"
S1 = "The We Company · Form S-1, SEC, 14 August 2019"

# ---- hook: frame 1 is the $47 billion release and the line ----
F1 = {"art": A + "c-bw-47.png", "label": BW, "view": [(0.42, 1.0), (0.43, 1.06)], "marks": [], "cx": 0.5}
E.vo("v0a", [F1], gap=0.2, caps="auto:billion,paperwork")
E.key("*$47B.*|Then the filing.", 0.0, E.t + 1.2, "O", instant=True)


def filing():
    E.vo("v0b", [art("s1-losses", S1, None, marks=[(1, wi("v0b", "nine"))])], gap=0.3, caps="auto:loss,revenue")
    E.vo("v0c", [art("s1-lease", S1, None, marks=[(1, wi("v0c", "forty-seven")), (0, wi("v0c", "fifteen"))])], gap=0.2, caps="auto:years,months")
    E.quote("wq-choose", "Adam Neumann · TechCrunch Disrupt NY, 15 May 2017", "auto:choose,profitable", gap=0.4, low=True)
chapter(1, "The filing", filing)


def six():
    E.vo("v0d", [art("rw", "The We Company · Form RW, SEC, 30 September 2019", None, marks=[(1, wi("v0d", "withdrawn."))])], gap=0.4, caps="auto:withdrawn")
chapter(2, "Six days", six)


def rescue():
    E.vo("v0e", [art("cc-8b", "CNBC · 23 October 2019", None, marks=[(0, wi("v0e", "eight"))])], gap=0.3, caps="auto:eight")
    E.vo("v0f", [art("cj-son", "CNBC · Reuters, 6 November 2019", None, marks=[(0, wi("v0f", "judgment"))])], gap=0.2, caps="auto:judgment,poor")
    E.quote("wq-regrets", "Adam Neumann · DealBook Summit, 9 November 2021", "auto:lessons,regrets", gap=0.4, low=True)
chapter(3, "The rescue", rescue)

# ---- the loop line: back to frame 1's card, runs into "$47 billion." ----
a = E.t
E.vo("v0g", [dict(F1, view=F1["view"][::-1])], gap=0.25, caps="auto:worth")
E.mark("hackyard.org", a - 1.0, E.t)

END = E.t
E.music("m-c45eea55.mp3", 0.0, END, round(max(0.0, 61.0 - END - 2.0), 3), 0.13, fade_in=0.0, fade_out=0.3)
E.write("The Fall Short: WeWork", vertical=True)
E.write_srt(ROOT / "renders" / "wework-short.en.srt")
print("end", round(END, 2))
