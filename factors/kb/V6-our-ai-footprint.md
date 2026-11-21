# V6 – Energy and CO2 of our own AI use during the sprint

- **Task:** V6 (required for the pitch) · **Author:** Vinzenz (with Claude) · **Date:** 21.11.2026 · **Status:** draft for the 14:30 freeze – all four counted (Vinzenz, Hakim, Rashed, Grok); final recounts at 14:15
- **Window:** Fri 20.11.2026 18:00 CET (17:00Z) until the time in each row of [`V6-tokens.csv`](V6-tokens.csv) (Vinzenz 12:16Z, Hakim 10:31Z, Rashed 12:07Z / 12:15Z, Grok ~12:00Z on 21.11.; final recounts at 14:15)
- **Sources:** measured token counts with cache split in [`V6-tokens.csv`](V6-tokens.csv): Vinzenz from his Claude Code session logs; Hakim from GitHub issue #39 (his agent's recount); Rashed and Grok from Rashed's Claude in the Slack DM to Vinzenz (21.11. 13:01–13:15).
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

## Result (all four, as of ~13:15)
| | Tokens in (of which cache reads) | Tokens out | kWh low / **mid** / high | kg CO2 low / **mid** / high |
| --- | ---: | ---: | --- | --- |
| Rashed (2 Claude Code cloud sessions) | 279.8 M (273.4 M) | 0.55 M | 0.35 / **4.5** / 68.3 | 0.07 / **1.22** / 21.8 |
| Hakim | 94.5 M (92.4 M) | 0.35 M | 0.16 / **1.6** / 23.6 | 0.03 / **0.44** / 7.5 |
| Vinzenz | 52.2 M (49.5 M) | 0.30 M | 0.13 / **1.1** / 13.4 | 0.03 / **0.31** / 4.3 |
| Grok (Cursor, split assumed) | 28.9 M (28.2 M) | 0.08 M | 0.04 / **0.5** / 7.1 | 0.01 / **0.13** / 2.3 |
| **Total** | **455 M (444 M)** | **1.29 M** | **0.68 / 7.7 / 112** | **0.14 / 2.1 / 36** |

The high case is about 15× the mid. Almost all of that gap comes from how cache reads are counted (`cache_read_share`), not from the token factors.

## Compared with the package
The package saves 1,438 / 2,664 / 6,496 kg CO2 a year (`measures/package_summary.csv`).
Our AI use for the sprint equals **about 7 hours** of that saving at mid (0.9 h at low, 2 days at high).

## Pitch sentence
> "Building this with four AI agents used about **8 kWh and 2 kg CO2**, about a 30 km car trip. Our package saves that in **about seven hours** of operation."

The car comparison is an assumption: about 0.07 kg CO2 per car-km (not from the pipeline). Drop it if the jury might ask for a source.

## Limits (say them if asked)
- **Not included:** Rashed's Friday VS Code session on his Mac (not countable from the cloud). Add more people or sessions as rows in `V6-tokens.csv` only; `V6-result.csv` keeps its `person` / `TOTAL` layout, which the app's Next year page reads.
- **Grok's split is assumed.** Cursor shows only a total (29 M) with no input / output / cache split and no model. We split it by the measured shares of our Claude Code rows (97.2 % cache reads, 2.6 % cache writes, 0.3 % output) and assume a large model.
- **Rashed's numbers are claims from his agent**, not re-measured by us. The chief-of-staff session values are rounded to 0.01 M; it ran partly on Fable 5.2 overnight, which we count as a large model.
- **Hakim's numbers are a claim from his agent** (issue #39), not re-measured by us. The gap between his two counts (78 M vs 94 M in) is explained (#agent-updates, 21.11. 12:48): the same growing logs were counted twice, and his long main session re-reads its whole context from the cache on every response (+16 M cache reads over 32 responses). The time labels were mixed: "11:40" was local time, "10:31Z" UTC. By 12:47 he was at 105.8 M in. The final recount comes at 14:15.
- **Grid:** `grid_EU`, the same as for the case's AI providers. Anthropic serves mainly from US data centres, and we have no sourced US factor (assumption).
- **Not included:** web searches (35), laptops, model training and embodied hardware. This is the same system boundary as the baseline.
- My Console usage screenshot (43.3 M in / 0.28 M out, morning of 21.11.) agreed with my session logs at that time (44.1 M / 0.26 M) within 2–7 %. The logs are used because only they show the cache split.
