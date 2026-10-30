/**
 * WaterWatch AI Integration — Main Frontend Application Logic
 * Coordinates tab switching, event listeners, API binding, and UI rendering.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Navigation Tab Switching
  const navTabs = document.querySelectorAll('.sidebar-item, .tab-btn');
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

  window.switchTab = switchTab;

  // URL Hash Navigation (e.g. #tab-live-demo)
  const handleHash = () => {
    const hash = window.location.hash.replace('#', '');
    if (hash) {
      const tabId = hash.startsWith('tab-') ? hash : `tab-${hash}`;
      if (document.getElementById(tabId)) {
        switchTab(tabId);
      }
    }
  };
  window.addEventListener('hashchange', handleHash);
  if (window.location.hash) {
    handleHash();
  } else {
    switchTab('tab-home');
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

  // ==========================================
  // 9. LIVE AI DEMO CONTROLLER & EVENT ENGINE
  // ==========================================
  window.waterwatchDemo = {
    selectedSampleKey: 'sample_waterlogged',
    customImageFile: null,
    currentImageElement: null,
    latestCvResult: null,
    latestRainResult: null,

    init() {
      // Pre-load default sample
      this.selectSample('sample_waterlogged');
      // Pre-load benchmarks
      this.loadBenchmarks();
    },

    selectSample(key) {
      this.selectedSampleKey = key;
      this.customImageFile = null;

      // Update card UI
      document.querySelectorAll('#demo-sample-grid .sample-card').forEach(c => {
        c.classList.toggle('active-sample', c.dataset.key === key);
      });

      const sampleMap = {
        'sample_waterlogged': '/static/samples/sample_waterlogged.jpg',
        'sample_dry_road': '/static/samples/sample_dry_road.png',
        'sample_urban_arterial': '/static/samples/sample_urban_arterial.png',
        'sample_rainy_wet_road': '/static/samples/sample_rainy_wet_road.png'
      };

      const imgUrl = sampleMap[key];
      if (imgUrl) {
        this.renderPreviewImage(imgUrl);
      }
    },

    handleCustomUpload(event) {
      const file = event.target.files && event.target.files[0];
      if (!file) return;

      this.customImageFile = file;
      this.selectedSampleKey = null;

      // Remove sample card selection
      document.querySelectorAll('#demo-sample-grid .sample-card').forEach(c => {
        c.classList.remove('active-sample');
      });

      const reader = new FileReader();
      reader.onload = (e) => {
        this.renderPreviewImage(e.target.result);
      };
      reader.readAsDataURL(file);
    },

    renderPreviewImage(src, detections = []) {
      const canvas = document.getElementById('demo-canvas');
      const outputBox = document.getElementById('demo-cv-output-box');
      if (!canvas || !outputBox) return;

      outputBox.style.display = 'block';
      const ctx = canvas.getContext('2d');
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        this.currentImageElement = img;
        canvas.width = img.naturalWidth || img.width;
        canvas.height = img.naturalHeight || img.height;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

        // Draw bounding boxes if provided
        if (detections && detections.length > 0) {
          detections.forEach((det, idx) => {
            const bbox = det.bbox_pixels;
            if (!bbox || bbox.length < 4) return;
            const [x1, y1, x2, y2] = bbox;
            const w = x2 - x1;
            const h = y2 - y1;

            // Box fill
            ctx.fillStyle = 'rgba(239, 68, 68, 0.22)';
            ctx.fillRect(x1, y1, w, h);

            // Box outline
            ctx.strokeStyle = '#ef4444';
            ctx.lineWidth = Math.max(3, Math.round(canvas.width / 350));
            ctx.strokeRect(x1, y1, w, h);

            // Label pill
            const confPct = Math.round(det.confidence * 100);
            const labelText = `Waterlogging #${idx + 1} (${confPct}%)`;
            const fontSize = Math.max(14, Math.round(canvas.width / 50));
            ctx.font = `bold ${fontSize}px sans-serif`;
            const textWidth = ctx.measureText(labelText).width;

            ctx.fillStyle = '#ef4444';
            ctx.fillRect(x1, Math.max(0, y1 - fontSize - 6), textWidth + 12, fontSize + 6);

            ctx.fillStyle = '#ffffff';
            ctx.fillText(labelText, x1 + 6, Math.max(fontSize, y1 - 4));
          });
        }
      };
      img.src = src;
    },

    async runDetection() {
      const btn = document.getElementById('btn-demo-run-cv');
      const slider = document.getElementById('demo-conf-slider');
      const confThreshold = slider ? parseFloat(slider.value) : 0.25;

      btn.disabled = true;
      btn.textContent = 'Processing Inference...';

      try {
        let result;
        if (this.customImageFile) {
          const formData = new FormData();
          formData.append('image', this.customImageFile);
          formData.append('conf_threshold', confThreshold);
          result = await apiClient.detectImage(formData);
        } else if (this.selectedSampleKey) {
          result = await apiClient.detectSample(this.selectedSampleKey, confThreshold);
        } else {
          alert('Please select a verified sample or upload an image first.');
          btn.disabled = false;
          btn.textContent = 'Run Waterlogging Detection';
          return;
        }

        this.latestCvResult = result;
        this.renderCvResult(result);
      } catch (err) {
        alert('Detection error: ' + err.message);
      } finally {
        btn.disabled = false;
        btn.textContent = 'Run Waterlogging Detection';
      }
    },

    renderCvResult(result) {
      const outputBox = document.getElementById('demo-cv-output-box');
      if (!outputBox) return;
      outputBox.style.display = 'block';

      // 1. Re-draw image with bounding boxes on canvas
      const imgUrl = result.image_url || (this.currentImageElement ? this.currentImageElement.src : null);
      if (imgUrl) {
        this.renderPreviewImage(imgUrl, result.detections || []);
      }

      // 2. Classification Badge
      const classBadge = document.getElementById('demo-cv-class-badge');
      if (result.waterlogging_detected) {
        classBadge.className = 'badge badge-high';
        classBadge.innerHTML = '🌊 WATERLOGGED ROAD';
      } else {
        classBadge.className = 'badge badge-low';
        classBadge.innerHTML = '☀️ NOT WATERLOGGED (CLEAR)';
      }

      // 3. Severity Heuristic
      const sevBadge = document.getElementById('demo-cv-severity-badge');
      const sev = result.severity || 'None';
      if (sev === 'High') {
        sevBadge.className = 'badge badge-high';
        sevBadge.textContent = 'High (Severe Pooling)';
      } else if (sev === 'Moderate') {
        sevBadge.className = 'badge badge-mod';
        sevBadge.textContent = 'Moderate (Curb Pooling)';
      } else if (sev === 'Low') {
        sevBadge.className = 'badge badge-mod';
        sevBadge.textContent = 'Low (Minor Puddle)';
      } else {
        sevBadge.className = 'badge badge-low';
        sevBadge.textContent = 'None (Dry Pavement)';
      }

      // 4. Latency
      document.getElementById('demo-cv-latency').textContent = `${result.inference_time_ms ?? '--'} ms`;

      // 5. Confidence
      const confPct = result.confidence_percentage ?? 0;
      document.getElementById('demo-cv-conf-pct').textContent = `${confPct}%`;
      const fillBar = document.getElementById('demo-cv-conf-fill');
      fillBar.style.width = `${Math.min(100, Math.max(5, confPct))}%`;
      fillBar.style.background = result.waterlogging_detected ? 'var(--accent-rose)' : 'var(--accent-emerald)';

      // 6. Boxes & Coverage Meta
      const metaBox = document.getElementById('demo-cv-boxes-meta');
      const boxCount = result.detection_count ?? 0;
      const coverage = result.total_water_area_percentage ?? 0;
      metaBox.innerHTML = `
        <span>Detected Bounding Boxes: <b>${boxCount}</b></span> | 
        <span>Visual Road Coverage: <b>${coverage}%</b></span> | 
        <span>Resolution: <b>${result.dimensions?.width ?? 0}x${result.dimensions?.height ?? 0}px</b></span>
      `;

      // 7. Uncertainty Warning
      const uncBox = document.getElementById('demo-cv-uncertainty-box');
      if (result.uncertainty_warning) {
        uncBox.style.display = 'block';
        uncBox.innerHTML = `⚠️ <b>Uncertainty Flag:</b> ${result.uncertainty_warning}`;
      } else {
        uncBox.style.display = 'none';
      }
    },

    setRainPreset(r1, r3, r6, r24, r72) {
      document.getElementById('demo-rain-1h').value = r1;
      document.getElementById('demo-rain-3h').value = r3;
      document.getElementById('demo-rain-6h').value = r6;
      document.getElementById('demo-rain-24h').value = r24;
      document.getElementById('demo-rain-72h').value = r72;
    },

    async runRainfallPrediction(event) {
      if (event) event.preventDefault();
      const btn = document.getElementById('btn-demo-run-rain');
      btn.disabled = true;
      btn.textContent = 'Computing Risk...';

      const payload = {
        locality_name: document.getElementById('demo-rain-locality').value,
        drainage_capacity_proxy: parseFloat(document.getElementById('demo-rain-drainage').value),
        rainfall_1h_mm: parseFloat(document.getElementById('demo-rain-1h').value),
        rainfall_3h_mm: parseFloat(document.getElementById('demo-rain-3h').value),
        rainfall_6h_mm: parseFloat(document.getElementById('demo-rain-6h').value),
        rainfall_24h_mm: parseFloat(document.getElementById('demo-rain-24h').value),
        rainfall_prev_72h_mm: parseFloat(document.getElementById('demo-rain-72h').value),
      };

      try {
        const res = await apiClient.predictRainfall(payload);
        this.latestRainResult = res;

        const outBox = document.getElementById('demo-rain-output-box');
        outBox.style.display = 'block';

        const riskBadge = document.getElementById('demo-rain-risk-badge');
        riskBadge.textContent = res.risk_category;
        if (res.risk_category === 'HIGH') {
          riskBadge.className = 'badge badge-high';
        } else if (res.risk_category === 'MODERATE') {
          riskBadge.className = 'badge badge-mod';
        } else {
          riskBadge.className = 'badge badge-low';
        }

        const probPct = Math.round(res.predicted_probability * 100);
        document.getElementById('demo-rain-prob').textContent = `${probPct}%`;
      } catch (err) {
        alert('Rainfall prediction error: ' + err.message);
      } finally {
        btn.disabled = false;
        btn.textContent = 'Predict Rainfall Risk';
      }
    },

    async runCombinedAssessment() {
      const btn = document.getElementById('btn-demo-run-combined');
      btn.disabled = true;
      btn.textContent = 'Fusing Streams...';

      const payload = {
        locality_name: document.getElementById('demo-rain-locality').value,
        drainage_capacity_proxy: parseFloat(document.getElementById('demo-rain-drainage').value),
        rainfall_1h_mm: parseFloat(document.getElementById('demo-rain-1h').value),
        rainfall_3h_mm: parseFloat(document.getElementById('demo-rain-3h').value),
        rainfall_6h_mm: parseFloat(document.getElementById('demo-rain-6h').value),
        rainfall_24h_mm: parseFloat(document.getElementById('demo-rain-24h').value),
        rainfall_prev_72h_mm: parseFloat(document.getElementById('demo-rain-72h').value),
        sample_key: this.selectedSampleKey || 'sample_waterlogged'
      };

      try {
        const res = await apiClient.runCombinedAssessment(payload);
        const outBox = document.getElementById('demo-combined-output-box');
        outBox.style.display = 'block';

        // Stream 1 Visual Summary
        const img = res.image_stream || {};
        document.getElementById('demo-comb-img-summary').innerHTML = `
          <div><b>Observation:</b> ${img.waterlogging_detected ? '🚨 Visible Waterlogging Detected' : '☀️ Road Surface Clear'}</div>
          <div><b>Visual Severity:</b> ${img.visual_severity}</div>
          <div><b>Confidence:</b> ${img.confidence_percentage}%</div>
          <div><b>Boxes Found:</b> ${img.bounding_boxes_count}</div>
          <div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px;">${img.source}</div>
        `;

        // Stream 2 Rainfall Summary
        const rain = res.rainfall_stream || {};
        document.getElementById('demo-comb-rain-summary').innerHTML = `
          <div><b>Hydrological Risk:</b> <span class="badge ${rain.risk_category === 'HIGH' ? 'badge-high' : rain.risk_category === 'MODERATE' ? 'badge-mod' : 'badge-low'}">${rain.risk_category}</span></div>
          <div><b>Activation Probability:</b> ${rain.probability_percentage}%</div>
          <div><b>Acute Rain:</b> ${payload.rainfall_1h_mm} mm/h | <b>Soil Saturation:</b> ${payload.rainfall_prev_72h_mm} mm</div>
          <div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px;">${rain.source}</div>
        `;

        // Verdict Badge
        const vBadge = document.getElementById('demo-comb-verdict-badge');
        vBadge.textContent = res.combined_status;
        vBadge.className = `badge ${res.combined_badge}`;

        // Rationale
        document.getElementById('demo-comb-rationale').textContent = res.rationale;
      } catch (err) {
        alert('Combined assessment error: ' + err.message);
      } finally {
        btn.disabled = false;
        btn.textContent = 'Run Combined Dual-Stream Assessment';
      }
    },

    async runRouteRecommendation() {
      const btn = document.getElementById('btn-demo-run-route');
      btn.disabled = true;
      btn.textContent = 'Evaluating Road Corridors...';

      const originName = document.getElementById('demo-route-origin').value;
      const destName = document.getElementById('demo-route-dest').value;
      const pref = document.getElementById('demo-route-pref').value;

      // Coordinates map for Nagpur landmarks
      const coordMap = {
        'Sitabuldi Interchange': { lat: 21.1466, lon: 79.0882 },
        'Dharampeth Main Road': { lat: 21.1458, lon: 79.0664 },
        'Civil Lines VIP Road': { lat: 21.1595, lon: 79.0768 },
        'Pardi Naka Underpass': { lat: 21.1442, lon: 79.1415 },
        'Manish Nagar (RUB Corridor)': { lat: 21.0920, lon: 79.0780 },
        'Ambazari Lake Road': { lat: 21.1278, lon: 79.0494 },
        'Narendra Nagar Flyover': { lat: 21.1092, lon: 79.0815 },
        'Sadar Residency Road': { lat: 21.1610, lon: 79.0820 }
      };

      const origCoord = coordMap[originName] || { lat: 21.1466, lon: 79.0882 };
      const destCoord = coordMap[destName] || { lat: 21.0920, lon: 79.0780 };

      const payload = {
        origin: { latitude: origCoord.lat, longitude: origCoord.lon, address_name: originName },
        destination: { latitude: destCoord.lat, longitude: destCoord.lon, address_name: destName },
        travel_mode: 'driving',
        preference: pref
      };

      try {
        const res = await apiClient.recommendRoutes(payload);
        const outBox = document.getElementById('demo-route-output-box');
        const listDiv = document.getElementById('demo-route-cards-list');
        outBox.style.display = 'block';
        listDiv.innerHTML = '';

        const routes = res.routes || [];
        if (routes.length === 0) {
          listDiv.innerHTML = '<div style="color:var(--text-muted); padding:1rem;">No alternative routes found.</div>';
          return;
        }

        routes.forEach((r, idx) => {
          const isRec = r.is_recommended;
          const card = document.createElement('div');
          card.className = `route-card ${isRec ? 'selected' : ''}`;
          card.style.marginBottom = '0.75rem';
          card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
              <span style="font-weight:700; color:#fff;">${r.corridor_name || `Corridor Option #${idx + 1}`}</span>
              ${isRec ? '<span class="badge badge-low" style="background:#065f46; color:#34d399;">RECOMMENDED SAFE ROUTE</span>' : ''}
            </div>
            <div style="font-size:0.85rem; color:var(--text-muted); display:flex; gap:1.25rem; margin-bottom:6px;">
              <span>📏 <b>${r.distance_km} km</b></span>
              <span>⏱️ <b>${r.duration_minutes} min</b></span>
              <span>🌊 Hazard Score: <b>${r.flood_risk_score}</b> (${r.hazard_level})</span>
            </div>
            <div style="font-size:0.8rem; color:#d1d5db;">${r.recommendation_rationale}</div>
          `;
          listDiv.appendChild(card);
        });
      } catch (err) {
        alert('Route recommendation error: ' + err.message);
      } finally {
        btn.disabled = false;
        btn.textContent = 'Find Flood-Safe Route';
      }
    },

    async loadBenchmarks() {
      try {
        const data = await apiClient.getBenchmarks();
        if (!data || !data.benchmark_summary) return;

        const s = data.benchmark_summary;
        const models = s.models || {};

        if (models.mobilenetv3_classifier && models.mobilenetv3_classifier.metrics) {
          const m = models.mobilenetv3_classifier.metrics;
          const kpi = document.getElementById('bm-kpi-mn-acc');
          if (kpi) kpi.textContent = `${(m.accuracy * 100).toFixed(1)}%`;
        }

        if (models.improved_yolov11 && models.improved_yolov11.metrics) {
          const y = models.improved_yolov11.metrics;
          const kpi = document.getElementById('bm-kpi-yolo-acc');
          if (kpi) kpi.textContent = `${(y.accuracy * 100).toFixed(1)}%`;
        }

        if (models.baseline_yolov11 && models.baseline_yolov11.metrics) {
          const b = models.baseline_yolov11.metrics;
          const kpi = document.getElementById('bm-kpi-base-fp');
          if (kpi) kpi.textContent = `${b.confusion_matrix.fp} / 48`;
        }
      } catch (err) {
        console.warn('Could not load benchmark telemetry:', err);
      }
    }
  };

  // Load initial data
  loadDashboard();
  loadModelStatusTab();
  window.waterwatchDemo.init();
});

