# R0 – Data cleaning, verified baseline and trap guard

- **Task:** R0 · **Author:** Rashed (with Claude) · **Date:** 20.11.2026 · **Status:** done
- **Sources:** all files in `data/` («Sample data ALTYCA, sprintd Basel 2026»); code in `pipeline/`

## Result
Baseline year Sep 2025 – Aug 2026: **CHF 470,288.93**, of which CHF 6,630.91 imputed for missing costs.
Confirmed to the franc by `pipeline/verify_baseline.py` (different code path) and by Hakim's `analysis/reconcile.py` (no pandas).

| Source | CHF |
| --- | ---: |
| Azure | 201,636 |
| SaaS | 114,158 |
| AWS | 60,274 |
| AI API (gateway) | 39,444 |
| AI subscriptions | 35,768 |
| Hoster | 19,009 |

With Vinzenz's factors (V1, V2), summed on the baseline rows of `out/fact_costs.csv` (refreshed 21.11.2026 from that file, one decimal): energy **35,782.8 kWh** (19,365.9–69,223.9), CO2 location-based **6,197.5 kg** (2,899.1–15,379.6). The earlier 36.3 MWh / 6.47 t in this note was the figure from before the factor update. `saas_licence_month` is still empty, so SaaS licences add no kWh.

## Cleaning decisions
Details per row in `out/quality_log.csv`; summary in `pipeline/README.md`. Duplicates removed (Azure 7, AWS 5, hoster 3, AI 87),
drafts dropped (AI subscriptions 24, SaaS 121), missing costs imputed from the median unit price, EUR/USD converted monthly,
SLA credits kept as money back, project IDs normalised, free text never used to change a number.

## Trap guard
`pipeline/trap_guard.py` quarantines planted instructions (all five, incl. T-1251), fails if the baseline drifts or db-fin/sandbox
costs disappear, and blocks measures that switch off protected resources or skip their ticket. Rules: `docs/traps.md`,
`docs/protected.csv`, `docs/one_off_costs.csv`.
