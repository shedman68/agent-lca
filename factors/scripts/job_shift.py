"""Best start hour for flexible jobs within their allowed window, using the hourly CO2 profile.

Usage: python job_shift.py <hourly_co2_csv> <jobs_csv> <out_profile_csv> <out_shift_csv>
- Profile: mean g CO2/kWh per (month, hour) over the baseline year (local time Europe/Zurich).
- Only jobs whose time_window starts with 'flexible' and whose resource sits in CH or DE.
- Quarterly model training is excluded: protected window (T-1053) -> human decision.
- Average intensity over the job's duration from a given start hour; windows are interpreted
  conservatively as an hour-of-day choice (day-to-day weather variation not used).
"""
import sys

import numpy as np
import pandas as pd

h = pd.read_csv(sys.argv[1], index_col=0)
h.index = pd.to_datetime(h.index, utc=True).tz_convert("Europe/Zurich")
jobs = pd.read_csv(sys.argv[2])

prof = pd.DataFrame({
    "CH": h["co2_ch_consumption"], "DE": h["co2_de"], "CH_production": h["co2_ch"],
})
prof["month"], prof["hour"] = prof.index.month, prof.index.hour
mh = prof.groupby(["month", "hour"])[["CH", "DE", "CH_production"]].mean()
mh.round(1).to_csv(sys.argv[3])

LOC = {"dp-prod": "CH", "logs": "CH", "st-archive": "CH", "dp-dev": "DE"}
WINDOW_HOURS = {
    "flexible: within 24 h": list(range(24)),
    "flexible: within the week": list(range(24)),
    "flexible: within the month": list(range(24)),
    "flexible: working day 08:00 to 18:00": list(range(8, 18)),
    "flexible: before the next working day": list(range(17, 24)) + list(range(0, 8)),
}


def avg_over(series_by_hour, start, dur):
    hrs = [(start + k) % 24 for k in range(int(np.ceil(dur)))] or [start]
    return float(np.mean([series_by_hour[x] for x in hrs]))


rows = []
flex = jobs[jobs["time_window"].str.startswith("flexible") & jobs["resource_id"].isin(LOC)]
for (name, rid, win), g in flex.groupby(["job_name", "resource_id", "time_window"]):
    if name == "Quarterly model training":
        rows.append(dict(job=name, resource=rid, grid=LOC[rid], window=win, note="excluded: protected window T-1053 (human decision)"))
        continue
    if win not in WINDOW_HOURS:
        continue
    dur = g["duration_h"].mean()
    start = int(g["start_time"].mode()[0][:2])
    grid = LOC[rid]
    now, best, best_h = [], [], []
    for m in range(1, 13):
        s = mh.loc[m, grid]
        cur = avg_over(s, start, dur)
        cand = {x: avg_over(s, x, dur) for x in WINDOW_HOURS[win] if (x + dur) <= 24 or "next working day" in win or "24 h" in win}
        bh = min(cand, key=cand.get)
        now.append(cur); best.append(cand[bh]); best_h.append(bh)
    rows.append(dict(job=name, resource=rid, grid=grid, window=win, runs=len(g), duration_h=round(dur, 2),
                     current_start=f"{start:02d}:00", best_start_typical=f"{pd.Series(best_h).mode()[0]:02d}:00",
                     g_per_kwh_now=round(np.mean(now), 1), g_per_kwh_best=round(np.mean(best), 1),
                     reduction_pct=round(100 * (1 - np.mean(best) / np.mean(now)), 1)))
r = pd.DataFrame(rows)
r.to_csv(sys.argv[4], index=False)
pd.set_option("display.width", 250)
print(r.to_string(index=False))
print("\nDaily swing (max-min of hourly means), g/kWh, by month:")
sw = mh.groupby(level=0).agg(lambda s: s.max() - s.min())[["CH", "DE"]].round(0)
print(sw.T.to_string())
