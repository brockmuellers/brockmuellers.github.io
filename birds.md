---
layout: page
title: Birds
permalink: /birds/
birds_data_url: https://birdnet-data.brockmuellers.com/birdnet-data.json
---

<style>
  .birdnet-links { display: flex; align-items: center; gap: 12px; margin-bottom: 1em; }
  /* "a." so these beat minima's a:visited and a:hover */
  a.birdnet-link {
    display: inline-flex; align-items: center; gap: 6px; flex-shrink: 0;
    padding: 6px 14px; border: 2px solid #2d6a4f; border-radius: 4px; background: #f0f7f4;
    color: #2d6a4f; text-decoration: none; font-size: 15px; line-height: 1;
  }
  .birdnet-link img { height: 22px; width: auto; display: block; }
  .birdnet-link .label { position: relative; top: 1px; }
  .birdnet-link .emoji { font-size: 20px; line-height: 22px; position: relative; top: 2px; }
  .updated-at { font-size: 12px; color: #555; }
  .note { margin: 0.5em 0 1em; font-size: 11px; color: #999; }

  #bird-recent { border-collapse: collapse; font-size: 13px; }
  #bird-recent th { font-weight: normal; color: #666; font-size: 11px; }
  #bird-recent th, #bird-recent td { text-align: left; padding: 3px 12px 3px 0; }
  #bird-recent td + td { color: #555; }
  #bird-recent th:last-child, #bird-recent td:last-child { text-align: right; padding: 3px 0; }

  #bird-heatmap { border-collapse: collapse; font-size: 13px; white-space: nowrap; }
  #bird-heatmap th.name { min-width: 140px; padding: 2px 8px; }
  #bird-heatmap td.name { text-align: right; padding: 3px 8px; }
  #bird-heatmap th.bar { width: 120px; padding: 2px 4px; font-weight: normal; color: #666; font-size: 11px; }
  #bird-heatmap td.bar { width: 120px; padding: 3px 4px; }
  #bird-heatmap .hour { width: 24px; text-align: center; padding: 2px 1px; font-size: 11px; }
  #bird-heatmap th.hour { font-weight: normal; }
  #bird-heatmap th.noon { color: #2d6a4f; }
  #bird-heatmap td.hour { border: 1px solid #f0f0f0; }
  .bird-bar {
    display: flex; align-items: center; justify-content: flex-end; box-sizing: border-box;
    height: 18px; min-width: 2px; padding-right: 3px; background: #2d6a4f; color: #fff; font-size: 11px;
  }
</style>

<div id="birds-status">Loading bird data...</div>
<div id="birds-content" style="display:none">
  <div class="birdnet-links">
    <a class="birdnet-link" href="/birdnet-station/">
      <img src="/assets/images/birdnet_logo.png">
      <span class="label">BirdNET Station</span>
    </a>
    <a class="birdnet-link" href="/birdnet-weather/">
      <span class="emoji">🌦</span>
      <span class="label">Weather</span>
    </a>
    <span class="updated-at">Updated at: <span id="generated-at-value"></span></span>
  </div>
  <h3>Recent detections</h3>
  <table id="bird-recent">
    <thead>
      <tr><th>Species</th><th>Time</th><th>Confidence</th></tr>
    </thead>
    <tbody id="bird-recent-body"></tbody>
  </table>
  <p class="note">Using BirdNET-Pi's local time zone (Vancouver) for bird observations.</p>
  <h3>Detections — last 7 days</h3>
  <div style="overflow-x:auto">
    <table id="bird-heatmap"></table>
  </div>
</div>

<script type="module">
const url = "{{ page.birds_data_url }}";
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

    // Observation timestamps are station-local with no offset ("2026-11-11 08:58:23"), so borrow generated_at's.
    // Known issue: browsers with pre-permanent-DST tz data show the table an hour off from the heatmap
    // (which reads the hour straight from the string). Fix if needed: append 'Z' instead and format with timeZone: 'UTC'.
    const offset = data.generated_at.slice(-6);  // e.g. "-07:00"
    const obsTime = o => new Date(o.timestamp.replace(' ', 'T') + offset);

    // ---- Recent detections ----
    const recentBody = document.getElementById("bird-recent-body");
    data.recent_observations.slice(0, 5).forEach(o => {
      const tr = recentBody.insertRow();
      const tdName = tr.insertCell();
      tdName.textContent = o.common_name;
      const tdTime = tr.insertCell();
      tdTime.textContent = obsTime(o).toLocaleString('en-US', { timeZone: data.timezone });
      const tdConf = tr.insertCell();
      tdConf.textContent = `${Math.round(o.confidence * 100)}%`;
    });

    // ---- Detections per species and hour, last 7 days ----
    const cutoff = new Date(data.generated_at).getTime() - 7 * DAY;
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
    const addTh = (text, className) => {
      const th = document.createElement("th");
      th.textContent = text;
      th.className = className;
      headerRow.appendChild(th);
    };
    addTh("", "name");
    addTh("Detections", "bar");
    for (let h = 0; h < 24; h++) addTh(h, h === 12 ? "hour noon" : "hour");

    // Data rows
    const tbody = table.createTBody();
    sorted.forEach(name => {
      const s = species[name];
      const tr = tbody.insertRow();

      const tdName = tr.insertCell();
      tdName.textContent = name;
      tdName.className = "name";

      const tdBar = tr.insertCell();
      tdBar.className = "bar";
      const bar = document.createElement("div");
      bar.className = "bird-bar";
      bar.style.width = `${Math.round(s.total / maxTotal * 100)}%`;
      bar.textContent = s.total;
      tdBar.appendChild(bar);

      s.hours.forEach(count => {
        const tdH = tr.insertCell();
        tdH.className = "hour";
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
