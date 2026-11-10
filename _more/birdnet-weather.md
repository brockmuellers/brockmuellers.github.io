---
layout: page
title: BirdNET Weather
permalink: /birdnet-weather/
weather_data_url: https://birdnet-data.brockmuellers.com/weather.json
summary: "Temperature, humidity, and rain at echo-birdnet"
---

Weather at [echo-birdnet]({% link _more/birdnet-station.md %}). Sensors: LaCrosse Temperature and Humidity Sensor, AcuRite Self-Emptying Rain Collector.

<div id="weather-status">Loading...</div>
<div id="weather-content" style="display:none">
  <p style="margin:0 0 1em;color:#555;font-size:13px"><strong>Updated at:</strong> <span id="generated-at-value"></span></p>
  <div id="weather-units" style="margin:0 0 1em;font-size:13px;color:#555">
    Units:
    <label><input type="radio" name="temp-unit" value="F" checked> °F</label>
    <label><input type="radio" name="temp-unit" value="C"> °C</label>
    &nbsp;·&nbsp;
    <label><input type="radio" name="rain-unit" value="in" checked> in</label>
    <label><input type="radio" name="rain-unit" value="mm"> mm</label>
  </div>
  <div id="weather-summary" style="margin:0 0 1.5em;display:flex;flex-direction:column;gap:8px"></div>
  <h3>Last 7 days</h3>
  <div id="weather-charts" style="margin:0 0 0.5em;display:flex;flex-direction:column;gap:16px"></div>
  <p style="margin:0 0 1.5em;font-size:11px;color:#999"><span style="display:inline-block;width:10px;height:10px;background:#e5e7eb;vertical-align:middle"></span> no data from sensor</p>
  <h3>Daily</h3>
  <table style="border-collapse:collapse;font-size:13px">
    <thead>
      <tr>
        <th style="text-align:left;padding:3px 16px 3px 0;font-weight:normal;color:#666;font-size:11px">Date</th>
        <th style="text-align:right;padding:3px 16px 3px 0;font-weight:normal;color:#666;font-size:11px">Low</th>
        <th style="text-align:right;padding:3px 16px 3px 0;font-weight:normal;color:#666;font-size:11px">High</th>
        <th style="text-align:right;padding:3px 16px 3px 0;font-weight:normal;color:#666;font-size:11px">Humidity</th>
        <th style="text-align:right;padding:3px 0;font-weight:normal;color:#666;font-size:11px">Rain</th>
      </tr>
    </thead>
    <tbody id="daily-body"></tbody>
  </table>
</div>

<script>
{
  const url = "{{ page.weather_data_url }}";
  const HOUR = 3600000, DAY = 24 * HOUR;
  const STALE_MINUTES = 30;
  const DAILY_ROWS = 14;
  const COLOR = { temp: "#ea580c", humidity: "#0d9488", rain: "#2563eb" };
  const BG = { yellow: "#fef9c3", red: "#fee2e2", neutral: "#f3f4f6" };
  const FG = { yellow: "#854d0e", red: "#991b1b", neutral: "#374151" };

  // Data is in °C and mm; convert for display based on the unit radios
  let useF = true, useIn = true;
  const fmtTemp = v => v == null ? "—" : useF ? `${(v * 9 / 5 + 32).toFixed(1)}°F` : `${v.toFixed(1)}°C`;
  const fmtHum  = v => v == null ? "—" : `${Math.round(v)}%`;
  const fmtRain = v => v == null ? "—" : useIn ? `${(v / 25.4).toFixed(2)} in` : `${v.toFixed(1)} mm`;

  fetch(url)
    .then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then(data => {
      const tz = data.timezone;
      document.getElementById("generated-at-value").textContent =
        new Date(data.generated_at).toLocaleString('en-US', { timeZone: tz });

      const render = () => {
        document.getElementById("weather-summary").innerHTML = "";
        document.getElementById("weather-charts").innerHTML = "";
        document.getElementById("daily-body").innerHTML = "";

        // ---- Summary chips ----
        const chip = (label, value, color = "neutral") => {
          const el = document.createElement("span");
          el.style.cssText = `display:inline-block;padding:3px 10px;border-radius:4px;font-size:12px;background:${BG[color]};color:${FG[color]}`;
          el.innerHTML = `<span style='opacity:0.7'>${label}:</span> ${value}`;
          return el;
        };
        const chipRow = (rowLabel, chips) => {
          const row = document.createElement("div");
          row.style.cssText = "display:flex;flex-wrap:wrap;gap:6px;align-items:center";
          const lbl = document.createElement("span");
          lbl.style.cssText = "font-size:11px;color:#999;width:70px;flex-shrink:0";
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
        const renderChart = (title, color, fmt, getVal, bars) => {
          if (hours.length < 2) return;
          const present = hours.filter(w => getVal(w) != null);
          if (!present.length) return;
          const t0 = hours[0].t, t1 = hours[hours.length - 1].t + HOUR;
          const xf = t => padL + ((t - t0) / (t1 - t0)) * (W - padL - padR);
          const mid = t => xf(t + HOUR / 2);
          const vMin = bars ? 0 : Math.min(...present.map(w => getVal(w).min));
          const vMax = bars ? Math.max(...present.map(getVal)) : Math.max(...present.map(w => getVal(w).max));
          const vRange = vMax - vMin || 1;
          const yf = v => plotH - py - ((v - vMin) / vRange) * (plotH - 2 * py);
          const f = n => n.toFixed(1);

          let svg = "";
          // Gray slots where the sensor wasn't heard
          hours.forEach(w => {
            if (getVal(w) == null) svg += `<rect x="${f(xf(w.t))}" y="0" width="${f(xf(w.t + HOUR) - xf(w.t))}" height="${plotH}" fill="#e5e7eb"/>`;
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
              svg += `<polygon points="${f(mid(a.t))},${f(yf(va.min))} ${f(mid(b.t))},${f(yf(vb.min))} ${f(mid(b.t))},${f(yf(vb.max))} ${f(mid(a.t))},${f(yf(va.max))}" fill="${color}" opacity="0.15"/>`;
              svg += `<line x1="${f(mid(a.t))}" y1="${f(yf(va.avg))}" x2="${f(mid(b.t))}" y2="${f(yf(vb.avg))}" stroke="${color}" stroke-width="1.5" stroke-linecap="round"/>`;
            }
            // A lone hour (no data on either side) has no line, so draw it as a dot
            hours.forEach((w, i) => {
              const v = getVal(w);
              if (v != null && getVal(hours[i - 1] || {}) == null && getVal(hours[i + 1] || {}) == null)
                svg += `<circle cx="${f(mid(w.t))}" cy="${f(yf(v.avg))}" r="2" fill="${color}"/>`;
            });
          }

          const wrap = document.createElement("div");
          wrap.innerHTML = `
            <div style="font-size:11px;color:${color};margin-bottom:2px">${title}</div>
            <svg viewBox="0 0 ${W} ${H}" style="display:block;width:100%;height:auto">
              <rect x="${padL}" y="0" width="${W - padL - padR}" height="${plotH}" fill="#f9fafb"/>
              ${svg}
              <text x="${padL - 4}" y="${py + 3}" text-anchor="end" font-size="9" fill="#999">${fmt(vMax)}</text>
              <text x="${padL - 4}" y="${plotH - py + 3}" text-anchor="end" font-size="9" fill="#999">${fmt(vMin)}</text>
            </svg>`;
          chartsDiv.appendChild(wrap);
        };

        renderChart("Temperature", COLOR.temp, fmtTemp, w => w.temp_c, false);
        renderChart("Humidity", COLOR.humidity, fmtHum, w => w.humidity, false);
        renderChart("Rain per hour", COLOR.rain, fmtRain, w => w.rain_mm, true);

        // ---- Daily table (newest first) ----
        const tbody = document.getElementById("daily-body");
        days.slice(-DAILY_ROWS).reverse().forEach((d, i) => {
          const tr = tbody.insertRow();
          const label = new Date(d.window_start).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', timeZone: tz });
          const cells = [
            [i === 0 ? `${label} (so far)` : label, "left"],
            [fmtTemp(d.temp_c && d.temp_c.min), "right"],
            [fmtTemp(d.temp_c && d.temp_c.max), "right"],
            [fmtHum(d.humidity && d.humidity.avg), "right"],
            [fmtRain(d.rain_mm), "right"],
          ];
          cells.forEach(([text, align], j) => {
            const td = tr.insertCell();
            td.textContent = text;
            td.style.cssText = `text-align:${align};padding:3px ${j === cells.length - 1 ? 0 : 16}px 3px 0;${j > 0 ? "color:#555" : ""}`;
          });
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
}
</script>
