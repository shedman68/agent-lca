"""Presentation of numbers already computed in out/ or measures/.

Nothing here changes a figure. A missing value stays an em dash.
"""
from __future__ import annotations

import pandas as pd


def missing(v) -> bool:
    return v is None or pd.isna(v)


def signed_pct(reduction_pct, digits: int = 1) -> str:
    """A reduction as '−28.4 %'. An increase as '+3.2 %'. Near zero as '0 %'."""
    if missing(reduction_pct):
        return "–"
    value = float(reduction_pct)
    if abs(value) < 0.05:
        return "0 %"
    number = f"{abs(value):,.{digits}f}"
    return f"−{number} %" if value > 0 else f"+{number} %"


def package_saved_line(summary) -> str:
    """One caption for the chosen package. Percents are printed from the summary row."""
    return (
        "Chosen package in `measures/package_summary.csv`: "
        f"CO2 low {signed_pct(summary['co2_pct_low'])} · mid {signed_pct(summary['co2_pct_mid'])} · "
        f"high {signed_pct(summary['co2_pct_high'])} · cost {signed_pct(summary['chf_pct'])} · "
        f"{float(summary['effort_pd']):.1f} person-days. "
        "Unticking a row shows the trade-off against that package."
    )
