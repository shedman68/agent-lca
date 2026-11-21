"""Data layer for the app. Reads out/ (pipeline output), analysis/kb/ (Hakim's knowledge base) and
measures/measures.csv (the package, computed from out/ by measures/measures.py).

Every number shown in the app comes from here, so it stays reproducible from `pipeline/pipeline.py`
(AGENTS.md rule 2). Nothing in this module reads data/ directly.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
KB = ROOT / "analysis" / "kb"
MEASURES = ROOT / "measures"

BASELINE_LABEL = "Sep 2025 – Aug 2026"
PD_CHF = 1_100  # AGENTS.md: 1 PD = CHF 1,100
TARGETS = {"co2_pct": 40.0, "cost_pct": 25.0, "pd_max": 15.0}

SOURCE_LABEL = {
    "azure": "Azure",
    "saas": "SaaS",
    "aws": "AWS",
    "ai_usage": "AI API",
    "ai_subscriptions": "AI subscriptions",
    "hoster": "Hoster",
}
# Fixed order = fixed colour slot per source (colour follows the entity, never its rank).
SOURCE_ORDER = ["Azure", "SaaS", "AWS", "AI API", "AI subscriptions", "Hoster"]

COUNTRY_LABEL = {
    "CH": "Switzerland",
    "DE": "Germany",
    "IE": "Ireland",
    "EU": "EU mixed (AI providers, SaaS)",
}

# Tool names have spelling variants (e.g. dp-prod: "Data Platform Prod" / "Data platform production"),
# so the app groups by resource_id and shows one canonical name per resource.
# Canonical names follow data/mapping_departments_tools.csv where the cost data disagrees with itself.
CANONICAL_TOOL = {
    "dp-prod": "Data platform production",
    "saas-other": "Other SaaS tools",
}


def _read(path: Path, **kw) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path, low_memory=False, **kw)


@st.cache_data(show_spinner=False)
def facts() -> pd.DataFrame:
    """Allocated fact table, baseline year only (Overhead already split by FTE share)."""
    f = _read(OUT / "fact_costs_allocated.csv")
    if f is None:
        raise FileNotFoundError("out/fact_costs_allocated.csv missing: run pipeline/pipeline.py --data data --out out")
    f = f[f["in_baseline"].astype(str).eq("True")].copy()
    f["source_label"] = f["source"].map(SOURCE_LABEL).fillna(f["source"])
    f["country_label"] = f["country"].map(COUNTRY_LABEL).fillna(f["country"])
    names = (
        f.groupby(["resource_id", "tool"]).size().reset_index(name="n")
        .sort_values("n", ascending=False).drop_duplicates("resource_id")
        .set_index("resource_id")["tool"].to_dict()
    )
    names.update(CANONICAL_TOOL)
    f["resource_id"] = f["resource_id"].fillna("unknown")
    f["tool_canonical"] = f["resource_id"].map(names).fillna(f["resource_id"])
    f["dept_allocated"] = f["dept_allocated"].fillna("Unassigned")
    f["country_label"] = f["country_label"].fillna("Unknown")
    return f


@st.cache_data(show_spinner=False)
def facts_unallocated() -> pd.DataFrame:
    """Unallocated fact table, baseline year only; holds kwh_* / co2_kg_* once factors are filled in."""
    f = _read(OUT / "fact_costs.csv")
    if f is None:
        raise FileNotFoundError("out/fact_costs.csv missing: run the pipeline")
    return f[f["in_baseline"].astype(str).eq("True")].copy()


def baseline_totals() -> dict:
    f = facts_unallocated()
    t = {"cost_chf": float(f["cost_chf"].sum()), "imputed_chf": float(f.loc[f["cost_imputed"].astype(str).eq("True"), "cost_chf"].sum())}
    for k in ("kwh", "co2_kg"):
        col = f"{k}_mid"
        t[k] = float(f[col].sum()) if col in f and f[col].notna().any() else None
    return t


def _one_role(r: pd.Series) -> str:
    r = r.dropna().unique()
    return "unknown" if len(r) == 0 else (str(r[0]) if len(r) == 1 else "several (per tool)")


def by_dimension(dim: str) -> pd.DataFrame:
    """dim in {'department', 'resource', 'country', 'source'} -> CHF per group, largest first."""
    f = facts()
    if dim == "department":
        g = f.groupby("dept_allocated", dropna=False)["cost_chf_alloc"].sum().rename("cost_chf").reset_index()
        g = g.rename(columns={"dept_allocated": "label"})
    elif dim == "resource":
        g = f.groupby(["resource_id", "tool_canonical"], dropna=False).agg(
            cost_chf=("cost_chf_alloc", "sum"),
            tool_spellings=("tool", "nunique"),
            source=("source_label", "first"),
            responsible_role=("responsible_role", _one_role),
        ).reset_index()
        g["label"] = g["tool_canonical"] + " (" + g["resource_id"] + ")"
    elif dim == "country":
        g = f.groupby("country_label", dropna=False)["cost_chf_alloc"].sum().rename("cost_chf").reset_index()
        g = g.rename(columns={"country_label": "label"})
    elif dim == "source":
        g = f.groupby("source_label", dropna=False)["cost_chf_alloc"].sum().rename("cost_chf").reset_index()
        g = g.rename(columns={"source_label": "label"})
    else:
        raise ValueError(dim)
    g = g.sort_values("cost_chf", ascending=False).reset_index(drop=True)
    g["share"] = g["cost_chf"] / g["cost_chf"].sum()
    return g


def monthly_by_source() -> pd.DataFrame:
    f = facts()
    return f.groupby(["month", "source_label"])["cost_chf_alloc"].sum().rename("cost_chf").reset_index()


def resource_cost(resource_id: str) -> tuple[float | None, str | None]:
    """Baseline CHF and responsible role for one resource_id, or (None, None) if it has no cost line in out/."""
    f = facts()
    s = f[f["resource_id"] == resource_id]
    if s.empty:
        return None, None
    roles = s["responsible_role"].dropna().mode()
    return float(s["cost_chf_alloc"].sum()), (None if roles.empty else str(roles.iloc[0]))


@st.cache_data(show_spinner=False)
def quality_log() -> pd.DataFrame | None:
    return _read(OUT / "quality_log.csv")


@st.cache_data(show_spinner=False)
def contradiction_checks() -> pd.DataFrame | None:
    return _read(OUT / "contradiction_checks.csv")


@st.cache_data(show_spinner=False)
def reconciliation_checks() -> pd.DataFrame | None:
    return _read(KB / "reconciliation_checks.csv")


def kb_check(check: str) -> pd.Series | None:
    r = reconciliation_checks()
    if r is None:
        return None
    hit = r[r["check"] == check]
    return None if hit.empty else hit.iloc[0]


@st.cache_data(show_spinner=False)
def findings_table() -> tuple[pd.DataFrame | None, str | None]:
    """Structured H2 findings: out/findings.csv (written by analysis/findings.py), else the committed
    copy analysis/kb/findings_numbers.csv. Returns (table, path shown in the app)."""
    for path, label in ((OUT / "findings.csv", "out/findings.csv"), (KB / "findings_numbers.csv", "analysis/kb/findings_numbers.csv")):
        f = _read(path)
        if f is not None and not f.empty:
            for c in ("cost_chf", "share_of_total_pct", "addressable_chf",
                      "addressable_kwh_mid", "addressable_co2_kg_mid",
                      "addressable_kwh_low", "addressable_co2_kg_low",
                      "addressable_kwh_high", "addressable_co2_kg_high"):
                if c in f.columns:
                    f[c] = pd.to_numeric(f[c], errors="coerce")
            return f, label
    return None, None


def findings_ranked() -> tuple[pd.DataFrame | None, str | None]:
    """Findings ordered by addressable location-based CO2 (mid). Rows with no CO2 stay at the end."""
    f, source = findings_table()
    if f is None:
        return None, None
    out = f.copy()
    out["_rank"] = out["addressable_co2_kg_mid"] if "addressable_co2_kg_mid" in out.columns else pd.NA
    out = out.sort_values("_rank", ascending=False, na_position="last").reset_index(drop=True)
    return out, source


def findings_markdown() -> str | None:
    p = KB / "findings.md"
    return p.read_text(encoding="utf-8") if p.exists() else None


@st.cache_data(show_spinner=False)
def measures() -> tuple[pd.DataFrame | None, str | None]:
    """Measures package in the template format (submission/template_measures_package.csv columns).

    Read from out/measures.csv if the pipeline copies it there, else measures/measures.csv, where
    measures/measures.py writes it (measures/README.md, tasks R1/R2). Returns (table, path) or (None, None).
    """
    for path, label in ((OUT / "measures.csv", "out/measures.csv"), (MEASURES / "measures.csv", "measures/measures.csv")):
        m = _read(path)
        if m is not None:
            break
    else:
        return None, None
    m = m[~m["measure_id"].astype(str).str.startswith("Example")].copy()
    for c in ("effort_person_days", "savings_cost_chf_per_year", "savings_energy_kwh_per_year",
              "savings_co2_kg_location_based", "savings_co2_kg_low", "savings_co2_kg_high"):
        if c in m:
            m[c] = pd.to_numeric(m[c], errors="coerce").fillna(0.0)
    return m, label


LEVELS = ("low", "mid", "high")
# Column on a measure row that holds location-based CO2 at each factor level.
CO2_COL = {"low": "savings_co2_kg_low", "mid": "savings_co2_kg_location_based", "high": "savings_co2_kg_high"}
AS_OF = "2026-11-21"  # draft-submission Saturday (AGENTS.md). Notice states are judged against this date.
DUE_2_DEC = "2026-12-02"


def _num(frame: pd.DataFrame, col: str) -> pd.Series:
    if col not in frame:
        return pd.Series(0.0, index=frame.index)
    return pd.to_numeric(frame[col], errors="coerce").fillna(0.0)


@st.cache_data(show_spinner=False)
def energy_totals() -> dict:
    """Baseline-year kWh and location-based kg CO2 at low, mid and high. Source: out/fact_costs.csv."""
    f = facts_unallocated()
    out = {"cost_chf": float(f["cost_chf"].sum())}
    for lvl in LEVELS:
        out[f"kwh_{lvl}"] = float(_num(f, f"kwh_{lvl}").sum()) if f"kwh_{lvl}" in f and f[f"kwh_{lvl}"].notna().any() else None
        out[f"co2_{lvl}"] = float(_num(f, f"co2_kg_{lvl}").sum()) if f"co2_kg_{lvl}" in f and f[f"co2_kg_{lvl}"].notna().any() else None
    return out


@st.cache_data(show_spinner=False)
def aligned_baseline() -> pd.DataFrame:
    """Baseline rows with department allocation and CO2 on the same line.

    Energy and CO2 are written to out/fact_costs.csv. The department split (test account → IT,
    overhead by FTE share) is out/fact_costs_allocated.csv. The pipeline copies the cost rows
    before it adds kWh, and with no overhead rows the two baseline frames are the same length
    and the same order. CO2 allocated to a department is co2_kg × alloc_share.
    """
    cost = facts_unallocated().reset_index(drop=True)
    alloc = facts().reset_index(drop=True)
    same_len = len(cost) == len(alloc)
    same_id = same_len and cost["resource_id"].fillna("unknown").equals(alloc["resource_id"].fillna("unknown"))
    same_chf = same_len and (cost["cost_chf"] - alloc["cost_chf"]).abs().max() < 0.02
    if not (same_id and same_chf):
        raise ValueError(
            "out/fact_costs.csv and out/fact_costs_allocated.csv do not line up row by row, "
            "so CO2 cannot be split by department without guessing. Re-run pipeline/pipeline.py."
        )
    out = cost.copy()
    out["dept_allocated"] = alloc["dept_allocated"].values
    out["alloc_share"] = pd.to_numeric(alloc["alloc_share"], errors="coerce").fillna(1.0).values
    out["cost_chf_alloc"] = pd.to_numeric(alloc["cost_chf_alloc"], errors="coerce").fillna(0.0).values
    out["tool_canonical"] = alloc["tool_canonical"].values
    out["country_label"] = alloc["country_label"].values
    out["source_label"] = alloc["source_label"].values
    for lvl in LEVELS:
        out[f"co2_alloc_{lvl}"] = _num(out, f"co2_kg_{lvl}") * out["alloc_share"]
        out[f"kwh_alloc_{lvl}"] = _num(out, f"kwh_{lvl}") * out["alloc_share"]
    return out


def impact_by(dim: str, metric: str = "co2", level: str = "mid") -> pd.DataFrame:
    """metric is 'co2', 'kwh' or 'cost'. dim is department, resource, country or source.

    Returns label, amount, share (of that metric), largest first.
    """
    if level not in LEVELS:
        raise ValueError(level)
    f = aligned_baseline()
    if metric == "cost":
        col = "cost_chf_alloc"
    elif metric == "co2":
        col = f"co2_alloc_{level}"
    elif metric == "kwh":
        col = f"kwh_alloc_{level}"
    else:
        raise ValueError(metric)
    if dim == "department":
        g = f.groupby("dept_allocated", dropna=False)[col].sum().rename("amount").reset_index()
        g = g.rename(columns={"dept_allocated": "label"})
    elif dim == "resource":
        g = f.groupby(["resource_id", "tool_canonical"], dropna=False)[col].sum().rename("amount").reset_index()
        g["label"] = g["tool_canonical"] + " (" + g["resource_id"] + ")"
    elif dim == "country":
        g = f.groupby("country_label", dropna=False)[col].sum().rename("amount").reset_index()
        g = g.rename(columns={"country_label": "label"})
    elif dim == "source":
        g = f.groupby("source_label", dropna=False)[col].sum().rename("amount").reset_index()
        g = g.rename(columns={"source_label": "label"})
    else:
        raise ValueError(dim)
    g = g.sort_values("amount", ascending=False).reset_index(drop=True)
    total = float(g["amount"].sum())
    g["share"] = 0.0 if total == 0 else g["amount"] / total
    return g


def overview_facts(level: str = "mid") -> dict:
    """Headline inputs for the overall picture. Every figure is a sum from out/."""
    totals = energy_totals()
    by_country = impact_by("country", "co2", level)
    by_resource = impact_by("resource", "co2", level)
    top_c = by_country.iloc[0]
    top_r = by_resource.iloc[0]
    return {
        "cost_chf": totals["cost_chf"],
        "kwh_low": totals["kwh_low"], "kwh_mid": totals["kwh_mid"], "kwh_high": totals["kwh_high"],
        "co2_low": totals["co2_low"], "co2_mid": totals["co2_mid"], "co2_high": totals["co2_high"],
        "co2_level": totals[f"co2_{level}"],
        "kwh_level": totals[f"kwh_{level}"],
        "level": level,
        "top_country": str(top_c["label"]),
        "top_country_share": float(top_c["share"]),
        "top_resource": str(top_r["label"]),
        "top_resource_share": float(top_r["share"]),
    }


def _as_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


@st.cache_data(show_spinner=False)
def package_rows() -> pd.DataFrame | None:
    """Every measure and candidate, with the chosen flag from measures/candidates.csv.

    measures/measures.csv is the chosen package (no candidate rows). If the two files disagree
    on which ids are in the package, `files_agree` is False and the caller must say so.
    """
    candidates = _read(MEASURES / "candidates.csv")
    chosen_file, _ = measures()
    if candidates is None or candidates.empty:
        return None
    c = candidates.copy()
    c["chosen"] = _as_bool(c["chosen"]) if "chosen" in c else False
    for col in ("effort_person_days", "savings_cost_chf_per_year", "savings_energy_kwh_per_year",
                "savings_co2_kg_location_based", "savings_co2_kg_low", "savings_co2_kg_high"):
        c[col] = _num(c, col)
    chosen_ids = set(c.loc[c["chosen"], "measure_id"].astype(str))
    file_ids = set() if chosen_file is None else set(chosen_file["measure_id"].astype(str))
    c["files_agree"] = chosen_ids == file_ids
    c["in_package"] = c["measure_id"].astype(str).isin(file_ids)
    return c


@st.cache_data(show_spinner=False)
def package_summary() -> pd.Series | None:
    path = MEASURES / "package_summary.csv"
    if not path.exists():
        return None
    s = pd.read_csv(path, index_col=0).iloc[:, 0]
    return s


def package_result(selected: pd.DataFrame, level: str = "mid") -> dict:
    """Sum the selected rows. Percentages use the baseline totals in out/fact_costs.csv.

    Savings themselves are the stored measure rows (measures/), not recomputed here.
    """
    if level not in LEVELS:
        raise ValueError(level)
    totals = energy_totals()
    co2_col = CO2_COL[level]
    if selected is None or selected.empty:
        pd_used = cost = co2 = kwh = 0.0
    else:
        pd_used = float(_num(selected, "effort_person_days").sum())
        cost = float(_num(selected, "savings_cost_chf_per_year").sum())
        co2 = float(_num(selected, co2_col).sum())
        kwh = float(_num(selected, "savings_energy_kwh_per_year").sum())
    base_cost = totals["cost_chf"]
    base_co2 = totals[f"co2_{level}"]
    return {
        "level": level,
        "pd": pd_used,
        "effort_chf": pd_used * PD_CHF,
        "cost_chf": cost,
        "cost_pct": (100.0 * cost / base_cost) if base_cost else None,
        "co2_kg": co2,
        "co2_pct": (100.0 * co2 / base_co2) if base_co2 else None,
        "kwh": kwh,
        "base_cost_chf": base_cost,
        "base_co2_kg": base_co2,
        "base_kwh": totals[f"kwh_{level}"],
    }


def notice_calendar() -> pd.DataFrame | None:
    """Unused seats and licences by contract, with the date notice must be given.

    Latest baseline month per tool supplies contract_end and notice_period_days.
    Unused CHF is the baseline-year sum of (purchased − active) / purchased × cost_chf
    on out/fact_costs.csv (the pipeline already applied FX). State is judged at AS_OF.
    """
    f = facts_unallocated()
    need = {"contract_end", "notice_period_days", "quantity", "seats_active", "tool", "source"}
    if not need.issubset(f.columns):
        return None
    sub = f[f["source"].isin(["saas", "ai_subscriptions"])].copy()
    if sub.empty:
        return None
    sub["quantity"] = _num(sub, "quantity")
    sub["seats_active"] = _num(sub, "seats_active")
    sub["cost_chf"] = _num(sub, "cost_chf")
    sub["idle_chf"] = (sub["quantity"] - sub["seats_active"]).clip(lower=0) / sub["quantity"].where(sub["quantity"] > 0) * sub["cost_chf"]
    sub["idle_chf"] = sub["idle_chf"].fillna(0.0)
    sub["month"] = sub["month"].astype(str).str[:7]
    annual = sub.groupby(["source", "tool"], dropna=False).agg(
        unused_chf=("idle_chf", "sum"),
        purchased=("quantity", "sum"),
        active=("seats_active", "sum"),
    ).reset_index()
    last_month = sub["month"].max()
    last = sub[sub["month"].eq(last_month)]
    terms = last.groupby(["source", "tool"], dropna=False).agg(
        contract_end=("contract_end", "min"),
        notice_period_days=("notice_period_days", "min"),
        month_chf=("cost_chf", "sum"),
        month_purchased=("quantity", "sum"),
        month_active=("seats_active", "sum"),
        responsible_role=("responsible_role", _one_role),
    ).reset_index()
    g = annual.merge(terms, on=["source", "tool"], how="left")
    g["notice_by"] = pd.to_datetime(g["contract_end"], errors="coerce") - pd.to_timedelta(
        pd.to_numeric(g["notice_period_days"], errors="coerce"), unit="D")
    as_of = pd.Timestamp(AS_OF)
    due = pd.Timestamp(DUE_2_DEC)

    def state(day: pd.Timestamp) -> str:
        if pd.isna(day):
            return "unknown"
        if day.normalize() == due:
            return "due 2 Dec"
        if day < as_of:
            return "passed"
        return "open"

    g["state"] = g["notice_by"].map(state)
    g["month_idle"] = (g["month_purchased"] - g["month_active"]).clip(lower=0)
    g["month_idle_chf"] = g["month_chf"] * g["month_idle"] / g["month_purchased"].where(g["month_purchased"] > 0)
    g["month_idle_chf"] = g["month_idle_chf"].fillna(0.0)
    g = g.sort_values(["notice_by", "unused_chf"], ascending=[True, False]).reset_index(drop=True)
    g["as_of"] = AS_OF
    g["last_month"] = last_month
    return g


def aws_zurich() -> dict | None:
    """AWS rows whose region names Zurich, from out/fact_costs.csv (baseline)."""
    f = facts_unallocated()
    if "region" not in f.columns:
        return None
    z = f[f["source"].eq("aws") & f["region"].astype(str).str.contains("Zurich", case=False, na=False)]
    if z.empty:
        return {"rows": 0, "cost_chf": 0.0, "co2_kg_mid": 0.0, "kwh_mid": 0.0}
    return {
        "rows": int(len(z)),
        "cost_chf": float(z["cost_chf"].sum()),
        "co2_kg_mid": float(_num(z, "co2_kg_mid").sum()),
        "kwh_mid": float(_num(z, "kwh_mid").sum()),
        "role": _one_role(z["responsible_role"]) if "responsible_role" in z else "Head of IT",
        "roles": sorted({str(x) for x in z["responsible_role"].dropna().unique()}) if "responsible_role" in z else [],
    }


def dp_prod_months() -> pd.DataFrame | None:
    """Baseline months of dp-prod from out/fact_costs.csv. Node-hours are the quantity column (unit node-hour)."""
    f = facts_unallocated()
    if f.empty or "resource_id" not in f.columns:
        return None
    rows = f[f["resource_id"].eq("dp-prod")].copy()
    if rows.empty:
        return None
    rows["month"] = rows["month"].astype(str).str[:7]
    g = rows.groupby("month", dropna=False).agg(
        cost_chf=("cost_chf", "sum"),
        node_hours=("quantity", "sum"),
        kwh_mid=("kwh_mid", "sum"),
        co2_kg_mid=("co2_kg_mid", "sum"),
    ).reset_index()
    return g.sort_values("month").reset_index(drop=True)


def job_shift() -> pd.DataFrame | None:
    """Carbon-aware shift table. Read as stored; the quarterly training row stays excluded."""
    path = ROOT / "factors" / "kb" / "V4-job-shift.csv"
    if not path.exists():
        return None
    return pd.read_csv(path)


def own_ai_note() -> str | None:
    """Vinzenz's own-use note, if he has written it. None means the file is absent."""
    path = ROOT / "factors" / "kb" / "V6-our-ai-footprint.md"
    return path.read_text(encoding="utf-8") if path.exists() else None


def own_ai_result() -> pd.DataFrame | None:
    """Vinzenz's V6 result table (one row per person plus TOTAL), as written by factors/scripts/own_ai.py."""
    path = ROOT / "factors" / "kb" / "V6-result.csv"
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except (OSError, ValueError):
        return None


def finding_cost(finding_id: str) -> float | None:
    """Baseline cost recorded for one finding in out/findings.csv, or None if that row has no cost."""
    table, _ = findings_table()
    if table is None or "finding_id" not in table.columns:
        return None
    hit = table[table["finding_id"].astype(str).eq(finding_id)]
    if hit.empty or "cost_chf" not in hit.columns or pd.isna(hit.iloc[0]["cost_chf"]):
        return None
    return float(hit.iloc[0]["cost_chf"])


def factors_table() -> pd.DataFrame | None:
    """factors/factors.csv as stored (low / mid / high, source, notes). Read only."""
    return _read(ROOT / "factors" / "factors.csv")


def kb_text(relpath: str) -> str | None:
    """A kb or submission markdown file, as stored (jury answers, path to operation). None if absent."""
    path = ROOT / relpath
    return path.read_text(encoding="utf-8") if path.exists() else None


def one_off_total() -> float | None:
    """Sum of one-off extra costs inside the baseline (docs/one_off_costs.csv: T-1212, T-1189). Never a saving."""
    frame = _read(ROOT / "docs" / "one_off_costs.csv")
    if frame is None or "extra_cost_chf" not in frame.columns:
        return None
    return float(pd.to_numeric(frame["extra_cost_chf"], errors="coerce").fillna(0).sum())
