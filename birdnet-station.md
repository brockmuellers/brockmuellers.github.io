---
layout: page
title: BirdNET Station
permalink: /birdnet-station/
machine_logs_url: https://birdnet-data.brockmuellers.com/machine-logs.json
---

<div id="machine-status">Loading...</div>
<div id="machine-content" style="display:none">
</div>

<script>
(function() {
  var url = "{{ page.machine_logs_url }}";

  fetch(url)
    .then(function(r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(function(data) {
      document.getElementById("machine-status").style.display = "none";
      document.getElementById("machine-content").style.display = "block";
    })
    .catch(function(err) {
      document.getElementById("machine-status").textContent = "Failed to load: " + err.message;
    });
})();
</script>
