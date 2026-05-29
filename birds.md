---
layout: page
title: Birds
permalink: /birds/
birds_data_url: https://birdnet-data.brockmuellers.com/birdnet-data.json
---

<div id="birds-status">Loading bird data...</div>
<div id="birds-generated-at" style="display:none">
  <p><strong>Data generated at:</strong> <span id="generated-at-value"></span></p>
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
      document.getElementById("generated-at-value").textContent = data.generated_at;
      document.getElementById("birds-generated-at").style.display = "block";
    })
    .catch(function(err) {
      document.getElementById("birds-status").textContent = "Failed to load bird data: " + err.message;
    });
})();
</script>
