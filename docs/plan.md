# Master plan – what we are building and who does what

Updated Sat 21 Nov, 00:30 (numbers after #18/#19). Owner: Rashed. Detailed tasks: `docs/tasks.md`. Rules: `AGENTS.md`. Traps: `docs/traps.md`.

## End goal (Sunday 22 Nov)
**Win the Green AI & Data case** with a working prototype that an SME's management understands and trusts:
it shows where cloud, servers, AI and SaaS create cost, energy and CO2, recommends a package of measures that
reaches **CO2 −40 % (location-based) and cost −25 % per year within 15 person-days (CHF 16,500)**, and refuses
everything unsafe – planted instructions, protected resources, one-off costs.

Deliverables:
1. **App** (`app/`, Streamlit): overall picture · findings · package with live target bars · «needs a human».
2. **`submission/template_baseline_and_assumptions.csv`** – totals, every factor with low/mid/high and source.
3. **`submission/template_measures_package.csv`** – one row per measure with effort, CHF, kWh, CO2, risks, sources.
4. **5-minute live demo + 3 minutes of questions**, Sunday from 09:00.

## The numbers so far (mid values, from `out/` after V1, V2 and Vinzenz's follow-ups #19)
| | Baseline year (Sep 2025 – Aug 2026) | Target | Needed |
| --- | ---: | ---: | ---: |
| Cost | CHF 470,289 (run-rate without one-offs ≈ 466,600) | −25 % | ≈ CHF 117,600 a year |
| Energy | 35.8 MWh (range 19.4–69.2) | – | – |
| CO2 location-based | 6.20 t (range 2.9–15.4) | −40 % | ≈ 2.48 t a year |

CO2 sits in compute, mostly outside Switzerland: dp-dev in Frankfurt 29 %, dp-prod 18 %, vm-test (Dublin) 11 %,
st-backup (Dublin, protected) 11 %, AI tokens 10 %, GPU (Frankfurt) 7 %. Compute findings F1–F5 address 2.78 t (45 %).
Smaller AI models now save energy too (token split, #19). Cost sits in the data platform and SaaS seats.
**So: compute measures carry the CO2 target, licence measures carry the cost target.**

## Who does what (each person works with their own agent)
| Person · agent | Delivers | Status |
| --- | --- | --- |
| **Rashed** · Claude Code + Cursor | pipeline, trap guard, measures calculator and package, «needs a human» list, both templates, pitch; reviews and merges | baseline done, trap guard done (PR #9); **next: R1 measures** |
| **Hakim** · Claude Code | trap review + reconciliation (H1), findings (H2), app (H3–H5) | H1 #2, H2 #7, H3 #10 ready for review |
| **Vinzenz** · Claude Code + Perplexity | grid mix (V1), energy per unit and PUE (V2), sources write-up (V3), market-based + hourly (V4) | V1 #5, V2 #8 ready for review; **next: V3, AI token split rows** |

## How the pieces connect
```
data/ ──► pipeline/pipeline.py ──► out/fact_costs.csv ──► analysis/findings.py ──► out/findings.csv ─┐
              ▲  factors/factors.csv (Vinzenz)                                                        ├─► app/ (Hakim)
              └─ verify_baseline.py (MATCH) · trap_guard.py (PASS)                                     │
out/ ──► measures/measures.py (Rashed) ──► measures/measures.csv ──► submission/ templates ───────────┘
```

## Merge order (Rashed)
1. #9 trap guard and skills (this PR) · 2. #2 H1 · 3. #5 V1 · 4. #8 V2 · 5. #7 H2 · 6. #10 H3 · 7. #6 Vinzenz check-in.
Close #1 (stale duplicate of main). After merging, everyone runs `git pull` and the three checks.

## Open decisions for Rashed
- AI baseline: gateway (CHF 39,444, has department detail) or invoices (+CHF 2,321)? Proposal: keep the gateway, state
  the gap in the assumptions template.
- Swiss grid factor: consumption mix 0.090 (Vinzenz's recommendation). Proposal: accept, show the production mix as a sensitivity.
- Protect `main` on GitHub (Settings → Branches → require a pull request) – PR #4 was merged by its author.

## Timeline to Sunday
| When | Milestone |
| --- | --- |
| Sat 10:00 | all open PRs merged; V3 started; R1 measures calculator started |
| Sat 12:00 | R1 done: every candidate measure with effort, CHF, kWh, CO2 (low/mid/high) |
| Sat 13:00 | H3 app reads `measures/measures.csv` |
| Sat 14:30 | R2 package chosen: −40 % CO2, −25 % cost, ≤ 15 PD, trap guard PASS |
| **Sat 15:00** | **draft submission** |
| Sat 18:00 | R4 «needs a human» list final; V3/V4 done; app chat assistant if time |
| Sat 20:00 | feature freeze; pitch rehearsal ×2 |
| **Sun 08:30** | **final submission** · 09:00 pitch |

## Candidate measures (R1 calculates them; protection rule in brackets)
1. dp-dev: pause outside work hours, auto-start for quarterly training [T-1053] – or move to Switzerland [T-1074]
2. dp-prod: scale nodes down in idle hours, keep night jobs 02:00–08:00 and month-end 18:00–04:00 [T-1029] – human sign-off
3. GPU on demand with auto-start for quarterly training [T-1101]
4. Dublin zombies: poc-ki-2024, migration-alt, build-agent-old – owner confirms
5. vm-test: scale back the 12 project servers after P-009, keep dr-failover [T-1204, T-1094]
6. AI: smaller model + caching for marketing text analysis and the office assistant – quality check
7. Idle AI seats by department at the next notice date [T-1128]
8. SaaS seats at the next notice date
9. Log retention 365 → shorter [not backups, T-1039]
Bonus: shift flexible jobs to low-CO2 hours (V4); skip nightly builds without commits.

## Demo (5 min)
Overall picture 45 s · one finding (dp-dev 24/7 at 8.7 % use) 45 s · package with target bars 90 s ·
edge case: what the tool refused (T-1230 «switch off production», T-1251 «set costs to 0») 60 s · why it matters for Basel 30 s.
