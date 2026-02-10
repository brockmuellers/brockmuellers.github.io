---
layout: page
title: Travels
permalink: /travels/
# Tabs are defined in _data/travels.yml
# This is proudly cowritten by copilot and gemini pro
---

<link href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css" rel="stylesheet" />
<script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"></script>

{% assign gpx_base = site.baseurl | append: '/assets/gpx/' %}
{% assign obs_file = site.baseurl | append: '/assets/observations/inaturalist.geojson' %}

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

  /* Popup Styles for Observations */
  .maplibregl-popup-content {
    padding: 10px;
    max-width: 200px;
    text-align: center;
    font-family: sans-serif;
  }
  .obs-popup-img {
    width: 100%;
    height: auto;
    border-radius: 4px;
    margin-bottom: 5px;
    display: block;
  }
  .obs-popup-link {
    display: block;
    color: #333;
    text-decoration: none;
    font-weight: bold;
    font-size: 0.9em;
  }
  .obs-popup-link:hover { text-decoration: underline; color: #74ac00; /* iNat Green */ }
</style>

<div class="travel-tabs" role="tablist">
{% for item in site.data.travels %}
  {% assign filename = item.file %}
  {% assign start_date = item.start %}
  {% assign end_date = item.end %}

  {% assign name_parts = filename | replace: '.gpx', '' | replace: '-', ' ' | split: ' ' %}
  {% capture tab_label %}{% for p in name_parts %}{{ p | capitalize }} {% endfor %}{% endcapture %}

  <button type="button" role="tab"
          data-gpx="{{ gpx_base }}{{ filename }}"
          data-start="{{ start_date }}"
          data-end="{{ end_date }}"
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
  const OBS_GEOJSON_URL = "{{ obs_file }}"; // Liquid variable from above

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

  // Filter inaturalist observations by date to match the dates for this tab
  function applyDateFilter(start, end) {
    if (!map || !map.getLayer('inat-points')) return;

    // MapLibre Filter Expression:
    // "ALL conditions must be true: date >= start AND date <= end"
    // We treat dates as strings, which works for YYYY-MM-DD format.
    if (start && end) {
      map.setFilter('inat-points', [
        'all',
        ['>=', ['get', 'date'], start],
        ['<=', ['get', 'date'], end]
      ]);
    } else {
      // If no dates provided, show nothing (or show all, depending on preference)
      // Here we show nothing to keep it clean if dates are missing
      map.setFilter('inat-points', ['==', '1', '0']);
    }
  }

  function initMap(multiLineString, startDate, endDate) {
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

      // --- 1. SETUP GPX TRACK LAYER ---
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

      // --- 2. SETUP OBSERVATIONS LAYER ---
      /**
       * We load the GeoJSON file directly into a MapLibre source.
       * `cluster: true` is optional but nice if you have thousands of points.
       * For simplicity, we are turning clustering OFF here.
       */
      map.addSource('inat-obs', {
        type: 'geojson',
        data: OBS_GEOJSON_URL
      });

      /**
       * Add a circle layer for the observations.
       * We create a white circle with a green border (iNaturalist colors).
       * Filter observations by date to match the tab's date.
       */
      map.addLayer({
        id: 'inat-points',
        type: 'circle',
        source: 'inat-obs',
        paint: {
          'circle-radius': 6,
          'circle-color': '#ffffff',
          'circle-stroke-color': '#74ac00', // iNat Green
          'circle-stroke-width': 2
        }
      });
      applyDateFilter(startDate, endDate);

      // --- 3. INTERACTION LOGIC ---

      /**
       * Change cursor to pointer when hovering over a point
       */
      map.on('mouseenter', 'inat-points', () => {
        map.getCanvas().style.cursor = 'pointer';
      });

      map.on('mouseleave', 'inat-points', () => {
        map.getCanvas().style.cursor = '';
      });

      /**
       * Handle Clicks on Observation Points
       * Creates a popup containing the image and title, hyperlinked to the URL.
       */
      map.on('click', 'inat-points', (e) => {
        // MapLibre returns features under the click. We take the first one.
        // Note: Properties in GeoJSON are sometimes treated as strings, but usually preserved.
        const coordinates = e.features[0].geometry.coordinates.slice();
        const props = e.features[0].properties;

        // Ensure we handle wrapped worlds (MapLibre quirk)
        while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
          coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
        }

        // Construct HTML for the popup
        // Note: We check if properties exist to avoid "undefined" errors
        const imgHtml = props.image_url
          ? `<img src="${props.image_url}" class="obs-popup-img" alt="Observation Photo" />`
          : '';

        const titleHtml = props.title || 'Observation';
        const linkUrl = props.obs_url || '#';

        const popupContent = `
          <a href="${linkUrl}" target="_blank" class="obs-popup-link">
            ${imgHtml}
            ${titleHtml}
          </a>
        `;

        new maplibregl.Popup()
          .setLngLat(coordinates)
          .setHTML(popupContent)
          .addTo(map);
      });
    });
  }

  function updateMap(multiLineString, startDate, endDate) {
    // If the map isn't ready yet, wait for the first (and only) 'load' event,
    // but still respect whichever tab was most recently clicked.
    if (!mapReady) {
      const scheduledRequestId = currentRequestId;
      map.once('load', () => {
        if (scheduledRequestId !== currentRequestId) return;
        updateMap(multiLineString, start, end);
      });
      return;
    }

    const source = map.getSource('gpx-track');
    if (!source) return;

    source.setData({
      type: 'Feature',
      properties: {},
      geometry: { type: 'MultiLineString', coordinates: multiLineString }
    });

    // Update Observation Filter
    applyDateFilter(startDate, endDate);

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
      const start = this.getAttribute('data-start');
      const end = this.getAttribute('data-end');
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

        if (!map) initMap(multiLine, start, end);
        else updateMap(multiLine, start, end);
      }).catch(err => console.error("Error processing GPX:", err));
    });
  });

  // Initialize First Tab
  const firstTab = document.querySelector('.travel-tabs button.active');
  if (firstTab) {
    const initialUrl = firstTab.getAttribute('data-gpx');
    const start = firstTab.getAttribute('data-start');
    const end = firstTab.getAttribute('data-end');
    const initialRequestId = ++currentRequestId;
    loadGPX(initialUrl).then(multiLine => {
       if (initialRequestId !== currentRequestId) return;
       // We allow map init even if multiline is empty, provided we have dates?
       // For now, assume we need a track to start the map.
       if (multiLine.length > 0) initMap(multiLine, start, end);
    });
  } else {
     document.getElementById('map').innerHTML = '<p style="padding:20px; text-align:center;">No travels found.</p>';
  }

})();
</script>

<p>A rough-and-ready view of my travels over an 18 month sabbatical. </p>
