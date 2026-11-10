#!/usr/bin/env python3
"""Build normal daily high/low temperatures for the BirdNET weather page.

Pulls 1991-2020 daily highs and lows from the Open-Meteo Historical Weather API
(ERA5 reanalysis, CC BY 4.0) and writes per-calendar-day percentiles to
assets/weather/climatology.json. Run once; the output rarely needs updating.

Usage: ./build_climatology.py
"""
import json
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, timedelta

LAT, LON = 49.27, -123.06  # Rounded station location (grid cells are ~10 km anyway)
START, END = "1991-01-01", "2020-12-31"  # Standard 30-year normals period
WINDOW = 7  # Pool each day with ±7 days around it, to smooth out year-to-year noise
PERCENTILES = [10, 25, 50, 75, 90]
OUT = "assets/weather/climatology.json"


def percentile(sorted_vals, p):
    """Linear interpolation between closest ranks."""
    k = (len(sorted_vals) - 1) * p / 100
    lo = int(k)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


params = urllib.parse.urlencode({
    "latitude": LAT, "longitude": LON, "start_date": START, "end_date": END,
    "daily": "temperature_2m_max,temperature_2m_min", "timezone": "America/Vancouver",
})
with urllib.request.urlopen(f"https://archive-api.open-meteo.com/v1/archive?{params}") as r:
    daily = json.load(r)["daily"]

# Group values by calendar day ("MM-DD"); Feb 29 is folded into Feb 28
highs, lows = defaultdict(list), defaultdict(list)
for t, hi, lo in zip(daily["time"], daily["temperature_2m_max"], daily["temperature_2m_min"]):
    key = t[5:].replace("02-29", "02-28")
    if hi is not None: highs[key].append(hi)
    if lo is not None: lows[key].append(lo)

# For each calendar day (using a non-leap year), pool the surrounding window
days = [date(2001, 1, 1) + timedelta(d) for d in range(365)]
keys = [d.strftime("%m-%d") for d in days]
out = {}
for i, key in enumerate(keys):
    window = [keys[(i + o) % 365] for o in range(-WINDOW, WINDOW + 1)]
    hi = sorted(v for k in window for v in highs[k])
    lo = sorted(v for k in window for v in lows[k])
    out[key] = {
        "high": [round(percentile(hi, p), 1) for p in PERCENTILES],
        "low": [round(percentile(lo, p), 1) for p in PERCENTILES],
    }

with open(OUT, "w") as f:
    json.dump({
        "source": "Open-Meteo Historical Weather API (ERA5), CC BY 4.0",
        "latitude": LAT, "longitude": LON, "period": f"{START[:4]}-{END[:4]}",
        "percentiles": PERCENTILES, "units": "°C",
        "days": out,
    }, f, separators=(",", ":"))
print(f"Wrote {OUT} ({len(out)} days)")
