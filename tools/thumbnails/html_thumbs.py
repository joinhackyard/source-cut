#!/usr/bin/env python3
"""html_thumbs.py <film>: three thumbnail variants (A face, B proof, C contrast) built in HTML from <film>/thumbnail/spec.json.

No AI pixels: real photos and real document crops, laid out in HTML and snapshotted on the render VM. Use it when you
want exact likeness, or as the reference the GPT builder (gpt_thumbs.py) is checked against.

Follows playbooks/thumbnails.md: <=3 elements, 1-3 words, text never over a face, brand colours only, a real
document crop with the blue marker as the proof element. Writes thumbnail/index.html (one composition, a variant per
second), snapshots it on the render VM, and saves renders/<project>-thumb-{a,b,c}.{png,jpg} plus thumbs-mobile.jpg.

spec.json: {"variants": [{"kind": "face"|"card", "photo": "media/images/x.jpg", "pos": "70% 30%", "shift": 0, "zoom": 1, "bright": 1.13, "shade": 0.0-0.6,
            "text": "left"|"right", "l1": "22%", "l2": "58%.", "size": 160,
            "card": {"png": "media/artifacts/c-x.png", "marks": [0, 2], "at": "br"|"bl"|"tr", "w": 440}}]}
"""
import html
import json
import pathlib
import re
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools" / "lib"))
from env import need  # noqa: E402

ENV = need("SOURCE_CUT_RENDER_HOST")
VM, KEY = ENV["SOURCE_CUT_RENDER_HOST"], str(pathlib.Path(ENV.get("SOURCE_CUT_SSH_KEY", "~/.ssh/id_ed25519")).expanduser())
REMOTE = ENV.get("SOURCE_CUT_REMOTE_ROOT", "videos")
P = pathlib.Path(sys.argv[1]).resolve()
proj = P.name
T = P / "thumbnail"
spec = json.loads((T / "spec.json").read_text())
(T / "assets").mkdir(parents=True, exist_ok=True)
(T / "renders").mkdir(exist_ok=True)
for f in ("SpaceGrotesk-latin.woff2", "gsap-3.14.2.min.js"):  # fetched by scripts/setup-assets.sh
    shutil.copy(REPO / "engine" / "assets" / f, T / "assets" / f)


def asset(rel):
    src = P / rel
    shutil.copy(src, T / "assets" / src.name)
    return "assets/" + src.name


def png_size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.split(",")
    return int(out[0]), int(out[1])


def card(c, big):
    """A crop of the real document around the marked lines, with the blue marker drawn on them."""
    png = P / c["png"]
    rects = json.loads((P / "media/artifacts/rects.json").read_text())[png.stem]
    W, H = png_size(png)
    rs = [r for k in c["marks"] for r in rects["marks"][k]["rects"] if r[2] > 4]
    x0 = max(0, min(r[0] for r in rs) - 300)  # a tight excerpt; the card's side edges fade (no hard-cut words)
    x1 = min(W, max(r[0] + r[2] for r in rs) + 300)
    y0 = max(0, min(r[1] for r in rs) - 90)
    y1 = min(H, max(r[1] + r[3] for r in rs) + 130)
    x0, x1, y0 = (0, W, 0) if big else (x0, x1, y0)
    w = c.get("w", 760 if big else 560)
    s = w / (x1 - x0)
    hl = "".join(f'<i style="left:{(r[0] - x0) * s - 4:.0f}px;top:{(r[1] - y0) * s - 2:.0f}px;'
                 f'width:{r[2] * s + 8:.0f}px;height:{r[3] * s + 4:.0f}px"></i>' for r in rs)
    at = c.get("at", "br")
    place = {"br": "right:56px;bottom:52px", "bl": "left:60px;bottom:52px", "tr": "right:56px;top:56px",
             "mr": "right:70px;top:50%;transform:translateY(-50%) rotate(-3deg)"}[at]
    rot = "" if at == "mr" else "transform:rotate(-3deg);"
    fade = "" if big else "-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 14%,#000 86%,transparent 100%);"
    return (f'<div class="card" style="{place};{rot}{fade}width:{w:.0f}px;height:{(y1 - y0) * s:.0f}px">'
            f'<img src="{asset(c["png"])}" style="width:{W * s:.0f}px;left:{-x0 * s:.0f}px;top:{-y0 * s:.0f}px" alt="" />'
            f"{hl}</div>")


def variant(i, v):
    side = v.get("text", "left")
    big = v["kind"] == "card"
    words = max(len(v["l1"]), len(v.get("l2", "")))
    size = v.get("size", min(176, int(640 / (0.58 * words))))
    grad = ("90deg" if side == "left" else "270deg")
    shade = v.get("shade", 0.0)
    move = (f"transform:translateX({v.get('shift', 0)}px) scale({v.get('zoom', 1)});transform-origin:50% 35%;"
            f"filter:brightness({v.get('bright', 1.13)}) contrast(1.12) saturate(1.06);")
    bg = (f'<img class="bg" src="{asset(v["photo"])}" style="object-position:{v.get("pos", "70% 30%")};'
          f'{"filter:blur(10px) brightness(0.42) saturate(0.8);transform:scale(1.08);" if big else ""}'
          f'{"" if big else move}" alt="" />')
    edge = round(max(0, v.get('shift', 0)) / 12.8 + 2)  # keep the shifted photo's left edge under solid surface
    fade = (f'<div class="fade" style="background:linear-gradient({grad},#090c13 0%,#090c13 {edge}%,rgba(9,12,19,.92) {max(26, edge + 8)}%,'
            f'rgba(9,12,19,.55) 44%,rgba(9,12,19,{shade}) 62%),linear-gradient(0deg,rgba(9,12,19,.55) 0%,rgba(9,12,19,0) 32%)"></div>')
    text = (f'<h1 class="line" style="{side}:62px;font-size:{size}px">'
            f'<span>{html.escape(v["l1"])}</span>'
            + (f'<span><span class="hl">{html.escape(v["l2"])}</span></span>' if v.get("l2") else "") + "</h1>")
    crd = card(v["card"], big) if v.get("card") else ""
    mark = ('<div class="brand"><div class="mark"><span class="rail"></span><span class="rail r2"></span>'
            '<span class="bridge"></span><span class="node n1"></span><span class="node n2"></span><span class="node n3"></span>'
            '<span class="node n4"></span><span class="node n5"></span><span class="node n6"></span></div>Hackyard</div>')
    return (f'<div id="v{i}" class="clip v" data-start="{i}" data-duration="1" data-track-index="1">'
            f"{bg}{fade}{crd}{text}{mark}</div>")


CSS = """
@font-face{font-family:"Space Grotesk";src:url("assets/SpaceGrotesk-latin.woff2") format("woff2");font-weight:300 700}
html,body{margin:0;background:#090c13}
#root{position:relative;width:1280px;height:720px;overflow:hidden;background:#090c13}
.v{position:absolute;inset:0;overflow:hidden;background:#090c13}
.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:brightness(1.13) contrast(1.12) saturate(1.06)}
.fade{position:absolute;inset:0}
.card{position:absolute;overflow:hidden;background:#f4efe4;border-radius:6px;
  box-shadow:0 28px 60px rgba(9,12,19,.7),0 0 0 1px rgba(231,240,251,.08)}
.card img{position:absolute;max-width:none}
.card i{position:absolute;background:rgba(43,92,228,.34);border-bottom:3px solid #2b5ce4;border-radius:2px}
.line{position:absolute;top:50%;transform:translateY(-54%);margin:0;font:700 160px/0.92 "Space Grotesk",sans-serif;
  letter-spacing:-0.05em;color:#fff;text-shadow:0 6px 30px rgba(9,12,19,.55)}
.line>span{display:block;white-space:nowrap}
.line .hl{display:inline-block;background:#2b5ce4;color:#fff;padding:.02em .12em .1em .08em;margin-top:.1em;text-shadow:none}
.brand{position:absolute;left:62px;top:50px;display:inline-flex;align-items:center;color:#e7f0fb;
  font:500 28px/1 "Space Grotesk",sans-serif;letter-spacing:-.04em;opacity:.92}
.mark{position:relative;width:.78em;height:.88em;margin-right:.3em}
.mark span{position:absolute;background:#9cbdff}
.mark .rail{top:11.71875%;left:11.4035%;width:4.386%;height:76.5625%}.mark .rail.r2{left:85.0877%}
.mark .bridge{top:47.65625%;left:13.1579%;width:73.6842%;height:4.6875%}
.mark .node{width:26.3158%;height:23.4375%;border-radius:2px}
.mark .n1{top:0;left:0}.mark .n2{top:0;left:73.6842%}.mark .n3{top:38.28125%;left:0}
.mark .n4{top:38.28125%;left:73.6842%}.mark .n5{top:76.5625%;left:0}.mark .n6{top:76.5625%;left:73.6842%}
"""

vs = spec["variants"]
page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{proj} thumbnails</title>'
        f'<script src="assets/gsap-3.14.2.min.js"></script><style>{CSS}</style></head><body>'
        f'<div id="root" data-composition-id="main" data-start="0" data-duration="{len(vs)}" data-width="1280" data-height="720">'
        + "".join(variant(i, v) for i, v in enumerate(vs))
        + '</div><script>(function(){const tl=gsap.timeline({paused:true});tl.set("#root",{opacity:1},0);'
          'window.__timelines=window.__timelines||{};window.__timelines["main"]=tl;})();</script></body></html>')
(T / "index.html").write_text(page)

at = ",".join(f"{i + 0.5}" for i in range(len(vs)))
rel = T.relative_to(pathlib.Path.cwd()) if T.is_relative_to(pathlib.Path.cwd()) else T
out = subprocess.run([str(REPO / "tools/render/vm.sh"), str(rel), "snapshot", "--at", at], capture_output=True, text=True).stdout
snap = re.search(r"snapshots/([^/]+)/frame-00", out).group(1)
sh = lambda c: subprocess.run(c, shell=True, check=True, capture_output=True, text=True).stdout
sh(f"ssh -i {KEY} {VM} 'docker run --rm -v $(realpath {REMOTE}/{rel}):/w hyperframes-runner chown -R $(id -u):$(id -g) /w/.hyperframes'")
names = []
for i in range(len(vs)):
    n = T / "renders" / f"{proj}-thumb-{'abc'[i]}"
    sh(f"scp -i {KEY} -q '{VM}:{REMOTE}/{rel}/.hyperframes/artifacts/snapshots/{snap}/frame-0{i}-at-{i + 0.5}s.png' {n}.png")
    sh(f"ffmpeg -v error -y -i {n}.png -q:v 2 {n}.jpg")
    names.append(f"{n}.jpg")
# mobile check: each variant at 336 px (home feed) and 168 px (search / suggested), side by side
inputs = " ".join(f"-i {n}" for n in names)
fc = "".join(f"[{i}]split[a{i}][b{i}];[a{i}]scale=336:-1[x{i}];[b{i}]scale=168:-1,pad=168:189:0:0:color=0x111927[y{i}];"
             f"[x{i}][y{i}]hstack[r{i}];" for i in range(len(names)))
fc += "".join(f"[r{i}]" for i in range(len(names))) + f"vstack=inputs={len(names)}"
sh(f"ffmpeg -v error -y {inputs} -filter_complex '{fc}' {T / 'renders/thumbs-mobile.jpg'}")
print(proj, "->", ", ".join(pathlib.Path(n).name for n in names), "+ thumbs-mobile.jpg")
