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


def lifecycle(today: str = "Use", phases: tuple[str, ...] = ("Materials", "Build", "Use", "End of use / life"),
              light: bool = False) -> str:
    """A thin orbit with four life-cycle phases. The phase we measure today is lit. A light travels clockwise
    Materials → Build → Use → End of use / life and each label brightens as it passes (SMIL inside the SVG;
    hidden under reduced motion)."""
    ink, muted, line = ("#0d0f12", "#4b5560", "#d4d9df") if light else (INK, MUTED, LINE)
    cx, cy, r = 300, 200, 150
    pos = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    anchors = ["middle", "start", "middle", "end"]
    offs = [(0, -22), (22, 6), (0, 34), (-22, 6)]
    period = 8.0  # seconds for one turn; each phase gets a quarter
    nodes = []
    for i, ((x, y), name, anc, (dx, dy)) in enumerate(zip(pos, phases, anchors, offs)):
        lit = name == today
        base = TEAL if lit else muted
        # the label brightens while the light is near its phase (a quarter turn around it)
        t0 = i / 4
        keys = sorted({0.0, max(0.0, t0 - 0.06), t0, min(1.0, t0 + 0.12), 1.0})
        vals = [TEAL if abs(k - t0) < 1e-9 else base for k in keys]
        if t0 == 0:  # Materials sits at the start (and end) of the loop
            keys, vals = [0.0, 0.12, 0.94, 1.0], [TEAL, base, base, TEAL]
        anim = (f'<animate class="lt" attributeName="fill" dur="{period}s" repeatCount="indefinite" '
                f'keyTimes="{";".join(f"{k:.3f}" for k in keys)}" values="{";".join(vals)}"/>')
        nodes.append(
            f'<circle cx="{x}" cy="{y}" r="{11 if lit else 7}" fill="{TEAL if lit else "none"}" '
            f'stroke="{TEAL if lit else muted}" stroke-width="2"/>'
            + (f'<circle cx="{x}" cy="{y}" r="24" fill="{TEAL}" opacity=".18"/>' if lit else "")
            + f'<text x="{x + dx}" y="{y + dy}" text-anchor="{anc}" font-family="{FONT}" font-size="17" '
              f'font-weight="{800 if lit else 600}" fill="{base}">{name}{" · today" if lit else ""}{anim}</text>')
    # lit arc: the quarter around 'Use' (bottom)
    arc = (f'<path d="M {cx + r * 0.707:.1f} {cy + r * 0.707:.1f} A {r} {r} 0 0 1 {cx - r * 0.707:.1f} {cy + r * 0.707:.1f}" '
           f'fill="none" stroke="{TEAL}" stroke-width="4" stroke-linecap="round"/>')
    orbit = f"M {cx} {cy - r} A {r} {r} 0 1 1 {cx} {cy + r} A {r} {r} 0 1 1 {cx} {cy - r}"  # clockwise from the top
    glow = (f'<g class="light"><circle r="22" fill="{TEAL}" opacity=".22"/><circle r="12" fill="{TEAL}" opacity=".45"/>'
            f'<circle r="6" fill="#ffffff"/>'
            f'<animateMotion dur="{period}s" repeatCount="indefinite" path="{orbit}"/></g>')
    css = "<style>@media (prefers-reduced-motion:reduce){.light{display:none}}</style>"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 420" role="img">{css}'
           f'<defs><radialGradient id="g" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{TEAL}" stop-opacity=".16"/>'
           f'<stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></radialGradient></defs>'
           f'<circle cx="{cx}" cy="{cy}" r="{r + 40}" fill="url(#g)"/>'
           f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{line}" stroke-width="2" stroke-dasharray="2 7"/>'
           f'{arc}{"".join(nodes)}{glow}'
           f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" font-family="{FONT}" font-size="30" font-weight="800" '
           f'fill="{ink}">Digital</text><text x="{cx}" y="{cy + 26}" text-anchor="middle" font-family="{FONT}" '
           f'font-size="15" font-weight="600" fill="{muted}">footprint of an SME</text></svg>')
    return _img(svg, "Life cycle: materials, build, use (measured today), end of use / life", "500px")


# Stylised positions (not to scale) in a 900 x 460 frame: Basel is the decision point.
_PLACES = {"Basel": (470, 330), "Switzerland": (700, 380), "Germany": (560, 120), "Ireland": (150, 170)}
_CITY = {"Switzerland": "Zurich", "Germany": "Frankfurt", "Ireland": "Dublin"}
_LABEL = {"Switzerland": (30, 8, "start"), "Germany": (30, 8, "start"), "Ireland": (0, -48, "middle")}


def basel_map(shares: dict[str, float], light: bool = False) -> str:
    """Decisions in Basel, electricity in Zurich, Frankfurt and Dublin. Line weight = share of CO₂ (passed in)."""
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
        # Flow: light dashes run from each data centre to Basel (the footprint lands where decisions are made).
        arcs.append(f'<path class="flow" d="M {bx} {by} Q {mx:.0f} {my:.0f} {x} {y}" fill="none" stroke="#ffffff" '
                    f'stroke-opacity=".55" stroke-width="{max(1.5, (2 + 16 * sh) * 0.35):.1f}" stroke-linecap="round" '
                    f'stroke-dasharray="2 22"/>')
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
    flow_css = ("<style>.flow{animation:gxflow 1.4s linear infinite}@keyframes gxflow{to{stroke-dashoffset:24}}"
                "@media (prefers-reduced-motion:reduce){.flow{animation:none;display:none}}</style>")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 460" role="img">{flow_css}{dots}{"".join(arcs)}'
           f'{"".join(labels)}{basel}'
           f'<text x="30" y="440" font-family="{FONT}" font-size="14" font-weight="600" fill="{muted}">Share of CO₂ by '
           f'data-centre country · not to scale</text></svg>')
    alt = "Share of CO₂ by data-centre country: " + ", ".join(f"{_CITY[c]} {v * 100:.0f} %" for c, v in shares.items()
                                                               if c in _CITY)
    return _img(svg, alt, "900px")


def next_year_chart(labels: list[str], without_t: list[float], with_t: list[float], light: bool = False,
                    note: str = "") -> str:
    """Cumulative t CO₂ over the next 12 months, without and with the plan. Lines draw themselves (CSS in the SVG,
    off under reduced motion); the gap between them fills in after. Values are passed in, nothing is computed here."""
    ink, muted, line = ("#0d0f12", "#4b5560", "#d4d9df") if light else (INK, MUTED, LINE)
    grey = "#8b95a1" if not light else "#6b7480"
    stat = "#8a6400" if light else "#ffd166"
    w, h, l, r, t, b = 900, 360, 70, 150, 30, 50
    top = max(without_t) * 1.08 if without_t and max(without_t) > 0 else 1.0
    n = len(labels)
    X = lambda i: l + (w - l - r) * (i / max(1, n - 1))
    Y = lambda v: t + (h - t - b) * (1 - v / top)
    pts = lambda vals: " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
    area = (f"M {X(0):.1f},{Y(without_t[0]):.1f} " + " ".join(f"L {X(i):.1f},{Y(v):.1f}" for i, v in enumerate(without_t))
            + " " + " ".join(f"L {X(i):.1f},{Y(v):.1f}" for i, v in reversed(list(enumerate(with_t)))) + " Z")
    grid = "".join(f'<line x1="{l}" x2="{w - r}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{line}" stroke-width="1"/>'
                   f'<text x="{l - 10}" y="{Y(v) + 5:.1f}" text-anchor="end" font-family="{FONT}" font-size="14" fill="{muted}">{v:g} t</text>'
                   for v in _ticks(top))
    xl = "".join(f'<text x="{X(i):.1f}" y="{h - b + 26}" text-anchor="middle" font-family="{FONT}" font-size="14" '
                 f'fill="{muted}">{lab}</text>' for i, lab in enumerate(labels))
    end = n - 1
    ends = (f'<text class="lab" x="{X(end) + 12:.1f}" y="{Y(without_t[end]) + 6:.1f}" font-family="{FONT}" font-size="22" '
            f'font-weight="800" fill="{stat}">{without_t[end]:.1f} t</text>'
            f'<text class="lab" x="{X(end) + 12:.1f}" y="{Y(without_t[end]) + 26:.1f}" font-family="{FONT}" font-size="14" '
            f'font-weight="700" fill="{grey}">without the plan</text>'
            f'<text class="lab" x="{X(end) + 12:.1f}" y="{Y(with_t[end]) + 6:.1f}" font-family="{FONT}" font-size="22" '
            f'font-weight="800" fill="{stat}">{with_t[end]:.1f} t</text>'
            f'<text class="lab" x="{X(end) + 12:.1f}" y="{Y(with_t[end]) + 26:.1f}" font-family="{FONT}" font-size="14" '
            f'font-weight="700" fill="{TEAL}">with the plan</text>')
    css = ("<style>.ln{stroke-dasharray:2000;stroke-dashoffset:0;animation:draw 2.2s cubic-bezier(.4,.1,.2,1) both}"
           ".gap{animation:fade .8s ease-out 1.6s both}.lab{animation:fade .6s ease-out 2s both}"
           "@keyframes draw{from{stroke-dashoffset:2000}}@keyframes fade{from{opacity:0}}"
           "@media (prefers-reduced-motion:reduce){.ln,.gap,.lab{animation:none}}</style>")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img">{css}{grid}{xl}'
           f'<path class="gap" d="{area}" fill="{TEAL}" fill-opacity=".14"/>'
           f'<polyline class="ln" points="{pts(without_t)}" fill="none" stroke="{grey}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
           f'<polyline class="ln" points="{pts(with_t)}" fill="none" stroke="{TEAL}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
           f'{ends}<text x="{l}" y="{h - 6}" font-family="{FONT}" font-size="13" fill="{muted}">{note}</text></svg>')
    alt = (f"Cumulative CO₂ next year: without the plan {without_t[-1]:.1f} t, with the plan {with_t[-1]:.1f} t."
           if without_t and with_t else "Next year chart")
    return _img(svg, alt, "900px")


def _ticks(top: float) -> list[float]:
    step = 1 if top <= 8 else 2 if top <= 16 else 5
    return [float(v) for v in range(0, int(top) + 1, step)]
