"""Page components for app v2 (R9, Rashed's Claude): hero line, key numbers, cards, story bar, explain lines.

Presentation only: every number is passed in by app.py, which reads it from app/data.py (out/, measures/).
The global look (fonts, colour variables, hidden Streamlit chrome) is Grok's app/theme.py; these styles read its
CSS variables and fall back to ALTYCA's colours if a variable is missing.
"""
from __future__ import annotations

import streamlit as st

STORY_KEY = "story_mode"

CSS = """<style>
.gx-eyebrow{font-size:13px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;color:var(--teal-ink,#00cc99);margin:0 0 10px;}
.gx-hero{font-size:clamp(30px,4.4vw,52px);line-height:1.08;font-weight:800;letter-spacing:-.035em;color:var(--ink,#f2f4f5);margin:0 0 14px;max-width:22ch;}
.gx-hero em{font-style:normal;color:var(--teal-ink,#00cc99);}
.gx-sub{font-size:19px;line-height:1.5;color:var(--ink2,#c4cad1);max-width:60ch;margin:0 0 26px;}
.gx-kpis{display:flex;flex-wrap:wrap;gap:14px;margin:8px 0 26px;}
.gx-kpi{flex:1 1 220px;min-width:min(200px,100%);}
.gx-kpi .v{font-size:clamp(34px,4vw,48px);font-weight:800;letter-spacing:-.04em;line-height:1;color:var(--ink,#f2f4f5);font-variant-numeric:tabular-nums;}
.gx-kpi .u{font-size:17px;font-weight:700;color:var(--muted,#9aa3ad);margin-left:6px;letter-spacing:0;}
.gx-kpi .l{font-size:14px;color:var(--muted,#9aa3ad);margin-top:8px;font-weight:600;}
.gx-kpi.good .v{color:var(--teal-ink,#00cc99);}
.gx-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));gap:14px;margin:6px 0 22px;}
.gx-card{background:var(--card,#16191e);border:1px solid var(--line,#262b33);border-radius:16px;padding:20px 22px;}
.gx-card h4{margin:0 0 8px;font-size:18px;font-weight:750;color:var(--ink,#f2f4f5);letter-spacing:-.01em;}
.gx-card p{margin:0;font-size:15.5px;line-height:1.5;color:var(--ink2,#c4cad1);}
.gx-card .n{font-size:28px;font-weight:800;letter-spacing:-.03em;color:var(--ink,#f2f4f5);font-variant-numeric:tabular-nums;margin-top:14px;}
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
.gx-bridge{font-size:16px;color:var(--ink2,#c4cad1);margin:28px 0 8px;}
@media (max-width:720px){.gx-sub{font-size:17px;}}
</style>"""


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def hero(eyebrow: str, line: str, sub: str = "") -> None:
    """One summary line in big type. The line may wrap a phrase in <em> for the accent colour."""
    sub_html = f'<p class="gx-sub">{sub}</p>' if sub else ""
    eye = f'<p class="gx-eyebrow">{eyebrow}</p>' if eyebrow else ""
    st.html(f'<div>{eye}<p class="gx-hero">{line}</p>{sub_html}</div>')


def explain(term: str, text: str) -> None:
    """First time an idea appears: one plain sentence, so the page makes sense without a voice-over."""
    st.html(f'<p class="gx-explain"><b>{term}</b> {text}</p>')


def bridge(text: str) -> None:
    st.html(f'<p class="gx-bridge">{text}</p>')


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
