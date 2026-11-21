# V6 – Energy and CO2 of our own AI use during the sprint

- **Task:** V6 (required for the pitch) · **Author:** Vinzenz (with Claude) · **Date:** 21.11.2026 · **Status:** draft for the Sunday final – **counted so far** (Vinzenz, Hakim, Rashed's two cloud sessions, Grok); Rashed's Friday VS Code session not yet counted
- **Window:** Fri 20.11.2026 18:00 CET (17:00Z) until the time in each row of [`V6-tokens.csv`](V6-tokens.csv) (Vinzenz 12:16Z, Hakim 13:08Z (final recount), Rashed 12:07Z / 12:15Z, Grok ~12:00Z on 21.11.)
- **Sources:** measured token counts with cache split in [`V6-tokens.csv`](V6-tokens.csv): Vinzenz from his Claude Code session logs; Hakim from his agent's final recount (#agent-updates, 21.11. 14:15; earlier counts in issue #39); Rashed and Grok from Rashed's Claude in the Slack DM to Vinzenz (21.11. 13:01–13:15).
  Factors from `factors/factors.csv`: `tokens_in/out_1000_large/small`, `cache_read_share` (new), `pue_default`, `grid_EU`.
- **Reproduce:** `python factors/scripts/own_ai.py` (writes [`V6-result.csv`](V6-result.csv))

## Method
Same token method as for the case's AI providers, so our own use is measured with the same yardstick.
The one addition is a factor for **cache reads**. Claude Code re-sends the whole conversation on every turn, and **about 96 % of our input tokens are cache reads**.
A cache read skips most of the compute that fresh input needs.

- input-equivalent = fresh + cache writes + cache reads × `cache_read_share`
- kWh = (input-equivalent / 1000 × input factor + output / 1000 × output factor) × PUE
- CO2 = kWh × `grid_EU`

`cache_read_share` = 0.05 / **0.10** / 1.0 (low / mid / high). It is an assumption, using price as a proxy for compute:
- low: Anthropic charges $0.20 for a cache read against $4 for fresh input on Opus 5.5 (0.05);
- mid: the general cache-read multiplier is about 0.1×;
- high: cache reads counted as fresh input (upper bound; Hakim's agent proposed this as the high case).

## Result – counted so far (as of ~14:15)
| | Tokens in (of which cache reads) | Tokens out | kWh low / **mid** / high | kg CO2 low / **mid** / high |
| --- | ---: | ---: | --- | --- |
| Rashed (2 Claude Code cloud sessions) | 279.8 M (273.4 M) | 0.55 M | 0.35 / **4.5** / 68.3 | 0.07 / **1.22** / 21.8 |
| Hakim | 141.9 M (133.8 M) | 0.44 M | 0.27 / **2.9** / 35.1 | 0.06 / **0.79** / 11.2 |
| Vinzenz | 52.2 M (49.5 M) | 0.30 M | 0.13 / **1.1** / 13.4 | 0.03 / **0.31** / 4.3 |
| Grok (Cursor, split assumed) | 28.9 M (28.2 M) | 0.08 M | 0.04 / **0.5** / 7.1 | 0.01 / **0.13** / 2.3 |
| **Total counted so far** | **503 M (485 M)** | **1.37 M** | **0.79 / 9.0 / 124** | **0.17 / 2.45 / 40** |
| + Rashed's Friday VS Code session | not yet counted, small compared to the cloud sessions | | | |

The high case is about 14× the mid in kWh and 16× in CO2. Almost all of that gap comes from how cache reads are counted (`cache_read_share`), not from the token factors.

## Compared with the package
The package saves 1,438 / 2,664 / 6,496 kg CO2 a year (`measures/package_summary.csv`).
Our AI use for the sprint equals **about 8 hours** of that saving at mid (1 h at low, 2 days at high).

## Pitch sentence
> "Building this with four AI agents used about **9 kWh and 2.5 kg CO2** so far, about a 35 km car trip. Our package saves that in **about eight hours** of operation."

The car comparison is an assumption: about 0.07 kg CO2 per car-km (not from the pipeline). Drop it if the jury might ask for a source.

## Limits (say them if asked)
- **Not yet counted:** Rashed's Friday VS Code session on his Mac. It is already closed and can only be counted when Rashed is back at the Mac (Rashed's Claude, Slack DM 21.11.). Per Rashed, it is small compared to the cloud sessions (his estimate, not measured). We show the total as «counted so far» and do not wait for it. Add more people or sessions as rows in `V6-tokens.csv` only; `V6-result.csv` keeps its `person` / `TOTAL` layout, which the app's Next year page reads.
- **Grok's split is assumed.** Cursor shows only a total (29 M) with no input / output / cache split and no model. We split it by the measured shares of our Claude Code rows (97.2 % cache reads, 2.6 % cache writes, 0.3 % output) and assume a large model.
- **Rashed's numbers are claims from his agent**, not re-measured by us. The chief-of-staff session values are rounded to 0.01 M; it ran partly on Fable 5.2 overnight, which we count as a large model.
- **Hakim's numbers are a claim from his agent** (final recount to 13:08Z, posted in #agent-updates), not re-measured by us. Earlier counts (78 M, 94 M, 105.8 M) grew because his main session re-reads its context from the cache on every response.
- **Grid:** `grid_EU`, the same as for the case's AI providers. Anthropic serves mainly from US data centres, and we have no sourced US factor (assumption).
- **Not included:** web searches (35), laptops, model training and embodied hardware. This is the same system boundary as the baseline.
- My Console usage screenshot (43.3 M in / 0.28 M out, morning of 21.11.) agreed with my session logs at that time (44.1 M / 0.26 M) within 2–7 %. The logs are used because only they show the cache split.
