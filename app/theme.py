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


def apply() -> None:
    """Global look (Grok owns this file from R9 on): font, CSS variables, hidden Streamlit chrome, type scale.

    Contract used by app/ui.py: CSS variables --bg --card --card2 --line --ink --ink2 --muted --teal --teal-ink
    --pink --pink-bg --teal-bg --on-teal, and session_state["light_mode"] for the projector switch."""
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
@media (max-width:720px){{.block-container{{padding-left:16px;padding-right:16px;padding-top:1.2rem;}}
[data-testid="stSidebar"]{{min-width:0 !important;}}}}
</style>""", unsafe_allow_html=True)

