/**
 * Leaflet Spatial Map Adapter for Sidetrack
 * Clean, high-contrast spatial polyline renderer with interactive timeline-to-map sub-path sync.
 */
function initSidetrackMap() {
  const mapElement = document.getElementById('sidetrack-map');
  if (!mapElement || typeof L === 'undefined' || mapElement.dataset.initialized === 'true') return;

  mapElement.dataset.initialized = 'true';

  try {
    const map = L.map('sidetrack-map', {
      zoomControl: true,
      attributionControl: true,
      touchZoom: true,
      scrollWheelZoom: false
    }).setView([39.0347, -94.5906], 15);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    const geojsonRaw = mapElement.getAttribute('data-geojson');
    if (!geojsonRaw || !geojsonRaw.trim()) return;

    const geojsonData = JSON.parse(geojsonRaw);
    const coords = geojsonData ? geojsonData.coordinates : [];

    if (coords && coords.length > 0) {
      // High-contrast emerald main route polyline
      const mainLayer = L.geoJSON(geojsonData, {
        style: {
          color: '#10b981',
          weight: 5,
          opacity: 0.9,
          lineCap: 'round',
          lineJoin: 'round'
        }
      }).addTo(map);

      // Origin marker pin
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

      const bounds = mainLayer.getBounds();

      // Parse & render Route Evidence pins on map
      const evidenceRaw = mapElement.getAttribute('data-evidence');
      if (evidenceRaw && evidenceRaw.trim()) {
        try {
          const evidenceItems = JSON.parse(evidenceRaw);
          evidenceItems.forEach((item) => {
            if (item.type === 'exact' && item.lat && item.lon) {
              const name = item.common_name || '';
              let emoji = '🐦';
              if (name.includes('Woodpecker')) emoji = '🪵';
              else if (name.includes('Waxwing')) emoji = '🪶';
              else if (name.includes('Owl')) emoji = '🦉';
              else if (name.includes('Duck') || name.includes('Goose')) emoji = '🦆';

              const evIcon = L.divIcon({
                className: 'custom-div-icon',
                html: `<div class="map-evidence-icon-pin"><span class="map-evidence-emoji">${emoji}</span></div>`,
                iconSize: [32, 32],
                iconAnchor: [16, 16]
              });

              const marker = L.marker([item.lat, item.lon], { icon: evIcon }).addTo(map);

              const tooltipHtml = `
                <div style="font-family: inherit;">
                  <strong style="font-size: 0.88rem; color: #f8fafc;">📍 ${item.common_name}</strong>
                  <div style="font-size: 0.78rem; color: #38bdf8; margin-top: 2px;">Reported ~${item.dist}m from walk</div>
                  <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 1px;">Source: ${item.source}</div>
                </div>
              `;

              // Show hovering tooltip on desktop
              marker.bindTooltip(tooltipHtml, {
                direction: 'top',
                className: 'map-evidence-tooltip',
                offset: [0, -16],
                opacity: 0.98
              });

              // Click popup for mobile tapping
              marker.bindPopup(tooltipHtml);

              bounds.extend([item.lat, item.lon]);
            }
          });
        } catch (e) {
          console.warn('Could not parse route evidence JSON:', e);
        }
      }


      map.fitBounds(bounds, { padding: [40, 40] });


      // Interactive timeline segment hover & focus highlighting using segment-specific GeoJSON

      const segmentCards = document.querySelectorAll('.timeline-segment-card');
      let highlightLayer = null;

      segmentCards.forEach((card) => {
        const highlightSegment = () => {
          const segGeojsonRaw = card.getAttribute('data-segment-geojson');
          mainLayer.setStyle({ opacity: 0.35, weight: 4 });

          if (highlightLayer) {
            map.removeLayer(highlightLayer);
          }

          if (segGeojsonRaw && segGeojsonRaw.trim()) {
            try {
              const segGeojson = JSON.parse(segGeojsonRaw);
              highlightLayer = L.geoJSON(segGeojson, {
                style: {
                  color: '#38bdf8',
                  weight: 8,
                  opacity: 1.0,
                  lineCap: 'round',
                  lineJoin: 'round'
                }
              }).addTo(map);
            } catch (err) {
              console.warn('Could not parse segment GeoJSON:', err);
            }
          }
        };

        const resetHighlight = () => {
          mainLayer.setStyle({ opacity: 0.9, weight: 5 });
          if (highlightLayer) {
            map.removeLayer(highlightLayer);
            highlightLayer = null;
          }
        };

        card.addEventListener('mouseenter', highlightSegment);
        card.addEventListener('mouseleave', resetHighlight);
        card.addEventListener('focus', highlightSegment);
        card.addEventListener('blur', resetHighlight);
      });
    }
  } catch (e) {
    console.error('Error rendering route polyline:', e);
  }
}

document.addEventListener('DOMContentLoaded', initSidetrackMap);
document.addEventListener('htmx:afterSettle', initSidetrackMap);
document.addEventListener('htmx:load', initSidetrackMap);
