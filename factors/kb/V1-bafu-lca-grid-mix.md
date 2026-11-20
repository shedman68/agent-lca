# V1 – Grid mix factors from the FOEN life cycle inventory database (BAFU:2026)

- **Task:** V1 grid mix, location-based (also input for V3 write-up and V4 market-based factors)
- **Author:** Vinzenz (with Claude Code)
- **Date:** 2026-11-20
- **Status:** draft – values not yet written to `factors/factors.csv`

## Source
- FOEN / BAFU, *Life cycle inventory database BAFU:20XY*, version **BAFU:2026 v1**, impact method **IPCC 2021, GWP 100** (kg CO2-eq).
- Data product page: https://api.data-platform-stg.cloud.bafu.admin.ch/en/dataproduct-economy-consumption-lca (staging docs site)
- File: `https://data.bafu.admin.ch/download/economy-consumption/lca/v2026-11-06/data/economy-consumption_lca_lcia_results.zip`
  (loaded 2026-11-06, 48 MB zip, 561,509 rows; not committed to the repo because of its size)
- Values in the database are per MJ; converted with 1 kWh = 3.6 MJ.

## Result: kg CO2-eq per kWh (life-cycle, location-based)

Medium voltage (typical connection of a data centre); low voltage in brackets.

| Region | Consumption mix "at grid" (incl. imports) | Production mix | Dataset updated |
| --- | --- | --- | --- |
| Switzerland (CH) | **0.089** (0.097) | 0.028 (0.032) | 2021 / 2025 |
| Germany (DE) | **0.431** (0.451) | 0.465 (0.488) | 2025 |
| Ireland (IE) | **0.320** (0.342) | 0.336 (0.361) | 2025 |
| Europe (RER) | **0.319** (0.344) | 0.320 (0.342) | 2025 |
| ENTSO-E area | 0.272 (0.294) | 0.274 (0.292) | 2025 |

Process names used: `Electricity, medium voltage, at grid` and `Electricity, medium voltage, production XX, at grid`
(same with `low voltage`), location CH / DE / IE / RER / ENTSO-E.

## Recommendation for Switzerland
Use the **consumption mix (≈ 0.09 kg/kWh)**, not the production mix (≈ 0.03 kg/kWh).
The consumption mix is what is physically drawn from the Swiss grid, including imports (mainly from Germany in winter).
The production mix ignores those imports and would make the baseline look about 3× cleaner.

## Market-based variants for Switzerland (input for V4)
| Process (low voltage, CH) | kg CO2-eq/kWh |
| --- | --- |
| Certified electricity | 0.014 |
| Supply mix with guarantees of origin (GO) | 0.027 |
| Consumer mix GO | 0.032 |
| Residual mix | 0.046 |

## Limits – what this source does not give us
- **No ranges.** One value per process. Proposed range until we have a second source:
  low = production mix, mid = medium-voltage consumption mix, high = low-voltage consumption mix. Label as «assumption».
- **Life-cycle factors** (include plant construction, fuel chain, grid losses). Operational-only factors (EEA, IEA, Electricity Maps
  direct) are lower. State this choice in `factors/sources.md` (V3).
- **The CH consumption mix dataset was last updated in 2021**; the production mix and the other countries in 2025.
- **Not useful for V2:** no energy per vCPU-hour, GPU-hour, storage, transfer, tokens, CI minutes and no PUE.
  The database only has embodied emissions per device (e.g. server ≈ 430 kg CO2-eq, rack server ≈ 500, network equipment ≈ 140).
- **No hourly profile** (needed for V4); use UNIGE (CH) and ENTSO-E / Electricity Maps (DE).

## Next
1. Find a second source per country (UNIGE, ENTSO-E, EEA) to set low/high.
2. Fill the grid rows in `factors/factors.csv` with source and date.
3. Start V2 sources: Cloud Carbon Footprint, ML.ENERGY, Uptime Institute PUE survey, provider reports.

## How to reproduce
Filter scripts are kept outside the repo (`C:\Users\vinze\bafu-scripts\`): read the CSV, keep `impact_method == "IPCC 2021"`,
`impact_category == "GWP 100"`, select the process names above and multiply `value` by 3.6.
