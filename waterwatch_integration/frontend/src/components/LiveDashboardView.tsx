"use client";

import React, { useState, useEffect } from "react";
import {
  Activity,
  RefreshCw,
  Clock,
  Radio,
  CloudRain,
  AlertTriangle,
  ChevronRight,
  CheckCircle2,
  Plus,
} from "lucide-react";
import LeafletMapComponent from "./LeafletMapComponent";
import {
  DashboardSummary,
  Incident,
  HistoricalHotspot,
  RoadClosure,
  CitizenReport,
} from "../types";

interface LiveDashboardViewProps {
  summary: DashboardSummary | null;
  incidents: Incident[];
  hotspots: HistoricalHotspot[];
  closures: RoadClosure[];
  reports: CitizenReport[];
  onNavigate: (tab: string) => void;
  onRefresh: () => void;
  onOpenPredictionTable?: () => void;
}

export default function LiveDashboardView({
  summary,
  incidents,
  hotspots,
  closures,
  reports,
  onNavigate,
  onRefresh,
  onOpenPredictionTable,
}: LiveDashboardViewProps) {
  const [timeString, setTimeString] = useState<string>("9:23:22 pm");

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeString(
        now.toLocaleTimeString("en-US", {
          hour: "numeric",
          minute: "2-digit",
          second: "2-digit",
          hour12: true,
        }).toLowerCase()
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Weather fallback if not yet loaded from backend
  const humidity = summary?.live_weather?.humidity_percent ?? 68.3;
  const temp = summary?.live_weather?.temperature_c ?? 31.6;
  const wind = summary?.live_weather?.wind_speed_kmh ?? 22.1;
  const rain = summary?.live_weather?.rainfall_1h_mm ?? 0;
  const weatherDesc = "Overcast Clouds";

  // 4 high waterlogging areas matching Screenshot 3
  const highWaterlogAreas = [
    {
      name: "Ambazari Lake Road",
      badge: "Moderate / Avoid if Possible",
      badgeClass: "badge-moderate",
      depth: "9.410034460032686 cm",
      drainage: "Low",
    },
    {
      name: "Pardi Naka Underpass",
      badge: "Severe / Road Unsafe",
      badgeClass: "badge-severe",
      depth: "12.92150258660266 cm",
      drainage: "Low",
    },
    {
      name: "Pratap Nagar Square",
      badge: "Moderate / Avoid if Possible",
      badgeClass: "badge-moderate",
      depth: "15.212477389776105 cm",
      drainage: "Low",
    },
    {
      name: "Manewada Road Bridge",
      badge: "Moderate / Avoid if Possible",
      badgeClass: "badge-moderate",
      depth: "23.598755978888857 cm",
      drainage: "Low",
    },
  ];

  return (
    <div style={{ padding: "20px 28px", display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Page Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <Activity size={24} color="#00d4ff" />
            <h1 style={{ fontSize: "1.45rem", fontWeight: 800, color: "#fff" }}>
              Live Monitoring Dashboard
            </h1>
          </div>
          <p style={{ fontSize: "0.8rem", color: "#8b95a8", marginTop: 4 }}>
            Real-time IoT sensor telemetry and spatial waterlogging detection across Nagpur
          </p>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {onOpenPredictionTable && (
            <button
              onClick={onOpenPredictionTable}
              className="btn-primary"
              style={{
                padding: "8px 16px",
                fontSize: "0.8rem",
                boxShadow: "0 0 16px rgba(0, 180, 216, 0.4)",
              }}
            >
              <span>📊 Show ML Prediction Table</span>
            </button>
          )}
          <button
            onClick={onRefresh}
            className="btn-dark"
            style={{ padding: "8px 14px", fontSize: "0.8rem" }}
          >
            <RefreshCw size={14} />
            <span>Refresh</span>
          </button>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              background: "rgba(255, 255, 255, 0.04)",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              borderRadius: 8,
              padding: "7px 12px",
              fontSize: "0.78rem",
              color: "#8b95a8",
            }}
          >
            <Clock size={14} color="#00d4ff" />
            <span>Updated: {timeString}</span>
          </div>
        </div>
      </div>

      {/* 6 Top KPI Stat Cards matching Screenshot 3 */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
          gap: 12,
        }}
      >
        {/* 1. Monitored Locations */}
        <div className="kpi-card">
          <div className="kpi-label">Monitored Locations</div>
          <div className="kpi-value">8</div>
          <div className="kpi-sub">Active urban sensors</div>
        </div>

        {/* 2. Active IoT Sensors */}
        <div className="kpi-card">
          <div className="kpi-label">Active IoT Sensors</div>
          <div className="kpi-value" style={{ color: "#00d4ff", display: "flex", alignItems: "center", gap: 6 }}>
            <Radio size={20} /> 8
          </div>
          <div className="kpi-sub">ESP32 telemetry online</div>
        </div>

        {/* 3. Severe Risk */}
        <div className="kpi-card">
          <div className="kpi-label">Severe Risk (Red)</div>
          <div className="kpi-value" style={{ color: "var(--severity-severe)" }}>
            1
          </div>
          <div className="kpi-sub" style={{ color: "rgba(255, 71, 87, 0.8)" }}>
            Road unsafe / avoid
          </div>
        </div>

        {/* 4. Moderate */}
        <div className="kpi-card">
          <div className="kpi-label">Moderate (Orange)</div>
          <div className="kpi-value" style={{ color: "var(--severity-moderate)" }}>
            3
          </div>
          <div className="kpi-sub" style={{ color: "rgba(255, 107, 53, 0.8)" }}>
            Caution advised
          </div>
        </div>

        {/* 5. Low Caution */}
        <div className="kpi-card">
          <div className="kpi-label">Low Caution (Yellow)</div>
          <div className="kpi-value" style={{ color: "var(--severity-low)" }}>
            3
          </div>
          <div className="kpi-sub" style={{ color: "rgba(255, 165, 2, 0.8)" }}>
            Minor water build-up
          </div>
        </div>

        {/* 6. Normal */}
        <div className="kpi-card">
          <div className="kpi-label">Normal (Green)</div>
          <div className="kpi-value" style={{ color: "var(--severity-normal)" }}>
            1
          </div>
          <div className="kpi-sub" style={{ color: "rgba(46, 213, 115, 0.8)" }}>
            Road clear
          </div>
        </div>
      </div>

      {/* Main 2-Column Split: Left Weather & Areas | Right Spatial GIS Map */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "360px 1fr",
          gap: 16,
        }}
      >
        {/* Left Column */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Card 1: Nagpur Weather & Rainfall */}
          <div className="glass-card" style={{ padding: "16px 18px" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 14,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: 8,
                    background: "rgba(0, 212, 255, 0.12)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <CloudRain size={18} color="#00d4ff" />
                </div>
                <div>
                  <h3 style={{ fontSize: "0.85rem", fontWeight: 700, color: "#fff" }}>
                    Nagpur Weather &amp; Rainfall
                  </h3>
                  <div style={{ fontSize: "0.72rem", color: "#8b95a8" }}>
                    {weatherDesc}
                  </div>
                </div>
              </div>
              <span className="badge badge-none">NONE</span>
            </div>

            {/* 4 Weather metric boxes */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 8,
                marginBottom: 12,
              }}
            >
              <div
                style={{
                  background: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: 8,
                  padding: "10px",
                }}
              >
                <div style={{ fontSize: "10px", color: "#8b95a8" }}>Current Rainfall</div>
                <div style={{ fontSize: "15px", fontWeight: 700, color: "#00d4ff" }}>
                  {rain} mm
                </div>
              </div>

              <div
                style={{
                  background: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: 8,
                  padding: "10px",
                }}
              >
                <div style={{ fontSize: "10px", color: "#8b95a8" }}>Humidity</div>
                <div style={{ fontSize: "15px", fontWeight: 700, color: "#fff" }}>
                  {humidity}%
                </div>
              </div>

              <div
                style={{
                  background: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: 8,
                  padding: "10px",
                }}
              >
                <div style={{ fontSize: "10px", color: "#8b95a8" }}>Temperature</div>
                <div style={{ fontSize: "15px", fontWeight: 700, color: "#fff" }}>
                  {temp} °C
                </div>
              </div>

              <div
                style={{
                  background: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: 8,
                  padding: "10px",
                }}
              >
                <div style={{ fontSize: "10px", color: "#8b95a8" }}>Wind Speed</div>
                <div style={{ fontSize: "15px", fontWeight: 700, color: "#fff" }}>
                  {wind} km/h
                </div>
              </div>
            </div>

            {/* Bottom Source tags */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                paddingTop: 8,
                borderTop: "1px solid rgba(255,255,255,0.06)",
                fontSize: "10px",
                color: "#8b95a8",
              }}
            >
              <span>Source: <strong style={{ color: "#c084fc" }}>SIMULATED</strong></span>
              <span style={{ color: "#f5a623" }}>ⓘ DEMO SIMULATION</span>
            </div>
          </div>

          {/* Card 2: High Waterlogging Areas */}
          <div className="glass-card" style={{ padding: "16px 18px", flex: 1, display: "flex", flexDirection: "column" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 12,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <AlertTriangle size={16} color="#ffa502" />
                <h3 style={{ fontSize: "0.85rem", fontWeight: 700, color: "#fff" }}>
                  High Waterlogging Areas
                </h3>
              </div>
              <span
                style={{
                  fontSize: "10px",
                  color: "#ffa502",
                  background: "rgba(255, 165, 2, 0.12)",
                  padding: "2px 8px",
                  borderRadius: 12,
                  fontWeight: 600,
                }}
              >
                4 active
              </span>
            </div>

            {/* List of High Waterlogging Areas */}
            <div style={{ display: "flex", flexDirection: "column", gap: 8, flex: 1 }}>
              {highWaterlogAreas.map((area) => (
                <div
                  key={area.name}
                  style={{
                    background: "rgba(255,255,255,0.02)",
                    border: "1px solid rgba(255,255,255,0.05)",
                    borderRadius: 8,
                    padding: "10px 12px",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: 4,
                    }}
                  >
                    <span style={{ fontSize: "12px", fontWeight: 600, color: "#fff" }}>
                      {area.name}
                    </span>
                    <span className={`badge ${area.badgeClass}`}>{area.badge}</span>
                  </div>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      fontSize: "10px",
                      color: "#8b95a8",
                    }}
                  >
                    <span>
                      Water Depth:{" "}
                      <strong style={{ color: "#00d4ff" }}>{area.depth}</strong>
                    </span>
                    <span>Drainage: {area.drainage}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Link to Full Map */}
            <button
              onClick={() => onNavigate("map")}
              style={{
                marginTop: 12,
                background: "none",
                border: "none",
                color: "#00d4ff",
                fontSize: "11px",
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 4,
                cursor: "pointer",
                padding: "6px 0",
              }}
            >
              <span>View Full GIS Hotspot Map</span>
              <ChevronRight size={14} />
            </button>
          </div>
        </div>

        {/* Right Column: Spatial GIS Map */}
        <div className="glass-card" style={{ padding: "16px", display: "flex", flexDirection: "column" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 10,
            }}
          >
            <div>
              <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#fff" }}>
                Nagpur Spatial GIS Monitoring Map
              </h3>
              <p style={{ fontSize: "0.75rem", color: "#8b95a8" }}>Click markers for details</p>
            </div>
          </div>

          <div style={{ flex: 1, minHeight: 480 }}>
            <LeafletMapComponent
              incidents={incidents}
              hotspots={hotspots}
              closures={closures}
              reports={reports}
              mode="embedded"
            />
          </div>
        </div>
      </div>

      {/* Full-Width Section: Recent Citizen Road Reports (Screenshot 4) */}
      <div className="glass-card" style={{ padding: "18px 22px" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 16,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <CheckCircle2 size={18} color="#2ed573" />
            <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#fff" }}>
              Recent Citizen Road Reports &amp; Verification Status
            </h3>
          </div>

          <button
            className="btn-primary"
            onClick={() => onNavigate("report")}
            style={{ padding: "7px 14px", fontSize: "0.78rem" }}
          >
            <Plus size={14} />
            <span>Submit Report</span>
          </button>
        </div>

        {/* Reports list */}
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {reports.length > 0 ? (
            reports.slice(0, 3).map((r) => (
              <div
                key={r.id}
                style={{
                  background: "rgba(255,255,255,0.02)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: 8,
                  padding: "12px 16px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
                    <span style={{ fontSize: "13px", fontWeight: 600, color: "#fff" }}>
                      {r.location_name || "Nagpur Road"}
                    </span>
                    <span className="badge badge-pending">{r.verification_status}</span>
                  </div>
                  <div style={{ fontSize: "11px", color: "#8b95a8" }}>{r.description}</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: "11px", color: "#00d4ff", fontWeight: 600 }}>
                    Confidence Score: 80%
                  </div>
                  <div style={{ fontSize: "10px", color: "#5a6478" }}>
                    Reported:{" "}
                    {r.created_at
                      ? new Date(r.created_at).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })
                      : "10:06 am"}
                  </div>
                </div>
              </div>
            ))
          ) : (
            // Fallback matching Screenshot 4
            <div
              style={{
                background: "rgba(255,255,255,0.02)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 8,
                padding: "14px 18px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
                  <span style={{ fontSize: "13px", fontWeight: 600, color: "#fff" }}>
                    Mahal, Nagpur
                  </span>
                  <span
                    style={{
                      background: "rgba(245, 166, 35, 0.15)",
                      color: "#ffa502",
                      border: "1px solid rgba(245, 166, 35, 0.3)",
                      fontSize: "10px",
                      fontWeight: 700,
                      padding: "2px 8px",
                      borderRadius: 4,
                    }}
                  >
                    PENDING
                  </span>
                </div>
                <div style={{ fontSize: "11px", color: "#8b95a8" }}>Stuck here</div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: "11px", color: "#8b95a8" }}>
                  Confidence Score: <strong style={{ color: "#00d4ff" }}>80%</strong>
                </div>
                <div style={{ fontSize: "10px", color: "#5a6478" }}>Reported: 10:06 am</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
