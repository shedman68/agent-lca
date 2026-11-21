# V1 – Grid mix factors, location-based (final values)

- **Task:** V1 grid mix, location-based
- **Author:** Vinzenz (with Claude Code)
- **Date:** 2026-11-20
- **Status:** final for review – values are in `factors/factors.csv` (keys `grid_CH`, `grid_DE`, `grid_IE`, `grid_EU`)
- **Background research:** [V1-bafu-lca-grid-mix.md](V1-bafu-lca-grid-mix.md) (FOEN BAFU:2026 database extract)

## Result (kg CO2-eq per kWh)

| Key | Region | Low | **Mid** | High | Used for |
| --- | --- | --- | --- | --- | --- |
| `grid_CH` | Switzerland, consumption mix | 0.057 | **0.090** | 0.098 | Hoster, on-prem servers in CH |
| `grid_DE` | Germany | 0.329 | **0.330** | 0.431 | Azure / AWS Frankfurt region |
| `grid_IE` | Ireland | 0.255 | **0.257** | 0.320 | Dublin region (incl. zombie servers) |
| `grid_EU` | Europe, mixed | 0.210 | **0.272** | 0.319 | AI providers and SaaS ("EU mixed") |

Rule for all rows: **mid = best value for the baseline year Sep 2025 – Aug 2026** (calendar year 2025 where available),
low / high = the lowest / highest credible independent source. Every row has at least two independent sources.

## Switzerland – why the consumption mix
| Option | Value | Source |
| --- | --- | --- |
| Production mix (only what is generated in CH) | 0.028–0.039 | FOEN BAFU:2026 (0.028 MV / 0.032 LV); Ember 2025 (0.039) |
| **Consumption mix (incl. imports)** | **0.057–0.098** | VSE 2026 (2024: 0.057, 2025: 0.090); FOEN BAFU:2026 (0.089); UNIGE 2024 (0.098) |

**Recommendation: consumption mix, mid 0.090.**
- The company consumes electricity from the Swiss grid. In winter and in dry springs Switzerland imports a large share,
  mostly from Germany (gas and coal). That electricity is physically consumed in Switzerland, so it belongs in the footprint.
- The production mix ignores imports and would make Swiss servers look about **3× cleaner** than they are.
- 2025 is the year that covers most of the baseline (Sep–Dec 2025) and was a high-import year (low reservoir levels in spring,
  VSE report p. 4–5). Two independent methods give the same value: VSE hourly calculation 0.090 and FOEN database 0.089.
- **Range:** low 0.057 is the very clean year 2024 (good hydro); high 0.098 is UNIGE's hourly import-tracing method
  (2017–2021 average), which shows that the conventional annual method tends to underestimate imports.
  Monthly values swing much more. Our own hourly data for the baseline year (V4) gives a monthly mean of 26 g in Jun vs 98 g in Jan,
  2–4× apart. The absolute level is lower than VSE; use it for the shape only (see [V4-market-based-and-hourly.md](V4-market-based-and-hourly.md)).
  The Stadt Zürich / treeze range (70–164 g) was not checked and is no longer used.

## Germany
- **Update 21.11.2026 (review #5):** aligned to life-cycle, so all grid mids share one system boundary. The mid was UBA 0.344 (direct CO2 only).
- **Mid 0.330** – Ember 2025 life-cycle value (via Our World in Data); the same source and basis as the Ireland mid.
- **Low 0.329** – Electricity Maps, Grid Review 2025 Germany, consumption-based 328.9 g (snippet only).
- **High 0.431** – FOEN BAFU:2026 life-cycle consumption mix at medium voltage (includes upstream chain and grid; older reference year).
- **Cross-check only:** Umweltbundesamt 0.344 per consumed kWh in 2025 (2024 = 0.353, 2023 = 0.379), direct CO2 only.

## Ireland
- **Mid 0.257** – Ember 2025 life-cycle (most recent annual value found).
- **Low 0.255** – SEAI 2023 (cited in EPA State of the Environment Report 2024). No SEAI value for 2024/2025 found yet.
- **High 0.320** – FOEN BAFU:2026 life-cycle consumption mix at medium voltage.

## Europe ("EU mixed" for AI providers and SaaS)
- **Mid 0.272** – FOEN BAFU:2026, ENTSO-E area; Ember 2025 "Europe" gives 0.271 independently.
  ENTSO-E is chosen over EU-27 because provider data centres sit in the whole interconnected grid (incl. CH, NO, GB).
- **Low 0.210** – Ember 2025, EU-27 only.
- **High 0.319** – FOEN BAFU:2026, RER (Europe) life-cycle.

## How certain? (for the jury)
- CH: **medium** certainty – the method choice (production vs consumption) matters 3×; the year matters 1.6× (0.057 vs 0.090).
- DE, IE, EU: **good** certainty for the order of magnitude; ±25 % between direct-only and full life-cycle accounting.
- All values are location-based. Market-based values (guarantees of origin) follow in V4.

## Sources
1. VSE / strom.ch, *CO2-Gehalt des Strommix Schweiz bis 2050*, 15.01.2026 – https://www.strom.ch/de/dokument/co2-gehalt-des-strommix-schweiz-bis-2050-2026 (p. 2: 2024 = 57 g, 2025 = 90 g CO2-eq/kWh, 2025 partly provisional)
2. FOEN / BAFU, life cycle inventory database BAFU:2026 v1, IPCC 2021 GWP100 – https://api.data-platform-stg.cloud.bafu.admin.ch/en/dataproduct-economy-consumption-lca (file loaded 06.11.2026)
3. Romano, Patel, Hollmuller, *Energy* (2024), UNIGE – https://archive-ouverte.unige.ch/unige:181220 (98 g CO2-eq/kWh, 2017–2021); hourly data: https://www.unige.ch/sysener/services/CO2
4. Umweltbundesamt, *CO2-Emissionen pro Kilowattstunde Strom 2025* – https://www.umweltbundesamt.de/themen/co2-emissionen-pro-kilowattstunde-strom-2025-nur (checked 20.11.2026)
5. Ember yearly electricity data via Our World in Data – https://ourworldindata.org/grapher/carbon-intensity-electricity (downloaded 20.11.2026)
6. EPA Ireland, *State of the Environment Report 2024* (SEAI data) – https://epawebapp.epa.ie/ebooks/soe2024/324/
7. (not used any more – unchecked) Stadt Zürich / treeze, *Ökobilanz monatliche Strombereitstellung* (2025)
