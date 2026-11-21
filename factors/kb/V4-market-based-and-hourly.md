# V4 (bonus) – Market-based factor and hourly CO2 profile

- **Task:** V4 market-based factors (guarantees of origin) and hourly CO2 profile for CH and DE, for shifting flexible jobs
- **Author:** Vinzenz (with Claude Code; market-based research by a research agent, numbers checked)
- **Date:** 2026-11-21
- **Status:** final for review
- **Files:**
  - `factors/factors.csv`, row `grid_market_based`: bonus, not used by the pipeline
  - `factors/hourly_co2_profile.csv`: month × hour profile for CH and DE
  - [V4-hourly-co2.html](V4-hourly-co2.html): interactive heatmaps and job table, open in a browser
  - [V4-job-shift.csv](V4-job-shift.csv): job-shift results
  - `factors/scripts/`: scripts to reproduce

## 1. Market-based factor (bonus template row `grid_mix_market_based`)

**Result: 0.011 / 0.054 / 0.284 kg CO2/kWh.** Indicative market-based CO2 for the baseline year: **≈ 1.9 t** (0.4–9.9), compared with 6.2 t location-based.

| Location | Share of kWh | Low | Mid | High |
| --- | --- | --- | --- | --- |
| Switzerland (Azure, AWS, hoster) | 58 % | 0.011 certified renewable GO | **0.028** Swiss supplier mix with GOs (BAFU:2026) | 0.090 physical consumption mix |
| Azure Frankfurt | 20 % | 0.011 | **0.063** Microsoft FY25 EMEA market-based (reviewed fact sheet, our division) | 0.725 AIB residual DE |
| AWS Dublin | 15 % | 0.011 | **0.044** Amazon audited market/location ratio × grid_IE (our derivation) | 0.366 AIB residual IE |
| AI providers + SaaS (EU) | 7 % | 0.011 | **0.272** no supplier data → location-based EU | 0.452 AIB average residual |

**Key facts:**
- **Switzerland has no residual mix.** AIB 2024: "not applicable for Austria and Switzerland in which all power consumption is tracked with GOs".
  Every Swiss kWh carries a guarantee of origin, so the hoster tickets saying "guarantees of origin confirmed" (T-1030, T-1181, T-1203, T-1227) say almost nothing on their own.
  What matters is which GOs: hydro, nuclear or imported. **Low (0.011) only after a human has seen the certificates.**
- **Providers are moving away from cheap certificates.** Microsoft stopped buying unbundled certificates in Feb 2025, and its market-based Scope 2 rose from 0.26 Mt to 2.7 Mt (FY24 → FY25).
  AWS is phasing them out too. Its carbon footprint tool was deprecated on 30.06.2026, so baseline-year data must come from the new "AWS Sustainability" service.
- **The basis is mixed.** AIB residual mixes are direct CO2 only; our location-based factors are life-cycle. The high values therefore understate a full life-cycle view. Stated, not adjusted.
- **Location-based stays the official CO2.** The market-based value is shown for comparison only. It is not used for the −40 % target.

## 2. Hourly CO2 profile, CH and DE (Sep 2025 – Aug 2026)

**Data:** Energy-Charts API (Fraunhofer ISE), 8,760 hours, no gaps:
- `co2eq` for DE, CH, FR, IT and AT
- CH production by type
- physical cross-border flows

**Switzerland = consumption mix**, built hour by hour the same way as VSE: (CH generation × CH intensity + imports × intensity of the exporting country) / (generation + imports).

| | Mean (time-weighted) | Range of month × hour means |
| --- | --- | --- |
| CH consumption mix | 50 g/kWh | 13 – 137 |
| CH production mix | 18 g/kWh | – |
| DE | 377 g/kWh | 158 – 518 |

**Calibration – use the shape, not the level.** Our CH annual mean (50 g) is well below VSE (90 g) and BAFU (89 g).
- Energy-Charts uses lower emission factors: its CH production mix is 18 g, against BAFU's 28–32 g.
- Our simple flow method counts transit flows through Switzerland.

The hourly series is therefore used **only for the timing** (which hours and months are cleaner). All CO2 totals keep the annual factors from V1.

**Patterns:**
- **Switzerland:** winter is 2–4× dirtier than summer (monthly mean 98 g in Jan vs 26 g in Jun), and the import share rises to ~43 % in Dec–Jan. Nights are the dirtiest hours (imports from Germany); late afternoon and evening are cleanest. The daily swing is 17–75 g.
- **Germany:** midday solar dominates from March to September, with a daily swing of up to 342 g in May. In winter the swing is small (69–107 g).

## 3. Shifting flexible jobs (`data/extra/data_platform_jobs.csv`)

The best start hour is chosen **inside each job's own allowed window**, using the average CO2 per kWh over the job's duration.

| Job | Resource | Window | Now | Best | g/kWh now → best | Change |
| --- | --- | --- | --- | --- | --- | --- |
| Log rotation | logs (CH) | within 24 h | 04:00 | 21:00 | 66 → 27 | −58 % |
| Data cleansing | dp-prod (CH) | within the week | 03:00 | 16:00 | 64 → 29 | −54 % |
| Catalogue scan | dp-prod (CH) | within the week | 05:00 | 21:00 | 59 → 27 | −54 % |
| Archiving | st-archive (CH) | within the month | 04:00 | 16:00 | 57 → 29 | −48 % |
| Cost export | dp-prod (CH) | within 24 h | 06:00 | 21:00 | 46 → 27 | −40 % |
| Dev smoke test | dp-dev (DE) | working day 08–18 | 10:00 | 13:00 | 284 → 252 | −11 % |
| Test data refresh | dp-dev (DE) | before next working day | 17:00 | varies | 379 → 356 | −6 % |
| Embedding update | dp-dev (DE) | within 24 h | 12:00 | 13:00 | 253 → 252 | −1 % |

**Not moved:**
- Fixed jobs: nightly ETL, morning reports, Power BI refresh, backup window, month-end and year-end close.
- Quarterly model training: protected window T-1053, human decision.
- The AI text analysis: no hourly profile exists for "EU mixed".

**Caveats:**
1. **Moving a job only saves CO2 if the cluster draws less power when the job is not running.** dp-prod and dp-dev run around the clock today, so shifting is a *bonus on top of* a schedule or auto-pause measure. It saves nothing alone.
2. **Protection windows:** dp-prod jobs keep their current start on the last 3 working days of each month and at year-end close (T-1029). dp-dev keeps days 1–3 of each quarter free for training (T-1053).
3. **These are relative reductions per kWh of the job.** The kWh per job is not in the data (node count per job unknown), so no absolute saving is claimed here. That belongs in Rashed's measures calculator.
4. The CH percentages rest on the hourly shape, which has the calibration gap described above. Treat them as "roughly half", not as exact values.

## Trap check
- **Guarantees of origin** are not used for location-based CO2. For market-based, the GO tickets are claims only, and the low value requires a human to see the certificates.
- **No protected resource is switched off or moved** into its protection window; quarterly training is excluded.
- **`time_window` used as a constraint:** it is a scheduler field describing when a job may run, not an instruction to an AI.
- **Web sources** were cross-checked. The AIB 2025 country values (DE, IE) were not extracted, because the file was too large; 2024 values are used and labelled.
- **Baseline unchanged:** `verify_baseline.py` = MATCH; the new `grid_market_based` row is ignored by the pipeline.

## Sources
1. Energy-Charts API, Fraunhofer ISE – https://api.energy-charts.info (`co2eq`, `public_power`, `cbpf`; downloaded 20–21.11.2026)
2. AIB, European Residual Mixes 2024 v1.1 (11.08.2025) – https://www.aib-net.org/sites/default/files/assets/eecs/Residual%20Mix/2024_Final%20_Residual%20mix%20calculation%20results_11082025.pdf (opened by the research agent)
3. AIB, European Residual Mix 2025 edition (28.05.2026) – https://www.aib-net.org/facts/european-residual-mix (averages only)
4. Pronovo, Cockpit Stromkennzeichnung (reporting year 2023, Aug 2024) – https://shkn.pronovo.ch/dokumente/de/Cockpit_Stromkennzeichnung_de.pdf
5. Microsoft, 2026 Environmental Data Fact Sheet (FY25, reviewed 09.07.2026) – https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/msc/documents/presentations/CSR/2026-Microsoft-Environmental-Data-Fact-Sheet-PDF.pdf
6. Amazon, 2025 GHG assurance Scope 1 & 2 (EY, 21.05.2026) – https://sustainability.aboutamazon.com/2025-ghg-assurance-scope-1-2.pdf
7. AWS Customer Carbon Footprint Tool release notes – https://docs.aws.amazon.com/ccft/latest/releasenotes/what-is-ccftrn.html
8. FOEN BAFU:2026 v1 (consumer mix GO, certified electricity) – see [V1-bafu-lca-grid-mix.md](V1-bafu-lca-grid-mix.md)
9. VSE / strom.ch 2026 (hourly method, imports) – see [V1-grid-mix-factors.md](V1-grid-mix-factors.md)
