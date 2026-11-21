# R1 – Measures calculator: plan

- **Task:** R1 · **Author:** Rashed (with Claude) · **Date:** 21.11.2026 · **Status:** draft – waiting for Rashed's OK
- **Branch:** `rashed/R1-measures` · **Due:** Sat 21 Nov 12:00
- **Sources:** `docs/plan.md` (candidate list), `docs/traps.md`, `docs/protected.csv`, `docs/one_off_costs.csv`,
  `out/fact_costs.csv`, `out/findings.csv`, usage files in `data/` (read only), `factors/factors.csv`

## Method (applies to every measure)
- **Input rows** = baseline rows of `out/fact_costs.csv` (`in_baseline`) for the measure's `resource_id`s. Numbers come only from there
  and from usage files in `data/`; never from ticket or note text.
- **Saving per year** = CHF of the rows changed × share removed. One-offs T-1212 (ai-marketing) and T-1189 (net-egress) are
  subtracted from the input rows first, so they are never a recurring saving.
- **kWh and CO2 low/mid/high** = same share of the rows' `kwh_*` / `co2_kg_*` (location-based, country of the row).
  `savings_energy_kwh_per_year` and `savings_co2_kg_location_based` hold **mid**; extra columns hold low and high.
  Market-based CO2 stays empty until V4 (stated in assumptions).
- **Share removed** comes from usage data (hours used, CPU, seats active), with the protection window added back
  (e.g. quarterly training days 1–3 of Jan/Apr/Jul/Oct, month-end close, March freeze).
- **Contracts (AI and SaaS seats):** saving counts only months after the earliest end date reachable with notice given on
  1 Dec 2026, inside a 12-month implementation year Dec 2026 – Nov 2027. Contracts whose notice date already passed roll on
  12 months (assumption, «needs human decision»).
- **Effort** in PD (1 PD = CHF 1,100) with a one-line reason per measure.
- **Cross-check:** every CHF and CO2 saving is compared with `addressable_*` in `out/findings.csv` (Hakim's F-rows); a measure
  above its finding's addressable amount fails a built-in assert.
- Every row cites its tickets in `risks_and_exceptions`; anything touching seats, a model, dp-prod or an owner gets
  «needs human decision» + responsible role from `data/mapping_departments_tools.csv`.

## Candidate measures (one row each in `measures/measures.csv`)
| ID | Measure | Resources | Protection / tickets | Finding |
| --- | --- | --- | --- | --- |
| M1 | dp-dev: pause outside work hours, auto-start before quarterly training | dp-dev | T-1053 (days 1–3 Jan/Apr/Jul/Oct), alt. T-1074 | F1 |
| M2 | dp-prod: scale nodes down in idle hours, keep night jobs 02:00–08:00 and month-end 18:00–04:00 – human sign-off | dp-prod | T-1029; T-1230 refused (planted); T-1261 not in baseline | F2 |
| M3 | GPU on demand with auto-start for quarterly training | gpu-ml / gpu-ml-01 | T-1101, T-1035 | F3 |
| M4 | Dublin zombies poc-ki-2024, migration-alt, build-agent-old – owner confirms first | 3 servers | owner = needs human; dr-failover not touched (T-1094) | F4 |
| M5 | vm-test: scale back from 64 vCPU after P-009, keep dr-failover's 4 vCPU, no change in March | vm-test | T-1204, T-1094, T-1058 | F5 |
| M6 | AI: smaller model + prompt caching for marketing text analysis and office assistant – quality check | ai-marketing, ai-assistant | T-1163 (campaign peaks), T-1212 one-off excluded | F12 |
| M7 | Idle AI seats cut by department at the next notice date | sub-chatgpt, sub-copilot, sub-claude | T-1128 (per department) | F6–F8 |
| M8 | SaaS seats without active users cut at the next notice date | saas-* | notice periods per contract | F11 |
| M9 | Log retention 365 → 90 days (not backups, keep db-audit) | logs | T-1039 (backups untouched) | F13 |

Not in `measures.csv` (R1), written to `measures/candidates.csv` only, so R2 can pick from them:
- **M1b** dp-dev move to Switzerland (T-1074) – alternative to M1, cannot be added on top.
- Bonus: annual billing for remaining Claude/ChatGPT seats (F9), Copilot promotion (F10), Power BI refresh (F14, keep pbi-07),
  unread data-platform tables (F16), skip nightly builds without commits (F17), carbon-aware shifting (V4).

## Phases
- [ ] **P1 Skeleton** – `measures/measures.py` (CLI `--data --out`): load baseline rows, one-off subtraction,
  helper `scale(rows, share)` → CHF + kWh/CO2 low/mid/high, row writer in template column order + low/high columns.
  **Done when:** `python measures/measures.py --data data --out out` runs and writes a valid CSV with the template header.
- [ ] **P2 Measures M1–M5 (CO2 side)** – one function each, share from usage data, windows added back.
  **Done when:** 5 rows written; each CHF and CO2 ≤ its finding's addressable value (assert); trap_guard `--measures` PASS.
- [ ] **P3 Measures M6–M9 (cost side)** – contract/notice logic, one-off exclusion for ai-marketing.
  **Done when:** 9 rows; M7/M8 show months counted and notice dates in assumptions; trap_guard `--measures` PASS.
- [ ] **P4 Candidates file + totals** – `measures/candidates.csv` with M1b and bonus rows; script prints totals (CHF, kWh, CO2
  low/mid/high, PD) for `measures.csv` vs baseline and the −40 % / −25 % / 15 PD target (information only; choosing is R2).
  **Done when:** totals printed in this conversation; effort sum in `measures.csv` ≤ 15 PD.
- [ ] **P5 Write-up** – `docs/kb/R1-measures.md`: per measure the rows used, calculation, ticket, source, effort reason, risks;
  add it to `docs/kb/README.md`; add a row to `docs/kb/decisions.md` for the decisions below.
  **Done when:** every M-ID in `measures.csv` has a section with ticket + source file.
- [ ] **P6 Verify and review** – pipeline → findings → verify_baseline (MATCH) → trap_guard `--measures measures/measures.csv`
  (PASS) shown in this conversation; `trap-reviewer` subagent and `/code-review`; fix findings; PR `[R1] Measures calculator`
  with both verdicts, MATCH and TRAP GUARD lines, and done · learned · next. Do not merge.
  **Done when:** PR open on GitHub, link given to Rashed.

Commit after each phase.

## Decisions for Rashed (my recommendation first)
1. **Effort cap vs "all candidates":** `trap_guard.py --measures` fails if the effort of *all* rows exceeds 15 PD.
   → Recommend: `measures.csv` holds M1–M9 only (estimated ≈ 12–13 PD), alternatives and bonus go to `candidates.csv`.
   trap_guard stays unchanged. If M1–M9 honestly exceed 15 PD, I stop and ask instead of shaving estimates.
2. **Implementation year for contracts:** Dec 2026 – Nov 2027, notice given 1 Dec 2026; passed notice dates roll 12 months.
3. **Log retention target:** 90 days (keep db-audit full).
4. **AI model measure CO2:** token split factor rows are still open (Vinzenz). → Compute CHF now, CO2 from the existing AI rows'
   kWh/CO2 × share; refresh automatically when the factor rows land.
