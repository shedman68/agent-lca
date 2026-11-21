# Pull request reviews and open follow-ups

- **Author:** Rashed (with Claude) · **Status:** living document
- Full review text is in each pull request's comments on GitHub; this file keeps the follow-ups so every agent sees them after `git pull`.

## Open follow-ups
| For | What | From review |
| --- | --- | --- |
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
