"""Sort order for the optimisation cards on "Your plan". Text and order only: no number is changed here.

Three views (the key is stored in st.session_state, the label is shown):
- co2:  CO2 saved per year (the picked factor set), high to low. Ties: CHF, then ID.
- cost: CHF saved per year, high to low. Ties: CO2, then ID.
- both: combined share = CO2 / total CO2 + CHF / total CHF over the shown rows, high to low. Ties: CO2, CHF, ID.
Licence optimisations have no CO2 (SaaS has no energy factor): they count as 0 kg and stay in the list.
"""
from __future__ import annotations

import pandas as pd

SORTS = {"co2": "Biggest CO2 saving", "cost": "Biggest cost saving", "both": "CO2 and cost together"}
DEFAULT = "co2"
CHF_COL = "savings_cost_chf_per_year"


def _num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").fillna(0.0)


def sort_rows(rows: pd.DataFrame, co2_col: str, how: str = DEFAULT) -> pd.DataFrame:
    """Return a copy of rows in display order, with helper columns _co2, _chf and _share. Input is not changed."""
    df = rows.copy()
    df["_co2"] = _num(df[co2_col]) if co2_col in df else 0.0
    df["_chf"] = _num(df[CHF_COL]) if CHF_COL in df else 0.0
    tot_co2, tot_chf = float(df["_co2"].sum()), float(df["_chf"].sum())
    df["_share"] = (df["_co2"] / tot_co2 if tot_co2 else 0.0) + (df["_chf"] / tot_chf if tot_chf else 0.0)
    df["_id"] = df["measure_id"].astype(str) if "measure_id" in df else ""
    if how == "cost":
        keys, asc = ["_chf", "_co2", "_id"], [False, False, True]
    elif how == "both":
        keys, asc = ["_share", "_co2", "_chf", "_id"], [False, False, False, True]
    else:
        keys, asc = ["_co2", "_chf", "_id"], [False, False, True]
    return df.sort_values(keys, ascending=asc, kind="mergesort").reset_index(drop=True)


def short_name(text: str, limit: int = 26) -> str:
    """First words of a description, cut at a word boundary, for chart labels."""
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(",;:") + " …"
