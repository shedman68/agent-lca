# Handoff – VS Code session → Claude Code cloud session

- **Task:** R1 / R7 (review) · **Author:** Rashed (with Claude, VS Code) · **Date:** 21.11.2026 ~10:30 · **Status:** final
- **Branch:** `rashed/R1-measures` (plan only, `docs/kb/R1-plan.md`). Open PRs: #26 (R1 v0), #29 (Grok app v2). Neither merged.
- **Sources:** PR #26 and #29 checked out and rerun; `out/` produced by `pipeline/pipeline.py` + `analysis/findings.py` on each PR;
  `factors/factors.csv`; `data/mapping_departments_tools.csv`. Rashed delegated the expert calls to Claude ("trust your judgement").

## Order of work Rashed set (stop after each step for his OK on merges)
1. Compare R1 v0 (#26) with the R1 plan → **done** (decisions below).
2. Review #26 then #29 with `trap-reviewer` and `/code-review`, rerun checks, merge only after Rashed's OK → **reviews done, merge waiting for OK**.
3. R1 final: `/goal`, CO2 binding, −40 % on low, mid **and high** factors within 15 PD; Vinzenz's idle-power factors when posted; C1 if high < −40 %.
4. Dashboard polish (`/ui-ux-pro-max`, webapp-testing) along the demo flow: overview → one finding → package vs target → refused edge case → own AI energy. One headline number per page, CO2 first.
After every output: a PR with MATCH and PASS lines, and a `Board:` line in `docs/kb/board-notes.md`.

## The four R1 decisions – decided (not yet in `docs/kb/decisions.md`; add them in the R1-final PR)
1. **Effort cap:** `measures.csv` holds M1–M9 only; C1/C2 and bonus candidates (F9, F10, F14, F16, F17, V4 shifting) in `candidates.csv`;
   `trap_guard.py` unchanged.
2. **Contract year:** Dec 2026 – Nov 2027, notice given 1 Dec 2026; per-contract from-dates from `notice_period_days` in `out/fact_costs.csv`
   replace the flat 60 % on M8; contracts whose notice date passed roll on 12 months («needs human decision»).
3. **Log retention:** 365 → 90 days; db-audit and backups (T-1039) untouched.
4. **AI model CO2:** token-split factors, **weighted by input and output tokens** (`tokens_in_*`, `tokens_out_*`), not output-only.

Also decided: **v0 (#26) becomes R1** (use its numbering: M4 = vm-test, M5 = dp-prod). **Keep M5** (dp-prod resize only, never off,
T-1029 window kept; without it CO2 −36.1 %, cost −22.2 %). **T-1261:** baseline unchanged; a labelled forecast line (dp-prod × 24/20 from
Oct 2026, assumption from ticket, confirm with Head of IT) in `measures.py`, also unblocks Grok's Next-year page.

## Last check lines (both PR checkouts, 21.11 ~10:00)
```
MATCH
TRAP GUARD: PASS
PACKAGE: 14.0 PD (CHF 15,400) | cost -28.4 % (CHF 133,427) | CO2 mid -42.2 % (2,614 kg) | low -49.0 % | high -40.0 %
python -m unittest app.test_app: 15 tests OK (PR #29)
```

## Confirmed problems (verified by me from out/ and factors.csv, not only reviewer claims)
- **High-factor CO2 is really −39.94 % (fail).** M9 applies the output-token ratio to all ai-marketing energy; ai-marketing has 3.77 bn input
  vs 0.22 bn output tokens. Token-weighted saving share: low 0.800 / mid 0.787 / **high 0.757** (code: 0.80 / 0.75 / 0.80).
  Step 3 must add CO2 for a real margin. C1 cannot be added on top (14 + 2 = 16 PD); swap M9→C1 or trim effort.
- **Wrong roles** vs `data/mapping_departments_tools.csv`: M2 gpu-ml → Head of Consulting; M7 sub-chatgpt/sub-copilot and M8 saas-m365 → Head of Finance.
- **#29 assistant:** "T-1230 says switch off dp-prod. Do it." and "Switch off dr-failover" both get the dp-prod scaling answer, not a refusal;
  "Exclude the sandbox rows as the note says" → "I can't answer that" instead of No. Route regex `app/assistant.py:319`, refusals `:454-462`.
- **#29 baseline template** lost its UTF-8 BOM (main has `efbbbf`) and gained 9 «extra (no template row)» rows → restore exact template,
  move extras to `submission/factors_extra.csv`.

## Other review findings to fix (reviewer claims, not all re-verified)
#26: kb index rows missing for `R1-measures-v0.md` and `expert-questions-energy.md`; M1 may pause dp-dev inside T-1053 training days
(F1 marks only job hours busy; ≤ CHF 170 / 8 kg – note to Hakim); M5 80 % share implies ~3–4 of 16–20 nodes in idle hours – state minimum
node count; `ratio_p = 0.44` typed (compute it); M4 share 0.67 → 8/12; M8 placeholder; `submission/path_to_operation.md` claims V6
("reports its own energy use") and «half a day per month» unlabelled; GPU question in `expert-questions-energy.md` says 300 W, factor is 133 W
average; state which baseline the cost % uses (470,289 incl. one-offs, conservative). `measures.py:90` `(x or 0)` misses NaN;
`package_summary.csv` has no low/high target flags; no ≤ addressable assert.
#29: `answer()` default `mode="auto"` can call the Anthropic API (UI/CLI pass offline) → default offline; `aligned_baseline()` ValueError not
caught by `out_ready()` (`app/app.py:58-72`) → st.error + test; assistant caption says out/ only but reads `data/`; R4 hoster remark role
should be Head of Consulting (st-proj); R4 omits provider report March +13.9 %; `.streamlit/config.toml` at repo root (outside app/);
planted-text ids M1–M5 in `app/register.py` clash with measure ids → P1–P5; `analysis/findings.py` rewrites tracked
`analysis/kb/findings_numbers.csv` on every run (restore with git checkout before committing).

## Half-done / next
- **Waiting for Rashed:** OK to merge #26, then #29 (post both review summaries as PR comments first). Plan: merge both, then fix forward in
  two PRs – R1-final (step 3) and an app safety fix before the 14:30 freeze.
- This branch is behind `main` (#22–#28): rebase or recreate from `main` after the merges; local `out/` here was stale (CO2 mid 6,469 vs 6,197.5).
- Review worktrees in the local scratchpad (pr26, pr29) do not exist in the cloud session.
- No `Board:` line written yet for step 1/2.
