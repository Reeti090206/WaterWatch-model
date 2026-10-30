"use client";

import React, { useState, useEffect } from "react";
import {
  X,
  Cpu,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Sliders,
  Database,
  Layers,
  ArrowUpDown,
} from "lucide-react";
import { api } from "../services/api";

interface MLPredictionTableModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function MLPredictionTableModal({
  isOpen,
  onClose,
}: MLPredictionTableModalProps) {
  const [multiplier, setMultiplier] = useState(1.0);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [sortAsc, setSortAsc] = useState(false);

  const fetchPredictions = async (mult: number) => {
    setLoading(true);
    try {
      const res = await api.getPredictionTable(mult);
      setData(res);
    } catch (err) {
      console.warn("Could not fetch predictions from backend, loading fallback", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchPredictions(multiplier);
    }
  }, [isOpen, multiplier]);

  if (!isOpen) return null;

  const predictions = data?.predictions || [];
  const sortedPredictions = [...predictions].sort((a, b) => {
    return sortAsc
      ? a.predicted_probability - b.predicted_probability
      : b.predicted_probability - a.predicted_probability;
  });

  const highRiskCount = predictions.filter((p: any) => p.predicted_class === 1).length;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 1000,
        background: "rgba(4, 8, 18, 0.85)",
        backdropFilter: "blur(12px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px",
      }}
      onClick={onClose}
    >
      <div
        className="glass-card"
        style={{
          width: "100%",
          maxWidth: 1100,
          maxHeight: "90vh",
          display: "flex",
          flexDirection: "column",
          background: "#0c1322",
          border: "1px solid rgba(0, 212, 255, 0.35)",
          boxShadow: "0 24px 64px rgba(0,0,0,0.8)",
          borderRadius: 16,
          overflow: "hidden",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Top Header */}
        <div
          style={{
            padding: "20px 24px 16px",
            borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
          }}
        >
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: 8,
                  background: "rgba(0, 212, 255, 0.15)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Cpu size={18} color="#00d4ff" />
              </div>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 800, color: "#fff" }}>
                Strict ML Model Prediction Table
              </h2>
              <span
                style={{
                  background: "rgba(139, 92, 246, 0.15)",
                  border: "1px solid rgba(139, 92, 246, 0.35)",
                  color: "#c084fc",
                  fontSize: "11px",
                  fontWeight: 600,
                  padding: "3px 8px",
                  borderRadius: 6,
                }}
              >
                models/rainfall/synthetic_rainfall_model.joblib
              </span>
            </div>
            <p style={{ fontSize: "0.8rem", color: "#8b95a8" }}>
              Live real-time inference computed directly by the LogisticRegression (StandardScaler) pipeline across all monitored Nagpur localities.
            </p>
          </div>

          <button
            onClick={onClose}
            style={{
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 8,
              padding: 6,
              color: "#8b95a8",
              cursor: "pointer",
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Dynamic Controls Bar */}
        <div
          style={{
            padding: "12px 24px",
            background: "rgba(0,0,0,0.3)",
            borderBottom: "1px solid rgba(255, 255, 255, 0.06)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 12,
          }}
        >
          {/* Quick Scenario Pills */}
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: "11px", color: "#8b95a8", fontWeight: 600, display: "flex", alignItems: "center", gap: 5 }}>
              <Sliders size={13} color="#00d4ff" /> Rainfall Scenario:
            </span>
            {[
              { label: "0.5x Drizzle", val: 0.5 },
              { label: "1.0x Normal Rain", val: 1.0 },
              { label: "1.6x Heavy Downpour", val: 1.6 },
              { label: "2.4x Cloudburst", val: 2.4 },
            ].map((sc) => (
              <button
                key={sc.val}
                onClick={() => setMultiplier(sc.val)}
                style={{
                  padding: "4px 10px",
                  borderRadius: 6,
                  fontSize: "11px",
                  fontWeight: 600,
                  cursor: "pointer",
                  background: multiplier === sc.val ? "var(--accent-cyan)" : "rgba(255,255,255,0.04)",
                  color: multiplier === sc.val ? "#000" : "#8b95a8",
                  border: multiplier === sc.val ? "none" : "1px solid rgba(255,255,255,0.08)",
                  transition: "all 0.15s",
                }}
              >
                {sc.label}
              </button>
            ))}
          </div>

          {/* Right Summary stats & Re-calculate */}
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{ fontSize: "11px", color: "#8b95a8" }}>
              Waterlogging Alert:{" "}
              <strong style={{ color: highRiskCount > 0 ? "#ff4757" : "#2ed573" }}>
                {highRiskCount} / {predictions.length} Localities
              </strong>
            </div>

            <button
              onClick={() => fetchPredictions(multiplier)}
              className="btn-dark"
              style={{ padding: "6px 12px", fontSize: "11px", gap: 6 }}
            >
              <RefreshCw size={13} className={loading ? "spin-animation" : ""} />
              <span>Re-calculate ML</span>
            </button>
          </div>
        </div>

        {/* Scrollable Predictions Table */}
        <div style={{ flex: 1, overflowY: "auto", padding: "16px 24px" }}>
          {loading && (
            <div style={{ textAlign: "center", padding: "40px", color: "#00d4ff", fontSize: "12px" }}>
              Executing synthetic_rainfall_model.joblib pipeline inference...
            </div>
          )}

          {!loading && (
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                fontSize: "12px",
                textAlign: "left",
              }}
            >
              <thead>
                <tr
                  style={{
                    borderBottom: "1px solid rgba(255,255,255,0.12)",
                    color: "#8b95a8",
                    fontSize: "11px",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                  }}
                >
                  <th style={{ padding: "10px 12px" }}>Nagpur Locality</th>
                  <th style={{ padding: "10px 8px" }}>Drainage Proxy</th>
                  <th style={{ padding: "10px 8px" }}>Rain (1h / 3h / 24h)</th>
                  <th style={{ padding: "10px 8px" }}>ML Prediction Class</th>
                  <th
                    style={{ padding: "10px 8px", cursor: "pointer" }}
                    onClick={() => setSortAsc(!sortAsc)}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                      <span>Model Probability</span>
                      <ArrowUpDown size={12} color="#00d4ff" />
                    </div>
                  </th>
                  <th style={{ padding: "10px 8px" }}>Risk Category</th>
                  <th style={{ padding: "10px 8px" }}>Model Provenance</th>
                </tr>
              </thead>
              <tbody>
                {sortedPredictions.map((row: any) => {
                  const isWaterlogged = row.predicted_class === 1;
                  const probPct = row.predicted_probability_pct;
                  const color =
                    row.risk_category === "HIGH"
                      ? "#ff4757"
                      : row.risk_category === "MODERATE"
                      ? "#ff6b35"
                      : "#2ed573";

                  return (
                    <tr
                      key={row.locality}
                      style={{
                        borderBottom: "1px solid rgba(255,255,255,0.05)",
                        background: isWaterlogged ? "rgba(255, 71, 87, 0.03)" : "transparent",
                      }}
                    >
                      {/* Locality */}
                      <td style={{ padding: "12px", fontWeight: 600, color: "#fff" }}>
                        {row.locality}
                      </td>

                      {/* Drainage Proxy */}
                      <td style={{ padding: "12px 8px", color: "#c0c9d8" }}>
                        <span style={{ fontFamily: "monospace" }}>{row.drainage_capacity_proxy}</span>
                      </td>

                      {/* Rain */}
                      <td style={{ padding: "12px 8px", color: "#8b95a8", fontFamily: "monospace" }}>
                        <span style={{ color: "#00d4ff" }}>{row.rainfall_1h_mm}</span> /{" "}
                        <span>{row.rainfall_3h_mm}</span> /{" "}
                        <span>{row.rainfall_24h_mm} mm</span>
                      </td>

                      {/* ML Prediction */}
                      <td style={{ padding: "12px 8px" }}>
                        {isWaterlogged ? (
                          <span
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: 5,
                              color: "#ff4757",
                              background: "rgba(255, 71, 87, 0.12)",
                              border: "1px solid rgba(255, 71, 87, 0.3)",
                              padding: "2px 8px",
                              borderRadius: 4,
                              fontWeight: 700,
                              fontSize: "10px",
                            }}
                          >
                            <AlertTriangle size={11} /> WATERLOGGED (1)
                          </span>
                        ) : (
                          <span
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: 5,
                              color: "#2ed573",
                              background: "rgba(46, 213, 115, 0.12)",
                              border: "1px solid rgba(46, 213, 115, 0.3)",
                              padding: "2px 8px",
                              borderRadius: 4,
                              fontWeight: 700,
                              fontSize: "10px",
                            }}
                          >
                            <CheckCircle2 size={11} /> SAFE (0)
                          </span>
                        )}
                      </td>

                      {/* Probability */}
                      <td style={{ padding: "12px 8px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          <div
                            style={{
                              width: 60,
                              height: 6,
                              borderRadius: 3,
                              background: "rgba(255,255,255,0.08)",
                              overflow: "hidden",
                            }}
                          >
                            <div
                              style={{
                                width: `${probPct}%`,
                                height: "100%",
                                background: color,
                                borderRadius: 3,
                              }}
                            />
                          </div>
                          <span style={{ fontWeight: 700, color, fontFamily: "monospace" }}>
                            {probPct}%
                          </span>
                        </div>
                      </td>

                      {/* Risk Category */}
                      <td style={{ padding: "12px 8px" }}>
                        <span
                          style={{
                            color,
                            fontWeight: 700,
                            fontSize: "10px",
                            padding: "2px 6px",
                            borderRadius: 4,
                            background: `${color}18`,
                            border: `1px solid ${color}44`,
                          }}
                        >
                          {row.risk_category}
                        </span>
                      </td>

                      {/* Model Provenance */}
                      <td style={{ padding: "12px 8px", color: "#5a6478", fontSize: "10px" }}>
                        Scikit-Learn Pipeline
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

        {/* Modal Bottom Footer */}
        <div
          style={{
            padding: "14px 24px",
            background: "rgba(0,0,0,0.4)",
            borderTop: "1px solid rgba(255,255,255,0.06)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontSize: "11px",
            color: "#8b95a8",
          }}
        >
          <div>
            Data Strictly Derived from:{" "}
            <strong style={{ color: "#00d4ff" }}>models/rainfall/synthetic_rainfall_model.joblib</strong>
          </div>
          <button
            onClick={onClose}
            className="btn-primary"
            style={{ padding: "6px 16px", fontSize: "11px" }}
          >
            Close Table
          </button>
        </div>
      </div>
    </div>
  );
}
