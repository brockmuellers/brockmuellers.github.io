---
layout: page
title: Travels
permalink: /travels/
gpx_url: /assets/gpx/sample.gpx
---

<link href="https://unpkg.com/maplibre-gl@2.4.0/dist/maplibre-gl.css" rel="stylesheet" />
<script src="https://unpkg.com/maplibre-gl@2.4.0/dist/maplibre-gl.js"></script>

<div id="map" style="width: 100%; height: 500px; margin: 1em 0; background-color: #f0f0f0;"></div>

<script>
(function() {
  const gpxUrl = '{{ page.gpx_url | prepend: site.baseurl }}';

  function parseGPX(xmlText) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(xmlText, 'text/xml');
    
    // We will build a MultiLineString (Array of Arrays of coords)
    // allowing for gaps in the track (segments)
    const lines = [];
    
    // 1. Look for Tracks and Segments
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
      // 2. Fallback for Routes (rte) or flat tracks
      const pts = doc.querySelectorAll('rtept, trkpt');
      const line = [];
      pts.forEach(pt => {
        const lat = parseFloat(pt.getAttribute('lat'));
        const lon = parseFloat(pt.getAttribute('lon'));
        if (!isNaN(lat) && !isNaN(lon)) line.push([lon, lat]);
      });
      if (line.length > 1) lines.push(line);
    }
    
    return lines; // Returns [[x,y], [x,y]], [[x,y], [x,y]]...
  }

  // Rewrite bounds to avoid stack overflow on large arrays
  function getBounds(multiLine) {
    const bounds = new maplibregl.LngLatBounds();
    multiLine.forEach(line => {
      line.forEach(coord => {
        bounds.extend(coord);
      });
    });
    return bounds;
  }

  fetch(gpxUrl)
    .then(r => r.text())
    .then(gpxText => {
      const multiLineString = parseGPX(gpxText);
      
      if (multiLineString.length === 0) {
        document.getElementById('map').innerText = 'No track points found.';
        return;
      }

      const bounds = getBounds(multiLineString);

      const map = new maplibregl.Map({
        container: 'map',
        // We define the style locally using standard OSM raster tiles
        style: {
            'version': 8,
            'sources': {
                'raster-tiles': {
                    'type': 'raster',
                    'tiles': [
                        'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
                    ],
                    'tileSize': 256,
                    'attribution': '&copy; OpenStreetMap Contributors'
                }
            },
            'layers': [{
                'id': 'simple-tiles',
                'type': 'raster',
                'source': 'raster-tiles',
                'minzoom': 0,
                'maxzoom': 19
            }]
        },
        bounds: bounds,
        zoom: 12
      });

      map.on('load', function() {
        map.addSource('gpx-track', {
          type: 'geojson',
          data: {
            type: 'Feature',
            properties: {},
            geometry: {
              type: 'MultiLineString', // Changed from LineString
              coordinates: multiLineString
            }
          }
        });

        map.addLayer({
          id: 'gpx-line',
          type: 'line',
          source: 'gpx-track',
          layout: { 'line-join': 'round', 'line-cap': 'round' },
          paint: {
            'line-color': '#3388ff',
            'line-width': 4
          }
        });
      });
    })
    .catch(err => {
      console.error(err);
      document.getElementById('map').innerText = 'Error loading map.';
    });
})();
</script>

<p>This map loads and displays the GPX file at <code>{{ page.gpx_url }}</code>. Replace <code>gpx_url</code> in the page front matter to show a different track.</p>
