"""Visuals for app v2 (R9): drawn as SVG, offline, no stock photos. Data-driven where they show numbers.

Embedded as <img src="data:image/svg+xml;base64,…"> because Streamlit's HTML sanitiser strips inline <svg>.
Every number drawn here is passed in by app.py from app/data.py.
"""
from __future__ import annotations

import base64

TEAL, PINK, INK, MUTED, LINE = "#00cc99", "#f84aa7", "#f2f4f5", "#9aa3ad", "#2a3039"
FONT = "Manrope, system-ui, sans-serif"


def _img(svg: str, alt: str, max_w: str = "100%") -> str:
    b64 = base64.b64encode(svg.encode("utf-8")).decode()
    return (f'<img src="data:image/svg+xml;base64,{b64}" alt="{alt}" '
            f'style="width:100%;max-width:{max_w};height:auto;display:block;margin:4px 0 18px">')


def lifecycle(today: str = "Use", phases: tuple[str, ...] = ("Materials", "Build", "Use", "End of life"),
              light: bool = False) -> str:
    """A thin orbit with four life-cycle phases. The phase we measure today is lit; the rest is 'next'."""
    ink, muted, line = ("#0d0f12", "#4b5560", "#d4d9df") if light else (INK, MUTED, LINE)
    cx, cy, r = 260, 200, 150
    pos = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    anchors = ["middle", "start", "middle", "end"]
    offs = [(0, -22), (22, 6), (0, 34), (-22, 6)]
    nodes = []
    for (x, y), name, anc, (dx, dy) in zip(pos, phases, anchors, offs):
        lit = name == today
        nodes.append(
            f'<circle cx="{x}" cy="{y}" r="{11 if lit else 7}" fill="{TEAL if lit else "none"}" '
            f'stroke="{TEAL if lit else muted}" stroke-width="2"/>'
            + (f'<circle cx="{x}" cy="{y}" r="24" fill="{TEAL}" opacity=".18"/>' if lit else "")
            + f'<text x="{x + dx}" y="{y + dy}" text-anchor="{anc}" font-family="{FONT}" font-size="17" '
              f'font-weight="{800 if lit else 600}" fill="{TEAL if lit else muted}">{name}'
              f'{" · today" if lit else ""}</text>')
    # lit arc: the quarter around 'Use' (bottom)
    arc = (f'<path d="M {cx + r * 0.707:.1f} {cy + r * 0.707:.1f} A {r} {r} 0 0 1 {cx - r * 0.707:.1f} {cy + r * 0.707:.1f}" '
           f'fill="none" stroke="{TEAL}" stroke-width="4" stroke-linecap="round"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 420" role="img">'
           f'<defs><radialGradient id="g" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{TEAL}" stop-opacity=".16"/>'
           f'<stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></radialGradient></defs>'
           f'<circle cx="{cx}" cy="{cy}" r="{r + 40}" fill="url(#g)"/>'
           f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{line}" stroke-width="2" stroke-dasharray="2 7"/>'
           f'{arc}{"".join(nodes)}'
           f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" font-family="{FONT}" font-size="30" font-weight="800" '
           f'fill="{ink}">Digital</text><text x="{cx}" y="{cy + 26}" text-anchor="middle" font-family="{FONT}" '
           f'font-size="15" font-weight="600" fill="{muted}">footprint of an SME</text></svg>')
    return _img(svg, "Life cycle: materials, build, use (measured today), end of life", "460px")


# Stylised positions (not to scale) in a 900 x 460 frame: Basel is the decision point.
_PLACES = {"Basel": (470, 330), "Switzerland": (700, 380), "Germany": (560, 120), "Ireland": (150, 170)}
_CITY = {"Switzerland": "Zurich", "Germany": "Frankfurt", "Ireland": "Dublin"}
_LABEL = {"Switzerland": (30, 8, "start"), "Germany": (30, 8, "start"), "Ireland": (0, -48, "middle")}


def basel_map(shares: dict[str, float], light: bool = False) -> str:
    """Decisions in Basel, electricity in Zurich, Frankfurt and Dublin. Line weight = share of CO2 (passed in)."""
    ink, muted, line = ("#0d0f12", "#4b5560", "#d4d9df") if light else (INK, MUTED, LINE)
    bx, by = _PLACES["Basel"]
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="1.6" fill="{line}"/>'
                   for x in range(30, 900, 26) for y in range(30, 460, 26))
    arcs, labels = [], []
    for country, (x, y) in _PLACES.items():
        if country == "Basel" or country not in shares:
            continue
        sh = shares[country]
        dx, dy = x - bx, y - by
        mx, my = (bx + x) / 2 - dy * 0.22, (by + y) / 2 + dx * 0.22  # bow sideways, away from the labels
        arcs.append(f'<path d="M {bx} {by} Q {mx:.0f} {my:.0f} {x} {y}" fill="none" stroke="{TEAL}" stroke-opacity=".9" '
                    f'stroke-width="{2 + 16 * sh:.1f}" stroke-linecap="round"/>')
        ox, oy, anc = _LABEL[country]
        labels.append(
            f'<circle cx="{x}" cy="{y}" r="22" fill="{TEAL}" opacity=".15"/><circle cx="{x}" cy="{y}" r="9" fill="{TEAL}"/>'
            f'<text x="{x + ox}" y="{y + oy}" text-anchor="{anc}" font-family="{FONT}" font-size="32" font-weight="800" '
            f'fill="{ink}">{sh * 100:.0f} %</text>'
            f'<text x="{x + ox}" y="{y + oy + 24}" text-anchor="{anc}" font-family="{FONT}" font-size="16" font-weight="700" '
            f'fill="{muted}">{_CITY[country]} · {country}</text>')
    basel = (f'<circle cx="{bx}" cy="{by}" r="12" fill="{ink}"/>'
             f'<text x="{bx - 22}" y="{by + 7}" text-anchor="end" font-family="{FONT}" font-size="20" font-weight="800" '
             f'fill="{ink}">Basel</text><text x="{bx - 22}" y="{by + 30}" text-anchor="end" font-family="{FONT}" '
             f'font-size="15" font-weight="600" fill="{muted}">decisions</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 460" role="img">{dots}{"".join(arcs)}'
           f'{"".join(labels)}{basel}'
           f'<text x="30" y="440" font-family="{FONT}" font-size="14" font-weight="600" fill="{muted}">Share of CO2 by '
           f'data-centre country · not to scale</text></svg>')
    alt = "Share of CO2 by data-centre country: " + ", ".join(f"{_CITY[c]} {v * 100:.0f} %" for c, v in shares.items()
                                                               if c in _CITY)
    return _img(svg, alt, "900px")
