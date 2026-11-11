---
layout: page
title: BirdNET Weather
permalink: /birdnet-weather/
weather_data_url: https://birdnet-data.brockmuellers.com/weather.json
summary: "Temperature, humidity, and rain at echo-birdnet"
---

Weather at [echo-birdnet]({% link _more/birdnet-station.md %}). Sensors: LaCrosse Temperature and Humidity Sensor, AcuRite Self-Emptying Rain Collector.

<style>
  .updated-at, #weather-units { margin: 0 0 1em; color: #555; font-size: 13px; }
  #weather-summary { margin: 0 0 1.5em; display: flex; flex-direction: column; gap: 8px; }
  #weather-charts { margin: 0 0 0.5em; display: flex; flex-direction: column; gap: 16px; }
  #month-chart, #month-rain-chart { margin: 0 0 0.5em; }
  .chip-row { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
  .chip-row-label { font-size: 11px; color: #999; width: 70px; flex-shrink: 0; }
  .chip { display: inline-block; padding: 3px 10px; border-radius: 4px; font-size: 12px; }
  .chip-label { opacity: 0.7; }
  .chart-title { font-size: 11px; margin-bottom: 2px; }
  .chart-svg { display: block; width: 100%; height: auto; }
  .muted { color: #999; }
  .harbour-note { color: #6b7280; }
  .caption { margin: 0 0 1.5em; font-size: 11px; color: #999; }
  .credits { margin: 1.5em 0 0; font-size: 11px; color: #999; }
  .swatch { display: inline-block; vertical-align: middle; }
  .swatch.no-data { width: 10px; height: 10px; background: #e5e7eb; }
  .swatch.dashed { width: 14px; border-top: 1px dashed #9ca3af; }

  #daily { border-collapse: collapse; font-size: 13px; }
  #daily th { font-weight: normal; color: #666; font-size: 11px; }
  #daily th, #daily td { text-align: right; padding: 3px 16px 3px 0; }
  #daily th:first-child, #daily td:first-child { text-align: left; }
  #daily th:last-child, #daily td:last-child { padding: 3px 0; }
  #daily td + td { color: #555; }

  #forecast-options { margin: 0 0 0.5em; color: #555; font-size: 13px; }
  #forecast { border-collapse: collapse; font-size: 13px; margin: 0 0 0.5em; }
  #forecast th { font-weight: normal; color: #666; font-size: 11px; }
  #forecast th, #forecast td { text-align: right; padding: 3px 0 3px 16px; }
  #forecast th:first-child, #forecast td:first-child { text-align: left; padding-left: 0; }
  #forecast tfoot td { color: #555; }
  #forecast tfoot tr:first-child td { border-top: 2px solid #9ca3af; }  /* Separates the days from the stats */
  #forecast .best { font-weight: bold; }
  /* "?" hover tips; tabindex lets a tap show them on touch screens */
  .tip { position: relative; cursor: help; }
  .tip-icon { display: inline-block; width: 13px; height: 13px; line-height: 13px; border-radius: 50%; background: #e5e7eb; color: #555; font-size: 10px; text-align: center; }
  .tip::after { content: attr(data-tip); display: none; position: absolute; left: 0; top: 100%; z-index: 1; width: 240px; padding: 6px 8px; border-radius: 4px; background: #374151; color: #fff; font-size: 12px; font-weight: normal; white-space: normal; text-align: left; }
  .tip:hover::after, .tip:focus::after { display: block; }
</style>

<div id="weather-status">Loading...</div>
<div id="weather-content" style="display:none">
  <p class="updated-at"><strong>Updated at:</strong> <span id="generated-at-value"></span></p>
  <div id="weather-units">
    Units:
    <label><input type="radio" name="temp-unit" value="F" checked> °F</label>
    <label><input type="radio" name="temp-unit" value="C"> °C</label>
    &nbsp;·&nbsp;
    <label><input type="radio" name="rain-unit" value="in" checked> in</label>
    <label><input type="radio" name="rain-unit" value="mm"> mm</label>
  </div>
  <div id="weather-summary"></div>
  <h3>Last 7 days</h3>
  <div id="weather-charts"></div>
  <p class="caption"><span class="swatch no-data"></span> no data from sensor
    &nbsp;·&nbsp; <span class="swatch dashed"></span> Open-Meteo's current readings for the area</p>
  <div id="month-section" style="display:none">
    <h3 id="month-title"></h3>
    <div id="month-chart"></div>
    <p class="caption">
      Dots are this sensor's daily highs and lows (hollow = today so far). Bands show the normal range of highs and lows for this area (~10 km resolution), 1991–2020: the darker band is the 25th to 75th percentile, the lighter band is the 10th to 90th percentile, and the line is the median.
      This sensor may read consistently warmer or cooler than the area; see the temperature chart above for a comparison with current data.
    </p>
    <div id="month-rain-chart"></div>
    <p id="month-rain-caption" class="caption">
      Line is this sensor's rain so far this month; dashed line is Environment Canada's Vancouver Harbour gauge, ~4 km away (posted a day or two late).
      Bands show the normal range of totals at that gauge by each day, 1991–2020, with the same percentiles as above. Rain varies a lot over short distances, so expect some difference.
    </p>
  </div>
  <h3>Daily</h3>
  <table id="daily">
    <thead>
      <tr><th>Date</th><th>Low</th><th>High</th><th>Humidity</th><th>Rain</th></tr>
    </thead>
    <tbody id="daily-body"></tbody>
  </table>
  <div id="forecast-section" style="display:none">
    <h3>Forecast accuracy</h3>
    <div id="forecast-options">
      Forecast made
      <label><input type="radio" name="fc-lead" value="1" checked> 1 day</label>
      <label><input type="radio" name="fc-lead" value="3"> 3 days</label>
      <label><input type="radio" name="fc-lead" value="5"> 5 days</label>
      ahead<br>
      <label><input type="radio" name="fc-key" value="high" checked> High</label>
      <label><input type="radio" name="fc-key" value="low"> Low</label>
      <label><input type="radio" name="fc-key" value="rain"> Rain</label>
    </div>
    <table id="forecast">
      <thead id="forecast-head"></thead>
      <tbody id="forecast-body"></tbody>
      <tfoot id="forecast-foot"></tfoot>
    </table>
    <p class="caption">
      Each model's forecast for this location, from Open-Meteo's archive of past runs: ECMWF (European), GFS (US), GEM (Environment Canada), and ICON (German); most weather apps use one or more of these.
      Model highs and lows are hourly, so they can be a little milder than the sensor's. Days with less than 22 hours of sensor data are left out.
    </p>
  </div>
  <p class="credits">Model and historical weather data by <a href="https://open-meteo.com/">Open-Meteo.com</a> (<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>).
    Rain data from <a href="https://climate.weather.gc.ca/">Environment and Climate Change Canada</a>; contains information licensed under the <a href="https://open.canada.ca/en/open-government-licence-canada">Open Government Licence – Canada</a>.</p>
</div>

{% include chart.html %}
<script type="module">
const url = "{{ page.weather_data_url }}";
const HOUR = 3600000, DAY = 24 * HOUR;
const STALE_MINUTES = 30;
const DAILY_ROWS = 14;
const COLOR = { temp: "#ea580c", humidity: "#0d9488", rain: "#2563eb", dew: "#7c3aed" };
const BG = { yellow: "#fef9c3", red: "#fee2e2", neutral: "#f3f4f6" };
const FG = { yellow: "#854d0e", red: "#991b1b", neutral: "#374151" };

// Data is in °C and mm; convert for display based on the unit radios
let useF = true, useIn = true;
const fmtTemp = v => v == null ? "—" : useF ? `${(v * 9 / 5 + 32).toFixed(1)}°F` : `${v.toFixed(1)}°C`;
const fmtHum  = v => v == null ? "—" : `${Math.round(v)}%`;
const fmtRain = v => v == null ? "—" : useIn ? `${(v / 25.4).toFixed(2)} in` : `${v.toFixed(1)} mm`;

// Optional extras: if one fails or takes more than a few seconds, the page renders without it
const getJson = u => fetch(u, { signal: AbortSignal.timeout(5000) }).then(r => r.ok ? r.json() : null).catch(() => null);
const climP = getJson("{{ '/assets/weather/climatology.json' | relative_url }}");
const omP = getJson("https://api.open-meteo.com/v1/forecast?latitude=49.27&longitude=-123.06&hourly=temperature_2m,relative_humidity_2m&past_days=8&forecast_days=1&timezone=GMT&timeformat=unixtime");
const ecP = getJson("https://api.weather.gc.ca/collections/climate-daily/items?f=json&CLIMATE_IDENTIFIER=1108446&sortby=-LOCAL_DATE&limit=31&properties=LOCAL_DATE,TOTAL_PRECIPITATION");
// Archived model forecasts: each variable_previous_dayN is what the model run N days earlier forecast for that hour
const FC_MODELS = { ecmwf_ifs025: "ECMWF", gfs_seamless: "GFS", gem_seamless: "GEM", icon_seamless: "ICON" };
const fcVars = [1, 3, 5].flatMap(n => [`temperature_2m_previous_day${n}`, `precipitation_previous_day${n}`]);
const fcP = getJson(`https://previous-runs-api.open-meteo.com/v1/forecast?latitude=49.27&longitude=-123.06&hourly=${fcVars}&models=${Object.keys(FC_MODELS)}&past_days=31&forecast_days=1&timezone=America/Vancouver`);

fetch(url, { signal: AbortSignal.timeout(20000) })
  .then(r => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  })
  .then(data => Promise.all([data, climP, omP, ecP, fcP]))
  .then(([data, clim, om, ec, fc]) => {
    const tz = data.timezone;
    document.getElementById("generated-at-value").textContent =
      new Date(data.generated_at).toLocaleString('en-US');  // Viewer's time zone

    const render = () => {
      document.getElementById("weather-summary").innerHTML = "";
      document.getElementById("weather-charts").innerHTML = "";
      document.getElementById("daily-body").innerHTML = "";

      // ---- Summary chips ----
      const chip = (label, value, color = "neutral") => {
        const el = document.createElement("span");
        el.className = "chip";
        el.style.background = BG[color];
        el.style.color = FG[color];
        el.innerHTML = `<span class="chip-label">${label}:</span> ${value}`;
        return el;
      };
      const chipRow = (rowLabel, chips) => {
        const row = document.createElement("div");
        row.className = "chip-row";
        const lbl = document.createElement("span");
        lbl.className = "chip-row-label";
        lbl.textContent = rowLabel;
        row.appendChild(lbl);
        chips.forEach(c => row.appendChild(c));
        return row;
      };

      const ageMinutes = ts => (Date.now() - new Date(ts).getTime()) / 60000;
      const fmtAge = m => m < 60 ? `${Math.round(m)}m ago` : m < 1440 ? `${Math.round(m / 60)}h ago` : `${Math.round(m / 1440)}d ago`;
      // Chip flagging a missing or stale sensor
      const sensorWarnings = (name, reading) => {
        if (!reading) return [chip(name, "no data", "red")];
        const age = ageMinutes(reading.ts);
        return age > STALE_MINUTES ? [chip(name, `last heard ${fmtAge(age)}`, "yellow")] : [];
      };

      const cur = data.current || {};
      const th = cur.thermometer, rg = cur.rain_gauge;
      const days = data.daily || [];
      const today = days[days.length - 1] || {};
      const summaryDiv = document.getElementById("weather-summary");

      summaryDiv.appendChild(chipRow("Current", [
        chip("Temp", fmtTemp(th?.temp_c)),
        chip("Humidity", fmtHum(th?.humidity)),
        chip("Rain today", fmtRain(today.rain_mm)),
        ...sensorWarnings("Thermometer", th),
        ...sensorWarnings("Rain gauge", rg),
      ]));

      const week = days.slice(-7);
      const weekMins = week.filter(d => d.temp_c).map(d => d.temp_c.min);
      const weekMaxes = week.filter(d => d.temp_c).map(d => d.temp_c.max);
      const weekRain = week.filter(d => d.rain_mm != null);
      summaryDiv.appendChild(chipRow("Last 7 days", [
        chip("Low", fmtTemp(weekMins.length ? Math.min(...weekMins) : null)),
        chip("High", fmtTemp(weekMaxes.length ? Math.max(...weekMaxes) : null)),
        chip("Rain", fmtRain(weekRain.length ? weekRain.reduce((s, d) => s + d.rain_mm, 0) : null)),
      ]));

      // ---- Hourly charts (last 7 days) ----
      const cutoff = new Date(data.generated_at).getTime() - 7 * DAY;
      // Hours with no entry (both sensors out) become empty slots, so they're drawn as gaps too
      const byT = new Map((data.hourly || []).map(w => [new Date(w.window_start).getTime(), w]));
      const times = [...byT.keys()].filter(t => t >= cutoff);
      const hours = [];
      if (times.length) {
        const first = Math.min(...times), last = Math.max(...times);
        for (let t = first; t <= last; t += HOUR) hours.push({ ...byT.get(t), t });
      }

      const chartsDiv = document.getElementById("weather-charts");
      const W = 740, plotH = 90, H = plotH + 14, padL = 44, padR = 4, py = 6;
      const localHour = ms => parseInt(new Date(ms).toLocaleString('en-US', { hour: 'numeric', hourCycle: 'h23', timeZone: tz }));
      const fmtDate = ms => new Date(ms).toLocaleDateString('en-US', { weekday: 'short', month: 'numeric', day: 'numeric', timeZone: tz });

      // Display units for axis ticks (see chartAxis)
      const UNIT = {
        temp: useF ? { suffix: "°F", to: c => c * 9 / 5 + 32, from: f => (f - 32) * 5 / 9 } : { suffix: "°C" },
        hum: { suffix: "%" },
        rain: useIn ? { suffix: " in", to: mm => mm / 25.4, from: i => i * 25.4 } : { suffix: " mm" },
      };

      // unit is one of UNIT, for the y axis.
      // getVal(w) returns a number (bars) or {min,max,avg} (band + line), or undefined if missing.
      // ref (optional) is a Map of hour start ms -> value, drawn as a dashed gray comparison line.
      // extra (optional) is {getVal, color}: a second series (one number per hour) drawn as a thin line.
      const renderChart = (title, color, unit, getVal, bars, ref, extra) => {
        if (hours.length < 2) return;
        const present = hours.filter(w => getVal(w) != null);
        if (!present.length) return;
        const t0 = hours[0].t, t1 = hours[hours.length - 1].t + HOUR;
        const xf = t => padL + ((t - t0) / (t1 - t0)) * (W - padL - padR);
        const mid = t => xf(t + HOUR / 2);
        const refPts = ref ? [...ref].filter(([t, v]) => t >= t0 && t <= t1 && v != null) : [];
        const extraVals = extra ? hours.map(extra.getVal).filter(v => v != null) : [];
        const refVals = [...refPts.map(([, v]) => v), ...extraVals];
        const vMin = bars ? 0 : Math.min(...present.map(w => getVal(w).min), ...refVals);
        const vMax = bars ? Math.max(...present.map(getVal)) : Math.max(...present.map(w => getVal(w).max), ...refVals);
        const axis = chartAxis(vMin, vMax, 5, unit);
        const yf = chartYScale(axis.lo, axis.hi, plotH, py);
        const f = n => n.toFixed(1);

        let svg = chartGrid(axis, yf, padL, W - padR);
        // Gray slots where the sensor wasn't heard
        hours.forEach(w => {
          if (getVal(w) == null) svg += `<rect x="${f(xf(w.t))}" y="${py}" width="${f(xf(w.t + HOUR) - xf(w.t))}" height="${plotH - 2 * py}" fill="#e5e7eb"/>`;
        });
        // Local-midnight gridlines with date labels
        hours.forEach(w => {
          if (localHour(w.t) !== 0) return;
          svg += `<line x1="${f(xf(w.t))}" y1="0" x2="${f(xf(w.t))}" y2="${plotH}" stroke="#e5e7eb"/>`;
          svg += `<text x="${f(xf(w.t) + 2)}" y="${H - 2}" font-size="9" fill="#999">${fmtDate(w.t)}</text>`;
        });

        if (bars) {
          present.forEach(w => {
            const v = getVal(w);
            if (v > 0) svg += `<rect x="${f(xf(w.t))}" y="${f(yf(v))}" width="${f(Math.max(xf(w.t + HOUR) - xf(w.t) - 0.5, 1))}" height="${f(yf(0) - yf(v))}" fill="${color}" opacity="0.4"/>`;
          });
        } else {
          // Connect only consecutive hours that both have data, so gaps stay gaps
          for (let i = 0; i < hours.length - 1; i++) {
            const a = hours[i], b = hours[i + 1], va = getVal(a), vb = getVal(b);
            if (va == null || vb == null) continue;
            svg += chartBand(mid(a.t), va, mid(b.t), vb, yf, color);
            svg += chartLine(mid(a.t), va, mid(b.t), vb, yf, color);
          }
          // A lone hour (no data on either side) has no line, so draw it as a dot
          hours.forEach((w, i) => {
            const v = getVal(w);
            if (v != null && getVal(hours[i - 1] || {}) == null && getVal(hours[i + 1] || {}) == null)
              svg += `<circle cx="${f(mid(w.t))}" cy="${f(yf(v.avg))}" r="2" fill="${color}"/>`;
          });
        }
        // Second series, connecting consecutive hours that both have a value
        if (extra) for (let i = 0; i < hours.length - 1; i++) {
          const va = extra.getVal(hours[i]), vb = extra.getVal(hours[i + 1]);
          if (va != null && vb != null)
            svg += `<line x1="${f(mid(hours[i].t))}" y1="${f(yf(va))}" x2="${f(mid(hours[i + 1].t))}" y2="${f(yf(vb))}" stroke="${extra.color}" stroke-width="1" stroke-linecap="round" opacity="0.5"/>`;
        }
        // Comparison line; its values are instants at the top of each hour
        if (refPts.length > 1)
          svg += `<polyline points="${refPts.map(([t, v]) => `${f(xf(t))},${f(yf(v))}`).join(" ")}" fill="none" stroke="#9ca3af" stroke-width="1" stroke-dasharray="4 3"/>`;

        const wrap = document.createElement("div");
        wrap.innerHTML = `
          <div class="chart-title" style="color:${color}">${title}</div>
          <svg viewBox="0 0 ${W} ${H}" class="chart-svg">
            <rect x="${padL}" y="0" width="${W - padL - padR}" height="${plotH}" fill="#f9fafb"/>
            ${svg}
          </svg>`;
        chartsDiv.appendChild(wrap);
      };

      // Open-Meteo hourly readings as a Map (ms -> value), and the sensor's average offset from them
      const omSeries = key => om && om.hourly ? new Map(om.hourly.time.map((s, i) => [s * 1000, om.hourly[key][i]])) : null;
      const avgDiff = (ref, getVal) => {
        if (!ref) return null;
        // Compare each sensor hour (t to t+1h) with the midpoint of Open-Meteo's readings at t and t+1h
        const diffs = hours.filter(w => getVal(w) && ref.get(w.t) != null && ref.get(w.t + HOUR) != null)
          .map(w => getVal(w).avg - (ref.get(w.t) + ref.get(w.t + HOUR)) / 2);
        return diffs.length ? diffs.reduce((s, x) => s + x, 0) / diffs.length : null;
      };
      const vsOm = (mag, word) => ` <span class="muted">· this week the sensor averaged ${mag} ${word} than Open-Meteo's current readings (dashed line)</span>`;

      const omTemp = omSeries("temperature_2m"), dT = avgDiff(omTemp, w => w.temp_c);
      // Dew point from the hour's average temperature and humidity (Magnus formula)
      const dewPoint = w => {
        if (!w.temp_c || !w.humidity) return null;
        const g = Math.log(w.humidity.avg / 100) + 17.62 * w.temp_c.avg / (243.12 + w.temp_c.avg);
        return 243.12 * g / (17.62 - g);
      };
      const tempVsOm = dT == null ? "" :
        vsOm(useF ? `${(Math.abs(dT) * 9 / 5).toFixed(1)}°F` : `${Math.abs(dT).toFixed(1)}°C`, dT >= 0 ? "warmer" : "cooler");
      const tempTitle = `Temperature <span style="color:${COLOR.dew}">and dew point</span>${tempVsOm}`;
      renderChart(tempTitle, COLOR.temp, UNIT.temp, w => w.temp_c, false, omTemp, { getVal: dewPoint, color: COLOR.dew });

      const omHum = omSeries("relative_humidity_2m"), dH = avgDiff(omHum, w => w.humidity);
      const humVsOm = dH == null ? "" : vsOm(`${Math.abs(dH).toFixed(0)} points`, dH >= 0 ? "higher" : "lower");
      const humTitle = `Humidity${humVsOm}`;
      renderChart(humTitle, COLOR.humidity, UNIT.hum, w => w.humidity, false, omHum);
      renderChart("Rain per hour", COLOR.rain, UNIT.rain, w => w.rain_mm, true);

      // ---- This month vs. normal ----
      if (clim && days.length) {
        const HI = "#dc2626", LO = "#2563eb";
        const ym = days[days.length - 1].window_start.slice(0, 7);
        const [yr, mo] = ym.split("-").map(Number);
        const nDays = new Date(yr, mo, 0).getDate();
        const pad = n => String(n).padStart(2, "0");
        // Percentiles [p10, p25, p50, p75, p90] per day; Feb 29 uses Feb 28's normals
        const norm = Array.from({ length: nDays }, (_, i) => clim.days[`${pad(mo)}-${pad(Math.min(i + 1, mo === 2 ? 28 : 31))}`]);
        const mine = days.filter(d => d.window_start.startsWith(ym) && d.temp_c);
        const todayStr = days[days.length - 1].window_start;

        const mH = 180, mTotal = mH + 14, mPy = 8;
        const xd = day => padL + ((day - 0.5) / nDays) * (W - padL - padR);  // day 1..nDays, centered in its slot
        const vMin = Math.min(...norm.map(n => n.low[0]), ...mine.map(d => d.temp_c.min));
        const vMax = Math.max(...norm.map(n => n.high[4]), ...mine.map(d => d.temp_c.max));
        const axis = chartAxis(vMin, vMax, 8, UNIT.temp);
        const yf = chartYScale(axis.lo, axis.hi, mH, mPy);
        const f = n => n.toFixed(1);
        // Normal bands (p10–p90, p25–p75) and median line, from one [p10, p25, p50, p75, p90] row per day
        const bands = (rows, yf, color) => {
          const pts = (k, rs = rows) => rs.map((r, i) => `${f(xd(i + 1))},${f(yf(r[k]))}`);
          const area = (lo, hi, opacity) =>
            `<polygon points="${[...pts(hi), ...pts(lo).reverse()].join(" ")}" fill="${color}" opacity="${opacity}"/>`;
          return area(0, 4, 0.1) + area(1, 3, 0.15) +
            `<polyline points="${pts(2).join(" ")}" fill="none" stroke="${color}" stroke-width="1.5" opacity="0.6"/>`;
        };
        const labelDays = [1, 5, 10, 15, 20, 25, nDays];
        const dayLines = labelDays.map(day =>
          `<line x1="${f(xd(day))}" y1="0" x2="${f(xd(day))}" y2="${mH}" stroke="#e5e7eb"/>`).join("");
        const dayLabels = labelDays.map(day =>
          `<text x="${f(xd(day))}" y="${mTotal - 2}" text-anchor="middle" font-size="9" fill="#999">${day}</text>`).join("");
        // Plot frame with gridlines and axis labels
        const frame = (svg, axis, yf) => `
          <svg viewBox="0 0 ${W} ${mTotal}" class="chart-svg">
            <rect x="${padL}" y="0" width="${W - padL - padR}" height="${mH}" fill="#f9fafb"/>
            ${dayLines}${chartGrid(axis, yf, padL, W - padR)}${svg}${dayLabels}
          </svg>`;

        let svg = "";
        [["high", HI], ["low", LO]].forEach(([key, c]) => {
          svg += bands(norm.map(n => n[key]), yf, c);
        });
        mine.forEach(d => {
          const day = +d.window_start.slice(8), today = d.window_start === todayStr;
          [[d.temp_c.max, HI], [d.temp_c.min, LO]].forEach(([v, c]) => {
            svg += `<circle cx="${f(xd(day))}" cy="${f(yf(v))}" r="3.5" fill="${today ? "#fff" : c}" stroke="${today ? c : "#fff"}" stroke-width="${today ? 1.5 : 1}"/>`;
          });
        });

        document.getElementById("month-title").textContent =
          `${new Date(yr, mo - 1, 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })} vs. normal`;
        document.getElementById("month-chart").innerHTML = `
          <div class="chart-title"><span style="color:${HI}">● Daily high</span> &nbsp; <span style="color:${LO}">● Daily low</span></div>
          ${frame(svg, axis, yf)}`;

        // Rain so far this month: running totals for this sensor and Vancouver Harbour, over the normal range
        const rainNorm = clim.rain_mtd[pad(mo)];
        const rainRows = Array.from({ length: nDays }, (_, i) => rainNorm[Math.min(i, rainNorm.length - 1)]);  // Feb 29 reuses Feb 28
        let total = 0;
        const myRain = days.filter(d => d.window_start.startsWith(ym) && d.rain_mm != null)
          .map(d => [+d.window_start.slice(8), total += d.rain_mm]);
        // Harbour: stop at its first missing day, since a gap would undercount everything after it
        const hb = {};
        (ec?.features ?? []).forEach(x => { hb[x.properties.LOCAL_DATE.slice(0, 10)] = x.properties.TOTAL_PRECIPITATION; });
        const harbour = [];
        let harbourTotal = 0;
        for (let day = 1; hb[`${ym}-${pad(day)}`] != null; day++) {
          harbourTotal += hb[`${ym}-${pad(day)}`];
          harbour.push([day, harbourTotal]);
        }
        document.getElementById("month-rain-caption").style.display = myRain.length ? "" : "none";
        if (myRain.length) {
          const last = a => a.length ? a[a.length - 1][1] : 0;
          const rMax = Math.max(rainRows[nDays - 1][4], last(myRain), last(harbour));
          const rAxis = chartAxis(0, rMax, 8, UNIT.rain);
          const ry = chartYScale(rAxis.lo, rAxis.hi, mH, mPy);
          const line = (pts, attrs) => `<polyline points="${pts.map(([day, v]) => `${f(xd(day))},${f(ry(v))}`).join(" ")}" fill="none" ${attrs}/>`;
          let rsvg = bands(rainRows, ry, COLOR.rain);
          if (harbour.length) rsvg += line(harbour, `stroke="#9ca3af" stroke-width="1.5" stroke-dasharray="4 3"`);
          rsvg += line(myRain, `stroke="${COLOR.rain}" stroke-width="2"`);
          myRain.forEach(([day, v]) => {
            const today = `${ym}-${pad(day)}` === todayStr;
            rsvg += `<circle cx="${f(xd(day))}" cy="${f(ry(v))}" r="3.5" fill="${today ? "#fff" : COLOR.rain}" stroke="${today ? COLOR.rain : "#fff"}" stroke-width="${today ? 1.5 : 1}"/>`;
          });
          const todayDay = +todayStr.slice(8);
          const harbourNote = harbour.length
            ? ` &nbsp; <span class="harbour-note">- - Vancouver Harbour: ${fmtRain(last(harbour))} through ${new Date(yr, mo - 1, harbour.length).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>`
            : "";
          document.getElementById("month-rain-chart").innerHTML = `
            <div class="chart-title"><span style="color:${COLOR.rain}">● Rain so far: ${fmtRain(last(myRain))}</span>${harbourNote}
              <span class="muted">· normal by today: ${fmtRain(rainRows[todayDay - 1][2])}</span></div>
            ${frame(rsvg, rAxis, ry)}`;
        }
        document.getElementById("month-section").style.display = "block";
      }

      // ---- Daily table (newest first) ----
      const tbody = document.getElementById("daily-body");
      days.slice(-DAILY_ROWS).reverse().forEach((d, i) => {
        const tr = tbody.insertRow();
        // window_start is a bare local date ("2026-11-09"), which JS parses as UTC midnight, so format it in UTC too
        const label = new Date(d.window_start).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', timeZone: 'UTC' });
        [
          i === 0 ? `${label} (so far)` : label,
          fmtTemp(d.temp_c && d.temp_c.min),
          fmtTemp(d.temp_c && d.temp_c.max),
          fmtHum(d.humidity && d.humidity.avg),
          fmtRain(d.rain_mm),
        ].forEach(text => { tr.insertCell().textContent = text; });
      });

      // ---- Forecast accuracy: past days' sensor readings vs. each model's forecast from N days before ----
      if (fc?.hourly) {
        const lead = document.querySelector("input[name=fc-lead]:checked").value;
        const key = document.querySelector("input[name=fc-key]:checked").value;
        const isRain = key === "rain";
        // Only days the sensor covered almost fully, counted from the hourly data (so at most the last 30 days)
        const localDay = ms => new Date(ms).toLocaleDateString('en-CA', { timeZone: tz });  // YYYY-MM-DD
        const hoursCovered = {};
        (data.hourly || []).forEach(w => {
          if ((isRain ? w.rain_mm : w.temp_c) == null) return;
          const day = localDay(new Date(w.window_start).getTime());
          hoursCovered[day] = (hoursCovered[day] || 0) + 1;
        });
        const actual = d => isRain ? d.rain_mm : key === "high" ? d.temp_c?.max : d.temp_c?.min;
        // Skip today, which isn't over yet
        const rows = days.slice(0, -1).filter(d => hoursCovered[d.window_start] >= 22 && actual(d) != null).reverse();

        // A model's forecast for a local day, from its 24 hourly values (Vancouver has no DST, so every day is 24 hours)
        const fcIdx = new Map(fc.hourly.time.map((s, i) => [s, i]));
        const forecast = (model, date) => {
          const i = fcIdx.get(`${date}T00:00`);
          if (i == null) return null;
          // Precipitation is the total over the preceding hour, so the day's rain is 01:00 through the next 00:00
          const vals = isRain
            ? fc.hourly[`precipitation_previous_day${lead}_${model}`].slice(i + 1, i + 25)
            : fc.hourly[`temperature_2m_previous_day${lead}_${model}`].slice(i, i + 24);
          if (vals.length < 24 || vals.includes(null)) return null;
          return isRain ? vals.reduce((s, v) => s + v, 0) : key === "high" ? Math.max(...vals) : Math.min(...vals);
        };

        const fmt = isRain ? fmtRain : fmtTemp;
        // Differences: scale only, no +32
        const fmtDiff = v => isRain ? fmtRain(v) : useF ? `${(v * 9 / 5).toFixed(1)}°F` : `${v.toFixed(1)}°C`;
        // A "close enough" miss: 2°F (1.1°C) or 0.1 in (2.5 mm)
        const tolerance = isRain ? 2.54 : 10 / 9;
        const signed = v => v == null ? "—" : `${v > 0 ? "+" : v < 0 ? "−" : ""}${fmtDiff(Math.abs(v))}`;
        const models = Object.keys(FC_MODELS);
        // Per model: forecast minus actual each day, and (rain) whether it correctly called a rain day or a dry day
        const misses = Object.fromEntries(models.map(m => [m, []]));
        const rainCalls = Object.fromEntries(models.map(m => [m, []]));
        const RAIN_DAY = 1;  // mm
        const label = date => new Date(date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', timeZone: 'UTC' });

        document.getElementById("forecast-head").innerHTML =
          `<tr><th>Date</th><th>Actual</th>${models.map(m => `<th>${FC_MODELS[m]}</th>`).join("")}</tr>`;
        document.getElementById("forecast-body").innerHTML = rows.map(d => {
          const cells = models.map(m => {
            const v = forecast(m, d.window_start);
            if (v != null) {
              misses[m].push(v - actual(d));
              rainCalls[m].push((v >= RAIN_DAY) === (actual(d) >= RAIN_DAY));
            }
            return `<td>${fmt(v)}</td>`;
          });
          return `<tr><td>${label(d.window_start)}</td><td>${fmt(actual(d))}</td>${cells.join("")}</tr>`;
        }).join("");

        const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : null;
        // Standard deviation: how much the misses vary around the model's bias
        const spread = a => {
          if (a.length < 2) return null;
          const m = mean(a);
          return Math.sqrt(mean(a.map(x => (x - m) ** 2)));
        };
        const share = (a, ok) => a.length ? a.filter(ok).length / a.length : null;
        const pct = v => `${Math.round(v * 100)}%`;
        // One stat per model (stat(m)), shaded green from best (strongest, and bold) to worst (faintest).
        // score(v) is lower for better values: by default closer to zero is better.
        const statRow = (name, tip, stat, show, score = Math.abs) => {
          const vals = models.map(stat);
          const scores = vals.filter(v => v != null).map(score);
          const best = Math.min(...scores), worst = Math.max(...scores);
          return `<tr><td>${name} <span class="tip" tabindex="0" data-tip="${tip}"><span class="tip-icon">?</span></span></td><td></td>${vals.map(v => {
            if (v == null) return "<td>—</td>";
            const s = score(v), shade = worst > best ? (worst - s) / (worst - best) : 1;
            return `<td style="background: rgba(22, 163, 74, ${(0.05 + 0.3 * shade).toFixed(2)})"${s === best ? ` class="best"` : ""}>${show(v)}</td>`;
          }).join("")}</tr>`;
        };
        document.getElementById("forecast-foot").innerHTML =
          statRow("Spread", "How much the misses vary from day to day, around the bias (standard deviation). A forecast that's always 3° high has no spread. A steady offset in the sensor doesn't affect it, so it's the fairest comparison between models.",
            m => spread(misses[m]), fmtDiff) +
          statRow("Bias", "Whether the forecast ran high (+) or low (−) on average. A steady bias is easy to adjust for in your head. An offset in the sensor itself shows up as bias for every model.",
            m => mean(misses[m]), signed) +
          statRow(`Days within ${fmtDiff(tolerance)}`, "How often the forecast was close enough to what the sensor measured.",
            m => share(misses[m], x => Math.abs(x) <= tolerance), pct, v => -v) +
          (isRain ? statRow("Rain or not", `How often the forecast correctly called whether there'd be at least ${fmtRain(RAIN_DAY)} of rain that day.`,
            m => share(rainCalls[m], ok => ok), pct, v => -v) : "") +
          statRow("Worst miss", "The forecast's single biggest miss in this period.",
            m => misses[m].length ? Math.max(...misses[m].map(Math.abs)) : null, fmtDiff);
        document.getElementById("forecast-section").style.display = rows.length ? "block" : "none";
      }
    };

    render();
    document.getElementById("weather-units").addEventListener("change", () => {
      useF = document.querySelector("input[name=temp-unit]:checked").value === "F";
      useIn = document.querySelector("input[name=rain-unit]:checked").value === "in";
      render();
    });
    document.getElementById("forecast-options").addEventListener("change", render);

    document.getElementById("weather-status").style.display = "none";
    document.getElementById("weather-content").style.display = "block";
  })
  .catch(err => {
    document.getElementById("weather-status").textContent = `Failed to load: ${err.message}`;
  });
</script>
