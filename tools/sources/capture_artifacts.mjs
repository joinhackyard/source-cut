// Screenshot real web artifacts (Wayback pages, filings, archives, excerpt pages) for the edit, and record where
// the sentences to highlight sit on each shot. Runs on the render VM inside hyperframes-runner:
//   docker run --rm -v ~/capture:/w -w /w hyperframes-runner node capture_artifacts.mjs artifacts.json out
// artifacts.json: [{name, url, width, height, dsf?, mobile?, anchor?, marks?: [phrase, ...]}]
// Writes out/<name>.png and out/rects.json: {name: {w, h, marks: [{phrase, rects: [[x, y, w, h], ...]}]}} in image px.
import fs from "node:fs";
import { createRequire } from "node:module";

const puppeteer = createRequire("/usr/local/lib/node_modules/hyperframes/")("puppeteer-core");

const [, , jobsFile, outDir] = process.argv;
const jobs = JSON.parse(fs.readFileSync(jobsFile, "utf8"));
fs.mkdirSync(outDir, { recursive: true });
const browser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH || "/usr/bin/chromium",
  args: ["--no-sandbox", "--hide-scrollbars", "--disable-gpu"],
});
const out = fs.existsSync(`${outDir}/rects.json`) ? JSON.parse(fs.readFileSync(`${outDir}/rects.json`, "utf8")) : {};

for (const j of jobs) {
  const page = await browser.newPage();
  const dsf = j.dsf || 2;
  await page.setViewport({ width: j.width, height: j.height, deviceScaleFactor: dsf, isMobile: !!j.mobile, hasTouch: !!j.mobile });
  if (j.mobile) {
    await page.setUserAgent("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1");
  }
  try {
    await page.goto(j.url, { waitUntil: "networkidle2", timeout: 90000 });
  } catch (e) {
    console.log(j.name, "goto:", e.message.split("\n")[0]);
  }
  await new Promise((r) => setTimeout(r, j.wait || 2500));
  // put the anchor sentence ~18% down the viewport
  const found = await page.evaluate((anchor) => {
    if (!anchor) return true;
    const re = new RegExp(anchor.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/\s+/g, "\\s+"), "i");
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let n = w.nextNode(); n; n = w.nextNode()) {
      const m = re.exec(n.textContent);
      if (m) {
        const r = document.createRange();
        r.setStart(n, m.index);
        r.setEnd(n, m.index + m[0].length);
        const b = r.getBoundingClientRect();
        window.scrollTo(0, Math.max(0, window.scrollY + b.top - innerHeight * 0.18));
        return true;
      }
    }
    return false;
  }, j.anchor || "");
  // drop cookie banners and other fixed/sticky overlays so they never sit on the shot
  await page.evaluate(() => {
    for (const el of document.querySelectorAll("body *")) {
      const p = getComputedStyle(el).position;
      if (p === "fixed" || p === "sticky") el.remove();
    }
  });
  await new Promise((r) => setTimeout(r, 800));
  const marks = await page.evaluate((phrases) => {
    const res = [];
    for (const p of phrases || []) {
      const rects = [];
      const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      for (let n = w.nextNode(); n; n = w.nextNode()) {
        // whitespace in the phrase matches any run of spaces/newlines (pre-formatted text wraps mid-sentence)
        const re = new RegExp(p.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/\s+/g, "\\s+"), "i");
        const m = re.exec(n.textContent);
        if (!m) continue;
        const r = document.createRange();
        r.setStart(n, m.index);
        r.setEnd(n, m.index + m[0].length);
        for (const c of r.getClientRects()) rects.push([c.left, c.top, c.width, c.height]);
        break;
      }
      res.push({ phrase: p, rects });
    }
    return res;
  }, j.marks);
  await page.screenshot({ path: `${outDir}/${j.name}.png` });
  out[j.name] = {
    url: j.url, w: j.width * dsf, h: j.height * dsf, anchorFound: found,
    marks: marks.map((m) => ({ phrase: m.phrase, rects: m.rects.map((r) => r.map((v) => Math.round(v * dsf))) })),
  };
  console.log(j.name, found ? "ok" : "ANCHOR NOT FOUND", marks.map((m) => `${m.phrase.slice(0, 24)}:${m.rects.length}`).join(" "));
  await page.close();
}
fs.writeFileSync(`${outDir}/rects.json`, JSON.stringify(out, null, 1));
await browser.close();
