/**
 * Minimal Leaflet Map Adapter for Sidetrack
 * Renders spatial route geometry and habitat markers.
 */
document.addEventListener('DOMContentLoaded', () => {
  const mapElement = document.getElementById('sidetrack-map');
  if (mapElement && typeof L !== 'undefined') {
    // Default KC coordinates (Loose Park)
    const map = L.map('sidetrack-map').setView([39.0347, -94.5906], 14);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    console.log('Sidetrack Leaflet Map Adapter initialized.');
  }
});
