# Template row edits for Rashed (submission/)

- **Task:** "Vinzenz sends template row edits" (status page, by 13:30) · **Author:** Vinzenz (with Claude) · **Date:** 21.11.2026 · **Status:** final for Rashed
- **Checked:** `submission/template_baseline_and_assumptions.csv` and `submission/factors_extra.csv` (main @ dd42743) against `factors/factors.csv`, by script.
- **Rows ready to paste:** [`template-row-edits.csv`](template-row-edits.csv). It has one column naming the target file, and otherwise the same columns as the submission files. `submission/` is Rashed's folder, so I changed nothing there.

## Check result
- **Template:** all 11 factor rows match `factors.csv` exactly (values, source, calculation). The UTF-8 BOM is present.
- **factors_extra.csv:** all 9 rows match. The only difference is `saas_licence_month`, where your calculation text is clearer than ours, so keep it.
- **Units:** I withdraw my earlier suggestion. The official template (`data/template_baseline_and_assumptions.csv`) itself says "kWh" for the six energy rows, so keep the template exact.

## Edits (4 rows)
1. **Template, `total_co2_market_based_baseline_year_kg` (Bonus, now blank): 213.0 / 1,932.3 / 19,659.6 kg.**
   Calculation: baseline kWh × the energy-weighted `grid_market_based` at the same level.
   The high (19.7 t) is above the location-based high (15.4 t) because residual mixes exclude certified green power. The Germany residual mix is 0.725.
   This is correct for "nothing proven", but say so if the row is shown. Location-based stays the official number.
   The low (213 kg) accepts the hoster's guarantees of origin (T-1030/1181/1203/1227) before anyone has seen the certificates, so it is a claim, not proof.
   The comparison mixes AIB residual mixes (direct CO2 only) with life-cycle location factors. On a life-cycle basis the market high would be higher still.
   If you prefer, leave the row blank, as now.
2. **factors_extra, `node_hour_idle`: 0.020 / 0.030 / 0.042 kWh per idle node hour.** Labelled "sensitivity only" (decision 12:15).
3. **factors_extra, `gpu_hour_idle`: 0.10 / 0.12 / 0.18 kWh per idle GPU hour.** Labelled "sensitivity only".
4. **factors_extra, `cache_read_share`: 0.05 / 0.10 / 1.0.** Labelled "only for the own-AI footprint (V6)".

`growth_per_year` stays blank, as stated (T-1261 is after the baseline).
