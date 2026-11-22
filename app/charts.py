"""Chart helpers (Altair). Follows the dataviz method: form first, colour by job, fixed slot order,
thin marks (<= 24px bars, 4px rounded data-end), recessive hairline grid, text in ink tokens,
tooltip on every mark, table view next to every chart. Light and dark steps are chosen separately.
"""
from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

# Two accents only: green for the data, ink-blue when a second series is unavoidable.
# Green / amber / red are reserved for pass, close and miss. They are not used as series colours.
PALETTE = {
    # R9 palette, aligned with theme.py. Teal #00cc99 is the dark-mode data colour.
    # Light bars use #007a5c: #00cc99 on white is 2.1:1, and the gauge paints white type on STATUS.
    # Pink is not a series colour. Refusals use theme.PINK (#f84aa7) in theme.py only.
    "light": {
        "surface": "#ffffff", "ink": "#0d0f12", "ink2": "#24303a", "muted": "#3a4450",
        "grid": "#d5dbe1", "axis": "#8b97a3",
        "series": ["#d8f6ee", "#9ee8d4", "#4ecfb0", "#00a37c", "#007a5c", "#084e3c"],
        "accent": "#007a5c", "accent2": "#1f4e73", "track": "#e5f6f1", "other": "#b7c0c8",
    },
    "dark": {
        "surface": "#16191e", "ink": "#f5f6f7", "ink2": "#d5dbe1", "muted": "#b4bec8",
        "grid": "#2c333c", "axis": "#46505a",
        "series": ["#0c3d32", "#0e5c48", "#0a8064", "#00a37c", "#00cc99", "#b8f6e4"],
        "accent": "#00cc99", "accent2": "#9ec0dc", "track": "#1a2e2a", "other": "#46505a",
    },
}
# good is the darker teal: gauge pills set color:#ffffff on this fill, and white on #00cc99 is 2.1:1.
# #007a5c with white is 5.3:1. The big PASS number stays #00cc99 via theme.TEAL on the near-black ground.
STATUS = {"good": "#007a5c", "warning": "#b8860b", "serious": "#b86a2a", "critical": "#b42318"}
FONT = 'Manrope, system-ui, -apple-system, "Segoe UI", sans-serif'
# Inline HTML styles cannot contain a double quote: Streamlit's sanitizer ends the attribute there.
FONT_INLINE = "Manrope, system-ui, -apple-system, Segoe UI, sans-serif"


def mode() -> str:
    """R9: dark (ALTYCA) unless the presenter switches on light mode for a washed-out projector."""
    try:
        return "light" if st.session_state.get("light_mode", False) else "dark"
    except Exception:  # no session (plain import in a test)
        return "dark"


def pal() -> dict:
    return PALETTE[mode()]


def _style(chart: alt.Chart) -> alt.Chart:
    p = pal()
    return (
        chart.configure(background="transparent", font=FONT)
        .configure_view(stroke=None)
        .configure_axis(
            labelColor=p["ink2"], titleColor=p["ink2"], gridColor=p["grid"], gridWidth=1,
            domainColor=p["axis"], tickColor=p["axis"], labelFontSize=16, titleFontSize=16, titleFontWeight="normal",
        )
        .configure_legend(labelColor=p["ink2"], titleColor=p["ink2"], orient="top", title=None, labelFontSize=16)
    )


def chf_axis(title: str = "CHF per year") -> alt.Axis:
    """Axis with plain thousands separators (1,200 not 1.2K), the same format as every label on the page."""
    return alt.Axis(title=title, format=",.0f", tickCount=5, labelFontSize=14, titleFontSize=15)


def _amount_text(v: float, unit: str) -> str:
    if unit == "CHF":
        return f"CHF {v:,.0f}"
    if unit == "kg":
        return f"{v:,.0f} kg"
    if unit == "kWh":
        return f"{v:,.0f} kWh"
    return f"{v:,.0f} {unit}"


def ranked_bars(df: pd.DataFrame, label: str = "label", value: str = "cost_chf", highlight: set | None = None,
                tooltip_extra: list | None = None, height_per_row: int = 36, unit: str = "CHF",
                axis_title: str | None = None) -> alt.Chart:
    """Ranked horizontal bars, one hue (magnitude). Optional emphasis: highlighted labels in accent, rest gray."""
    p = pal()
    d = df.copy()
    d["_chf"] = d[value].map(lambda v: _amount_text(float(v), unit))
    d["_share"] = d["share"].map(lambda v: f"{v * 100:.1f} %") if "share" in d else ""
    if highlight:
        d["_hl"] = d[label].isin(highlight)
        color = alt.condition("datum._hl", alt.value(p["accent"]), alt.value(p["other"]))
    else:
        color = alt.value(p["accent"])
    tips = [alt.Tooltip(f"{label}:N", title="Group"), alt.Tooltip("_chf:N", title=unit), alt.Tooltip("_share:N", title="Share")]
    tips += tooltip_extra or []
    order = list(d[label])
    base = alt.Chart(d).encode(y=alt.Y(f"{label}:N", sort=order, title=None, axis=alt.Axis(labelLimit=420, domain=False, ticks=False, labelPadding=10, labelColor=PALETTE[mode()]["ink2"], labelFontSize=16)))
    axis = chf_axis(axis_title or ("CHF per year" if unit == "CHF" else f"{unit} per year"))
    # Room right of the longest bar so its value label is never clipped.
    xmax = float(d[value].max()) if len(d) else 0.0
    scale = alt.Scale(domain=[0, xmax * 1.18], nice=False) if xmax > 0 else alt.Scale(nice=True)
    bars = base.mark_bar(size=18, cornerRadiusEnd=4).encode(
        x=alt.X(f"{value}:Q", axis=axis, scale=scale), color=color, tooltip=tips,
    )
    # value at the tip: every bar when the chart is short (up to 6 rows), else the top 3
    top = d if len(d) <= 6 else d.head(3)
    text = alt.Chart(top).mark_text(align="left", dx=6, color=p["ink2"], fontSize=16).encode(
        y=alt.Y(f"{label}:N", sort=order), x=f"{value}:Q", text="_chf:N",
    )
    return _style((bars + text).properties(height=max(120, height_per_row * len(d))))


def monthly_stack(df: pd.DataFrame, order: list[str]) -> alt.Chart:
    """Stacked columns per month, one fixed categorical slot per source (colour follows the entity)."""
    p = pal()
    d = df.copy()
    d["_chf"] = d["cost_chf"].map(lambda v: f"CHF {v:,.0f}")
    d["_order"] = d["source_label"].map({s: i for i, s in enumerate(order)})
    color = alt.Color("source_label:N", scale=alt.Scale(domain=order, range=p["series"][: len(order)]),
                      legend=alt.Legend(orient="top", direction="horizontal", symbolType="square"))
    chart = alt.Chart(d).mark_bar(size=22, stroke=p["surface"], strokeWidth=2).encode(
        x=alt.X("month:O", title=None, axis=alt.Axis(labelAngle=0, labelExpr="slice(datum.label, 2)")),
        y=alt.Y("sum(cost_chf):Q", axis=chf_axis("CHF per month"), stack="zero"),
        color=color,
        order=alt.Order("_order:Q", sort="ascending"),
        tooltip=[alt.Tooltip("month:O", title="Month"), alt.Tooltip("source_label:N", title="Source"),
                 alt.Tooltip("_chf:N", title="Cost")],
    )
    return _style(chart.properties(height=300))


STATUS_ICON = {"good": ("✓", "Pass"), "critical": ("✕", "Miss"), "warning": ("!", "Close"),
               "pending": ("…", "Pending")}


def _ring(pct_fill: float, status: str, center: str, sub: str, size: int, caption: str) -> str:
    """CSS donut. Streamlit's HTML sanitizer drops SVG, so the ring is a conic-gradient.

    pct_fill is 0–1 of the track. The state colour is the arc; Pass/Miss is also written out.
    """
    p = pal()
    fill = max(0.0, min(1.0, pct_fill)) * 100
    state = STATUS.get(status, p["other"]) if status != "pending" else p["other"]
    icon, label = STATUS_ICON.get(status, ("…", "Pending"))
    hole = int(size * 0.68)
    return (
        f'<div style="flex:0 0 auto;text-align:center;font-family:{FONT_INLINE};color:{p["ink"]}">'
        f'<div role="img" aria-label="{caption}: {center}, {label}" '
        f'style="width:{size}px;height:{size}px;border-radius:50%;margin:0 auto;'
        f'background:conic-gradient({state} 0 {fill:.1f}%, {p["track"]} {fill:.1f}% 100%);'
        f'display:flex;align-items:center;justify-content:center;">'
        f'<div style="width:{hole}px;height:{hole}px;border-radius:50%;background:{p["surface"]};'
        f'display:flex;flex-direction:column;align-items:center;justify-content:center;">'
        f'<div style="font-size:{int(size * 0.15)}px;font-weight:700;line-height:1;'
        f'font-variant-numeric:tabular-nums;letter-spacing:-.02em">{center}</div>'
        f'<div style="font-size:{max(16, int(size * 0.075))}px;color:{p["ink2"]};margin-top:6px">{sub}</div></div></div>'
        f'<div style="font-size:24px;font-weight:700;margin-top:12px">{caption}</div>'
        f'<div style="display:inline-block;margin-top:8px;padding:6px 18px;border-radius:999px;background:{state};'
        f'color:{"#0d0f12" if status in ("warning", "good") else "#ffffff"};font-size:24px;font-weight:800;letter-spacing:.08em">'
        f'{icon} {label.upper()}</div></div>'
    )


def verdict_html(passed: int, total: int, level: str) -> str:
    """One line above the gauges, readable from the back of the room. Text, not colour only."""
    p = pal()
    ok = passed == total
    bg = STATUS["good"] if ok else STATUS["critical"]
    text = (f"✓ All {total} targets met" if ok else f"✕ {total - passed} of {total} targets missed")
    return (
        f'<div style="font-family:{FONT_INLINE};display:flex;flex-wrap:wrap;align-items:baseline;gap:14px;margin:4px 0 10px">'
        f'<span style="background:{bg};color:{"#0d0f12" if ok else "#ffffff"};border-radius:10px;padding:8px 20px;font-size:30px;font-weight:800">{text}</span>'
        f'<span style="color:{p["ink2"]};font-size:20px">{level} factors</span></div>'
    )


def gauge_board_html(co2: dict, cost: dict, effort: dict) -> str:
    """Three equal rings in one row, CO₂ first: each value and PASS/MISS is readable on a projector from 3 m."""
    p = pal()
    rings = [_ring(g["fill"], g["status"], g["center"], g["sub"], 250, g["caption"]) for g in (co2, cost, effort)]
    cells = "".join(f'<div style="flex:1 1 260px;display:flex;justify-content:center">{r}</div>' for r in rings)
    return (
        f'<div style="display:flex;flex-wrap:wrap;align-items:flex-start;gap:24px;font-family:{FONT_INLINE};'
        f'color:{p["ink"]}">{cells}</div>'
    )


def meter_list_html(rows: list[dict]) -> str:
    """Meter list: name · bar · figure · status per row (flex rows, fixed side widths so bars align).

    Track is a lighter step of the fill's ramp; a 2px ink tick marks the target. Status never colour-only:
    icon + label beside it. rows: {name, value, target, max, value_txt, target_txt, status, note}.
    """
    p = pal()
    fill_of = {"good": p["accent"], "warning": STATUS["warning"], "critical": STATUS["critical"], "pending": p["other"]}
    out = [f'<div style="font-family:{FONT};margin:8px 0 4px">']
    for r in rows:
        w = 0 if r["max"] <= 0 else max(0.0, min(1.0, r["value"] / r["max"])) * 100
        t = 0 if r["max"] <= 0 else min(1.0, r["target"] / r["max"]) * 100
        icon, label = STATUS_ICON[r["status"]]
        out.append(
            '<div style="display:flex;align-items:center;gap:16px;margin:0 0 18px 0">'
            f'<div style="flex:0 0 220px;color:{p["ink"]};font-size:15px;font-weight:600">{r["name"]}'
            f'<div style="color:{p["muted"]};font-size:12px;font-weight:400">{r.get("note", "")}</div></div>'
            f'<div role="meter" aria-label="{r["name"]}: {r["value_txt"]} of required {r["target_txt"]}" '
            f'style="flex:1 1 auto;position:relative;height:14px;border-radius:7px;background:{p["track"]}">'
            f'<div style="width:{w:.1f}%;height:100%;border-radius:7px;background:{fill_of[r["status"]]}"></div>'
            f'<div title="Target {r["target_txt"]}" style="position:absolute;left:calc({t:.1f}% - 1px);top:-6px;width:2px;height:26px;background:{p["ink"]}"></div></div>'
            f'<div style="flex:0 0 150px;color:{p["ink"]};font-size:15px;font-variant-numeric:tabular-nums">{r["value_txt"]}'
            f'<span style="color:{p["muted"]};font-size:12px"> / {r["target_txt"]}</span></div>'
            f'<div style="flex:0 0 120px;color:{p["ink2"]};font-size:13px"><span style="display:inline-block;width:18px;height:18px;border-radius:9px;'
            f'background:{fill_of[r["status"]]};color:{"#0b0b0b" if r["status"] in ("warning", "good") else "#ffffff"};text-align:center;line-height:18px;'
            f'font-size:11px;margin-right:6px">{icon}</span>{label}</div></div>'
        )
    out.append("</div>")
    return "".join(out)


def optimisation_map(df: pd.DataFrame, x_title: str = "CO₂ saved (kg per year)", y_title: str = "CHF saved per year",
                     size_title: str = "Person-days", room_right: bool = False) -> alt.Chart:
    """CO₂ against CHF per optimisation, one hue. Columns: co2, chf, pd, label, name. Dot size = person-days.
    Licence optimisations sit on the y-axis (0 kg): that is correct, they save francs only."""
    p = pal()
    d = df.copy()
    d["_co2"] = d["co2"].map(lambda v: f"{v:,.0f} kg")
    d["_chf"] = d["chf"].map(lambda v: f"CHF {v:,.0f}")
    d["_pd"] = d["pd"].map(lambda v: f"{v:.1f}")
    xmax = float(d["co2"].max()) if len(d) else 0.0
    ymax = float(d["chf"].max()) if len(d) else 0.0
    xpad = 1.95 if room_right else 1.35  # room_right: the right 40 % stays free for the reading card
    xs = alt.Scale(domain=[0, xmax * xpad if xmax else 1], nice=False)
    ys = alt.Scale(domain=[0, ymax * 1.15 if ymax else 1], nice=False)
    tips = [alt.Tooltip("name:N", title="Optimisation"), alt.Tooltip("_co2:N", title="CO₂"),
            alt.Tooltip("_chf:N", title="CHF"), alt.Tooltip("_pd:N", title=size_title)]
    base = alt.Chart(d).encode(
        x=alt.X("co2:Q", scale=xs, axis=alt.Axis(title=x_title, format=",.0f", tickCount=4, labelFontSize=14, titleFontSize=15)),
        y=alt.Y("chf:Q", scale=ys, axis=chf_axis(y_title)),
    )
    dots = base.mark_circle(color=p["accent"], opacity=0.85, stroke=p["surface"], strokeWidth=1).encode(
        size=alt.Size("pd:Q", scale=alt.Scale(range=[80, 900]), legend=alt.Legend(title=size_title, orient="top", values=[0.5, 1.5, 3.0])),
        tooltip=tips,
    )
    # Greedy label placement: from the top, each label sits just above its dot unless a label close by on the
    # x-axis is within one line; then it moves one line down. Positions only; the dots stay on their values.
    height, line = 400, 22.0  # the plot area is shorter than the chart, so one text line is ~22 chart px
    ydom = ymax * 1.15 if ymax else 1.0
    xdom = xmax * xpad if xmax else 1.0
    px = height / ydom
    placed, label_y = [], {}
    for i, r in d.sort_values("chf", ascending=False).iterrows():
        ly = (ydom - float(r["chf"])) * px - 9
        xf = float(r["co2"]) / xdom
        moved = True
        while moved:
            moved = False
            for qx, qy in placed:
                if abs(qx - xf) < 0.3 and abs(qy - ly) < line:
                    ly, moved = qy + line, True
        placed.append((xf, ly))
        label_y[i] = ydom - ly / px
    d["_ly"] = pd.Series(label_y)
    right = d["co2"] / xdom >= (0.45 if room_right else 0.6)  # far-right labels go left: no clipping, no card overlap
    enc = dict(x=alt.X("co2:Q", scale=xs), y=alt.Y("_ly:Q", scale=ys), text="label:N")
    t_l = alt.Chart(d[~right]).mark_text(align="left", dx=11, baseline="middle", color=p["ink2"], fontSize=13).encode(**enc)
    t_r = alt.Chart(d[right]).mark_text(align="right", dx=-11, baseline="middle", color=p["ink2"], fontSize=13).encode(**enc)
    return _style((dots + t_l + t_r).properties(height=height))
