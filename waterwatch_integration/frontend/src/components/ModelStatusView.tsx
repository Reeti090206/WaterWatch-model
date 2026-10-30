"use client";

import React, { useEffect, useState } from "react";
import { api } from "../services/api";

export default function ModelStatusView() {
  const [modelData, setModelData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getModelsStatus()
      .then((data) => setModelData(data))
      .catch((err) => console.error("Failed to load model status", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      <div className="glass-panel" style={{ padding: "20px" }}>
        <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#f8fafc", marginBottom: "6px" }}>
          🧠 Machine Learning & Data Provenance Matrix
        </h3>
        <p style={{ fontSize: "0.85rem", color: "#94a3b8" }}>
          Full architectural transparency regarding model training data, municipal operational readiness, and strict research integrity.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "16px" }}>
        {/* Synthetic Rainfall Model */}
        <div className="glass-panel" style={{ padding: "20px", borderLeft: "4px solid #8b5cf6" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "10px" }}>
            <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#f8fafc" }}>
              Experimental Rainfall Risk Model
            </h4>
            <span className="badge-synthetic">READY_EXPERIMENTAL</span>
          </div>
          <div style={{ fontSize: "12px", color: "#cbd5e1", lineHeight: 1.5, display: "flex", flexDirection: "column", gap: "6px" }}>
            <div><strong>Algorithm:</strong> LogisticRegression with StandardScaler</div>
            <div><strong>Artifact:</strong> <code>models/rainfall/synthetic_rainfall_model.joblib</code></div>
            <div><strong>Features:</strong> 1h, 3h, 6h, 24h, 72h accumulation, drainage proxy</div>
            <div><strong>Status:</strong> Operational for integration, routing, and simulation.</div>
            <div style={{ background: "rgba(139, 92, 246, 0.15)", padding: "8px", borderRadius: "6px", color: "#c084fc", fontSize: "11px", marginTop: "6px" }}>
              ⚠️ <strong>Provenance:</strong> Trained on synthetic demonstration data. Demonstrates pipeline integrity and API contract compliance without falsifying official records.
            </div>
          </div>
        </div>

        {/* Municipal Ground Truth Model */}
        <div className="glass-panel" style={{ padding: "20px", borderLeft: "4px solid #f97316" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "10px" }}>
            <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#f8fafc" }}>
              Municipal Production Model
            </h4>
            <span style={{ background: "rgba(249, 115, 22, 0.2)", color: "#fb923c", border: "1px solid rgba(249, 115, 22, 0.4)", padding: "3px 8px", borderRadius: "6px", fontSize: "0.7rem", fontWeight: 600 }}>
              BLOCKED ON DATA
            </span>
          </div>
          <div style={{ fontSize: "12px", color: "#cbd5e1", lineHeight: 1.5, display: "flex", flexDirection: "column", gap: "6px" }}>
            <div><strong>Target Scope:</strong> Calibrated municipal waterlogging warning system for NMC.</div>
            <div><strong>Blocker Reason:</strong> Genuine municipal ground-truth waterlogging records from Nagpur Municipal Corporation / traffic police are not yet released.</div>
            <div><strong>Integrity Safeguard:</strong> Production workflow remains strictly blocked until official records are ingested.</div>
            <div style={{ background: "rgba(249, 115, 22, 0.15)", padding: "8px", borderRadius: "6px", color: "#fdba74", fontSize: "11px", marginTop: "6px" }}>
              🛡️ <strong>Integrity Commitment:</strong> Zero synthetic records have been inserted into the official verified dataset.
            </div>
          </div>
        </div>

        {/* YOLOv11 Model */}
        <div className="glass-panel" style={{ padding: "20px", borderLeft: "4px solid #06b6d4" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "10px" }}>
            <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#f8fafc" }}>
              Image-Based Flood Detector
            </h4>
            <span style={{ background: "rgba(6, 182, 212, 0.2)", color: "#38bdf8", border: "1px solid rgba(6, 182, 212, 0.4)", padding: "3px 8px", borderRadius: "6px", fontSize: "0.7rem", fontWeight: 600 }}>
              READY_OPERATIONAL
            </span>
          </div>
          <div style={{ fontSize: "12px", color: "#cbd5e1", lineHeight: 1.5, display: "flex", flexDirection: "column", gap: "6px" }}>
            <div><strong>Architecture:</strong> Ultralytics YOLOv11 Nano (yolo11n)</div>
            <div><strong>Artifact:</strong> <code>models/image/best.pt</code></div>
            <div><strong>Classes:</strong> <code>water_logging</code> (bounding box surface reflection)</div>
            <div><strong>Inference Time:</strong> ~15-25 ms on CPU</div>
            <div style={{ background: "rgba(6, 182, 212, 0.15)", padding: "8px", borderRadius: "6px", color: "#67e8f9", fontSize: "11px", marginTop: "6px" }}>
              ℹ️ <strong>Physical Scope:</strong> Detects optical standing water surfaces. Depth in cm requires physical gauge calibration.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
