"""V6 - energy and CO2 of our own AI use during the sprint (Vinzenz, 21.11.2026).
Input: factors/kb/V6-tokens.csv (one row per person / tool / model class, measured token counts with cache split).
kWh = [ (fresh + cache_write + cache_read x cache_read_share) / 1000 x tokens_in_1000_<class>
        + out / 1000 x tokens_out_1000_<class> ] x pue_default ;  CO2 = kWh x grid_EU.
All factors from factors/factors.csv, at the same level (low / mid / high). Usage: python factors/scripts/own_ai.py
"""
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
fa = pd.read_csv(ROOT / "factors/factors.csv").set_index("key")
t = pd.read_csv(ROOT / "factors/kb/V6-tokens.csv")
out = []
for l in ["low", "mid", "high"]:
    v = lambda k: float(fa.loc[k, f"value_{l}"])
    t["kwh_" + l] = ((t.tokens_in_fresh + t.tokens_cache_write + t.tokens_cache_read * v("cache_read_share")) / 1000
                     * t.model_class.map(lambda c: v(f"tokens_in_1000_{c}"))
                     + t.tokens_out / 1000 * t.model_class.map(lambda c: v(f"tokens_out_1000_{c}"))) * v("pue_default")
    t["co2_kg_" + l] = t["kwh_" + l] * v("grid_EU")
t["tokens_in_total"] = t.tokens_in_fresh + t.tokens_cache_write + t.tokens_cache_read
cols = ["tokens_in_total", "tokens_cache_read", "tokens_out"] + [f"{m}_{l}" for m in ["kwh", "co2_kg"] for l in ["low", "mid", "high"]]
by = t.groupby("person")[cols].sum(); by.loc["TOTAL"] = by.sum()
pd.set_option("display.width", 200); print(by.round(3).to_string())
by.round(4).to_csv(ROOT / "factors/kb/V6-result.csv")
