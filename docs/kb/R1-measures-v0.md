# R1 v0 – first draft of the measures package (for review, not final)

- **Task:** R1 / R9 · **Author:** Rashed (with Claude, written overnight) · **Date:** 21.11.2026 02:30 · **Status:** draft
- **Sources:** `out/findings.csv`, `out/fact_costs.csv`, `factors/factors.csv`, `docs/protected.csv`, `docs/one_off_costs.csv`.
  Run: `python3 measures/measures.py --out out`. Files: `measures/measures.csv` (package), `measures/candidates.csv`, `measures/package_summary.csv`.
- The VS Code session holds a separate R1 plan on the local branch `rashed/R1-measures` (`docs/kb/R1-plan.md`, four open decisions).
  This v0 does not replace it: merge the two in the morning.

## Result (computed)
**14.0 person-days (CHF 15,400) · cost −28.4 % (CHF 133,427) · CO2 −42.2 % mid (2,614 kg) · −49.0 % on low factors · −40.0 % on high factors.**
Checks with this package: `verify_baseline` MATCH · `trap_guard --measures` TRAP GUARD: PASS.

| ID | Measure | PD | CHF / year | CO2 kg (low / mid / high) | Protection |
| --- | --- | ---: | ---: | --- | --- |
| M1 | Pause dp-dev outside working hours, auto-start for training | 2.0 | 26,316 | 717 / 1,221 / 2,446 | T-1053 |
| M2 | GPU on demand | 1.0 | 10,863 | 235 / 325 / 1,604 | T-1101 |
| M3 | Retire three unused Dublin servers | 0.5 | 4,628 | 76 / 131 / 249 | T-1204; fallback server stays (T-1094) |
| M4 | Scale test environment back (8 of 12 project servers) | 1.5 | 12,403 | 205 / 350 / 666 | T-1204, T-1058 |
| M5 | Resize dp-prod in idle hours (never stop) | 3.0 | 29,127 | 141 / 378 / 632 | T-1029 |
| M6 | Log retention 365 → 90 days | 1.0 | 8,566 | 37 / 120 / 269 | backups untouched (T-1039) |
| M7 | Unused AI seats per department | 1.0 | 10,983 | 0 | T-1128 |
| M8 | Unused SaaS seats at notice dates | 2.5 | 25,946 | 0 | notice dates |
| M9 | Small model + caching for marketing classification | 1.5 | 4,595 | 11 / 89 / 293 | T-1163, T-1212 |

Not in the package (candidates): C1 small model for simple office-assistant tasks (2 PD, CHF 6,063, 137 kg) · C2 move dp-dev to
Switzerland (5 PD assumed, 404 kg, cost effect unknown).

## What is an assumption (must be reviewed before the draft submission)
1. **Realisation shares:** M2 energy 75 %, M4 67 %, M5 80 %, M7 80 %, M8 60 %. Everything else 100 % of the finding's addressable value.
2. **Person-days per measure** – none comes from the data.
3. C1: 50 % of large-model office-assistant use can move; small/large price ratio 0.44 (from finding F12).
4. C2: 5 PD and no cost change.

## Risks
- **CO2 margin is 2.2 points (mid) and zero on the high factors.** M1 alone is 47 % of the CO2 saving. If Vinzenz lowers the dp-dev node factor
  for 8.7 % load (QA-01), M1 and the baseline both shrink; the percentage may hold, to be recomputed.
- M5 needs sign-off from Head of Consulting and Finance; without M5 cost falls to −22.2 % and CO2 to −36.1 % (computed from the table above).
- 1 PD of slack. Swapping M9 for C1 gives more CO2 for 0.5 PD more.
- M8 does not model each contract's notice date yet; 60 % is a placeholder for «deadline passed» contracts.
