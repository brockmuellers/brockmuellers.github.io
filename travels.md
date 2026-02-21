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

  /* Waypoint search */
  .waypoint-search { margin: 1em 0; }
  .waypoint-search label { display: block; font-weight: 600; margin-bottom: 0.35em; }
  .waypoint-search input[type="text"] {
    padding: 0.5em 0.75em;
    width: 100%;
    max-width: 320px;
    font-size: 1em;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
  .waypoint-search input[type="text"]:focus {
    outline: none;
    border-color: #74ac00;
    box-shadow: 0 0 0 2px rgba(116, 172, 0, 0.2);
  }
  .waypoint-search button {
    margin-top: 0.5em;
    padding: 0.5em 1em;
    background: #74ac00;
    color: #fff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
  }
  .waypoint-search button:hover { background: #5d8a00; }
  .waypoint-search button:disabled { opacity: 0.6; cursor: not-allowed; }
  #waypoint-search-results {
    margin-top: 1em;
    padding: 0;
    list-style: none;
  }
  #waypoint-search-results .waypoint-item {
    padding: 1em;
    margin-bottom: 0.75em;
    background: #f9f9f9;
    border-left: 4px solid #74ac00;
    border-radius: 0 4px 4px 0;
  }
  #waypoint-search-results .waypoint-item h4 { margin: 0 0 0.35em 0; font-size: 1.1em; }
  #waypoint-search-results .waypoint-item .waypoint-meta { font-size: 0.85em; color: #666; margin-bottom: 0.5em; }
  #waypoint-search-results .waypoint-item p { margin: 0; line-height: 1.5; }
  #waypoint-search-results .search-error { color: #c00; padding: 0.75em; }
  #waypoint-search-results .search-empty { color: #666; font-style: italic; padding: 0.75em; }
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

<div class="waypoint-search">
  <label for="waypoint-query">Search waypoints</label>
  <input type="text" id="waypoint-query" placeholder="e.g. ancient temples" aria-label="Search waypoints by keyword" />
  <button type="button" id="waypoint-search-btn">Search</button>
  <div id="waypoint-search-results" aria-live="polite"></div>
</div>

<script>
(function() {
  const gpxCache = {}; // Cache to store parsed coordinates
  const OBS_GEOJSON_URL = "{{ obs_file }}"; // Liquid variable from above
  const TRAVEL_LOG_SITE_TOKEN = "{{ site.travel_log_site_token | default: '' }}";
  const WAYPOINT_SEARCH_API = "{{ site.travel_log_waypoint_search_api }}";

  // Logic for WORLD placeholder: Create a list of all real GPX files
  const ALL_TRACKS = [
    {% for item in site.data.travels %}
      {% unless item.file == 'WORLD' %}
        "{{ gpx_base }}{{ item.file }}",
      {% endunless %}
    {% endfor %}
  ];

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
       * We create a circle with a green border (iNaturalist colors).
       * Filter observations by date to match the tab's date.
       */
      map.addLayer({
        id: 'inat-points',
        type: 'circle',
        source: 'inat-obs',
        paint: {
          'circle-radius': 5,
          'circle-stroke-color': '#74ac00', // iNat Green border
          'circle-stroke-width': 3,

          // LOGIC: Color based on "counts" property; black for rarest sightings -> red -> white
          'circle-color': [
            'step',
            ['to-number', ['get', 'global_count']],

            '#000000',
            5, '#4a0404',
            20, '#7f0000',
            75, '#b30000',
            250, '#d73027',
            1000, '#f46d43',
            3500, '#fdae61',
            10000, '#fee090',
            25000, '#ffffbf',
            50000, '#ffffff'
          ]
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
        const obsCount = props.global_count || '[Unknown]';

        const popupContent = `
          <a href="${linkUrl}" target="_blank" class="obs-popup-link">
            ${imgHtml}
            ${titleHtml}
          </a>
          ${obsCount} global observations
        `;

        new maplibregl.Popup()
          .setLngLat(coordinates)
          .setHTML(popupContent)
          .addTo(map);
      });

      // --- Right Click (Context Menu) for Coordinates ---

      // 1. Prevent the default browser menu from appearing
      map.getCanvas().addEventListener('contextmenu', (e) => e.preventDefault());

      // 2. Show coordinates on right-click
      map.on('contextmenu', (e) => {
        const lat = e.lngLat.lat.toFixed(5);
        const lon = e.lngLat.lng.toFixed(5);

        new maplibregl.Popup({ closeButton: false }) // Hide the "x" since clicking elsewhere closes it
          .setLngLat(e.lngLat)
          .setHTML(`
            <div style="text-align:center; font-size: 0.9em; padding: 5px;">
              <strong>${lat}, ${lon}</strong><br>
              <button onclick="navigator.clipboard.writeText('${lat}, ${lon}')" style="margin-top:5px; cursor:pointer;">
                Copy to Clipboard
              </button>
            </div>
          `)
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

      // Check if this is the "World View" tab
      if (url.includes('WORLD')) {
        // Load ALL tracks and combine them into one flat array
        trackPromise = Promise.all(ALL_TRACKS.map(u => loadGPX(u)))
                              .then(results => results.flat());
      } else {
        // Load just the single track
        trackPromise = loadGPX(url);
      }

      trackPromise.then(multiLine => {
        // Ignore if a newer tab has been clicked since this request started
        if (requestId !== currentRequestId) return;
        if (multiLine.length === 0) return;

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

    let trackPromise;
    if (initialUrl.includes('WORLD')) {
      // If the first tab is World, load ALL tracks
      trackPromise = Promise.all(ALL_TRACKS.map(u => loadGPX(u)))
                            .then(results => results.flat());
    } else {
      // Otherwise, load the single file
      trackPromise = loadGPX(initialUrl);
    }

    trackPromise.then(multiLine => {
       if (initialRequestId !== currentRequestId) return;
       // We allow map init even if multiline is empty, provided we have dates?
       // For now, assume we need a track to start the map.
       if (multiLine.length > 0) initMap(multiLine, start, end);
    }).catch(err => console.error("Error loading initial tab:", err));
  } else {
     document.getElementById('map').innerHTML = '<p style="padding:20px; text-align:center;">No travels found.</p>';
  }

  // --- Waypoint search ---
  const waypointQuery = document.getElementById('waypoint-query');
  const waypointSearchBtn = document.getElementById('waypoint-search-btn');
  const waypointResults = document.getElementById('waypoint-search-results');

  function renderWaypointResults(data) {
    if (!Array.isArray(data) || data.length === 0) {
      waypointResults.innerHTML = '<p class="search-empty">No waypoints found. Try another search.</p>';
      return;
    }
    waypointResults.innerHTML = data.map(function(item) {
      const score = typeof item.score === 'number' ? item.score.toFixed(1) : item.score;
      const dist = typeof item.distance === 'number' ? item.distance.toFixed(3) : item.distance;
      return (
        '<li class="waypoint-item">' +
          '<h4>' + (item.name || 'Unnamed') + '</h4>' +
          '<div class="waypoint-meta">Score: ' + score + (item.distance != null ? ' &middot; Distance: ' + dist : '') + '</div>' +
          (item.description ? '<p>' + item.description + '</p>' : '') +
        '</li>'
      );
    }).join('');
  }

  function doWaypointSearch() {
    const q = (waypointQuery.value || '').trim();
    if (!q) {
      waypointResults.innerHTML = '<p class="search-empty">Enter a search term (e.g. ancient temples).</p>';
      return;
    }
    waypointResults.innerHTML = '<p class="search-empty">Searching…</p>';
    waypointSearchBtn.disabled = true;

    const url = WAYPOINT_SEARCH_API + '?q=' + encodeURIComponent(q);
    const headers = { 'Accept': 'application/json' };
    if (TRAVEL_LOG_SITE_TOKEN) headers['X-Site-Token'] = TRAVEL_LOG_SITE_TOKEN;

    fetch(url, { headers: headers })
      .then(function(r) {
        if (!r.ok) throw new Error(r.status === 401 ? 'Invalid or missing site token. Set travel_log_site_token in _config.yml.' : 'Search failed: ' + r.status);
        return r.json();
      })
      .then(function(data) {
        renderWaypointResults(data);
      })
      .catch(function(err) {
        waypointResults.innerHTML = '<p class="search-error">' + (err.message || 'Search failed.') + '</p>';
      })
      .finally(function() {
        waypointSearchBtn.disabled = false;
      });
  }

  if (waypointSearchBtn && waypointQuery) {
    waypointSearchBtn.addEventListener('click', doWaypointSearch);
    waypointQuery.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') { e.preventDefault(); doWaypointSearch(); }
    });
  }

})();
</script>

<p>A rough-and-ready view of my travels over an 18 month sabbatical. </p>
