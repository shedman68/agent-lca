# Decision log

- **Author:** Rashed (with Claude) · **Status:** living document, newest on top
- Every decision: date, what, why, who decided, where it was discussed.

| Date | Decision | Why | Who | Where |
| --- | --- | --- | --- | --- |
| 21.11. 00:15 | Hard rules enforced by Claude Code: deny edits to `data/` and pushes to `main`; Stop hook requires MATCH + trap guard PASS; `trap-reviewer` subagent before every PR | prompts cannot guarantee zero-exception rules | Rashed | this PR |
| 21.11. 00:00 | `analysis/findings.py` is official step 2 after `pipeline.py`; then verify_baseline and trap_guard. `anthropic` optional; demo runs offline | fast, keeps rule 2 (numbers only via `out/`); offline demo sends no case data anywhere | Rashed | #14, #15 |
| 21.11. 00:00 | Findings get kWh and CO2 (low/mid/high); the assistant shows CO2 and reads seats from `out/` | needed for R1/R2; closes the review gap on #12 | Rashed | #14, #16 |
| 20.11. 23:45 | AI API baseline uses the **AI gateway** (CHF 39,444), not the invoices; the +CHF 2,321 (5.9 %) invoice gap is stated in the assumptions template | gateway has department and tool detail; gap is small and disclosed | Rashed | #2 review |
| 20.11. 23:45 | Merge order #9 → #2 → #5 → #8 → #7 → #10 → #6 → #12 → #11; #1 closed as a stale duplicate | stacked pull requests; one version of the truth on `main` | Rashed | chat |
| 20.11. 23:30 | Every agent uses the `trap-guard` skill first; `pipeline/trap_guard.py` must print PASS in every PR | the data contains planted instructions and protected resources | Rashed | #9 |
| 20.11. 21:00 | Baseline year Sep 2025 – Aug 2026: **CHF 470,288.93**, verified by two independent routes (pipeline + Hakim's reconcile.py) | case rules; verified to the franc | Rashed, Hakim | #2 |
| pending | Swiss grid factor: consumption mix 0.090 kg/kWh (production mix as sensitivity) | Vinzenz's recommendation, two sources agree | Rashed to confirm | #5 |
| pending | Protect `main` on GitHub (require a pull request) | #4 was merged by its author | Rashed (GitHub settings) | chat |
