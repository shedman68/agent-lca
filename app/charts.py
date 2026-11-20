"""Chart helpers (Altair). Follows the dataviz method: form first, colour by job, fixed slot order,
thin marks (<= 24px bars, 4px rounded data-end), recessive hairline grid, text in ink tokens,
tooltip on every mark, table view next to every chart. Light and dark steps are chosen separately.
"""
from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

PALETTE = {
    "light": {
        "surface": "#fcfcfb", "ink": "#0b0b0b", "ink2": "#52514e", "muted": "#898781",
        "grid": "#e1e0d9", "axis": "#c3c2b7",
        "series": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"],
        "accent": "#2a78d6", "track": "#cde2fb", "other": "#c3c2b7",
    },
    "dark": {
        "surface": "#1a1a19", "ink": "#f0efec", "ink2": "#c3c2b7", "muted": "#898781",
        "grid": "#2c2c2a", "axis": "#383835",
        "series": ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#0ca30c", "#9085e9", "#e66767"],
        "accent": "#3987e5", "track": "#184f95", "other": "#52514e",
    },
}
STATUS = {"good": "#0ca30c", "warning": "#fab219", "serious": "#ec835a", "critical": "#d03b3b"}
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'


def mode() -> str:
    try:
        return "dark" if st.context.theme.type == "dark" else "light"
    except Exception:  # older Streamlit or no theme info
        return "light"


def pal() -> dict:
    return PALETTE[mode()]


def _style(chart: alt.Chart) -> alt.Chart:
    p = pal()
    return (
        chart.configure(background="transparent", font=FONT)
        .configure_view(stroke=None)
        .configure_axis(
            labelColor=p["muted"], titleColor=p["ink2"], gridColor=p["grid"], gridWidth=1,
            domainColor=p["axis"], tickColor=p["axis"], labelFontSize=12, titleFontSize=12, titleFontWeight="normal",
        )
        .configure_legend(labelColor=p["ink2"], titleColor=p["ink2"], orient="top", title=None, labelFontSize=12)
    )


def chf_axis(title: str = "CHF per year") -> alt.Axis:
    return alt.Axis(title=title, format="~s", labelExpr="datum.value == 0 ? '0' : replace(datum.label, 'k', 'K')", tickCount=5)


def ranked_bars(df: pd.DataFrame, label: str = "label", value: str = "cost_chf", highlight: set | None = None,
                tooltip_extra: list | None = None, height_per_row: int = 30) -> alt.Chart:
    """Ranked horizontal bars, one hue (magnitude). Optional emphasis: highlighted labels in accent, rest gray."""
    p = pal()
    d = df.copy()
    d["_chf"] = d[value].map(lambda v: f"CHF {v:,.0f}")
    d["_share"] = d["share"].map(lambda v: f"{v:.1%}") if "share" in d else ""
    if highlight:
        d["_hl"] = d[label].isin(highlight)
        color = alt.condition("datum._hl", alt.value(p["accent"]), alt.value(p["other"]))
    else:
        color = alt.value(p["accent"])
    tips = [alt.Tooltip(f"{label}:N", title="Group"), alt.Tooltip("_chf:N", title="Cost"), alt.Tooltip("_share:N", title="Share")]
    tips += tooltip_extra or []
    order = list(d[label])
    base = alt.Chart(d).encode(y=alt.Y(f"{label}:N", sort=order, title=None, axis=alt.Axis(labelLimit=260, domain=False, ticks=False, labelPadding=8, labelColor=PALETTE[mode()]["ink2"])))
    bars = base.mark_bar(size=18, cornerRadiusEnd=4).encode(
        x=alt.X(f"{value}:Q", axis=chf_axis(), scale=alt.Scale(nice=True)), color=color, tooltip=tips,
    )
    # value at the tip: label only the top 3 (selective), rest via axis + tooltip + table
    top = d.head(3)
    text = alt.Chart(top).mark_text(align="left", dx=6, color=p["ink2"], fontSize=12).encode(
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


STATUS_ICON = {"good": ("✓", "Target met"), "critical": ("✕", "Not met"), "warning": ("!", "Close"),
               "pending": ("…", "Pending")}


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
            f'background:{fill_of[r["status"]]};color:{"#0b0b0b" if r["status"] == "warning" else "#ffffff"};text-align:center;line-height:18px;'
            f'font-size:11px;margin-right:6px">{icon}</span>{label}</div></div>'
        )
    out.append("</div>")
    return "".join(out)
