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

// Optional extras: if either fails, the page still renders without it
const getJson = u => fetch(u).then(r => r.ok ? r.json() : null).catch(() => null);
const climP = getJson("{{ '/assets/weather/climatology.json' | relative_url }}");
const omP = getJson("https://api.open-meteo.com/v1/forecast?latitude=49.27&longitude=-123.06&hourly=temperature_2m,relative_humidity_2m&past_days=8&forecast_days=1&timezone=GMT&timeformat=unixtime");
const ecP = getJson("https://api.weather.gc.ca/collections/climate-daily/items?f=json&CLIMATE_IDENTIFIER=1108446&sortby=-LOCAL_DATE&limit=31&properties=LOCAL_DATE,TOTAL_PRECIPITATION");

fetch(url)
  .then(r => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  })
  .then(data => Promise.all([data, climP, omP, ecP]))
  .then(([data, clim, om, ec]) => {
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
        chip("Temp", fmtTemp(th && th.temp_c)),
        chip("Humidity", fmtHum(th && th.humidity)),
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
      if (times.length) for (let t = Math.min(...times); t <= Math.max(...times); t += HOUR) hours.push({ ...byT.get(t), t });

      const chartsDiv = document.getElementById("weather-charts");
      const W = 740, plotH = 90, H = plotH + 14, padL = 44, padR = 4, py = 6;
      const localHour = ms => parseInt(new Date(ms).toLocaleString('en-US', { hour: 'numeric', hourCycle: 'h23', timeZone: tz }));
      const fmtDate = ms => new Date(ms).toLocaleDateString('en-US', { weekday: 'short', month: 'numeric', day: 'numeric', timeZone: tz });

      // getVal(w) returns a number (bars) or {min,max,avg} (band + line), or undefined if missing.
      // ref (optional) is a Map of hour start ms -> value, drawn as a dashed gray comparison line.
      // extra (optional) is {getVal, color}: a second series (one number per hour) drawn as a thin line.
      const renderChart = (title, color, fmt, getVal, bars, ref, extra) => {
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
        const yf = chartYScale(vMin, vMax, plotH, py);
        const f = n => n.toFixed(1);

        let svg = "";
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
            <text x="${padL - 4}" y="${py + 3}" text-anchor="end" font-size="9" fill="#999">${fmt(vMax)}</text>
            <text x="${padL - 4}" y="${plotH - py + 3}" text-anchor="end" font-size="9" fill="#999">${fmt(vMin)}</text>
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
      const tempTitle = `Temperature <span style="color:${COLOR.dew}">and dew point</span>` + (dT == null ? "" :
        vsOm(useF ? `${(Math.abs(dT) * 9 / 5).toFixed(1)}°F` : `${Math.abs(dT).toFixed(1)}°C`, dT >= 0 ? "warmer" : "cooler"));
      renderChart(tempTitle, COLOR.temp, fmtTemp, w => w.temp_c, false, omTemp, { getVal: dewPoint, color: COLOR.dew });

      const omHum = omSeries("relative_humidity_2m"), dH = avgDiff(omHum, w => w.humidity);
      const humTitle = "Humidity" + (dH == null ? "" : vsOm(`${Math.abs(dH).toFixed(0)} points`, dH >= 0 ? "higher" : "lower"));
      renderChart(humTitle, COLOR.humidity, fmtHum, w => w.humidity, false, omHum);
      renderChart("Rain per hour", COLOR.rain, fmtRain, w => w.rain_mm, true);

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
        const yf = chartYScale(vMin, vMax, mH, mPy);
        const f = n => n.toFixed(1);
        // Normal bands (p10–p90, p25–p75) and median line, from one [p10, p25, p50, p75, p90] row per day
        const bands = (rows, yf, color) => {
          const pts = (k, rs = rows) => rs.map((r, i) => `${f(xd(i + 1))},${f(yf(r[k]))}`);
          const area = (lo, hi, opacity) =>
            `<polygon points="${[...pts(hi), ...pts(lo).reverse()].join(" ")}" fill="${color}" opacity="${opacity}"/>`;
          return area(0, 4, 0.1) + area(1, 3, 0.15) +
            `<polyline points="${pts(2).join(" ")}" fill="none" stroke="${color}" stroke-width="1.5" opacity="0.6"/>`;
        };
        const dayLabels = [1, 5, 10, 15, 20, 25, nDays].map(day =>
          `<text x="${f(xd(day))}" y="${mTotal - 2}" text-anchor="middle" font-size="9" fill="#999">${day}</text>`).join("");
        // Plot frame with min/max labels on the y axis
        const frame = (svg, yLabelMax, yLabelMin) => `
          <svg viewBox="0 0 ${W} ${mTotal}" class="chart-svg">
            <rect x="${padL}" y="0" width="${W - padL - padR}" height="${mH}" fill="#f9fafb"/>
            ${svg}${dayLabels}
            <text x="${padL - 4}" y="${mPy + 3}" text-anchor="end" font-size="9" fill="#999">${yLabelMax}</text>
            <text x="${padL - 4}" y="${mH - mPy + 3}" text-anchor="end" font-size="9" fill="#999">${yLabelMin}</text>
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
          ${frame(svg, fmtTemp(vMax), fmtTemp(vMin))}`;

        // Rain so far this month: running totals for this sensor and Vancouver Harbour, over the normal range
        const rainNorm = clim.rain_mtd[pad(mo)];
        const rainRows = Array.from({ length: nDays }, (_, i) => rainNorm[Math.min(i, rainNorm.length - 1)]);  // Feb 29 reuses Feb 28
        let total = 0;
        const myRain = days.filter(d => d.window_start.startsWith(ym) && d.rain_mm != null)
          .map(d => [+d.window_start.slice(8), total += d.rain_mm]);
        // Harbour: stop at its first missing day, since a gap would undercount everything after it
        const hb = {};
        ((ec && ec.features) || []).forEach(x => { hb[x.properties.LOCAL_DATE.slice(0, 10)] = x.properties.TOTAL_PRECIPITATION; });
        const harbour = [];
        for (let day = 1, t = 0; hb[`${ym}-${pad(day)}`] != null; day++) harbour.push([day, t += hb[`${ym}-${pad(day)}`]]);
        document.getElementById("month-rain-caption").style.display = myRain.length ? "" : "none";
        if (myRain.length) {
          const last = a => a.length ? a[a.length - 1][1] : 0;
          const rMax = Math.max(rainRows[nDays - 1][4], last(myRain), last(harbour));
          const ry = chartYScale(0, rMax, mH, mPy);
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
            ? ` &nbsp; <span style="color:#6b7280">- - Vancouver Harbour: ${fmtRain(last(harbour))} through ${new Date(yr, mo - 1, harbour.length).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>`
            : "";
          document.getElementById("month-rain-chart").innerHTML = `
            <div class="chart-title"><span style="color:${COLOR.rain}">● Rain so far: ${fmtRain(last(myRain))}</span>${harbourNote}
              <span class="muted">· normal by today: ${fmtRain(rainRows[todayDay - 1][2])}</span></div>
            ${frame(rsvg, fmtRain(rMax), fmtRain(0))}`;
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
    };

    render();
    document.getElementById("weather-units").addEventListener("change", () => {
      useF = document.querySelector("input[name=temp-unit]:checked").value === "F";
      useIn = document.querySelector("input[name=rain-unit]:checked").value === "in";
      render();
    });

    document.getElementById("weather-status").style.display = "none";
    document.getElementById("weather-content").style.display = "block";
  })
  .catch(err => {
    document.getElementById("weather-status").textContent = `Failed to load: ${err.message}`;
  });
</script>
