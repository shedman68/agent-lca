"""Data layer for the app. Reads only out/ (pipeline output) and analysis/kb/ (Hakim's knowledge base).

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
    f["tool_canonical"] = f["resource_id"].map(names)
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


def by_dimension(dim: str) -> pd.DataFrame:
    """dim in {'department', 'resource', 'country', 'source'} -> CHF per group, largest first."""
    f = facts()
    if dim == "department":
        g = f.groupby("dept_allocated")["cost_chf_alloc"].sum().rename("cost_chf").reset_index()
        g = g.rename(columns={"dept_allocated": "label"})
    elif dim == "resource":
        g = f.groupby(["resource_id", "tool_canonical"]).agg(
            cost_chf=("cost_chf_alloc", "sum"),
            tool_spellings=("tool", "nunique"),
            source=("source_label", "first"),
            responsible_role=("responsible_role", lambda r: r.iloc[0] if r.nunique() == 1 else "several (per tool)"),
        ).reset_index()
        g["label"] = g["tool_canonical"] + " (" + g["resource_id"] + ")"
    elif dim == "country":
        g = f.groupby("country_label")["cost_chf_alloc"].sum().rename("cost_chf").reset_index()
        g = g.rename(columns={"country_label": "label"})
    elif dim == "source":
        g = f.groupby("source_label")["cost_chf_alloc"].sum().rename("cost_chf").reset_index()
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
    return float(s["cost_chf_alloc"].sum()), str(s["responsible_role"].mode().iloc[0])


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


def findings_markdown() -> str | None:
    p = KB / "findings.md"
    return p.read_text(encoding="utf-8") if p.exists() else None


@st.cache_data(show_spinner=False)
def measures() -> pd.DataFrame | None:
    """Measures package in the template format (submission/template_measures_package.csv columns).

    Expected at out/measures.csv (written by measures/measures.py, task R1/R2). None until then.
    """
    m = _read(OUT / "measures.csv")
    if m is None:
        return None
    m = m[~m["measure_id"].astype(str).str.startswith("Example")].copy()
    for c in ("effort_person_days", "savings_cost_chf_per_year", "savings_energy_kwh_per_year", "savings_co2_kg_location_based"):
        if c in m:
            m[c] = pd.to_numeric(m[c], errors="coerce").fillna(0.0)
    return m
