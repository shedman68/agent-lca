"""GreenOps Basel: cost, energy and CO2 of cloud, servers, AI and SaaS.

Run from the repo root:  python -m streamlit run app/app.py
Reads only out/ (pipeline output) and analysis/kb/ (findings, reconciliation). See app/README.md.
Free text in the data is shown as data on the "Needs a human" page and never acted on.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import assistant  # noqa: E402
import charts  # noqa: E402
import format_num  # noqa: E402
import data  # noqa: E402
import i18n  # noqa: E402
import register  # noqa: E402

st.set_page_config(page_title="GreenOps Basel", page_icon="🌿", layout="wide")
i18n.install(st)  # German toggle in the sidebar; English mode changes nothing

CITE = "Sample data ALTYCA, sprintd Basel 2026"
# Case targets (AGENTS.md). These are the decision rules, not figures measured from out/.
CO2_TARGET = data.TARGETS["co2_pct"]
COST_TARGET = data.TARGETS["cost_pct"]
PD_CAP = data.TARGETS["pd_max"]

st.markdown(
    """
    <style>
    html, body, .stApp, .stMarkdown p, .stMarkdown li, label, [data-testid="stCaptionContainer"] p {font-size: 16px;}
    .stMarkdown p, .stMarkdown li, [data-testid="stCaptionContainer"] p {line-height: 1.5;}
    [data-testid="stSidebar"] {min-width: 19rem;}
    h1 {font-size: 2.15rem !important; letter-spacing: -0.03em; font-weight: 700; margin-bottom: 0.2rem !important;}
    h2 {font-size: 1.3rem !important; font-weight: 650; margin-top: 1.5rem !important; margin-bottom: 0.45rem !important;}
    h3 {font-size: 1.12rem !important; font-weight: 650; margin-top: 1.15rem !important; margin-bottom: 0.35rem !important;}
    [data-testid="stMetricValue"] {font-size: 1.85rem; font-weight: 700; font-variant-numeric: tabular-nums; letter-spacing: -0.02em;}
    [data-testid="stMetricLabel"] {font-size: 0.78rem; letter-spacing: 0.04em; text-transform: uppercase; opacity: 0.75;}
    [data-testid="stMetric"] {padding: 0.15rem 0 0.35rem;}
    .block-container {padding-top: 1.35rem; padding-bottom: 3rem; max-width: 1180px;}
    @media (max-width: 720px) {
      [data-testid="stSidebar"] {min-width: 0 !important;}
      h1 {font-size: 1.6rem !important;}
      .block-container {padding-top: 0.85rem; padding-left: 0.7rem; padding-right: 0.7rem;}
      [data-testid="stHorizontalBlock"] {flex-wrap: wrap !important;}
      [data-testid="stColumn"] {width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important;}
      .stButton > button {min-height: 44px; height: auto; white-space: normal; text-align: left;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def chf(v: float | None, digits: int = 0) -> str:
    return "–" if v is None or pd.isna(v) else f"CHF {v:,.{digits}f}"


def _missing(v) -> bool:
    return v is None or pd.isna(v)


def _tonnes(v) -> str:
    """Tonnes from kg. A missing factor level stays an em dash, never a guessed 0."""
    return "–" if _missing(v) else f"{float(v) / 1000:,.1f}"


def _kwh_text(v) -> str:
    return "–" if _missing(v) else f"{float(v):,.0f}"


def compact_chf(v: float) -> str:
    return f"CHF {v / 1000:,.1f}K" if abs(v) < 1e6 else f"CHF {v / 1e6:,.2f}M"


def pct_share(v, digits: int = 1) -> str:
    """A 0–1 share as '35.9 %'. Presentation only: the figure is unchanged."""
    return "–" if _missing(v) else f"{float(v) * 100:,.{digits}f} %"


def _kpi_card(label: str, value: str, unit: str = "", hint: str = "", *, unit_first: bool = False) -> str:
    """One KPI tile: small muted label, big number, small unit, optional hint. No logic."""
    p = charts.pal()
    bg = "#eef4f1" if charts.mode() == "light" else p["track"]
    ink = "#0f1512" if charts.mode() == "light" else p["ink"]
    unit_span = (
        f'<span style="font-size:15px;font-weight:600;letter-spacing:0;color:{p["muted"]};'
        f'vertical-align:middle">{{u}}</span>'
    )
    if unit and unit_first:
        number = f'{unit_span.format(u=unit)}&nbsp;{value}'
    elif unit:
        number = f'{value}&nbsp;{unit_span.format(u=unit)}'
    else:
        number = value
    hint_html = (
        f'<div style="font-size:13px;color:{p["muted"]};margin-top:8px;line-height:1.4">{hint}</div>'
        if hint else ""
    )
    return (
        f'<div style="flex:1 1 200px;min-width:min(180px, 100%);padding:18px 20px 16px;border-radius:12px;'
        f'background:{bg};border:1px solid {p["grid"]};font-family:{charts.FONT_INLINE};color:{ink}">'
        f'<div style="font-size:12px;letter-spacing:.06em;text-transform:uppercase;font-weight:600;'
        f'color:{p["muted"]};line-height:1.35;margin:0 0 10px;min-height:2.7em">{label}</div>'
        f'<div style="font-size:34px;font-weight:700;line-height:1.08;letter-spacing:-.03em;'
        f'font-variant-numeric:tabular-nums;color:{ink}">{number}</div>'
        f'{hint_html}</div>'
    )


def _kpi_row(*cards: str) -> str:
    return (
        f'<div style="display:flex;flex-wrap:wrap;gap:16px;margin:6px 0 14px;'
        f'align-items:stretch">{"".join(cards)}</div>'
    )


def _qty(v, digits: int = 0) -> str:
    return "–" if _missing(v) else f"{float(v):,.{digits}f}"


def table_view(df: pd.DataFrame, label: str = "Table view") -> None:
    with st.expander(label):
        st.dataframe(df, hide_index=True, width="stretch")


def out_ready() -> bool:
    """Stop the page with a clear message when pipeline output is missing. Never substitute a number."""
    try:
        totals = data.energy_totals()
    except FileNotFoundError as exc:
        st.error(f"The numbers file is missing: {exc}. From the repo root run "
                 "`python3 pipeline/pipeline.py --data data --out out`, then "
                 "`python3 analysis/findings.py --data data --out out` and "
                 "`python3 measures/measures.py --out out`.")
        return False
    try:
        data.aligned_baseline()
    except ValueError as exc:  # the two out/ files do not line up row by row: stop, never guess a split
        st.error(str(exc))
        return False
    if totals.get("co2_mid") is None:
        st.error("out/fact_costs.csv has no CO2 column yet. Fill factors/factors.csv and rerun the pipeline. "
                 "This page will not estimate a figure.")
        return False
    return True


def factor_level() -> str:
    """Low / mid / high factors. The label is the jury question: they may recalculate on another set."""
    st.caption("Low, mid and high are three factor sets. The cards use the one you pick. Cost does not change.")
    choice = st.segmented_control(
        "What the jury might recalculate",
        ["Low factors", "Mid factors", "High factors"],
        default="Mid factors",
        key="factor_level_label",
    )
    return {"Low factors": "low", "Mid factors": "mid", "High factors": "high"}.get(choice or "Mid factors", "mid")


def _hero_html(facts_now: dict, level: str) -> str:
    level_label = {"low": "Low factors", "mid": "Mid factors", "high": "High factors"}[level]
    return _kpi_row(
        _kpi_card(
            "CO2 per year",
            _tonnes(facts_now["co2_level"]),
            "t",
            f'Location-based: electricity mix of the country where it runs, not a green certificate. '
            f'{level_label}. Range {_tonnes(facts_now["co2_low"])}–{_tonnes(facts_now["co2_high"])} t',
        ),
        _kpi_card(
            f'Energy ({level})',
            _kwh_text(facts_now["kwh_level"]),
            "kWh",
            f'Range {_kwh_text(facts_now["kwh_low"])}–{_kwh_text(facts_now["kwh_high"])} kWh',
        ),
        _kpi_card(
            "Cost",
            _qty(facts_now["cost_chf"]),
            "CHF",
            "Same on every factor set",
            unit_first=True,
        ),
    )


def _overview_sentence(facts_now: dict) -> str:
    return (
        f"{facts_now['top_country']} accounts for {pct_share(facts_now['top_country_share'])} of the CO2, "
        f"and {facts_now['top_resource']} is the largest resource at {pct_share(facts_now['top_resource_share'])}."
    )


# =============================================================================== 1 Overall picture
def page_overview() -> None:
    st.title("Overall picture")
    st.caption(f"Baseline year {data.BASELINE_LABEL} · every number from `out/` · {CITE}")
    st.caption("CO2 here is location-based: the electricity mix where the server runs, not a green-power certificate.")
    if not out_ready():
        return
    level = factor_level()
    facts_now = data.overview_facts(level)
    st.html(_hero_html(facts_now, level))
    with st.popover("How this number was calculated"):
        st.markdown(
            f"**{_tonnes(facts_now['co2_level'])} t** is the sum of `co2_kg_{level}` on baseline rows "
            f"in `out/fact_costs.csv` (Sep 2025–Aug 2026), divided by 1,000. "
            "Low and high are the same sum on `co2_kg_low` and `co2_kg_high`. "
            "Energy is the sum of `kwh_*`. Cost is the sum of `cost_chf` "
            f"({chf(facts_now['cost_chf'], 2)}). "
            "Each row is quantity × energy factor × PUE (extra electricity for cooling and the building) where that factor says so × the grid factor "
            "of the row's country. Factors: `factors/factors.csv`. The pipeline writes the product; this page only adds it up. "
            "An em dash means that column is empty, so no figure is estimated."
        )
    if _missing(facts_now["co2_level"]) or _missing(facts_now["kwh_level"]):
        st.info(f"`out/fact_costs.csv` has no {level} energy or CO2. A factor value is missing. "
                "Nothing is estimated on this page.")
        return
    st.markdown(_overview_sentence(facts_now))

    metric = st.segmented_control(
        "The chart shows", ["CO2", "Cost"], default="CO2", key="overview_metric",
    )
    metric_key = "cost" if metric == "Cost" else "co2"
    unit = "CHF" if metric_key == "cost" else "kg"
    axis = "CHF per year" if metric_key == "cost" else f"kg CO2 per year ({level} factors)"
    st.subheader("By department" + (" · cost" if metric_key == "cost" else " · CO2"))
    with st.popover("How departments are split"):
        st.markdown("Department uses `dept_allocated` and `alloc_share` from `out/fact_costs_allocated.csv` "
                    "multiplied by the row's CO2 or cost. The test account is folded into IT. "
                    "There is no overhead left to split in the baseline year.")
    dept = data.impact_by("department", metric_key, level)
    st.altair_chart(charts.ranked_bars(dept, value="amount", unit=unit, axis_title=axis), width="stretch", theme=None)

    tab_tool, tab_country, tab_month = st.tabs(["By tool", "By country", "Cost per month"])
    with tab_tool:
        tool = data.impact_by("resource", metric_key, level)
        st.caption("Grouped by `resource_id`. Tool names in the cost files have spelling variants, so the label "
                   "is the canonical name plus the id.")
        top_n = 12
        top, rest = tool.head(top_n), tool.iloc[top_n:]
        shown = top[["label", "amount", "share"]].rename(columns={"amount": "amount"})
        if not rest.empty:
            shown = pd.concat([shown, pd.DataFrame([{
                "label": f"Other ({len(rest)} resources)",
                "amount": rest["amount"].sum(),
                "share": rest["share"].sum(),
            }])], ignore_index=True)
        st.altair_chart(charts.ranked_bars(shown, value="amount", unit=unit, axis_title=axis), width="stretch", theme=None)
        pretty = tool.assign(amount=tool["amount"].round(1), share_pct=(tool["share"] * 100).round(1))
        table_view(pretty.rename(columns={"label": "tool", "amount": unit, "share_pct": "share %"})
                   .drop(columns=["share"], errors="ignore"), "Table view: all resources")
    with tab_country:
        country = data.impact_by("country", metric_key, level)
        st.caption("Country is where the work runs. CO2 uses that country's electricity mix, not a certificate. "
                   "AI providers and SaaS are «EU mixed».")
        st.altair_chart(charts.ranked_bars(country, value="amount", unit=unit, axis_title=axis), width="stretch", theme=None)
        table_view(country.assign(amount=country["amount"].round(1), share_pct=(country["share"] * 100).round(1))
                   .rename(columns={"label": "country", "amount": unit, "share_pct": "share %"})
                   .drop(columns=["share"]), "Table view: countries")
    with tab_month:
        st.caption("Cost only. Energy and CO2 are not stored per month in a separate file; the year total is above.")
        monthly = data.monthly_by_source()
        st.altair_chart(charts.monthly_stack(monthly, data.SOURCE_ORDER), width="stretch", theme=None)
        src = data.by_dimension("source")
        table_view(src.assign(cost_chf=src["cost_chf"].round(2), share=(src["share"] * 100).round(1))
                   .rename(columns={"label": "source", "cost_chf": "CHF", "share": "share %"}), "Table view: per source")


# =============================================================================== 2 Findings
FINDING_STATUS = {  # status never colour-only: badge = icon + label
    "CANDIDATE": ("Candidate", ":material/check_circle:", "blue"),
    "HUMAN_REVIEW": ("Needs human review", ":material/rate_review:", "orange"),
    "BLOCKED": ("Protected: keep", ":material/block:", "red"),
}


def _kg(v) -> str:
    return "–" if v is None or pd.isna(v) else f"{float(v):,.0f} kg"


def _kwh(v) -> str:
    return "–" if v is None or pd.isna(v) else f"{float(v):,.0f} kWh"


def _finding_card(r: pd.Series) -> None:
    label, icon, color = FINDING_STATUS.get(r["status"], (str(r["status"]), ":material/help:", "gray"))
    with st.container(border=True):
        st.markdown(f"**{r['finding_id']} · {r['title']}**")
        st.badge(label, icon=icon, color=color)
        st.html(_kpi_row(
            _kpi_card("Idle or unused", _qty(r["addressable_chf"]), "CHF", unit_first=True),
            _kpi_card("Energy, mid", _kwh_text(r.get("addressable_kwh_mid")), "kWh"),
            _kpi_card("CO2, location-based mid", _qty(r.get("addressable_co2_kg_mid")), "kg"),
        ))
        base = chf(r["cost_chf"])
        st.caption(f"Baseline cost of the resource: {base}. Resource `{r['resource']}`.")
        st.markdown(f"**Evidence:** {r['evidence']}  \n**Protection rule:** {r['protection_rule']}")
        with st.popover("How this was calculated"):
            st.markdown(f"{r['calculation']}  \n**Sources:** `{r['sources']}`")


def _findings_structured(f: pd.DataFrame, source: str) -> None:
    st.caption(f"Ranked by addressable CO2 (location-based, mid factors) · `{source}`")
    with st.popover("How to read this page"):
        st.markdown("Written by `analysis/findings.py`. «Idle or unused» is not a saving claim. "
                    "Addressable means that idle or unused part. "
                    "Findings overlap, so they are not added together. The package decides the savings.")
    if f.empty:
        st.info("The findings file has no rows.")
        return
    top, rest = f.head(5), f.iloc[5:]
    lead = top.iloc[0]
    st.markdown(f"### Largest: {lead['finding_id']} · {_kg(lead.get('addressable_co2_kg_mid'))} CO2 a year")
    st.caption(f"{chf(lead['addressable_chf'])} · {_kwh(lead.get('addressable_kwh_mid'))} · {lead['title']}")
    bars = top.dropna(subset=["addressable_co2_kg_mid"]).copy()
    if not bars.empty:
        base_co2 = data.energy_totals()["co2_mid"]
        if _missing(base_co2) or not base_co2:
            st.info("`out/fact_costs.csv` has no mid CO2 total, so the chart is not drawn. "
                    "The rows below still come from the findings file.")
        else:
            bars = bars.assign(label=bars["finding_id"] + " · " + bars["title"].astype(str),
                               share=bars["addressable_co2_kg_mid"] / base_co2)
            st.altair_chart(charts.ranked_bars(bars, value="addressable_co2_kg_mid", unit="kg",
                                                axis_title="kg CO2 per year, addressable, mid factors"),
                            width="stretch", theme=None)
    for _, r in top.iterrows():
        _finding_card(r)
    with st.expander(f"The other {len(rest)} findings"):
        st.caption("Same file. Cost-only findings (seats, SaaS) have 0 kg here and stay in this list.")
        for _, r in rest.iterrows():
            _finding_card(r)
    table_view(f.drop(columns=["_rank"], errors="ignore"), "Table view: every finding")


def page_findings() -> None:
    st.title("Findings")
    f, source = data.findings_ranked()
    if f is not None:
        _findings_structured(f, source)
        return
    st.caption("Top drivers and waste. Source: `analysis/kb/findings.md` (task H2); every number reproducible from `out/`.")
    md = data.findings_markdown()
    if md is None:
        st.info("Findings are not merged yet (task H2, `analysis/kb/findings.md`). "
                "This page fills itself once that file exists. Nothing is shown until then, "
                "so no number appears here that hasn't been checked against `out/`.", icon="⏳")
        st.markdown("**Topics planned for H2:** dp-dev utilisation · GPU idle outside quarterly training · "
                    "Dublin zombie servers · idle AI seats · SaaS seat gaps.")
        return
    parts = re.split(r"(?m)^## ", md)
    intro, sections = parts[0], parts[1:]
    if intro.strip():
        st.markdown(re.sub(r"(?m)^# .*$", "", intro))
    for s in sections:
        title, _, body = s.partition("\n")
        with st.container(border=True):
            st.subheader(title.strip())
            st.markdown(body)


# =============================================================================== 3 Package
def _protection_hits(text: str) -> list[str]:
    """Protection rules a measure touches, matched on resource_id and on the resource's names in words."""
    low = text.lower()

    def has(k: str) -> bool:
        return re.search(rf"(?<![\w-]){re.escape(k.lower())}(?![\w-])", low) is not None

    hits = []
    for p in register.PROTECTED:
        keys = ({p["resource"], p["cost_resource"]} - {None}) | set(p.get("aliases", []))
        if any(has(k) for k in keys):
            hits.append(f'{p["resource"]} ({p["tickets"]})')
    for rule, keys in register.ALSO_RESPECT_KEYS.items():
        if any(has(k) for k in keys):
            hits.append(rule)
    return hits


def _signed(reduction_pct: float) -> str:
    """A reduction shows as −x %; a package that adds cost or CO2 shows as +x %, never as 0 %."""
    return format_num.signed_pct(reduction_pct)


def _bound_status(value: float | None, target: float, *, higher_is_better: bool) -> str:
    if value is None:
        return "pending"
    if higher_is_better:
        if value >= target:
            return "good"
        return "warning" if value >= target - 2 else "critical"
    if value <= target:
        return "good"
    return "warning" if value <= target + 1 else "critical"


def _tickets(text: str) -> str:
    found = list(dict.fromkeys(re.findall(r"T-\d+", str(text))))
    return ", ".join(found)


def _selected_ids(rows: pd.DataFrame) -> set[str]:
    """Ids ticked on the last edit. The gauges are drawn before the table, so they read this set."""
    saved = st.session_state.get("pkg_ids")
    if isinstance(saved, list):
        return set(saved)
    return set(rows.loc[rows["chosen"], "measure_id"].astype(str))


def page_package() -> None:
    st.title("Measures package")
    st.caption(f"Case targets per year: CO2 −{CO2_TARGET:.0f} % (location-based) · cost −{COST_TARGET:.0f} % · "
               f"at most {PD_CAP:.0f} person-days (1 PD = CHF {data.PD_CHF:,.0f}) · rows from `measures/`")
    if not out_ready():
        return
    rows = data.package_rows()
    if rows is None or rows.empty:
        st.error("`measures/candidates.csv` is missing, so the package cannot be shown. "
                 "Run `python3 measures/measures.py --out out`. No savings figure is invented here.")
        return
    if not bool(rows["files_agree"].iloc[0]):
        st.warning("`measures/measures.csv` and the chosen rows in `measures/candidates.csv` do not list the same ids. "
                   "The ticks start from `candidates.csv`. The files were not changed.")

    level = factor_level()
    selected_ids = _selected_ids(rows)
    selected = rows[rows["measure_id"].astype(str).isin(selected_ids)]
    result = data.package_result(selected, level)
    summary = data.package_summary()

    co2_pct = result["co2_pct"]
    co2_status = _bound_status(co2_pct, CO2_TARGET, higher_is_better=True)
    cost_status = _bound_status(result["cost_pct"], COST_TARGET, higher_is_better=True)
    pd_status = _bound_status(result["pd"], PD_CAP, higher_is_better=False)
    board = charts.gauge_board_html(
        co2={"fill": 0.0 if co2_pct is None else co2_pct / CO2_TARGET, "status": co2_status,
             "center": "–" if co2_pct is None else _signed(co2_pct), "sub": f"target −{CO2_TARGET:.0f} %",
             "caption": "CO2 reduction"},
        cost={"fill": (result["cost_pct"] or 0) / COST_TARGET, "status": cost_status,
              "center": _signed(result["cost_pct"] or 0), "sub": f"target −{COST_TARGET:.0f} %",
              "caption": "Cost reduction"},
        effort={"fill": result["pd"] / PD_CAP, "status": pd_status,
                "center": f"{result['pd']:.1f}", "sub": f"{'von' if i18n.is_de() else 'of'} {PD_CAP:.0f} PD",
                "caption": "Budget"},
    )
    passed = sum(s_ == "good" for s_ in (co2_status, cost_status, pd_status))
    st.html(charts.verdict_html(passed, 3, level.capitalize()))
    st.html(board)
    pcol, ccol, ecol = st.columns(3)
    with pcol.popover(i18n.tr("How CO2 was calculated")):
        base_co2 = result["base_co2_kg"]
        pct = result["co2_pct"]
        base_txt = "–" if _missing(base_co2) else f"{base_co2:,.0f} kg"
        pct_txt = format_num.signed_pct(pct)
        st.markdown(
            f"Sum of `{data.CO2_COL[level]}` on the ticked rows in `measures/candidates.csv`, "
            f"divided by the sum of `co2_kg_{level}` on baseline rows in `out/fact_costs.csv` "
            f"({result['co2_kg']:,.0f} kg of {base_txt} = {pct_txt}). "
            "Low, mid and high are three columns already stored on each measure. "
            "Mid is `savings_co2_kg_location_based`. Market-based CO2 is blank in the file and is not shown. "
            "An em dash means that baseline column is empty, so the percent is not estimated."
        )
    with ccol.popover(i18n.tr("How cost was calculated")):
        st.markdown(
            f"Sum of `savings_cost_chf_per_year` on the ticked rows "
            f"({chf(result['cost_chf'])}) divided by baseline `cost_chf` in `out/fact_costs.csv` "
            f"({chf(result['base_cost_chf'], 2)}). Cost does not change with the factor switch."
        )
    with ecol.popover(i18n.tr("How the budget was calculated")):
        st.markdown(
            f"Sum of `effort_person_days` on the ticked rows ({result['pd']:.1f}). "
            f"CHF {result['effort_chf']:,.0f} = person-days × CHF {data.PD_CHF:,.0f}. "
            f"The cap is {PD_CAP:.0f} person-days (CHF {PD_CAP * data.PD_CHF:,.0f}), from the case rules."
        )
    st.html(_kpi_row(
        _kpi_card("CO2 saved", _qty(result["co2_kg"]), "kg"),
        _kpi_card("Cost saved", _qty(result["cost_chf"]), "CHF", unit_first=True),
        _kpi_card("Effort", f"{result['pd']:.1f}", "person-days", f'CHF {result["effort_chf"]:,.0f}'),
        _kpi_card("Energy saved, mid", _qty(result["kwh"]), "kWh"),
    ))
    st.caption("Energy saved uses the mid factor only (the measure file stores one energy column).")
    if summary is not None:
        st.caption(format_num.package_saved_line(summary))

    idle_file = Path(__file__).resolve().parent.parent / "factors" / "kb" / "V2-idle-impact.csv"
    if idle_file.exists():
        try:
            idle = pd.read_csv(idle_file, index_col=0)
            with st.expander("Sensitivity: if paused hours count at idle power", expanded=False):
                st.markdown(
                    "The package counts every server hour with one factor, in the baseline and in the savings alike. "
                    "A server that sits idle draws about half of an average hour (Vinzenz, `factors/kb/V2-idle-factors.md`). "
                    "Counted that way on both sides, baseline and savings both shrink. This is a sensitivity, not the package.")
                idle_rows = [("Package as counted (official)", "pkg_now_pct"),
                             ("Idle power in baseline and savings", "B_pct")]
                idle_tab = pd.DataFrame([{"Counting": n, **{lvl: format_num.signed_pct(idle.loc[k, lvl]) for lvl in ["low", "mid", "high"]}}
                                         for n, k in idle_rows])
                st.dataframe(idle_tab, hide_index=True, width="stretch")
                st.caption("Source: `factors/kb/V2-idle-impact.csv` (rows `pkg_now_pct`, `B_pct`), written by "
                           "`factors/scripts/idle_impact.py` from `out/`, `measures/candidates.csv` and `factors/factors.csv`. "
                           "Not shown: idle power in the savings only (baseline and savings counted differently), and "
                           "moving dp-dev to Zurich (C2, about 5 person-days, outside the 15 PD budget). Decision: Rashed, 21.11.")
        except (OSError, ValueError, KeyError):
            st.info("`factors/kb/V2-idle-impact.csv` could not be read; the sensitivity is not shown.")

    st.subheader("Tick measures on or off")
    st.caption("On a phone, swipe the measure table sideways. The gauges above follow the ticks.")
    st.caption("Package rows are the chosen set and start ticked. C1 is in that set. C2 is a candidate and starts off. "
               "C2's stored CO2 already assumes M1 stays on; this page does not recalculate it. "
               "A «Yes» in Needs a human means the row asks for a decision. Nothing here switches a protected resource off.")
    if st.button("Reset to the chosen package"):
        # The editor key includes the factor level (pkg_editor_mid, and the same for low and high).
        # Clearing only "pkg_editor" leaves those ticks in place, and the next run copies them back.
        for key in list(st.session_state.keys()):
            if key == "pkg_ids" or str(key).startswith("pkg_editor"):
                del st.session_state[key]
        st.rerun()

    view = rows.copy()
    view["include"] = view["measure_id"].astype(str).isin(selected_ids)
    view["where"] = view["chosen"].map(lambda flag: "Package" if flag else "Candidate")
    view["co2_kg"] = view[data.CO2_COL[level]]
    view["co2_range_kg"] = view.apply(
        lambda r: f"{r['savings_co2_kg_low']:,.0f}–{r['savings_co2_kg_high']:,.0f}", axis=1)
    view["tickets"] = (view["risks_and_exceptions"].fillna("") + " " + view["assumptions_and_sources"].fillna("")).map(_tickets)
    view["needs_human"] = view["risks_and_exceptions"].fillna("").str.contains("Needs human decision").map(
        lambda flag: "Yes" if flag else "No")
    view["protection"] = (view["resource_or_source"].fillna("") + " " + view["description"].fillna("")).map(
        lambda text: ", ".join(_protection_hits(text)) or "—")
    editor_cols = ["include", "measure_id", "needs_human", "description", "co2_kg",
                   "savings_cost_chf_per_year", "effort_person_days", "responsible_role",
                   "tickets", "where", "co2_range_kg"]
    edited = st.data_editor(
        view[editor_cols], hide_index=True, width="stretch", key=f"pkg_editor_{level}",
        disabled=[c for c in editor_cols if c != "include"],
        column_config={
            "include": st.column_config.CheckboxColumn("On"),
            "measure_id": "Id",
            "where": "Set",
            "description": st.column_config.TextColumn("Measure", width="large"),
            "effort_person_days": st.column_config.NumberColumn("PD", format="%.1f"),
            "savings_cost_chf_per_year": st.column_config.NumberColumn("CHF / year", format="%,.0f"),
            "co2_kg": st.column_config.NumberColumn(f"CO2 kg ({level})", format="%,.0f"),
            "co2_range_kg": "CO2 kg low–high",
            "tickets": "Tickets",
            "responsible_role": "Role",
            "needs_human": "Needs a human",
        },
    )
    # One extra run so the gauges, which are drawn above this table, pick up the tick change.
    new_ids = sorted(edited.loc[edited["include"].astype(bool), "measure_id"].astype(str))
    if set(new_ids) != selected_ids:
        st.session_state["pkg_ids"] = new_ids
        st.rerun()
    with st.expander("Protection rule, change and the calculation on each row"):
        detail = view.loc[view["measure_id"].astype(str).isin(selected_ids),
                          ["measure_id", "change", "protection", "risks_and_exceptions", "assumptions_and_sources"]]
        st.dataframe(detail, hide_index=True, width="stretch")


# =============================================================================== 4 Needs a human
def _clean_log_text(text: str) -> str:
    """Display only: the pipeline log prints numpy reprs such as '[np.float64(21.0)]'; show '21.0'."""
    return re.sub(r"\[?np\.float64\(([\d.]+)\)\]?", r"\1", str(text))


def _contradictions(ql: pd.DataFrame | None) -> list[tuple[str, str, str, str]]:
    ai = data.kb_check("AI gateway vs provider invoices, all providers")
    pr = data.kb_check("provider_monthly_report vs azure+aws+hoster (12 baseline months)")
    cards = []
    if ai is not None:
        cards.append(("AI invoices are above the AI gateway",
                      f"Invoices {chf(ai['pipeline'])} vs gateway {chf(ai['independent'])}: "
                      f"**{chf(ai['diff'])} higher ({pct_share(ai['diff'] / ai['independent'])})**. The baseline uses the gateway "
                      "(it has department and tool detail); the invoice is what was actually paid.",
                      "Decide: keep the gateway and add the gap as a labelled line, or switch AI API to invoice totals.",
                      "Head of Finance · lead (Rashed) for the baseline method"))
    if pr is not None:
        cards.append(("Provider report is above our Azure + AWS + hoster total",
                      f"Report {chf(pr['pipeline'])} vs our total {chf(pr['independent'])}: "
                      f"**{chf(pr['diff'])} higher ({pct_share(pr['diff'] / pr['independent'])})** over the baseline year; "
                      f"KB status: *{pr['status']}* ({pr['note']}), but month by month it swings strongly "
                      "(see `analysis/kb/reconciliation.md`).",
                      "Not a reason to change the baseline (separate summary of unknown scope). Ask what the report includes.",
                      "Head of IT"))
    p2 = data.finding_cost("P2")
    billed = ("Finding P2 in `out/findings.csv` has no cost figure." if p2 is None
              else f"Finding P2 in `out/findings.csv` records {chf(p2, 1)} for that server, billed inside vm-test.")
    cards.append(("Disaster-recovery server is billed inside vm-test",
                  "dr-failover has no own cost line (`cost_resource` is empty). " + billed +
                  " Ticket T-1094 protects the emergency fallback, but its resource_id is `vm-test`.",
                  "Keep dr-failover running. Do not let T-1094 make vm-test protected all year: only T-1204 (March 2026) protects vm-test.",
                  "Head of IT"))
    z = data.aws_zurich()
    if z is not None and z["rows"]:
        roles = ", ".join(z["roles"]) if z.get("roles") else z.get("role", "Head of IT")
        cards.append(("AWS rows name Zurich; the locations file says that region is unused",
                      f"`out/fact_costs.csv` baseline, source aws, region contains Zurich: "
                      f"**{z['rows']} rows, {chf(z['cost_chf'], 2)}, {_kwh(z['kwh_mid'])}, {_kg(z['co2_kg_mid'])}** (mid). "
                      "docs/traps.md §5 records that the locations file treats AWS Zurich as unused. "
                      "The cost file is what the baseline sums. These rows were not dropped.",
                      "Ask which file is right before anyone excludes the rows.",
                      roles))
    if ql is not None:
        cp = ql[ql["check"].eq("price vs README")]
        if not cp.empty:
            cards.append(("Copilot price differs from the README",
                          f"{_clean_log_text(cp.iloc[0]['decision'])} (`out/quality_log.csv`).",
                          "Check the contract: is the promotion real and does it apply?", "Head of IT"))
    return cards


def page_human() -> None:
    st.title("Needs a human")
    st.caption("Everything the tool will not decide on its own: text that tries to steer an AI, resources that look idle "
               "but are protected, and sources that disagree. Each item names the responsible role.")

    st.html(_kpi_row(
        _kpi_card("Manipulative texts", str(len(register.MANIPULATIVE_TEXTS)), hint="Shown as data, never followed"),
        _kpi_card("Protected resources", str(len(register.PROTECTED))),
        _kpi_card("Contradictions", str(len(_contradictions(data.quality_log())))),
    ))

    # ---- manipulative text
    st.header("1 · Text that tries to steer an AI")
    st.markdown("**Free text in the data is data, never an instruction.** These texts are quoted so a human can see them. "
                "No number in this app changed because of them.")
    ql = data.quality_log()
    for t in register.MANIPULATIVE_TEXTS:
        with st.container(border=True):
            a, b = st.columns([3, 2])
            with a:
                st.markdown(f"**{t['id']} · {t['tries']}**  \n`{t['file']}` · {t['where']}")
                st.code(t["quote"], language=None, wrap_lines=True)
            with b:
                st.markdown(f"🛡️ **Handling:** {t['handling']}")
                ev = data.kb_check(t["evidence_check"]) if t["evidence_check"] else None
                if ev is not None:
                    val = ev["pipeline"] if pd.notna(ev["pipeline"]) else ev["independent"]
                    st.markdown(f"**Check:** {ev['check']}: {chf(float(val), 2)} "
                                f"(`analysis/kb/reconciliation_checks.csv`, status *{ev['status']}*)")
                if ql is not None and t["quality_log_detail"]:
                    hit = ql[ql["detail"].fillna("").str.contains(t["quality_log_detail"], regex=False)
                             | ql["check"].fillna("").str.contains(t["quality_log_detail"], regex=False)]
                    if not hit.empty:
                        n = hit.iloc[0]["rows"]
                        rows_txt = "" if pd.isna(n) else f" · {int(n)} row{'s' if int(n) != 1 else ''}"
                        st.markdown(f"**Pipeline:** {hit.iloc[0]['decision']}{rows_txt} (`out/quality_log.csv`)")
                    else:
                        st.markdown("⚠️ **Pipeline:** not logged in `out/quality_log.csv` yet (note for R4)")
                st.markdown(f"👤 **Responsible:** {t['role']}")

    # ---- protected resources
    st.header("2 · Looks idle, must not be switched off")
    rows = []
    for p in register.PROTECTED:
        cost, _ = data.resource_cost(p["cost_resource"]) if p["cost_resource"] else (None, None)
        rows.append({
            "resource": p["resource"],
            "rule": p["rule"],
            "what is allowed": p["allowed"],
            "tickets": p["tickets"],
            "cost line in out/": p["cost_resource"] or "none",
            "CHF per year": None if cost is None else round(cost, 0),
            "responsible": p["role"],  # owner of the protected resource itself, not of the cost line it sits in
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch",
                 column_config={"CHF per year": st.column_config.NumberColumn(format="%,.0f"),
                                "rule": st.column_config.TextColumn(width="large"),
                                "what is allowed": st.column_config.TextColumn(width="large")})
    st.caption("CHF per year is the baseline cost under the resource_id shown (`out/fact_costs_allocated.csv`). "
               "gpu-ml-01 is billed as `gpu-ml`; pbi-07 is one report inside the Power BI capacity `pbi-kap`.")
    with st.expander("Also respect"):
        st.dataframe(pd.DataFrame(register.ALSO_RESPECT, columns=["what", "rule", "source", "responsible"]),
                     hide_index=True, width="stretch")

    # ---- contradictions
    st.header("3 · Sources that disagree")
    cards = _contradictions(ql)
    for title, what, decide, role in cards:
        with st.container(border=True):
            st.markdown(f"**{title}**  \n{what}  \n➡️ {decide}  \n👤 **Responsible:** {role}")
    cc = data.contradiction_checks()
    if cc is not None:
        table_view(cc, "All cross-source checks from the pipeline (`out/contradiction_checks.csv`)")

    # ---- one-offs
    st.header("4 · One-off costs: real, but never a recurring saving")
    one = []
    for ticket, what, check, role in register.ONE_OFFS:
        ev = data.kb_check(check)
        one.append({"ticket": ticket, "what": what,
                    "extra CHF in baseline": None if ev is None else round(float(ev["pipeline"]), 2), "responsible": role})
    st.dataframe(pd.DataFrame(one), hide_index=True, width="stretch")
    st.caption("A measure must not «save» these again. Source: `analysis/kb/reconciliation_checks.csv`.")

    st.header("5 · Notice dates")
    cal = data.notice_calendar()
    if cal is None or cal.empty:
        st.info("`out/fact_costs.csv` has no SaaS or AI-subscription rows with a contract end, so no notice date is shown.")
    else:
        as_of = str(cal["as_of"].iloc[0])
        due = cal[cal["state"].eq("due 2 Dec")]
        passed = cal[cal["state"].eq("passed")]
        st.markdown(f"State is judged on **{as_of}** (draft-submission Saturday). "
                    f"Notice by = contract end minus notice days, from the latest baseline month "
                    f"(`{cal['last_month'].iloc[0]}`) in `out/fact_costs.csv`. "
                    f"Unused CHF is the baseline-year sum of (purchased − active) / purchased × cost_chf.")
        st.html(_kpi_row(
            _kpi_card("Due 2 Dec, unused in the baseline year",
                      _qty(float(due["unused_chf"].sum())), "CHF", unit_first=True),
            _kpi_card("Notice already passed, unused in the baseline year",
                      _qty(float(passed["unused_chf"].sum())), "CHF", unit_first=True),
        ))
        show = cal.assign(notice_by=pd.to_datetime(cal["notice_by"]).dt.strftime("%Y-%m-%d"))
        st.dataframe(show[["tool", "source", "state", "notice_by", "unused_chf", "month_idle_chf", "responsible_role"]],
                     hide_index=True, width="stretch",
                     column_config={"unused_chf": st.column_config.NumberColumn("Unused CHF, baseline year", format="%,.0f"),
                                    "month_idle_chf": st.column_config.NumberColumn("Unused CHF, latest month", format="%,.0f"),
                                    "state": st.column_config.TextColumn("State"),
                                    "responsible_role": st.column_config.TextColumn("Role")})
        st.caption("«due 2 Dec» is the notice date 2026-12-02. «passed» is a notice date before "
                   f"{as_of}. The role is `responsible_role` on the cost row. T-1128 still leaves AI seat cuts to the department heads.")


# =============================================================================== 6 Next year
TEAM_AI_USERS = ["Rashed", "Hakim", "Vinzenz", "Grok"]  # people whose AI use V6 should count


def page_next() -> None:
    st.title("Next year")
    st.caption("From `out/` and `factors/kb/`. Nothing on this page is added to the package.")
    if not out_ready():
        return

    st.header("Our own AI use")
    res = data.own_ai_result()
    total = None if res is None else res[res["person"].astype(str).str.upper().eq("TOTAL")]
    if total is not None and not total.empty:
        t = total.iloc[0]
        counted = [p_ for p_ in res["person"].astype(str) if p_.upper() != "TOTAL"]
        missing = [p_ for p_ in TEAM_AI_USERS if p_ not in counted]
        st.html(_kpi_row(
            _kpi_card(
                "Our AI use during the sprint",
                f'{float(t["co2_kg_mid"]):,.2f}',
                "kg",
                f'location-based CO2, mid factors · Range {float(t["co2_kg_low"]):,.2f}–{float(t["co2_kg_high"]):,.1f} kg',
            ),
            _kpi_card("Energy, mid", f'{float(t["kwh_mid"]):,.1f}', "kWh"),
        ))
        st.caption(f"Counted so far: {', '.join(counted)}." + (f" Not counted yet: {', '.join(missing)}." if missing else "")
                   + " Source: `factors/kb/V6-result.csv` (Vinzenz, V6).")
    note = data.own_ai_note()
    if note is None:
        st.info("`factors/kb/V6-our-ai-footprint.md` is not in the repo yet (Vinzenz, V6). "
                "No kilograms are shown for the team's own AI use.")
    else:
        with st.expander("Method and tokens (V6 note)"):
            st.markdown(note)

    st.header("Production platform, baseline months")
    months = data.dp_prod_months()
    st.markdown("**Growth after the baseline year (T-1261):** dp-prod grows from 20 to 24 nodes on 1 Oct 2026. "
                "The baseline and the package stay on the baseline year, as the case asks. "
                "If dp-prod ran on 24 nodes for a full year, its cost, energy and CO2 would be up to 20 % higher (24/20).")
    if months is not None and not months.empty:
        up = 24 / 20 - 1
        st.markdown(f"Range for that growth, from `out/`: up to **+CHF {months['cost_chf'].sum() * up:,.0f}**, "
                    f"**+{months['kwh_mid'].sum() * up:,.0f} kWh** and **+{months['co2_kg_mid'].sum() * up:,.0f} kg CO2** "
                    "a year (mid factors). The package resizes dp-prod in idle hours (M5), so the same measure covers the extra nodes. "
                    "Not added to any total.")
    if months is None or months.empty:
        st.info("`out/fact_costs.csv` has no baseline rows for dp-prod.")
    else:
        st.dataframe(months, hide_index=True, width="stretch",
                     column_config={"cost_chf": st.column_config.NumberColumn("CHF", format="%,.0f"),
                                    "node_hours": st.column_config.NumberColumn("Node-hours", format="%,.0f"),
                                    "kwh_mid": st.column_config.NumberColumn("kWh, mid", format="%,.0f"),
                                    "co2_kg_mid": st.column_config.NumberColumn("kg CO2, mid", format="%,.1f")})
        st.caption("Each month is the sum of dp-prod baseline rows in `out/fact_costs.csv`. "
                   "Quantity unit on those rows is node-hour. June 2026 costs less than the neighbouring months "
                   "while the node-hours stay in the same band; the file is shown as stored, including that month. "
                   "A package saving is not subtracted here.")

    st.header("Notice dates")
    cal = data.notice_calendar()
    if cal is None or cal.empty:
        st.info("No notice dates in `out/fact_costs.csv`.")
    else:
        due = cal[cal["state"].eq("due 2 Dec")]
        st.markdown(f"Judged on **{cal['as_of'].iloc[0]}**. "
                    f"**{len(due)}** contracts are due 2 Dec. The full list, with roles, is on Needs a human.")
        show = due.assign(notice_by=pd.to_datetime(due["notice_by"]).dt.strftime("%Y-%m-%d"))
        st.dataframe(show[["tool", "notice_by", "unused_chf", "responsible_role"]], hide_index=True, width="stretch",
                     column_config={"unused_chf": st.column_config.NumberColumn("Unused CHF, baseline year", format="%,.0f")})

    st.header("Carbon-aware job shift")
    shift = data.job_shift()
    if shift is None:
        st.info("`factors/kb/V4-job-shift.csv` is missing. No shift saving is shown.")
    else:
        st.dataframe(shift, hide_index=True, width="stretch")
        st.caption("Source: `factors/kb/V4-job-shift.csv`. The quarterly model-training row is excluded there "
                   "(protected window T-1053). These reductions are not added to the package savings.")

# =============================================================================== navigation
pages = [
    st.Page(page_overview, title=i18n.tr("Overall picture"), icon="📊", default=True),
    st.Page(page_findings, title=i18n.tr("Findings"), icon="🔎", url_path="findings"),
    st.Page(page_package, title=i18n.tr("Package"), icon="🎯", url_path="package"),
    st.Page(page_human, title=i18n.tr("Needs a human"), icon="🙋", url_path="needs-a-human"),
    st.Page(assistant.render_assistant, title=i18n.tr("Ask the data"), icon="💬", url_path="ask"),
    st.Page(page_next, title=i18n.tr("Next year"), icon="📅", url_path="next-year"),
]
nav = st.navigation(pages)
with st.sidebar:
    st.toggle("Deutsch", key=i18n.KEY, help="Interface in German. Text from the data and all numbers stay as stored.")
    st.caption(f"Numbers: `out/` from `pipeline/pipeline.py` · {CITE}")
    if st.button("Reload data"):
        st.cache_data.clear()
        st.rerun()
nav.run()
