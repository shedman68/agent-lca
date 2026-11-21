"""Design system for the pitch app (R9). Grok owns this file.

Presentation only. Nothing here reads ``data/`` or computes a figure. ``kpi()`` prints
strings the page already loaded from ``out/`` or ``measures/``.

How a page turns the look on
----------------------------
Call ``apply()`` once, near the top of ``app.py``, before charts or page widgets::

    import theme

    theme.apply()                  # dark, unless the toggle or ?light=1 says otherwise
    theme.apply(light=True)        # force the projector (light) mode for this run
    theme.kpi("CO2 cut", value, delta, theme.TONE_GOOD)
    theme.kpi("Hand-over", label, None, theme.TONE_NEEDS_HUMAN)

The sidebar switch in ``app.py`` is already wired::

    st.toggle("Light mode (projector)", key=theme.LIGHT_KEY)

Open a projector link as ``/?light=1`` (also ``true``, ``yes``, ``on``). ``?light=0``
forces dark. Resolution order:

1. The ``light`` argument, when it is not ``None``, wins and is stored on the session.
2. Else ``st.session_state["light_mode"]`` wins (the toggle).
3. On the first visit only, the ``light`` query param seeds the session.
4. Default is dark.

``ui.py`` reads these CSS variables, with its own fallbacks if one is missing:
``--bg --card --card2 --line --ink --ink2 --muted --teal --teal-ink --pink
--pink-bg --teal-bg --on-teal``.

Colour
------
Dark: background ``#0d0f12``, cards ``#16191e``, text ``#f5f6f7``, teal ``#00cc99``
for good / PASS, pink ``#f84aa7`` only for a refusal or a needs-a-human hand-over.
Light (projector): same hues. Small teal and pink *type* steps down to ``#006b4f``
and ``#9d1458`` so it stays WCAG AA on white. Teal fills keep ``#00cc99`` with
near-black type. White on ``#00cc99`` is about 2.1:1 and is not used.

Measured contrast (WCAG AA is 4.5:1 for text, 3:1 for large type and UI marks):

- ``#f5f6f7`` on ``#0d0f12`` 17.7:1, on ``#16191e`` 16.3:1
- ``#00cc99`` on ``#0d0f12`` 9.2:1, on ``#16191e`` 8.5:1
- ``#f84aa7`` on ``#0d0f12`` 6.0:1, on ``#16191e`` 5.5:1
- ``#0d0f12`` on ``#00cc99`` 9.2:1 (button label)
- ``#006b4f`` on ``#f3f5f6`` 6.0:1, ``#9d1458`` on ``#f3f5f6`` 7.2:1
- ``#f84aa7`` on white is 3.2:1, so light mode uses it as a border, not as small type

Font
----
Manrope (SIL Open Font License, ``app/static/OFL-Manrope.txt``) is the variable
woff2 ``app/static/manrope-latin-wght-normal.woff2``. Streamlit serves it at
``/app/static/manrope-latin-wght-normal.woff2`` when ``[server] enableStaticServing``
is true. The same bytes are also inlined as a data URI so the demo stays offline
if static serving is off. No CDN and no Google Fonts.

Tones
-----
``TONE_GOOD`` and ``TONE_PASS`` use teal. ``TONE_REFUSAL`` and ``TONE_NEEDS_HUMAN``
use pink. ``TONE_NEUTRAL`` uses the ink colour. Pink is not a decoration.
"""
from __future__ import annotations

import base64
import html
from functools import lru_cache
from pathlib import Path

import streamlit as st

try:
    import i18n
except ImportError:  # imported as app.theme from the repo root
    from app import i18n

# Session key for the projector switch. app.py binds st.toggle(..., key=LIGHT_KEY).
LIGHT_KEY = "light_mode"

BG = "#0d0f12"
CARD = "#16191e"
INK = "#f5f6f7"
TEAL = "#00cc99"
PINK = "#f84aa7"

# Light-mode text steps. The brand swatches stay TEAL and PINK; these exist so
# small type clears WCAG AA on a white projector image.
TEAL_INK_LIGHT = "#006b4f"
PINK_INK_LIGHT = "#9d1458"

TONE_NEUTRAL = "neutral"
TONE_GOOD = "good"
TONE_PASS = "pass"
TONE_REFUSAL = "refusal"
TONE_NEEDS_HUMAN = "needs_human"
TONES = (TONE_NEUTRAL, TONE_GOOD, TONE_PASS, TONE_REFUSAL, TONE_NEEDS_HUMAN)
_PINK_TONES = frozenset({TONE_REFUSAL, TONE_NEEDS_HUMAN})
_TEAL_TONES = frozenset({TONE_GOOD, TONE_PASS})

_ON = frozenset({"1", "true", "yes", "on", "light"})
_OFF = frozenset({"0", "false", "no", "off", "dark"})

FONT_FILENAME = "manrope-latin-wght-normal.woff2"
FONT_URL = f"/app/static/{FONT_FILENAME}"
FONT = "Manrope, system-ui, -apple-system, Segoe UI, sans-serif"

TOKENS = {
    "dark": {
        "bg": BG,
        "card": CARD,
        "card2": "#1c2026",
        "line": "#2c333c",
        "ink": INK,
        "ink2": "#d5dbe1",
        "muted": "#b4bec8",
        "teal": TEAL,
        "teal_ink": TEAL,
        "pink": PINK,
        "pink_mark": PINK,
        "pink_bg": "#2a1421",
        "teal_bg": "#102821",
        "on_teal": BG,
        "glow": (
            "radial-gradient(880px 420px at 100% -12%, rgba(0,204,153,.13), transparent 58%),"
            "radial-gradient(640px 380px at -12% 108%, rgba(0,204,153,.05), transparent 52%)"
        ),
    },
    "light": {
        "bg": "#f3f5f6",
        "card": "#ffffff",
        "card2": "#e7ebef",
        "line": "#c5ced6",
        "ink": BG,
        "ink2": "#24303a",
        "muted": "#3a4450",
        "teal": TEAL,
        "teal_ink": TEAL_INK_LIGHT,
        "pink": PINK_INK_LIGHT,
        "pink_mark": PINK,
        "pink_bg": "#fde7f3",
        "teal_bg": "#e5f7f1",
        "on_teal": BG,
        "glow": (
            "radial-gradient(880px 420px at 100% -12%, rgba(0,204,153,.16), transparent 58%),"
            "radial-gradient(640px 360px at -8% 110%, rgba(0,204,153,.06), transparent 50%)"
        ),
    },
}


def _query_light() -> bool | None:
    """Return True/False when ``?light=`` is set, else None. Never raises."""
    try:
        qp = st.query_params
    except Exception:
        return None
    if "light" not in qp:
        return None
    raw = str(qp.get("light", "")).strip().lower()
    if raw in _ON or raw == "":
        return True
    if raw in _OFF:
        return False
    return None


def _store(value: bool) -> None:
    try:
        st.session_state[LIGHT_KEY] = value
    except Exception:
        pass


def resolve_light(light: bool | None = None) -> bool:
    """The mode ``apply`` will paint. See the module docstring for the order."""
    if light is not None:
        _store(bool(light))
        return bool(light)
    try:
        if LIGHT_KEY in st.session_state:
            return bool(st.session_state[LIGHT_KEY])
    except Exception:
        return False
    seeded = _query_light()
    if seeded is not None:
        _store(seeded)
        return seeded
    return False


def is_light() -> bool:
    try:
        if LIGHT_KEY in st.session_state:
            return bool(st.session_state[LIGHT_KEY])
    except Exception:
        return False
    return bool(_query_light())


def t() -> dict:
    return TOKENS["light" if is_light() else "dark"]


def tone_color(tone: str) -> str:
    """CSS colour for a tone. Pink only for a refusal or a needs-a-human hand-over."""
    k = t()
    if tone in _PINK_TONES:
        return k["pink"]
    if tone in _TEAL_TONES:
        return k["teal_ink"]
    return k["ink"]


def _font_path() -> Path | None:
    root = Path(__file__).resolve().parent
    for rel in (f"static/{FONT_FILENAME}", f"fonts/{FONT_FILENAME}"):
        path = root / rel
        if path.is_file():
            return path
    return None


@lru_cache(maxsize=1)
def _font_face() -> str:
    path = _font_path()
    if path is None:
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return (
        "@font-face{font-family:Manrope;font-style:normal;font-weight:200 800;font-display:swap;"
        f"src:url({FONT_URL}) format('woff2'),"
        f"url(data:font/woff2;base64,{encoded}) format('woff2');}}"
    )


def _css(k: dict) -> str:
    face = _font_face()
    return f"""<style>
{face}
:root{{--bg:{k['bg']};--card:{k['card']};--card2:{k['card2']};--line:{k['line']};--ink:{k['ink']};--ink2:{k['ink2']};
--muted:{k['muted']};--teal:{k['teal']};--teal-ink:{k['teal_ink']};--pink:{k['pink']};--pink-mark:{k['pink_mark']};
--pink-bg:{k['pink_bg']};--teal-bg:{k['teal_bg']};--on-teal:{k['on_teal']};}}
html,body,.stApp,.stApp p,.stApp li,.stApp label,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp button,.stApp input,
.stApp textarea,.stMarkdown,[data-testid="stSidebar"] a,[data-testid="stSidebar"] p,
[data-testid="stMetricValue"],[data-testid="stMetricLabel"]{{font-family:{FONT} !important;}}
[data-testid="stIconMaterial"],.material-symbols-rounded{{font-family:"Material Symbols Rounded" !important;}}
.stApp,[data-testid="stAppViewContainer"]{{background:{k['glow']},var(--bg) !important;color:var(--ink);}}
[data-testid="stHeader"]{{background:transparent !important;}}
[data-testid="stSidebar"]{{background:var(--card) !important;border-right:1px solid var(--line);}}
[data-testid="stSidebar"] *{{color:var(--ink2);}}
[data-testid="stSidebar"] [aria-current="page"],[data-testid="stSidebar"] a[aria-current="page"]{{color:var(--ink) !important;}}
.stApp p,.stApp li,.stApp label,.stApp span{{color:inherit;}}
.stMarkdown p,.stMarkdown li{{color:var(--ink2);font-size:17px;line-height:1.55;}}
[data-testid="stCaptionContainer"] p{{color:var(--muted) !important;font-size:15px;}}
h1,h2,h3{{color:var(--ink) !important;letter-spacing:-.025em;font-weight:700 !important;}}
h1{{font-size:13px !important;letter-spacing:.14em !important;text-transform:uppercase;font-weight:800 !important;
color:var(--teal-ink) !important;padding:0 !important;margin:0 0 10px !important;}}
h2{{font-size:1.55rem !important;margin-top:2rem !important;}}
h3{{font-size:1.15rem !important;}}
a,.stApp a{{color:var(--teal-ink);text-underline-offset:3px;}}
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],
.stDeployButton,[data-testid="stAppDeployButton"],[data-testid="stToolbarActions"]{{display:none !important;visibility:hidden !important;}}
.block-container{{max-width:1080px;padding-top:1.75rem;padding-bottom:4.5rem;}}
[data-testid="stMetric"]{{background:transparent;border:0;padding:0;}}
[data-testid="stMetricLabel"]{{color:var(--muted) !important;font-size:14px !important;font-weight:650 !important;letter-spacing:.01em;}}
[data-testid="stMetricValue"]{{color:var(--ink) !important;font-size:clamp(2.4rem,5vw,4rem) !important;font-weight:760 !important;
letter-spacing:-.045em !important;line-height:.95 !important;font-variant-numeric:tabular-nums;}}
[data-testid="stMetricDelta"]{{font-size:1rem !important;font-weight:650 !important;}}
[data-testid="stExpander"] details{{background:var(--card);border:1px solid var(--line);border-radius:14px;box-shadow:none;}}
[data-testid="stExpander"] summary p{{font-weight:650;color:var(--ink) !important;}}
.stTextInput input,.stNumberInput input,.stTextArea textarea,.stDateInput input,
[data-baseweb="select"] > div,[data-baseweb="input"] > div{{background:var(--card) !important;color:var(--ink) !important;
border-color:var(--line) !important;}}
[data-testid="stChatMessage"]{{background:var(--card);border:1px solid var(--line);border-radius:16px;box-shadow:none;}}
[data-testid="stDataFrame"],[data-testid="stTable"]{{border:1px solid var(--line);border-radius:12px;}}
.stButton>button,.stLinkButton>a,[data-testid="stPageLink"] a{{min-height:44px;border-radius:12px;font-weight:650;box-shadow:none;}}
.stButton>button[kind="primary"],.stButton>button[data-testid="stBaseButton-primary"]{{background:var(--teal) !important;color:var(--on-teal) !important;border:0 !important;}}
.stButton>button[kind="secondary"],.stButton>button[data-testid="stBaseButton-secondary"]{{background:var(--card) !important;color:var(--ink) !important;border:1px solid var(--line) !important;}}
.stApp :focus-visible{{outline:2px solid var(--teal-ink);outline-offset:3px;}}
.theme-kpi{{padding:2px 0 18px;min-width:min(220px,100%);}}
.theme-kpi .l{{font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 8px;}}
.theme-kpi .v{{font-size:clamp(44px,6vw,76px);font-weight:760;letter-spacing:-.05em;line-height:.92;color:var(--ink);
font-variant-numeric:tabular-nums;}}
.theme-kpi .u{{font-size:.38em;font-weight:700;letter-spacing:0;margin-left:.25em;color:var(--muted);}}
.theme-kpi .d{{margin-top:8px;font-size:16px;font-weight:650;color:var(--ink2);font-variant-numeric:tabular-nums;}}
.theme-kpi.tone-good .v,.theme-kpi.tone-pass .v{{color:var(--teal-ink);}}
.theme-kpi.tone-refusal,.theme-kpi.tone-needs-human{{border-left:3px solid var(--pink-mark);padding-left:14px;}}
.theme-kpi.tone-refusal .v,.theme-kpi.tone-needs-human .v,.theme-kpi.tone-refusal .l,.theme-kpi.tone-needs-human .l{{color:var(--pink);}}
@media (max-width:720px){{.block-container{{padding-left:16px;padding-right:16px;padding-top:1rem;}}
[data-testid="stSidebar"]{{min-width:0 !important;}}
.theme-kpi .v{{font-size:44px;}}}}
@media (prefers-reduced-motion:reduce){{.theme-kpi{{animation:none !important;}}}}
</style>"""


def apply(light: bool | None = None) -> None:
    """Paint the global look. ``light=True`` is the projector switch. See the module docstring."""
    k = TOKENS["light" if resolve_light(light) else "dark"]
    st.markdown(_css(k), unsafe_allow_html=True)


def _show(markup: str) -> None:
    """Render HTML without the phrase table. Values may be figures; they are not interface copy."""
    raw = getattr(st, "_raw_html", None)
    if raw is not None:
        raw(markup)
        return
    html_fn = getattr(st, "html", None)
    if html_fn is not None:
        html_fn(markup)
        return
    st.markdown(markup, unsafe_allow_html=True)


def kpi(label: str, value: str, delta: str | None = None, tone: str = TONE_NEUTRAL) -> None:
    """One big number. ``tone`` is a ``TONE_*`` constant. Pink only for refusal / needs-a-human.

    The label is interface copy and goes through ``i18n.tr``. ``value`` and ``delta`` are escaped
    and not translated: pass figures the page already read from ``out/``. Call ``apply()`` first.
    """
    if tone not in TONES:
        tone = TONE_NEUTRAL
    delta_html = f'<div class="d">{html.escape(str(delta))}</div>' if delta else ""
    shown = html.escape(i18n.tr(str(label)))
    _show(
        f'<div class="theme-kpi tone-{tone}"><div class="l">{shown}</div>'
        f'<div class="v">{html.escape(str(value))}</div>{delta_html}</div>'
    )
