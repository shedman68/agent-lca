# Review follow-ups on V1 / V2 (from `docs/kb/reviews.md`)

- **Author:** Vinzenz (with Claude Code) · **Date:** 2026-11-21 · **Status:** final for review
- **Source of the requests:** Rashed's reviews of #5 and #8, listed in `docs/kb/reviews.md`

| # | Request | What changed in `factors/factors.csv` | Effect |
| --- | --- | --- | --- |
| 1 | Split token factors (review #8) | New rows `tokens_in_1000_large` 0.00001/**0.0001**/0.00018, `tokens_out_1000_large` 0.0002/**0.0006**/0.0025, `tokens_in_1000_small` 0.000002/**0.00002**/0.00005, `tokens_out_1000_small` 0.00004/**0.00015**/0.0005 kWh per 1k (excl. PUE, sources per row) | None on the baseline: the pipeline keeps the blended `tokens_1000`. Lets the measures calculator show the saving of "smaller model + caching" (≈ 4–5× less energy per token) |
| 2 | System boundary per grid factor (review #5) | `grid_DE` mid UBA 0.344 (direct only) → **Ember 2025 0.330 (life-cycle)**; low 0.329 (Electricity Maps, snippet only), high 0.431 unchanged. Every grid row now starts its notes with `BOUNDARY:`; all mids are life-cycle; only the IE low (SEAI) is direct | DE CO2 −4 % |
| 3 | GPU mid ~20 % vs data 5–7 % (review #8) | `gpu_hour` mid 0.18 → **0.13**, derived from `server_metrics_weekly.csv`: 52 weeks, mean `gpu_avg_pct` 9.2 % (median 6.5 %; ~43 % in the 4 training weeks) with the power model GPU 46 + u × 254 W plus host 55 + u × 95 W | GPU CO2 0.65 → 0.45 t |

## New baseline (pipeline → findings → verify → trap guard, 21.11.2026)
- **Energy:** 19.4 / **35.8** / 69.2 MWh (was 36.3 mid).
- **CO2 location-based:** 2.9 / **6.2** / 15.4 t (was 6.47 mid). The reduction is from the GPU (−0.20 t) and the Germany grid (−0.07 t).
- **Market-based (bonus):** about 1.9 t.
- **Sensitivity at the high value:** tokens +21 %, nodes +19 %, GPU +18 %, storage +16 %, Germany +11 %, PUE +9 %.
- **Checks:** `verify_baseline.py` MATCH · `trap_guard.py` PASS · `analysis/findings.py` CO2 kg mid 6197.5.
- **Updated to the new numbers:** `factors/sources.md`, [V1-grid-mix-factors.md](V1-grid-mix-factors.md), [V2-energy-per-unit-pue.md](V2-energy-per-unit-pue.md), [V4-market-based-and-hourly.md](V4-market-based-and-hourly.md), [V5-jury-questions.md](V5-jury-questions.md).

## Trap check
- **GPU mid:** the lower value reflects measured use and doesn't touch the protected quarterly training (T-1101). The high value still covers training weeks at full load.
- **Germany:** the factor change follows the review. It lowers CO2 by a small amount; the higher BAFU value stays as the high end.
