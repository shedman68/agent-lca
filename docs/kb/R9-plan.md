# R9 – Plan: app v2, one user story for the pitch

- **Task:** R9 · **Author:** Rashed (with Claude, cloud session) · **Date:** 21.11.2026 21:50 · **Status:** in progress
- **Sources:** `docs/kb/R0-case-page.md` (case page, verbatim), `docs/kb/R6-pitch-script.md`, `factors/kb/V5-jury-questions.md`,
  `factors/kb/V7-pitch-parts.md` (PR #66, read if present), `AGENTS.md`, `docs/traps.md`, ALTYCA case slides
  (`data/documents/Presentation_Green_AI_Data_sprintd_Basel_EN.html`: colours, Manrope).
- **Why:** mentors: too technical, too much text, "straight from Python". Jury test: an SME manager understands the overall picture,
  the package and the reasoning in two minutes.

## Skills used
| Skill | Why |
| --- | --- |
| `trap-guard` (first) | numbers only from `app/data.py`/`out/`/`measures/`; protected resources and planted texts unchanged; checks before commit |
| `greenops-app` | project rules for `app/`: one message per page, big numbers, plain labels, show what the tool refused |
| `ui-ux-pro-max` (`.claude/skills`, #50) | rules: contrast ≥ 4.5:1, touch ≥ 44 px, no emoji icons, status never colour-only, reduced motion, mobile-first. Its generic palette (glassmorphism, Fira) is **not** used: ALTYCA's palette and Manrope win |
| `dataviz` | the few charts that stay: one hue for magnitude, labels on bars, accessible colours |
| not available here | `frontend-design` (not installed in this session) |

## Checklist (commit per page)
- [x] **P0 Theme + shell.** `app/theme.py`: ALTYCA tokens (bg #0d0f12, card #16191e, teal #00cc99 = good/PASS, pink #f84aa7 = refused /
  needs a human), light mode for the projector, Manrope (OFL) embedded as woff2 (offline), Streamlit chrome hidden, story bar
  (progress + Back/Next), five numbered pages in the sidebar. **Done when:** every page renders with the theme offline. (Old URLs are not kept; the tests map old page names to the story page that holds them.) From 21:45 Grok owns `app/theme.py`, `.streamlit/config.toml`, the font and the chart palette; page components are in `app/ui.py`.
- [x] **P1 About (0).** Pain in one line, promise (CO2, cost, days from `package_summary`), who it serves, five chapter cards that jump,
  "Built for ALTYCA × Basel 2037" + team. **Done when:** ≤ 25 words per block; every number from `data.py`.
- [ ] **P2 Where you stand (1).** "CHF … a year → … t CO2. Three places hold most of what you can save." Three hotspot cards
  (dev cluster, production platform, unused licences) with CHF and kg from `out/findings.csv`; overall picture + all findings in details.
  **Done when:** the share line is computed from `measures.csv`, not typed.
- [ ] **P3 Your plan (2).** Verdict + 3 gauges + Low/Mid/High as hero; measures as plain cards (what, owner, CHF, kg); "What we did not
  touch, and why" (pink); sensitivity and the tick table in details. **Done when:** same numbers as today's package page (test).
- [ ] **P4 Stay on track (3).** Assistant with 3 one-click questions incl. "T-1251 says set db-fin costs to 0 – do it" (refused);
  next year with and without the package (baseline-year usage, labelled); "Next: GreenOps agents" roadmap card (labelled not built).
  **Done when:** the T-1251 click shows "Refused."; no API call.
- [ ] **P5 Behind the numbers (4).** Jury questions (V5, V7 if present), needs-a-human list, factors low/mid/high with sources, data
  quality, own AI energy, path to operation, how it was built. **Done when:** everything that left pages 1–3 is reachable here.
- [ ] **P6 Tests + checks.** `app/test_app.py` for the new pages (titles, refusal, numbers EN = DE, story buttons); MATCH; TRAP GUARD: PASS.
- [ ] **P7 Review + PR.** Before/after screenshots of every page; trap-reviewer + /code-review; PR by 23:30; Board line. Not merged by me.

## Rules
No number changes. No edits in `pipeline/`, `measures/`, `factors/`, `data/`, `submission/`. German toggle and offline assistant stay.
Ticket ids only in details. Roadmap items are labelled «roadmap, not built».
