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
  <div id="health-metrics" style="margin:0 0 1.5em;display:flex;flex-direction:column;gap:8px"></div>
  <div id="source-filters" style="margin:0 0 1em;display:flex;flex-wrap:wrap;gap:6px;align-items:center">
    <span style="font-size:11px;color:#666;font-weight:normal">Sources:</span>
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
(function() {
  var url = "{{ page.event_log_url }}";

  var LEVEL_STYLE = {
    "INFO":  "color:#2d6a4f",
    "WARN":  "color:#b45309",
    "ERROR": "color:#b91c1c;font-weight:bold"
  };

  fetch(url)
    .then(function(r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(function(data) {
      document.getElementById("generated-at-value").textContent =
        new Date(data.generated_at).toLocaleString('en-US', { timeZone: data.timezone });

      // Health metrics
      var h = data.health;
      var healthDiv = document.getElementById("health-metrics");
      var BG = { green: "#dcfce7", yellow: "#fef9c3", red: "#fee2e2", neutral: "#f3f4f6" };
      var FG = { green: "#166534", yellow: "#854d0e", red: "#991b1b", neutral: "#374151" };

      var uploadAge = (new Date(data.generated_at) - new Date(h.last_successful_upload_at)) / 60000;
      var uptimeH = Math.floor(h.uptime_seconds / 3600);
      var uptimeM = Math.floor((h.uptime_seconds % 3600) / 60);

      var T = {
        temp:   { green: 60,   yellow: 70,   higher: false },
        memory: { green: 300,  yellow: 100,  higher: true  },
        wifi:   { green: -65,  yellow: -80,  higher: true  },
      };

      var CURRENT_METRICS = [
        { label: "Upload",  value: uploadAge,              green: 60,       yellow: 180,      higher: false,
          fmt: function(v) { return v < 60 ? Math.round(v) + "m ago" : v < 1440 ? Math.round(v / 60) + "h ago" : ">1d ago"; } },
        { label: "Temp",    value: h.temp_c,               green: T.temp.green,   yellow: T.temp.yellow,   higher: T.temp.higher,
          fmt: function(v) { return v + "°C"; } },
        { label: "Memory",  value: h.memory_available_mb,  green: T.memory.green, yellow: T.memory.yellow, higher: T.memory.higher,
          fmt: function(v) { return Math.round(v) + " MB free"; } },
        { label: "Disk",    value: h.disk["/"].used_pct,   green: 70,       yellow: 85,       higher: false,
          fmt: function(v) { return v + "% used"; } },
        { label: "WiFi",    value: h.wifi_signal_dbm,      green: T.wifi.green,   yellow: T.wifi.yellow,   higher: T.wifi.higher,
          fmt: function(v) { return v + " dBm"; } },
        { label: "Uptime",  value: h.uptime_seconds, color: "neutral",
          fmt: function() { return (uptimeH > 0 ? uptimeH + "h " : "") + uptimeM + "m"; } },
      ];

      function windowMetrics(w) {
        return [
          { label: "Max Temp",   value: w.temp_c.max,              green: T.temp.green,   yellow: T.temp.yellow,   higher: T.temp.higher,
            fmt: function(v) { return v + "°C"; } },
          { label: "Avg WiFi",   value: w.wifi_signal_dbm.avg,     green: T.wifi.green,   yellow: T.wifi.yellow,   higher: T.wifi.higher,
            fmt: function(v) { return Math.round(v) + " dBm"; } },
          { label: "Min Memory", value: w.memory_available_mb.min, green: T.memory.green, yellow: T.memory.yellow, higher: T.memory.higher,
            fmt: function(v) { return Math.round(v) + " MB free"; } },
        ];
      }

      function chipColor(m) {
        if (m.color) return m.color;
        return m.higher
          ? (m.value > m.green ? "green" : m.value > m.yellow ? "yellow" : "red")
          : (m.value <= m.green ? "green" : m.value <= m.yellow ? "yellow" : "red");
      }

      function chip(label, value, color) {
        var el = document.createElement("span");
        el.style.cssText = "display:inline-block;padding:3px 10px;border-radius:4px;font-size:12px;background:" + BG[color] + ";color:" + FG[color];
        el.innerHTML = "<span style='opacity:0.7'>" + label + ":</span> " + value;
        return el;
      }

      function metricSection(sectionLabel, metrics) {
        var row = document.createElement("div");
        row.style.cssText = "display:flex;flex-wrap:wrap;gap:6px;align-items:center";
        var lbl = document.createElement("span");
        lbl.style.cssText = "font-size:11px;color:#999;width:60px;flex-shrink:0";
        lbl.textContent = sectionLabel;
        row.appendChild(lbl);
        metrics.forEach(function(m) {
          row.appendChild(chip(m.label, m.fmt(m.value), chipColor(m)));
        });
        return row;
      }

      healthDiv.appendChild(metricSection("Current",   CURRENT_METRICS));
      healthDiv.appendChild(metricSection("Last Hour", windowMetrics(data.last_hour)));
      healthDiv.appendChild(metricSection("Last Day",  windowMetrics(data.last_day)));

      var tbody = document.getElementById("event-log-body");
      var filtersDiv = document.getElementById("source-filters");

      // 1. Group sequential identical events
      var groupedEvents = [];
      var currentGroup = [];

      data.events.forEach(function(e) {
        if (currentGroup.length === 0) {
          currentGroup.push(e);
        } else {
          var first = currentGroup[0];
          if (e.level === first.level && e.source === first.source && e.msg === first.msg) {
            currentGroup.push(e);
          } else {
            groupedEvents.push(currentGroup);
            currentGroup = [e];
          }
        }
      });
      if (currentGroup.length > 0) {
        groupedEvents.push(currentGroup);
      }

      // Helper function to build a standard table row
      function renderRow(e, isHidden) {
        var tr = tbody.insertRow();
        if (isHidden) tr.style.display = "none";

        var tdTs = tr.insertCell();
        tdTs.textContent = new Date(e.ts).toLocaleString('en-US', { timeZone: data.timezone });
        tdTs.style.cssText = "padding:3px 12px 3px 0;color:#555;white-space:nowrap";

        var tdLevel = tr.insertCell();
        tdLevel.textContent = e.level;
        tdLevel.style.cssText = "padding:3px 12px 3px 0;white-space:nowrap;" + (LEVEL_STYLE[e.level] || "");

        var tdSrc = tr.insertCell();
        tdSrc.textContent = e.source;
        tdSrc.style.cssText = "padding:3px 12px 3px 0;color:#555";

        var tdMsg = tr.insertCell();
        tdMsg.textContent = e.msg;
        tdMsg.style.cssText = "padding:3px 0";

        return tr;
      }

      // 2. Render the groups, tracking row structure for filtering
      var renderedGroups = [];

      groupedEvents.forEach(function(group) {
        var mainRow = renderRow(group[0], false);
        var toggleTr = null;
        var hiddenRows = [];
        var groupState = { expanded: false };

        if (group.length > 1) {
          toggleTr = tbody.insertRow();
          var toggleTd = toggleTr.insertCell();
          toggleTd.colSpan = 4;
          toggleTd.style.cssText = "padding:6px 0; text-align:center; background-color:#f9fafb; cursor:pointer; color:#0366d6; font-size:11px; border-top: 1px dashed #e1e4e8; border-bottom: 1px dashed #e1e4e8;";
          toggleTd.textContent = "▼ Expand " + (group.length - 1) + " identical lines";

          for (var i = 1; i < group.length; i++) {
            hiddenRows.push(renderRow(group[i], true));
          }

          toggleTd.addEventListener("click", (function(td, rows, state) {
            return function() {
              state.expanded = !state.expanded;
              td.textContent = state.expanded ? "▲ Collapse lines" : "▼ Expand " + (group.length - 1) + " identical lines";
              rows.forEach(function(r) {
                r.style.display = state.expanded ? "table-row" : "none";
              });
            };
          })(toggleTd, hiddenRows, groupState));
        }

        renderedGroups.push({ source: group[0].source, mainRow: mainRow, toggleTr: toggleTr, hiddenRows: hiddenRows, state: groupState });
      });

      // 3. Build source filter buttons
      var hiddenSources = {};
      var allSources = [];
      renderedGroups.forEach(function(g) {
        if (allSources.indexOf(g.source) === -1) allSources.push(g.source);
      });
      allSources.sort();

      function applyFilter() {
        renderedGroups.forEach(function(g) {
          var hide = !!hiddenSources[g.source];
          g.mainRow.style.display = hide ? "none" : "table-row";
          if (g.toggleTr) g.toggleTr.style.display = hide ? "none" : "table-row";
          g.hiddenRows.forEach(function(r) {
            r.style.display = (hide || !g.state.expanded) ? "none" : "table-row";
          });
        });
      }

      allSources.forEach(function(src) {
        var btn = document.createElement("button");
        btn.textContent = src;
        btn.style.cssText = "font-size:11px;padding:2px 8px;border:1px solid #ccc;border-radius:3px;background:#fff;cursor:pointer;color:#333";
        btn.dataset.source = src;
        btn.addEventListener("click", function() {
          if (hiddenSources[src]) {
            delete hiddenSources[src];
            btn.style.cssText = "font-size:11px;padding:2px 8px;border:1px solid #ccc;border-radius:3px;background:#fff;cursor:pointer;color:#333";
          } else {
            hiddenSources[src] = true;
            btn.style.cssText = "font-size:11px;padding:2px 8px;border:1px solid #ccc;border-radius:3px;background:#e9ecef;cursor:pointer;color:#999;text-decoration:line-through";
          }
          applyFilter();
        });
        filtersDiv.appendChild(btn);
      });

      document.getElementById("machine-status").style.display = "none";
      document.getElementById("machine-content").style.display = "block";
    })
    .catch(function(err) {
      document.getElementById("machine-status").textContent = "Failed to load: " + err.message;
    });
})();
</script>
