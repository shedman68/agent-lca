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
            for c in ("cost_chf", "share_of_total_pct", "addressable_chf"):
                f[c] = pd.to_numeric(f[c], errors="coerce")
            return f, label
    return None, None


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
    for c in ("effort_person_days", "savings_cost_chf_per_year", "savings_energy_kwh_per_year", "savings_co2_kg_location_based"):
        if c in m:
            m[c] = pd.to_numeric(m[c], errors="coerce").fillna(0.0)
    return m, label
