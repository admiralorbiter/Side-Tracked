/**
 * Leaflet Spatial Map Adapter for Sidetrack
 * Clean, high-contrast spatial polyline renderer for pedestrian closed walking loops.
 */
document.addEventListener('DOMContentLoaded', () => {
  const mapElement = document.getElementById('sidetrack-map');
  if (!mapElement || typeof L === 'undefined') return;

  // Default fallback center: Loose Park, Kansas City
  const map = L.map('sidetrack-map', {
    zoomControl: true,
    attributionControl: true
  }).setView([39.0347, -94.5906], 15);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  const geojsonRaw = mapElement.getAttribute('data-geojson');
  if (!geojsonRaw || !geojsonRaw.trim()) return;

  try {
    const geojsonData = JSON.parse(geojsonRaw);
    const coords = geojsonData ? geojsonData.coordinates : [];

    if (coords && coords.length > 0) {
      // High-contrast emerald route polyline
      const geojsonLayer = L.geoJSON(geojsonData, {
        style: {
          color: '#10b981',
          weight: 5,
          opacity: 0.9,
          lineCap: 'round',
          lineJoin: 'round'
        }
      }).addTo(map);

      // Subtle, elegant origin marker pin
      const startCoords = coords[0];
      if (startCoords && startCoords.length >= 2) {
        const startLatLon = [startCoords[1], startCoords[0]];

        const startIcon = L.divIcon({
          className: 'custom-div-icon',
          html: `<div class="map-start-pin"><span class="map-start-dot"></span><span>Start & Finish</span></div>`,
          iconSize: [100, 26],
          iconAnchor: [50, 13]
        });

        L.marker(startLatLon, { icon: startIcon }).addTo(map);
      }

      // Smoothly fit map view to the exact walking loop bounds
      map.fitBounds(geojsonLayer.getBounds(), { padding: [40, 40] });
    }
  } catch (e) {
    console.error('Error rendering route polyline:', e);
  }
});
