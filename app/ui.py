"""Page components for app v2 (R9, Rashed's Claude): hero line, key numbers, cards, story bar, explain lines.

Presentation only: every number is passed in by app.py, which reads it from app/data.py (out/, measures/).
The global look (fonts, colour variables, hidden Streamlit chrome) is Grok's app/theme.py; these styles read its
CSS variables and fall back to ALTYCA's colours if a variable is missing.

Theme contract (grok/R9-theme, app/theme.py): --bg --card --card2 --line --ink --ink2 --muted --teal
--teal-ink --pink --pink-bg --teal-bg --on-teal. This file uses only those, plus its own fallbacks.
"""
from __future__ import annotations

import base64
import re
import html as _html
from pathlib import Path

import streamlit as st

import i18n

# Hero photos are owned by grok/R9-theme and land in app/static/img/. Missing file = teal glow.
HERO_FILES = {
    "about": "about.jpg",
    "connect": "connect.jpg",
    "stand": "stand.jpg",
    "plan": "plan.jpg",
    "track": "track.jpg",
}
_IMG_DIR = Path(__file__).resolve().parent / "static" / "img"
_GLOW = (
    "radial-gradient(920px 440px at 82% 12%, rgba(0,204,153,.38), transparent 62%),"
    "radial-gradient(640px 360px at 6% 100%, rgba(0,204,153,.16), transparent 58%),"
    "linear-gradient(165deg, #10241e 0%, #0d0f12 72%)"
)
_SCRIM = "linear-gradient(105deg, rgba(13,15,18,.90) 0%, rgba(13,15,18,.66) 52%, rgba(13,15,18,.42) 100%)"

STORY_KEY = "story_mode"


def _raw(markup: str) -> None:
    """st.html without the German phrase table: cards mix our labels with text from the data files."""
    getattr(st, "_raw_html", st.html)(markup)


def esc(text) -> str:
    """Text from the data (descriptions, roles, titles) is escaped and never translated."""
    return _html.escape(str(text))

CSS = """<style>
.gx-num{color:var(--gx-stat,#ffd166);font-weight:800;font-size:1.12em;font-variant-numeric:tabular-nums;white-space:nowrap;}
[data-testid="stPopoverBody"]{background:var(--card,#16191e) !important;color:var(--ink2,#c4cad1) !important;border:1px solid var(--line,#262b33) !important;}
[data-testid="stPopoverBody"] p,[data-testid="stPopoverBody"] li,[data-testid="stPopoverBody"] span{color:var(--ink2,#c4cad1) !important;}
[data-testid="stPopoverBody"] strong,[data-testid="stPopoverBody"] b{color:var(--ink,#f2f4f5) !important;}
.gx-term{background:#0a0c0f;border:1px solid var(--line,#262b33);border-radius:14px;overflow:hidden;margin:14px 0 22px;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;}
.gx-term .bar{display:flex;align-items:center;gap:7px;padding:10px 14px;background:#14171c;border-bottom:1px solid var(--line,#262b33);}
.gx-term .bar i{width:11px;height:11px;border-radius:50%;background:#3a4047;display:inline-block;}
.gx-term .bar span{margin-left:10px;font-size:13px;color:#9aa3ad;letter-spacing:.02em;}
.gx-term .body{padding:16px 20px 18px;}
.gx-term p{margin:0 0 8px;font-size:19px;line-height:1.45;color:#c4cad1;}
.gx-term p b{color:#f2f4f5;font-weight:700;display:inline-block;min-width:6.5em;}
.gx-term .pr{color:#00cc99;font-weight:700;margin-right:6px;}
.gx-term p.ok{color:#00cc99;font-weight:700;margin:12px 0 0;}
@media (max-width:720px){.gx-term p{font-size:15px;}.gx-term p b{min-width:0;margin-right:4px;}.gx-term .body{padding:12px 14px;}}
.gx-team{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin:8px 0 4px;}
.gx-person{display:flex;flex-direction:column;align-items:center;text-align:center;gap:6px;padding:22px 12px 20px;
  background:var(--card,#16191e);border:1px solid var(--line,#262b33);border-radius:18px;}
.gx-person b{font-size:19px;color:var(--ink,#f2f4f5);margin-top:6px;}
.gx-person span{font-size:15px;color:var(--muted,#9aa3ad);line-height:1.35;}
.gx-avatar{width:112px;height:112px;border-radius:50%;object-fit:cover;border:2px solid var(--teal,#00cc99);}
.gx-initials{display:flex;align-items:center;justify-content:center;background:var(--teal-bg,#0f2a23);color:var(--teal,#00cc99);
  font-size:38px;font-weight:800;letter-spacing:.02em;}
.st-key-beat_hook .gx-photo{margin-bottom:0;}
.st-key-beat_hook,.st-key-beat_team,.st-key-beat_why,.st-key-beat_promise{margin:0 0 12px;}
.st-key-beat_why .gx-grid{margin:0;}
@media (max-width:720px){.gx-team{grid-template-columns:1fr;gap:12px;}.gx-person{flex-direction:row;text-align:left;padding:14px 16px;gap:14px;}
  .gx-person b{margin-top:0;}.gx-avatar{width:64px;height:64px;}.gx-initials{font-size:24px;}
  .gx-person{display:grid;grid-template-columns:64px 1fr;grid-template-rows:auto auto;column-gap:14px;}
  .gx-person .gx-avatar{grid-row:1 / span 2;}}
.gx-hitl{display:inline-block;margin-left:8px;padding:2px 10px;border-radius:999px;border:1px solid var(--pink,#f84aa7);font-size:13px;font-weight:700;letter-spacing:.04em;white-space:nowrap;}
.gx-team-note{font-size:14px;color:var(--muted,#9aa3ad);margin:10px 0 0;text-align:center;}
button[data-variant="segmented_control"]{background:var(--card,#16191e) !important;color:var(--ink2,#c4cad1) !important;border-color:var(--line,#262b33) !important;min-height:44px;}
button[data-variant="segmented_control"] *{color:inherit !important;}
button[data-variant="segmented_control"][aria-checked="true"]{background:var(--teal,#00cc99) !important;color:var(--on-teal,#0d0f12) !important;border-color:var(--teal,#00cc99) !important;font-weight:700;}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"]{min-width:0;max-width:100%;}
[data-testid="stChatMessage"] table{display:block;max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch;border-collapse:collapse;font-size:14px;}
[data-testid="stChatMessage"] th,[data-testid="stChatMessage"] td{white-space:normal;word-break:normal;overflow-wrap:normal;hyphens:none;padding:6px 10px;vertical-align:top;}
[data-testid="stChatMessage"] th{min-width:72px;color:var(--ink,#f2f4f5) !important;font-weight:700;border-bottom:1px solid var(--line,#262b33) !important;}
[data-testid="stChatMessage"] td{color:var(--ink2,#c4cad1) !important;border-bottom:1px solid var(--line,#262b33) !important;}
[data-testid="stChatMessage"] th,[data-testid="stChatMessage"] td{background:transparent !important;}
[data-testid="stFileUploaderDropzone"]{background:var(--card2,#1c2026) !important;border:1px dashed var(--line,#262b33) !important;color:var(--ink2,#c4cad1) !important;}
[data-testid="stFileUploaderDropzone"] span,[data-testid="stFileUploaderDropzone"] small,[data-testid="stFileUploaderDropzoneInstructions"] *{color:var(--ink2,#c4cad1) !important;}
[data-testid="stFileUploaderDropzone"] button{background:var(--card,#16191e) !important;color:var(--ink,#f2f4f5) !important;border:1px solid var(--line,#262b33) !important;}
/* R10 item 2: popover buttons ("How … was calculated") and inline code chips readable in dark and light mode */
[data-testid="stPopover"] button,[data-testid="stPopoverButton"],[data-testid="stPopover"] > div > button{
  background:var(--card,#16191e) !important;color:var(--ink,#f2f4f5) !important;border:1px solid var(--line,#262b33) !important;}
[data-testid="stPopover"] button p,[data-testid="stPopover"] button span,[data-testid="stPopover"] button div{color:var(--ink,#f2f4f5) !important;}
[data-testid="stPopover"] button svg{fill:var(--ink,#f2f4f5) !important;color:var(--ink,#f2f4f5) !important;}
.stApp code,[data-testid="stSidebar"] code,[data-testid="stCaptionContainer"] code{
  background:var(--card2,#1c2026) !important;color:var(--ink2,#c4cad1) !important;border:1px solid var(--line,#262b33);
  border-radius:6px;padding:1px 6px;}
.gx-eyebrow{font-size:13px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;color:var(--teal-ink,#00cc99);margin:0 0 10px;}
.gx-hero{font-size:clamp(30px,4.4vw,52px);line-height:1.08;font-weight:800;letter-spacing:-.035em;color:var(--ink,#f2f4f5);margin:0 0 14px;max-width:22ch;}
.gx-hero em{font-style:normal;color:var(--teal-ink,#00cc99);}
.gx-sub{font-size:19px;line-height:1.5;color:var(--ink2,#c4cad1);max-width:60ch;margin:0 0 26px;}
.gx-kpis{display:flex;flex-wrap:wrap;gap:14px;margin:8px 0 26px;}
.gx-kpi{flex:1 1 220px;min-width:min(200px,100%);}
.gx-kpi .v{font-size:clamp(34px,4vw,48px);font-weight:800;letter-spacing:-.04em;line-height:1;color:var(--gx-stat,#ffd166);font-variant-numeric:tabular-nums;}
.gx-kpi .u{font-size:17px;font-weight:700;color:var(--muted,#9aa3ad);margin-left:6px;letter-spacing:0;}
.gx-kpi .l{font-size:14px;color:var(--muted,#9aa3ad);margin-top:8px;font-weight:600;}
.gx-kpi.good .v{color:var(--gx-stat,#ffd166);}
.gx-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));gap:14px;margin:6px 0 22px;}
.gx-card{background:var(--card,#16191e);border:1px solid var(--line,#262b33);border-radius:16px;padding:20px 22px;}
.gx-card h4{margin:0 0 8px;font-size:18px;font-weight:750;color:var(--ink,#f2f4f5);letter-spacing:-.01em;}
.gx-card p{margin:0;font-size:15.5px;line-height:1.5;color:var(--ink2,#c4cad1);}
.gx-card .n{font-size:30px;font-weight:800;letter-spacing:-.03em;color:var(--gx-stat,#ffd166);font-variant-numeric:tabular-nums;margin-top:14px;}
.gx-card .n span{font-size:15px;font-weight:700;color:var(--muted,#9aa3ad);margin-left:4px;letter-spacing:0;}
.gx-card .meta{font-size:13.5px;color:var(--muted,#9aa3ad);margin-top:10px;font-weight:600;}
.gx-card .k{font-size:12.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted,#9aa3ad);font-weight:700;margin:0 0 8px;}
.gx-card.accent{border-color:var(--teal,#00cc99);}
.gx-card.pink{border-color:var(--pink,#f84aa7);background:var(--pink-bg,#2a1421);}
.gx-card.pink h4{color:var(--pink,#f84aa7);}
.gx-pill{display:inline-block;padding:3px 12px;border-radius:999px;font-size:13px;font-weight:750;letter-spacing:.02em;}
.gx-pill.good{background:var(--teal-bg,#0f2a23);color:var(--teal-ink,#00cc99);}
.gx-pill.pink{background:var(--pink-bg,#2a1421);color:var(--pink,#f84aa7);}
.gx-pill.muted{background:var(--card2,#1c2026);color:var(--muted,#9aa3ad);}
.gx-story{display:flex;align-items:center;gap:14px;margin:0 0 26px;}
.gx-story .bar{flex:1;height:4px;border-radius:2px;background:var(--line,#262b33);overflow:hidden;}
.gx-story .bar i{display:block;height:100%;background:var(--teal,#00cc99);}
.gx-story .s{font-size:13px;font-weight:700;color:var(--muted,#9aa3ad);letter-spacing:.08em;text-transform:uppercase;white-space:nowrap;}
.gx-foot{border-top:1px solid var(--line,#262b33);margin-top:40px;padding-top:18px;font-size:14px;color:var(--muted,#9aa3ad);}
@media (prefers-reduced-motion:no-preference){.gx-hero,.gx-kpis,.gx-grid{animation:gxin .35s ease-out both;}}
@keyframes gxin{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.gx-refuse{background:var(--pink-bg,#2a1421);border:1px solid var(--pink,#f84aa7);border-radius:14px;padding:14px 18px;color:var(--ink,#f2f4f5);font-size:17px;}
.gx-refuse b{color:var(--pink,#f84aa7);}
.gx-explain{font-size:15px;color:var(--muted,#9aa3ad);border-left:3px solid var(--teal,#00cc99);padding:2px 0 2px 12px;margin:0 0 18px;max-width:70ch;}
.gx-explain b{color:var(--ink2,#c4cad1);}
.gx-roadmap{font-size:14px;color:var(--muted,#9aa3ad);margin:-8px 0 18px;max-width:70ch;}
.gx-roadmap .k{font-size:12px;letter-spacing:.12em;text-transform:uppercase;font-weight:700;margin-right:8px;}
.gx-bridge{font-size:16px;color:var(--ink2,#c4cad1);margin:28px 0 8px;}
.gx-photo{position:relative;border-radius:20px;padding:32px 28px 12px;margin:0 0 22px;min-height:210px;
background-color:#0d0f12;background-size:cover;background-position:center;border:1px solid var(--line,#262b33);overflow:hidden;}
.gx-photo .gx-hero{color:#f5f6f7;}
.gx-photo .gx-hero em,.gx-photo .gx-eyebrow{color:#00cc99;}
.gx-photo .gx-sub{color:#d5dbe1;}
.gx-sr{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;}
@media (max-width:720px){.gx-sub{font-size:17px;}.gx-photo{padding:22px 16px 4px;min-height:180px;box-shadow:inset 0 0 0 2000px rgba(13,15,18,.35);}}
</style>"""


STAT_DARK, STAT_LIGHT = "#ffd166", "#8a6400"  # key numbers; the light step keeps ≥ 4.5:1 on white


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    stat = STAT_LIGHT if st.session_state.get("light_mode") else STAT_DARK
    st.markdown(f"<style>:root{{--gx-stat:{stat};}}</style>", unsafe_allow_html=True)


_STAT_RE = re.compile(r"(?<![\w\-/.])([−+\-]?\d[\d,]*(?:\.\d+)?\s?(?:%|×))")


def marks(html_text: str) -> str:
    """Key statistics inside a sentence (percentages, «3.7×») in the stat colour, bold and a little bigger.
    Use on text that is already escaped: it adds spans only around the matched figures."""
    return _STAT_RE.sub(r'<span class="gx-num">\1</span>', html_text)


def photo_band(inner: str, slug: str) -> str:
    """Opening band. Uses app/static/img/<file> when that file is present, otherwise a dark teal glow.

    The static URL is always named, so the photo appears once grok/R9-theme serves app/static/.
    A file already on disk is also inlined, so the demo works before static serving is on.
    Style values stay free of double quotes: Streamlit's sanitiser would cut the attribute there.
    """
    filename = HERO_FILES[slug]
    url = f"/app/static/img/{filename}"
    path = _IMG_DIR / filename
    layers = [f"url({url})"]
    if path.is_file():
        b64 = base64.b64encode(path.read_bytes()).decode()
        layers.insert(0, f"url(data:image/jpeg;base64,{b64})")
    style = f"background-image:{_SCRIM},{','.join(layers)},{_GLOW};"
    label = _html.escape(f"Opening photo {filename}. Teal glow until that file is served.")
    # The headline stays real text. role=img would hide it from the accessibility tree.
    return (f'<div class="gx-photo" style="{style}" data-hero="{filename}">'
            f'<span class="gx-sr">{label}</span>{inner}</div>')


def hero(eyebrow: str, line: str, sub: str = "", photo: str = "") -> None:
    """One summary line in big type. The line may wrap a phrase in <em> for the accent colour.

    photo is a key of HERO_FILES (about, connect, stand, plan, track). Empty keeps a plain line.
    """
    sub_html = f'<p class="gx-sub">{sub}</p>' if sub else ""
    eye = f'<p class="gx-eyebrow">{eyebrow}</p>' if eyebrow else ""
    inner = f'{eye}<p class="gx-hero">{i18n.tr(line, label=False)}</p>{i18n.tr(sub_html, label=False)}'
    if photo:
        _raw(photo_band(inner, photo))
    else:
        _raw(f"<div>{inner}</div>")


def explain(term: str, text: str) -> None:
    """First time an idea appears: one plain sentence, so the page makes sense without a voice-over."""
    _raw(f'<p class="gx-explain"><b>{i18n.tr(term)}</b> {marks(i18n.tr(text, label=False))}</p>')


def roadmap_note(text: str) -> None:
    """One muted line for a roadmap item: same «Roadmap · not built yet» label as the GreenOps agents cards. No controls."""
    _raw(f'<p class="gx-roadmap"><span class="k">{i18n.tr("Roadmap · not built yet")}</span>{i18n.tr(text, label=False)}</p>')


def bridge(text: str) -> None:
    _raw(f'<p class="gx-bridge">{i18n.tr(text, label=False)}</p>')


def kpis(items: list[tuple[str, str, str]], good: set[int] | None = None) -> None:
    """At most three or four key numbers: (value, unit, label)."""
    good = good or set()
    cells = "".join(
        f'<div class="gx-kpi{" good" if i in good else ""}"><div class="v">{v} <span class="u">{u}</span></div>'
        f'<div class="l">{i18n.tr(lbl)}</div></div>' for i, (v, u, lbl) in enumerate(items))
    _raw(f'<div class="gx-kpis">{cells}</div>')


def card(title: str, body: str = "", number: str = "", unit: str = "", meta: str = "", kind: str = "",
         kicker: str = "", data_title: bool = False, data_body: bool = False) -> str:
    """Our own title, body, unit and kicker are translated here. Text from the data files is escaped and kept
    as stored: set data_title / data_body, and pass meta already built (data parts through esc())."""
    title = esc(title) if data_title else i18n.tr(title)
    body = esc(body) if data_body else i18n.tr(body, label=False)
    unit, kicker = i18n.tr(unit), i18n.tr(kicker)
    k = f'<p class="k">{kicker}</p>' if kicker else ""
    n = f'<div class="n">{number} <span>{unit}</span></div>' if number else ""  # a real space: CSS margins can be overridden
    m = f'<div class="meta">{marks(meta)}</div>' if meta else ""
    b = f"<p>{marks(body)}</p>" if body else ""
    return f'<div class="gx-card {kind}">{k}<h4>{title}</h4>{b}{n}{m}</div>'


def grid(cards: list[str]) -> None:
    _raw(f'<div class="gx-grid">{"".join(cards)}</div>')


TEAM_DIR = Path(__file__).resolve().parent / "static" / "team"


@st.cache_data(show_spinner=False)
def _photo_b64(path_str: str, mtime: float) -> str | None:
    """Any size photo → 400 px square JPEG (centre crop), base64. None when the file cannot be read."""
    try:
        import io
        from PIL import Image, ImageOps
        img = ImageOps.exif_transpose(Image.open(path_str)).convert("RGB")
        img = ImageOps.fit(img, (400, 400))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=82, optimize=True)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


def _avatar(name: str) -> str:
    """Round photo from app/static/team/<name>.jpg|.jpeg|.png (any size, shrunk here). No usable file: initials."""
    for ext in ("jpg", "jpeg", "png", "JPG", "JPEG", "PNG"):
        path = TEAM_DIR / f"{name.lower()}.{ext}"
        if path.is_file():
            b64 = _photo_b64(str(path), path.stat().st_mtime)
            if b64:
                return f'<img class="gx-avatar" src="data:image/jpeg;base64,{b64}" alt="{esc(name)}">'
    initials = "".join(w[0] for w in name.split()[:2]).upper()
    return f'<div class="gx-avatar gx-initials" aria-hidden="true">{esc(initials)}</div>'


def team(members: list[tuple[str, str]]) -> None:
    """Three equal team cards: round photo (or initials), name, role underneath."""
    cells = "".join(f'<div class="gx-person">{_avatar(n)}<b>{esc(n)}</b><span>{i18n.tr(r)}</span></div>'
                    for n, r in members)
    _raw(f'<div class="gx-team">{cells}</div>')


def terminal(title: str, lines: list[tuple[str, str]], done: str) -> str:
    """A small terminal block: one «> step  detail» line each, a done line at the end. Big mono type, few words."""
    rows = "".join(f'<p><span class="pr">&gt;</span> <b>{esc(i18n.tr(k))}</b> {esc(v)}</p>' for k, v in lines)
    return (f'<div class="gx-term gx-check"><div class="bar"><i></i><i></i><i></i><span>{esc(title)}</span></div>'
            f'<div class="body">{rows}<p class="ok"><span class="pr">✓</span> {esc(i18n.tr(done))}</p></div></div>')


def story_bar(step: int, total: int, label: str) -> None:
    pct = int(round(100 * step / total))
    _raw(f'<div class="gx-story" role="progressbar" aria-valuenow="{step}" aria-valuemin="0" aria-valuemax="{total}" '
            f'aria-label="Story progress"><span class="s">Step {step} of {total}</span>'
            f'<div class="bar"><i style="width:{pct}%"></i></div><span class="s">{label}</span></div>')
