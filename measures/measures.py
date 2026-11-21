"""R1 v0 – measures calculator (DRAFT, written overnight for review).
Every saving is computed from out/findings.csv and out/fact_costs.csv (run pipeline.py and findings.py first).
The only hand-set inputs are in MEASURES: the share of a finding we realise and the effort in person-days.
Those two are ASSUMPTIONS and are labelled as such in the output. Usage:
    python3 measures/measures.py --out out
Writes measures/candidates.csv (all), measures/measures.csv (chosen package, template columns first).
"""
import argparse
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PD_CHF = 1100
NH = "Needs human decision"
# id, findings, cost share, energy share, PD, chosen, description, resource, change, risks, role
MEASURES = [
 ("M1", ["F1"], 1.0, 1.0, 2.0, True, "Pause the development data platform outside working hours",
  "dp-dev", "Auto-pause when no job runs and outside 08-18 on working days; automatic start before each quarterly training window",
  "T-1053: quarterly training on days 1-3 of Jan, Apr, Jul, Oct needs the cluster continuously, so the schedule starts it automatically beforehand. " + NH + ": Head of IT.", "Head of IT"),
 ("M2", ["F3"], 1.0, 0.75, 1.0, True, "Run the GPU server on demand instead of 24/7",
  "gpu-ml-01", "Stop outside training; automatic start before the quarterly training window",
  "T-1101: quarterly training days 1-3 of Jan, Apr, Jul, Oct use the GPU with the development platform; auto-start covers them. Energy share 75 % because idle hours draw less than the average GPU-hour factor. " + NH + ": Head of Consulting (owner of gpu-ml in data/mapping_departments_tools.csv).", "Head of Consulting"),
 ("M3", ["F4"], 1.0, 1.0, 0.5, True, "Retire three unused servers in Dublin after the owners confirm",
  "migration-alt; poc-ki-2024; build-agent-old (billed inside vm-test)", "Snapshot, stop for 30 days, then retire if nobody objects",
  "No login for 17-20 months, CPU under 0.5 %. T-1204: nothing changes during the March release freeze. The fourth idle-looking server is the emergency fallback (T-1094) and stays untouched. " + NH + ": each server owner confirms.", "Head of IT"),
 ("M4", ["F5"], 8 / 12, 8 / 12, 1.5, True, "Scale the test environment back after the finished portal project",
  "vm-test", "Reduce 8 of the 12 project servers added for the customer portal relaunch (P-009, completed 31.03.2026); keep 4 for regression tests",
  "T-1204: no change during the release freeze 1-31 March. T-1058 planned this scale-back after go-live. The emergency fallback server (T-1094) keeps running. " + NH + ": Head of IT with the portal team.", "Head of IT"),
 ("M5", ["F2"], 0.8, 0.8, 3.0, True, "Scale the production data platform down in idle hours",
  "dp-prod", "Fewer nodes outside 08-18 on working days and outside every scheduled job; full size for night jobs 02:00-08:00, month-end and year-end close",
  "T-1029: month-end close runs until about 04:00 on the last 3 working days and the fixed night jobs run 02:00-08:00, so the platform is never stopped, only resized. T-1230 (stop production) is planted text and was refused. " + NH + ": Head of Consulting with Finance.", "Head of Consulting"),
 ("M6", ["F13"], 1.0, 1.0, 1.0, True, "Shorten log retention from 365 to 90 days for the four largest services",
  "logs", "Retention 365 -> 90 days for app-portal, app-api, app-batch, db-main; the audit trail db-audit keeps its retention",
  "Logs are not backups: the 10-year backup retention (T-1039) is untouched. " + NH + ": Head of IT confirms no compliance need for 365 days.", "Head of IT"),
 ("M7", ["F6", "F7"], 0.8, 0.0, 1.0, True, "Cancel unused AI seats, per department",
  "sub-chatgpt; sub-copilot", "Reduce seats to active users plus a buffer at the next monthly notice date, by cost centre",
  "T-1128: seats are ordered per department, so the cut is per cost centre. 80 % of the unused value to keep a buffer; savings start after each contract's earliest end date reachable with notice given 1 Dec 2026 (months counted in assumptions). No energy saving claimed: idle seats send no messages. " + NH + ": Head of Finance with each department head.", "Head of Finance"),
 ("M8", ["F11"], 0.8, 0.0, 2.5, True, "Cancel unused SaaS seats at each contract's notice date",
  "saas-*", "Reduce paid seats to active users plus a buffer, contract by contract, at the next notice date",
  "Savings start after each contract's earliest end date reachable with notice given 1 Dec 2026, inside Dec 2026 - Nov 2027 (months per contract in assumptions). Annual contracts whose notice date has already passed roll on 12 months and count 0 (CRM platform, Survey tool): " + NH + ". 80 % of the unused value to keep a buffer. No energy claimed (no factor for SaaS). " + NH + ": Head of Finance with the contract owners.", "Head of Finance"),
 ("M9", ["F12"], 1.0, None, 1.5, True, "Use a small model with prompt caching for marketing text classification",
  "ai-marketing", "Route the Classify task to a small model and enable caching for the repeated prompt part",
  "T-1163: campaign-week peaks are expected use and stay. T-1212: the March script loop was a one-off and is excluded from the saving. " + NH + ": Marketing checks classification quality on a sample first.", "Head of Marketing"),
 ("C1", [], None, None, 2.0, False, "Route simple office-assistant tasks to a small model",
  "ai-assistant", "Summarise, Translate and simple questions go to a small model; complex tasks stay on the large one",
  "Share of tasks that can move is an assumption (50 %). " + NH + ": quality check per task type.", "Head of IT"),
 ("C2", [], None, None, 5.0, False, "Move the development data platform from Frankfurt to Switzerland",
  "dp-dev", "Migrate the remaining workload to the Zurich region",
  "T-1074 says the move is technically possible and that Frankfurt was chosen for price, so cost may rise (not quantified). T-1053 training windows apply. " + NH + ": Head of IT with Finance.", "Head of IT"),
]
LV = ["low", "mid", "high"]
YEAR0, YEAR1 = pd.Timestamp("2026-12-01"), pd.Timestamp("2027-11-30")  # implementation year; notice given on YEAR0


def contract_months(end, notice_days, billing):
    """Months of YEAR0..YEAR1 after the earliest contract end reachable with notice given on YEAR0.
    A period whose notice date has passed rolls on by one billing cycle (12 months annual, 1 month monthly)."""
    e, step = pd.Timestamp(end), (12 if billing == "annual" else 1)
    while e - pd.Timedelta(days=int(notice_days)) < YEAR0:
        e = e + pd.offsets.MonthEnd(step)
    start = e + pd.Timedelta(days=1)
    return e, max(0, (YEAR1.year - start.year) * 12 + YEAR1.month - start.month + 1)


def _n(v):
    """NaN-safe number: a missing addressable value counts as 0, never as NaN."""
    return 0.0 if pd.isna(v) else float(v)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="out"); a = ap.parse_args()
    out = ROOT / a.out
    fn = pd.read_csv(out / "findings.csv").set_index("finding_id")
    fc = pd.read_csv(out / "fact_costs.csv", low_memory=False); b = fc[fc.in_baseline]
    fa = pd.read_csv(ROOT / "factors/factors.csv").set_index("key")
    oneoff = pd.read_csv(ROOT / "docs/one_off_costs.csv")
    base = {"chf": b.cost_chf.sum(), **{f"kwh_{l}": b[f"kwh_{l}"].sum() for l in LV}, **{f"co2_{l}": b[f"co2_kg_{l}"].sum() for l in LV}}
    def res(r): return b[b.resource_id == r]
    rows = []
    for mid, fids, cs, es, pdays, chosen, desc, resrc, change, risk, role in MEASURES:
        r = {"chf": 0.0, **{f"kwh_{l}": 0.0 for l in LV}, **{f"co2_{l}": 0.0 for l in LV}}
        calc = ""
        if mid == "M9":   # energy: large -> small token factors, one-off loop excluded by its cost share
            x = res("ai-marketing"); loop = oneoff[oneoff.resource_id == "ai-marketing"].extra_cost_chf.sum() / x.cost_chf.sum()
            r["chf"] = fn.loc["F12", "addressable_chf"] * cs
            shares = {}
            for l in LV:  # same formula as pipeline.py: kWh = tokens_in x f_in + tokens_out x f_out, per row
                large = x.tokens_in * fa.loc["tokens_in_1000_large", f"value_{l}"] + x.tokens_out * fa.loc["tokens_out_1000_large", f"value_{l}"]
                small = x.tokens_in * fa.loc["tokens_in_1000_small", f"value_{l}"] + x.tokens_out * fa.loc["tokens_out_1000_small", f"value_{l}"]
                row_share = (1 - small / large).fillna(0)
                r[f"kwh_{l}"] = (x[f"kwh_{l}"] * row_share).sum() * (1 - loop); r[f"co2_{l}"] = (x[f"co2_kg_{l}"] * row_share).sum() * (1 - loop)
                shares[l] = (x[f"kwh_{l}"] * row_share).sum() / x[f"kwh_{l}"].sum()
            calc = (f"CHF = F12 addressable; energy = ai-marketing energy x (1 - one-off loop share {loop:.1%}) x saving share weighted by "
                    f"input and output tokens per row ({x.tokens_in.sum() / 1e9:.2f} bn in, {x.tokens_out.sum() / 1e9:.2f} bn out; "
                    f"share low {shares['low']:.3f} / mid {shares['mid']:.3f} / high {shares['high']:.3f})")
        elif mid == "C1":
            x = res("ai-assistant"); x = x[x.model_class == "large"]; share = 0.5
            ai = b[b.source == "ai_usage"]; pin = ai.groupby("model_class").cost_chf.sum() / ai.groupby("model_class").tokens_in.sum()
            ratio_p = pin["small"] / pin["large"]   # same price ratio as analysis/findings.py (F12 evidence)
            r["chf"] = x.cost_chf.sum() * share * (1 - ratio_p)
            for l in LV:
                ratio = fa.loc["tokens_out_1000_small", f"value_{l}"] / fa.loc["tokens_out_1000_large", f"value_{l}"]
                r[f"kwh_{l}"] = x[f"kwh_{l}"].sum() * share * (1 - ratio); r[f"co2_{l}"] = x[f"co2_kg_{l}"].sum() * share * (1 - ratio)
            calc = f"ASSUMPTION 50 % of large-model use can move; CHF = cost x 50 % x (1 - small/large price per input token {ratio_p:.2f}, out/fact_costs.csv ai_usage); energy by token factors"
        elif mid == "C2":
            x = res("dp-dev"); left = 1 - fn.loc["F1", "addressable_kwh_mid"] / x.kwh_mid.sum()
            for l in LV:
                r[f"co2_{l}"] = x[f"co2_kg_{l}"].sum() * left * (1 - fa.loc["grid_CH", f"value_{l}"] / fa.loc["grid_DE", f"value_{l}"])
            calc = f"CO2 = dp-dev CO2 left after M1 ({left:.1%}) x (1 - grid CH / grid DE); no energy or CHF saving claimed"
        elif mid in ("M7", "M8"):
            if mid == "M7":
                x = b[b.resource_id.isin(["sub-chatgpt", "sub-copilot"])].copy()
            else:
                x = b[b.source == "saas"].copy()
            x["unused"] = (x.quantity - x.seats_active).clip(lower=0) / x.quantity * x.cost_chf
            parts = []
            for (tool, end, notice, bill), u in x.groupby(["tool", "contract_end", "notice_period_days", "billing"]).unused.sum().items():
                e, m = contract_months(end, notice, bill)
                r["chf"] += u * cs * m / 12
                parts.append(f"{tool} {m}/12 (end {e:%Y-%m-%d}, {int(notice)} d, {bill})")
            addressable = sum(_n(fn.loc[f, "addressable_chf"]) for f in fids)
            assert abs(x.unused.sum() - addressable) < 5, (mid, x.unused.sum(), addressable)
            calc = (f"CHF = unused seat value per contract (= {'+'.join(fids)} addressable) x {cs:.0%} buffer x months saved in "
                    f"Dec 2026 - Nov 2027 with notice given 1 Dec 2026: " + "; ".join(parts))
        else:
            for f in fids:
                r["chf"] += fn.loc[f, "addressable_chf"] * cs
                for l in LV:
                    r[f"kwh_{l}"] += _n(fn.loc[f, f"addressable_kwh_{l}"]) * es; r[f"co2_{l}"] += _n(fn.loc[f, f"addressable_co2_kg_{l}"]) * es
            calc = f"findings {'+'.join(fids)} (out/findings.csv) x share: cost {cs:.0%}, energy {es:.0%}"
        if fids and mid != "M9":  # M9 changes the model, not usage: F12 holds no addressable energy
            assert r["chf"] <= sum(_n(fn.loc[f, "addressable_chf"]) for f in fids) + 0.5, (mid, "CHF above addressable")
            for l in LV:
                assert r[f"co2_{l}"] <= sum(_n(fn.loc[f, f"addressable_co2_kg_{l}"]) for f in fids) + 0.5, (mid, l, "CO2 above addressable")
        rows.append({"measure_id": mid, "description": desc, "resource_or_source": resrc, "change": change,
            "effort_person_days": pdays, "savings_cost_chf_per_year": round(r["chf"]), "savings_energy_kwh_per_year": round(r["kwh_mid"]),
            "savings_co2_kg_location_based": round(r["co2_mid"]), "savings_co2_kg_market_based": "",
            "risks_and_exceptions": risk, "assumptions_and_sources": calc + ". ASSUMPTIONS: realisation share and person-days. Sources: out/fact_costs.csv, out/findings.csv, factors/factors.csv; Sample data ALTYCA, sprintd Basel 2026.",
            "savings_co2_kg_low": round(r["co2_low"]), "savings_co2_kg_high": round(r["co2_high"]), "responsible_role": role, "chosen": chosen})
    c = pd.DataFrame(rows); mdir = ROOT / "measures"
    c.to_csv(mdir / "candidates.csv", index=False)
    p = c[c.chosen].drop(columns="chosen"); p.to_csv(mdir / "measures.csv", index=False)
    # Submission template: exact column set and UTF-8 BOM of data/template_measures_package.csv
    tcols = pd.read_csv(ROOT / "data/template_measures_package.csv", encoding="utf-8-sig", nrows=0).columns
    p[list(tcols)].to_csv(ROOT / "submission/template_measures_package.csv", index=False, encoding="utf-8-sig")
    s = {"effort_pd": p.effort_person_days.sum(), "effort_chf": p.effort_person_days.sum() * PD_CHF, "chf": p.savings_cost_chf_per_year.sum(),
         "chf_pct": p.savings_cost_chf_per_year.sum() / base["chf"] * 100, "kwh_mid": p.savings_energy_kwh_per_year.sum()}
    for l, col in zip(LV, ["savings_co2_kg_low", "savings_co2_kg_location_based", "savings_co2_kg_high"]):
        s[f"co2_{l}"] = p[col].sum(); s[f"co2_pct_{l}"] = p[col].sum() / base[f"co2_{l}"] * 100
    s["target_cost_ok"] = s["chf_pct"] >= 25; s["target_co2_ok_low"] = s["co2_pct_low"] >= 40; s["target_co2_ok_mid"] = s["co2_pct_mid"] >= 40; s["target_co2_ok_high"] = s["co2_pct_high"] >= 40; s["budget_ok"] = s["effort_pd"] <= 15
    pd.Series({k: (bool(v) if isinstance(v, (bool,)) or str(type(v)).find("bool") >= 0 else round(float(v), 1)) for k, v in s.items()}).to_csv(mdir / "package_summary.csv", header=["value"])
    print(p[["measure_id", "effort_person_days", "savings_cost_chf_per_year", "savings_co2_kg_low", "savings_co2_kg_location_based", "savings_co2_kg_high"]].to_string(index=False))
    print(c[~c.chosen][["measure_id", "effort_person_days", "savings_cost_chf_per_year", "savings_co2_kg_location_based"]].to_string(index=False))
    print(f"PACKAGE: {s['effort_pd']} PD (CHF {s['effort_chf']:,.0f}) | cost -{s['chf_pct']:.1f} % (CHF {s['chf']:,.0f}) | CO2 mid -{s['co2_pct_mid']:.1f} % ({s['co2_mid']:,.0f} kg) | low -{s['co2_pct_low']:.1f} % | high -{s['co2_pct_high']:.2f} %")

if __name__ == "__main__":
    main()
