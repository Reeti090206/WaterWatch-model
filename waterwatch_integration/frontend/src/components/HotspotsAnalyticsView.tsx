"use client";

import React from "react";
import { HistoricalHotspot } from "../types";

interface HotspotProps {
  hotspots: HistoricalHotspot[];
}

export default function HotspotsAnalyticsView({ hotspots }: HotspotProps) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      <div className="glass-panel" style={{ padding: "20px" }}>
        <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#f8fafc", marginBottom: "6px" }}>
          ⚠️ Nagpur Chronic Flood Hotspots & Vulnerable Corridors
        </h3>
        <p style={{ fontSize: "0.85rem", color: "#94a3b8" }}>
          Historical lowlands, Railway Underbridges (RUBs), and arterial chokepoints prone to recurrent inundation during heavy precipitation events.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "16px" }}>
        {hotspots.map((h) => (
          <div
            key={h.id}
            className="glass-panel glass-panel-hover"
            style={{ padding: "20px", display: "flex", flexDirection: "column", gap: "10px" }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <h4 style={{ fontSize: "1rem", fontWeight: 700, color: "#f1f5f9" }}>{h.name}</h4>
                <div style={{ fontSize: "12px", color: "#94a3b8" }}>Locality: {h.locality}</div>
              </div>
              <span
                style={{
                  background: "rgba(139, 92, 246, 0.2)",
                  color: "#c084fc",
                  border: "1px solid rgba(139, 92, 246, 0.4)",
                  padding: "2px 8px",
                  borderRadius: "4px",
                  fontSize: "11px",
                  fontWeight: 600,
                }}
              >
                {h.hotspot_code}
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", background: "rgba(15, 23, 42, 0.6)", padding: "10px", borderRadius: "8px", fontSize: "12px" }}>
              <div>
                <span style={{ color: "#64748b" }}>Avg Inundation:</span>
                <div style={{ fontWeight: 700, color: "#f87171" }}>{h.average_depth_cm} cm</div>
              </div>
              <div>
                <span style={{ color: "#64748b" }}>Critical Rain Threshold:</span>
                <div style={{ fontWeight: 700, color: "#38bdf8" }}>{h.typical_critical_threshold_mm} mm/h</div>
              </div>
              <div>
                <span style={{ color: "#64748b" }}>Drainage Efficiency:</span>
                <div style={{ fontWeight: 600 }}>{(h.drainage_capacity_proxy * 100).toFixed(0)}%</div>
              </div>
              <div>
                <span style={{ color: "#64748b" }}>5-Year Events:</span>
                <div style={{ fontWeight: 600 }}>{h.incident_count_last_5yr} floods</div>
              </div>
            </div>

            <div style={{ fontSize: "12px", color: "#cbd5e1" }}>
              <strong>Underlying Cause:</strong> {h.chronic_cause}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
