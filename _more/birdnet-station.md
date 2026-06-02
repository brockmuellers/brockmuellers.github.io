---
layout: page
title: BirdNET Station
permalink: /birdnet-station/
event_log_url: https://birdnet-data.brockmuellers.com/birdnet-events.json
summary: "Status and logs for echo-birdnet"
---

echo-birdnet — Raspberry Pi running [BirdNET-Pi](https://github.com/mcguirepr89/BirdNET-Pi) with [custom telemetry tools](https://github.com/brockmuellers/birdnet-tools).

<div id="machine-status">Loading...</div>
<div id="machine-content" style="display:none">
  <p style="margin:0 0 1em;color:#555;font-size:13px"><strong>Updated at:</strong> <span id="generated-at-value"></span></p>
  <div id="health-metrics" style="margin:0 0 1em;display:flex;flex-direction:column;gap:8px"></div>
  <div id="metric-charts" style="margin:0 0 1.5em;display:flex;flex-wrap:wrap;gap:16px"></div>
  <div style="margin:0 0 1em;padding-top:0.75em;border-top:1px solid #e5e7eb;display:flex;flex-direction:column;gap:6px">
    <div id="level-filters" style="display:flex;flex-wrap:wrap;gap:6px;align-items:center">
      <span style="font-size:11px;color:#666;font-weight:normal;width:60px;flex-shrink:0">Levels:</span>
    </div>
    <div id="source-filters" style="display:flex;flex-wrap:wrap;gap:6px;align-items:center">
      <span style="font-size:11px;color:#666;font-weight:normal;width:60px;flex-shrink:0">Sources:</span>
    </div>
  </div>
  <table id="event-log" style="border-collapse:collapse;font-size:13px;width:100%">
    <thead>
      <tr>
        <th style="text-align:left;padding:3px 12px 3px 0;font-weight:normal;color:#666;font-size:11px;white-space:nowrap">Time</th>
        <th style="text-align:left;padding:3px 12px 3px 0;font-weight:normal;color:#666;font-size:11px">Level</th>
        <th style="text-align:left;padding:3px 12px 3px 0;font-weight:normal;color:#666;font-size:11px">Source</th>
        <th style="text-align:left;padding:3px 0;font-weight:normal;color:#666;font-size:11px">Message</th>
      </tr>
    </thead>
    <tbody id="event-log-body"></tbody>
  </table>
</div>

<script>
{
  const url = "{{ page.event_log_url }}";

  const LEVEL_STYLE = {
    "INFO":  "color:#2d6a4f",
    "WARN":  "color:#b45309",
    "ERROR": "color:#b91c1c;font-weight:bold"
  };

  fetch(url)
    .then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then(data => {
      document.getElementById("generated-at-value").textContent =
        new Date(data.generated_at).toLocaleString('en-US', { timeZone: data.timezone });

      const h = data.health;
      const healthDiv = document.getElementById("health-metrics");
      const BG = { green: "#dcfce7", yellow: "#fef9c3", red: "#fee2e2", neutral: "#f3f4f6" };
      const FG = { green: "#166534", yellow: "#854d0e", red: "#991b1b", neutral: "#374151" };

      const uploadAge = (new Date(data.generated_at) - new Date(h.last_successful_upload_at)) / 60000;
      const uptimeH = Math.floor(h.uptime_seconds / 3600);
      const uptimeM = Math.floor((h.uptime_seconds % 3600) / 60);

      const T = {
        temp:   { green: 55,  yellow: 70,   higher: false },
        memory: { green: 300, yellow: 100,  higher: true  },
        wifi:   { green: -65, yellow: -80,  higher: true  },
        upload: { green: 20,  yellow: 60,  higher: false },
        disk:   { green: 70,  yellow: 85,   higher: false },
      };

      const CURRENT_METRICS = [
        { label: "Upload",  value: uploadAge,             ...T.upload, fmt: v => v < 60 ? `${Math.round(v)}m ago` : v < 1440 ? `${Math.round(v / 60)}h ago` : ">1d ago" },
        { label: "Disk",    value: h.disk["/"].used_pct,  ...T.disk,   fmt: v => `${v}% used` },
        { label: "Temp",    value: h.temp_c,              ...T.temp,   fmt: v => `${v}°C` },
        { label: "Memory",  value: h.memory_available_mb, ...T.memory, fmt: v => `${Math.round(v)} MB free` },
        { label: "WiFi",    value: h.wifi_signal_dbm,     ...T.wifi,   fmt: v => `${v} dBm` },
        { label: "Uptime",  value: h.uptime_seconds, color: "neutral",
          fmt: () => `${uptimeH > 0 ? uptimeH + "h " : ""}${uptimeM}m` },
      ];

      const windowMetrics = w => [
        { label: "Max Temp",   value: w.temp_c.max,              ...T.temp,   fmt: v => `${v}°C` },
        { label: "Min Memory", value: w.memory_available_mb.min, ...T.memory, fmt: v => `${Math.round(v)} MB free` },
        { label: "Avg WiFi",   value: w.wifi_signal_dbm.avg,     ...T.wifi,   fmt: v => `${Math.round(v)} dBm` },
      ];

      const chipColor = m => {
        if (m.color) return m.color;
        return m.higher
          ? (m.value > m.green ? "green" : m.value > m.yellow ? "yellow" : "red")
          : (m.value <= m.green ? "green" : m.value <= m.yellow ? "yellow" : "red");
      };

      const chip = (label, value, color) => {
        const el = document.createElement("span");
        el.style.cssText = `display:inline-block;padding:3px 10px;border-radius:4px;font-size:12px;background:${BG[color]};color:${FG[color]}`;
        el.innerHTML = `<span style='opacity:0.7'>${label}:</span> ${value}`;
        return el;
      };

      const metricSection = (sectionLabel, metrics) => {
        const row = document.createElement("div");
        row.style.cssText = "display:flex;flex-wrap:wrap;gap:6px;align-items:center";
        const lbl = document.createElement("span");
        lbl.style.cssText = "font-size:11px;color:#999;width:60px;flex-shrink:0";
        lbl.textContent = sectionLabel;
        row.appendChild(lbl);
        metrics.forEach(m => row.appendChild(chip(m.label, m.fmt(m.value), chipColor(m))));
        return row;
      };

      healthDiv.appendChild(metricSection("Current",   CURRENT_METRICS));
      healthDiv.appendChild(metricSection("Last Hour", windowMetrics(data.last_hour)));
      healthDiv.appendChild(metricSection("Last Day",  windowMetrics(data.last_day)));

      const CHART_METRICS = [
        { key: "temp_c",              label: "Temperature", ...T.temp,   fmt: v => `${v.toFixed(1)}°C` },
        { key: "memory_available_mb", label: "Memory Free", ...T.memory, fmt: v => `${Math.round(v)} MB` },
        { key: "wifi_signal_dbm",     label: "WiFi Signal", ...T.wifi,   fmt: v => `${Math.round(v)} dBm` },
      ];

      const windows = [...data.metric_windows].sort((a, b) =>
        new Date(a.window_start).getTime() - new Date(b.window_start).getTime()
      );

      if (windows && windows.length >= 2) {
        const times = windows.map(w => new Date(w.window_start).getTime());
        const tMin = Math.min(...times), tMax = Math.max(...times), tRange = tMax - tMin;
        const chartsDiv = document.getElementById("metric-charts");
        const fmtTime = ms => new Date(ms).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', timeZone: data.timezone, hour12: false });
        const midnightTimes = times.filter(t => fmtTime(t) === '00:00');
        const fmtDate = ms => new Date(ms).toLocaleDateString('en-US', { month: 'numeric', day: 'numeric', timeZone: data.timezone });

        CHART_METRICS.forEach(metric => {
          if (!(metric.key in windows[0])) return;
          const vals = windows.map(w => w[metric.key]);
          const allVals = vals.flatMap(v => [v.min, v.max]);
          const vMin = Math.min(...allVals), vMax = Math.max(...allVals);
          const vRange = vMax - vMin || 1;

          const W = 252, plotH = 67, H = plotH + 12, px = 4, py = 6;
          const xf = t => px + ((t - tMin) / tRange) * (W - 2 * px);
          const yf = v => plotH - py - ((v - vMin) / vRange) * (plotH - 2 * py);

          const bandPts = [
            ...vals.map((v, i) => `${xf(times[i])},${yf(v.min)}`),
            ...[...vals].reverse().map((v, i) => `${xf(times[vals.length - 1 - i])},${yf(v.max)}`),
          ].join(" ");
          const avgPts = vals.map((v, i) => `${xf(times[i])},${yf(v.avg)}`).join(" ");

          const latestColor = chipColor({ ...metric, value: vals[vals.length - 1].avg });

          const wrap = document.createElement("div");
          wrap.style.cssText = "display:flex;flex-direction:column;gap:2px";
          wrap.innerHTML = `
            <div style="font-size:11px;color:#999">${metric.label}</div>
            <div style="display:flex;gap:3px;align-items:flex-start">
              <div style="display:flex;flex-direction:column;justify-content:space-between;font-size:9px;color:#bbb;text-align:right;height:${plotH}px">
                <span>${metric.fmt(vMax)}</span>
                <span>${metric.fmt(vMin)}</span>
              </div>
              <svg width="${W}" height="${H}" style="display:block;border-radius:3px;background:#f9fafb">
                <polygon points="${bandPts}" fill="${BG[latestColor]}" opacity="0.8"/>
                <polyline points="${avgPts}" fill="none" stroke="${FG[latestColor]}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>
                <text x="${px}" y="${H - 2}" text-anchor="start" font-size="9" fill="#bbb">${fmtTime(tMin)}</text>
                <text x="${W - px}" y="${H - 2}" text-anchor="end" font-size="9" fill="#bbb">${fmtTime(tMax)}</text>
                ${midnightTimes.map(t => `<text x="${xf(t).toFixed(1)}" y="${H - 2}" text-anchor="middle" font-size="9" fill="#bbb">${fmtDate(t)}</text>`).join('')}
              </svg>
            </div>`;
          chartsDiv.appendChild(wrap);
        });
      }

      const tbody = document.getElementById("event-log-body");
      const filtersDiv = document.getElementById("source-filters");

      const groupedEvents = [];
      let currentGroup = [];

      data.events.forEach(e => {
        if (currentGroup.length === 0) {
          currentGroup.push(e);
        } else {
          const first = currentGroup[0];
          if (e.level === first.level && e.source === first.source && e.msg === first.msg) {
            currentGroup.push(e);
          } else {
            groupedEvents.push(currentGroup);
            currentGroup = [e];
          }
        }
      });
      if (currentGroup.length > 0) groupedEvents.push(currentGroup);

      const renderRow = (e, isHidden) => {
        const tr = tbody.insertRow();
        if (isHidden) tr.style.display = "none";
        const tdTs = tr.insertCell();
        tdTs.textContent = new Date(e.ts).toLocaleString('en-US', { timeZone: data.timezone });
        tdTs.style.cssText = "padding:3px 12px 3px 0;color:#555;white-space:nowrap";
        const tdLevel = tr.insertCell();
        tdLevel.textContent = e.level;
        tdLevel.style.cssText = `padding:3px 12px 3px 0;white-space:nowrap;${LEVEL_STYLE[e.level] || ""}`;
        const tdSrc = tr.insertCell();
        tdSrc.textContent = e.source;
        tdSrc.style.cssText = "padding:3px 12px 3px 0;color:#555";
        const tdMsg = tr.insertCell();
        tdMsg.textContent = e.msg;
        tdMsg.style.cssText = "padding:3px 0";
        return tr;
      };

      const renderedGroups = groupedEvents.map(group => {
        const mainRow = renderRow(group[0], false);
        let toggleTr = null;
        let hiddenRows = [];
        const groupState = { expanded: false };

        if (group.length > 1) {
          toggleTr = tbody.insertRow();
          const toggleTd = toggleTr.insertCell();
          toggleTd.colSpan = 4;
          toggleTd.style.cssText = "padding:6px 0; text-align:center; background-color:#f9fafb; cursor:pointer; color:#0366d6; font-size:11px; border-top: 1px dashed #e1e4e8; border-bottom: 1px dashed #e1e4e8;";
          toggleTd.textContent = `▼ Expand ${group.length - 1} identical lines`;
          hiddenRows = group.slice(1).map(e => renderRow(e, true));
          toggleTd.addEventListener("click", () => {
            groupState.expanded = !groupState.expanded;
            toggleTd.textContent = groupState.expanded ? "▲ Collapse lines" : `▼ Expand ${group.length - 1} identical lines`;
            hiddenRows.forEach(r => { r.style.display = groupState.expanded ? "table-row" : "none"; });
          });
        }

        return { source: group[0].source, level: group[0].level, mainRow, toggleTr, hiddenRows, state: groupState };
      });

      const hiddenSources = new Set();
      const hiddenLevels = new Set();
      const allSources = [...new Set(renderedGroups.map(g => g.source))].sort();
      const allLevels = [...new Set(renderedGroups.map(g => g.level))].sort();
      const INITIAL_LIMIT = 100;
      let showAll = renderedGroups.length <= INITIAL_LIMIT;

      const applyFilter = () => {
        renderedGroups.forEach((g, i) => {
          const hide = hiddenSources.has(g.source) || hiddenLevels.has(g.level) || (!showAll && i >= INITIAL_LIMIT);
          g.mainRow.style.display = hide ? "none" : "table-row";
          if (g.toggleTr) g.toggleTr.style.display = hide ? "none" : "table-row";
          g.hiddenRows.forEach(r => {
            r.style.display = (hide || !g.state.expanded) ? "none" : "table-row";
          });
        });
      };

      const levelFiltersDiv = document.getElementById("level-filters");
      allLevels.forEach(lvl => {
        const btn = document.createElement("button");
        btn.textContent = lvl;
        btn.style.cssText = "font-size:11px;padding:2px 8px;border:1px solid #ccc;border-radius:3px;background:#fff;cursor:pointer;color:#333";
        btn.addEventListener("click", () => {
          if (hiddenLevels.has(lvl)) {
            hiddenLevels.delete(lvl);
            btn.style.cssText = "font-size:11px;padding:2px 8px;border:1px solid #ccc;border-radius:3px;background:#fff;cursor:pointer;color:#333";
          } else {
            hiddenLevels.add(lvl);
            btn.style.cssText = "font-size:11px;padding:2px 8px;border:1px solid #ccc;border-radius:3px;background:#e9ecef;cursor:pointer;color:#999;text-decoration:line-through";
          }
          applyFilter();
        });
        levelFiltersDiv.appendChild(btn);
      });

      allSources.forEach(src => {
        const btn = document.createElement("button");
        btn.textContent = src;
        btn.style.cssText = "font-size:11px;padding:2px 8px;border:1px solid #ccc;border-radius:3px;background:#fff;cursor:pointer;color:#333";
        btn.dataset.source = src;
        btn.addEventListener("click", () => {
          if (hiddenSources.has(src)) {
            hiddenSources.delete(src);
            btn.style.cssText = "font-size:11px;padding:2px 8px;border:1px solid #ccc;border-radius:3px;background:#fff;cursor:pointer;color:#333";
          } else {
            hiddenSources.add(src);
            btn.style.cssText = "font-size:11px;padding:2px 8px;border:1px solid #ccc;border-radius:3px;background:#e9ecef;cursor:pointer;color:#999;text-decoration:line-through";
          }
          applyFilter();
        });
        filtersDiv.appendChild(btn);
      });

      applyFilter();

      if (!showAll) {
        const showMoreBtn = document.createElement("button");
        showMoreBtn.textContent = `Show all (${renderedGroups.length - INITIAL_LIMIT} more groups)`;
        showMoreBtn.style.cssText = "margin-top:8px;font-size:12px;padding:4px 12px;border:1px solid #ccc;border-radius:3px;background:#fff;cursor:pointer;color:#333";
        showMoreBtn.addEventListener("click", () => {
          showAll = true;
          showMoreBtn.remove();
          applyFilter();
        });
        document.getElementById("event-log").insertAdjacentElement("afterend", showMoreBtn);
      }

      document.getElementById("machine-status").style.display = "none";
      document.getElementById("machine-content").style.display = "block";
    })
    .catch(err => {
      document.getElementById("machine-status").textContent = `Failed to load: ${err.message}`;
    });
}
</script>
