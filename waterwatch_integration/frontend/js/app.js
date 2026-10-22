/**
 * WaterWatch AI Integration — Main Frontend Application Logic
 * Coordinates tab switching, event listeners, API binding, and UI rendering.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Navigation Tab Switching
  const navTabs = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  function switchTab(targetTabId) {
    navTabs.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === targetTabId);
    });
    tabPanes.forEach(pane => {
      pane.classList.toggle('active', pane.id === targetTabId);
    });

    if (targetTabId === 'tab-map' || targetTabId === 'tab-routes') {
      setTimeout(() => {
        if (window.nagpurMap && window.nagpurMap.map) {
          window.nagpurMap.map.invalidateSize();
        }
      }, 200);
    }
  }

  navTabs.forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  // 2. Initialize Leaflet Map
  window.nagpurMap.initMap();

  // 3. Load Main Dashboard Data
  async function loadDashboard() {
    try {
      const summary = await apiClient.getDashboardSummary();
      const m = summary.metrics || {};

      document.getElementById('kpi-total-incidents').textContent = m.total_incidents ?? 0;
      document.getElementById('kpi-verified').textContent = m.verified_waterlogging_incidents ?? 0;
      document.getElementById('kpi-unverified').textContent = m.unverified_citizen_reports ?? 0;
      document.getElementById('kpi-closures').textContent = m.active_road_closures ?? 0;
      document.getElementById('kpi-hotspots').textContent = m.chronic_hotspots ?? 0;

      // Live Weather Box
      const w = summary.live_weather || {};
      const weatherBox = document.getElementById('weather-status-box');
      if (w.status === 'LIVE_OBSERVATION') {
        weatherBox.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-size:1.4rem; font-weight:700;">${w.temperature_celsius ?? '--'} °C</div>
              <div style="font-size:0.85rem; color:var(--text-muted);">${w.location}</div>
            </div>
            <div style="text-align:right;">
              <span class="badge badge-low" style="background:rgba(56,189,248,0.2); color:#38bdf8;">Precip: ${w.current_precipitation_mm ?? 0} mm/h</span>
              <div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px;">Humidity: ${w.humidity_percent ?? '--'}% | Wind: ${w.wind_speed_kmh ?? '--'} km/h</div>
            </div>
          </div>
          <div style="font-size:0.7rem; color:var(--text-muted); margin-top:6px;">Source: ${w.source} (${w.observation_time || ''})</div>
        `;
      } else {
        weatherBox.innerHTML = `
          <div style="color:#fde68a; font-size:0.85rem;">
            ⚠️ <b>NO LIVE DATA AVAILABLE</b> — Real-time atmospheric API unreachable.
          </div>
        `;
      }

      // Load map layers
      const [incidents, closures, hotspots, reports] = await Promise.all([
        apiClient.getIncidents(),
        apiClient.getRoadClosures(),
        apiClient.getHotspots(),
        apiClient.getCitizenReports()
      ]);

      window.nagpurMap.renderIncidents(incidents);
      window.nagpurMap.renderRoadClosures(closures);
      window.nagpurMap.renderHotspots(hotspots);
      window.nagpurMap.renderReports(reports);

      // Render recent alerts table on dashboard
      renderDashboardAlerts(incidents, closures);
    } catch (e) {
      console.error('Error loading dashboard:', e);
    }
  }

  function renderDashboardAlerts(incidents, closures) {
    const tableBody = document.getElementById('recent-alerts-body');
    if (!tableBody) return;
    tableBody.innerHTML = '';

    const allAlerts = [
      ...closures.map(c => ({ title: `ROAD CLOSURE: ${c.road_name}`, loc: c.locality, sev: 'Critical', type: 'Closure' })),
      ...incidents.map(i => ({ title: i.title, loc: i.location_name, sev: i.severity, type: 'Incident' }))
    ];

    if (allAlerts.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--text-muted);">No active hazards reported.</td></tr>';
      return;
    }

    allAlerts.slice(0, 5).forEach(a => {
      const badgeCls = a.sev === 'Critical' || a.sev === 'High' ? 'badge-high' : 'badge-mod';
      const row = document.createElement('tr');
      row.innerHTML = `
        <td style="padding:0.5rem; font-weight:500;">${a.title}</td>
        <td style="padding:0.5rem; color:var(--text-muted);">${a.loc}</td>
        <td style="padding:0.5rem;"><span class="badge ${badgeCls}">${a.sev}</span></td>
        <td style="padding:0.5rem; font-size:0.8rem;">${a.type}</td>
      `;
      tableBody.appendChild(row);
    });
  }

  // 4. Map Layer Toggles
  ['layer-incidents', 'layer-closures', 'layer-hotspots', 'layer-reports'].forEach(id => {
    const chk = document.getElementById(id);
    if (chk) {
      chk.addEventListener('change', (e) => {
        const layerKey = id.replace('layer-', '');
        window.nagpurMap.toggleLayer(layerKey, e.target.checked);
      });
    }
  });

  // 5. Intelligent Route Planner
  const NAGPUR_LANDMARKS = {
    "Nagpur Airport (MIHAN Corridor)": { lat: 21.0922, lon: 79.0617 },
    "Sitabuldi Interchange / Metro": { lat: 21.1448, lon: 79.0837 },
    "Dharampeth (West Nagpur)": { lat: 21.1432, lon: 79.0614 },
    "Sadar Residency Road (North)": { lat: 21.1610, lon: 79.0825 },
    "Manish Nagar / Narendra Nagar RUB": { lat: 21.1078, lon: 79.0765 },
    "Nagpur Central Railway Station": { lat: 21.1524, lon: 79.0887 },
    "Mankapur Ring Road Junction": { lat: 21.1925, lon: 79.0792 }
  };

  const originSelect = document.getElementById('route-origin-preset');
  const destSelect = document.getElementById('route-dest-preset');
  if (originSelect && destSelect) {
    Object.keys(NAGPUR_LANDMARKS).forEach(name => {
      originSelect.add(new Option(name, name));
      destSelect.add(new Option(name, name));
    });
    originSelect.value = "Nagpur Airport (MIHAN Corridor)";
    destSelect.value = "Sadar Residency Road (North)";
  }

  const planRouteBtn = document.getElementById('btn-plan-route');
  if (planRouteBtn) {
    planRouteBtn.addEventListener('click', async () => {
      const origName = originSelect.value;
      const destName = destSelect.value;
      const origCoords = NAGPUR_LANDMARKS[origName];
      const destCoords = NAGPUR_LANDMARKS[destName];
      const pref = document.getElementById('route-preference').value;
      const mode = document.getElementById('route-mode').value;

      planRouteBtn.disabled = true;
      planRouteBtn.textContent = 'Calculating Alternatives & Risk...';

      try {
        const payload = {
          origin: { name: origName, latitude: origCoords.lat, longitude: origCoords.lon },
          destination: { name: destName, latitude: destCoords.lat, longitude: destCoords.lon },
          travel_mode: mode,
          preference: pref
        };

        const res = await apiClient.recommendRoutes(payload);
        renderRouteResults(res.routes);
      } catch (err) {
        alert('Route planning failed: ' + err.message);
      } finally {
        planRouteBtn.disabled = false;
        planRouteBtn.textContent = 'Find Recommended Route';
      }
    });
  }

  function renderRouteResults(routes) {
    const container = document.getElementById('route-candidates-container');
    container.innerHTML = '';

    if (!routes || routes.length === 0) {
      container.innerHTML = '<p style="color:var(--text-muted);">No candidate routes found.</p>';
      return;
    }

    // Render routes on map
    window.nagpurMap.renderRoutes(routes, 0);

    routes.forEach((r, idx) => {
      const card = document.createElement('div');
      card.className = `route-card ${r.is_recommended ? 'selected' : ''}`;
      const badgeCls = r.estimated_risk_level === 'LOW_ESTIMATED_RISK' ? 'badge-low' : (r.estimated_risk_level === 'MODERATE_ESTIMATED_RISK' ? 'badge-mod' : 'badge-high');

      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
          <b style="color:#fff;">Route ${idx + 1} (${r.preference_type.toUpperCase()})</b>
          <span class="badge ${badgeCls}">${r.estimated_risk_level.replace('_ESTIMATED_RISK', '')} RISK</span>
        </div>
        <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:6px;">
          ⏱️ <b>${r.duration_minutes} min</b> | 📏 <b>${r.distance_km} km</b> | Hazard Score: <b>${r.risk_score}</b>
        </div>
        <p style="font-size:0.8rem; color:#e2e8f0; margin-bottom:4px;">${r.recommendation_rationale}</p>
        ${r.hazard_factors.length > 0 ? `
          <ul style="font-size:0.75rem; color:#fb7185; padding-left:1.2rem; margin-top:4px;">
            ${r.hazard_factors.map(h => `<li>${h}</li>`).join('')}
          </ul>
        ` : ''}
      `;

      card.addEventListener('click', () => {
        document.querySelectorAll('.route-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        window.nagpurMap.renderRoutes(routes, idx);
      });

      container.appendChild(card);
    });
  }

  // 6. Rainfall Prediction Tab
  const predictForm = document.getElementById('rainfall-predict-form');
  if (predictForm) {
    predictForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('btn-run-prediction');
      btn.disabled = true;
      btn.textContent = 'Evaluating ML Pipeline...';

      const payload = {
        rainfall_1h_mm: parseFloat(document.getElementById('p-rain-1h').value),
        rainfall_3h_mm: parseFloat(document.getElementById('p-rain-3h').value),
        rainfall_6h_mm: parseFloat(document.getElementById('p-rain-6h').value),
        rainfall_24h_mm: parseFloat(document.getElementById('p-rain-24h').value),
        rainfall_prev_72h_mm: parseFloat(document.getElementById('p-rain-72h').value),
        drainage_capacity_proxy: parseFloat(document.getElementById('p-drainage-proxy').value),
        locality_name: document.getElementById('p-locality').value
      };

      try {
        const res = await apiClient.predictRainfall(payload);
        const resultBox = document.getElementById('prediction-result-box');
        resultBox.style.display = 'block';

        const isFlooded = res.waterlogging_predicted;
        const color = res.risk_category === 'HIGH' ? '#f43f5e' : (res.risk_category === 'MODERATE' ? '#f59e0b' : '#10b981');

        resultBox.innerHTML = `
          <div style="border-left: 4px solid ${color}; padding-left:1rem;">
            <h3 style="color:${color}; margin-bottom:4px;">
              ${isFlooded ? '⚠️ WATERLOGGING PREDICTED' : '✅ NO WATERLOGGING PREDICTED'} (${res.risk_category} RISK)
            </h3>
            <p style="font-size:0.95rem; margin-bottom:4px;">
              Experimental Model Score: <b>${(res.predicted_probability * 100).toFixed(1)}%</b> (Probability: ${res.predicted_probability})
            </p>
            <p style="font-size:0.85rem; color:var(--text-muted);">
              Locality: <b>${res.location}</b> | Model: <b>${res.model_name} (${res.model_version})</b> | Status: <b>${res.training_data_status}</b>
            </p>
            <div class="disclaimer-box" style="margin-top:8px;">
              <b>Disclaimer:</b> ${res.scientific_disclaimer}
            </div>
          </div>
        `;
      } catch (err) {
        alert('Prediction error: ' + err.message);
      } finally {
        btn.disabled = false;
        btn.textContent = 'Calculate Waterlogging Risk';
      }
    });
  }

  // 7. Image-Based Detection Tab
  const imageInput = document.getElementById('image-upload-input');
  const detectBtn = document.getElementById('btn-run-detect');
  const imagePreview = document.getElementById('image-preview');

  if (imageInput) {
    imageInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (ev) => {
          imagePreview.src = ev.target.result;
          imagePreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
      }
    });
  }

  if (detectBtn) {
    detectBtn.addEventListener('click', async () => {
      const file = imageInput.files[0];
      if (!file) {
        alert('Please select an image first.');
        return;
      }

      detectBtn.disabled = true;
      detectBtn.textContent = 'Running YOLOv11 Inference...';

      const formData = new FormData();
      formData.append('image', file);
      formData.append('conf_threshold', document.getElementById('detect-conf-thresh').value);

      try {
        const res = await apiClient.detectImage(formData);
        const resultContainer = document.getElementById('image-detect-results');
        resultContainer.style.display = 'block';

        const hasWater = res.waterlogging_detected;
        const color = hasWater ? '#f43f5e' : '#10b981';

        resultContainer.innerHTML = `
          <div style="border-left: 4px solid ${color}; padding-left:1rem; margin-top:1rem;">
            <h3 style="color:${color}; margin-bottom:4px;">
              ${hasWater ? `🌊 WATERLOGGING DETECTED (${res.detection_count} surface patches)` : '✅ NO WATERLOGGING DETECTED'}
            </h3>
            <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:6px;">
              Image: ${res.image_filename} | Resolution: ${res.dimensions.width}x${res.dimensions.height} px
            </p>
            ${res.detections.length > 0 ? `
              <div style="background:rgba(17,24,39,0.7); padding:0.5rem; border-radius:6px; font-size:0.8rem;">
                <b>Detected Bounding Boxes:</b>
                <ul style="padding-left:1rem; margin-top:4px;">
                  ${res.detections.map(d => `<li>Patch [${d.bbox_pixels.join(', ')}] — Conf: <b>${(d.confidence*100).toFixed(1)}%</b></li>`).join('')}
                </ul>
              </div>
            ` : ''}
            <div class="disclaimer-box" style="margin-top:8px;">
              ${res.disclaimer}
            </div>
          </div>
        `;
      } catch (err) {
        alert('Detection failed: ' + err.message);
      } finally {
        detectBtn.disabled = false;
        detectBtn.textContent = 'Run Optical Detection';
      }
    });
  }

  // 8. Citizen Incident Reporting Tab
  const reportForm = document.getElementById('citizen-report-form');
  if (reportForm) {
    reportForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('btn-submit-report');
      btn.disabled = true;
      btn.textContent = 'Submitting Report...';

      const formData = new FormData();
      formData.append('location_name', document.getElementById('report-loc-name').value);
      formData.append('latitude', document.getElementById('report-lat').value);
      formData.append('longitude', document.getElementById('report-lon').value);
      formData.append('description', document.getElementById('report-desc').value);
      formData.append('estimated_severity', document.getElementById('report-sev').value);
      formData.append('water_depth_cm', document.getElementById('report-depth').value || '');
      formData.append('reporter_name', document.getElementById('report-name').value || 'Anonymous Citizen');

      const photoFile = document.getElementById('report-photo').files[0];
      if (photoFile) formData.append('image', photoFile);

      try {
        const res = await apiClient.submitReport(formData);
        const feedback = document.getElementById('report-feedback-box');
        feedback.style.display = 'block';
        feedback.innerHTML = `
          <div style="background:rgba(16,185,129,0.15); border:1px solid #10b981; padding:1rem; border-radius:8px;">
            <h4 style="color:#34d399; margin-bottom:4px;">Report Submitted Successfully!</h4>
            <p style="font-size:0.85rem; margin-bottom:4px;">Tracking Code: <b>${res.report_code}</b></p>
            <p style="font-size:0.8rem; color:var(--text-muted);">${res.message}</p>
          </div>
        `;
        reportForm.reset();
        // Refresh map reports
        const reports = await apiClient.getCitizenReports();
        window.nagpurMap.renderReports(reports);
      } catch (err) {
        alert('Submission failed: ' + err.message);
      } finally {
        btn.disabled = false;
        btn.textContent = 'Submit Waterlogging Report';
      }
    });
  }

  // 9. Admin Authority Dashboard Tab
  const adminLoginBtn = document.getElementById('btn-admin-login');
  if (adminLoginBtn) {
    adminLoginBtn.addEventListener('click', async () => {
      const token = document.getElementById('admin-token-input').value;
      if (!token) {
        alert('Please enter your administrative secret token.');
        return;
      }
      loadAdminReports(token);
    });
  }

  async function loadAdminReports(token) {
    try {
      const reports = await apiClient.getCitizenReports();
      const container = document.getElementById('admin-reports-table-body');
      container.innerHTML = '';

      if (reports.length === 0) {
        container.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No reports to review.</td></tr>';
        return;
      }

      document.getElementById('admin-panel-content').style.display = 'block';

      reports.forEach(r => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td style="padding:0.6rem; font-family:monospace; font-size:0.8rem;">${r.report_code}</td>
          <td style="padding:0.6rem;"><b>${r.location_name}</b><br><small style="color:var(--text-muted);">${r.description.slice(0, 40)}...</small></td>
          <td style="padding:0.6rem;"><span class="badge ${r.estimated_severity === 'Critical' ? 'badge-high' : 'badge-mod'}">${r.estimated_severity}</span></td>
          <td style="padding:0.6rem;"><span class="badge" style="background:rgba(255,255,255,0.1);">${r.verification_status}</span></td>
          <td style="padding:0.6rem;">${r.image_url ? `<a href="${r.image_url}" target="_blank" style="color:#38bdf8;">View Photo</a>` : 'No Image'}</td>
          <td style="padding:0.6rem; white-space:nowrap;">
            ${r.verification_status === 'UNVERIFIED' ? `
              <button class="btn-verify" data-id="${r.id}" style="background:#10b981; color:#fff; border:none; padding:4px 8px; border-radius:4px; font-size:0.75rem; cursor:pointer; margin-right:4px;">Verify</button>
              <button class="btn-reject" data-id="${r.id}" style="background:#f43f5e; color:#fff; border:none; padding:4px 8px; border-radius:4px; font-size:0.75rem; cursor:pointer;">Reject</button>
            ` : `<small style="color:var(--text-muted);">${r.reviewed_by || 'Reviewed'}</small>`}
          </td>
        `;

        const verifyBtn = row.querySelector('.btn-verify');
        if (verifyBtn) {
          verifyBtn.addEventListener('click', async () => {
            const note = prompt('Enter municipal verification remarks:', 'Field verified by NMC Quick Response Team');
            if (note !== null) {
              await apiClient.reviewReport(r.id, 'VERIFY', note, token);
              loadAdminReports(token);
              loadDashboard();
            }
          });
        }

        const rejectBtn = row.querySelector('.btn-reject');
        if (rejectBtn) {
          rejectBtn.addEventListener('click', async () => {
            const note = prompt('Enter rejection reason:', 'Duplicate or unsubstantiated report');
            if (note !== null) {
              await apiClient.reviewReport(r.id, 'REJECT', note, token);
              loadAdminReports(token);
            }
          });
        }

        container.appendChild(row);
      });
    } catch (err) {
      alert('Failed to load admin reports: ' + err.message);
    }
  }

  // 10. Model Status Diagnostics Tab
  async function loadModelStatusTab() {
    try {
      const statusData = await apiClient.getModelsStatus();
      const container = document.getElementById('model-status-cards');
      if (!container) return;

      const rf = statusData.rainfall_model || {};
      const img = statusData.image_model || {};
      const prod = statusData.production_model || {};

      container.innerHTML = `
        <div class="card" style="margin-bottom:1rem; border-left: 4px solid #10b981;">
          <h4 style="color:#34d399; margin-bottom:4px;">🟢 Experimental Rainfall Model (Status: READY)</h4>
          <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:4px;">Architecture: <b>${rf.model_type}</b></p>
          <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:4px;">Artifact: <code>${rf.artifact_path}</code></p>
          <p style="font-size:0.8rem; color:#fde68a;"><b>Note:</b> ${rf.limitations}</p>
        </div>

        <div class="card" style="margin-bottom:1rem; border-left: 4px solid #f43f5e;">
          <h4 style="color:#fb7185; margin-bottom:4px;">🔴 Verified Production Rainfall Model (Status: BLOCKED ON DATA)</h4>
          <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:4px;">
            <b>Blocker:</b> Genuine municipal incident logs with GPS timestamps from NMC / Traffic Police are required before this model can be trained.
          </p>
          <p style="font-size:0.8rem; color:var(--text-muted);">Zero synthetic records are permitted in the production track.</p>
        </div>

        <div class="card" style="margin-bottom:1rem; border-left: 4px solid #f59e0b;">
          <h4 style="color:#fbbf24; margin-bottom:4px;">🟡 Image Waterlogging Model (Status: OPTICAL DETECTION ONLY)</h4>
          <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:4px;">Architecture: <b>${img.model_type}</b></p>
          <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:4px;">Artifact: <code>${img.artifact_path}</code></p>
          <p style="font-size:0.8rem; color:#fde68a;"><b>Note:</b> ${img.limitations}</p>
        </div>
      `;
    } catch (e) {
      console.error(e);
    }
  }

  // Load initial data
  loadDashboard();
  loadModelStatusTab();
});
