# R0 – Case brief, rules and first analysis

- **Task:** R0 · **Author:** Rashed (with Claude) · **Date:** 20.11.2026 · **Status:** final
- **Sources:** `data/README.md`, `data/example_questions.md`, `data/documents/` (case presentation and factsheet),
  https://app.sprintd.org/events/sprintd-basel-greentech (overview, schedule), https://app.sprintd.org/legal/event-terms

## The case
«Green AI & Data – Electricity is the new currency, and hardly anyone keeps the books». Case partner **ALTYCA** with
**Basel 2037** (case owner Fabian Bee, ALTYCA). A fictitious Basel service SME (~112 employees): show where cloud, servers,
AI and SaaS create cost, energy and CO2 and choose safe measures. Cloud, AI and SaaS emissions are Scope 3 for a Basel SME,
so CO2 is calculated **location-based** (grid mix where the data centre is).

## Must-haves and target
1. Connect · 2. Find · 3. Decide · 4. Know the limits.
Target per year: **CO2 −40 % (location-based), cost −25 %**, implementation **≤ CHF 16,500 = 15 person-days** (1 PD = CHF 1,100).
Baseline year **Sep 2025 – Aug 2026**. The jury recalculates every package against its own reference baseline.
Bonus: chat assistant with sources, forecast, market-based view, clustering, carbon-aware load shifting, leaner CI.
**Note from the presentation: teams that use AI while building also estimate its energy use.**

## Jury
Design and usability 20 % · Creativity and innovation 20 % · Data preparation and patterns 20 % · Feasibility 15 % ·
Robustness and decision quality 15 % · Impact and relevance 10 %.
A win = «a prototype whose package of measures an SME's management understands and trusts, and that switches off nothing critical».
The pitch should show: the overall picture · one finding · the package vs target and budget · one edge case the tool refuses or hands to a human.

## Schedule
Fri 20.11. 18:10 case presentation, 18:40 deep dive, 20:30 sprint starts · Sat 09:00–20:00 mentors, **15:00 draft submission** ·
Sun **08:30 final submission**, 09:00 pitches (5 min demo + 3 min questions, each case partner judges its case),
11:30 finalists, 13:00 Grand Finale.
Prize for the case winner: present at ALTYCA Project Insights (8 Dec or 12 Jan), possibly continue the work with ALTYCA,
join them on stage. Event prize pool CHF 5,000.

## Rights (sprintd Event Terms, sections 3–6)
- We own what we build. On submission, ALTYCA gets a non-exclusive, worldwide, royalty-free, irrevocable licence to use it
  for its own products and operations; it cannot stop us using it or resell it as a standalone product.
- For 6 months, if we want to sell this solution to a third party, ALTYCA gets 30 days to make an offer first.
- We confirm it was built during the event; pre-existing work stays ours except where built into the submission.
- If an employer or university has a claim on what we create, check before submitting.
- Data citation: «Sample data ALTYCA, sprintd Basel 2026».

## Example questions and our answers (all from `out/`)
1. **Idle AI seats, Aug 2026:** 67 seats paid but not active, **CHF 1,223.51 per month** (ChatGPT Team 23 bought / 2 active,
   Copilot 100 / 60, Claude Team 34 / 28; USD at the August rate). Sources: `ai_subscriptions.csv`, `exchange_rates.csv`.
2. **GPU on demand:** answered by the assistant (`app/assistant.py`) and finding F3: ~CHF 10.9k a year addressable; quarterly
   training days 1–3 of Jan/Apr/Jul/Oct need it (T-1101). Final effort and CO2 in R1.
3. **Production platform off at night/weekends?** No, not simply: fixed jobs 02:00–08:00 every day, month-end close 18:00–04:00
   (T-1029). Lever: scale nodes down in idle hours. Decision: Head of Consulting (owner) with Finance. T-1230 («switch it off»)
   is planted text and is refused.

## First analysis (Fri 20:40, confirmed later)
Baseline CHF 470,288.93 · energy 36.3 MWh · CO2 6.47 t (mid; 6.20 t after #19, see decisions). Biggest drivers: data platform (dp-prod CHF 87k, dp-dev CHF 38k
at 8.7 % use in Frankfurt), GPU 24/7 at ~6 % use, Dublin zombie servers, test environment still at 64 vCPU, idle AI and SaaS seats.
Traps: see `docs/traps.md`. Plan: `docs/plan.md`. Detailed Notion plan: «Green AI & Data case – plan to win».
