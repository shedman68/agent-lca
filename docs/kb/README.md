# docs/kb – knowledge base for Rashed's tasks (lead)

Every task output for R0–R7 is saved here as a Markdown file `<task-id>-<short-name>.md`.
Each file starts with task, author, date, status (draft / final) and sources.
Machine-readable outputs stay where the code reads them (`out/`, `measures/measures.csv`, `submission/`); the files here explain them.

| File | Task | Status |
| --- | --- | --- |
| [decisions.md](decisions.md) | Decision log for the whole team (newest on top) | living |
| [reviews.md](reviews.md) | Pull request reviews and open follow-ups per person | living |
| [R0-case-brief.md](R0-case-brief.md) | R0 case, jury, schedule, rights, example answers, first analysis | final |
| [R0-baseline.md](R0-baseline.md) | R0 data cleaning, verified baseline, trap guard | done |
| [R0-team-setup.md](R0-team-setup.md) | R0 team workflow, local setup, Claude Code setup (skills, reviewer, hooks, /goal) | final |
| [BUILD-overnight-brief.md](BUILD-overnight-brief.md) | Brief for an autonomous overnight agent: app v2 (package page, CO2 first, assistant, bonus) | final |
| [QA-01-review-sat-0200.md](QA-01-review-sat-0200.md) | Independent QA against the jury criteria: 35 % complete, gaps, priorities | final |
| [G-app-v2.md](G-app-v2.md) | G1–G5 app v2: package, findings, assistant, submission drafts, next-year page (M1–M4). 24-node forecast not calculated | draft |
| [G6-hardening.md](G6-hardening.md) | G6 robustness tests, demo script, offline page screenshots | draft |
| [R0-vscode-prompt.md](R0-vscode-prompt.md) | R0 hand-over prompt for Claude Code in VS Code, with best practices | final |
| R1-measures.md | R1 measures calculator | open |
| R2-package.md | R2 chosen package vs target and budget | open |
| [R4-needs-a-human.md](R4-needs-a-human.md) | R4 needs-a-human list: protection windows, planted text, contradictions, one-offs | draft |
| [R6-demo-script.md](R6-demo-script.md) | R6 five-minute click script (overall picture, one finding, package, refused edge, own AI) | draft |
| R6-pitch.md | R6 pitch script | open |
| [R7-submission-pack.md](R7-submission-pack.md) | G7 index of files to submit, line check against out/ and measures/, what Rashed still decides before 15:00 | draft |
| [R8-UAT-checklist.md](R8-UAT-checklist.md) | Phone UAT for the mentor demo: pages, figures from out/ and measures/, traps, go-live | draft |
| [G9-mentor-polish.md](G9-mentor-polish.md) | G9 phone polish on top of #65: signs, plain labels, narrow-screen layout | draft |
| [G8-template-gaps.md](G8-template-gaps.md) | G8 baseline template: cost low = mid = high, allocation text rule, T-1261 note | draft |
| handoff-vscode-to-cloud.md | Handoff VS Code → cloud: R1 decisions, review findings #26/#29, next steps | final |
| [R9-plan.md](R9-plan.md) | R9 plan: app v2, one user story for the pitch (six steps, story mode) | done (merged in #71; review follow-ups in R10) |
| [R9-handover-grok.md](R9-handover-grok.md) | R9 handover: what Claude had built, what Grok added per page, what is left | done (merged in #71) |
| [R10-polish.md](R10-polish.md) | R10 final polish of app v2: checklist, checks, screenshots in `screenshots/r10/` | done, PR open |

Other knowledge bases: [analysis/kb](../../analysis/kb/README.md) (Hakim) · [factors/kb](../../factors/kb/README.md) (Vinzenz).
