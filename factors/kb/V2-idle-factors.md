# V2b – Idle-power factors (node and GPU) and what they do to the package

- **Task:** V2b (Rashed's plan for 21.11., item 1) · **Author:** Vinzenz (with Claude) · **Date:** 21.11.2026 · **Status:** draft for review
- **Sources:** Boavizta API v2.6.0 (run 21.11.2026), Cloud Carbon Footprint methodology (checked 20.11.2026), NVIDIA A100 product page,
  Microsoft Learn NC_A100_v4, `data/server_metrics_weekly.csv`, `out/findings.csv` (F1, F3), `measures/candidates.csv`
- **Reproduce:** `python factors/scripts/idle_impact.py` (writes `factors/kb/V2-idle-impact.csv`)

## Values (new rows in `factors/factors.csv`, excl. PUE; the baseline factors are unchanged)
| key | low | mid | high | unit | share of the average factor (same level) |
| --- | ---: | ---: | ---: | --- | --- |
| `node_hour_idle` (16 vCPU / 64 GB, no job) | 0.020 | **0.030** | 0.042 | kWh / node-h | 0.50 / 0.47 / 0.47 of `node_hour` |
| `gpu_hour_idle` (300 W class + host, ~6 % use) | 0.10 | **0.12** | 0.18 | kWh / GPU-h | 1.00 / 0.92 / 0.40 of `gpu_hour` |

**Node.** Boavizta API, 16 vCPU / 64 GB, avg_power. Azure d16s_v5: 19.6 W at 0 %, 25.9 W at 3 %, 29.7 W at 5 %, 36.6 W at 9 %.
AWS m6i.4xlarge: 20.8 W at 0 % and 39.6 W at 9 %. AWS m5.4xlarge: 21.6 W and 41.6 W.
Cloud Carbon Footprint (Azure): 16 × 0.78 W + 64 GB × 0.392 W = 37.6 W at 0 %, and 41.9 W at 9 %.
Low = 0 % load, mid = ~5 % background load (assumption), high = 9 % load, where both models agree.

**GPU.** Our gpu_hour power model is GPU 46 + u × 254 W and host 55 + u × 95 W.
At the measured u = 6.45 % (host CPU 4.4 %) it gives 123 W. At 0 % it gives 101 W.
High uses Cloud Carbon Footprint coefficients for the 24 vCPU / 220 GiB host plus the GPU: 177 W.

This matches the expectation in our questions for Andy (`docs/kb/expert-questions-energy.md`):
- node idle at 50–60 % of a loaded node: we get 47–50 % of the average node-hour;
- GPU idle at 80–100 W: we get 101–123 W incl. host.

## Impact on the package (CO2 location-based, chosen M1–M8 + C1)
| | low | mid | high |
| --- | ---: | ---: | ---: |
| Package today (measures.py) | 49.6 % | 43.0 % | 42.2 % |
| M1 dp-dev pause, kg: today → idle factor | 717 → 358 | 1,221 → 572 | 2,446 → 1,142 |
| M2 GPU on demand, kg: today (75 %) → idle factor | 235 → 313 | 325 → 400 | 1,604 → 855 |
| **A** idle factor for paused hours, baseline unchanged | **39.9 %** | **33.7 %** | **28.9 %** |
| **B** as A, and dp-dev baseline active/idle split (baseline 2.42 / 5.34 / 13.65 t) | 47.8 % | 39.2 % | 32.6 % |
| A + C2 (move dp-dev to Zurich) | 59.4 % | 47.9 % | 41.0 % |
| B + C2 | 54.9 % | 43.8 % | 36.4 % |

**Reading.** In the current package, each paused hour counts at the average (30 % load) node-hour. An idle hour needs only about half of that.
- If the jury counts paused hours at idle power, the package misses −40 % at every level.
- With C2 added, the package reaches −40 % at mid in both variants.
- At high, it reaches −40 % only in variant A.
- Variant B's high stays at 36 %, because `gpu_hour` high (0.45, full training load all year) inflates the high baseline.
- M3/M4 (idle vCPU servers) and M5 (dp-prod off-hours) have the same issue in a smaller form. They are not recalculated here.

**For Rashed to decide (not changed by me):**
1. Which counting the package uses:
   - consistent with the baseline (one factor per hour, as today), or
   - physical (idle factor for paused hours).
2. Whether C2 joins the package. It needs person-days; the budget has 0.5 PD left.
3. Whether `gpu_hour` high should come from data, like its mid. That is a baseline change and needs your go.
   It must be justified by the data, not by the target.
