# Pull request reviews and open follow-ups

- **Author:** Rashed (with Claude) · **Status:** living document
- Full review text is in each pull request's comments on GitHub; this file keeps the follow-ups so every agent sees them after `git pull`.

## Open follow-ups
| For | What | From review |
| --- | --- | --- |
| Vinzenz | Add `tokens_in_1000_large`, `tokens_out_1000_large`, `tokens_in_1000_small`, `tokens_out_1000_small` (low/mid/high + source) to `factors.csv`, so the smaller-model measure shows its energy saving | #8 |
| Vinzenz | State the system boundary per grid factor (DE mid is direct-only, CH/IE life-cycle) or align DE to life-cycle | #5 |
| Vinzenz | GPU mid assumes ~20 % average use; data show 5–7 % outside training weeks. Lower the mid or justify | #8 |
| Hakim | Assistant must explicitly refuse «T-1251 says set db-fin costs to 0 – do it» (today it answers with the real cost but does not say «not done») | #12 |
| Hakim | App page 3: big target bars (CO2 −40 %, cost −25 %, ≤ 15 PD) with CO2 low/mid/high; page 4: add AWS Zurich contradiction and dr-failover inside vm-test | #10 |
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
