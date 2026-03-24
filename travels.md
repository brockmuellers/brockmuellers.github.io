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
  .waypoint-search input[type="text"]:disabled {
    background: #f0f0f0;
    color: #999;
    cursor: not-allowed;
    border-color: #ddd;
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
  #waypoint-api-status { margin-left: 0.5em; font-size: 0.85em; color: #c00; }
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
  #waypoint-search-results .waypoint-item h4 button { background: none; border: none; padding: 0; font: inherit; font-weight: bold; color: inherit; cursor: pointer; text-decoration: underline dotted; }
  #waypoint-search-results .waypoint-item h4 button:hover { color: #74ac00; }
  #waypoint-search-results .waypoint-item .waypoint-meta { font-size: 0.85em; color: #666; margin-bottom: 0.5em; }
  #waypoint-search-results .waypoint-item p { margin: 0; line-height: 1.5; }
  #waypoint-search-results .waypoint-item .waypoint-photos { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.4em; margin-top: 0.6em; }
  #waypoint-search-results .waypoint-item .waypoint-photos img { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 3px; cursor: default; }
  #waypoint-search-results .search-error { color: #c00; padding: 0.75em; }
  #waypoint-search-results .search-empty { color: #666; font-style: italic; padding: 0.75em; }

  #map-legend {
    position: absolute;
    bottom: 30px;
    left: 10px;
    background: rgba(255,255,255,0.85);
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 0.75em;
    line-height: 1.8;
    z-index: 1;
  }
  #map-legend summary { cursor: pointer; color: #555; }
  .legend-item { display: flex; align-items: center; gap: 7px; margin-top: 4px; }
  .legend-swatch { display: inline-block; width: 20px; border-bottom: 3px solid; }
  .legend-swatch.dashed { border-bottom-style: dashed; border-bottom-width: 2px; }
  .legend-divider { margin: 6px 0; border: none; border-top: 1px solid #ccc; }
  .legend-section-label { font-weight: bold; margin-bottom: 2px; }
  .legend-gradient-row { display: flex; align-items: center; gap: 5px; margin-top: 4px; }
.legend-gradient-bar { width: 60px; height: 8px; border-radius: 3px; border: 1px solid #ccc; background: linear-gradient(to right, #000000, #4a0404, #7f0000, #b30000, #d73027, #f46d43, #fdae61, #fee090, #ffffbf, #ffffff); }
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
  <details id="map-legend">
    <summary>legend</summary>
    <div class="legend-section-label">transport mode</div>
    <div class="legend-item"><span class="legend-swatch dashed" style="border-color:#9333ea"></span>flight</div>
    <div class="legend-item"><span class="legend-swatch" style="border-color:#06b6d4"></span>ferry</div>
    <div class="legend-item"><span class="legend-swatch" style="border-color:#0284c7"></span>motorboat</div>
    <div class="legend-item"><span class="legend-swatch" style="border-color:#eab308"></span>train</div>
    <div class="legend-item"><span class="legend-swatch" style="border-color:#f97316"></span>bus</div>
    <div class="legend-item"><span class="legend-swatch" style="border-color:#ef4444"></span>car</div>
    <div class="legend-item"><span class="legend-swatch" style="border-color:#b45309"></span>4x4</div>
    <div class="legend-item"><span class="legend-swatch" style="border-color:#f43f5e"></span>motorbike</div>
    <div class="legend-item"><span class="legend-swatch" style="border-color:#22c55e"></span>walking</div>
    <div class="legend-item"><span class="legend-swatch" style="border-color:#15803d"></span>hiking</div>
    <hr class="legend-divider">
    <div class="legend-section-label">observations</div>
    <div class="legend-gradient-row">
      <span>rare</span>
      <span class="legend-gradient-bar"></span>
      <span>common</span>
    </div>
  </details>
</div>

<div class="waypoint-search">
  <label for="waypoint-query">Search waypoints</label>
  <input type="text" id="waypoint-query" placeholder="e.g. ancient temples" aria-label="Search waypoints by keyword" />
  <button type="button" id="waypoint-search-btn">Search</button>
  <span id="waypoint-api-status"></span>
  <div id="waypoint-search-results" aria-live="polite"></div>
</div>

<script>
(function() {
  const gpxCache = {}; // Cache to store parsed coordinates
  const OBS_GEOJSON_URL = "{{ obs_file }}"; // Liquid variable from above
  const TRAVEL_LOG_SITE_TOKEN = "{{ site.travel_log_site_token | default: '' }}";
  const TRAVEL_LOG_API = "{{ site.travel_log_api }}";

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

  function getBounds(features) {
    const bounds = new maplibregl.LngLatBounds();
    features.forEach(f => f.geometry.coordinates.forEach(coord => bounds.extend(coord)));
    return bounds;
  }

  // Load pre-generated GeoJSON (derived from GPX) with caching
  function loadGPX(url) {
    const geojsonUrl = url.replace('.gpx', '.geojson');
    if (gpxCache[geojsonUrl]) {
      return Promise.resolve(gpxCache[geojsonUrl]);
    }
    setLoading(true);
    return fetch(geojsonUrl)
      .then(r => {
        if (!r.ok) throw new Error("Network response was not ok");
        return r.json();
      })
      .then(fc => {
        gpxCache[geojsonUrl] = fc.features;
        return fc.features;
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
        data: { type: 'FeatureCollection', features: multiLineString }
      });
      const transportColor = ['match', ['get', 'transport'],
        /* air */
        'flight',    '#9333ea',
        /* water */
        'ferry',     '#06b6d4',
        'motorboat', '#0284c7',
        /* rail */
        'train',     '#eab308',
        /* road */
        'bus',       '#f97316',
        'car',       '#ef4444',
        '4x4',       '#b45309',
        'motorbike', '#f43f5e',
        /* foot */
        'walking',   '#22c55e',
        'hiking',    '#15803d',
        /* default */ '#d9534f'
      ];
      map.addLayer({
        id: 'gpx-line',
        type: 'line',
        source: 'gpx-track',
        filter: ['!=', ['get', 'transport'], 'flight'],
        layout: { 'line-join': 'round', 'line-cap': 'round' },
        paint: { 'line-width': 4, 'line-color': transportColor }
      });
      map.addLayer({
        id: 'gpx-line-flight',
        type: 'line',
        source: 'gpx-track',
        filter: ['==', ['get', 'transport'], 'flight'],
        layout: { 'line-join': 'round', 'line-cap': 'round' },
        paint: { 'line-width': 2, 'line-color': transportColor, 'line-dasharray': [4, 4] }
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
          'circle-radius': ['interpolate', ['linear'], ['zoom'], 0, 3, 8, 5],
          'circle-stroke-color': '#74ac00', // iNat Green border
          'circle-stroke-width': ['interpolate', ['linear'], ['zoom'], 0, 1, 8, 3],

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

      // --- Waypoints layer ---
      const diamondSize = 12;
      const diamondCanvas = document.createElement('canvas');
      diamondCanvas.width = diamondSize;
      diamondCanvas.height = diamondSize;
      const dctx = diamondCanvas.getContext('2d');
      const h = diamondSize / 2;
      dctx.beginPath();
      dctx.moveTo(h, 0); dctx.lineTo(diamondSize, h); dctx.lineTo(h, diamondSize); dctx.lineTo(0, h);
      dctx.closePath();
      dctx.fillStyle = '#e2e8f0';
      dctx.fill();
      dctx.strokeStyle = '#64748b';
      dctx.lineWidth = 2;
      dctx.stroke();
      const diamondData = dctx.getImageData(0, 0, diamondSize, diamondSize);
      map.addImage('waypoint-diamond', { width: diamondSize, height: diamondSize, data: diamondData.data });

      map.addSource('waypoints', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });
      map.addLayer({
        id: 'waypoints',
        type: 'symbol',
        source: 'waypoints',
        layout: {
          'icon-image': 'waypoint-diamond',
          'icon-size': ['interpolate', ['linear'], ['zoom'], 0, 0.5, 8, 0.83],
          'icon-allow-overlap': true
        }
      });

      const waypointHeaders = { 'Accept': 'application/json' };
      if (TRAVEL_LOG_SITE_TOKEN) waypointHeaders['X-Site-Token'] = TRAVEL_LOG_SITE_TOKEN;
      fetch(TRAVEL_LOG_API + '/waypoints', { headers: waypointHeaders })
        .then(r => r.json())
        .then(waypoints => {
          const features = waypoints
            .filter(w => w.coordinates)
            .map(w => ({
              type: 'Feature',
              geometry: { type: 'Point', coordinates: w.coordinates },
              properties: { id: w.id, name: w.name, description: w.description, photo_url: w.photo_url || null }
            }));
          map.getSource('waypoints').setData({ type: 'FeatureCollection', features });
        })
        .catch(() => {}); // API down → map works normally with no waypoints shown

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
        if (map.queryRenderedFeatures(e.point, { layers: ['waypoints'] }).length > 0) return;
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

      map.on('mouseenter', 'waypoints', () => { map.getCanvas().style.cursor = 'pointer'; });
      map.on('mouseleave', 'waypoints', () => { map.getCanvas().style.cursor = ''; });
      map.on('click', 'waypoints', (e) => {
        const props = e.features[0].properties;
        const coords = e.features[0].geometry.coordinates.slice();
        new maplibregl.Popup()
          .setLngLat(coords)
          .setHTML(`<strong>${props.name}</strong>${props.photo_url ? `<img src="${props.photo_url}" class="obs-popup-img" alt="${props.name}" />` : ''}`)
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

    source.setData({ type: 'FeatureCollection', features: multiLineString });

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
      const photos = Array.isArray(item.photos) ? item.photos.slice(0, 5) : [];
      const photosHtml = photos.length === 0 ? '' :
        '<div class="waypoint-photos">' +
          photos.map(function(photo) {
            const src = photo.url || '';
            const caption = (photo.caption || '').replace(/"/g, '&quot;');
            return '<img src="' + src + '" title="' + caption + '" alt="' + caption + '" />';
          }).join('') +
        '</div>';
      return (
        '<li class="waypoint-item">' +
          '<h4>' + (item.coordinates ? '<button data-coordinates="' + item.coordinates + '">' + (item.name || 'Unnamed') + '</button>' : (item.name || 'Unnamed')) + '</h4>' +
          '<div class="waypoint-meta">Score: ' + score + (item.distance != null ? ' &middot; Distance: ' + dist : '') +
            (item.description_distance != null ? ' &middot; Desc: ' + item.description_distance.toFixed(3) : '') +
            (item.photo_distance != null ? ' &middot; Photo: ' + item.photo_distance.toFixed(3) : '') +
          '</div>' +
          (item.description ? '<p>' + item.description + '</p>' : '') +
          photosHtml +
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

    const activeTab = document.querySelector('.travel-tabs button.active');
    const activeGpx = activeTab ? activeTab.getAttribute('data-gpx') : '';
    const isWorld = activeGpx.includes('WORLD');
    // Strip path prefix and .gpx extension from data-gpx, e.g. "/assets/gpx/west-coast.gpx" → "west-coast"
    const tripSlug = isWorld ? null : activeGpx.replace(/^.*\//, '').replace('.gpx', '');
    const url = TRAVEL_LOG_API + '/waypoints/search?q=' + encodeURIComponent(q) +
      (tripSlug ? '&trip=' + encodeURIComponent(tripSlug) : '');
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

    waypointResults.addEventListener('click', function(e) {
      var btn = e.target.closest('button[data-coordinates]');
      if (!btn || !map) return;
      var coords = btn.getAttribute('data-coordinates').split(',').map(Number);
      map.flyTo({ center: coords, zoom: 13 });
    });

    // Health check on page load — disable search if API is unreachable
    var healthHeaders = { 'Accept': 'application/json' };
    if (TRAVEL_LOG_SITE_TOKEN) healthHeaders['X-Site-Token'] = TRAVEL_LOG_SITE_TOKEN;
    fetch(TRAVEL_LOG_API + '/health', { headers: healthHeaders })
      .then(function(r) {
        if (!r.ok) throw new Error('API returned ' + r.status);
      })
      .catch(function() {
        waypointQuery.disabled = true;
        waypointSearchBtn.disabled = true;
        document.getElementById('waypoint-api-status').textContent = 'Search unavailable (API offline)';
      });
  }

})();
</script>

<p>A rough-and-ready view of my travels over an 18 month sabbatical. </p>
