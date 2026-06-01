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
  <h3>Detections — last 7 days</h3>
  <div style="overflow-x:auto">
    <table id="bird-heatmap" style="border-collapse:collapse;font-size:13px;white-space:nowrap"></table>
  </div>
</div>

<script>
(function() {
  var url = "{{ page.birds_data_url }}";
  var GREEN = "#2d6a4f";
  var BAR_WIDTH = 120;

  fetch(url)
    .then(function(r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(function(data) {
      document.getElementById("generated-at-value").textContent =
        new Date(data.generated_at).toLocaleString('en-US', { timeZone: data.timezone });

      var recentBody = document.getElementById("bird-recent-body");
      var top5 = data.recent_observations.slice(0, 5);
      top5.forEach(function(o) {
        var tr = recentBody.insertRow();
        var tdName = tr.insertCell();
        tdName.textContent = o.common_name;
        tdName.style.cssText = "padding:3px 12px 3px 0";
        var tdTime = tr.insertCell();
        tdTime.textContent = new Date(o.timestamp.replace(' ', 'T')).toLocaleString('en-US', { timeZone: data.timezone });
        tdTime.style.cssText = "padding:3px 12px 3px 0;color:#555";
        var tdConf = tr.insertCell();
        tdConf.textContent = Math.round(o.confidence * 100) + "%";
        tdConf.style.cssText = "text-align:right;padding:3px 0;color:#555";
      });

      var cutoff = new Date(data.generated_at).getTime() - 7 * 24 * 60 * 60 * 1000;
      var recent = data.recent_observations.filter(function(o) {
        return new Date(o.timestamp.replace(' ', 'T')).getTime() > cutoff;
      });

      var species = {};
      recent.forEach(function(o) {
        if (!species[o.common_name]) species[o.common_name] = { total: 0, hours: new Array(24).fill(0) };
        species[o.common_name].total++;
        species[o.common_name].hours[parseInt(o.timestamp.split(' ')[1])]++;
      });

      var sorted = Object.keys(species).sort(function(a, b) {
        return species[b].total - species[a].total;
      });

      var maxTotal = sorted.length ? species[sorted[0]].total : 1;
      var maxHour = 1;
      sorted.forEach(function(name) {
        species[name].hours.forEach(function(c) { if (c > maxHour) maxHour = c; });
      });

      var table = document.getElementById("bird-heatmap");

      // Header row
      var headerRow = table.createTHead().insertRow();
      function addTh(text, css) {
        var t = document.createElement("th");
        t.textContent = text;
        t.style.cssText = css || "";
        headerRow.appendChild(t);
      }
      addTh("", "min-width:140px;padding:2px 8px");
      addTh("Detections", "width:" + BAR_WIDTH + "px;padding:2px 4px;font-weight:normal;color:#666;font-size:11px");
      for (var h = 0; h < 24; h++) {
        addTh(h, "width:24px;text-align:center;padding:2px 1px;font-weight:normal;font-size:11px" + (h === 12 ? ";color:" + GREEN : ""));
      }

      // Data rows
      var tbody = table.createTBody();
      sorted.forEach(function(name) {
        var s = species[name];
        var tr = tbody.insertRow();

        var tdName = tr.insertCell();
        tdName.textContent = name;
        tdName.style.cssText = "text-align:right;padding:3px 8px";

        var tdBar = tr.insertCell();
        tdBar.style.cssText = "padding:3px 4px;width:" + BAR_WIDTH + "px";
        var bar = document.createElement("div");
        var pct = Math.round(s.total / maxTotal * 100);
        bar.style.cssText = "background:" + GREEN + ";height:18px;width:" + pct + "%;min-width:2px;display:flex;align-items:center;justify-content:flex-end;padding-right:3px;box-sizing:border-box;color:#fff;font-size:11px";
        bar.textContent = s.total;
        tdBar.appendChild(bar);

        for (var h = 0; h < 24; h++) {
          var tdH = tr.insertCell();
          tdH.style.cssText = "width:24px;text-align:center;padding:2px 1px;font-size:11px;border:1px solid #f0f0f0";
          var count = s.hours[h];
          if (count > 0) {
            var alpha = 0.2 + (count / maxHour) * 0.8;
            tdH.style.backgroundColor = "rgba(45,106,79," + alpha.toFixed(2) + ")";
            tdH.style.color = alpha > 0.55 ? "#fff" : "#333";
            tdH.textContent = count;
          }
        }
      });

      document.getElementById("birds-status").style.display = "none";
      document.getElementById("birds-content").style.display = "block";
    })
    .catch(function(err) {
      document.getElementById("birds-status").textContent = "Failed to load bird data: " + err.message;
    });
})();
</script>
