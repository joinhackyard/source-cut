#!/usr/bin/env python3
"""The Fall: "WeWork: From $47 Billion to a Failed IPO" (1920x1080, about 7 minutes). The worked example for Source Cut.

Evidence edit on the series format (playbooks/series-documentary.md), no stock. Public record only: every
characterisation of Adam Neumann is attributed to a named outlet or document. Neumann speaks in his own clips (CBS 2016,
TechCrunch Disrupt 2017, CNBC 2019, DealBook 2021); Masayoshi Son and David Faber on CNBC (2019); Bloomberg and CNBC's
Deirdre Bosa for the verdicts; CBS footage of the spaces. Documents (the S-1 and its amendments, Form RW, WeWork and SoftBank
releases, Fast Company, CNBC, Reuters, the 10-Q and the bankruptcy 8-Ks) sit on cards with a marker on the words the
narrator says, each cut verbatim from the saved source.

Media is not in the repo: fetch photos (media/images/commons.json), voice the lines (voice/lines.tsv), capture the
pages (pages/), cut the quotes listed in RESEARCH.md, and add your own music, then run `python3 build.py`.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2] / "engine"))
from build_lib import Edit  # noqa: E402
from film_helpers import H  # noqa: E402

E = Edit(ROOT, 1920, 1080, bright=set())
E.caps_all, E.drift, E.cap_mode = True, True, "line"
E.focus = {}
E.hero = {
    "w0a": "fortyseven", "w0b": "rent", "w0c": "withdrawn", "w0d": "fell", "w1a": "shorter", "w1b": "cbs", "w1c": "not",
    "w1d": "fortyseven", "w1e": "twenty", "w1f": "consciousness", "w1g": "opportunity", "w1h": "losses", "w2a": "public",
    "w2b": "consciousness", "w2c": "nine", "w2d": "ninetythree", "w2e": "fortyseven", "w2f": "months", "w2g": "promised",
    "w3a": "majority", "w3b": "four", "w3c": "trademarks", "w3d": "unwound", "w3e": "hundred", "w3f": "ten", "w4a": "charge",
    "w4b": "distraction", "w4c": "withdrew", "w4d": "eighty", "w4e": "eight", "w4f": "seven", "w4g": "poor", "w5a": "nine",
    "w5b": "interview", "w5c": "doubt", "w5d": "bankruptcy", "w5e": "cancelled", "w5f": "dropbox", "w6a": "numbers",
    "w6b": "costs", "w6c": "owed", "w6d": "proof", "w7a": "eight",
}
H.setup(E, chapters=5)
vo, art, photo, band, wi, chapter, M = H.vo, H.art, H.photo, H.band, H.wi, H.chapter, H.M

S1 = "The We Company · Form S-1, SEC, 14 August 2019"
FC = "Fast Company · Katrina Brooker, 8 January 2019"
BW = "WeWork press release · Business Wire, 8 January 2019"
WR = "WeWork Newsroom · 24 September 2019"
SB = "WeWork and SoftBank joint release · 22 October 2019"
CC = "CNBC · Annie Palmer and Christine Wang, 23 October 2019"
CBS = "CBS This Morning · 25 May 2016"
NY = ("i-wework-ny.jpg", "WeWork, New York (2019) · photo: Ajay Suresh")
BA = ("i-wework-ba.jpg", "WeWork, Buenos Aires (2020) · photo: Hnapel")


# ================= COLD OPEN =================
E.pause(0.7, ["black"])
s = vo("w0a", [photo(*NY, [(0.5, 1.0), (0.5, 1.06)]), art("bw-47", BW, marks=[(1, wi("w0a", "forty-seven"))])], cuts=[wi("w0a", "SoftBank's")], gap=0.2)
E.stamp("January 2019", s, E.t - 0.1)
s = vo("w0b", [art("s1-lease", S1, marks=[(1, wi("w0b", "forty-seven"))])], gap=0.2)
E.stamp("August 2019", s, E.t - 0.1)
vo("w0c", [art("rw", "The We Company · Form RW, SEC, 30 September 2019", marks=[(1, wi("w0c", "withdrawn."))])], gap=0.6)
vo("w0d", ["black"], gap=0.8, kw=[(0, "From $47 billion|*to a failed IPO*.", "K")])
M["title"] = E.chapter("THE FALL", "WeWork", 4.6)

# ================= 1/5 THE PITCH =================
chapter(1, "The pitch")
vo("w1a", [band("wb-space", CBS), photo(*BA, [(0.5, 1.0), (0.5, 1.06)])], cuts=[wi("w1a", "rented")], gap=0.2)
s = vo("w1b", [photo("i-neumann-2015.jpg", "Adam Neumann, 2015 · photo: TechCrunch", [(0.35, 1.0), (0.33, 1.06)])], gap=0.2)
E.stamp("2016", s, E.t - 0.1)
E.quote("wq-wegen", "Adam Neumann · CBS This Morning, 25 May 2016", "auto:generation,money", gap=0.4, low="full")
vo("w1c", [photo("i-neumann-2015b.jpg", "Adam Neumann, 2015 · photo: TechCrunch", [(0.3, 1.0), (0.28, 1.06)])], gap=0.2)
E.quote("wq-community", "Adam Neumann · TechCrunch Disrupt NY, 15 May 2017", "auto:community", gap=0.4, low="full")
s = vo("w1d", [art("bw-47", BW, marks=[(0, wi("w1d", "six")), (1, wi("w1d", "forty-seven"))])], gap=0.3)
E.stamp("8 January 2019", s, E.t - 0.1)
vo("w1e", [art("fc-deal", FC, marks=[(0, wi("w1e", "twenty")), (1, wi("w1e", "fallen"))])], gap=0.3)
vo("w1f", [art("wc-mission", "WeWork Newsroom · 8 January 2019", marks=[(0, wi("w1f", "elevate"))])], gap=0.3)
vo("w1g", [art("fc-downturn", FC, marks=[(0, wi("w1g", "scary."))])], gap=0.2)
E.quote("wq-months", "Adam Neumann · CNBC, 10 January 2019", "auto:three,decision", gap=0.4, low="full")
s = vo("w1h", ["black"], gap=0.2, kw=[(wi("w1h", "Masayoshi"), "Masayoshi Son|*SoftBank*", "K")])
E.stamp("March 2019", s, E.t - 0.1)
E.quote("wq-son", "Masayoshi Son with David Faber · CNBC, 8 March 2019", "auto:losing,subscription", gap=1.0, low="full")

# ================= 2/5 THE FILING =================
chapter(2, "The filing")
s = vo("w2a", [photo(*NY, [(0.5, 1.06), (0.5, 1.12)]), art("s1-mission", S1, marks=[])], cuts=[wi("w2a", "filed")], gap=0.2)
E.stamp("14 August 2019", s, E.t - 0.1)
vo("w2b", [art("s1-mission", S1, marks=[(0, wi("w2b", "Elevate"))])], gap=0.3)
vo("w2c", [art("s1-losses", S1, marks=[(0, wi("w2c", "net")), (1, wi("w2c", "nine"))])], gap=0.3)
vo("w2d", ["black"], gap=0.4, kw=[(wi("w2d", "dollar"), "$1.93 spent|*per $1 of revenue*.", "K")])
vo("w2e", [art("s1-lease", S1, marks=[(0, wi("w2e", "fifteen")), (1, wi("w2e", "forty-seven"))])], gap=0.3)
vo("w2f", [art("s1-members", S1, marks=[(0, wi("w2f", "fifteen"))])], gap=0.3)
vo("w2g", ["black"], gap=1.0, kw=[(0, "15 years owed.|*15 months promised*.", "K")])

# ================= 3/5 THE FINE PRINT =================
chapter(3, "The fine print")
vo("w3a", [art("s1-votes", S1, marks=[(0, wi("w3a", "twenty")), (1, wi("w3a", "majority"))])], gap=0.3)
vo("w3b", [art("s1-leases4", S1, marks=[(0, wi("w3b", "four"))])], gap=0.3)
vo("w3c", [art("s1-tm", S1, marks=[(0, wi("w3c", "partnership")), (1, wi("w3c", "five"))])], gap=0.3)
vo("w3d", [art("a1-unwound", "The We Company · S-1 Amendment No. 1, SEC, September 2019", marks=[(0, wi("w3d", "unwound,"))])], gap=0.3)
vo("w3e", [art("s1-credit", S1, marks=[(0, wi("w3e", "personal"))])], gap=0.3)
s = vo("w3f", [art("a2-votes", "The We Company · S-1 Amendment No. 2, SEC, 13 September 2019", marks=[(1, wi("w3f", "twenty")), (0, wi("w3f", "market"))])], gap=1.0)
E.stamp("13 September 2019", s, E.t - 0.1)

# ================= 4/5 THE FALL =================
chapter(4, "Six days")
s = vo("w4a", [art("ld-step", WR, marks=[(0, wi("w4a", "stepped"))]), art("cs-charge", "CNBC · Lauren Feiner, 24 September 2019", marks=[(0, wi("w4a", "charge"))])],
       cuts=[wi("w4a", "CNBC")], gap=0.2)
E.stamp("24 September 2019", s, E.t - 0.1)
vo("w4b", [art("ld-scrutiny", WR, marks=[(0, wi("w4b", "scrutiny"))])], gap=0.3)
s = vo("w4c", [art("rw", "The We Company · Form RW, SEC, 30 September 2019", marks=[(0, wi("w4c", "withdrew")), (1, wi("w4c", "IPO"))])], gap=0.4)
E.stamp("30 September 2019", s, E.t - 0.1)
s = vo("w4d", [art("sb-rescue", SB, marks=[(0, wi("w4d", "Five")), (1, wi("w4d", "three,")), (2, wi("w4d", "eighty"))])], gap=0.2)
E.stamp("October 2019", s, E.t - 0.1)
vo("w4e", [art("sb-observer", SB, marks=[(0, wi("w4e", "observer."))]), art("cc-8b", CC, marks=[(0, wi("w4e", "eight"))])], cuts=[wi("w4e", "According")], gap=0.3)
vo("w4f", [art("cc-17", CC, marks=[(0, wi("w4f", "one"))])], gap=0.3)
s = vo("w4g", [art("cj-son", "CNBC · Reuters, 6 November 2019", marks=[(0, wi("w4g", "judgment"))])], gap=0.2)
E.stamp("6 November 2019", s, E.t - 0.1)
E.quote("wq-bloomberg", "Bloomberg Television · 6 November 2019", "auto:implosion,eight", gap=1.0, low="full")

# ================= 5/5 THE LONG TAIL =================
chapter(5, "The long tail")
M["rehook"] = E.t
s = vo("w5a", [photo(*BA, [(0.5, 1.06), (0.5, 1.12)]), art("bx-9b", "WeWork Newsroom · 26 March 2021", marks=[(0, wi("w5a", "nine"))])], cuts=[wi("w5a", "by")], gap=0.2)
E.stamp("October 2021", s, E.t - 0.1)
vo("w5b", [photo("i-neumann-2015.jpg", "Adam Neumann, 2015 · photo: TechCrunch", [(0.3, 1.08), (0.3, 1.14)])], gap=0.2)
E.quote("wq-regrets", "Adam Neumann · DealBook Summit, The New York Times, 9 November 2021", "auto:lessons,regrets", gap=0.4, low="full")
s = vo("w5c", [art("q-doubt", "WeWork Inc. · Form 10-Q, SEC, 8 August 2023", marks=[(0, wi("w5c", "substantial"))])], gap=0.3)
E.stamp("August 2023", s, E.t - 0.1)
s = vo("w5d", [art("ch11", "WeWork Inc. · Form 8-K, SEC, 6 November 2023", marks=[(0, wi("w5d", "Chapter")), (1, wi("w5d", "US"))])], gap=0.3)
E.stamp("6 November 2023", s, E.t - 0.1)
s = vo("w5e", [art("em-cancel", "WeWork Inc. · Form 8-K, SEC, 12 June 2024", marks=[(0, wi("w5e", "June")), (1, wi("w5e", "cancelled."))])], gap=0.8)
E.stamp("June 2024", s, E.t - 0.1)
vo("w5f", ["black"], gap=1.2, kw=[(0, "Tomorrow: *Dropbox*", "K")])

# ================= THE LESSON =================
M["lesson"] = E.chapter("", "What to take from it", 3.4)
vo("w6a", [art("s1-losses", S1, marks=[(0, wi("w6a", "problem"))])], gap=0.6)
vo("w6b", ["black"], gap=0.3, kw=[(0, "1. Know what a dollar|*of revenue costs you*.", "K")])
E.quote("wq-choose", "Adam Neumann · TechCrunch Disrupt NY, 15 May 2017", "auto:choose,profitable", gap=0.6, low="full")
vo("w6c", ["black"], gap=0.3, kw=[(0, "2. Match what you owe|*with what you're owed*.", "K")])
E.quote("wq-bosa", "Deirdre Bosa · CNBC, 7 November 2023 · photo: WeWork London, Robert Lamb", "auto:leases,risky", gap=0.6, low="full")
vo("w6d", ["black"], gap=0.8, kw=[(0, "3. A valuation is a price.|*Not proof*.", "K")])
E.checklist("What to take from it", ["Know what each dollar of revenue costs you.", "Match how long you owe with how long you are owed.",
                                     "A valuation is a price someone paid, not proof the business works."], 4.4)

# ================= CLOSE =================
M["close"] = E.t
vo("w7a", [art("bw-47", BW, marks=[(1, wi("w7a", "forty-seven"))]), art("cc-8b", CC, marks=[(0, wi("w7a", "eight"))])], cuts=[wi("w7a", "Roughly")], gap=0.2)
a = E.t
E.pause(2.6, ["black"])
E.key("$47 billion.|*Then the math*.", a, E.t - 0.1, "K")
E.endcard(4.6, "Find your people. hackyard.org")

# ================= MUSIC (tracks not included: put your own in media/bgm and change the names) =================
END = E.t
M["l0"] = M["lesson"]
b1 = min(M["c2"] + 1.5, 150.0)
b2 = min(M["rehook"] + 1.0, b1 + 175.0)
b3 = M["l0"] + 1.0
assert b3 - b2 + 1.0 <= 176.0 and END - b3 + 2.0 <= 107.0, (b1, b2, b3, END)
E.music("m-ec14c91b.mp3", 0.0, b1, 0.0, 0.11, fade_in=2.0, fade_out=2.0)
E.music("m-cb0b7d7e.mp3", b1 - 2.0, b2, 0.0, 0.09, fade_in=1.5, fade_out=1.5, lane=1)
E.music("m-78d68d14.mp3", b2 - 1.0, b3, 0.0, 0.09, fade_in=1.0, fade_out=2.0)
E.music("m-e9f8d56b.mp3" if END - b3 + 2.0 <= 83.0 else "m-a73bae6d.mp3", b3 - 2.0, END,
        round(max(0.0, (83.0 if END - b3 + 2.0 <= 83.0 else 107.0) - (END - b3 + 2.0) - 0.3), 3), 0.12, fade_in=2.0, fade_out=4.0, lane=1)
E.write("The Fall: WeWork", vertical=False)
E.write_srt(ROOT / "renders" / "wework.en.srt")
print({k: f"{int(v // 60)}:{v % 60:04.1f}" for k, v in M.items()}, "end", f"{int(END // 60)}:{END % 60:04.1f}")
