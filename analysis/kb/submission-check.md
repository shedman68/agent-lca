# Submission check: both templates against out/ and measures/ (Sat 21 Nov, 13:05)

- **Task:** Rashed's task 2 (by 13:30) · **Author:** Hakim's agent · **Checked on:** `main` 760cdeb, after `pipeline.py` and `analysis/findings.py`
- **Rerun:** `python analysis/check_submission.py`. The 77 checks with values are in [submission_checks.csv](submission_checks.csv).

## Result: 77 checks, 0 mismatches
| Area | Checks | What was compared |
| --- | ---: | --- |
| Format | 6 | Both files have the UTF-8 BOM, the exact columns and the 17 parameter rows in the template order, like `data/template_*.csv`. Every Must row has a value |
| Baseline totals | 7 | Cost CHF 470,288.93; energy 19,365.9 / 35,782.8 / 69,223.9 kWh; CO2 2,899.1 / 6,197.5 / 15,379.6 kg = sums of `out/fact_costs.csv` (baseline rows) |
| Factors | 33 | Every factor row (grid CH/DE/IE, vCPU, node, GPU, storage, tokens, message, PUE; low/mid/high) = `factors/factors.csv` |
| Measures | 10 | The 9 rows M1–M8 + C1 = `measures/measures.csv` in every shared column (numbers, risks, changes) |
| Package | 12 | Sums: 14.5 PD, CHF 134,306, 12,603 kWh, CO2 1,438 / 2,664 / 6,496 kg = `measures/package_summary.csv`; −49.6 / −43.0 / −42.2 % = sum ÷ baseline of the same level; −28.6 % cost; CHF 15,950 = 14.5 × 1,100; targets met |
| vs findings | 6 | M1 = F1, M3 = F4, M6 = F13 in CHF and CO2 mid (`out/findings.csv`) |
| Not in out/ | 3 | Market-based total 213 / 1,932.3 / 19,659.6 kg and market-based grid mix: bonus rows from Vinzenz (`factors/kb`); `growth_per_year` blank |

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
