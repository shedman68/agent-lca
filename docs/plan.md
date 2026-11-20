# Plan

Full plan in Notion: «Green AI & Data case – plan to win». Short version:

## Status (Fri 21:30)
- [x] Data cleaned, baseline verified: CHF 470,289
- [x] Traps documented (`docs/traps.md`)
- [ ] Factors researched with ranges (`factors/factors.csv`) → energy + CO2 baseline
- [ ] Measures package that hits −40 % CO2 / −25 % cost / ≤ 15 PD (`measures/`)
- [ ] App: overall picture · findings · package with target bar · «needs a human» panel
- [ ] Both templates filled (`submission/`)
- [ ] Pitch rehearsed twice

## Candidate measures (to calculate)
1. Pause dp-dev outside working hours; auto-start for quarterly training (T-1053)
2. Night/weekend schedule for dp-prod except finance closing (T-1029) → human sign-off
3. GPU server on demand, except quarterly training (T-1101)
4. Delete Dublin zombies: poc-ki-2024, migration-alt, build-agent-old → owner confirms
5. Auto-stop sandboxes; schedule test servers except March freeze (T-1204)
6. Smaller model + caching for Office AI assistant and marketing text analysis
7. Cut idle AI seats by department (T-1128)
8. Right-size SaaS seats at next notice date
9. Log retention / storage tiers – not backups (T-1039)
Bonus: carbon-aware shifting of flexible jobs; skip nightly builds without commits.

## Demo (5 min)
Overall picture 45 s · one finding (dp-dev 24/7 at ~9 % use) 45 s · package with target bar 90 s ·
edge case: production at month-end + the manipulative ticket the tool refuses 60 s · why it matters for Basel 30 s.
