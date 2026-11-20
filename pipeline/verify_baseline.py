"""
Independent check of the baseline-year cost, written separately from pipeline.py.
Different route: merge the exchange rates as a table (not row-by-row mapping),
sum without imputation, then add the imputed amounts from out/fact_costs.csv.
The two totals must match to the franc.

Usage: python verify_baseline.py --data <case data folder> --out out
"""
import argparse
from pathlib import Path
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True, type=Path)
ap.add_argument("--out", default=Path("out"), type=Path)
a = ap.parse_args()
R = lambda n: pd.read_csv(a.data / n, encoding="utf-8-sig").drop_duplicates()

fx = pd.read_csv(a.data / "exchange_rates.csv", encoding="utf-8-sig")
fx["ym"] = fx["month"].str[:7]
rates = pd.concat([fx.assign(cur="EUR", r=fx.eur_chf), fx.assign(cur="USD", r=fx.usd_chf),
                   fx.assign(cur="CHF", r=1.0)])[["ym", "cur", "r"]]

def total(df, ymcol, amt, cur):
    d = df.assign(ym=ymcol, cur=cur).merge(rates, on=["ym", "cur"], how="left")
    assert d["r"].notna().all(), "missing exchange rate"
    d = d[(d.ym >= "2025-09") & (d.ym <= "2026-08")]
    return (d[amt] * d["r"]).sum()   # NaN costs are skipped here (no imputation)

az, aw, ho, ai = R("azure_costs.csv"), R("aws_costs.csv"), R("hoster_invoice.csv"), R("ai_usage.csv")
su, sa = R("ai_subscriptions.csv"), R("saas_contracts.csv")
su, sa = su[su.contract_status.eq("Final")], sa[sa.contract_status.eq("Final")]
parts = {
    "azure": total(az, az.Date.str[:7], "CostInBillingCurrency", az.BillingCurrency),
    "aws": total(aw, aw.line_item_usage_start_date.str[:7], "line_item_unblended_cost", aw.line_item_currency_code),
    "hoster": total(ho, ho.Date.str[6:10] + "-" + ho.Date.str[3:5], "Amount_CHF", "CHF"),
    "ai_usage": total(ai, ai.date.str[:7], "cost_chf", "CHF"),
    "ai_subscriptions": total(su, su.month.str[:7], "amount", su.currency),
    "saas": total(sa, sa.month.str[:7], "amount", sa.currency),
}
raw = sum(parts.values())
f = pd.read_csv(a.out / "fact_costs.csv", parse_dates=["date"], low_memory=False)
b = f[f.in_baseline]
imputed = b.loc[b.cost_imputed.astype(bool), "cost_chf"].sum()
pipe = b.cost_chf.sum()
print("Independent sum without imputation:", f"{raw:,.2f}")
print("Imputed amounts in pipeline:       ", f"{imputed:,.2f}")
print("Independent + imputed:             ", f"{raw + imputed:,.2f}")
print("Pipeline total:                    ", f"{pipe:,.2f}")
for k, v in parts.items():
    pv = b.loc[b.source == k, "cost_chf"].sum() - b.loc[(b.source == k) & b.cost_imputed.astype(bool), "cost_chf"].sum()
    print(f"  {k:17s} independent {v:12,.2f}   pipeline excl. imputed {pv:12,.2f}   diff {pv - v:8.2f}")
ok = abs(raw + imputed - pipe) < 1
print("MATCH" if ok else "MISMATCH – investigate before using the baseline")
