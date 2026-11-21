"""Sensitivity: what the idle-power factors do to the measures package (Vinzenz, 21.11.2026).
Reads only committed outputs: factors/factors.csv, out/findings.csv, out/fact_costs.csv, measures/candidates.csv.
Does NOT change the pipeline or measures.py (Rashed owns those). Usage:
    python factors/scripts/idle_impact.py
Variant A: baseline unchanged; paused hours of M1 (dp-dev) and M2 (gpu-ml-01) counted at the idle factor.
Variant B: as A, and the dp-dev baseline also counted physically (active hours at node_hour, idle hours at node_hour_idle).
Both variants are shown with and without C2 (move dp-dev Frankfurt -> Zurich).
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
LV = ["low", "mid", "high"]
fa = pd.read_csv(ROOT / "factors/factors.csv").set_index("key")
fn = pd.read_csv(ROOT / "out/findings.csv").set_index("finding_id")
fc = pd.read_csv(ROOT / "out/fact_costs.csv", low_memory=False); b = fc[fc.in_baseline]
c = pd.read_csv(ROOT / "measures/candidates.csv").set_index("measure_id")
chosen = c[c.chosen.astype(str) == "True"]
col = {"low": "savings_co2_kg_low", "mid": "savings_co2_kg_location_based", "high": "savings_co2_kg_high"}
ACTIVE = 748 / 8616   # dp-dev active share of runtime, out/findings.csv F1 evidence
M2_SHARE = 0.75       # energy share used in measures.py for M2

def f(k, l): return float(fa.loc[k, f"value_{l}"])

rows = []
for l in LV:
    base = b[f"co2_kg_{l}"].sum(); pkg = chosen[col[l]].sum()
    r_node = f("node_hour_idle", l) / f("node_hour", l)
    r_gpu = min(1.0, f("gpu_hour_idle", l) / f("gpu_hour", l))
    m1_old = c.loc["M1", col[l]]; m2_old = c.loc["M2", col[l]]
    m1_new = fn.loc["F1", f"addressable_co2_kg_{l}"] * r_node
    m2_new = fn.loc["F3", f"addressable_co2_kg_{l}"] * r_gpu
    dpdev = b[b.resource_id == "dp-dev"][f"co2_kg_{l}"].sum()
    dpdev_b = dpdev * (ACTIVE + (1 - ACTIVE) * r_node)
    grid = 1 - f("grid_CH", l) / f("grid_DE", l)
    pkg_a = pkg - m1_old - m2_old + m1_new + m2_new
    base_b = base - dpdev + dpdev_b
    c2_a = (dpdev - m1_new) * grid; c2_b = (dpdev_b - m1_new) * grid
    rows.append({"level": l, "baseline_t": base / 1000, "pkg_now_pct": 100 * pkg / base,
                 "ratio_node_idle": r_node, "ratio_gpu_idle": r_gpu,
                 "M1_kg_now": m1_old, "M1_kg_idle": m1_new, "M2_kg_now": m2_old, "M2_kg_idle": m2_new,
                 "A_pct": 100 * pkg_a / base, "A_plus_C2_pct": 100 * (pkg_a + c2_a) / base,
                 "B_baseline_t": base_b / 1000, "B_pct": 100 * pkg_a / base_b, "B_plus_C2_pct": 100 * (pkg_a + c2_b) / base_b})
out = pd.DataFrame(rows).set_index("level").T.round(3)
print(out.to_string())
out.to_csv(ROOT / "factors/kb/V2-idle-impact.csv")
