# V6 – Energy and CO2 of our own AI use during the sprint

- **Task:** V6 (required for the pitch) · **Author:** Vinzenz (with Claude) · **Date:** 21.11.2026 · **Status:** draft – Vinzenz + Hakim measured; **Rashed and Grok (Cursor) still missing**
- **Window:** Fri 20.11.2026 18:00 CET (17:00Z) until the time in each row of [`V6-tokens.csv`](V6-tokens.csv) (Vinzenz 10:50Z, Hakim 10:31Z on 21.11.)
- **Sources:** measured token counts with cache split in [`V6-tokens.csv`](V6-tokens.csv): Vinzenz from his Claude Code session logs, Hakim from GitHub issue #39 (his agent's recount).
  Factors from `factors/factors.csv`: `tokens_in/out_1000_large/small`, `cache_read_share` (new), `pue_default`, `grid_EU`.
- **Reproduce:** `python factors/scripts/own_ai.py` (writes [`V6-result.csv`](V6-result.csv))

## Method
Same token method as for the case's AI providers, so our own use is measured with the same yardstick.
The one addition is a factor for **cache reads**. Claude Code re-sends the whole conversation on every turn, and **97 % of our input tokens are cache reads**.
A cache read skips most of the compute that fresh input needs.

- input-equivalent = fresh + cache writes + cache reads × `cache_read_share`
- kWh = (input-equivalent / 1000 × input factor + output / 1000 × output factor) × PUE
- CO2 = kWh × `grid_EU`

`cache_read_share` = 0.05 / **0.10** / 1.0 (low / mid / high). It is an assumption, using price as a proxy for compute:
- low: Anthropic charges $0.20 for a cache read against $4 for fresh input on Opus 5.5 (0.05);
- mid: the general cache-read multiplier is about 0.1×;
- high: cache reads counted as fresh input (upper bound; Hakim's agent proposed this as the high case).

## Result so far (Vinzenz + Hakim)
| | Tokens in (of which cache reads) | Tokens out | kWh low / **mid** / high | kg CO2 low / **mid** / high |
| --- | ---: | ---: | --- | --- |
| Hakim | 94.5 M (92.4 M) | 0.35 M | 0.16 / **1.6** / 23.6 | 0.03 / **0.44** / 7.5 |
| Vinzenz | 44.1 M (41.6 M) | 0.26 M | 0.11 / **1.0** / 11.3 | 0.02 / **0.27** / 3.6 |
| **Total** | **138.6 M (134.0 M)** | **0.62 M** | **0.27 / 2.6 / 34.9** | **0.06 / 0.71 / 11.1** |
| Rashed | – | – | – | **missing** |
| Grok (Cursor) | – | – | – | **missing** |

The high case is 13× the mid. Almost all of that gap comes from how cache reads are counted, not from the token factors.

## Compared with the package
The package saves 1,438 / 2,664 / 6,496 kg CO2 a year (`measures/package_summary.csv`).
Our AI use so far equals **2.3 hours** of that saving at mid (0.3 h at low, 15 h at high).

## Pitch sentence (update when Rashed and Grok are in)
> "Building this with AI so far used about **2.6 kWh and 0.7 kg CO2**, about as much as a 10 km car trip. Our package saves the same amount in **under three hours** of operation."

The car comparison is an assumption: about 0.07 kg CO2 per car-km (not from the pipeline). Drop it if the jury might ask for a source.

## Limits (say them if asked)
- **Not yet complete:** Rashed's Claude Code and Cursor use and Grok's Cursor use are missing. They will raise the total.
- **Hakim's numbers are a claim from his agent** (issue #39), not re-measured by us. His first count (until 11:40 local) was *lower* (78 M in) than the recount (until 11:31, 94 M in), and the recount was used. Ask Hakim which sessions the difference comes from.
- **Grid:** `grid_EU`, the same as for the case's AI providers. Anthropic serves mainly from US data centres, and we have no sourced US factor (assumption).
- **Not included:** web searches (35), laptops, model training and embodied hardware. This is the same system boundary as the baseline.
- My Console usage screenshot (43.3 M in / 0.28 M out) agrees with my session logs (44.1 M / 0.26 M) within 2–7 %. The logs are used because only they show the cache split.
