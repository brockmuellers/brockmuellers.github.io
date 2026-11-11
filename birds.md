---
layout: page
title: Birds
permalink: /birds/
birds_data_url: https://birdnet-data.brockmuellers.com/birdnet-data.json
---

<div id="birds-status">Loading bird data...</div>
<div id="birds-content" style="display:none">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:1em">
    <a href="/birdnet-station/" style="display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border:2px solid #2d6a4f;border-radius:4px;text-decoration:none;font-size:15px;line-height:1;color:#2d6a4f;background:#f0f7f4;flex-shrink:0">
      <img src="/assets/images/birdnet_logo.png" style="height:22px;width:auto;display:block">
      <span style="position:relative;top:1px">BirdNET Station</span>
    </a>
    <a href="/birdnet-weather/" style="display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border:2px solid #2d6a4f;border-radius:4px;text-decoration:none;font-size:15px;line-height:1;color:#2d6a4f;background:#f0f7f4;flex-shrink:0">
      <span style="font-size:20px;line-height:22px;position:relative;top:2px">🌦</span>
      <span style="position:relative;top:1px">Weather</span>
    </a>
    <span style="font-size:12px;color:#555">Updated at: <span id="generated-at-value"></span></span>
  </div>
  <h3>Recent detections</h3>
  <table id="bird-recent" style="border-collapse:collapse;font-size:13px">
    <thead>
      <tr>
        <th style="text-align:left;padding:3px 12px 3px 0;font-weight:normal;color:#666;font-size:11px">Species</th>
        <th style="text-align:left;padding:3px 12px 3px 0;font-weight:normal;color:#666;font-size:11px">Time</th>
        <th style="text-align:right;padding:3px 0;font-weight:normal;color:#666;font-size:11px">Confidence</th>
      </tr>
    </thead>
    <tbody id="bird-recent-body"></tbody>
  </table>
  <p style="margin:0.5em 0 1em;font-size:11px;color:#999">Using BirdNET-Pi's local time zone (Vancouver) for bird observations.</p>
  <h3>Detections — last 7 days</h3>
  <div style="overflow-x:auto">
    <table id="bird-heatmap" style="border-collapse:collapse;font-size:13px;white-space:nowrap"></table>
  </div>
</div>

<script type="module">
const url = "{{ page.birds_data_url }}";
const GREEN = "#2d6a4f";
const BAR_WIDTH = 120;
const DAY = 24 * 60 * 60 * 1000;

fetch(url)
  .then(r => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  })
  .then(data => {
    // "Updated at" is in the viewer's time zone; observation times are in the station's
    document.getElementById("generated-at-value").textContent =
      new Date(data.generated_at).toLocaleString('en-US');

    // Observation timestamps are the station's local time with no offset ("2026-11-11 08:58:23").
    // Treat them as UTC and format in UTC, so they show the station's clock as-is.
    const obsTime = o => new Date(o.timestamp.replace(' ', 'T') + 'Z');

    // ---- Recent detections ----
    const recentBody = document.getElementById("bird-recent-body");
    data.recent_observations.slice(0, 5).forEach(o => {
      const tr = recentBody.insertRow();
      const tdName = tr.insertCell();
      tdName.textContent = o.common_name;
      tdName.style.cssText = "padding:3px 12px 3px 0";
      const tdTime = tr.insertCell();
      tdTime.textContent = obsTime(o).toLocaleString('en-US', { timeZone: 'UTC' });
      tdTime.style.cssText = "padding:3px 12px 3px 0;color:#555";
      const tdConf = tr.insertCell();
      tdConf.textContent = `${Math.round(o.confidence * 100)}%`;
      tdConf.style.cssText = "text-align:right;padding:3px 0;color:#555";
    });

    // ---- Detections per species and hour, last 7 days ----
    // Station-local clock time of generated_at, on the same footing as obsTime
    const cutoff = new Date(data.generated_at.slice(0, 19) + 'Z').getTime() - 7 * DAY;
    const recent = data.recent_observations.filter(o => obsTime(o).getTime() > cutoff);

    const species = {};
    recent.forEach(o => {
      species[o.common_name] ??= { total: 0, hours: new Array(24).fill(0) };
      species[o.common_name].total++;
      species[o.common_name].hours[parseInt(o.timestamp.split(' ')[1])]++;
    });

    const sorted = Object.keys(species).sort((a, b) => species[b].total - species[a].total);
    const maxTotal = sorted.length ? species[sorted[0]].total : 1;
    const maxHour = Math.max(1, ...sorted.flatMap(name => species[name].hours));

    const table = document.getElementById("bird-heatmap");

    // Header row
    const headerRow = table.createTHead().insertRow();
    const addTh = (text, css = "") => {
      const th = document.createElement("th");
      th.textContent = text;
      th.style.cssText = css;
      headerRow.appendChild(th);
    };
    addTh("", "min-width:140px;padding:2px 8px");
    addTh("Detections", `width:${BAR_WIDTH}px;padding:2px 4px;font-weight:normal;color:#666;font-size:11px`);
    for (let h = 0; h < 24; h++) {
      addTh(h, "width:24px;text-align:center;padding:2px 1px;font-weight:normal;font-size:11px" + (h === 12 ? `;color:${GREEN}` : ""));
    }

    // Data rows
    const tbody = table.createTBody();
    sorted.forEach(name => {
      const s = species[name];
      const tr = tbody.insertRow();

      const tdName = tr.insertCell();
      tdName.textContent = name;
      tdName.style.cssText = "text-align:right;padding:3px 8px";

      const tdBar = tr.insertCell();
      tdBar.style.cssText = `padding:3px 4px;width:${BAR_WIDTH}px`;
      const bar = document.createElement("div");
      const pct = Math.round(s.total / maxTotal * 100);
      bar.style.cssText = `background:${GREEN};height:18px;width:${pct}%;min-width:2px;display:flex;align-items:center;justify-content:flex-end;padding-right:3px;box-sizing:border-box;color:#fff;font-size:11px`;
      bar.textContent = s.total;
      tdBar.appendChild(bar);

      s.hours.forEach(count => {
        const tdH = tr.insertCell();
        tdH.style.cssText = "width:24px;text-align:center;padding:2px 1px;font-size:11px;border:1px solid #f0f0f0";
        if (count > 0) {
          const alpha = 0.2 + (count / maxHour) * 0.8;
          tdH.style.backgroundColor = `rgba(45,106,79,${alpha.toFixed(2)})`;
          tdH.style.color = alpha > 0.55 ? "#fff" : "#333";
          tdH.textContent = count;
        }
      });
    });

    document.getElementById("birds-status").style.display = "none";
    document.getElementById("birds-content").style.display = "block";
  })
  .catch(err => {
    document.getElementById("birds-status").textContent = `Failed to load bird data: ${err.message}`;
  });
</script>
