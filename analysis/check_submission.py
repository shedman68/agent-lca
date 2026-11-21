"""
QA: cross-check both submission tables against their sources.

  submission/template_baseline_and_assumptions.csv  vs out/fact_costs.csv (totals) and factors/factors.csv (factors, sources)
  submission/template_measures_package.csv           vs measures/measures.csv, measures/package_summary.csv, out/findings.csv
  both                                               vs the official templates in data/ (columns, rows, encoding)

Every printed row is one real comparison. Rows that cannot be compared are listed separately as notes, not counted.
Tolerances: effort exact; CHF/kWh/CO2 of a measure exact (integers); sums and derived values within rounding (stated per row).
Usage: python analysis/check_submission.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
rd = lambda p: pd.read_csv(ROOT / p, encoding="utf-8-sig")
res, notes = [], []
ALLOWED_SUFFIX = ("Market-based CO2 stays blank: measures/measures.csv has no market-based kilogram, "
                  "and the pipeline baseline is location-based.")


def chk(area, item, sub, src, ok, note=""):
    res.append(dict(area=area, item=item, submission=sub, source=src, status="OK" if bool(ok) else "MISMATCH", note=note))


def near(a, b, tol):
    if pd.isna(a) and pd.isna(b):
        return True
    return pd.notna(a) and pd.notna(b) and abs(float(a) - float(b)) <= tol


# ---------- format against the official templates
for name in ["template_baseline_and_assumptions.csv", "template_measures_package.csv"]:
    sub_raw, tpl_raw = (ROOT / "submission" / name).read_bytes(), (ROOT / "data" / name).read_bytes()
    bom = lambda r: r[:3] == b"\xef\xbb\xbf"
    chk("format", f"{name}: UTF-8 BOM like the template", bom(sub_raw), bom(tpl_raw), bom(sub_raw) == bom(tpl_raw))
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
chk("baseline", "total_cost_baseline_year_chf (mid), exact to the rappen", s.loc["total_cost_baseline_year_chf", "value_mid"],
    round(b.cost_chf.sum(), 2), near(s.loc["total_cost_baseline_year_chf", "value_mid"], round(b.cost_chf.sum(), 2), 0.005))
for p, col in [("total_energy_baseline_year_kwh", "kwh"), ("total_co2_location_based_baseline_year_kg", "co2_kg")]:
    for l in ("low", "mid", "high"):
        v = round(b[f"{col}_{l}"].sum(), 1)
        chk("baseline", f"{p} ({l}), within 0.05", s.loc[p, f"value_{l}"], v, near(s.loc[p, f"value_{l}"], v, 0.05))

# ---------- factors against factors/factors.csv (template_parameter maps the rows), plus source present
fac = rd("factors/factors.csv")
fk = fac.set_index("key")
fmap = fac.dropna(subset=["template_parameter"])
fmap = fmap[~fmap.template_parameter.str.startswith("(")].set_index("template_parameter")
for p in s.index:
    if p in fmap.index:
        for l in ("low", "mid", "high"):
            chk("factors", f"{p} ({l}), exact", s.loc[p, f"value_{l}"], fmap.loc[p, f"value_{l}"],
                near(s.loc[p, f"value_{l}"], fmap.loc[p, f"value_{l}"], 1e-12))
        src = str(s.loc[p, "source"])
        chk("factors", f"{p}: source given", src[:50], "non-empty source", src.strip() not in ("", "nan"))

# market-based total: kWh x grid_market_based (factors.csv), the same formula Vinzenz used
for l in ("low", "mid", "high"):
    v = round(b[f"kwh_{l}"].sum() * float(fk.loc["grid_market_based", f"value_{l}"]), 1)
    p = "total_co2_market_based_baseline_year_kg"
    chk("baseline", f"{p} ({l}) = kWh x grid_market_based, within 0.5", s.loc[p, f"value_{l}"], v, near(s.loc[p, f"value_{l}"], v, 0.5))
notes.append("growth_per_year is blank (bonus). T-1261 is shown as a sentence and range on the Next year page (10:10 decision).")

# ---------- measures table against measures/measures.csv
mt, mm = rd("submission/template_measures_package.csv"), rd("measures/measures.csv")
mmi = mm.set_index("measure_id")
summ = rd("measures/package_summary.csv")
summ = summ.set_index(summ.columns[0]).iloc[:, 0]
chk("measures", "measure ids and order", "|".join(mt.measure_id), "|".join(mm.measure_id), list(mt.measure_id) == list(mm.measure_id))
NUM = ["effort_person_days", "savings_cost_chf_per_year", "savings_energy_kwh_per_year", "savings_co2_kg_location_based"]
TXT = ["description", "resource_or_source", "change", "risks_and_exceptions"]
for _, r in mt.iterrows():
    src = mmi.loc[r.measure_id]
    for c in NUM:
        chk("measures", f"{r.measure_id}.{c}, exact", r[c], src[c], near(r[c], src[c], 0))
    for c in TXT:
        chk("measures", f"{r.measure_id}.{c}, identical text", str(r[c])[:40], str(src[c])[:40], str(r[c]) == str(src[c]))
    a, z = str(r.assumptions_and_sources), str(src.assumptions_and_sources)
    ok = a == z or a == f"{z} {ALLOWED_SUFFIX}"
    chk("measures", f"{r.measure_id}.assumptions_and_sources, identical or + the one allowed sentence",
        f"+{len(a) - len(z)} chars" if a != z else "identical", "measures.csv text", ok,
        "" if ok else f"unexpected text: {a[len(z):][:80]}")
    chk("measures", f"{r.measure_id}.savings_co2_kg_market_based blank (stated in the allowed sentence)",
        r.savings_co2_kg_market_based, "blank", pd.isna(r.savings_co2_kg_market_based))

# ---------- package: sums of the template itself, then targets on those sums
tot = {"effort_pd": (mt.effort_person_days.sum(), 0), "chf": (mt.savings_cost_chf_per_year.sum(), 0),
       "kwh_mid": (mt.savings_energy_kwh_per_year.sum(), 0), "co2_mid": (mt.savings_co2_kg_location_based.sum(), 0)}
for k, (v, tol) in tot.items():
    chk("package", f"template sum {k} = package_summary, exact", round(v, 1), float(summ[k]), near(v, float(summ[k]), tol))
for l, col in [("low", "savings_co2_kg_low"), ("high", "savings_co2_kg_high")]:
    chk("package", f"sum co2_{l} (measures.csv) = package_summary, exact", round(mm[col].sum(), 1), float(summ[f"co2_{l}"]),
        near(mm[col].sum(), float(summ[f"co2_{l}"]), 0))
base = {"low": b.co2_kg_low.sum(), "mid": b.co2_kg_mid.sum(), "high": b.co2_kg_high.sum()}
co2_sum = {"low": mm.savings_co2_kg_low.sum(), "mid": mt.savings_co2_kg_location_based.sum(), "high": mm.savings_co2_kg_high.sum()}
for l in ("low", "mid", "high"):
    pct = co2_sum[l] / base[l] * 100
    chk("package", f"co2_pct_{l} = sum / baseline {l}, within 0.05 pp", round(pct, 2), float(summ[f"co2_pct_{l}"]),
        near(pct, float(summ[f"co2_pct_{l}"]), 0.05))
chf_pct = mt.savings_cost_chf_per_year.sum() / b.cost_chf.sum() * 100
chk("package", "chf_pct = template sum / baseline, within 0.05 pp", round(chf_pct, 2), float(summ["chf_pct"]), near(chf_pct, float(summ["chf_pct"]), 0.05))
pd_sum = mt.effort_person_days.sum()
chk("package", "effort_chf = template PD x 1,100, exact", pd_sum * 1100, float(summ["effort_chf"]), pd_sum * 1100 == float(summ["effort_chf"]))
for l in ("low", "mid", "high"):
    chk("package", f"target CO2 >= 40 % on {l} (from template/measures sums)", round(co2_sum[l] / base[l] * 100, 2), ">= 40", co2_sum[l] / base[l] >= 0.40)
chk("package", "target cost >= 25 % (template sum)", round(chf_pct, 2), ">= 25", chf_pct >= 25)
chk("package", "budget <= 15 PD (template sum)", pd_sum, "<= 15", pd_sum <= 15)

# ---------- measures against findings (out/findings.csv) with the stated shares
fi = pd.read_csv(ROOT / "out/findings.csv").set_index("finding_id")
SHARE = {"M1": (["F1"], 1.0, 1.0), "M2": (["F3"], 1.0, 0.75), "M3": (["F4"], 1.0, 1.0), "M4": (["F5"], 8 / 12, 8 / 12),
         "M5": (["F2"], 0.8, 0.8), "M6": (["F13"], 1.0, 1.0), "M7": (["F6", "F7"], 0.8, 0.8)}
for mid, (fids, s_chf, s_e) in SHARE.items():
    r = mmi.loc[mid]
    chf = sum(fi.loc[f, "addressable_chf"] for f in fids) * s_chf
    co2 = sum(fi.loc[f, "addressable_co2_kg_mid"] for f in fids) * s_e
    chk("vs findings", f"{mid} CHF = {'+'.join(fids)} x {s_chf:.0%}, within 1", r.savings_cost_chf_per_year, round(chf), near(r.savings_cost_chf_per_year, chf, 1))
    chk("vs findings", f"{mid} CO2 mid = {'+'.join(fids)} x {s_e:.0%}, within 1", r.savings_co2_kg_location_based, round(co2), near(r.savings_co2_kg_location_based, co2, 1))
notes.append("M8 (per contract, measures/m8_contracts.csv) and C1 (assumption 50 % of large-model tasks) are not shares of one finding: not compared.")

# ---------- protection rules cited where a measure touches a protected or windowed resource
RULES = {"M1": ["T-1053"], "M2": ["T-1101"], "M3": ["T-1204", "T-1094"], "M4": ["T-1204", "T-1094"], "M5": ["T-1029"], "M6": ["T-1039"], "M7": ["T-1128"]}
for mid, tickets in RULES.items():
    txt = str(mt.set_index("measure_id").loc[mid, "risks_and_exceptions"])
    missing = [t for t in tickets if t not in txt]
    chk("rules", f"{mid} risks cite {', '.join(tickets)}", "missing: " + ", ".join(missing) if missing else "all cited", ", ".join(tickets), not missing)

out = pd.DataFrame(res)
pd.set_option("display.width", 230, "display.max_colwidth", 70, "display.max_rows", 400)
print(out.to_string(index=False))
print("\nNOTES (not counted):\n- " + "\n- ".join(notes))
print(f"\nSUMMARY: {len(out)} comparisons, {int((out.status == 'MISMATCH').sum())} mismatches")
print(out.groupby("area").status.value_counts().unstack(fill_value=0).to_string())
out.to_csv(ROOT / "analysis/kb/submission_checks.csv", index=False)
