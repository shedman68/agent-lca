# factors/kb – knowledge base for energy and CO2 factors (Vinzenz)

Every task output for V1–V5 is saved here as a Markdown file: `<task-id>-<short-name>.md`.
Each file starts with task, author, date, status (draft / final) and sources.
The machine-readable values stay in `factors/factors.csv` (read by the pipeline); the files here explain and source them.

| File | Task | Status |
| --- | --- | --- |
| [template-row-edits.md](template-row-edits.md) | Row edits for the submission files, ready to paste ([template-row-edits.csv](template-row-edits.csv)) | final for Rashed |
| [V6-our-ai-footprint.md](V6-our-ai-footprint.md) | V6 energy and CO2 of our own AI use (tokens in [V6-tokens.csv](V6-tokens.csv), result [V6-result.csv](V6-result.csv)) | draft – Rashed and Grok missing |
| [template-factor-check.md](template-factor-check.md) | Check of the factor rows in the submission template (PR #29) | done |
| [V2-idle-factors.md](V2-idle-factors.md) | V2b idle-power factors (node, GPU) + package impact ([V2-idle-impact.csv](V2-idle-impact.csv)) | draft for review |
| [review-followups-V1-V2.md](review-followups-V1-V2.md) | Review follow-ups: token split, grid system boundary, GPU mid from data | final for review |
| [V4-market-based-and-hourly.md](V4-market-based-and-hourly.md) | V4 bonus: market-based factor, hourly CO2 CH/DE, job shifting | final for review |
| [V4-hourly-co2.html](V4-hourly-co2.html) | V4 interactive heatmaps + job table (open in a browser) | final for review |
| [V5-jury-questions.md](V5-jury-questions.md) | V5 jury questions + answers, Q3 on −40 % at high factors (21.11.) | final (Q3 per counting decision 12:15) |
| [../sources.md](../sources.md) | V3 write-up for the jury: one paragraph per factor, sensitivity, PUE trust | final for review |
| [trap-check-V1-V2.md](trap-check-V1-V2.md) | Trap audit of V1 + V2 (manipulative text, one-offs, GOs, duplicates) | done |
| [V2-energy-per-unit-pue.md](V2-energy-per-unit-pue.md) | V2 energy per unit and PUE – values, derivations, sources | final for review |
| [V1-grid-mix-factors.md](V1-grid-mix-factors.md) | V1 grid mix – final values, sources, CH recommendation | final for review |
| [V1-bafu-lca-grid-mix.md](V1-bafu-lca-grid-mix.md) | V1 grid mix – FOEN BAFU:2026 LCA data (background) | done |
