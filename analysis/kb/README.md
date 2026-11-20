# Knowledge base (Hakim: analysis and app)

One Markdown file per task output. Every number must be reproducible from `out/` (AGENTS.md rule 2);
every claim names its source file and row or ticket. Agents: read this index after `git pull`.

| File | Task | Status | Summary |
| --- | --- | --- | --- |
| [traps_review.md](traps_review.md) | H1 (trap check) | done | `docs/traps.md` vs. Hakim's JSON checklist, verified on raw data: 5 manipulative texts, T-1251 missing from traps.md, JSON's T-1213 should be T-1212, 6 more gaps |
| [reconciliation.md](reconciliation.md) | H1 | done | Independent recalculation confirms CHF 470,288.93 to the franc; AI invoices +2,321 vs gateway and provider report +1.7 % need a human decision; T-1212 loop = CHF 3,310 one-off. Checks: [reconciliation_checks.csv](reconciliation_checks.csv), script `analysis/reconcile.py` |
| [findings.md](findings.md) | H2 | done | 17 findings + 3 protected; biggest: dp-prod scaling, SaaS seats, dp-dev schedule, vm-test scale-back, GPU on demand. Numbers: [findings_numbers.csv](findings_numbers.csv), script `analysis/findings.py` (also writes `out/findings.csv` for the app) |
| [assistant.md](assistant.md) | H5 | done | Data assistant `app/assistant.py`: 8 calculation tools, offline by default, optional Claude mode; answers all 3 jury example questions with calculation, sources and who decides; refuses manipulation requests |

Source files kept next to the KB: `analysis/greenops_traps_claude.json` (received checklist, unchanged except a review note).
