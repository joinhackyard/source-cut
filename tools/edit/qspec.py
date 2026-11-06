"""qspec.py: find the time span of a quote in transcribed raw sections.

    from qspec import load, span
    W = load("media/raw/words.jsonl")                 # from clip_words.sh
    span(W, "abc123-102-131", "We have a", "regrets.")  # -> [t_first_word_start, t_last_word_end]

Paste the result into qcut.py's spec as ["quote-name", "abc123-102-131", t0, t1]. Matching ignores case and punctuation.
"""
import json, re
def load(p): return {json.loads(l)["file"][:-4]: json.loads(l)["words"] for l in open(p) if l.strip()}
n = lambda s: re.sub(r"[^a-z0-9%$]", "", s.lower())
def find(ws, phrase, frm=0):
    p = [n(x) for x in phrase.split()]
    for i in range(frm, len(ws) - len(p) + 1):
        if [n(w[0]) for w in ws[i:i + len(p)]] == p: return i
    raise SystemExit(f"not found: {phrase}")
def span(W, stem, first, last):
    ws = W[stem]; i = find(ws, first); j = find(ws, last, i) + len(last.split()) - 1
    return [ws[i][1], ws[j][2]]
