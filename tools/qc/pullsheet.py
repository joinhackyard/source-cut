#!/usr/bin/env python3
"""pullsheet.py <remote project path> <snapshot id> <out prefix> <w> <h> <cols> <per sheet>

Copy a HyperFrames snapshot set back from the render VM and tile it into contact sheets (<prefix>0.jpg, 1.jpg, ...),
so a whole film can be reviewed as a handful of images. Prints each sheet with the times it covers.
"""
import os
import pathlib
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "lib"))
from env import need  # noqa: E402

env = need("SOURCE_CUT_RENDER_HOST")
host, key = env["SOURCE_CUT_RENDER_HOST"], os.path.expanduser(env.get("SOURCE_CUT_SSH_KEY", "~/.ssh/id_ed25519"))
proj, sid, pre, w, h, cols, per = sys.argv[1:8]
w, h, cols, per = int(w), int(h), int(cols), int(per)
d = tempfile.mkdtemp()
subprocess.run(f"ssh -i {key} {host} 'docker run --rm -v $(realpath {proj}):/work hyperframes-runner chown -R $(id -u):$(id -g) "
               f"/work/.hyperframes; cd {proj}/.hyperframes/artifacts/snapshots/{sid} && tar cf - frame-*.png' | tar xf - -C {d}",
               shell=True, check=True)
fs = sorted([f for f in os.listdir(d) if f.startswith("frame-")], key=lambda f: int(re.search(r"frame-(\d+)", f)[1]))
for k in range(0, len(fs), per):
    ch = fs[k:k + per]
    args, fl = [], []
    for i, f in enumerate(ch):
        args += ["-i", os.path.join(d, f)]
        fl.append(f"[{i}]scale={w}:{h},setsar=1[v{i}]")
    n = len(ch)
    pad = (-n) % cols
    for j in range(pad):
        args += ["-f", "lavfi", "-i", f"color=black:s={w}x{h}"]
        fl.append(f"[{n + j}]setsar=1[v{n + j}]")
    rows = []
    for r in range((n + pad) // cols):
        fl.append("".join(f"[v{r * cols + c}]" for c in range(cols)) + f"hstack={cols}[r{r}]")
        rows.append(f"[r{r}]")
    fl.append("".join(rows) + (f"vstack={len(rows)}" if len(rows) > 1 else "null"))
    out = f"{pre}{k // per}.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-threads", "4"] + args + ["-filter_complex", ";".join(fl), "-frames:v", "1", out], check=True)
    print(out, [re.search(r"at-([\d.]+)s", f)[1] for f in ch])
