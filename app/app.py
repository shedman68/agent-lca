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
import charts  # noqa: E402
import data  # noqa: E402
import register  # noqa: E402

st.set_page_config(page_title="GreenOps Basel", page_icon="🌿", layout="wide")

CITE = "Sample data ALTYCA, sprintd Basel 2026"


def chf(v: float | None, digits: int = 0) -> str:
    return "–" if v is None or pd.isna(v) else f"CHF {v:,.{digits}f}"


def compact_chf(v: float) -> str:
    return f"CHF {v / 1000:,.1f}K" if abs(v) < 1e6 else f"CHF {v / 1e6:,.2f}M"


def table_view(df: pd.DataFrame, label: str = "Table view") -> None:
    with st.expander(label):
        st.dataframe(df, hide_index=True, width="stretch")


# =============================================================================== 1 Overall picture
def page_overview() -> None:
    st.title("Overall picture")
    st.caption(f"Baseline year {data.BASELINE_LABEL} · all numbers from `out/` (pipeline) · {CITE}")

    t = data.baseline_totals()
    c1, c2, c3, c4 = st.columns([1.4, 1, 1, 1])
    c1.markdown(f'<div style="font-size:13px;opacity:.7">Total cost per year</div>'
                f'<div style="font-size:48px;font-weight:600;line-height:1.1">{chf(t["cost_chf"])}</div>',
                unsafe_allow_html=True)
    c2.metric("Imputed (missing costs)", compact_chf(t["imputed_chf"]),
              help="Missing costs filled with quantity × median unit price of the same resource (out/quality_log.csv).")
    c3.metric("Energy per year", f"{t['kwh']:,.0f} kWh" if t["kwh"] is not None else "Pending",
              help="Appears once factors/factors.csv is filled in (V1, V2) and the pipeline is rerun.")
    c4.metric("CO2 per year (location-based)", f"{t['co2_kg'] / 1000:,.1f} t" if t["co2_kg"] is not None else "Pending",
              help="Appears once factors/factors.csv is filled in (V1, V2) and the pipeline is rerun.")

    st.subheader("Cost per month by source")
    m = data.monthly_by_source()
    st.altair_chart(charts.monthly_stack(m, data.SOURCE_ORDER), width="stretch", theme=None)
    src = data.by_dimension("source")
    table_view(src.assign(cost_chf=src["cost_chf"].round(2), share=(src["share"] * 100).round(1))
               .rename(columns={"label": "source", "cost_chf": "CHF", "share": "share %"}), "Table view: per source")

    tab_dept, tab_tool, tab_country = st.tabs(["By department", "By tool", "By country"])
    with tab_dept:
        d = data.by_dimension("department")
        st.caption("Shared overhead (e.g. Office AI assistant) is split by FTE share per month (headcount.csv); "
                   "the AWS test account goes 100 % to IT.")
        st.altair_chart(charts.ranked_bars(d), width="stretch", theme=None)
        table_view(d.assign(cost_chf=d["cost_chf"].round(2), share=(d["share"] * 100).round(1))
                   .rename(columns={"label": "department", "cost_chf": "CHF", "share": "share %"}))
    with tab_tool:
        r = data.by_dimension("resource")
        st.caption("Grouped by `resource_id`, because tool names have spelling variants in the data "
                   "(dp-prod appears as «Data Platform Prod» and «Data platform production»).")
        top_n = 15
        top = r.head(top_n)
        rest = r.iloc[top_n:]
        shown = top[["label", "cost_chf", "share"]]
        if not rest.empty:
            shown = pd.concat([shown, pd.DataFrame([{"label": f"Other ({len(rest)} resources)",
                                                     "cost_chf": rest["cost_chf"].sum(), "share": rest["share"].sum()}])])
        st.altair_chart(charts.ranked_bars(shown), width="stretch", theme=None)
        table_view(r.assign(cost_chf=r["cost_chf"].round(2), share=(r["share"] * 100).round(1))
                   [["resource_id", "tool_canonical", "source", "cost_chf", "share", "tool_spellings", "responsible_role"]]
                   .rename(columns={"tool_canonical": "tool", "cost_chf": "CHF", "share": "share %",
                                    "tool_spellings": "name variants in data"}), "Table view: all resources")
    with tab_country:
        c = data.by_dimension("country")
        st.caption("Country decides the grid factor for location-based CO2. AI providers and SaaS are «EU mixed».")
        st.altair_chart(charts.ranked_bars(c), width="stretch", theme=None)
        table_view(c.assign(cost_chf=c["cost_chf"].round(2), share=(c["share"] * 100).round(1))
                   .rename(columns={"label": "country", "cost_chf": "CHF", "share": "share %"}))


# =============================================================================== 2 Findings
def page_findings() -> None:
    st.title("Findings")
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
    if abs(reduction_pct) < 0.05:
        return "0 %"
    return f"−{reduction_pct:.1f} %" if reduction_pct > 0 else f"+{-reduction_pct:.1f} %"


def page_package() -> None:
    st.title("Measures package")
    st.caption("Targets per year: CO2 −40 % (location-based) · cost −25 % · effort at most 15 person-days "
               f"(CHF {15 * data.PD_CHF:,}; 1 PD = CHF {data.PD_CHF:,}).")
    t = data.baseline_totals()
    m = data.measures()

    if m is None or m.empty:
        st.info("The package is not calculated yet (tasks R1/R2). The app reads it from `out/measures.csv` "
                "in the format of `submission/template_measures_package.csv`. The target bar below shows the "
                "required values until then.", icon="⏳")
        sel = pd.DataFrame(columns=["measure_id", "effort_person_days", "savings_cost_chf_per_year", "savings_co2_kg_location_based"])
    else:
        m = m.copy()
        m["protection"] = (m["resource_or_source"].fillna("") + " " + m["description"].fillna("")).map(
            lambda s: ", ".join(_protection_hits(s)))
        m.insert(0, "include", True)
        st.subheader("Choose measures")
        st.caption("Untick a measure to see its effect on the targets. Measures touching a protected resource "
                   "are listed with their rule; they need human sign-off (see «Needs a human»).")
        cols = ["include", "measure_id", "description", "resource_or_source", "protection", "effort_person_days",
                "savings_cost_chf_per_year", "savings_energy_kwh_per_year", "savings_co2_kg_location_based",
                "risks_and_exceptions"]
        edited = st.data_editor(m[[c for c in cols if c in m]], hide_index=True, width="stretch",
                                disabled=[c for c in cols if c != "include"], key="pkg")
        sel = m[edited["include"].values]

    pd_used = float(sel["effort_person_days"].sum()) if len(sel) else 0.0
    cost_saved = float(sel["savings_cost_chf_per_year"].sum()) if len(sel) else 0.0
    co2_saved = float(sel["savings_co2_kg_location_based"].sum()) if len(sel) else 0.0
    cost_pct = 100 * cost_saved / t["cost_chf"]
    co2_pct = 100 * co2_saved / t["co2_kg"] if t["co2_kg"] else None
    pending = m is None or m.empty

    def st_min(v, target):
        return "pending" if pending or v is None else ("good" if v >= target else "critical")

    rows = [
        {"name": "CO2 reduction", "value": co2_pct or 0.0, "target": 40, "max": 60,
         "value_txt": "pending" if co2_pct is None else _signed(co2_pct), "target_txt": "−40 %",
         "status": "pending" if co2_pct is None else st_min(co2_pct, 40),
         "note": "baseline CO2 pending (factors)" if t["co2_kg"] is None else f"{co2_saved / 1000:,.1f} t of {t['co2_kg'] / 1000:,.1f} t"},
        {"name": "Cost reduction", "value": cost_pct, "target": 25, "max": 40,
         "value_txt": _signed(cost_pct), "target_txt": "−25 %", "status": st_min(cost_pct, 25),
         "note": f"{chf(cost_saved)} of {chf(t['cost_chf'])}"},
        {"name": "Effort", "value": pd_used, "target": 15, "max": 20,
         "value_txt": f"{pd_used:.1f} PD", "target_txt": "≤ 15 PD",
         "status": "pending" if pending else ("good" if pd_used <= 15 else "critical"),
         "note": f"{chf(pd_used * data.PD_CHF)} of CHF {15 * data.PD_CHF:,}"},
    ]
    st.subheader("Target bar")
    st.html(charts.meter_list_html(rows))
    st.caption("The tick marks the target. Cost and CO2: bar fills towards more savings; effort: must stay left of the tick.")


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
                      f"**{chf(ai['diff'])} higher ({ai['diff'] / ai['independent']:.1%})**. The baseline uses the gateway "
                      "(it has department and tool detail); the invoice is what was actually paid.",
                      "Decide: keep the gateway and add the gap as a labelled line, or switch AI API to invoice totals.",
                      "Head of Finance · lead (Rashed) for the baseline method"))
    if pr is not None:
        cards.append(("Provider report is above our Azure + AWS + hoster total",
                      f"Report {chf(pr['pipeline'])} vs our total {chf(pr['independent'])}: "
                      f"**{chf(pr['diff'])} higher ({pr['diff'] / pr['independent']:.1%})** over the baseline year; "
                      f"KB status: *{pr['status']}* ({pr['note']}), but month by month it swings strongly "
                      "(see `analysis/kb/reconciliation.md`).",
                      "Not a reason to change the baseline (separate summary of unknown scope). Ask what the report includes.",
                      "Head of IT"))
    cards.append(("T-1094 is about dr-failover but filed under vm-test",
                  "The ticket protects the emergency fallback dr-failover, but its resource_id is `vm-test`. "
                  "dr-failover has no own cost line in `out/`.",
                  "Keep dr-failover running. Do not let T-1094 make vm-test protected all year: only T-1204 (March 2026) protects vm-test.",
                  "Head of IT"))
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

    c1, c2, c3 = st.columns(3)
    c1.metric("Manipulative texts", len(register.MANIPULATIVE_TEXTS), help="Shown as data, never followed")
    c2.metric("Protected resources", len(register.PROTECTED))
    c3.metric("Contradictions", len(_contradictions(data.quality_log())))

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


# =============================================================================== navigation
pages = [
    st.Page(page_overview, title="Overall picture", icon="📊", default=True),
    st.Page(page_findings, title="Findings", icon="🔎", url_path="findings"),
    st.Page(page_package, title="Package", icon="🎯", url_path="package"),
    st.Page(page_human, title="Needs a human", icon="🙋", url_path="needs-a-human"),
]
nav = st.navigation(pages)
with st.sidebar:
    st.caption(f"Numbers: `out/` from `pipeline/pipeline.py` · {CITE}")
    if st.button("Reload data"):
        st.cache_data.clear()
        st.rerun()
nav.run()
