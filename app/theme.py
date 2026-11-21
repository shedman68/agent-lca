"""Look and feel of app v2 (R9): ALTYCA's case-slide palette, Manrope, one idea per screen.

Presentation only: no figure is computed here. Every number shown through these helpers is passed in by app.py,
which reads it from app/data.py (out/ and measures/).
Colours: near-black #0d0f12, cards #16191e, teal #00cc99 = good / PASS, pink #f84aa7 = refused / needs a human.
Manrope (SIL Open Font License, app/fonts/OFL-Manrope.txt) is embedded so the demo runs offline.
"""
from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

import streamlit as st

LIGHT_KEY = "light_mode"
STORY_KEY = "story_mode"

TOKENS = {
    "dark": {"bg": "#0d0f12", "card": "#16191e", "card2": "#1c2026", "line": "#262b33", "ink": "#f2f4f5",
             "ink2": "#c4cad1", "muted": "#9aa3ad", "teal": "#00cc99", "teal_ink": "#00cc99", "pink": "#f84aa7",
             "pink_bg": "#2a1421", "teal_bg": "#0f2a23", "on_teal": "#0d0f12",
             "glow": "radial-gradient(1200px 600px at 85% -10%, rgba(0,204,153,.10), transparent 60%),"
                     "radial-gradient(900px 500px at -10% 110%, rgba(248,74,167,.06), transparent 60%)"},
    "light": {"bg": "#f6f7f8", "card": "#ffffff", "card2": "#f0f2f4", "line": "#dde1e6", "ink": "#0d0f12",
              "ink2": "#2d3640", "muted": "#4b5560", "teal": "#00cc99", "teal_ink": "#00785a", "pink": "#c4157a",
              "pink_bg": "#fdeaf4", "teal_bg": "#e3f7f0", "on_teal": "#0d0f12",
              "glow": "radial-gradient(1200px 600px at 85% -10%, rgba(0,204,153,.10), transparent 60%)"},
}
FONT = "Manrope, system-ui, -apple-system, Segoe UI, sans-serif"


def is_light() -> bool:
    try:
        return bool(st.session_state.get(LIGHT_KEY, False))
    except Exception:
        return False


def t() -> dict:
    return TOKENS["light" if is_light() else "dark"]


@lru_cache(maxsize=1)
def _font_b64() -> str:
    path = Path(__file__).resolve().parent / "fonts" / "manrope-latin-wght-normal.woff2"
    return base64.b64encode(path.read_bytes()).decode() if path.exists() else ""


def inject() -> None:
    """Global CSS: font, tokens, hidden Streamlit chrome, type scale, components. Call once per run."""
    k = t()
    font = _font_b64()
    face = (f"@font-face{{font-family:Manrope;src:url(data:font/woff2;base64,{font}) format('woff2');"
            "font-weight:200 800;font-style:normal;font-display:swap;}") if font else ""
    st.markdown(f"""<style>
{face}
:root{{--bg:{k['bg']};--card:{k['card']};--card2:{k['card2']};--line:{k['line']};--ink:{k['ink']};--ink2:{k['ink2']};
--muted:{k['muted']};--teal:{k['teal']};--teal-ink:{k['teal_ink']};--pink:{k['pink']};--pink-bg:{k['pink_bg']};
--teal-bg:{k['teal_bg']};--on-teal:{k['on_teal']};}}
html,body,.stApp,.stApp p,.stApp li,.stApp label,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp button,.stApp input,
.stApp textarea,.stMarkdown,[data-testid="stSidebar"] a,[data-testid="stSidebar"] p{{font-family:{FONT} !important;}}
[data-testid="stIconMaterial"],.material-symbols-rounded{{font-family:"Material Symbols Rounded" !important;}}
.gx-refuse{{background:var(--pink-bg);border:1px solid var(--pink);border-radius:14px;padding:14px 18px;color:var(--ink);font-size:17px;}}
.gx-refuse b{{color:var(--pink);}}
.stApp{{background:{k['glow']},var(--bg) !important;color:var(--ink);}}
[data-testid="stSidebar"]{{background:var(--card) !important;border-right:1px solid var(--line);}}
[data-testid="stSidebar"] *{{color:var(--ink2);}}
.stApp p,.stApp li,.stApp label,.stApp span{{color:inherit;}}
.stMarkdown p,.stMarkdown li{{color:var(--ink2);font-size:17px;line-height:1.55;}}
[data-testid="stCaptionContainer"] p{{color:var(--muted) !important;font-size:15px;}}
h1,h2,h3{{color:var(--ink) !important;letter-spacing:-.025em;}}
h1{{font-size:13px !important;letter-spacing:.14em !important;text-transform:uppercase;font-weight:800 !important;
color:var(--teal-ink) !important;padding:0 !important;margin:0 0 10px !important;}}
h2{{font-size:1.45rem !important;font-weight:700 !important;margin-top:2.2rem !important;}}
h3{{font-size:1.15rem !important;font-weight:700 !important;}}
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],
.stDeployButton,[data-testid="stAppDeployButton"]{{display:none !important;visibility:hidden !important;}}
header[data-testid="stHeader"]{{background:transparent !important;}}
.block-container{{max-width:1120px;padding-top:2.2rem;padding-bottom:4rem;}}
[data-testid="stExpander"] details{{background:var(--card);border:1px solid var(--line);border-radius:14px;}}
[data-testid="stExpander"] summary p{{font-weight:650;color:var(--ink) !important;}}
.stButton>button,.stLinkButton>a,[data-testid="stPageLink"] a{{min-height:44px;border-radius:12px;font-weight:650;}}
.stButton>button[kind="primary"]{{background:var(--teal);color:var(--on-teal);border:0;}}
.stButton>button[kind="secondary"]{{background:var(--card);color:var(--ink);border:1px solid var(--line);}}
.gx-eyebrow{{font-size:13px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;color:var(--teal-ink);margin:0 0 10px;}}
.gx-hero{{font-size:clamp(30px,4.4vw,52px);line-height:1.08;font-weight:800;letter-spacing:-.035em;color:var(--ink);margin:0 0 14px;max-width:22ch;}}
.gx-hero em{{font-style:normal;color:var(--teal-ink);}}
.gx-sub{{font-size:19px;line-height:1.5;color:var(--ink2);max-width:60ch;margin:0 0 26px;}}
.gx-kpis{{display:flex;flex-wrap:wrap;gap:14px;margin:8px 0 26px;}}
.gx-kpi{{flex:1 1 220px;min-width:min(200px,100%);}}
.gx-kpi .v{{font-size:clamp(34px,4vw,48px);font-weight:800;letter-spacing:-.04em;line-height:1;color:var(--ink);font-variant-numeric:tabular-nums;}}
.gx-kpi .u{{font-size:17px;font-weight:700;color:var(--muted);margin-left:6px;letter-spacing:0;}}
.gx-kpi .l{{font-size:14px;color:var(--muted);margin-top:8px;font-weight:600;}}
.gx-kpi.good .v{{color:var(--teal-ink);}}
.gx-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));gap:14px;margin:6px 0 22px;}}
.gx-card{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px 22px;}}
.gx-card h4{{margin:0 0 8px;font-size:18px;font-weight:750;color:var(--ink);letter-spacing:-.01em;}}
.gx-card p{{margin:0;font-size:15.5px;line-height:1.5;color:var(--ink2);}}
.gx-card .n{{font-size:28px;font-weight:800;letter-spacing:-.03em;color:var(--ink);font-variant-numeric:tabular-nums;margin-top:14px;}}
.gx-card .n span{{font-size:15px;font-weight:700;color:var(--muted);margin-left:4px;letter-spacing:0;}}
.gx-card .meta{{font-size:13.5px;color:var(--muted);margin-top:10px;font-weight:600;}}
.gx-card .k{{font-size:12.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:700;margin:0 0 8px;}}
.gx-card.accent{{border-color:var(--teal);}}
.gx-card.pink{{border-color:var(--pink);background:var(--pink-bg);}}
.gx-card.pink h4{{color:var(--pink);}}
.gx-pill{{display:inline-block;padding:3px 12px;border-radius:999px;font-size:13px;font-weight:750;letter-spacing:.02em;}}
.gx-pill.good{{background:var(--teal-bg);color:var(--teal-ink);}}
.gx-pill.pink{{background:var(--pink-bg);color:var(--pink);}}
.gx-pill.muted{{background:var(--card2);color:var(--muted);}}
.gx-story{{display:flex;align-items:center;gap:14px;margin:0 0 26px;}}
.gx-story .bar{{flex:1;height:4px;border-radius:2px;background:var(--line);overflow:hidden;}}
.gx-story .bar i{{display:block;height:100%;background:var(--teal);}}
.gx-story .s{{font-size:13px;font-weight:700;color:var(--muted);letter-spacing:.08em;text-transform:uppercase;white-space:nowrap;}}
.gx-foot{{border-top:1px solid var(--line);margin-top:40px;padding-top:18px;font-size:14px;color:var(--muted);}}
@media (prefers-reduced-motion:no-preference){{.gx-hero,.gx-kpis,.gx-grid{{animation:gxin .35s ease-out both;}}}}
@keyframes gxin{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
@media (max-width:720px){{.block-container{{padding-left:16px;padding-right:16px;padding-top:1.2rem;}}
.gx-sub{{font-size:17px;}} [data-testid="stSidebar"]{{min-width:0 !important;}}}}
</style>""", unsafe_allow_html=True)


def hero(eyebrow: str, line: str, sub: str = "") -> None:
    """One summary line in big type. `line` may wrap a phrase in <em> for the accent colour."""
    sub_html = f'<p class="gx-sub">{sub}</p>' if sub else ""
    eye = f'<p class="gx-eyebrow">{eyebrow}</p>' if eyebrow else ""
    st.html(f'<div>{eye}<p class="gx-hero">{line}</p>{sub_html}</div>')


def kpis(items: list[tuple[str, str, str]], good: set[int] | None = None) -> None:
    """At most three or four key numbers: (value, unit, label)."""
    good = good or set()
    cells = "".join(
        f'<div class="gx-kpi{" good" if i in good else ""}"><div class="v">{v}<span class="u">{u}</span></div>'
        f'<div class="l">{lbl}</div></div>' for i, (v, u, lbl) in enumerate(items))
    st.html(f'<div class="gx-kpis">{cells}</div>')


def card(title: str, body: str = "", number: str = "", unit: str = "", meta: str = "", kind: str = "",
         kicker: str = "") -> str:
    k = f'<p class="k">{kicker}</p>' if kicker else ""
    n = f'<div class="n">{number}<span>{unit}</span></div>' if number else ""
    m = f'<div class="meta">{meta}</div>' if meta else ""
    b = f"<p>{body}</p>" if body else ""
    return f'<div class="gx-card {kind}">{k}<h4>{title}</h4>{b}{n}{m}</div>'


def grid(cards: list[str]) -> None:
    st.html(f'<div class="gx-grid">{"".join(cards)}</div>')


def story_bar(step: int, total: int, label: str) -> None:
    pct = int(round(100 * step / total))
    st.html(f'<div class="gx-story" role="progressbar" aria-valuenow="{step}" aria-valuemin="0" aria-valuemax="{total}" '
            f'aria-label="Story progress"><span class="s">Step {step} of {total}</span>'
            f'<div class="bar"><i style="width:{pct}%"></i></div><span class="s">{label}</span></div>')
