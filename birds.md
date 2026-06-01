---
layout: page
title: Birds
permalink: /birds/
birds_data_url: https://birdnet-data.brockmuellers.com/birdnet-data.json
---

<div id="birds-status">Loading bird data...</div>
<div id="birds-content" style="display:none">
  <p><strong>Updated at:</strong> <span id="generated-at-value"></span></p>
  <h3>Recent observations</h3>
  <table>
    <thead><tr><th>Bird</th><th>Time</th><th>Confidence</th></tr></thead>
    <tbody id="recent-observations"></tbody>
  </table>
</div>

<script>
(function() {
  var url = "{{ page.birds_data_url }}";

  fetch(url)
    .then(function(response) {
      if (!response.ok) throw new Error("HTTP " + response.status);
      return response.json();
    })
    .then(function(data) {
      document.getElementById("birds-status").style.display = "none";
      document.getElementById("generated-at-value").textContent = new Date(data.generated_at).toLocaleString('en-US', { timeZone: data.timezone });

      var tbody = document.getElementById("recent-observations");
      data.recent_observations.slice(0, 5).forEach(function(obs) {
        var tr = document.createElement("tr");
        tr.innerHTML = "<td>" + obs.common_name + "</td>" +
                       "<td>" + obs.timestamp + "</td>" +
                       "<td>" + Math.round(obs.confidence * 100) + "%</td>";
        tbody.appendChild(tr);
      });

      document.getElementById("birds-content").style.display = "block";
    })
    .catch(function(err) {
      document.getElementById("birds-status").textContent = "Failed to load bird data: " + err.message;
    });
})();
</script>
