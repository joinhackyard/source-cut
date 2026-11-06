"""Azure OpenAI image calls (generate or edit with reference images). Key and endpoint come from .env.

Used by gpt_thumbs.py. The deployment allows about 10 images a minute: calls are spaced 6.5 s apart and can run in up
to four parallel streams. If output moderation blocks a job, retry once; if it is blocked again, change the reference
(a different photo, or a different document) rather than the wording.
"""
import base64
import json
import pathlib
import sys
import time
import urllib.error
import urllib.request
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "lib"))
from env import need  # noqa: E402

API = "2025-04-01-preview"
_last = [0.0]


def _multipart(fields, files):
    b = uuid.uuid4().hex
    parts = [f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode() for k, v in fields.items()]
    for p in files:
        p = pathlib.Path(p)
        mime = "image/png" if p.suffix == ".png" else "image/jpeg"
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="image[]"; filename="{p.name}"\r\n'
                     f"Content-Type: {mime}\r\n\r\n".encode() + p.read_bytes() + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={b}"


def generate(prompt, out, refs=(), size="1536x1024", quality="high"):
    """Write one image to `out`. With refs, uses the edits endpoint (references guide the subject and layout)."""
    env = need("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_KEY")
    dep = env.get("AZURE_IMAGE_DEPLOYMENT", "gpt-image-2.5-sunburst")
    base = f"{env['AZURE_OPENAI_ENDPOINT'].rstrip('/')}/openai/deployments/{dep}/images"
    wait = 6.5 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()
    fields = {"prompt": prompt, "size": size, "quality": quality, "n": 1}
    if refs:
        body, ctype = _multipart(fields, refs)
        url = f"{base}/edits?api-version={API}"
    else:
        body, ctype = json.dumps(fields).encode(), "application/json"
        url = f"{base}/generations?api-version={API}"
    req = urllib.request.Request(url, data=body, method="POST", headers={"api-key": env["AZURE_OPENAI_KEY"], "Content-Type": ctype})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        return False, e.read().decode()[:400]
    pathlib.Path(out).write_bytes(base64.b64decode(data["data"][0]["b64_json"]))
    return True, str(out)
