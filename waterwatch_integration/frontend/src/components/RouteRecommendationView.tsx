"use client";

import React, { useState } from "react";
import { RouteRecommendationResponse, RouteSegment } from "../types";
import { api } from "../services/api";

interface RouteProps {
  onSelectRouteForMap: (route: RouteSegment) => void;
  activeRoute: RouteSegment | null;
}

const NAGPUR_LOCATIONS = [
  { name: "Sitabuldi Interchange", lat: 21.1466, lng: 79.0833 },
  { name: "Nagpur Railway Station", lat: 21.1524, lng: 79.0888 },
  { name: "Chhatrapati Square", lat: 21.107, lng: 79.061 },
  { name: "Narendra Nagar RUB (Flood Prone)", lat: 21.105, lng: 79.078 },
  { name: "Medical Square", lat: 21.132, lng: 79.098 },
  { name: "Dharampeth Traffic Signal", lat: 21.1415, lng: 79.062 },
  { name: "Mor Bhavan Bus Terminus", lat: 21.143, lng: 79.077 },
  { name: "Sadar Residency Road", lat: 21.161, lng: 79.082 },
  { name: "MIDC Hingna Industrial Area", lat: 21.095, lng: 78.995 },
];

export default function RouteRecommendationView({ onSelectRouteForMap, activeRoute }: RouteProps) {
  const [originIndex, setOriginIndex] = useState(0);
  const [destIndex, setDestIndex] = useState(1);
  const [preference, setPreference] = useState<"fastest" | "lowest_risk" | "balanced">("balanced");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recommendation, setRecommendation] = useState<RouteRecommendationResponse | null>(null);

  const handleCalculateRoute = async () => {
    setLoading(true);
    setError(null);
    try {
      const origin = NAGPUR_LOCATIONS[originIndex];
      const destination = NAGPUR_LOCATIONS[destIndex];

      const payload = {
        origin: {
          name: origin.name,
          latitude: origin.lat,
          longitude: origin.lng,
        },
        destination: {
          name: destination.name,
          latitude: destination.lat,
          longitude: destination.lng,
        },
        travel_mode: "driving",
        preference,
      };

      const result = await api.recommendRoutes(payload);
      setRecommendation(result);
      if (result.routes && result.routes.length > 0) {
        // Automatically select recommended or first route on Google Map
        const recommended = result.routes.find((r) => r.is_recommended) || result.routes[0];
        onSelectRouteForMap(recommended);
      }
    } catch (e: any) {
      setError(e.message || "Failed to calculate routes");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* Route Inputs Card */}
      <div className="glass-panel" style={{ padding: "20px" }}>
        <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "16px", color: "#f8fafc" }}>
          🧭 Intelligent Safe Route Planner
        </h3>
        <p style={{ fontSize: "0.85rem", color: "#94a3b8", marginBottom: "16px" }}>
          Evaluates multi-factor waterlogging exposure, active road closures, chronic underpass buffers, and synthetic rainfall predictions across Nagpur arterial corridors.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr auto", gap: "14px", alignItems: "flex-end" }}>
          <div>
            <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "6px" }}>
              Origin Location
            </label>
            <select
              className="input-field"
              value={originIndex}
              onChange={(e) => setOriginIndex(Number(e.target.value))}
            >
              {NAGPUR_LOCATIONS.map((loc, i) => (
                <option key={i} value={i} style={{ background: "#0f172a" }}>
                  📍 {loc.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "6px" }}>
              Destination Location
            </label>
            <select
              className="input-field"
              value={destIndex}
              onChange={(e) => setDestIndex(Number(e.target.value))}
            >
              {NAGPUR_LOCATIONS.map((loc, i) => (
                <option key={i} value={i} style={{ background: "#0f172a" }}>
                  🎯 {loc.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "6px" }}>
              Routing Preference
            </label>
            <select
              className="input-field"
              value={preference}
              onChange={(e) => setPreference(e.target.value as any)}
            >
              <option value="balanced" style={{ background: "#0f172a" }}>⚖️ Balanced (Recommended)</option>
              <option value="lowest_risk" style={{ background: "#0f172a" }}>🛡️ Lowest Flood Risk (Safest)</option>
              <option value="fastest" style={{ background: "#0f172a" }}>⚡ Fastest Duration</option>
            </select>
          </div>

          <button
            onClick={handleCalculateRoute}
            disabled={loading}
            className="btn-primary"
            style={{ height: "42px", padding: "0 22px" }}
          >
            {loading ? "Calculating..." : "Find Safe Routes"}
          </button>
        </div>

        {error && (
          <div style={{ marginTop: "14px", color: "#f87171", fontSize: "0.85rem" }}>
            ⚠️ {error}
          </div>
        )}
      </div>

      {/* Route Candidates Result Cards */}
      {recommendation && (
        <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#f8fafc" }}>
              Recommended Corridors ({recommendation.routes.length} options evaluated)
            </h4>
            <span style={{ fontSize: "12px", color: "#94a3b8" }}>
              Click any route to view and highlight on the Google Map
            </span>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "14px" }}>
            {recommendation.routes.map((route, idx) => {
              const isSelected = activeRoute?.preference_type === route.preference_type;
              const isLowestRisk = route.preference_type === "lowest_risk";
              const isFastest = route.preference_type === "fastest";

              const riskBadgeClass =
                route.risk_score < 0.35
                  ? "badge-low"
                  : route.risk_score < 0.65
                  ? "badge-mod"
                  : "badge-high";

              return (
                <div
                  key={idx}
                  onClick={() => onSelectRouteForMap(route)}
                  className={`glass-panel glass-panel-hover ${isSelected ? "route-card-active" : ""}`}
                  style={{
                    padding: "18px",
                    cursor: "pointer",
                    border: isSelected ? "2px solid #06b6d4" : "1px solid rgba(255,255,255,0.08)",
                    background: isSelected ? "rgba(6, 182, 212, 0.08)" : undefined,
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "10px" }}>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                        <span style={{ fontWeight: 700, fontSize: "0.95rem", color: "#f8fafc" }}>
                          {isLowestRisk ? "🛡️ Safest Alternative" : isFastest ? "⚡ Fastest Alternative" : "⚖️ Balanced Route"}
                        </span>
                        {route.is_recommended && (
                          <span style={{ background: "rgba(16, 185, 129, 0.2)", color: "#34d399", fontSize: "10px", fontWeight: 700, padding: "2px 6px", borderRadius: "4px" }}>
                            RECOMMENDED
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: "11px", color: "#94a3b8", marginTop: "2px" }}>
                        Exposure score: {(route.risk_score * 100).toFixed(0)}/100
                      </div>
                    </div>
                    <span className={riskBadgeClass}>{route.estimated_risk_level.replace(/_/g, " ")}</span>
                  </div>

                  {/* Metrics */}
                  <div style={{ display: "flex", gap: "16px", marginBottom: "12px", borderBottom: "1px solid rgba(255,255,255,0.06)", paddingBottom: "10px" }}>
                    <div>
                      <div style={{ fontSize: "11px", color: "#64748b" }}>Distance</div>
                      <div style={{ fontWeight: 700, fontSize: "1.05rem", color: "#f1f5f9" }}>{route.distance_km} km</div>
                    </div>
                    <div>
                      <div style={{ fontSize: "11px", color: "#64748b" }}>Est. Duration</div>
                      <div style={{ fontWeight: 700, fontSize: "1.05rem", color: "#f1f5f9" }}>{route.duration_minutes} min</div>
                    </div>
                    <div>
                      <div style={{ fontSize: "11px", color: "#64748b" }}>Waypoints</div>
                      <div style={{ fontWeight: 700, fontSize: "1.05rem", color: "#f1f5f9" }}>{route.coordinates.length}</div>
                    </div>
                  </div>

                  {/* Hazard Factors */}
                  <div>
                    <div style={{ fontSize: "11px", color: "#94a3b8", fontWeight: 600, marginBottom: "4px" }}>
                      Flood Hazard Analysis:
                    </div>
                    <div style={{ fontSize: "12px", color: "#cbd5e1", lineHeight: 1.4 }}>
                      {route.recommendation_rationale}
                    </div>

                    {route.hazard_factors && route.hazard_factors.length > 0 && (
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginTop: "8px" }}>
                        {route.hazard_factors.map((h, i) => (
                          <span
                            key={i}
                            style={{
                              background: "rgba(239, 68, 68, 0.15)",
                              color: "#f87171",
                              fontSize: "10px",
                              padding: "2px 6px",
                              borderRadius: "4px",
                            }}
                          >
                            ⚠️ {h}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ fontSize: "11px", color: "#64748b", fontStyle: "italic", marginTop: "6px" }}>
            * {recommendation.disclaimer}
          </div>
        </div>
      )}
    </div>
  );
}
