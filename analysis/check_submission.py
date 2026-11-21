"""
QA: cross-check both submission tables against their sources.

  submission/template_baseline_and_assumptions.csv  vs out/fact_costs.csv (totals) and factors/factors.csv (factors)
  submission/template_measures_package.csv           vs measures/measures.csv and measures/package_summary.csv
  both                                               vs the official templates in data/ (columns, rows, encoding)

Usage: python analysis/check_submission.py   (prints one line per check and a summary)
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
rd = lambda p: pd.read_csv(ROOT / p, encoding="utf-8-sig")
res = []


def chk(area, item, sub, src, ok, note=""):
    res.append(dict(area=area, item=item, submission=sub, source=src, status="OK" if ok else "MISMATCH", note=note))


close = lambda a, b, tol=0.051: (pd.isna(a) and pd.isna(b)) or (pd.notna(a) and pd.notna(b) and abs(float(a) - float(b)) <= tol)

# ---------- format against the official templates
for name in ["template_baseline_and_assumptions.csv", "template_measures_package.csv"]:
    sub_raw, tpl_raw = (ROOT / "submission" / name).read_bytes(), (ROOT / "data" / name).read_bytes()
    chk("format", f"{name}: UTF-8 BOM like the template", sub_raw[:3] == b"\xef\xbb\xbf", tpl_raw[:3] == b"\xef\xbb\xbf",
        (sub_raw[:3] == b"\xef\xbb\xbf") == (tpl_raw[:3] == b"\xef\xbb\xbf"))
    s, t = rd(f"submission/{name}"), rd(f"data/{name}")
    chk("format", f"{name}: columns", "|".join(s.columns), "|".join(t.columns), list(s.columns) == list(t.columns))
    if name.startswith("template_baseline"):
        chk("format", f"{name}: parameter rows and order", len(s), len(t), list(s.parameter) == list(t.parameter))
        must = t[t.must_or_bonus.eq("Must")].parameter
        empty = [p for p in must if s.set_index("parameter").loc[p, ["value_low", "value_mid", "value_high"]].isna().all()]
        chk("format", f"{name}: every Must row has a value", ", ".join(empty) or "all filled", "", not empty)

# ---------- baseline totals against out/
b = pd.read_csv(ROOT / "out/fact_costs.csv", low_memory=False)
b = b[b.in_baseline.astype(bool)]
s = rd("submission/template_baseline_and_assumptions.csv").set_index("parameter")
chk("baseline", "total_cost_baseline_year_chf (mid)", s.loc["total_cost_baseline_year_chf", "value_mid"], round(b.cost_chf.sum(), 2),
    close(s.loc["total_cost_baseline_year_chf", "value_mid"], round(b.cost_chf.sum(), 2), 0.005))
for p, col in [("total_energy_baseline_year_kwh", "kwh"), ("total_co2_location_based_baseline_year_kg", "co2_kg")]:
    for l in ("low", "mid", "high"):
        v = round(b[f"{col}_{l}"].sum(), 1)
        chk("baseline", f"{p} ({l})", s.loc[p, f"value_{l}"], v, close(s.loc[p, f"value_{l}"], v))

# ---------- factors against factors/factors.csv (template_parameter column maps the rows)
fac = rd("factors/factors.csv")
fmap = fac.dropna(subset=["template_parameter"])
fmap = fmap[~fmap.template_parameter.str.startswith("(")].set_index("template_parameter")
for p in s.index:
    if p in fmap.index:
        for l in ("low", "mid", "high"):
            chk("factors", f"{p} ({l})", s.loc[p, f"value_{l}"], fmap.loc[p, f"value_{l}"],
                close(s.loc[p, f"value_{l}"], fmap.loc[p, f"value_{l}"], 1e-9))
for p in ["total_co2_market_based_baseline_year_kg", "grid_mix_market_based", "growth_per_year"]:
    chk("not in out/", p, "/".join(str(s.loc[p, f"value_{l}"]) for l in ("low", "mid", "high")), "factors/kb (Vinzenz)", True,
        "bonus row; not derivable from out/, check the source column")

# ---------- measures table against measures/measures.csv and package_summary.csv
mt, mm = rd("submission/template_measures_package.csv"), rd("measures/measures.csv")
summ = rd("measures/package_summary.csv").set_index(rd("measures/package_summary.csv").columns[0]).iloc[:, 0]
chk("measures", "measure ids", "|".join(mt.measure_id), "|".join(mm.measure_id), list(mt.measure_id) == list(mm.measure_id))
cols = [c for c in mt.columns if c in mm.columns and c != "measure_id"]
for _, r in mt.iterrows():
    src = mm.set_index("measure_id").loc[r.measure_id]
    for c in cols:
        a, z = r[c], src[c]
        same = close(a, z, 0.5) if isinstance(a, (int, float)) and not isinstance(a, bool) else (str(a) == str(z) or (pd.isna(a) and pd.isna(z)))
        appended = isinstance(a, str) and isinstance(z, str) and a.startswith(z)   # submission adds a sentence, source text kept
        if appended and not same:
            chk("measures", f"{r.measure_id}.{c}", f"+{len(a) - len(z)} chars appended", "source text kept", True,
                a[len(z):].strip()[:90])
        elif not same:
            chk("measures", f"{r.measure_id}.{c}", str(a)[:60], str(z)[:60], False)
tot = {"effort_pd": mt.effort_person_days.sum(), "chf": mt.savings_cost_chf_per_year.sum(),
       "kwh_mid": mt.savings_energy_kwh_per_year.sum(), "co2_mid": mt.savings_co2_kg_location_based.sum()}
for k, v in tot.items():
    chk("package", f"sum {k}", round(v, 1), float(summ[k]), close(v, float(summ[k]), 1.0))
for l, col in [("low", "savings_co2_kg_low"), ("high", "savings_co2_kg_high")]:
    chk("package", f"sum co2_{l} (measures.csv)", round(mm[col].sum(), 1), float(summ[f"co2_{l}"]), close(mm[col].sum(), float(summ[f"co2_{l}"]), 1.0))
base = {"low": b.co2_kg_low.sum(), "mid": b.co2_kg_mid.sum(), "high": b.co2_kg_high.sum()}
for l in ("low", "mid", "high"):
    pct = round(float(summ[f"co2_{l}"]) / base[l] * 100, 1)
    chk("package", f"co2_pct_{l} = co2_{l} / baseline {l}", pct, float(summ[f"co2_pct_{l}"]), close(pct, float(summ[f"co2_pct_{l}"]), 0.05))
pct = round(float(summ["chf"]) / b.cost_chf.sum() * 100, 1)
chk("package", "chf_pct = chf / baseline", pct, float(summ["chf_pct"]), close(pct, float(summ["chf_pct"]), 0.05))
chk("package", "effort_chf = PD x 1,100", float(summ["effort_pd"]) * 1100, float(summ["effort_chf"]), float(summ["effort_pd"]) * 1100 == float(summ["effort_chf"]))
chk("package", "targets: CO2 >= 40 % mid, cost >= 25 %, <= 15 PD",
    f"{summ['co2_pct_mid']} / {summ['chf_pct']} / {summ['effort_pd']}", "40 / 25 / 15",
    float(summ["co2_pct_mid"]) >= 40 and float(summ["chf_pct"]) >= 25 and float(summ["effort_pd"]) <= 15)

# ---------- measures against findings (same resource, derived numbers)
fi = pd.read_csv(ROOT / "out/findings.csv").set_index("finding_id")
for mid, fid in [("M1", "F1"), ("M3", "F4"), ("M6", "F13")]:
    r = mm.set_index("measure_id").loc[mid]
    chk("vs findings", f"{mid} CHF = {fid} addressable", r.savings_cost_chf_per_year, round(fi.loc[fid, "addressable_chf"]),
        close(r.savings_cost_chf_per_year, round(fi.loc[fid, "addressable_chf"]), 1))
    chk("vs findings", f"{mid} CO2 mid = {fid}", r.savings_co2_kg_location_based, round(fi.loc[fid, "addressable_co2_kg_mid"]),
        close(r.savings_co2_kg_location_based, round(fi.loc[fid, "addressable_co2_kg_mid"]), 1))

out = pd.DataFrame(res)
pd.set_option("display.width", 230, "display.max_colwidth", 70, "display.max_rows", 300)
print(out.to_string(index=False))
print(f"\nSUMMARY: {len(out)} checks, {int((out.status == 'MISMATCH').sum())} mismatches")
out.to_csv(ROOT / "analysis/kb/submission_checks.csv", index=False)
