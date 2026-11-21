"""Hourly CO2 intensity, baseline year Sep 2025 - Aug 2026, from the Energy-Charts API (Fraunhofer ISE).

DE: Energy-Charts co2eq (generation mix of Germany).
CH: consumption mix incl. imports, built like VSE: per hour
    (CH generation x CH intensity + sum(imports_n x intensity_n)) / (CH generation + sum(imports_n)).
    Exports leave with the same mix; pumped-storage pumping is not netted (simplification).
Usage: python energy_charts_hourly.py <download_dir> <out_csv>
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

API = "https://api.energy-charts.info"
DL = Path(sys.argv[1]); DL.mkdir(parents=True, exist_ok=True)
OUT = Path(sys.argv[2])
MONTHS = pd.date_range("2025-09-01", "2026-08-01", freq="MS")
NEIGH = {"Germany": "de", "France": "fr", "Italy": "it", "Austria": "at"}
GEN_EXCLUDE = {"Cross border electricity trading", "Load", "Residual load",
               "Renewable share of load", "Renewable share of generation"}


def get(endpoint, params, name):
    p = DL / f"{name}.json"
    if not p.exists():
        url = f"{API}/{endpoint}?" + "&".join(f"{k}={v}" for k, v in params.items())
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research script)"})
        for attempt in range(8):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    p.write_bytes(r.read())
                break
            except Exception as e:  # noqa: BLE001
                wait = 20 * (attempt + 1)
                print("retry", name, e, f"wait {wait}s", flush=True); time.sleep(wait)
        else:
            raise SystemExit(f"giving up on {name}")
        time.sleep(6)
    return json.loads(p.read_text())


def hourly(unix, values, name):
    s = pd.Series(values, index=pd.to_datetime(unix, unit="s", utc=True), name=name, dtype="float64")
    return s.resample("1h").mean()


frames = []
for m in MONTHS:
    start, end = m.strftime("%Y-%m-%d"), (m + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d")
    tag = m.strftime("%Y-%m")
    cols = []
    for c in ["de", "ch", "fr", "it", "at"]:
        j = get("co2eq", {"country": c, "start": start, "end": end}, f"co2eq_{c}_{tag}")
        cols.append(hourly(j["unix_seconds"], j["co2eq"], f"co2_{c}"))
    pp = get("public_power", {"country": "ch", "start": start, "end": end}, f"power_ch_{tag}")
    gen = None
    for t in pp["production_types"]:
        if t["name"] in GEN_EXCLUDE:
            continue
        s = hourly(pp["unix_seconds"], t["data"], t["name"]).clip(lower=0)
        gen = s if gen is None else gen.add(s, fill_value=0)
    cols.append(gen.rename("gen_ch_mw"))
    fl = get("cbpf", {"country": "ch", "start": start, "end": end}, f"cbpf_ch_{tag}")
    for c in fl["countries"]:
        if c["name"] in NEIGH:
            cols.append((hourly(fl["unix_seconds"], c["data"], c["name"]) * 1000).rename(f"flow_{NEIGH[c['name']]}_mw"))
    frames.append(pd.concat(cols, axis=1))

d = pd.concat(frames).sort_index()
d = d[~d.index.duplicated()]
num = d["gen_ch_mw"] * d["co2_ch"]
den = d["gen_ch_mw"].copy()
for code in NEIGH.values():
    imp = d[f"flow_{code}_mw"].clip(lower=0).fillna(0)
    num = num + imp * d[f"co2_{code}"].fillna(d["co2_de"])
    den = den + imp
d["co2_ch_consumption"] = num / den
d["import_share_ch"] = 1 - d["gen_ch_mw"] / den
d.index = d.index.tz_convert("Europe/Zurich")
d.to_csv(OUT)

print("hours:", len(d), "missing CH cons:", int(d["co2_ch_consumption"].isna().sum()), "missing DE:", int(d["co2_de"].isna().sum()))
print("annual mean g/kWh (time-weighted): CH production %.1f | CH consumption %.1f | DE %.1f"
      % (d["co2_ch"].mean(), d["co2_ch_consumption"].mean(), d["co2_de"].mean()))
w = den
print("CH consumption, energy-weighted: %.1f g/kWh; mean import share %.1f %%"
      % ((d["co2_ch_consumption"] * w).sum() / w[d["co2_ch_consumption"].notna()].sum(), 100 * d["import_share_ch"].mean()))
print(d.groupby(d.index.month)[["co2_ch_consumption", "co2_de", "import_share_ch"]].mean().round(2))
