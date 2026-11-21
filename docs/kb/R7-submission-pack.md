# R7 – Submission pack index

- **Task:** G7, for Rashed’s draft submission (Sat 21 Nov 15:00) · **Author:** Grok · **Date:** 21.11.2026 · **Status:** draft
- **Sources:** `out/fact_costs.csv` (baseline rows), `out/findings.csv`, `measures/measures.csv`, `measures/package_summary.csv`, `analysis/kb/reconciliation_checks.csv`, `factors/factors.csv` (factor rows only). Sample data ALTYCA, sprintd Basel 2026.
- Checked line by line on 21.11.2026 after `pipeline.py`, `analysis/findings.py` and `measures/measures.py`. Package choices in `measures/measures.py` were not changed. Nothing here switches off dp-prod, st-backup, dr-failover or pbi-07.

## Files to submit

| What | Path | State |
| --- | --- | --- |
| Baseline and assumptions table | `submission/template_baseline_and_assumptions.csv` | Draft. Totals match `out/`. Factor rows match `factors/factors.csv`. Two bonus totals left blank. |
| Measures package table | `submission/template_measures_package.csv` | Draft. M1–M9 match `measures/measures.csv`. Market-based CO2 column blank. |
| Needs-a-human list | `docs/kb/R4-needs-a-human.md` | Draft. Figures below match `out/` and `measures/`. |
| Demo script | `docs/kb/R6-demo-script.md` | Draft, rehearsed 21.11 against the running app. |
| Backup screenshots | `docs/kb/screenshots/overall-picture.png`, `findings.png`, `package.png`, `needs-a-human.png`, `ask.png`, `next-year.png` | From `scripts/screenshots.py`. Not regenerated in G7: the pages did not change. |
| Path to operation | `submission/path_to_operation.md` | Draft v0 (02:30). Required by the case (R8). Still for Rashed to finish. |

The app is `app/app.py`, offline: `python3 -m streamlit run app/app.py`.

## What the check found

No cell in the two tables was rewritten. No sentence in `docs/kb/R4-needs-a-human.md` was rewritten. The numbers already on those pages match the files they cite.

**Baseline totals** are the baseline rows of `out/fact_costs.csv` (`in_baseline`), shown to 1 decimal where the table does that:

| Cell | In the table | Sum in `out/` |
| --- | ---: | ---: |
| Cost, CHF | 470,288.93 | 470,288.93 |
| Energy kWh low / mid / high | 19,365.9 / 35,782.8 / 69,223.9 | 19,365.91296 / 35,782.750878 / 69,223.942809 |
| CO2 kg low / mid / high | 2,899.1 / 6,197.5 / 15,379.6 | 2,899.092562 / 6,197.480804 / 15,379.630045 |

`out/template_baseline_and_assumptions_prefilled.csv` rounds the same sums to whole numbers (cost 470,289, energy 19,366 / 35,783 / 69,224, CO2 2,899 / 6,197 / 15,380). The submission table keeps the tighter rounding and says so in the calculation column.

**Left blank because they are not in `out/`:** `total_co2_market_based_baseline_year_kg`, `growth_per_year`, `saas_licence_month`, and `savings_co2_kg_market_based` on every measure. Do not fill these for the draft unless a new pipeline run writes them.

**Factor rows** (grid CH/DE/IE/EU, market-based grid, vCPU, node, GPU, storage, tokens, subscription message, PUE, capacity-day, runner-minute, GB transferred) match `factors/factors.csv` low / mid / high. They are not a second total in `out/`. The prefilled template leaves them empty on purpose; the submission table copies the factor file.

**Measures M1–M9:** effort, CHF, kWh, location-based CO2, description, change and risks match `measures/measures.csv`. Low/high CO2 quoted in the assumptions text matches `savings_co2_kg_low` / `savings_co2_kg_high` on the same file. Package from `measures/package_summary.csv`: 14.0 PD, CHF 15,400, CHF 133,427 (−28.4 %), 12,423 kWh, CO2 mid 2,614 kg (−42.2 %), low −49.0 %, high −40.0 %.

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
| Without M5: cost −22.2 %, CO2 −36.1 % | ticked rows in `measures/candidates.csv` except M5, over the baseline | 22.18 % and 36.08 %, which round to those figures |

## What Rashed still decides before 15:00

1. **Own AI energy.** Still blocked. The card stays without a kilogram. Input needed: for each of Rashed, Hakim, Vinzenz and Grok, input-token count and output-token count per model, with the model marked large or small; or a measured kWh figure naming the meter or provider export. That input has to land in `out/` (Grok cannot edit `pipeline/` or `factors/`). Until then, `submission/path_to_operation.md` says «The tool reports its own energy use», and there is no figure to show.
2. **C1.** Still open. On high factors the chosen package is −40.0 % with no margin. R4 records the decision for after Vinzenz’s idle-power factors. Do not tick C1 in the demo unless that decision is made. `measures/measures.py` was not changed.
3. **M5 stays in the package.** Already decided 21.11 10:10. Dropping it misses both targets (cost −22.2 %, CO2 −36.1 %). Sign-off is still Head of Consulting with Finance. The measure resizes dp-prod in idle hours. It does not switch dp-prod off. st-backup, dr-failover and pbi-07 stay on.
4. **Leave the blanks blank** for the draft: market-based company CO2, company growth percent, SaaS licence energy, market-based CO2 on each measure. They are not in `out/`.
5. **One-off route**, only if a juror asks: `docs/one_off_costs.csv` (CHF 3,308 and CHF 364) or the reconciliation excess (CHF 3,309.99 and CHF 357.55). Neither is a recurring saving.
6. **Read `submission/path_to_operation.md` once.** It is still the 02:30 draft. The own-energy sentence is the line that does not yet have a number.
7. **One rehearsal** with `docs/kb/R6-demo-script.md`. Paste the T-1251 line. After High factors, click Mid factors before leaving Package, because the kilogram line changes to 6,159 kg. If the app fails, use the six PNGs and say only numbers that are on them.
