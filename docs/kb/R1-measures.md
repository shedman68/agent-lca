# R1 – Measures package (final for the draft submission)

- **Task:** R1 / R9 · **Author:** Rashed (with Claude) · **Date:** 21.11.2026 10:40 · **Status:** final for the 15:00 draft
- **Run:** `python3 measures/measures.py --out out` → `measures/measures.csv` (package), `candidates.csv`, `package_summary.csv`.
- **Sources:** `out/findings.csv`, `out/fact_costs.csv`, `factors/factors.csv`, `docs/protected.csv`, `docs/one_off_costs.csv`.

## Result (computed)
**14.5 person-days (CHF 15,950) · cost −29.0 % (CHF 136,514 a year) · CO2 −43.0 % mid (2,664 kg) · −49.6 % low · −42.2 % high.**
Passes all three targets on low, mid and high factors. Checks: `verify_baseline` MATCH · `trap_guard --measures` TRAP GUARD: PASS.

| ID | Measure | PD | CHF / year | CO2 kg low / mid / high | Decides |
| --- | --- | ---: | ---: | --- | --- |
| M1 | Pause dp-dev outside working hours, auto-start for training (T-1053) | 2.0 | 26,316 | 717 / 1,221 / 2,446 | Head of IT |
| M2 | GPU on demand, auto-start for training (T-1101) | 1.0 | 10,863 | 235 / 325 / 1,604 | Head of Consulting |
| M3 | Retire three unused Dublin servers; fallback server stays (T-1094) | 0.5 | 4,628 | 76 / 131 / 249 | Head of IT |
| M4 | Scale test environment back, 8 of 12 project servers (T-1204, T-1058) | 1.5 | 12,342 | 204 / 349 / 663 | Head of IT |
| M5 | Resize dp-prod in idle hours, never off (T-1029) | 3.0 | 29,127 | 141 / 378 / 632 | Head of Consulting with Finance |
| M6 | Log retention 365 → 90 days; backups untouched (T-1039) | 1.0 | 8,566 | 37 / 120 / 269 | Head of IT |
| M7 | Unused AI seats, per department (T-1128) | 1.0 | 10,983 | 0 | Head of Finance |
| M8 | Unused SaaS seats at notice dates | 2.5 | 25,946 | 0 | Head of Finance |
| C1 | Office AI assistant: simple tasks on a small model | 2.0 | 7,743 | 28 / 140 / 633 | Head of IT |

Not in the package: M9 marketing small model (1.5 PD, 94 kg mid) · C2 move dp-dev to Zurich (5 PD, 404 kg mid, cost effect unknown).

## Assumptions (not from the data)
Realisation shares (M2 energy 75 %, M4 8/12, M5 80 %, M7 80 %, M8 60 % placeholder), person-days per measure, C1: 50 % of large-model
office-assistant use can move. Everything else is computed from `out/`.

## Still open before 14:30
- M8 per-contract notice dates (decision 2) instead of the 60 % placeholder.
- Vinzenz's idle-power factors for dp-dev and GPU: rerun; margin on high factors is 2.2 points.
