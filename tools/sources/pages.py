"""Excerpt pages: a clean, readable card for a real document, with the exact sentences the narrator quotes.

Many sources are hard to show as they are (a 300-page S-1, a paywalled article, a scanned PDF). For those, set the
quoted paragraphs verbatim on a neutral newspaper-style page (masthead = the real outlet and date, real headline, real
byline), with "[…]" where you skip text, then screenshot it on the VM and record where each marked phrase sits.
Every marked phrase must appear word for word in the paragraphs: the builder refuses to write a page otherwise.

    from pages import Pages
    P = Pages("films/my-film", "mf")
    P.page("s1-lease", "The We Company · Form S-1", "14 August 2019", "Form S-1 Registration Statement", "Filed with the SEC",
           ["The average length of the initial term of our U.S. leases is approximately 15 years …"],
           marks=["approximately 15 years", "$47.2 billion"])
    P.capture()   # -> media/artifacts/c-s1-lease.png + media/artifacts/rects.json

Keep the excerpt short (the sentences you need, plus a line of context), and link the full source in the description.
"""
import html
import json
import pathlib
import subprocess
import sys

TOOLS = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS / "lib"))
from env import need  # noqa: E402

CSS = (pathlib.Path(__file__).with_name("page.css")).read_text()


class Pages:
    def __init__(self, film, tag):
        self.film, self.tag, self.jobs = pathlib.Path(film), tag, []
        (self.film / "pages").mkdir(parents=True, exist_ok=True)

    def page(self, name, mast, date, head, by, paras, marks, sub="", h=640, w=1080):
        ps = "".join('<p class="gap">[…]</p>' if p == "…" else f"<p>{html.escape(p)}</p>" for p in paras)
        s = (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
             f'<div class="mast"><span>{html.escape(mast)}</span><small>{html.escape(date)}</small></div>'
             f"<h1>{html.escape(head)}</h1>" + (f"<h2>{html.escape(sub)}</h2>" if sub else "")
             + f'<div class="by">{html.escape(by)}</div>{ps}</body></html>')
        for m in marks:
            assert any(m in p for p in paras) or m in head, f"{name}: marked phrase not in the text: {m!r}"
        (self.film / "pages" / f"{name}.html").write_text(s)
        self.jobs.append({"name": "c-" + name, "url": f"file:///w/pages/{name}.html", "width": w, "height": h, "marks": marks})

    def capture(self):
        """Screenshot every page on the render VM; copy PNGs and rects.json into media/artifacts/."""
        env = need("SOURCE_CUT_RENDER_HOST")
        host, key = env["SOURCE_CUT_RENDER_HOST"], str(pathlib.Path(env.get("SOURCE_CUT_SSH_KEY", "~/.ssh/id_ed25519")).expanduser())
        art = self.film / "media" / "artifacts"
        art.mkdir(parents=True, exist_ok=True)
        jobs = self.film / "pages" / "artifacts.json"
        jobs.write_text(json.dumps(self.jobs, indent=1))
        sh = lambda *c: subprocess.run(list(c), check=True, capture_output=True, text=True).stdout
        sh("ssh", "-i", key, host, "rm -rf ~/capture/pages && mkdir -p ~/capture/pages")
        sh("scp", "-q", "-i", key, str(TOOLS / "sources" / "capture_artifacts.mjs"), str(jobs), f"{host}:capture/")
        sh("scp", "-q", "-i", key, *map(str, (self.film / "pages").glob("*.html")), f"{host}:capture/pages/")
        print(sh("ssh", "-i", key, host,
                 f"cd ~/capture && rm -rf out-{self.tag} && docker run --rm -v ~/capture:/w -w /w hyperframes-runner "
                 f"node capture_artifacts.mjs artifacts.json out-{self.tag} 2>&1 | tail -40 && "
                 f"docker run --rm -v ~/capture:/w hyperframes-runner chown -R $(id -u):$(id -g) /w/out-{self.tag}"))
        sh("scp", "-q", "-i", key, f"{host}:capture/out-{self.tag}/*", str(art) + "/")
        r = json.loads((art / "rects.json").read_text())
        for j in self.jobs:  # every mark must be found and sit inside the shot
            v = r[j["name"]]
            bad = [m["phrase"] for m in v["marks"] if not m["rects"] or max(x[1] + x[3] for x in m["rects"]) > v["h"]]
            print(j["name"], v["h"], "MISSING OR OFF THE PAGE: " + "; ".join(bad) if bad else "ok")
