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
  "T-1101: quarterly training days 1-3 of Jan, Apr, Jul, Oct use the GPU with the development platform; auto-start covers them. Energy share 75 % because idle hours draw less than the average GPU-hour factor. " + NH + ": owner of the AI pilot.", "Head of Consulting"),
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
  "T-1128: seats are ordered per department, so the cut is per cost centre. 30-day notice, monthly billing. 80 % of the unused value to keep a buffer. No energy saving claimed: idle seats send no messages. " + NH + ": each department head.", "Head of Finance (with each department head)"),
 ("M8", ["F11"], 0.6, 0.0, 2.5, True, "Cancel unused SaaS seats at each contract's notice date",
  "saas-*", "Reduce paid seats to active users plus a buffer, contract by contract, at the next notice date",
  "Per contract (measures/m8_contracts.csv): notice given 1 Dec 2026; monthly-billed contracts save from 1 Dec + notice period, annual ones from the first contract end whose notice date is still open, otherwise one year later (CRM platform and Survey tool are locked until 2028). Counted: 90 % of the unused seat value (10 % buffer) for the months inside Dec 2026 - Nov 2027; the full run-rate is higher once every contract has renewed. No energy claimed (no factor for SaaS). " + NH + ": contract owners.", "Head of Finance (with contract owners)"),
 ("M9", ["F12"], 1.0, None, 1.5, False, "Use a small model with prompt caching for marketing text classification",
  "ai-marketing", "Route the Classify task to a small model and enable caching for the repeated prompt part",
  "T-1163: campaign-week peaks are expected use and stay. T-1212: the March script loop was a one-off and is excluded from the saving. " + NH + ": Marketing checks classification quality on a sample first.", "Head of Marketing"),
 ("C1", [], None, None, 2.0, True, "Route simple office-assistant tasks to a small model",
  "ai-assistant", "Summarise, Translate and simple questions go to a small model; complex tasks stay on the large one",
  "Share of tasks that can move is an assumption (50 %). " + NH + ": quality check per task type.", "Head of IT"),
 ("C2", [], None, None, 5.0, False, "Move the development data platform from Frankfurt to Switzerland",
  "dp-dev", "Migrate the remaining workload to the Zurich region",
  "T-1074 says the move is technically possible and that Frankfurt was chosen for price, so cost may rise (not quantified). T-1053 training windows apply. " + NH + ": Head of IT with Finance.", "Head of IT"),
]
LV = ["low", "mid", "high"]


def token_saving_share(rows, fa, level):
    """Share of AI energy saved by moving these rows from the large to the small model, weighted by input AND output tokens."""
    tin, tout = rows.tokens_in.sum(), rows.tokens_out.sum()
    big = tin * fa.loc["tokens_in_1000_large", f"value_{level}"] + tout * fa.loc["tokens_out_1000_large", f"value_{level}"]
    small = tin * fa.loc["tokens_in_1000_small", f"value_{level}"] + tout * fa.loc["tokens_out_1000_small", f"value_{level}"]
    return 1 - small / big if big else 0.0


def price_ratio_small_large(rows):
    """CHF per token of the small model divided by the large model, from the same resource's own rows."""
    g = rows.groupby("model_class")[["cost_chf", "tokens_in", "tokens_out"]].sum()
    per = g.cost_chf / (g.tokens_in + g.tokens_out)
    return float(per["small"] / per["large"])

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
            for l in LV:
                sh = token_saving_share(x, fa, l)
                r[f"kwh_{l}"] = x[f"kwh_{l}"].sum() * (1 - loop) * sh; r[f"co2_{l}"] = x[f"co2_kg_{l}"].sum() * (1 - loop) * sh
            calc = f"CHF = F12 addressable; energy = ai-marketing energy x (1 - one-off loop share {loop:.1%}) x token-weighted saving share (input and output tokens, large -> small factors)"
        elif mid == "M8":
            sa = b[b.source == "saas"].copy()
            sa["idle"] = (sa.quantity - sa.seats_active).clip(lower=0) / sa.quantity * sa.cost_chf
            g = sa.groupby(["tool", "contract_end", "notice_period_days", "billing"], dropna=False).idle.sum().reset_index()
            w0, w1 = pd.Timestamp("2026-12-01"), pd.Timestamp("2027-11-30")
            def effective(row):
                if row.billing == "monthly":
                    return w0 + pd.Timedelta(days=row.notice_period_days)
                end = pd.Timestamp(row.contract_end)
                while end - pd.Timedelta(days=row.notice_period_days) < w0:
                    end = end + pd.DateOffset(years=1)
                return end + pd.Timedelta(days=1)
            g["saves_from"] = g.apply(effective, axis=1).dt.date
            g["share_of_contract_year"] = (((w1 - pd.to_datetime(g.saves_from)).dt.days + 1).clip(lower=0) / 365).round(3)
            g["saving_chf_contract_year"] = (g.idle * 0.9 * g.share_of_contract_year).round(0)
            g.assign(idle=g.idle.round(0)).rename(columns={"idle": "unused_chf_baseline_year"}).to_csv(ROOT / "measures" / "m8_contracts.csv", index=False)
            r["chf"] = g.saving_chf_contract_year.sum()
            calc = (f"Per contract from out/fact_costs.csv saas rows: unused = (seats bought - active) / bought x cost; saving = 90 % of unused "
                    f"x share of Dec 2026 - Nov 2027 after the notice date (measures/m8_contracts.csv). Run-rate once all renewed: "
                    f"CHF {g.idle.sum() * 0.9:,.0f} a year")
        elif mid == "C1":
            allr = res("ai-assistant"); x = allr[allr.model_class == "large"]; share = 0.5
            ratio_p = price_ratio_small_large(allr)
            r["chf"] = x.cost_chf.sum() * share * (1 - ratio_p)
            for l in LV:
                sh = token_saving_share(x, fa, l)
                r[f"kwh_{l}"] = x[f"kwh_{l}"].sum() * share * sh; r[f"co2_{l}"] = x[f"co2_kg_{l}"].sum() * share * sh
            calc = (f"ASSUMPTION 50 % of large-model use (Summarise, Translate, simple questions) can move; "
                    f"CHF = large-model cost x 50 % x (1 - small/large price per token {ratio_p:.2f}, from ai-assistant rows); "
                    "energy = token-weighted saving share (input and output tokens)")
        elif mid == "C2":
            x = res("dp-dev"); left = 1 - fn.loc["F1", "addressable_kwh_mid"] / x.kwh_mid.sum()
            for l in LV:
                r[f"co2_{l}"] = x[f"co2_kg_{l}"].sum() * left * (1 - fa.loc["grid_CH", f"value_{l}"] / fa.loc["grid_DE", f"value_{l}"])
            calc = f"CO2 = dp-dev CO2 left after M1 ({left:.1%}) x (1 - grid CH / grid DE); no energy or CHF saving claimed"
        else:
            for f in fids:
                r["chf"] += fn.loc[f, "addressable_chf"] * cs
                for l in LV:
                    r[f"kwh_{l}"] += (fn.loc[f, f"addressable_kwh_{l}"] or 0) * es; r[f"co2_{l}"] += (fn.loc[f, f"addressable_co2_kg_{l}"] or 0) * es
            calc = f"findings {'+'.join(fids)} (out/findings.csv) x share: cost {cs:.0%}, energy {es:.0%}"
        rows.append({"measure_id": mid, "description": desc, "resource_or_source": resrc, "change": change,
            "effort_person_days": pdays, "savings_cost_chf_per_year": round(r["chf"]), "savings_energy_kwh_per_year": round(r["kwh_mid"]),
            "savings_co2_kg_location_based": round(r["co2_mid"]), "savings_co2_kg_market_based": "",
            "risks_and_exceptions": risk, "assumptions_and_sources": calc + ". ASSUMPTIONS: realisation share and person-days. Sources: out/fact_costs.csv, out/findings.csv, factors/factors.csv; Sample data ALTYCA, sprintd Basel 2026.",
            "savings_co2_kg_low": round(r["co2_low"]), "savings_co2_kg_high": round(r["co2_high"]), "responsible_role": role, "chosen": chosen})
    c = pd.DataFrame(rows); mdir = ROOT / "measures"
    c.to_csv(mdir / "candidates.csv", index=False)
    p = c[c.chosen].drop(columns="chosen"); p.to_csv(mdir / "measures.csv", index=False)
    s = {"effort_pd": p.effort_person_days.sum(), "effort_chf": p.effort_person_days.sum() * PD_CHF, "chf": p.savings_cost_chf_per_year.sum(),
         "chf_pct": p.savings_cost_chf_per_year.sum() / base["chf"] * 100, "kwh_mid": p.savings_energy_kwh_per_year.sum()}
    for l, col in zip(LV, ["savings_co2_kg_low", "savings_co2_kg_location_based", "savings_co2_kg_high"]):
        s[f"co2_{l}"] = p[col].sum(); s[f"co2_pct_{l}"] = p[col].sum() / base[f"co2_{l}"] * 100
    s["target_cost_ok"] = s["chf_pct"] >= 25; s["target_co2_ok_mid"] = s["co2_pct_mid"] >= 40; s["budget_ok"] = s["effort_pd"] <= 15
    pd.Series({k: (bool(v) if isinstance(v, (bool,)) or str(type(v)).find("bool") >= 0 else round(float(v), 1)) for k, v in s.items()}).to_csv(mdir / "package_summary.csv", header=["value"])
    print(p[["measure_id", "effort_person_days", "savings_cost_chf_per_year", "savings_co2_kg_low", "savings_co2_kg_location_based", "savings_co2_kg_high"]].to_string(index=False))
    print(c[~c.chosen][["measure_id", "effort_person_days", "savings_cost_chf_per_year", "savings_co2_kg_location_based"]].to_string(index=False))
    print(f"PACKAGE: {s['effort_pd']} PD (CHF {s['effort_chf']:,.0f}) | cost -{s['chf_pct']:.1f} % (CHF {s['chf']:,.0f}) | CO2 mid -{s['co2_pct_mid']:.1f} % ({s['co2_mid']:,.0f} kg) | low -{s['co2_pct_low']:.1f} % | high -{s['co2_pct_high']:.1f} %")

if __name__ == "__main__":
    main()
