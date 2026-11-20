# Energy and CO2 factors – sources and reasoning

Author: Vinzenz · 20 Nov 2026 · values in [`factors.csv`](factors.csv) · details and full calculations in [`kb/`](kb/README.md)

## How to read this
- **Every factor has a range.** *Mid* is our best estimate for the baseline year (Sep 2025 – Aug 2026). *Low* and *high* are the lowest and highest credible values we found, so they mark how wrong mid could reasonably be. We did not pick values to make the targets easier.
- **CO2 is location-based.** Each kWh is multiplied by the grid mix of the country where the data centre stands, not the company's own country.
- **PUE is applied once.** All energy factors exclude data-centre overhead. The pipeline then multiplies by `pue_default` wherever `applies_pue = yes`. Where a source already included overhead, we divided it out using that source's own PUE.
- **System boundary: every grid factor is life-cycle** at mid (since 21.11.2026; Germany was direct-only before). The one exception is Ireland's low value (SEAI, direct CO2). The basis is stated per row in `factors.csv`.
- **Result** (from `out/`, `verify_baseline.py` = MATCH): **35.8 MWh** (19.4–69.2) and **6.2 t CO2** (2.9–15.4) in the baseline year.
- **Which factors drive the uncertainty.** We moved one factor at a time to its high value and recorded the change in total CO2:

| Factor | Change in total CO2 at its high value |
| --- | --- |
| AI tokens | +21 % |
| Node-hours | +19 % |
| GPU | +18 % |
| Storage | +16 % |
| Grid Germany | +11 % |
| PUE | +9 % |

  Every other factor moves the total by less than 7 %. At their low values, the largest drops come from the node-hour factor (−18 %) and the Swiss grid mix (−11 %).

## Grid mix (kg CO2-eq per kWh)

**Switzerland – 0.090 (0.057–0.098), consumption mix.** We use the electricity *consumed* in Switzerland, including imports, rather than only what Swiss power plants *produce* (0.028–0.039). In winter and in dry springs Switzerland imports a large share of its power, mostly from Germany. That electricity is really used, so leaving it out would make Swiss servers look about three times cleaner than they are. For 2025, the year that covers most of the baseline, two independent methods agree: the electricity industry association VSE calculates 0.090 hourly (report of Jan 2026), and the federal LCA database BAFU:2026 gives 0.089. The range reflects the weather and the method. 2024 was a clean hydro year at 0.057. The University of Geneva's hourly import-tracing method gives 0.098. *Certainty: medium.* The method choice changes the result by 3×, the year by 1.6×.

**Germany – 0.330 (0.329–0.431).** Mid is Ember's 2025 life-cycle value, the same source and basis as Ireland's mid. Electricity Maps gives 0.329 for 2025 on a consumption basis; we saw that figure only in a search result. The high value is the BAFU:2026 life-cycle mix, which includes grid losses but has an older reference year. The national agency (Umweltbundesamt) gives 0.344, but it counts direct CO2 only, so we use it as a cross-check and not as a factor. We switched the mid from UBA to Ember after Rashed's review, so that all grid factors share one system boundary. *Certainty: good.*

**Ireland – 0.257 (0.255–0.320).** Mid is Ember 2025, the most recent annual value. The low value is from SEAI, the national energy agency (2023, cited by the EPA), and the high value is the BAFU:2026 life-cycle mix. We found no official SEAI value for 2024 or 2025. *Certainty: good.*

**Europe, mixed – 0.272 (0.210–0.319).** Used for the AI providers and the SaaS vendors, whose data centres sit anywhere in the interconnected European grid. Two independent sources agree: BAFU:2026 gives 0.272 for the ENTSO-E area and Ember 2025 gives 0.271 for Europe. The low value is EU-27 only (Ember); the high value is BAFU's Europe mix. *Certainty: good.*

## Energy per unit (kWh, excluding PUE)

**vCPU-hour – 0.0040 (0.0025–0.0056).** This is the power of one virtual CPU with its share of memory (4 GB) and the rest of the server. Two independent methods agree within about 30 %: the Boavizta model, which we ran live for Azure and AWS instance types, and the Cloud Carbon Footprint coefficients. The range is CPU load: low is 10 %, mid 30 %, high 50 %. Our servers run between about 9 % (dp-dev) and 50 %. We assume one Azure SQL vCore equals one vCPU. *Certainty: medium.*

**Node-hour – 0.064 (0.040–0.090).** One node has 16 vCPU and 64 GB RAM, so this is 16 × the vCPU value. Boavizta's direct result for that machine size gives the same numbers. This is the largest CO2 driver (47 %). dp-dev runs at about 9 % load, so its true value is closer to low. *Certainty: medium.*

**GPU-hour – 0.13 (0.10–0.45).** One NVIDIA A100-class GPU (300 W, per NVIDIA) plus its host server, sized after Azure's matching virtual machine (24 vCPU). The mid comes from our own data. Weekly GPU use in `server_metrics_weekly.csv` averages 9.2 % over the baseline year: 5–7 % in normal weeks and about 43 % in the four training weeks. That gives 133 W on average. We first assumed 20 % use (0.18), and lowered it after Rashed's review. Low is an idle GPU; high is full training load. The host share is our own derivation. *Certainty: medium.*

**Storage, GB-day – 0.00009 (0.000047–0.00017).** Drive power from Cloud Carbon Footprint (HDD 0.65 Wh, SSD 1.2 Wh per TB-hour), multiplied by the number of copies the cloud keeps: 3 for local, 6 for geo-redundant. Low is HDD with 3 copies, high is SSD with 6. The providers don't publish replication or how full their drives are, hence the wide range. *Certainty: medium–low.*

**Data transfer, GB – 0.01 (0.001–0.059), no PUE.** Published values span 60×. 0.001 counts only the extra energy for one more GB in the core network. 0.059 (Sustainable Web Design, from IEA data) shares all network energy over all traffic. Network energy is mostly fixed, so kWh per GB is a convention, not physics. Mid is our assumption. The impact is small: 0.5 MWh in total. *Certainty: low.*

**Power BI capacity-day – 0.77 (0.48–1.08), derived.** The capacity has 8 v-cores (Microsoft). 8 v-cores × 24 h × the vCPU value gives this figure. If only the 4 back-end cores do the work, the value halves. *Certainty: low.*

**CI runner-minute – 0.00013 (0.000083–0.00030), derived.** A standard runner has 2 vCPU (GitHub docs), so the value is 2 × the vCPU value ÷ 60. A direct Boavizta run for a 2-vCPU machine gives the same number. High assumes full load, because builds are CPU-heavy. *Certainty: medium–low.*

**AI, 1,000 tokens – 0.00017 (0.000038–0.00052).** No AI provider publishes energy per token. We modelled it from four studies: Epoch AI 2025, Jegham et al. 2025, ML.ENERGY 2026, and Google's measured 0.24 Wh per prompt (2025). Output tokens need about 6× more energy than input tokens, so we weighted by our own data: 5.6 input tokens per output token, and 97 % of tokens on large models. This factor causes the biggest uncertainty in the total (+21 % at high). **Split factors for the smaller-model measure:** `factors.csv` also gives input and output tokens separately for large and small models. Mid values in kWh per 1,000 tokens:

| | Input | Output |
| --- | --- | --- |
| Large model | 0.0001 | 0.0006 |
| Small model | 0.00002 | 0.00015 |

Small models therefore use about 4–5× less energy per token. The pipeline still uses the blended value; the split is for the measures calculator. *Certainty: low–medium.*

**AI subscription message – 0.0005 (0.00022–0.003).** Low is Google's measured median prompt without overhead (0.22 Wh). Mid is a typical work message with about 2,000 tokens of context and a 500-token answer. High is a long, document-grounded request (e.g. Copilot with files). *Certainty: medium for low and mid.*

**SaaS licence-month – not included.** No vendor publishes energy per licence and we found no credible average. Leaving SaaS out is explicit, so the energy baseline is a lower bound for SaaS.

## Data-centre efficiency (PUE)

**PUE – 1.21 (1.14–1.32).** PUE is the total power of a data centre divided by the power of its IT equipment. The pipeline uses one value, so we weighted each location's PUE by its share of our energy use:

| Location | Share of our energy | PUE (mid) | Basis |
| --- | --- | --- | --- |
| Azure Zurich | 46 % | 1.25 | Microsoft owns no Swiss data centres and rents space from colocation providers, so we use Swiss colocation values (federal energy office study, 2026) |
| Azure Frankfurt | 20 % | 1.16 | Microsoft, Europe (FY25) |
| AWS Dublin | 15 % | 1.10 | AWS Ireland fact sheet, 2025 |
| Swiss hoster | 8 % | 1.31 | Swiss colocation average (same 2026 study) |
| AI providers | 7 % | 1.15 | Hyperscaler fleet averages |

**How far to trust provider PUE:** not fully.
- The figures are self-reported and not audited.
- Fleet averages leave out rented colocation sites and new sites, which is exactly where the Swiss regions run.
- Annual averages hide partly loaded new sites.
- Industry averages are higher: 1.36 in the EU and 1.56 worldwide (Uptime Institute). Both figures are from secondary reports; we have not checked them in the originals. The high value of 1.32 therefore stays deliberately below the industry average, because our providers are large and efficient.

*Certainty: medium.*

## Bonus: market-based factor and hourly profile (V4)

**Market-based – 0.054 (0.011–0.284), not used for the targets.** This view counts the CO2 the suppliers claim through certificates.
- **Switzerland has no residual mix**, because every Swiss kWh must carry a guarantee of origin. We therefore use the Swiss supplier mix with guarantees of origin (0.028).
- **Frankfurt:** Microsoft's externally reviewed European market-based figure (0.063).
- **Dublin:** Amazon's audited market-to-location ratio (0.044, our derivation).
- **AI and SaaS:** the location mix, because no supplier data exists.

This gives about 1.9 t CO2 for the baseline year, compared with 6.2 t location-based. The location-based figure stays the official number. Details: [`kb/V4-market-based-and-hourly.md`](kb/V4-market-based-and-hourly.md).

**Hourly profile.** Built from Energy-Charts data for the baseline year, hour by hour, including Swiss imports.
- **Switzerland:** winter is 2–4× dirtier than summer, and nights (imports) are dirtier than afternoons and evenings.
- **Germany:** midday solar dominates in summer.
- **Use:** shape only. The Swiss level is lower than VSE's, so all totals keep the annual factors.
- **Flexible jobs on Swiss resources** could cut CO2 per kWh by roughly half by moving within their allowed window. This only helps together with auto-pause, and never inside protection windows. Interactive chart: [`kb/V4-hourly-co2.html`](kb/V4-hourly-co2.html).

## Choices the jury may question
- **Guarantees of origin.** IT tickets T-1030, T-1181, T-1203 and T-1227 say the hoster's electricity is backed by guarantees of origin, i.e. certificates for renewable power. We do **not** use them for location-based CO2, which would cut the hoster's CO2 by 3–6×. Certificates belong only in the optional market-based view, and only after a human has seen them.
- **One-off events stay in the baseline.** The AI script loop (T-1212) and the migration data transfer (T-1189) really used energy. They are never counted as recurring savings.
- **All factors are estimates.** Every value has a source with a date, or is labelled as an assumption. Full sources, calculations and a trap audit: [`kb/V1-grid-mix-factors.md`](kb/V1-grid-mix-factors.md), [`kb/V2-energy-per-unit-pue.md`](kb/V2-energy-per-unit-pue.md), [`kb/trap-check-V1-V2.md`](kb/trap-check-V1-V2.md).
