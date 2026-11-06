#!/usr/bin/env python3
"""Excerpt pages for this film's documents. Run from the repo root: python3 films/<slug>/edit/pages.py"""
import pathlib
import sys

FILM = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FILM.parents[1] / "tools" / "sources"))
from pages import Pages  # noqa: E402

P = Pages(FILM, FILM.name[:6])
# P.page(name, masthead, date, headline, byline, [paragraphs, "…" for a gap], marks=[exact phrases to sweep])
P.page("example", "Outlet · Document type", "1 January 2020", "Real headline", "Byline",
       ["A real sentence from the source, quoted exactly.", "…", "Another exact sentence with the number 47.2 in it."],
       marks=["the number 47.2"])
P.capture()
