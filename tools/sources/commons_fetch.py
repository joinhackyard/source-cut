#!/usr/bin/env python3
"""Download Wikimedia Commons files into <film>/media/images and record author + licence in CREDITS.md.

  python3 tools/sources/commons_fetch.py <film>/media/images/commons.json

commons.json: {"i-neumann-2015.jpg": "File:TechCrunch Disrupt NY 2015 - Day 2 (17378512882).jpg", ...}
Files wider than 2400 px (and SVGs) come down as a 2400 px rendition. CREDITS.md is rewritten every run, so it always
matches what the film uses; the upload package builds its photo credits from it.

Commons asks automated clients for a descriptive User-Agent: set SOURCE_CUT_USER_AGENT in .env.
If you get SSL certificate errors on macOS: export SSL_CERT_FILE=$(python3 -c "import certifi;print(certifi.where())")
"""
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "lib"))
from env import load  # noqa: E402

UA = {"User-Agent": load().get("SOURCE_CUT_USER_AGENT", "SourceCut/1.0 (https://github.com/joinhackyard/source-cut)")}
spec = pathlib.Path(sys.argv[1])
OUT = spec.parent
FILES = json.loads(spec.read_text())


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()


credits = ["# Archive photos (Wikimedia Commons)\n", "| File | Source | Author | Licence |", "| --- | --- | --- | --- |"]
for name, title in FILES.items():
    q = urllib.parse.urlencode({"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url|extmetadata|size",
                                "iiurlwidth": 2400, "format": "json"})
    page = next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?" + q))["query"]["pages"].values()))
    if "imageinfo" not in page:
        print("MISSING", title)
        continue
    ii = page["imageinfo"][0]
    md = ii.get("extmetadata", {})
    url = ii.get("thumburl") if (ii.get("width", 0) > 2400 or title.endswith(".svg")) else ii["url"]
    if not (OUT / name).exists():
        (OUT / name).write_bytes(get(url))
        time.sleep(1.0)
    strip = lambda k: urllib.parse.unquote(re.sub("<[^>]+>", "", md.get(k, {}).get("value", "")).strip())
    lic, art = strip("LicenseShortName"), strip("Artist")
    credits.append(f"| {name} | {ii['descriptionurl']} | {art[:80]} | {lic} |")
    print(name, ii["width"], "x", ii["height"], "|", lic, "|", art[:50])
(OUT / "CREDITS.md").write_text("\n".join(credits) + "\n")
