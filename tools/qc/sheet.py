"""sheet.py <dir> <out.jpg>: one row per downloaded clip, eight frames across it, labelled with times.

Use it on media/raw before choosing quotes and b-roll bands: it shows burned-in lower thirds, logos and interviewer
shots you must cut around (a band that shows the interviewer instead of the subject is a common miss)."""
import subprocess, sys, pathlib
from PIL import Image, ImageDraw
d = pathlib.Path(sys.argv[1]); fs = sorted(d.glob("*.mp4")); W, H = 256, 144; N = 8
out = Image.new("RGB", (W * N + 260, H * len(fs)), "white"); dr = ImageDraw.Draw(out)
for r, f in enumerate(fs):
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout)
    dr.text((4, r * H + 4), f.stem[:38], fill="black"); dr.text((4, r * H + 20), f"{dur:.0f}s", fill="black")
    for c in range(N):
        t = dur * (c + 0.5) / N
        p = subprocess.run(["ffmpeg", "-v", "error", "-threads", "2", "-ss", f"{t:.2f}", "-i", str(f), "-frames:v", "1", "-vf", f"scale={W}:{H}", "-f", "image2pipe", "-vcodec", "mjpeg", "-"], capture_output=True).stdout
        if p:
            import io; out.paste(Image.open(io.BytesIO(p)), (260 + c * W, r * H))
        dr.text((262 + c * W, r * H + 2), f"{t:.0f}", fill="yellow")
out.save(sys.argv[2], quality=72)
