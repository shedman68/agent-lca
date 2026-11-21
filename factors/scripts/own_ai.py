"""V6 – energy and CO2 of our own AI use during the sprint (Vinzenz, 21.11.2026).
Input: factors/kb/V6-tokens.csv (one row per person/tool/model class). Factors: factors/factors.csv.
kWh = tokens_in/1000 x tokens_in_1000_<class> + tokens_out/1000 x tokens_out_1000_<class>, x PUE; CO2 = kWh x grid_EU.
Cached input is counted as normal input (upper bound: cache reads need far less compute). Usage: python factors/scripts/own_ai.py
"""
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
fa = pd.read_csv(ROOT / "factors/factors.csv").set_index("key")
t = pd.read_csv(ROOT / "factors/kb/V6-tokens.csv")
rows = []
for l in ["low", "mid", "high"]:
    v = lambda k: float(fa.loc[k, f"value_{l}"])
    kwh = sum(r.tokens_in / 1000 * v(f"tokens_in_1000_{r.model_class}") + r.tokens_out / 1000 * v(f"tokens_out_1000_{r.model_class}") for r in t.itertuples())
    kwh *= v("pue_default")
    rows.append({"level": l, "kwh": round(kwh, 2), "co2_kg": round(kwh * v("grid_EU"), 2)})
print(t.groupby("person")[["tokens_in", "tokens_out", "web_searches"]].sum().to_string())
print(pd.DataFrame(rows).to_string(index=False))
