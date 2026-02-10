---
layout: page
title: Travels
permalink: /travels/
# Tabs are defined in _data/travels.yml
---

<link href="https://unpkg.com/maplibre-gl@2.4.0/dist/maplibre-gl.css" rel="stylesheet" />
<script src="https://unpkg.com/maplibre-gl@2.4.0/dist/maplibre-gl.js"></script>

{% assign gpx_base = site.baseurl | append: '/assets/gpx/' %}

<style>
  /* Added wrap for mobile screens */
  .travel-tabs { display: flex; flex-wrap: wrap; gap: 0; margin-bottom: 0; border-bottom: 1px solid #ccc; }
  .travel-tabs button {
    padding: 0.5em 1em;
    border: 1px solid #ccc;
    border-bottom: none;
    background: #f5f5f5;
    cursor: pointer;
    font-size: 1em;
    flex-grow: 1; /* Tabs fill space evenly */
    text-align: center;
  }
  .travel-tabs button:hover { background: #eee; }
  .travel-tabs button.active { background: #fff; margin-bottom: -1px; padding-bottom: calc(0.5em + 1px); font-weight: bold; }

  #map-container { position: relative; width: 100%; height: 500px; margin: 0 0 1em 0; background-color: #f0f0f0; }
  #map { width: 100%; height: 100%; }

  /* Loading overlay */
  #loader {
    display: none;
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(255,255,255,0.7);
    align-items: center; justify-content: center;
    z-index: 10; font-weight: bold; color: #555;
  }
</style>

<div class="travel-tabs" role="tablist">
{% for f in site.data.travels %}
  {% assign name_parts = f | replace: '.gpx', '' | replace: '-', ' ' | split: ' ' %}
  {% capture tab_label %}{% for p in name_parts %}{{ p | capitalize }} {% endfor %}{% endcapture %}

  <button type="button" role="tab"
          data-gpx="{{ gpx_base }}{{ f }}"
          aria-selected="{% if forloop.first %}true{% else %}false{% endif %}"
          class="{% if forloop.first %}active{% endif %}">
      {{ tab_label | strip }}
  </button>
{% endfor %}
</div>

<div id="map-container">
  <div id="loader">Loading Track...</div>
  <div id="map"></div>
</div>

<script>
(function() {
  const gpxCache = {}; // Cache to store parsed coordinates
  let map;
  const loader = document.getElementById('loader');
  let currentRequestId = 0; // Track the latest tab request
  let mapReady = false;     // Becomes true after the map 'load' event fires
  // Helper to toggle loading spinner
  const setLoading = (isLoading) => {
    loader.style.display = isLoading ? 'flex' : 'none';
  };

  function parseGPX(xmlText) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(xmlText, 'text/xml');
    const lines = [];

    // Priority 1: Track Segments
    const segments = doc.querySelectorAll('trkseg');
    if (segments.length > 0) {
      segments.forEach(seg => {
        const line = [];
        seg.querySelectorAll('trkpt').forEach(pt => {
          const lat = parseFloat(pt.getAttribute('lat'));
          const lon = parseFloat(pt.getAttribute('lon'));
          if (!isNaN(lat) && !isNaN(lon)) line.push([lon, lat]);
        });
        if (line.length > 1) lines.push(line);
      });
    } else {
      // Priority 2: Routes or flat tracks
      const pts = doc.querySelectorAll('rtept, trkpt');
      const line = [];
      pts.forEach(pt => {
        const lat = parseFloat(pt.getAttribute('lat'));
        const lon = parseFloat(pt.getAttribute('lon'));
        if (!isNaN(lat) && !isNaN(lon)) line.push([lon, lat]);
      });
      if (line.length > 1) lines.push(line);
    }
    return lines;
  }

  function getBounds(multiLine) {
    const bounds = new maplibregl.LngLatBounds();
    multiLine.forEach(line => {
      line.forEach(coord => bounds.extend(coord));
    });
    return bounds;
  }

  // Load GPX with caching
  function loadGPX(url) {
    if (gpxCache[url]) {
      return Promise.resolve(gpxCache[url]);
    }
    setLoading(true);
    return fetch(url)
      .then(r => {
        if (!r.ok) throw new Error("Network response was not ok");
        return r.text();
      })
      .then(text => {
        const data = parseGPX(text);
        gpxCache[url] = data; // Save to cache
        return data;
      })
      .finally(() => setLoading(false));
  }

  function initMap(multiLineString) {
    const bounds = getBounds(multiLineString);
    map = new maplibregl.Map({
      container: 'map',
      style: {
        version: 8,
        sources: {
          'raster-tiles': {
            type: 'raster',
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
            attribution: '&copy; OpenStreetMap Contributors'
          }
        },
        layers: [{ id: 'simple-tiles', type: 'raster', source: 'raster-tiles', minzoom: 0, maxzoom: 19 }]
      },
      bounds: bounds,
      fitBoundsOptions: { padding: 40 }
    });

    map.on('load', function() {
      mapReady = true;
      // Add source/layer once map is fully loaded
      map.addSource('gpx-track', {
        type: 'geojson',
        data: {
          type: 'Feature',
          properties: {},
          geometry: { type: 'MultiLineString', coordinates: multiLineString }
        }
      });
      map.addLayer({
        id: 'gpx-line',
        type: 'line',
        source: 'gpx-track',
        layout: { 'line-join': 'round', 'line-cap': 'round' },
        paint: { 'line-color': '#d9534f', 'line-width': 4 } // Changed color to a nice red
      });
    });
  }

  function updateMap(multiLineString) {
    // If the map isn't ready yet, wait for the first (and only) 'load' event,
    // but still respect whichever tab was most recently clicked.
    if (!mapReady) {
      const scheduledRequestId = currentRequestId;
      map.once('load', () => {
        if (scheduledRequestId !== currentRequestId) return;
        updateMap(multiLineString);
      });
      return;
    }

    const source = map.getSource('gpx-track');
    if (!source) {
      console.error("GPX source 'gpx-track' is missing.");
      return;
    }

    source.setData({
      type: 'Feature',
      properties: {},
      geometry: { type: 'MultiLineString', coordinates: multiLineString }
    });

    const bounds = getBounds(multiLineString);
    // Ensure bounds are valid before fitting
    if (!bounds.isEmpty()) {
      map.fitBounds(bounds, { padding: 40 });
    }
  }

  // Tab Click Event Listeners
  const buttons = document.querySelectorAll('.travel-tabs button');
  buttons.forEach(btn => {
    btn.addEventListener('click', function() {
      const url = this.getAttribute('data-gpx');
      const requestId = ++currentRequestId;

      // UI Updates
      buttons.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      this.classList.add('active');
      this.setAttribute('aria-selected', 'true');

      // Logic Updates
      loadGPX(url).then(multiLine => {
        // Ignore if a newer tab has been clicked since this request started
        if (requestId !== currentRequestId) return;
        if (multiLine.length === 0) return; // Handle empty GPX gracefully

        if (!map) initMap(multiLine);
        else updateMap(multiLine);
      }).catch(err => console.error("Error processing GPX:", err));
    });
  });

  // Initialize First Tab
  const firstTab = document.querySelector('.travel-tabs button.active');
  if (firstTab) {
    const initialUrl = firstTab.getAttribute('data-gpx');
    const initialRequestId = ++currentRequestId;
    loadGPX(initialUrl).then(multiLine => {
       if (initialRequestId !== currentRequestId) return;
       if (multiLine.length > 0) initMap(multiLine);
    });
  } else {
     document.getElementById('map').innerHTML = '<p style="padding:20px; text-align:center;">No travels found.</p>';
  }

})();
</script>

<p>A rough-and-ready view of my travels over an 18 month sabbatical. </p>
