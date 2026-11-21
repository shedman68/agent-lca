# Questions for Andy (energy / LCA expert)

- **Task:** R4 / V-support · **Author:** Rashed (with Claude) · **Date:** 21.11.2026 · **Status:** draft – answers to be added with date
- Context: Rashed, Hakim and Vinzenz worked together in the Sustainable Product Design team; Andy is the person for specific energy questions.
- Each question says why it matters for the jury and what we assume today (`factors/factors.csv`, `factors/sources.md`).

## Must ask (they change our numbers or our claim)
1. **Does pausing a cloud server really save the energy we claim?** We count energy = hours × factor and remove the paused hours
   (attributional). The provider may reuse the capacity. Is that claim acceptable in an LCA review for Scope 3, and how would you word it?
2. **Idle versus loaded power.** dp-dev runs at 8.7 % use, the GPU at ~6 %. We use one kWh factor per node-hour (assumes ~30 % load) and
   0.133 kWh per GPU-hour (300-watt class). What idle share of peak power would you use for a cloud node and for a GPU server?
3. **System boundary.** Our grid factors are life-cycle (incl. upstream), our energy per unit is operation only, and we leave out the
   embodied emissions of hardware. Is that mix defensible if we say so, or must we align?
4. **Swiss mix.** We use the consumption mix incl. imports, 0.090 kg CO2/kWh (range 0.057–0.098), not the production mix. Right choice for
   location-based Scope 3? Which source would you cite?
5. **Moving a workload from Frankfurt (0.330) to Zurich (0.090).** Can we claim the full difference under location-based accounting?
6. **Percent reduction under uncertainty.** Baseline CO2 is 2.9 / 6.2 / 15.4 t (low / mid / high). Our package gives −49 / −42 / −40 %.
   Is «at least −40 % across the range» the right way to state it?

## Good to ask (they strengthen the story)
7. **PUE** 1.14 / 1.21 / 1.32 by provider: apply to storage and network too? Any better public value for Azure Switzerland North and a Swiss hoster?
8. **AI tokens.** Our range is 0.000038–0.00052 kWh per 1,000 tokens (14×), split by model size and input/output. Which sources do you trust?
9. **SaaS seats** have no energy factor, so they carry zero CO2 in our baseline. Acceptable, or use a spend-based factor and flag it as low quality?
10. **Load shifting.** Annual average versus hourly factors: our hourly Swiss profile averages ~50 g, the annual factor is 90 g, so we use the
    profile for shape only. Is average-hourly good enough, or does it need marginal factors?
11. **Market-based view.** Every Swiss kWh carries a guarantee of origin and hosters claim «100 % renewable». How would you place that beside
    the location-based result without greenwashing?
12. **Data transfer:** 0.001–0.059 kWh/GB. Is a per-GB factor still state of the art, or should network be treated as fixed?
13. **Our own AI use this weekend:** tokens × token factor – is that a fair estimate, and what would you add (devices, cloud dev tools)?
