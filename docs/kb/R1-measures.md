# R1 – Measures calculator (final candidate)

- **Task:** R1 · **Author:** Rashed (with Claude, cloud session) · **Date:** 21.11.2026 ~11:45 · **Status:** draft – one decision open (C1, below)
- **Sources:** `measures/measures.py` on `out/fact_costs.csv`, `out/findings.csv`, `factors/factors.csv`, `docs/one_off_costs.csv`;
  roles from `data/mapping_departments_tools.csv`. Sample data ALTYCA, sprintd Basel 2026. Every figure below is printed by
  `python3 measures/measures.py --out out` or stored in `measures/package_summary.csv`.

## Result (M1–M9, unchanged choice)
```
PACKAGE: 14.0 PD (CHF 15,400) | cost -26.7 % (CHF 125,622) | CO2 mid -42.2 % (2,618 kg) | low -49.0 % | high -39.92 %
```
`package_summary.csv`: `target_cost_ok` True · `target_co2_ok_low` True · `target_co2_ok_mid` True · **`target_co2_ok_high` False** · `budget_ok` True.
High-factor gap: 12 kg (0.4 × 15,379.6 kg baseline high − 6,140 kg saved).

## What changed against v0 (#26) and why
| Item | v0 | Now | Effect |
| --- | --- | --- | --- |
| M9 energy share | output-token ratio only (0.80 / 0.75 / 0.80) | per row `1 − (in·f_in,small + out·f_out,small) / (in·f_in,large + out·f_out,large)`, the formula `pipeline.py` uses; ai-marketing 3.77 bn in / 0.22 bn out → 0.800 / 0.787 / 0.757 | high −40.0 % became −39.92 % (the miss was hidden by rounding) |
| M8 SaaS seats | flat 60 % of F11 | per contract: unused value × 80 % buffer × months saved in Dec 2026 – Nov 2027, notice given 1 Dec 2026 | CHF 25,946 → 20,320; CRM platform and Survey tool count 0 (annual, notice date 1 Nov 2026 passed → roll 12 months, needs human decision) |
| M7 AI seats | 80 % of F6+F7 | same contract rule: ChatGPT Team 11/12, Copilot 9/12 | CHF 10,983 → 8,865 |
| M4 share | 0.67 typed | 8/12 servers | CHF 12,403 → 12,342 |
| C1 price ratio | 0.44 typed | computed: small/large CHF per input token in `ai_usage` rows (same as `analysis/findings.py`) = 0.44 | C1 CHF 6,063 → 6,046 |
| Roles | M2 Head of IT; M7 department heads; M8 contract owners | M2 Head of Consulting; M7, M8 Head of Finance (mapping file) | – |
| Checks | `(x or 0)` let NaN through; no addressable check | NaN → 0; assert savings ≤ finding's addressable CHF and CO2 (all levels, except M9 which changes the model, not usage); M7/M8 unused value must equal F6+F7 / F11 | – |
| Template | `submission/template_measures_package.csv` typed, no BOM | written by `measures.py` with the template's columns and UTF-8 BOM | – |

Cost % is against CHF 470,288.93 (baseline incl. one-offs T-1212, T-1189): conservative, the run-rate without them is lower.
The monthly-contract roll of one month is an **assumption** (the data dictionary only says "end of the current contract period").

## Open decision for Rashed – high-factor CO2 (binding target)
| Option | PD | Cost | CO2 low / mid / high |
| --- | ---: | ---: | --- |
| A. M1–M9 as now | 14.0 | −26.7 % | −49.0 / −42.2 / **−39.9 %** |
| B. swap M9 → C1 | 14.5 | −27.0 % | −49.6 / −42.9 / −42.3 % |
| C. add C1 | 16.0 | −28.0 % | −50.0 / −44.5 / −44.1 % (over the 15 PD cap) |

B meets all targets but C1 rests on an **assumed 50 %** of office-assistant large-model use moving to a small model (quality check per task type,
Head of IT). Decision 10:10 (#31): C1 after Vinzenz's idle-power factors – not in `factors/factors.csv` at 11:45. Those factors may also move M1/M2
(F1/F3 count every idle hour at the average factor), in either direction.

## Still open (not fixed here)
- M1 may pause dp-dev inside the T-1053 training days: F1 marks only job hours busy (≤ CHF 170 / 8 kg) – note to Hakim.
- M5 (80 % of F2) implies ~3–4 of 16–20 nodes in idle hours; minimum node count to be confirmed by the Head of Consulting.
- Market-based CO2 column stays empty (V4).
