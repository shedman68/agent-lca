# Factor rows in the submission template – check

- **Task:** plan item 4 (check Grok's factor rows, PR #29) · **Author:** Vinzenz (with Claude) · **Date:** 21.11.2026 · **Status:** done, for the 12:30 session with Rashed
- **Checked:** `submission/template_baseline_and_assumptions.csv` (main @ 079bc11) against `factors/factors.csv`, by script (exact match of low/mid/high, source, calculation)

## Result
- **21 factor rows: all low / mid / high values, sources and calculations match `factors.csv` exactly.**
  Every row has a range, a source with a date, and a calculation.
- The only difference is `saas_licence_month`. Its calculation text in the template is clearer than ours ("excluded until a factor is sourced, no number invented"). Keep the template text.

## For Rashed (submission/ is your folder; I changed nothing there)
1. **Units:** six Must rows say only "kWh": vCPU-hour, node-hour, GPU-hour, storage GB-day, 1,000 tokens, subscription message.
   Write the unit in full ("kWh per vCPU hour", …) unless the official template fixes the unit text.
2. **Idle factors** `node_hour_idle` and `gpu_hour_idle` (PR #37) are not in the template.
   Add them as two rows only if the package uses them (your decision on idle counting).
3. **total_co2_market_based_baseline_year_kg is blank.** You could fill it from the factors: total kWh × `grid_market_based`.
   That gives 213 / **1,932** / 19,660 kg (19,366 × 0.011, 35,783 × 0.054, 69,224 × 0.284). Label it "derived from the energy-weighted market factor, bonus".
   The high value pairs the highest energy with the residual mix, so it is very wide. Otherwise, keep it blank and say so, as now.
4. `growth_per_year` blank: fine as stated (T-1261 is after the baseline).
