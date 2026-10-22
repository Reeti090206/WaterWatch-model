/**
 * WaterWatch AI Integration — Leaflet Nagpur Map Controller
 * Manages layer toggles, custom SVG icons, popup formatting, and route polyline rendering.
 */

class NagpurMapController {
  constructor(mapContainerId = 'nagpur-map') {
    this.containerId = mapContainerId;
    this.map = null;
    this.layers = {
      incidents: L.layerGroup(),
      closures: L.layerGroup(),
      hotspots: L.layerGroup(),
      reports: L.layerGroup(),
      routes: L.layerGroup()
    };
    this.routePolylines = [];
  }

  initMap() {
    if (this.map) return;
    const elem = document.getElementById(this.containerId);
    if (!elem) return;

    // Center on Zero Mile Stone, Nagpur [21.1458, 79.0882]
    this.map = L.map(this.containerId, {
      center: [21.1458, 79.0882],
      zoom: 12,
      zoomControl: true
    });

    // Dark-themed CartoDB Positron / Voyager or OpenStreetMap
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
      maxZoom: 19
    }).addTo(this.map);

    // Add layer groups to map
    Object.values(this.layers).forEach(layer => layer.addTo(this.map));

    // Handle map click for citizen reporting coordinate selection
    this.map.on('click', (e) => {
      const lat = e.latlng.lat.toFixed(5);
      const lon = e.latlng.lng.toFixed(5);
      const latInput = document.getElementById('report-lat');
      const lonInput = document.getElementById('report-lon');
      if (latInput && lonInput) {
        latInput.value = lat;
        lonInput.value = lon;
        L.popup()
          .setLatLng(e.latlng)
          .setContent(`<b>Selected Coordinates for Incident Report:</b><br>Lat: ${lat}, Lon: ${lon}`)
          .openOn(this.map);
      }
    });
  }

  clearLayer(layerName) {
    if (this.layers[layerName]) {
      this.layers[layerName].clearLayers();
    }
  }

  renderIncidents(incidents) {
    this.clearLayer('incidents');
    incidents.forEach(inc => {
      const isCritical = inc.severity === 'Critical' || inc.severity === 'High';
      const color = isCritical ? '#f43f5e' : '#f59e0b';
      const marker = L.circleMarker([inc.latitude, inc.longitude], {
        radius: isCritical ? 9 : 7,
        fillColor: color,
        color: '#ffffff',
        weight: 1.5,
        opacity: 1,
        fillOpacity: 0.85
      });

      marker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 13px;">
          <h4 style="margin: 0 0 4px 0; color: #111827;">${inc.title}</h4>
          <p style="margin: 2px 0;"><b>Location:</b> ${inc.location_name}</p>
          <p style="margin: 2px 0;"><b>Severity:</b> <span style="color: ${color}; font-weight: bold;">${inc.severity}</span></p>
          <p style="margin: 2px 0;"><b>Water Depth:</b> ${inc.water_depth_cm || 'Unmeasured'} cm</p>
          <p style="margin: 2px 0;"><b>Status:</b> ${inc.status}</p>
          <p style="margin: 2px 0;"><b>Source:</b> ${inc.source}</p>
          <small style="color: #6b7280;">Code: ${inc.incident_code}</small>
        </div>
      `);
      this.layers.incidents.addLayer(marker);
    });
  }

  renderRoadClosures(closures) {
    this.clearLayer('closures');
    closures.forEach(c => {
      const marker = L.circleMarker([c.latitude, c.longitude], {
        radius: 10,
        fillColor: '#000000',
        color: '#f43f5e',
        weight: 3,
        opacity: 1,
        fillOpacity: 0.9
      });

      marker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 13px;">
          <h4 style="margin: 0 0 4px 0; color: #b91c1c;">⛔ ACTIVE ROAD CLOSURE</h4>
          <p style="margin: 2px 0;"><b>Road:</b> ${c.road_name}</p>
          <p style="margin: 2px 0;"><b>Locality:</b> ${c.locality}</p>
          <p style="margin: 2px 0;"><b>Reason:</b> ${c.reason}</p>
          <small style="color: #6b7280;">Code: ${c.closure_code}</small>
        </div>
      `);
      this.layers.closures.addLayer(marker);
    });
  }

  renderHotspots(hotspots) {
    this.clearLayer('hotspots');
    hotspots.forEach(h => {
      const marker = L.circleMarker([h.latitude, h.longitude], {
        radius: 6,
        fillColor: '#8b5cf6',
        color: '#ffffff',
        weight: 1,
        opacity: 1,
        fillOpacity: 0.75
      });

      marker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 13px;">
          <h4 style="margin: 0 0 4px 0; color: #6d28d9;">📍 Historical Hotspot</h4>
          <p style="margin: 2px 0;"><b>Spot:</b> ${h.name}</p>
          <p style="margin: 2px 0;"><b>Locality:</b> ${h.locality}</p>
          <p style="margin: 2px 0;"><b>Historical Incidents (5y):</b> ${h.incident_count_last_5yr}</p>
          <p style="margin: 2px 0;"><b>Chronic Cause:</b> ${h.chronic_cause}</p>
          <p style="margin: 2px 0;"><b>Drainage Proxy:</b> ${h.drainage_capacity_proxy}</p>
        </div>
      `);
      this.layers.hotspots.addLayer(marker);
    });
  }

  renderReports(reports) {
    this.clearLayer('reports');
    reports.forEach(r => {
      const marker = L.circleMarker([r.latitude, r.longitude], {
        radius: 5,
        fillColor: '#06b6d4',
        color: '#ffffff',
        weight: 1,
        opacity: 1,
        fillOpacity: 0.75
      });

      marker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 13px;">
          <h4 style="margin: 0 0 4px 0; color: #0891b2;">📢 Citizen Report (${r.verification_status})</h4>
          <p style="margin: 2px 0;"><b>Location:</b> ${r.location_name}</p>
          <p style="margin: 2px 0;"><b>Description:</b> ${r.description}</p>
          <p style="margin: 2px 0;"><b>Reported Severity:</b> ${r.estimated_severity}</p>
          <small style="color: #6b7280;">ID: ${r.report_code}</small>
        </div>
      `);
      this.layers.reports.addLayer(marker);
    });
  }

  renderRoutes(routes, selectedIndex = 0) {
    this.clearLayer('routes');
    this.routePolylines = [];

    const colors = ['#38bdf8', '#10b981', '#f59e0b'];

    routes.forEach((rt, idx) => {
      const isSelected = idx === selectedIndex;
      const color = isSelected ? '#38bdf8' : (idx === 1 ? '#10b981' : '#a855f7');
      const weight = isSelected ? 6 : 4;
      const opacity = isSelected ? 0.95 : 0.55;

      const polyline = L.polyline(rt.coordinates, {
        color: color,
        weight: weight,
        opacity: opacity,
        dashArray: isSelected ? null : '5, 5'
      });

      polyline.bindPopup(`
        <div style="font-family: sans-serif; font-size: 13px;">
          <h4 style="margin: 0 0 4px 0;">Candidate Route (${rt.preference_type.toUpperCase()})</h4>
          <p style="margin: 2px 0;"><b>Distance:</b> ${rt.distance_km} km</p>
          <p style="margin: 2px 0;"><b>Est. Duration:</b> ${rt.duration_minutes} min</p>
          <p style="margin: 2px 0;"><b>Flood Risk:</b> <span style="font-weight: bold;">${rt.estimated_risk_level}</span> (${rt.risk_score})</p>
          <p style="margin: 2px 0; font-size: 11px;">${rt.recommendation_rationale}</p>
        </div>
      `);

      this.layers.routes.addLayer(polyline);
      this.routePolylines.push(polyline);
    });

    if (this.routePolylines[selectedIndex]) {
      this.map.fitBounds(this.routePolylines[selectedIndex].getBounds(), { padding: [40, 40] });
    }
  }

  toggleLayer(layerName, visible) {
    if (!this.layers[layerName]) return;
    if (visible) {
      if (!this.map.hasLayer(this.layers[layerName])) {
        this.map.addLayer(this.layers[layerName]);
      }
    } else {
      if (this.map.hasLayer(this.layers[layerName])) {
        this.map.removeLayer(this.layers[layerName]);
      }
    }
  }
}

window.nagpurMap = new NagpurMapController();
