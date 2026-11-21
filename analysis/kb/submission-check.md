# Submission check: both templates against out/, factors/ and measures/

- **Task:** Rashed's task 2 (by 13:30) · **Author:** Hakim's agent · **Date:** 21.11.2026 12:55 · **Status:** final (independent review applied)
- **Sources:** `submission/template_baseline_and_assumptions.csv`, `submission/template_measures_package.csv`, `data/template_*.csv`,
  `out/fact_costs.csv`, `out/findings.csv`, `factors/factors.csv`, `measures/measures.csv`, `measures/package_summary.csv`
  (`main` 760cdeb, after `pipeline.py` and `analysis/findings.py`)
- **Rerun:** `python analysis/check_submission.py`. Every comparison is one row in [submission_checks.csv](submission_checks.csv).
  Rows that cannot be compared are printed as notes and not counted.

## Result: 188 comparisons, 0 mismatches
| Area | Comparisons | What was compared |
| --- | ---: | --- |
| Format | 6 | Both files: UTF-8 BOM, exact columns, the 17 parameter rows in template order; every Must row has a value |
| Baseline totals | 10 | Cost CHF 470,288.93 (to the rappen); energy 19,365.9 / 35,782.8 / 69,223.9 kWh and CO2 2,899.1 / 6,197.5 / 15,379.6 kg (within 0.05); market-based CO2 213.0 / 1,932.3 / 19,659.6 kg = kWh × `grid_market_based` (within 0.5) |
| Factors | 44 | Every mapped factor row (grid CH/DE/IE/market, vCPU, node, GPU, storage, tokens, message, PUE; low/mid/high) **exactly** = `factors/factors.csv`, and each has a source |
| Measures | 91 | M1–M8 + C1 vs `measures/measures.csv`: effort, CHF, kWh, CO2 **exact**; description, resource, change, risks **identical**; assumptions identical or plus the one allowed sentence ("Market-based CO2 stays blank: …"); market-based column blank |
| Package | 16 | The template's own sums (14.5 PD, CHF 134,306, 12,603 kWh, 2,664 kg) and the measures' low/high (1,438 / 6,496 kg) = `package_summary.csv` exactly; −49.6 / −43.0 / −42.2 % and −28.6 % recomputed (within 0.05 pp); CHF 15,950 = 14.5 × 1,100; CO2 ≥ 40 % on low, mid and high, cost ≥ 25 %, ≤ 15 PD, all from the template sums |
| vs findings | 14 | M1 = F1, M2 = F3 (CO2 × 75 %), M3 = F4, M4 = F5 × 8/12, M5 = F2 × 80 %, M6 = F13, M7 = (F6 + F7) × 80 %, in CHF and CO2 mid (within 1) |
| Protection rules | 7 | Risks cite the ticket: M1 T-1053, M2 T-1101, M3 and M4 T-1204 + T-1094 (dr-failover stays, March freeze), M5 T-1029, M6 T-1039, M7 T-1128 |

**Notes, not counted:** `growth_per_year` is blank (bonus; T-1261 is a sentence and range on the Next year page). M8 (per contract)
and C1 (assumption: 50 % of large-model tasks) are not shares of one finding, so they are not compared with `out/findings.csv`.

**Test of the check itself:** changing M1's effort from 2.0 to 2.5 PD in a copy of the template gives 3 mismatches (the M1 effort,
the PD sum, CHF per PD). The file was restored afterwards (`git diff` empty).

## Observations (not errors; Rashed decides)
1. **Market-based is half-filled.** The baseline template has the market-based total (bonus, 1,932 kg mid), but every
   `savings_co2_kg_market_based` in the measures template is blank. Each assumptions text says why. Fine for the draft. For the
   final version, either fill the measures from the same factors or say in the pitch that the package is location-based only.
2. **The assumptions text in the submission has one extra sentence per measure** ("Market-based CO2 stays blank …").
   The source text from `measures.csv` is kept word for word.
3. **Measures that use a share of a finding** (documented in `assumptions_and_sources`):
   - M2 has 325 kg CO2 against F3's 434 kg (energy share 75 %);
   - M4 is 67 % of F5 (8 of the 12 project servers);
   - M5 is 80 % of F2;
   - M7 is 80 % of F6 + F7.

   If a juror compares the findings page with the package page, these are the explanations.
4. **`growth_per_year` is blank** (bonus). T-1261 (dp-prod 20 → 24 nodes from 1 Oct 2026) is on the Next year page as a sentence
   and a range only. That is consistent with the 10:10 decision.
5. **ID clash:** `out/findings.csv` uses P1–P3 for protected resources, and the app's Needs-a-human page uses P1–P5 for planted texts.
   Neither template uses these IDs, but the pitch might (see the comment on #30).
