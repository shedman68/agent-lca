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
    "contact": "basel.jpg",
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
.gx-rot .w i.gx-y{color:var(--gx-stat,#ffd166) !important;}
.gx-sources{border-top:1px solid var(--line,#262b33);margin:36px 0 8px;padding-top:14px;}
.gx-sources .tt{font-size:12.5px;letter-spacing:.12em;text-transform:uppercase;font-weight:800;color:var(--muted,#9aa3ad);margin:0 0 6px;}
.gx-sources ol{margin:0;padding-left:20px;}
.gx-sources li{font-size:13px;line-height:1.5;color:var(--muted,#9aa3ad);margin:0 0 3px;overflow-wrap:anywhere;}
.gx-sources li b{color:var(--ink2,#c4cad1);font-weight:700;}
.gx-upsim{background:#0a0c0f;border:1px dashed var(--teal,#00cc99);border-radius:14px;padding:14px 16px;margin:14px 0 4px;}
.gx-upsim .hd{display:flex;align-items:center;gap:10px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-size:15px;color:#f2f4f5;margin-bottom:10px;}
.gx-upsim .ic{color:#00cc99;font-weight:800;}
.gx-upsim .ok{margin-left:auto;color:#00cc99;font-weight:700;}
.gx-upsim .chips{display:flex;flex-wrap:wrap;gap:6px;}
.gx-upsim .chip{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.5px;color:#c4cad1;
  background:#14171c;border:1px solid var(--line,#262b33);border-radius:999px;padding:3px 10px;}
.gx-upsim .chip.more{color:#00cc99;border-color:#00cc99;}
.gx-upsim .prog{height:6px;border-radius:3px;background:#1a2e2a;margin-top:12px;overflow:hidden;}
.gx-upsim .prog i{display:block;height:100%;width:100%;background:#00cc99;}
.gx-agent .cmd{color:#f2f4f5;margin-bottom:10px;}
.gx-agent .work{color:#ffd166;font-weight:700;}
.gx-agent .spin{display:inline-block;color:#ff8a65;}
.gx-agent .ln .pr{color:#00cc99;}
@media (prefers-reduced-motion:no-preference){
  .gx-upsim .chip{animation:gxChip .45s cubic-bezier(.2,.8,.3,1) both;}
  .gx-upsim .prog i{animation:gxProg 1.3s ease-out .2s both;}
  .gx-upsim .ok{animation:gxFadeIn .3s ease-out 1.5s both;}
  .gx-agent .cmd{animation:gxFadeIn .2s ease-out both;}
  .gx-agent .typed{display:inline-block;overflow:hidden;white-space:nowrap;vertical-align:bottom;animation:gxTypeW .6s steps(24,end) both;}
  .gx-agent .work{animation:gxFadeIn .2s ease-out both,gxFadeOut .3s ease-in both;}
  .gx-agent .spin{animation:gxSpin 1s linear infinite;}
  .gx-agent .ln{animation:gxLineIn .35s ease-out both;}
}
@media (prefers-reduced-motion:reduce){.gx-agent .work{display:none;}}
@keyframes gxChip{from{opacity:0;transform:translateY(-18px) scale(.9);}}
@keyframes gxProg{from{width:0;}}
@keyframes gxFadeIn{from{opacity:0;}}
@keyframes gxFadeOut{to{opacity:0;height:0;margin:0;padding:0;overflow:hidden;}}
@keyframes gxTypeW{from{max-width:0;}to{max-width:40ch;}}
@keyframes gxSpin{to{transform:rotate(360deg);}}
@keyframes gxLineIn{from{opacity:0;transform:translateX(-10px);}}
@media (max-width:720px){[data-testid="stHeader"]{background:var(--bg,#0d0f12) !important;box-shadow:0 1px 0 var(--line,#262b33);}}
[data-testid="stToolbar"]{display:flex !important;visibility:visible !important;}
[data-testid="stExpandSidebarButton"]{display:flex !important;visibility:visible !important;opacity:1 !important;}
[data-testid="stExpandSidebarButton"] button,[data-testid="stExpandSidebarButton"]{color:var(--teal,#00cc99) !important;}
[data-testid="stHeaderLogo"]{display:block !important;visibility:visible !important;}
.gx-card .n.has-pop{position:relative;cursor:help;display:inline-block;}
.gx-pop{display:none;position:absolute;z-index:20;right:calc(100% + 34px);top:-40px;width:330px;background:#0a0c0f;
  border:1px solid var(--teal,#00cc99);border-radius:14px;padding:14px 16px;box-shadow:0 16px 40px rgba(0,0,0,.5);
  font-size:14px;font-weight:500;letter-spacing:0;color:var(--ink2,#c4cad1);text-align:left;}
.gx-pop .tt{margin:0 0 10px;font-size:13px;letter-spacing:.1em;text-transform:uppercase;font-weight:800;color:#f2f4f5;}
.gx-pop .bar{display:flex;height:16px;border-radius:8px;overflow:hidden;margin:0 0 12px;}
.gx-pop .bar i{display:block;height:100%;}
.gx-pop ul{list-style:none;margin:0;padding:0;}
.gx-pop li{display:flex;align-items:center;gap:8px;margin:0 0 6px;font-size:14px;color:#f2f4f5;}
.gx-pop li b{width:12px;height:12px;border-radius:3px;flex:0 0 auto;}
.gx-pop li span{margin-left:auto;color:#c4cad1;font-variant-numeric:tabular-nums;white-space:nowrap;}
.gx-pop .nt{margin:8px 0 0;font-size:12.5px;color:#9aa3ad;line-height:1.4;}
.gx-card .n.has-pop:hover .gx-pop,.gx-card .n.has-pop:focus-within .gx-pop{display:block;}
@media (max-width:1700px){.gx-pop{right:auto;left:0;top:auto;bottom:calc(100% + 12px);}}
@media (max-width:720px){.gx-pop{position:static;width:auto;margin:12px 0 0;}.gx-card .n.has-pop{display:block;}}
.gx-pop li{width:100%;}
.gx-best{display:block;margin-top:10px;padding:8px 10px;border:2px solid #ff5d73;border-radius:10px;}
.gx-partners{display:flex;align-items:center;gap:22px;flex-wrap:wrap;margin:4px 0 14px;}
.gx-partner{width:auto;max-width:220px;object-fit:contain;background:#ffffff;border-radius:12px;padding:8px 12px;}
.gx-partner-txt{font-weight:800;font-size:20px;letter-spacing:.02em;color:var(--ink,#f2f4f5);border:1px solid var(--line,#262b33);border-radius:12px;padding:10px 14px;}
.gx-partners .x{font-size:26px;font-weight:800;color:var(--muted,#9aa3ad);}
.gx-close h4{font-size:30px !important;margin:6px 0 10px !important;}
.gx-close ul{margin:0;padding:0;list-style:none;}
.gx-close li{font-size:20px;line-height:1.45;color:var(--ink2,#c4cad1);padding:4px 0;}
.gx-close li b{color:var(--ink,#f2f4f5);}
.gx-close li::before{content:"→ ";color:var(--teal,#00cc99);font-weight:800;}
.gx-talk{font-size:clamp(56px,9vw,120px);font-weight:900;letter-spacing:-.04em;line-height:1;color:var(--teal,#00cc99) !important;margin:18px 0 8px;}
.gx-talk-sub{font-size:20px;color:var(--ink2,#c4cad1);margin:0 0 26px;}
.gx-confetti{position:fixed;inset:0;pointer-events:none;z-index:999;overflow:hidden;}
.gx-confetti i{position:absolute;top:-24px;display:block;border-radius:2px;opacity:0;}
@media (prefers-reduced-motion:no-preference){.gx-confetti i{animation-name:gxFall;animation-timing-function:cubic-bezier(.3,.6,.4,1);animation-fill-mode:both;}}
@keyframes gxFall{0%{opacity:1;transform:translateY(0) rotate(0deg);}85%{opacity:1;}100%{opacity:0;transform:translateY(105vh) rotate(540deg);}}
.gx-nextyear{margin:6px 0 4px;}
.gx-term p.ok.result{font-size:22px;color:#f2f4f5;margin-top:16px;padding-top:14px;border-top:1px solid var(--line,#262b33);}
.gx-term p.ok.result .gx-num{font-size:1.15em;}
.gx-term p.ok.result .lbl{color:#00cc99;letter-spacing:.04em;}
@media (max-width:720px){.gx-term p.ok.result{font-size:16px;}}
.gx-rot .gx-rot-static{display:none;}
@media (prefers-reduced-motion:reduce){.gx-rot{height:auto !important;overflow:visible !important;}.gx-rot .w{display:none !important;}.gx-rot .gx-rot-static{display:inline !important;}}
.gx-does{font-size:.8em;display:inline-block;line-height:1.15;}
.gx-in{margin-top:8px;display:inline-flex;line-height:0;border-radius:7px;transition:transform .15s ease;}
.gx-in img{display:block;width:30px;height:30px;}
.gx-in:hover{transform:scale(1.08);}
.gx-rot{display:inline-block;height:1.22em;overflow:hidden;vertical-align:bottom;color:inherit;margin-bottom:-.1em;}
.gx-rot .w{display:block;transform:translateY(0);}
.gx-rot .w i{display:block;height:1.4em;line-height:1.22em;font-style:normal;}
.st-key-beat_track_top [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stMarkdownContainer"] p::before{content:"› ";color:#00cc99;font-weight:800;}
.st-key-beat_track_top [data-testid="stChatInput"],.st-key-beat_track_top [data-testid="stChatInput"] > div{background:#0a0c0f !important;border-color:var(--line,#262b33) !important;}
.st-key-beat_track_top [data-testid="stChatInput"] textarea{color:#f2f4f5 !important;background:transparent !important;}
.gx-log p{font-size:15px;margin:0 0 5px;line-height:1.4;}
.gx-log p b{min-width:13.5em;font-weight:600;}
.gx-log p.cmd{color:#f2f4f5;margin-bottom:12px;}
.gx-log p.ok .pr,.gx-log p.ok b{color:#00cc99;}
.gx-log p.warn .pr,.gx-log p.warn b{color:#ffb020;}
.gx-log p.bad .pr,.gx-log p.bad b{color:#ff5d73;}
.gx-log p.bad .note{color:#ffc2cb;}
.gx-log p.sum{margin-top:12px;color:#f2f4f5;}
.st-key-beat_track_top [data-testid="stChatMessage"]{background:#0a0c0f !important;border:1px solid var(--line,#262b33);border-radius:12px;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;}
.st-key-beat_track_top [data-testid="stChatMessage"] p{font-family:inherit;}
.st-key-beat_track_top [data-testid="stChatMessageAvatarUser"],.st-key-beat_track_top [data-testid="stChatMessageAvatarAssistant"]{display:none;}
.st-key-beat_track_top [data-testid="stChatMessage"]:has(.gx-refuse) .gx-refuse,.st-key-beat_track_top .gx-refuse{font-family:inherit;}
.st-key-beat_track_top [data-testid="stChatInput"] textarea{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;}
@media (max-width:720px){.gx-log p{font-size:13.5px;}.gx-log p b{min-width:0;display:block;}}
.st-key-beat_plan_map{position:relative;}
.st-key-beat_plan_map [data-testid="stElementContainer"]:has(.gx-callout){position:absolute;right:8px;top:56px;width:min(340px,36%);z-index:5;}
.gx-callout{box-shadow:0 12px 40px rgba(0,0,0,.45);border-color:var(--teal,#00cc99) !important;padding:16px 18px !important;}
.gx-callout p{font-size:15px !important;}
@media (max-width:720px){.st-key-beat_plan_map [data-testid="stElementContainer"]:has(.gx-callout){position:static;width:auto;}}
.gx-num{color:var(--gx-stat,#ffd166) !important;font-weight:800;font-size:1.12em;font-variant-numeric:tabular-nums;white-space:nowrap;}
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
.gx-team{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px;margin:8px 0 4px;}
@media (max-width:1100px){.gx-team{grid-template-columns:repeat(3,minmax(0,1fr));}}
.gx-avatar.gx-logo{object-fit:contain;background:#ffffff;padding:14px;}
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
  .gx-person .gx-avatar{grid-row:1 / span 3;}
  .gx-person .gx-in{grid-column:2;justify-self:start;margin-top:2px;}}
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
    if not path.is_file() and (_IMG_DIR.parent / filename).is_file():  # files uploaded straight into app/static/
        path = _IMG_DIR.parent / filename
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
         kicker: str = "", data_title: bool = False, data_body: bool = False, pop: str = "", ref: str = "") -> str:
    """Our own title, body, unit and kicker are translated here. Text from the data files is escaped and kept
    as stored: set data_title / data_body, and pass meta already built (data parts through esc())."""
    title = esc(title) if data_title else i18n.tr(title)
    body = esc(body) if data_body else i18n.tr(body, label=False)
    unit, kicker = i18n.tr(unit), i18n.tr(kicker)
    k = f'<p class="k">{kicker}</p>' if kicker else ""
    n = (f'<div class="n{" has-pop" if pop else ""}">{number} <span>{unit}</span>{pop}</div>'
         if number else "")  # a real space: CSS margins can be overridden; pop = optional hover pop-out
    m = f'<div class="meta">{marks(meta)}</div>' if meta else ""
    b = f"<p>{marks(body)}{ref}</p>" if body else ""  # ref: our own raised source number (HTML), after data text
    return f'<div class="gx-card {kind}">{k}<h4>{title}</h4>{b}{n}{m}</div>'


def grid(cards: list[str]) -> None:
    _raw(f'<div class="gx-grid">{"".join(cards)}</div>')


TEAM_DIR = Path(__file__).resolve().parent / "static" / "team"


@st.cache_data(show_spinner=False)
def _photo_b64(path_str: str, mtime: float) -> tuple[str, str, bool] | None:
    """Any size image → (base64, mime, is_logo). Photos: 400 px centre crop, JPEG. Images with transparency are
    treated as logos: fitted whole (no crop) on a transparent 400 px square, PNG."""
    try:
        import io
        from PIL import Image, ImageOps
        img = ImageOps.exif_transpose(Image.open(path_str))
        has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
        buf = io.BytesIO()
        if has_alpha:
            img = img.convert("RGBA")
            img.thumbnail((300, 300))
            canvas = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
            canvas.paste(img, ((400 - img.width) // 2, (400 - img.height) // 2), img)
            canvas.save(buf, "PNG", optimize=True)
            return base64.b64encode(buf.getvalue()).decode(), "image/png", True
        img = ImageOps.fit(img.convert("RGB"), (400, 400))
        img.save(buf, "JPEG", quality=82, optimize=True)
        return base64.b64encode(buf.getvalue()).decode(), "image/jpeg", False
    except Exception:
        return None


def _avatar(name: str) -> str:
    """Round photo or logo from app/static/team/<name>.jpg|.jpeg|.png (any size, shrunk here). None: initials."""
    for ext in ("jpg", "jpeg", "png", "JPG", "JPEG", "PNG"):
        path = TEAM_DIR / f"{name.lower()}.{ext}"
        if path.is_file():
            got = _photo_b64(str(path), path.stat().st_mtime)
            if got:
                b64, mime, logo = got
                cls = "gx-avatar gx-logo" if logo else "gx-avatar"
                return f'<img class="{cls}" src="data:{mime};base64,{b64}" alt="{esc(name)}">'
    initials = "".join(w[0] for w in name.split()[:2]).upper()
    return f'<div class="gx-avatar gx-initials" aria-hidden="true">{esc(initials)}</div>'


# A small LinkedIn «in» mark, drawn here (no download): blue rounded square, white «in».
_LINKEDIN_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 34 34"><rect width="34" height="34" rx="6" fill="#0A66C2"/>'
                 '<circle cx="9.5" cy="9.5" r="2.6" fill="#fff"/><rect x="7.3" y="13.3" width="4.4" height="13.2" fill="#fff"/>'
                 '<path d="M15 13.3h4.2v1.9c.6-1.1 2.1-2.2 4.3-2.2 4.4 0 5.2 2.9 5.2 6.6v6.9h-4.4v-6.1c0-1.5 0-3.4-2.1-3.4'
                 's-2.4 1.6-2.4 3.3v6.2H15z" fill="#fff"/></svg>')
_LINKEDIN_ICON = "data:image/svg+xml;base64," + base64.b64encode(_LINKEDIN_SVG.encode()).decode()


def team(members: list[tuple], links: bool = False) -> None:
    """Three equal team cards: round photo (or initials), full name, role underneath; optional LinkedIn link.
    The photo file is named after the first name (app/static/team/rashed.jpeg …)."""
    cells = []
    for m in members:
        name, role = m[0], m[1]
        url = m[2] if len(m) > 2 else ""
        link = (f'<a class="gx-in" href="{esc(url)}" target="_blank" rel="noopener" aria-label="LinkedIn: {esc(name)}" '
                f'title="LinkedIn"><img src="{_LINKEDIN_ICON}" alt="LinkedIn" width="30" height="30"></a>'
                if links and url else "")
        cells.append(f'<div class="gx-person">{_avatar(name.split()[0])}<b>{esc(name)}</b>'
                     f'<span>{i18n.tr(role)}</span>{link}</div>')
    _raw(f'<div class="gx-team">{"".join(cells)}</div>')


_ORG_CSS = """<style>
.gx-org{margin:4px 0 0;--o-line:rgba(255,255,255,.14);--o-glass:rgba(255,255,255,.045);--o-edge:rgba(255,255,255,.09);}
.gx-org.lt{--o-line:rgba(13,15,18,.18);--o-glass:rgba(13,15,18,.04);--o-edge:rgba(13,15,18,.12);}
.gx-org .lb{font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted,#9aa3ad);text-align:center;margin:0 0 12px;}
.gx-org .row{display:flex;gap:18px;}
.gx-org .grp{display:flex;flex-direction:column;align-items:center;min-width:0;}
.gx-org .hum{display:flex;flex-direction:column;align-items:center;text-align:center;gap:6px;}
.gx-org .hum .gx-avatar{width:56px;height:56px;min-width:56px;margin:0;border:1px solid var(--o-edge);box-shadow:0 0 0 4px rgba(255,255,255,.03);}
.gx-org .hum b{font-size:16px;font-weight:600;color:var(--ink,#f2f4f5);letter-spacing:-.01em;}
.gx-org .hum span{font-size:13px;color:var(--muted,#9aa3ad);margin-top:-4px;}
.gx-org img.wire{display:block;width:100%;height:34px;margin:6px 0 0;}
.gx-org .ags{display:flex;gap:10px;width:100%;margin-top:6px;}
.gx-org .ag{flex:1;display:flex;align-items:center;justify-content:center;gap:8px;padding:9px 10px;border-radius:999px;
  background:var(--o-glass);border:1px solid var(--o-edge);backdrop-filter:blur(8px);white-space:nowrap;}
.gx-org .ag .gx-avatar{width:22px;height:22px;min-width:22px;margin:0;border:0;}
.gx-org .ag .gx-avatar.gx-logo{padding:2px;}
.gx-org .ag b{font-size:13.5px;font-weight:500;color:var(--ink,#f2f4f5);}
.gx-org .lb.ag-lb{margin:14px 0 10px;}
.gx-org .track{position:relative;margin:26px 28px 6px;}
.gx-org .track .ln{position:absolute;left:0;right:0;top:6px;height:1px;background:var(--o-line);}
.gx-org .track .dot{position:absolute;top:1px;left:0;width:11px;height:11px;margin-left:-5px;border-radius:50%;background:#00cc99;
  box-shadow:0 0 0 4px rgba(0,204,153,.18),0 0 18px 4px rgba(0,204,153,.45);opacity:0;}
.gx-org .track ol{position:relative;display:flex;justify-content:space-between;list-style:none;margin:0;padding:0;}
.gx-org .track li{display:flex;flex-direction:column;align-items:center;gap:9px;width:0;white-space:nowrap;font-size:13px;color:var(--muted,#9aa3ad);}
.gx-org .track li i{display:block;width:7px;height:7px;margin-top:3px;border-radius:50%;background:var(--muted,#9aa3ad);opacity:.6;}
.gx-org .track li.end{gap:6px;}
.gx-org .track li.end:first-child{align-items:flex-start;text-align:left;}
.gx-org .track li.end:last-child{align-items:flex-end;text-align:right;}
.gx-org .track li.end:first-child i{margin-left:-11px;} .gx-org .track li.end:last-child i{margin-right:-11px;}
.gx-org .track li.end i{width:22px;height:22px;margin-top:-5px;border-radius:50%;opacity:1;background:var(--card,#16191e);
  border:2px solid #f6c445;box-shadow:0 0 0 4px rgba(246,196,69,.12);}
.gx-org .track li.end i::after{content:"";display:block;width:8px;height:8px;margin:5px auto 0;border-radius:50%;background:#f6c445;}
.gx-org .track li.end b{font-size:13px;font-weight:600;color:var(--ink,#f2f4f5);} .gx-org .track li.end small{font-size:11.5px;color:#f6c445;margin-top:-6px;}
.gx-org .loop{display:block;width:100%;height:26px;margin:2px 0 0;}
.gx-org .loopk{margin:-14px 0 0;text-align:center;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted,#9aa3ad);}
.gx-org .via{margin:22px 0 0;text-align:center;font-size:12.5px;color:var(--muted,#9aa3ad);}
.gx-org .via b{font-weight:500;color:var(--ink,#f2f4f5);} .gx-org .via em{font-style:normal;opacity:.6;}
@keyframes gxRide{0%{left:0;opacity:0;}4%{opacity:1;}92%{opacity:1;}100%{left:100%;opacity:0;}}
@keyframes gxNode{0%,6%{color:var(--ink,#f2f4f5);}14%,100%{color:var(--muted,#9aa3ad);}}
@keyframes gxEnd{0%,6%{box-shadow:0 0 0 6px rgba(246,196,69,.35),0 0 18px #f6c445;}14%,100%{box-shadow:0 0 0 4px rgba(246,196,69,.12);}}
@keyframes gxNodeDot{0%,6%{background:#00cc99;opacity:1;box-shadow:0 0 10px #00cc99;}14%,100%{background:var(--muted,#9aa3ad);opacity:.6;box-shadow:none;}}
@media (prefers-reduced-motion:no-preference){
  .gx-org .track .dot{animation:gxRide 8s linear infinite;}
  .gx-org .track li{animation:gxNode 8s linear infinite;} .gx-org .track li i{animation:gxNodeDot 8s linear infinite;}
  .gx-org .track li.end i{animation:gxEnd 8s linear infinite;}
}
@media (max-width:720px){.gx-org .row{flex-direction:column;gap:22px;} .gx-org img.wire{height:22px;}
  .gx-org .ags{gap:6px;} .gx-org .ag{padding:7px 6px;gap:5px;} .gx-org .ag b{font-size:11.5px;}
  .gx-org .ag .gx-avatar{width:18px;height:18px;min-width:18px;}
  .gx-org .ags{justify-content:center;} .gx-org .ag:only-child{flex:0 1 auto;padding:7px 18px;}
  .gx-org .track{margin:18px 0 6px 6px;} .gx-org .track .dot{display:none;}
  .gx-org .track .ln{left:10px;right:auto;top:8px;bottom:8px;width:1px;height:auto;}
  .gx-org .track ol{flex-direction:column;gap:12px;}
  .gx-org .track li,.gx-org .track li.end:first-child,.gx-org .track li.end:last-child{flex-direction:row;align-items:center;width:auto;
    gap:12px;font-size:13px;text-align:left;}
  .gx-org .track li i{margin:0 7px;} .gx-org .track li.end i,.gx-org .track li.end:first-child i,.gx-org .track li.end:last-child i{margin:0;}
  .gx-org .track li.end small{margin:0;} .gx-org .loop,.gx-org .loopk{display:none;}}
</style>"""


def _wire(k: int, light: bool = False) -> str:
    """Thin lines from one person down to k agents (a bracket for k > 1), with a light pulse travelling down each line.
    An SVG image: st.html drops inline <svg>, an <img> keeps it (and its own animation)."""
    xs = [100 * (i + .5) / k for i in range(k)]
    d = [f"M50 0 V14 H{x:.2f} V34" if k > 1 else "M50 0 V34" for x in xs]
    css = ("<style>path{fill:none;vector-effect:non-scaling-stroke}.b{stroke:" + ("#0d0f12;stroke-opacity:.25" if light else
                                                                               "#ffffff;stroke-opacity:.18") + ";stroke-width:1}"
           ".p{stroke:#00cc99;stroke-width:2;stroke-linecap:round;stroke-dasharray:8 120;opacity:0}"
           "@keyframes m{0%{stroke-dashoffset:8;opacity:0}10%,70%{opacity:1}100%{stroke-dashoffset:-120;opacity:0}}"
           "@media (prefers-reduced-motion:no-preference){.p{animation:m 2.4s cubic-bezier(.4,0,.2,1) infinite}}</style>")
    paths = "".join(f'<path class="b" d="{x}"/>' for x in d) + "".join(
        f'<path class="p" d="{x}" style="animation-delay:{.35 * i:.2f}s"/>' for i, x in enumerate(d))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 34" preserveAspectRatio="none">{css}{paths}</svg>')
    return f'<img class="wire" alt="" aria-hidden="true" src="data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}">'


def org_chart(people: list[tuple], flow: list[str], tools: list[str], tool_next: str = "", light: bool = False,
              ends: tuple | None = None, loop: str = "") -> str:
    """Team and agents as one quiet org chart: people on top (photo, name, role), their agents underneath as small pills
    (logo + one or two words), thin lines with a light pulse between them, and one track for the ALTYCA case: a dot
    travels along it and lights each step as it passes (CSS only; still under reduced motion).
    people: (name, role, [(agent, logo key)]). Our own text is translated here."""
    total = sum(len(a) for _, _, a in people) or 1
    grps = []
    for name, role, agents in people:
        pills = "".join(f'<div class="ag">{_avatar(logo)}<b>{esc(i18n.tr(a))}</b></div>' for a, logo in agents)
        grps.append(f'<div class="grp" style="flex:{len(agents)} 1 0">'
                    f'<div class="hum">{_avatar(name.split()[0])}<b>{esc(name)}</b><span>{esc(i18n.tr(role))}</span></div>'
                    f'{_wire(len(agents), light)}<div class="ags">{pills}</div></div>')
    # ends: ((who, what), (who, what)) – the customer at both ends of the track (e.g. the IT manager: uploads data,
    # gets the optimisations back); drawn as people (yellow), the steps in between as dots.
    items = ([("end",) + tuple(ends[0])] if ends else []) + [("step", x, "") for x in flow] + ([("end",) + tuple(ends[1])] if ends else [])
    n = len(items)
    li = []
    for i, (kind, label, sub) in enumerate(items):
        d = f"{8 * i / max(n - 1, 1) * .92:.2f}s"
        body = (f'<b>{esc(i18n.tr(label))}</b><small>{esc(i18n.tr(sub))}</small>' if kind == "end" else esc(i18n.tr(label)))
        li.append(f'<li class="{"end" if kind == "end" else ""}" style="animation-delay:{d}"><i style="animation-delay:{d}"></i>{body}</li>')
    steps = "".join(li)
    arc = ""
    if loop:
        stroke = "#0d0f12" if light else "#ffffff"
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 26" preserveAspectRatio="none"><path d="M98 2 C98 24 2 24 2 2" '
               f'fill="none" stroke="{stroke}" stroke-opacity=".22" stroke-dasharray="2 3" vector-effect="non-scaling-stroke"/></svg>')
        arc = (f'<img class="loop" alt="" aria-hidden="true" src="data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}">'
               f'<p class="loopk">{esc(i18n.tr(loop))}</p>')
    via = " · ".join(f"<b>{esc(t)}</b>" for t in tools) + (f" · <em>{esc(tool_next)}</em>" if tool_next else "")
    return (_ORG_CSS + f'<div class="gx-org{" lt" if light else ""}">'
            f'<p class="lb">{esc(i18n.tr("Wo/Man make the decisions"))}</p>'
            f'<div class="row">{"".join(grps)}</div>'
            f'<p class="lb ag-lb">{esc(i18n.tr("Man-made agents do the leg work with real verified data"))}</p>'
            f'<div class="track"><div class="ln"></div><div class="dot"></div><ol>{steps}</ol></div>{arc}'
            f'<p class="via">{esc(i18n.tr("Talking via"))} {via}</p></div>')


def roller(words: list[str], key: str, step_s: float = 1.1, loop: bool = True, classes: list[str] | None = None) -> str:
    """Words that roll down one after another (CSS only). loop=False stops on the last word.
    Without motion the words show as one static line, so nothing is hidden."""
    n = len(words)
    cls = classes or [""] * n
    stack = "".join(f'<i class="{c}">{esc(i18n.tr(w))}</i>' if c else f"<i>{esc(i18n.tr(w))}</i>"
                    for w, c in reversed(list(zip(words, cls))))  # last word on top: the text moves down
    frames = []
    for i in range(n):
        a, b = 100 * i / n, 100 * (i + 0.72) / n
        off = (n - 1 - i) * 1.4
        frames.append(f"{a:.2f}%,{b:.2f}%{{transform:translateY(-{off:.2f}em)}}")
    if not loop:
        frames.append("100%{transform:translateY(0)}")
    total = step_s * n
    it = "infinite" if loop else "1"
    # Without motion: a loop shows every word; a one-off roll shows only where it ends.
    static = " · ".join(esc(i18n.tr(w)) for w in words) if loop else esc(i18n.tr(words[-1]))
    return (f'<span class="gx-rot gx-rot-{key}" aria-label="{static}"><span class="w" aria-hidden="true">{stack}</span>'
            f'<span class="gx-rot-static">{static}</span></span>'
            f"<style>@keyframes gxRoll{key}{{{''.join(frames)}}}"
            f"@media (prefers-reduced-motion:no-preference){{.gx-rot-{key} .w{{transform:translateY(-{(n - 1) * 1.4:.2f}em);"
            f"animation:gxRoll{key} {total:.1f}s cubic-bezier(.6,0,.2,1) .3s {it} both}}}}</style>")


def logo(filename: str, alt: str, height: int = 56) -> str:
    """A partner logo from app/static/<filename>, inlined (any size, shrunk). Missing or unreadable: the name as text."""
    path = _IMG_DIR.parent / filename
    if path.is_file():
        got = _logo_b64(str(path), path.stat().st_mtime)
        if got:
            b64, mime = got
            return f'<img class="gx-partner" style="height:{height}px" src="data:{mime};base64,{b64}" alt="{esc(alt)}">'
    return f'<span class="gx-partner-txt">{esc(alt)}</span>'


@st.cache_data(show_spinner=False)
def _logo_b64(path_str: str, mtime: float) -> tuple[str, str] | None:
    try:
        import io
        from PIL import Image, ImageOps
        from PIL import ImageChops
        img = ImageOps.exif_transpose(Image.open(path_str))
        # Trim empty margins (transparent or near-white), so a small mark on a big canvas still reads.
        rgba = img.convert("RGBA")
        flat = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        flat.alpha_composite(rgba)  # transparent parts count as white
        diff = ImageChops.difference(flat.convert("RGB"), Image.new("RGB", rgba.size, (255, 255, 255))).convert("L")
        box = diff.point(lambda v: 255 if v > 24 else 0).getbbox()
        if box:
            pad = max(6, (box[3] - box[1]) // 6)
            img = flat.crop((max(0, box[0] - pad), max(0, box[1] - pad), min(rgba.width, box[2] + pad),
                             min(rgba.height, box[3] + pad))).convert("RGB")
        img.thumbnail((480, 200))
        buf = io.BytesIO()
        if img.mode in ("RGBA", "LA", "P"):
            img.convert("RGBA").save(buf, "PNG", optimize=True)
            return base64.b64encode(buf.getvalue()).decode(), "image/png"
        img.convert("RGB").save(buf, "JPEG", quality=85, optimize=True)
        return base64.b64encode(buf.getvalue()).decode(), "image/jpeg"
    except Exception:
        return None


def confetti(n: int = 70) -> str:
    """CSS-only confetti that falls once over the page (≈3 s). Off under reduced motion. Positions are fixed
    (no randomness), so every visit looks the same and tests stay stable."""
    colours = ["#00cc99", "#ffd166", "#f84aa7", "#9ec0dc", "#ffffff"]
    bits = []
    for i in range(n):
        left = (i * 37) % 100
        delay = (i * 53 % 900) / 1000
        dur = 2.2 + (i * 29 % 140) / 100
        rot = (i * 71) % 360
        w, h = (8, 14) if i % 3 else (10, 10)
        bits.append(f'<i style="left:{left}%;background:{colours[i % len(colours)]};width:{w}px;height:{h}px;'
                    f'animation-delay:{delay:.2f}s;animation-duration:{dur:.2f}s;transform:rotate({rot}deg)"></i>')
    return f'<div class="gx-confetti" aria-hidden="true">{"".join(bits)}</div>'


def breakdown_pop(title: str, parts: list[tuple[str, float]], unit: str, note: str = "") -> str:
    """A pop-out with one horizontal stacked bar (one colour per part) and a legend. Values are passed in."""
    colours = ["#00cc99", "#9ec0dc", "#ffd166", "#f84aa7", "#c4cad1"]
    total = sum(v for _, v in parts) or 1.0
    seg = "".join(f'<i style="width:{100 * v / total:.2f}%;background:{colours[i % len(colours)]}"></i>'
                  for i, (_, v) in enumerate(parts))
    leg = "".join(f'<li><b style="background:{colours[i % len(colours)]}"></b>{esc(i18n.tr(n))}'
                  f'<span>{v:,.2f} {esc(unit)} · {100 * v / total:.0f} %</span></li>' for i, (n, v) in enumerate(parts))
    nt = f'<p class="nt">{esc(i18n.tr(note, label=False))}</p>' if note else ""
    return (f'<div class="gx-pop" role="tooltip"><p class="tt">{esc(i18n.tr(title))}</p>'
            f'<div class="bar">{seg}</div><ul>{leg}</ul>{nt}</div>')


def upload_sim(files: list[str], extra: int, total: int) -> str:
    """Simulated upload: the real file names drop into a box one by one, a bar fills, then «N files received».
    CSS only, about 1.8 s; without motion it shows the end state."""
    chips = "".join(f'<span class="chip" style="animation-delay:{0.06 * i:.2f}s">{esc(f)}</span>'
                    for i, f in enumerate(files))
    more = f'<span class="chip more" style="animation-delay:{0.06 * len(files):.2f}s">+{extra} extra</span>' if extra else ""
    return (f'<div class="gx-upsim"><div class="hd"><span class="ic">↑</span> ALTYCA-case.json '
            f'<span class="ok">{total} {esc(i18n.tr("files received"))} ✓</span></div>'
            f'<div class="chips">{chips}{more}</div><div class="prog"><i></i></div></div>')


def agent_terminal(title: str, command: str, lines: list[tuple[str, str]], done_html: str, start: float = 1.6) -> str:
    """Claude-Code-like run: the command types itself, a «✻ Working…» line spins while each step appears with its
    result, then the result line pops in. CSS only (≈ start + 0.45 s per line); without motion everything shows."""
    step = 0.35
    rows = []
    t = start + 0.6
    for k, v in lines:
        rows.append(f'<p class="ln" style="animation-delay:{t:.2f}s"><span class="pr">●</span> <b>{esc(i18n.tr(k))}</b> '
                    f'{esc(v)}</p>')
        t += step
    work_end = t
    return (f'<div class="gx-term gx-agent"><div class="bar"><i></i><i></i><i></i><span>{esc(title)}</span></div>'
            f'<div class="body"><p class="cmd" style="animation-delay:{start:.2f}s"><span class="pr">&gt;</span> '
            f'<span class="typed" style="animation-delay:{start:.2f}s">{esc(command)}</span></p>'
            f'<p class="work" style="animation-delay:{start + 0.5:.2f}s,{work_end:.2f}s"><span class="spin">✻</span> '
            f'{esc(i18n.tr("Working"))}<span class="dots">…</span></p>'
            f'{"".join(rows)}'
            f'<p class="ok result ln" style="animation-delay:{work_end + 0.1:.2f}s"><span class="pr">✓</span> {done_html}</p>'
            f'</div></div>')


def sources(items: list[tuple[str, str]]) -> None:
    """«Sources» footer at the bottom of a page: numbered, what each number rests on and where it comes from."""
    if not items:
        return
    rows = "".join(f'<li><b>{esc(i18n.tr(what))}</b> – {esc(src)}</li>' for what, src in items)
    _raw(f'<div class="gx-sources"><p class="tt">{esc(i18n.tr("Sources"))}</p><ol>{rows}</ol></div>')


def terminal(title: str, lines: list[tuple[str, str]], done: str, done_html: str = "") -> str:
    """A small terminal block: one «> step  detail» line each, a done line at the end. Big mono type, few words."""
    rows = "".join(f'<p><span class="pr">&gt;</span> <b>{esc(i18n.tr(k))}</b> {esc(v)}</p>' for k, v in lines)
    return (f'<div class="gx-term gx-check"><div class="bar"><i></i><i></i><i></i><span>{esc(title)}</span></div>'
            f'<div class="body">{rows}<p class="ok{" result" if done_html else ""}"><span class="pr">✓</span> '
            f'{done_html or esc(i18n.tr(done))}</p></div></div>')


def activity_log(title: str, rows: list[tuple[str, str, str]], summary: str) -> str:
    """Claude-Code-like log: one line per file, ● green = clean, amber = needs a person, red = blocked."""
    icon = {"ok": "✓", "warn": "!", "bad": "✗"}
    lines = "".join(f'<p class="{st_}"><span class="pr">{icon.get(st_, "·")}</span> <b>{esc(f)}</b> '
                    f'<span class="note">{marks(esc(note))}</span></p>' for st_, f, note in rows)
    return (f'<div class="gx-term gx-log gx-check"><div class="bar"><i></i><i></i><i></i><span>{esc(title)}</span></div>'
            f'<div class="body"><p class="cmd"><span class="pr">&gt;</span> check every file, flag what needs a human</p>'
            f'{lines}<p class="ok sum"><span class="pr">●</span> {esc(summary)}</p></div></div>')


def story_bar(step: int, total: int, label: str) -> None:
    pct = int(round(100 * step / total))
    _raw(f'<div class="gx-story" role="progressbar" aria-valuenow="{step}" aria-valuemin="0" aria-valuemax="{total}" '
            f'aria-label="Story progress"><span class="s">Step {step} of {total}</span>'
            f'<div class="bar"><i style="width:{pct}%"></i></div><span class="s">{label}</span></div>')
