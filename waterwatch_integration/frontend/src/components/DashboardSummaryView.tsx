"use client";

import React from "react";
import { DashboardSummary, Incident } from "../types";

interface DashboardProps {
  summary: DashboardSummary | null;
  incidents: Incident[];
  onNavigateTab: (tab: string) => void;
}

export default function DashboardSummaryView({ summary, incidents, onNavigateTab }: DashboardProps) {
  const metrics = summary?.metrics;
  const weather = summary?.live_weather;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* Top Banner Notice */}
      <div
        style={{
          background: "linear-gradient(90deg, rgba(6, 182, 212, 0.1), rgba(59, 130, 246, 0.1))",
          border: "1px solid rgba(6, 182, 212, 0.25)",
          borderRadius: "10px",
          padding: "12px 18px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{ fontSize: "18px" }}>ℹ️</span>
          <span style={{ fontSize: "0.85rem", color: "#cbd5e1" }}>
            Nagpur Smart City Monsoon Watch: <strong>{metrics?.active_road_closures ?? 0} active road closures</strong> and{" "}
            <strong>{metrics?.total_incidents ?? 0} verified waterlogged locations</strong> tracked in real time.
          </span>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <button
            onClick={() => onNavigateTab("routing")}
            className="btn-primary"
            style={{ padding: "6px 14px", fontSize: "0.8rem" }}
          >
            🧭 Safe Route Recommender
          </button>
          <button
            onClick={() => onNavigateTab("citizen")}
            className="btn-secondary"
            style={{ padding: "6px 14px", fontSize: "0.8rem" }}
          >
            📢 Report Waterlogging
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "14px",
        }}
      >
        <div className="glass-panel glass-panel-hover" style={{ padding: "16px" }}>
          <div style={{ fontSize: "11px", color: "#94a3b8", textTransform: "uppercase", fontWeight: 600 }}>
            Active Waterlogging
          </div>
          <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "#f87171", marginTop: "4px" }}>
            {metrics?.total_incidents ?? 0}
          </div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>
            {metrics?.high_risk_locations ?? 0} critical/high severity
          </div>
        </div>

        <div className="glass-panel glass-panel-hover" style={{ padding: "16px" }}>
          <div style={{ fontSize: "11px", color: "#94a3b8", textTransform: "uppercase", fontWeight: 600 }}>
            Road Closures
          </div>
          <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "#fb923c", marginTop: "4px" }}>
            {metrics?.active_road_closures ?? 0}
          </div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>
            Active barricades & diversions
          </div>
        </div>

        <div className="glass-panel glass-panel-hover" style={{ padding: "16px" }}>
          <div style={{ fontSize: "11px", color: "#94a3b8", textTransform: "uppercase", fontWeight: 600 }}>
            Chronic Hotspots
          </div>
          <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "#c084fc", marginTop: "4px" }}>
            {metrics?.chronic_hotspots ?? 0}
          </div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>
            RUBs & vulnerable lowlands
          </div>
        </div>

        <div className="glass-panel glass-panel-hover" style={{ padding: "16px" }}>
          <div style={{ fontSize: "11px", color: "#94a3b8", textTransform: "uppercase", fontWeight: 600 }}>
            Citizen Reports
          </div>
          <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "#38bdf8", marginTop: "4px" }}>
            {metrics?.unverified_citizen_reports ?? 0}
          </div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>
            Pending authority review
          </div>
        </div>

        <div className="glass-panel glass-panel-hover" style={{ padding: "16px" }}>
          <div style={{ fontSize: "11px", color: "#94a3b8", textTransform: "uppercase", fontWeight: 600 }}>
            Rainfall 24h Total
          </div>
          <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "#34d399", marginTop: "4px" }}>
            {weather?.rainfall_24h_mm ?? 0} <span style={{ fontSize: "1rem" }}>mm</span>
          </div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>
            Live Open-Meteo Nagpur
          </div>
        </div>
      </div>

      {/* Weather Breakdown & Quick Incidents Table */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "16px" }}>
        {/* Weather Card */}
        <div className="glass-panel" style={{ padding: "18px" }}>
          <h3 style={{ fontSize: "0.95rem", fontWeight: 700, marginBottom: "12px", color: "#f8fafc" }}>
            🌦️ Meteorological Radar
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", borderBottom: "1px solid rgba(255,255,255,0.06)", paddingBottom: "6px" }}>
              <span style={{ color: "#94a3b8" }}>1-Hour Precipitation</span>
              <span style={{ fontWeight: 600, color: "#38bdf8" }}>{weather?.rainfall_1h_mm ?? 0} mm</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", borderBottom: "1px solid rgba(255,255,255,0.06)", paddingBottom: "6px" }}>
              <span style={{ color: "#94a3b8" }}>3-Hour Cumulative</span>
              <span style={{ fontWeight: 600, color: "#38bdf8" }}>{weather?.rainfall_3h_mm ?? 0} mm</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", borderBottom: "1px solid rgba(255,255,255,0.06)", paddingBottom: "6px" }}>
              <span style={{ color: "#94a3b8" }}>6-Hour Cumulative</span>
              <span style={{ fontWeight: 600, color: "#38bdf8" }}>{weather?.rainfall_6h_mm ?? 0} mm</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", borderBottom: "1px solid rgba(255,255,255,0.06)", paddingBottom: "6px" }}>
              <span style={{ color: "#94a3b8" }}>Wind Speed</span>
              <span style={{ fontWeight: 600 }}>{weather?.wind_speed_kmh ?? 0} km/h</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
              <span style={{ color: "#94a3b8" }}>Station Status</span>
              <span style={{ color: "#34d399", fontWeight: 600 }}>{weather?.status ?? "ONLINE"}</span>
            </div>
          </div>
        </div>

        {/* Live Incidents Feed */}
        <div className="glass-panel" style={{ padding: "18px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#f8fafc" }}>
              ⚠️ Live Nagpur Incident Alerts
            </h3>
            <span style={{ fontSize: "11px", color: "#94a3b8" }}>Auto-updated from municipal field log</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "8px", maxHeight: "240px", overflowY: "auto" }}>
            {incidents.length === 0 ? (
              <div style={{ fontSize: "0.85rem", color: "#64748b", padding: "12px 0" }}>
                No active waterlogging incidents reported right now.
              </div>
            ) : (
              incidents.slice(0, 5).map((inc) => (
                <div
                  key={inc.id}
                  style={{
                    background: "rgba(255, 255, 255, 0.03)",
                    border: "1px solid rgba(255, 255, 255, 0.06)",
                    borderRadius: "8px",
                    padding: "10px 14px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600, fontSize: "0.88rem", color: "#f1f5f9" }}>{inc.title}</div>
                    <div style={{ fontSize: "0.78rem", color: "#94a3b8" }}>
                      {inc.location_name} {inc.water_depth_cm ? `• Depth: ${inc.water_depth_cm} cm` : ""}
                    </div>
                  </div>
                  <span
                    className={
                      inc.severity === "Critical" || inc.severity === "High"
                        ? "badge-high"
                        : inc.severity === "Moderate"
                        ? "badge-mod"
                        : "badge-low"
                    }
                  >
                    {inc.severity}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
