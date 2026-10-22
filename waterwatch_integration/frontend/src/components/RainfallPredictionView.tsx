"use client";

import React, { useState } from "react";
import { RainfallPredictionResponse } from "../types";
import { api } from "../services/api";

export default function RainfallPredictionView() {
  const [locality, setLocality] = useState("Sitabuldi Ward 12");
  const [r1, setR1] = useState(42.5);
  const [r3, setR3] = useState(78.0);
  const [r6, setR6] = useState(115.0);
  const [r24, setR24] = useState(140.0);
  const [r72, setR72] = useState(165.0);
  const [drainage, setDrainage] = useState(0.45);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RainfallPredictionResponse | null>(null);

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await api.predictRainfallRisk({
        locality_name: locality,
        rainfall_1h_mm: Number(r1),
        rainfall_3h_mm: Number(r3),
        rainfall_6h_mm: Number(r6),
        rainfall_24h_mm: Number(r24),
        rainfall_prev_72h_mm: Number(r72),
        drainage_capacity_proxy: Number(drainage),
      });
      setResult(response);
    } catch (err: any) {
      setError(err.message || "Failed to run rainfall prediction");
    } finally {
      setLoading(false);
    }
  };

  const applyPreset = (preset: "heavy" | "moderate" | "light") => {
    if (preset === "heavy") {
      setR1(65.0);
      setR3(110.0);
      setR6(160.0);
      setR24(210.0);
      setR72(250.0);
      setDrainage(0.35);
    } else if (preset === "moderate") {
      setR1(22.0);
      setR3(45.0);
      setR6(70.0);
      setR24(95.0);
      setR72(110.0);
      setDrainage(0.55);
    } else {
      setR1(4.0);
      setR3(8.0);
      setR6(12.0);
      setR24(15.0);
      setR72(20.0);
      setDrainage(0.8);
    }
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "20px" }}>
      {/* Input Form */}
      <div className="glass-panel" style={{ padding: "22px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
          <div>
            <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#f8fafc" }}>
              🌧️ Predictive Rainfall Risk Model
            </h3>
            <p style={{ fontSize: "0.82rem", color: "#94a3b8", marginTop: "2px" }}>
              Infers waterlogging probability using trained scikit-learn pipeline.
            </p>
          </div>
          <span className="badge-synthetic">SYNTHETIC_EXPERIMENTAL</span>
        </div>

        {/* Presets */}
        <div style={{ display: "flex", gap: "8px", marginBottom: "18px", alignItems: "center" }}>
          <span style={{ fontSize: "11px", color: "#64748b" }}>Test Scenarios:</span>
          <button
            type="button"
            onClick={() => applyPreset("heavy")}
            className="btn-secondary"
            style={{ padding: "4px 10px", fontSize: "11px" }}
          >
            ⛈️ Heavy Monsoon (65mm/h)
          </button>
          <button
            type="button"
            onClick={() => applyPreset("moderate")}
            className="btn-secondary"
            style={{ padding: "4px 10px", fontSize: "11px" }}
          >
            🌦️ Moderate (22mm/h)
          </button>
          <button
            type="button"
            onClick={() => applyPreset("light")}
            className="btn-secondary"
            style={{ padding: "4px 10px", fontSize: "11px" }}
          >
            🌤️ Light Drizzle (4mm/h)
          </button>
        </div>

        <form onSubmit={handlePredict} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          <div>
            <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "4px" }}>
              Nagpur Locality Name
            </label>
            <input
              type="text"
              className="input-field"
              value={locality}
              onChange={(e) => setLocality(e.target.value)}
              required
            />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "4px" }}>
                1-Hour Rainfall (mm)
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                className="input-field"
                value={r1}
                onChange={(e) => setR1(Number(e.target.value))}
                required
              />
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "4px" }}>
                3-Hour Cumulative (mm)
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                className="input-field"
                value={r3}
                onChange={(e) => setR3(Number(e.target.value))}
                required
              />
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "4px" }}>
                6-Hour Cumulative (mm)
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                className="input-field"
                value={r6}
                onChange={(e) => setR6(Number(e.target.value))}
                required
              />
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "4px" }}>
                24-Hour Cumulative (mm)
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                className="input-field"
                value={r24}
                onChange={(e) => setR24(Number(e.target.value))}
                required
              />
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "4px" }}>
                Antecedent 72h Rainfall (mm)
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                className="input-field"
                value={r72}
                onChange={(e) => setR72(Number(e.target.value))}
                required
              />
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "4px" }}>
                Drainage Capacity Proxy (0.0 - 1.0)
              </label>
              <input
                type="number"
                step="0.05"
                min="0"
                max="1"
                className="input-field"
                value={drainage}
                onChange={(e) => setDrainage(Number(e.target.value))}
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
            style={{ marginTop: "6px" }}
          >
            {loading ? "Running ML Inference..." : "⚡ Run Waterlogging Prediction"}
          </button>
        </form>

        {error && (
          <div style={{ marginTop: "14px", color: "#f87171", fontSize: "0.85rem" }}>
            ⚠️ {error}
          </div>
        )}
      </div>

      {/* Results Display */}
      <div className="glass-panel" style={{ padding: "22px", display: "flex", flexDirection: "column" }}>
        <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#f8fafc", marginBottom: "16px" }}>
          Inference Assessment Result
        </h3>

        {!result ? (
          <div
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              color: "#64748b",
              textAlign: "center",
              padding: "40px 20px",
            }}
          >
            <div style={{ fontSize: "3rem", marginBottom: "10px" }}>📊</div>
            <p style={{ fontSize: "0.9rem" }}>Select parameters and click Run Prediction</p>
            <p style={{ fontSize: "0.75rem", color: "#475569", marginTop: "4px" }}>
              Inference is processed by synthetic_rainfall_model.joblib
            </p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* Probability Gauge Box */}
            <div
              style={{
                background: "rgba(15, 23, 42, 0.8)",
                border: "1px solid rgba(255, 255, 255, 0.08)",
                borderRadius: "10px",
                padding: "16px",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: "11px", color: "#94a3b8", textTransform: "uppercase", fontWeight: 600 }}>
                Waterlogging Activation Probability
              </div>
              <div
                style={{
                  fontSize: "2.8rem",
                  fontWeight: 900,
                  marginTop: "6px",
                  color:
                    result.risk_category === "HIGH"
                      ? "#f87171"
                      : result.risk_category === "MODERATE"
                      ? "#fbbf24"
                      : "#34d399",
                }}
              >
                {(result.predicted_probability * 100).toFixed(1)}%
              </div>
              <div style={{ marginTop: "8px" }}>
                <span
                  className={
                    result.risk_category === "HIGH"
                      ? "badge-high"
                      : result.risk_category === "MODERATE"
                      ? "badge-mod"
                      : "badge-low"
                  }
                >
                  RISK LEVEL: {result.risk_category}
                </span>
              </div>
            </div>

            {/* Model Metadata */}
            <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "0.85rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid rgba(255,255,255,0.06)", paddingBottom: "6px" }}>
                <span style={{ color: "#94a3b8" }}>Target Locality:</span>
                <span style={{ fontWeight: 600 }}>{result.location}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid rgba(255,255,255,0.06)", paddingBottom: "6px" }}>
                <span style={{ color: "#94a3b8" }}>Model Pipeline:</span>
                <span style={{ fontWeight: 600, color: "#38bdf8" }}>{result.model_name} (StandardScaler)</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid rgba(255,255,255,0.06)", paddingBottom: "6px" }}>
                <span style={{ color: "#94a3b8" }}>Binary Decision:</span>
                <span style={{ fontWeight: 700, color: result.waterlogging_predicted ? "#f87171" : "#34d399" }}>
                  {result.waterlogging_predicted ? "WATERLOGGING DETECTED (Class 1)" : "SAFE / NO FLOOD (Class 0)"}
                </span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "#94a3b8" }}>Provenance Tag:</span>
                <span className="badge-synthetic">{result.training_data_status}</span>
              </div>
            </div>

            {/* Scientific Disclaimer */}
            <div
              style={{
                background: "rgba(147, 51, 234, 0.08)",
                border: "1px solid rgba(147, 51, 234, 0.25)",
                borderRadius: "8px",
                padding: "10px",
                fontSize: "11px",
                color: "#d8b4fe",
                lineHeight: 1.4,
              }}
            >
              <strong>Scientific Notice:</strong> {result.scientific_disclaimer}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
