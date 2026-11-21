"""
QA: recompute CO2 by department, tool and country independently and compare with the app (app/data.py impact_by).

Independent route: the app joins out/fact_costs.csv and out/fact_costs_allocated.csv row by row by position.
Here the two files are joined by content (source, date, resource_id, unit, quantity, cost_chf, model, cost_center),
and each fact row's CO2 is split over departments by quantity_alloc / quantity (cost share where quantity is 0).

Usage: python analysis/check_app_co2.py --out out
"""
import argparse, logging, sys, warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")
logging.disable(logging.WARNING)
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=Path("out"), type=Path)
a = ap.parse_args()

KEY = ["source", "date", "resource_id", "unit", "quantity", "cost_chf", "model", "cost_center"]
LV = ("low", "mid", "high")
f = pd.read_csv(a.out / "fact_costs.csv", low_memory=False)
al = pd.read_csv(a.out / "fact_costs_allocated.csv", low_memory=False)
f, al = f[f.in_baseline.astype(str).eq("True")].copy(), al[al.in_baseline.astype(str).eq("True")].copy()
for d in (f, al):
    for c in KEY:
        d[c] = d[c].astype(str)

fk = f.groupby(KEY, dropna=False).agg(**{f"co2_{l}": (f"co2_kg_{l}", "sum") for l in LV},
                                       q=("quantity", lambda s: pd.to_numeric(s).sum()),
                                       chf=("cost_chf", lambda s: pd.to_numeric(s).sum()),
                                       country=("country", "first")).reset_index()
ak = al.groupby(KEY + ["dept_allocated"], dropna=False).agg(q_alloc=("quantity_alloc", "sum"),
                                                            chf_alloc=("cost_chf_alloc", "sum"),
                                                            tool=("tool", "first")).reset_index()
m = ak.merge(fk, on=KEY, how="left", validate="many_to_one")
unmatched = m.co2_mid.isna().sum()
share = (m.q_alloc / m.q).where(m.q != 0, m.chf_alloc / m.chf.where(m.chf != 0))
m["share"] = share.fillna(0)
for l in LV:
    m[f"co2_alloc_{l}"] = m[f"co2_{l}"] * m.share

tot_fact = f.co2_kg_mid.sum()
tot_mine = m.co2_alloc_mid.sum()
print(f"rows: facts {len(f)}, allocated {len(al)}, allocated keys without a fact match {unmatched}")
print(f"CO2 mid total: fact_costs {tot_fact:,.1f} kg | independent allocated {tot_mine:,.1f} kg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import data as appdata  # noqa: E402  (app/data.py, Streamlit cache works outside a running app)

worst = 0.0
for dim, mine_key in [("department", "dept_allocated"), ("country", "country"), ("resource", "resource_id")]:
    mine = m.groupby(mine_key, dropna=False).co2_alloc_mid.sum()
    app = appdata.impact_by(dim, "co2", "mid")
    if dim == "country":
        lab = {v: k for k, v in appdata.COUNTRY_LABEL.items()}
        app["key"] = app.label.map(lab).fillna(app.label)
    elif dim == "resource":
        app["key"] = app.label.str.extract(r"\(([^()]*)\)$")[0]
    else:
        app["key"] = app.label
    cmp = pd.DataFrame({"independent_kg": mine}).join(app.set_index("key")["amount"].rename("app_kg"), how="outer").fillna(0)
    cmp["diff_kg"] = cmp.app_kg - cmp.independent_kg
    worst = max(worst, cmp.diff_kg.abs().max())
    print(f"\n== CO2 mid by {dim}: max |diff| {cmp.diff_kg.abs().max():.3f} kg")
    print(cmp.sort_values("independent_kg", ascending=False).head(12).round(1).to_string())
for l in LV:
    print(f"total {l}: independent {m[f'co2_alloc_{l}'].sum():,.1f} | fact_costs {f[f'co2_kg_{l}'].sum():,.1f}")
print("\nRESULT:", "SAME (max diff < 0.5 kg)" if worst < 0.5 else f"DIFFERENT (max diff {worst:.1f} kg)")
