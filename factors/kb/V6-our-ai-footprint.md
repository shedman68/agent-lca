# V6 – Energy and CO2 of our own AI use during the sprint

- **Task:** V6 (required for the pitch) · **Author:** Vinzenz (with Claude) · **Date:** 21.11.2026 · **Status:** DRAFT – only Vinzenz's tokens so far; Rashed, Hakim and Grok (Cursor) still missing
- **Window:** Fri 20.11.2026 18:00 – Sun 22.11.2026 (sprint)
- **Sources:** token totals in [`V6-tokens.csv`](V6-tokens.csv), one row per person, tool and model class.
  Factors from `factors/factors.csv`: `tokens_in/out_1000_large/small`, `pue_default` and `grid_EU`.
- **Reproduce:** `python factors/scripts/own_ai.py`

## Method
kWh = input tokens / 1000 × input factor + output tokens / 1000 × output factor, by model class (large / small), × PUE.
CO2 = kWh × grid factor. This is the same token method we use for the case's AI providers, so our own use is measured with the same yardstick.

## Result so far (Vinzenz only: 43.3M input, 0.28M output tokens, 35 web searches)
| | low | mid | high |
| --- | ---: | ---: | ---: |
| Energy, kWh | 0.55 | 5.3 | 11.0 |
| CO2, kg | 0.12 | 1.45 | 3.5 |

Input tokens give about 80 % of the mid value.

| Person | Tool | Tokens in | Tokens out | Status |
| --- | --- | ---: | ---: | --- |
| Vinzenz | Claude Code (Opus 5.5, Haiku 5.5) | 43,309,083 | 284,662 | in (Console screenshot 21.11.) |
| Rashed | Claude Code + Cursor | – | – | **missing** |
| Hakim | Claude Code | – | – | **missing** |
| Grok | Cursor usage page | – | – | **missing** |

## Limits (say them in the pitch)
- **Cached input counts as fresh input.** Claude Code re-sends the conversation each turn, and most of it is read from the prompt cache, which needs much less compute.
  So this is an **upper bound**. A cached/uncached split would lower the mid.
- **Grid factor:** we use `grid_EU`, the same as for the case's AI providers. Anthropic and xAI run mainly in US data centres, and we have no sourced US factor (assumption).
- **Not included:** web searches (35, negligible), our laptops, training of the models, and embodied hardware. This is the same system boundary as the baseline.
- The Haiku share is read off the Console chart (~1.2M tokens, ±0.5M). Its effect is below 1 %.

## Pitch sentence (fill in when all totals are in)
> "Building this with AI cost about **[X] kWh and [Y] kg CO2** (range [low]–[high]). That is what our package saves in about **[Z] minutes** of a normal year."

Z = our kg / package CO2 saving per year (2,664 kg mid, `measures/package_summary.csv`) × 525,600 minutes.
With Vinzenz alone: 1.45 / 2,664 × 525,600 ≈ **4.8 hours**. So the sprint's own AI use pays back within the first day of the package running.
