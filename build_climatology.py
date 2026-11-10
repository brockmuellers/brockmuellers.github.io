#!/usr/bin/env python3
"""Build normal daily temperatures and monthly rainfall for the BirdNET weather page.

Writes 1991-2020 percentiles to assets/weather/climatology.json:
- Highs and lows per calendar day, from the Open-Meteo Historical Weather API (ERA5, CC BY 4.0)
- Rain so far this month per day of the month, from Environment Canada's Vancouver Harbour
  gauge (Open Government Licence - Canada). ERA5 rain runs ~50% wet here, since its grid
  cells take in the North Shore mountains. Run once; the output rarely needs updating.

Usage: ./build_climatology.py
"""
import calendar
import json
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, timedelta

LAT, LON = 49.27, -123.06  # Rounded station location (grid cells are ~10 km anyway)
START, END = "1991-01-01", "2020-12-31"  # Standard 30-year normals period
WINDOW = 7  # Pool each day with ±7 days around it, to smooth out year-to-year noise
PERCENTILES = [10, 25, 50, 75, 90]
RAIN_STATION = "1108446"  # Vancouver Harbour CS, ~4 km from the sensor
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

# Rain so far this month: for each month and day, the running total from the 1st, one value per year.
# Only months with no missing days are used. Feb 29 is left out, so Feb has 28 days.
rain, offset = {}, 0
while True:
    q = urllib.parse.urlencode({
        "f": "json", "CLIMATE_IDENTIFIER": RAIN_STATION, "datetime": f"{START}/{END}",
        "properties": "LOCAL_DATE,TOTAL_PRECIPITATION", "limit": 10000, "offset": offset,
    })
    with urllib.request.urlopen(f"https://api.weather.gc.ca/collections/climate-daily/items?{q}") as r:
        page = json.load(r)
    for f in page["features"]:
        rain[f["properties"]["LOCAL_DATE"][:10]] = f["properties"]["TOTAL_PRECIPITATION"]
    offset += len(page["features"])
    if not page["features"] or offset >= page["numberMatched"]:
        break

mtd = defaultdict(list)  # ("MM", day) -> totals across years
for y in range(int(START[:4]), int(END[:4]) + 1):
    for m in range(1, 13):
        n = calendar.monthrange(y, m)[1]
        vals = [rain.get(f"{y}-{m:02d}-{d:02d}") for d in range(1, n + 1)]
        if None in vals:
            continue
        total = 0
        for d, v in enumerate(vals[:28 if m == 2 else n], 1):
            total += v
            mtd[(f"{m:02d}", d)].append(total)
rain_mtd = {}
for m in range(1, 13):
    mm = f"{m:02d}"
    n = 28 if m == 2 else calendar.monthrange(2001, m)[1]
    rain_mtd[mm] = [[round(percentile(sorted(mtd[(mm, d)]), p), 1) for p in PERCENTILES] for d in range(1, n + 1)]

with open(OUT, "w") as f:
    json.dump({
        "source": {
            "temperature": "Open-Meteo Historical Weather API (ERA5), CC BY 4.0",
            "rain": f"Environment Canada climate station {RAIN_STATION} (Vancouver Harbour), Open Government Licence - Canada",
        },
        "latitude": LAT, "longitude": LON, "period": f"{START[:4]}-{END[:4]}",
        "percentiles": PERCENTILES, "units": {"temperature": "°C", "rain": "mm"},
        "days": out,
        "rain_mtd": rain_mtd,
    }, f, separators=(",", ":"))
print(f"Wrote {OUT} ({len(out)} days)")
