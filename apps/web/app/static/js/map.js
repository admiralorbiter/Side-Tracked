/**
 * Leaflet Spatial Map Adapter for Sidetrack
 * Clean, high-contrast spatial polyline renderer with interactive timeline-to-map sub-path sync
 * and dynamic route variation geometry switching.
 */

let sidetrackMapInstance = null;
let sidetrackMainPolyline = null;

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

    sidetrackMapInstance = map;

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

      sidetrackMainPolyline = mainLayer;

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

              const icon = L.divIcon({
                className: 'map-evidence-icon-pin',
                html: `<div class="map-evidence-emoji-box" title="${name}">${emoji}</div>`,
                iconSize: [32, 32],
                iconAnchor: [16, 16]
              });

              const marker = L.marker([item.lat, item.lon], { icon: icon }).addTo(map);

              // Tooltip on hover
              const tooltipContent = `
                <div class="map-evidence-tooltip">
                  <strong>📍 ${name}</strong><br>
                  <span style="font-size: 0.75rem; color: #38bdf8;">Reported ~${Math.round(item.distance_from_walk_m)}m from walk</span><br>
                  <span style="font-size: 0.7rem; color: #94a3b8;">Source: ${item.source_dataset}</span>
                </div>
              `;
              marker.bindTooltip(tooltipContent, {
                direction: 'top',
                offset: [0, -10],
                opacity: 0.95
              });

              // Popup on click
              const popupContent = `
                <div style="font-family: inherit; font-size: 0.85rem; padding: 4px;">
                  <strong style="color: #0f172a; font-size: 0.95rem;">${name}</strong><br>
                  <span style="color: #475569; font-size: 0.8rem;">${item.scientific_name || ''}</span>
                  <hr style="margin: 6px 0; border: none; border-top: 1px solid #e2e8f0;">
                  <div style="font-size: 0.78rem; color: #334155;">
                    📍 Reported ~${Math.round(item.distance_from_walk_m)}m from walking loop<br>
                    🛡️ Visibility: ${item.visibility}<br>
                    📅 Reported: ${item.observed_date || 'Recent'}
                  </div>
                </div>
              `;
              marker.bindPopup(popupContent);

              // Extend map bounds to include evidence pins
              bounds.extend([item.lat, item.lon]);
            }
          });
        } catch (err) {
          console.warn('Could not parse route evidence map items:', err);
        }
      }

      map.fitBounds(bounds, { padding: [40, 40] });

      // Interactive hover highlight for timeline segments
      const segmentCards = document.querySelectorAll('.timeline-segment-card[data-segment-index], .segment-card[data-segment-index]');
      let highlightLayer = null;


      segmentCards.forEach((card) => {
        const highlightSegment = () => {
          if (sidetrackMainPolyline) sidetrackMainPolyline.setStyle({ opacity: 0.35 });

          const segGeoRaw = card.getAttribute('data-segment-geojson') || card.dataset.segmentGeojson;
          let subGeo = null;

          if (segGeoRaw && segGeoRaw.trim()) {
            try {
              subGeo = JSON.parse(segGeoRaw);
            } catch (err) {
              console.warn('Could not parse card segment GeoJSON:', err);
            }
          }

          if (highlightLayer) {
            map.removeLayer(highlightLayer);
            highlightLayer = null;
          }

          if (subGeo) {
            highlightLayer = L.geoJSON(subGeo, {
              style: {
                color: '#38bdf8',
                weight: 8,
                opacity: 1.0,
                lineCap: 'round',
                lineJoin: 'round'
              }
            }).addTo(map);
          } else {
            const segIdx = parseInt(card.getAttribute('data-segment-index'), 10);
            const geojsonRaw = mapElement.getAttribute('data-geojson');
            if (geojsonRaw && geojsonRaw.trim()) {
              try {
                const fullGeo = JSON.parse(geojsonRaw);
                const totalCoords = fullGeo.coordinates.length;

                const startIdx = Math.floor((segIdx / segmentCards.length) * totalCoords);
                const endIdx = Math.min(
                  totalCoords,
                  Math.ceil(((segIdx + 1) / segmentCards.length) * totalCoords) + 1
                );

                const subCoords = fullGeo.coordinates.slice(startIdx, endIdx);

                highlightLayer = L.geoJSON({
                  type: 'LineString',
                  coordinates: subCoords
                }, {
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
          }
        };


        const resetHighlight = () => {
          if (sidetrackMainPolyline) sidetrackMainPolyline.setStyle({ opacity: 0.9, weight: 5 });
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

/**
 * Global helper to switch map polyline geometry, color & highlight when selecting a route variation.
 */
window.switchRouteVariation = function(idx, variationName, detourGeojson) {
  if (!sidetrackMapInstance) return;

  const colors = ['#10b981', '#f59e0b', '#38bdf8'];
  const weights = [5, 6, 6];
  const selectedColor = colors[idx % colors.length];
  const selectedWeight = weights[idx % weights.length];

  // Remove existing main polyline layer
  if (sidetrackMainPolyline) {
    sidetrackMapInstance.removeLayer(sidetrackMainPolyline);
  }

  // Draw new distinct detour polyline layer
  if (detourGeojson) {
    sidetrackMainPolyline = L.geoJSON(detourGeojson, {
      style: {
        color: selectedColor,
        weight: selectedWeight,
        opacity: 0.95,
        lineCap: 'round',
        lineJoin: 'round'
      }
    }).addTo(sidetrackMapInstance);

    // Auto-fit map bounds to focus on the new detour path
    sidetrackMapInstance.fitBounds(sidetrackMainPolyline.getBounds(), { padding: [45, 45] });
  }

  // Dispatch global custom event for species radar update
  window.dispatchEvent(new CustomEvent('variation-selected', {
    detail: { index: idx, name: variationName }
  }));
};

document.addEventListener('DOMContentLoaded', initSidetrackMap);
document.addEventListener('htmx:afterSettle', initSidetrackMap);
document.addEventListener('htmx:load', initSidetrackMap);
