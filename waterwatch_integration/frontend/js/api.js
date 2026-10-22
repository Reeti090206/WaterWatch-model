/**
 * WaterWatch AI Integration — Frontend API Client
 * Centralized fetch handlers communicating with FastAPI /api/v1 endpoints.
 */

const API_BASE = window.location.origin + '/api/v1';

const apiClient = {
  async getDashboardSummary() {
    const res = await fetch(`${API_BASE}/dashboard/summary`);
    if (!res.ok) throw new Error('Failed to fetch dashboard summary');
    return res.json();
  },

  async getIncidents(status, severity) {
    let url = `${API_BASE}/incidents`;
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (severity) params.append('severity', severity);
    if (params.toString()) url += `?${params.toString()}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch incidents');
    return res.json();
  },

  async getRoadClosures() {
    const res = await fetch(`${API_BASE}/road-closures`);
    if (!res.ok) throw new Error('Failed to fetch road closures');
    return res.json();
  },

  async getHotspots() {
    const res = await fetch(`${API_BASE}/hotspots`);
    if (!res.ok) throw new Error('Failed to fetch hotspots');
    return res.json();
  },

  async getAnalyticsSummary() {
    const res = await fetch(`${API_BASE}/analytics/summary`);
    if (!res.ok) throw new Error('Failed to fetch analytics summary');
    return res.json();
  },

  async getCitizenReports(status) {
    let url = `${API_BASE}/reports`;
    if (status) url += `?status=${encodeURIComponent(status)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch citizen reports');
    return res.json();
  },

  async submitReport(formData) {
    const res = await fetch(`${API_BASE}/reports`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Report submission failed' }));
      throw new Error(err.detail || 'Report submission failed');
    }
    return res.json();
  },

  async reviewReport(reportId, action, notes, adminToken) {
    const res = await fetch(`${API_BASE}/reports/${reportId}/review`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: action,
        reviewer_notes: notes,
        admin_token: adminToken
      })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Administrative review failed' }));
      throw new Error(err.detail || 'Administrative review failed');
    }
    return res.json();
  },

  async predictRainfall(payload) {
    const res = await fetch(`${API_BASE}/predictions/rainfall`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Prediction failed' }));
      throw new Error(err.detail || 'Prediction failed');
    }
    return res.json();
  },

  async detectImage(formData) {
    const res = await fetch(`${API_BASE}/detection/image`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Image inference failed' }));
      throw new Error(err.detail || 'Image inference failed');
    }
    return res.json();
  },

  async recommendRoutes(payload) {
    const res = await fetch(`${API_BASE}/routes/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Route planning failed' }));
      throw new Error(err.detail || 'Route planning failed');
    }
    return res.json();
  },

  async getModelsStatus() {
    const res = await fetch(`${API_BASE}/models/status`);
    if (!res.ok) throw new Error('Failed to fetch models status');
    return res.json();
  }
};
