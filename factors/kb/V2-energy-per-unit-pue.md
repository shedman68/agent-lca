# V2 – Energy per unit and PUE

- **Task:** V2 energy per unit and PUE
- **Author:** Vinzenz (with Claude Code; research split across three research agents, values checked against our data)
- **Date:** 2026-11-20
- **Status:** final for review – values are in `factors/factors.csv`
- **Rule:** all energy factors **exclude** data-centre overhead; the pipeline multiplies by `pue_default` where `applies_pue = yes`.
  Sources that include PUE were divided by their own PUE.

## Result

| Key | Unit | Low | **Mid** | High | Certainty |
| --- | --- | --- | --- | --- | --- |
| `vcpu_hour` | kWh / vCPU-h | 0.0025 | **0.0040** | 0.0056 | medium |
| `node_hour` (16 vCPU, 64 GB) | kWh / node-h | 0.040 | **0.064** | 0.090 | medium |
| `gpu_hour` (300 W class + host) | kWh / GPU-h | 0.10 | **0.13** | 0.45 | medium (mid from data) |
| `gb_storage_day` (incl. replication) | kWh / GB-day | 0.000047 | **0.00009** | 0.00017 | medium–low |
| `bi_capacity_day` (Power BI P1/F64) | kWh / day | 0.48 | **0.77** | 1.08 | low (derived) |
| `runner_minute` (2 vCPU) | kWh / min | 0.000083 | **0.00013** | 0.00030 | medium–low (derived) |
| `gb_transfer` (no PUE) | kWh / GB | 0.001 | **0.01** | 0.059 | low |
| `tokens_1000` (in + out) | kWh / 1k tokens | 0.000038 | **0.00017** | 0.00052 | low–medium |
| `subscription_message` | kWh / message | 0.00022 | **0.0005** | 0.003 | medium (low/mid) |
| `pue_default` | ratio | 1.14 | **1.21** | 1.32 | medium |
| `saas_licence_month` | – | – | – | – | **excluded** (no credible source; vendors publish nothing per licence) |

## Effect on the baseline (pipeline run 2026-11-21 after the review follow-ups, `verify_baseline.py` = MATCH)

| | Low | Mid | High |
| --- | --- | --- | --- |
| Energy, baseline year | 19.4 MWh | **35.8 MWh** | 69.2 MWh |
| CO2 location-based | 2.9 t | **6.2 t** | 15.4 t |

Largest CO2 drivers (mid): node-hours 2.91 t (47 %) · storage 1.10 t · vCPU-hours 0.95 t · AI tokens 0.63 t · GPU 0.45 t.
Changes since 20.11. (36.3 MWh, 6.47 t): the GPU mid comes from data (0.18 → 0.13), and the Germany grid is life-cycle (0.344 → 0.330).
These numbers come from `out/fact_costs.csv`; the official figures are whatever the pipeline produces after merge.

## Why these values

### Compute (vCPU, node, GPU, runner, Power BI)
- **Two independent methods agree within ~30 %:** Boavizta API v2.6.0 (run live for Azure d16s_v5, AWS m6i/m5.4xlarge at 10 / 30 / 50 % load)
  and the Cloud Carbon Footprint (CCF) coefficients (Azure 0.78–3.76 W per vCPU, memory 0.392 W/GB).
- **Range = utilisation:** low 10 %, mid 30 %, high 50 % CPU. Our servers run at ~9 % (dp-dev) to ~50 %, so the range covers the fleet.
- **Node-hour** = 16 × vCPU-hour; Boavizta's direct 16 vCPU / 64 GB results give the same numbers.
- **GPU:** A100 PCIe 300 W TDP (NVIDIA), idle 46 W (CCF), host = Azure NC24ads_A100_v4 (24 vCPU, 220 GiB). The mid comes from data (review #8): weekly
  `gpu_avg_pct` in `server_metrics_weekly.csv` averages 9.2 % (5–7 % outside the 4 training weeks at ~43 %).
  Power model: GPU 46 + u × 254 W, host 55 + u × 95 W, which gives a 133 W mean = 0.13 kWh/h. It was 0.18 at an assumed 20 %. High = full training load. Host share is our derivation.
- **Runner-minute** and **Power BI capacity-day** have no direct source; derived from vCPU-hour (2-vCPU GitHub runner; 8 v-cores for P1/F64 per Microsoft Learn).

### Storage and network
- **Storage:** CCF drive coefficients (HDD 0.65, SSD 1.2 Wh per TB-hour) × replication from CCF's provider constants (LRS 3, GRS 6, S3 6, disks 3).
  Providers do not publish replication or fill rates, so the range is wide.
- **Data transfer:** the published values span 60× (0.001 marginal core-only → 0.059 average allocation incl. access networks).
  Network energy is mostly fixed, so kWh per GB is a *convention* (Mytton, Lundén, Malmodin 2024). Mid 0.01 is our assumption. Impact is small (0.5 MWh).

### AI
- **No provider publishes energy per token.** Values come from Epoch AI (2025), Jegham et al. "How Hungry is AI?" (2025), ML.ENERGY (2026) and Google's measured
  0.24 Wh per median Gemini prompt (2025).
- **Weighted with our own data:** input:output = **5.6 : 1** and **97 %** of tokens are on large models (`ai_usage.csv`). Output tokens cost ~6× more than input.
- **Small models use ~4–5× less energy per token.** Added on 21.11. (review #8): `tokens_in_1000_large`, `tokens_out_1000_large`, `tokens_in_1000_small` and
  `tokens_out_1000_small` in `factors.csv`, each with low/mid/high and sources. Mid values: large input 0.0001, output 0.0006; small input 0.00002, output 0.00015 kWh per 1k.
  The pipeline keeps the blended `tokens_1000`; the split is for the measures calculator ("smaller model + caching").
- **Subscription message:** low = Google's measured median prompt without overhead (0.22 Wh); mid = typical enterprise message (~2k context + 500 output tokens = 0.5 Wh);
  high = long-context / document-grounded use (Copilot) ~3 Wh.

### PUE
| Location | Share of kWh | Low | Mid | High | Basis |
| --- | --- | --- | --- | --- | --- |
| Azure Zurich | 46 % | 1.16 | 1.25 | 1.35 | Microsoft owns no Swiss sites (runs in colocation) → Swiss colocation values (BFE 2026) |
| Azure Frankfurt | 20 % | 1.12 | 1.16 | 1.30 | Microsoft FY25 EMEA 1.16 |
| AWS Dublin | 15 % | 1.08 | 1.10 | 1.15 | AWS Ireland fact sheet: 1.10 (2025) |
| Swiss hoster | 8 % | 1.20 | 1.31 | 1.55 | BFE 2026: Swiss colocation average 1.31 |
| AWS CH | 4 % | 1.16 | 1.25 | 1.35 | as Azure Zurich |
| AI providers | 7 % | 1.09 | 1.15 | 1.30 | hyperscaler fleets (Google 1.09, Microsoft 1.17, AWS 1.14) + leased capacity |
| **Weighted `pue_default`** | | **1.14** | **1.21** | **1.32** | |

**How far to trust provider PUE:** self-reported and not audited; fleet averages exclude leased colocation and new sites (exactly where Swiss regions run);
annual averages hide partly loaded new sites (BFE: Swiss sites at ~30 % load). Industry averages are higher (EU 1.36, Uptime survey 1.56 – both snippet only).
The pipeline applies one PUE to all rows; per-provider PUE would need a pipeline change (Rashed).

## Sources (checked = number read in the original)
1. Boavizta API v2.6.0, `api.boavizta.org/v1/cloud/instance` – run 20.11.2026 (checked)
2. Cloud Carbon Footprint, methodology – https://www.cloudcarbonfootprint.org/docs/methodology/ and provider constants in github.com/cloud-carbon-footprint (checked 20.11.2026)
3. NVIDIA A100 – https://www.nvidia.com/en-us/data-center/a100/ (checked)
4. Microsoft Learn, NC_A100_v4 series (2024-07-31) – https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/nca100v4-series (checked)
5. Microsoft Learn, What is Power BI Premium? (2026-06-15) – https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-premium-what-is (checked)
6. GitHub Docs, GitHub-hosted runners – https://docs.github.com/en/actions/reference/runners/github-hosted-runners (checked)
7. Sustainable Web Design Model v4 – https://sustainablewebdesign.org/estimating-digital-emissions/ (checked)
8. Aslan et al., J. Industrial Ecology 22(4), 2018, DOI 10.1111/jiec.12630 (snippet only)
9. Mytton, Lundén, Malmodin, J. Industrial Ecology 28(4), 2024, DOI 10.1111/jiec.13512 (snippet only)
10. Elsworth et al. (Google), arXiv:2508.15734, 21.08.2025 – https://arxiv.org/html/2508.15734 (checked)
11. Epoch AI, How much energy does ChatGPT use?, 07.02.2025 – https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use (checked)
12. Jegham et al., How Hungry is AI?, arXiv:2505.09598 v6 – https://arxiv.org/html/2505.09598v6 (checked)
13. Chung et al., Where Do the Joules Go? (ML.ENERGY), arXiv:2601.22076, 29.01.2026 – https://arxiv.org/html/2601.22076 (checked)
14. Microsoft datacenter efficiency (FY25) – https://datacenters.microsoft.com/sustainability/efficiency/ (checked)
15. AWS Ireland sustainability fact sheet (2026) – https://sustainability.aboutamazon.com/aws-sustainability-fact-sheets/aws-fact-sheet-ireland.pdf (checked); AWS global – https://aws.amazon.com/sustainability/ (checked)
16. BFE / EnergieSchweiz, Rechenzentren in der Schweiz – Stromverbrauch und Effizienzpotenzial, 06.07.2026 – https://pubdb.bfe.admin.ch/de/publication/download/12677 (checked)
17. EU Energy Efficiency Directive, first data-centre reporting round (EC, June 2025) – EU average PUE 1.36 (snippet only)
18. Uptime Institute Global Data Center Survey 2024 – average PUE 1.56 (snippet only)
