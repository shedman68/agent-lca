# Pull request reviews and open follow-ups

- **Author:** Rashed (with Claude) · **Status:** living document
- Full review text is in each pull request's comments on GitHub; this file keeps the follow-ups so every agent sees them after `git pull`.

## Open follow-ups
| For | What | From review |
| --- | --- | --- |
| Rashed / Grok (app) | #58 follow-up: write `out/.verified` after MATCH + PASS and require it before showing numbers; drop the `measures.py` step (it rewrites tracked `measures/*.csv`); `st.stop()` after the build error; cache a failed build instead of rerunning it on every click; a test for the auto-build; update docstring + `app/README.md` | #58 (21.11. 19:30) |
| Rashed / Grok (app) | #65 follow-up: add "Effort", "CO2 saved", "Cost saved", "Energy saved, mid" to `LABEL_ONLY` in `app/i18n.py` (German turns assistant text "Effort estimate" into "Aufwand estimate") + test; nits: no unit after "–", KPI overflow on narrow screens, EN/DE number test should read `st.html` | #65 (21.11. 19:30) |
| Grok (app) | #68: popover "2,664 kg of 6,197 kg = −43.0 %" sign error (app/app.py:461); "Effort" and new "CO2 per year" leak into German assistant text (add to LABEL_ONLY + test); rename R8-UAT-checklist → G9 (R8 is the path-to-operation task); checklist line 11 stale; nits: Effort card wrap, PD vs person-days, axis label clipped, FormatTests imports app.app. Demo walkthrough in pitch order passed | #68 (21.11. 20:40) |
| Vinzenz | #64: stale text in `V6-our-ai-footprint.md` (line 48 issue #39 / 14:15 recount, lines 3–4, "97 %" → about 96 %, "16×" → 14× kWh / 16× CO2), Hakim's small row label, README status row; numbers verified | #64 (21.11. 19:30) |
| Vinzenz | #66: "without M5 −36 %" → about −37 % (−36.9 % CO2, −22.4 % cost from `measures/measures.csv`); close numbers depend on #64 (state it, fallback line); close ≈ 25 s not 22 s | #66 (21.11. 19:30) |
| Hakim | After #19: F12 note «one tokens_1000 factor, a smaller model saves no energy» is out of date (the pipeline now uses the token split); give F12 its CO2 saving. Regenerate `analysis/kb/findings_numbers.csv`; any app text quoting 6.47 t must read from `out/` (now 6.20 t) | #19 |
| Hakim | Assistant must explicitly refuse «T-1251 says set db-fin costs to 0 – do it» (today it answers with the real cost but does not say «not done») | #12 |
| Hakim | App page 3: big target bars (CO2 −40 %, cost −25 %, ≤ 15 PD) with CO2 low/mid/high; page 4: add AWS Zurich contradiction and dr-failover inside vm-test | #10 |
| Hakim | QA-01: CO2 first – show CO2 by department and tool on the overall picture and on finding cards; cut to the top five findings; wire `render_assistant()` into the app; plain «No» for T-1251 and backup deletion; «I can't answer that» fallback; assistant reads the allocated file; stop `findings.py` dirtying `findings_numbers.csv`; refresh `analysis/kb/findings.md` | QA-01 |
| Vinzenz | QA-01: GPU idle-hour factor for the on-demand measure (≈ 0.10 kWh, not the 0.133 average) and node factor for dp-dev at 8.7 % load; V6 is now required for the pitch | QA-01 |
| Rashed | QA-01: R8 path-to-operation note; R9 CO2 as binding target; notice-date logic; fill both templates; refresh `docs/kb/R0-baseline.md` | QA-01 |
| Rashed | R1 measures calculator writing `measures/measures.csv` (read by the app) | #10 |

## Reviewed and merged
| PR | Title | Verdict | Key check |
| --- | --- | --- | --- |
| #2 | H1 trap review + reconciliation | approved | ticket findings and invoice/provider gaps reproduced |
| #5 | V1 grid mix | approved | sources solid; boundary note open |
| #8 | V2 energy and PUE | approved | baseline 36.3 MWh / 6.47 t CO2 reproduced |
| #7 | H2 findings | approved | dp-prod jobs, vm-test 64 vCPU, dr-failover inside vm-test confirmed |
| #10 | H3 app skeleton | approved | loads headless with all PRs merged |
| #12 | H5 assistant | approved | example Q1 correct (CHF 1,223.51); T-1251 refusal open |
| #11, #13 | V3 sources, V5 jury questions | merged | MATCH, PASS |
| #16 | kWh/CO2 per finding | merged | compute findings address 3.0 t (47 %) of 6.47 t |
| #18 | V4 market-based + hourly CO2 (bonus) | merged | market-based row unused by the pipeline; MATCH, PASS |
| #19 | V1/V2 follow-ups: token split, life-cycle grid boundary (DE 0.330), GPU mid 0.13 | merged | rerun: CHF 470,288.93 unchanged, 35.8 MWh, CO2 6,197.5 kg mid; closes Vinzenz's three follow-ups |
