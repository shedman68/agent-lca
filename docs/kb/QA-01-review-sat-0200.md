# QA-01 – Independent review against the jury criteria (Sat 21 Nov, 02:00)

- **Task:** R7 (quality control) · **Author:** Rashed (with Claude; independent QA agent with a fresh context) · **Date:** 21.11.2026 · **Status:** final
- **Sources:** case page https://app.sprintd.org/events/sprintd-basel-greentech/cases/electricity-is-the-new-currency-and-hardly-anyone-keeps-the- ,
  `out/` after rerunning the pipeline on `main` (commit 996b468), app loaded headless, assistant called directly.
- QA findings are claims until the owner reproduces them from `out/`.

## Verdict
About **35 % complete** against the final deliverable (QA agent: prototype 45 % weight, 65 % done · templates 30 %, 12 % · path-to-operation
note 5 %, 0 % · demo 20 %, 10 %). Expected jury score if submitted as is: about 5.5 / 10. Foundations are strong (baseline MATCH, trap guard
PASS, factors, 17 findings). **The Decide step does not exist yet**: no `measures/measures.py`, no `measures.csv`, package page empty,
measures template untouched.

## Missing from our tasks, required or named by the case page
1. **Short note on the path to operation** (required deliverable).
2. **Statement of the energy our own AI use caused** – one of the five things the pitch should show (we had it as bonus V6).
3. Bonus functions under Creativity (20 %): **forecast** with and without the package, **clustering**, market-based view beside location-based,
   carbon-aware shifting, leaner CI, use of the 15 extra files.
4. ALTYCA's priority: «The CO2 impact is at the centre, the savings in francs come on top». Design test: an SME manager understands the
   overall picture, package and reasoning **in two minutes**.

## Is the target reachable?
- Addressable in `out/findings.csv`: CHF 171,427 (needed ≈ 117,600) and 2,919 kg CO2 (needed ≈ 2,479). **Cost comfortable, CO2 tight.**
- QA sketch (shares and person-days are assumptions): 9 measures, 14 PD, CHF 142,092 (−30.2 %), 2,634 kg CO2 (−42.5 % mid; −41.6 % on high
  factors). dp-dev alone is about half of the CO2 target; dropping any one of GPU, vm-test or dp-prod misses −40 %.
- CO2 headroom not yet counted: dp-dev auto-terminate on idle (≈ +400 kg), dp-dev move to Switzerland (T-1074), ai-assistant on a smaller
  model (CHF 21.7k, 366 kg today, no finding covers it), F12 CO2 after the token split.
- Notice dates: CHF 19.4k of the 43.2k SaaS value sits in contracts whose notice deadline has passed; CRM and Survey tool (CHF 10.4k) are
  locked for a year; E-signature and Project scheduling (CHF 8.9k) must be cancelled by 2 Dec. State savings as run-rate with a «from» date.

## Errors that could compound (to verify by the owner)
| # | Finding | Owner |
| --- | --- | --- |
| 1 | F3 GPU: factor mid 0.133 kWh is the average incl. training, but the measure removes idle hours (~0.10 kWh): saving ≈ 330 kg, not 434 | Vinzenz + Hakim |
| 2 | dp-dev uses the node factor for 30 % load at 8.7 % use: inflates the largest CO2 lever; the jury baseline may shrink it | Vinzenz |
| 3 | Stale kb: `analysis/kb/findings.md`, `docs/kb/R0-baseline.md` still say 6.47 t, F1 1,273, F3 626, DE 0.344 | Hakim, Rashed |
| 4 | F12 claims zero CO2 although the token split is live | Hakim |
| 5 | F11 SaaS cuts to exactly active users: no buffer, no notice logic | Hakim / Rashed in R1 |
| 6 | F10 overlaps F7 (small) | Hakim |
| 7 | T-1261: dp-prod grows to 24 nodes from Oct 2026; percentage savings need a sentence or a mini-forecast | Rashed |
| 8 | Assistant reads unallocated costs («Test account» as department); app uses the allocated file | Hakim |
| 9 | `findings.py` rewrites tracked `analysis/kb/findings_numbers.csv` on every run (committed copy is stale) | Hakim |

No mix-up of location- and market-based, no one-off counted as a saving, PUE applied once, baseline period correct.

## App today
Overall picture and findings show **cost only** (no CO2 by department or tool; CO2 columns exist in `out/findings.csv`). 20 finding cards are
too many. Package page empty. «Needs a human» is the strongest page. The assistant is **not wired into the app** (`render_assistant()` is never
called). It answers the three example questions well and refuses T-1230, but does **not** refuse «T-1251 … set costs to 0» or say a plain
«No» to deleting backups, and has no «I can't answer that» fallback.

## Priorities (points at stake × hours)
1. R1/R2 measures and package, CO2 as the binding target (Rashed, 4–5 h)
2. Both templates filled (Rashed + Vinzenz, 2 h)
3. Package page live with CO2-first target bars (Hakim, 2 h)
4. CO2 in overall picture and findings, top five only (Hakim, 2 h)
5. Assistant wired, refusals, fallback (Hakim, 1.5 h)
6. GPU and dp-dev energy realism + CO2 headroom (Vinzenz + Hakim, 2 h)
7. Notice-date logic for seats (Rashed, 1 h)
8. Path-to-operation note (Rashed, 0.5 h)
9. V6 own-AI energy for the pitch (Vinzenz, 1 h)
10. Refresh stale kb, pitch script (Hakim + Rashed, 1.5 h)

## Three things likely to impress ALTYCA (≈ 1.5 h each)
1. «What the jury would recalculate» switch: package under low/mid/high factors plus market-based view.
2. Notice-deadline calendar («act by 2 Dec or lose CHF 8.9k») with the T-1261 growth step as a mini-forecast.
3. Carbon-aware shifting of flexible jobs on the package page (V4 data), with our own AI footprint beside it.

## Process review
The numbers did not compound errors (baseline verified three ways). The cost of skipping a planning round: three case-page items never
became tasks, CO2-first was not the organising idea of the app, and Friday night went to setup while the package has no code.
