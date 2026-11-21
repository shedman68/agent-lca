# R7 – Submission pack index

- **Task:** G7, for Rashed’s draft submission (Sat 21 Nov 15:00) · **Author:** Grok · **Date:** 21.11.2026 · **Status:** draft
- **Sources:** `out/fact_costs.csv` (baseline rows), `out/findings.csv`, `measures/measures.csv`, `measures/package_summary.csv`, `analysis/kb/reconciliation_checks.csv`, `factors/factors.csv` (factor rows only). Sample data ALTYCA, sprintd Basel 2026.
- Checked line by line on 21.11.2026 after `pipeline.py`, `analysis/findings.py` and `measures/measures.py`. Package choices in `measures/measures.py` were not changed. Nothing here switches off dp-prod, st-backup, dr-failover or pbi-07.

## Files to submit

| What | Path | State |
| --- | --- | --- |
| Baseline and assumptions table | `submission/template_baseline_and_assumptions.csv` | Draft. Location-based totals match `out/`. Factor rows match `factors/factors.csv`. Empty cells filled by `submission/build_templates.py`: cost low/high and growth are n/a; market-based company CO2 is the bonus product of baseline kWh and `grid_market_based`. |
| Measures package table | `submission/template_measures_package.csv` | Draft. Regenerated from `measures/measures.csv`: M1–M8 and C1. Market-based CO2 column blank. |
| Needs-a-human list | `docs/kb/R4-needs-a-human.md` | Draft. Figures below match `out/` and `measures/`. |
| Demo script | `docs/kb/R6-demo-script.md` | Draft, rehearsed 21.11 against the running app. |
| Backup screenshots | `docs/kb/screenshots/overall-picture.png`, `findings.png`, `package.png`, `needs-a-human.png`, `ask.png`, `next-year.png` | From `scripts/screenshots.py`. Not regenerated in G7: the pages did not change. |
| Path to operation | `submission/path_to_operation.md` | Draft v0 (02:30). Required by the case (R8). Still for Rashed to finish. |

The app is `app/app.py`, offline: `python3 -m streamlit run app/app.py`.

## What the check found

After the rebase onto main the measures table was regenerated. It had still listed M1–M9. The package in `measures/measures.csv` is M1–M8 and C1. Two sentences in `docs/kb/R4-needs-a-human.md` were updated for that package: the without-M5 percents, and C1, which is now in the package. The other R4 figures below were checked against `out/` before this rebase; the baseline total was checked again (`verify_baseline.py` prints MATCH).

**Baseline totals** are the baseline rows of `out/fact_costs.csv` (`in_baseline`), shown to 1 decimal where the table does that:

| Cell | In the table | Sum in `out/` |
| --- | ---: | ---: |
| Cost, CHF | 470,288.93 | 470,288.93 |
| Energy kWh low / mid / high | 19,365.9 / 35,782.8 / 69,223.9 | 19,365.91296 / 35,782.750878 / 69,223.942809 |
| CO2 kg low / mid / high | 2,899.1 / 6,197.5 / 15,379.6 | 2,899.092562 / 6,197.480804 / 15,379.630045 |

`out/template_baseline_and_assumptions_prefilled.csv` rounds the same sums to whole numbers (cost 470,289, energy 19,366 / 35,783 / 69,224, CO2 2,899 / 6,197 / 15,380). The submission table keeps the tighter rounding and says so in the calculation column.

**Filled or marked n/a.** `total_cost_baseline_year_chf` low and high are n/a: the cost is one reconciled total. `growth_per_year` is n/a in every value and in source: `out/` has no company-wide growth rate, and T-1261 is not used as one. `allocation_rule_shared_costs` low and high are n/a because the rule is one text; the source is `pipeline/pipeline.py` plus the mapping file and `headcount.csv`. `total_co2_market_based_baseline_year_kg` is a bonus product, not a pipeline total: baseline kWh 19,365.91296 / 35,782.750878 / 69,223.942809 times `grid_market_based` 0.011 / 0.054 / 0.284 = 213.0 / 1,932.3 / 19,659.6 kg. PR #45 describes that product and was still open, so the script calculated it from `out/` and `factors/factors.csv`. `savings_co2_kg_market_based` stays blank on every measure, with that note in `assumptions_and_sources`. `saas_licence_month` stays empty in `submission/factors_extra.csv` because `factors/factors.csv` has no value.

**Factor rows** (grid CH/DE/IE/EU, market-based grid, vCPU, node, GPU, storage, tokens, subscription message, PUE, capacity-day, runner-minute, GB transferred) match `factors/factors.csv` low / mid / high. They are not a second total in `out/`. The prefilled template leaves them empty on purpose; the submission table copies the factor file.

**Measures M1–M8 and C1:** effort, CHF, kWh, location-based CO2, description, change and risks are copied by `submission/build_templates.py` from `measures/measures.csv`. M9 is not in that file. Package from `measures/package_summary.csv`: 14.5 PD, CHF 15,950, CHF 134,306 (−28.6 %), 12,603 kWh, CO2 mid 2,664 kg (−43.0 %), low −49.6 %, high −42.2 %.

**R4 list**, each figure against its file:

| Claim in R4 | File | Result |
| --- | --- | --- |
| Baseline CHF 470,288.93 | `reconciliation_checks.csv`, «BASELINE TOTAL» and «baseline is not ~40 % lower» | same |
| Hoster CHF 19,009.04 | same file, «hoster: total» | same |
| db-fin CHF 11,933.84 | same file, «db-fin costs are not zero» | same, 364 baseline rows |
| Invoices CHF 41,764.67 vs gateway CHF 39,444.06, gap CHF 2,320.61 | same file, «AI gateway vs provider invoices, all providers» | same |
| Report CHF 285,820.00 vs Azure+AWS+hoster CHF 280,919.23, gap CHF 4,900.77 | same file, «provider_monthly_report vs azure+aws+hoster» | same |
| AWS Zurich: 727 rows, CHF 20,723.64, 1,487 kWh, 133.8 kg | `out/fact_costs.csv` via `data.aws_zurich()` | 727 rows, 20,723.64 CHF, 1,487.16 kWh, 133.84 kg |
| Sandbox rows CHF 2.11 | same reconciliation file, «exclude test account» | independent 2.11 |
| P2 dr-failover CHF 1,542.7 inside vm-test | `out/findings.csv` | 1,542.70 |
| T-1212 extra CHF 3,308 and CHF 3,309.99 | `docs/one_off_costs.csv` 3,308; reconciliation pipeline 3,309.99 | both stated, not a saving |
| T-1189 extra CHF 364 and CHF 357.55 | `docs/one_off_costs.csv` 364; reconciliation pipeline 357.55 | both stated, not a saving |
| E-signature unused CHF 5,675; Project scheduling unused CHF 3,203.89 | notice calendar on `out/fact_costs.csv` | 5,675.00 and 3,203.886 |
| Without M5: cost −22.4 %, CO2 −36.9 % | `measures/package_summary.csv` minus the M5 row in `measures/measures.csv`, over the baseline | CHF 105,179 is 22.4 % of 470,288.93; 2,286 kg is 36.9 % of 6,197.5 kg |

## What Rashed still decides before 15:00

1. **Own AI energy is partial.** `factors/kb/V6-our-ai-footprint.md` is in the repo and the Next year card shows it. The mid total there is Vinzenz and Hakim only (2.6 kWh, 0.71 kg). Rashed and Grok are missing. Do not invent their tokens. `submission/path_to_operation.md` still says «The tool reports its own energy use» and has no team total.
2. **C1 is in the package.** High factors are −42.2 % (`co2_pct_high` 42.2). The quality check per task type is still Head of IT. Do not tick C2 in the demo.
3. **M5 stays in the package.** Already decided 21.11 10:10. Dropping it misses both targets (cost −22.4 %, CO2 −36.9 %). Sign-off is still Head of Consulting with Finance. The measure resizes dp-prod in idle hours. It does not switch dp-prod off. st-backup, dr-failover and pbi-07 stay on.
4. **Market-based measure CO2 stays blank.** The company market-based row is the bonus product above, not an official baseline. Company growth is n/a. SaaS licence energy stays empty.
5. **One-off route**, only if a juror asks: `docs/one_off_costs.csv` (CHF 3,308 and CHF 364) or the reconciliation excess (CHF 3,309.99 and CHF 357.55). Neither is a recurring saving.
6. **Read `submission/path_to_operation.md` once.** It is still the 02:30 draft.
7. **One rehearsal** with `docs/kb/R6-demo-script.md`. Paste the T-1251 line. After High factors, click Mid factors before leaving Package, because the kilogram line changes to 6,496 kg. The screenshots in `docs/kb/screenshots/` are from before this package. If the app fails, say the numbers in this file and in `measures/package_summary.csv`, not a number that is only on an old PNG.
