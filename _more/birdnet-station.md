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
      data.events.forEach(function(e) {
        var tr = tbody.insertRow();
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
      });

      document.getElementById("machine-status").style.display = "none";
      document.getElementById("machine-content").style.display = "block";
    })
    .catch(function(err) {
      document.getElementById("machine-status").textContent = "Failed to load: " + err.message;
    });
})();
</script>
