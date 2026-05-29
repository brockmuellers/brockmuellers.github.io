---
layout: page
title: Birds
permalink: /birds/
birds_data_url: https://birdnet-data.brockmuellers.com/birdnet-data.json
---

<div id="birds-status">Loading bird data...</div>
<div id="birds-content" style="display:none">
  <p id="birds-title" style="text-align:center;font-weight:bold"></p>
  <h3>Last 7 days — by hour</h3>
  <div id="birds-chart" style="overflow-x:auto"></div>
  <h3>All time — by 15-minute window</h3>
  <div id="birds-chart-15min" style="overflow-x:auto"></div>
</div>

<script>
(function() {
  fetch("{{ page.birds_data_url }}")
    .then(function(r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(function(data) {
      document.getElementById("birds-status").style.display = "none";

      // Aggregate recent_observations into { speciesName: { total, hours: {0..23: count} } }
      var species = {};
      data.recent_observations.forEach(function(obs) {
        var name = obs.common_name;
        var hour = parseInt(obs.timestamp.split(" ")[1].split(":")[0], 10);
        if (!species[name]) species[name] = { total: 0, hours: {} };
        species[name].total += 1;
        species[name].hours[hour] = (species[name].hours[hour] || 0) + 1;
      });

      var names = Object.keys(species).sort(function(a, b) {
        return species[b].total - species[a].total;
      });
      var totalAll = names.reduce(function(s, n) { return s + species[n].total; }, 0);
      var maxTotal = species[names[0]].total;
      var maxHour = 0;
      names.forEach(function(n) {
        Object.keys(species[n].hours).forEach(function(h) {
          if (species[n].hours[h] > maxHour) maxHour = species[n].hours[h];
        });
      });

      document.getElementById("birds-title").textContent =
        "All " + names.length + "  |  " + totalAll + " detections  |  Last updated: " + data.generated_at;

      // Build table
      var HOURS = Array.from({length: 24}, function(_, i) { return i; });
      var cellW = "28px";
      var barW = "120px";

      var html = "<table style='border-collapse:collapse;font-size:13px'>";

      // Header row
      html += "<tr>";
      html += "<td style='width:120px'></td>";
      html += "<td style='width:" + barW + ";text-align:center;color:#666;font-size:11px'>Detections</td>";
      HOURS.forEach(function(h) {
        html += "<td style='width:" + cellW + ";text-align:center;color:#666;font-size:11px'>" + h + "</td>";
      });
      html += "</tr>";

      // Species rows
      names.forEach(function(name) {
        var sp = species[name];
        var barPct = (sp.total / maxTotal * 100).toFixed(1);
        html += "<tr>";
        html += "<td style='text-align:right;padding-right:6px;white-space:nowrap'>" + name + "</td>";
        // Bar cell
        html += "<td style='padding:2px 4px'>" +
          "<div style='display:flex;align-items:center;gap:4px'>" +
          "<div style='width:" + barPct + "%;max-width:100px;background:#333;height:14px'></div>" +
          "<span style='font-size:11px'>" + sp.total + "</span>" +
          "</div></td>";
        // Hour cells
        HOURS.forEach(function(h) {
          var count = sp.hours[h] || 0;
          var alpha = count ? (0.15 + 0.85 * count / maxHour).toFixed(2) : 0;
          var bg = count ? "rgba(50,50,50," + alpha + ")" : "#e8e8e8";
          var label = count ? String(count) : "";
          html += "<td style='width:" + cellW + ";height:22px;background:" + bg +
            ";text-align:center;font-size:11px;color:#fff;border:1px solid #ccc'>" + label + "</td>";
        });
        html += "</tr>";
      });

      // Hour-of-day footer label
      html += "<tr><td></td><td style='text-align:center;font-size:11px;color:#666'>Detections</td>";
      html += "<td colspan='24' style='text-align:center;font-size:11px;color:#666;padding-top:4px'>Hour of Day</td></tr>";

      html += "</table>";
      document.getElementById("birds-chart").innerHTML = html;

      // --- 15-minute heatmap ---
      // Aggregate into { speciesName: { total, slots: {"00:00": count, ...} } }
      var SLOTS = [];
      for (var hh = 0; hh < 24; hh++) {
        ["00","15","30","45"].forEach(function(mm) {
          SLOTS.push((hh < 10 ? "0" : "") + hh + ":" + mm);
        });
      }

      var species15 = {};
      Object.keys(data.monthly_stats).forEach(function(month) {
        Object.keys(data.monthly_stats[month]).forEach(function(name) {
          if (!species15[name]) species15[name] = { total: 0, slots: {} };
          var slots = data.monthly_stats[month][name];
          Object.keys(slots).forEach(function(slot) {
            var count = slots[slot];
            species15[name].total += count;
            species15[name].slots[slot] = (species15[name].slots[slot] || 0) + count;
          });
        });
      });

      var names15 = Object.keys(species15).sort(function(a, b) {
        return species15[b].total - species15[a].total;
      });
      var maxTotal15 = species15[names15[0]].total;
      var maxSlot = 0;
      names15.forEach(function(n) {
        Object.keys(species15[n].slots).forEach(function(s) {
          if (species15[n].slots[s] > maxSlot) maxSlot = species15[n].slots[s];
        });
      });

      var cellW15 = "16px";
      var html15 = "<table style='border-collapse:collapse;font-size:11px'>";

      // Header: show hour label on the :00 slot only
      html15 += "<tr><td style='width:120px'></td><td style='width:120px'></td>";
      SLOTS.forEach(function(slot) {
        var label = slot.endsWith(":00") ? slot.split(":")[0] : "";
        html15 += "<td style='width:" + cellW15 + ";text-align:center;color:#666;font-size:10px'>" + label + "</td>";
      });
      html15 += "</tr>";

      names15.forEach(function(name) {
        var sp = species15[name];
        var barPct = (sp.total / maxTotal15 * 100).toFixed(1);
        html15 += "<tr>";
        html15 += "<td style='text-align:right;padding-right:6px;white-space:nowrap'>" + name + "</td>";
        html15 += "<td style='padding:2px 4px'>" +
          "<div style='display:flex;align-items:center;gap:4px'>" +
          "<div style='width:" + barPct + "%;max-width:100px;background:#333;height:14px'></div>" +
          "<span style='font-size:11px'>" + sp.total + "</span>" +
          "</div></td>";
        SLOTS.forEach(function(slot) {
          var count = sp.slots[slot] || 0;
          var alpha = count ? (0.15 + 0.85 * count / maxSlot).toFixed(2) : 0;
          var bg = count ? "rgba(50,50,50," + alpha + ")" : "#e8e8e8";
          html15 += "<td style='width:" + cellW15 + ";height:20px;background:" + bg +
            ";border:1px solid #ccc'></td>";
        });
        html15 += "</tr>";
      });

      html15 += "<tr><td></td><td style='text-align:center;font-size:11px;color:#666'>Detections</td>";
      html15 += "<td colspan='" + SLOTS.length + "' style='text-align:center;font-size:11px;color:#666;padding-top:4px'>Hour of Day</td></tr>";
      html15 += "</table>";

      document.getElementById("birds-chart-15min").innerHTML = html15;
      document.getElementById("birds-content").style.display = "";
    })
    .catch(function(err) {
      document.getElementById("birds-status").textContent = "Failed to load bird data: " + err.message;
    });
})();
</script>
