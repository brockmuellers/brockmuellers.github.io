---
layout: page
title: BirdNET Station
permalink: /birdnet-station/
event_log_url: https://birdnet-data.brockmuellers.com/birdnet-events.json
summary: "Status and logs for echo-birdnet"
---

echo-birdnet — Raspberry Pi running [BirdNET-Pi](https://github.com/mcguirepr89/BirdNET-Pi).

<div id="machine-status">Loading...</div>
<div id="machine-content" style="display:none">
  <p style="margin:0 0 1.5em;color:#555;font-size:13px"><strong>Updated at:</strong> <span id="generated-at-value"></span></p>
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
