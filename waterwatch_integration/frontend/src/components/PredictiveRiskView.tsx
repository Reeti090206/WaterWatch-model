"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  RefreshCw,
  TrendingUp,
  Sliders,
  Info,
  CheckCircle2,
  CloudRain,
  ShieldAlert,
} from "lucide-react";

interface PredictiveRiskViewProps {
  onOpenPredictionTable?: () => void;
}

export default function PredictiveRiskView({
  onOpenPredictionTable,
}: PredictiveRiskViewProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRerun = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 800);
  };

  // Location risk data matching Nagpur localities
  const locationForecasts = [
    {
      name: "Pardi Naka Underpass",
      riskCategory: "HIGH",
      riskScore: 82,
      riskColor: "#ff4757",
      rainfallImpact: "Severe (Depression basin)",
      drainageCapacity: "Low (Submersible pumps restricted)",
      advice: "Route closure recommended for heavy downpours",
    },
    {
      name: "Ambazari Lake Road",
      riskCategory: "MODERATE",
      riskScore: 58,
      riskColor: "#ff6b35",
      rainfallImpact: "Overflow runoff from lake spillway",
      drainageCapacity: "Moderate (Natural canal flow)",
      advice: "Drive with caution, avoid edge shoulders",
    },
    {
      name: "Pratap Nagar Square",
      riskCategory: "MODERATE",
      riskScore: 54,
      riskColor: "#ff6b35",
      rainfallImpact: "Intersection ponding at low grade",
      drainageCapacity: "Low to Moderate",
      advice: "Expect slow moving traffic during showers",
    },
    {
      name: "Manewada Road Bridge",
      riskCategory: "MODERATE",
      riskScore: 51,
      riskColor: "#ff6b35",
      rainfallImpact: "Culvert backflow during cloudburst",
      drainageCapacity: "Moderate",
      advice: "Monitor telemetry sensors",
    },
    {
      name: "Civil Lines VIP Road",
      riskCategory: "LOW",
      riskScore: 14,
      riskColor: "#2ed573",
      rainfallImpact: "Minimal surface retention",
      drainageCapacity: "High (Underground stormwater network)",
      advice: "All lanes operational and safe",
    },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
      {/* Page Header matching Image 3 */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <AlertTriangle size={24} color="#ffa502" />
            <h1 style={{ fontSize: "1.45rem", fontWeight: 800, color: "#fff" }}>
              Predictive Waterlogging Risk Dashboard
            </h1>
          </div>
          <p style={{ fontSize: "0.8rem", color: "#8b95a8", marginTop: 4 }}>
            Rainfall-based risk estimation combining historical frequency, drainage capacity, and IoT sensors
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
            onClick={handleRerun}
            className="btn-dark"
            style={{ padding: "8px 16px", fontSize: "0.8rem", gap: 8 }}
          >
            <RefreshCw size={14} className={isRefreshing ? "spin-animation" : ""} />
            <span>Re-run Prediction Engine</span>
          </button>
        </div>
      </div>

      {/* Amber Academic Integrity & Methodology Disclaimer matching Image 3 */}
      <div
        style={{
          background: "rgba(245, 166, 35, 0.05)",
          border: "1px solid rgba(245, 166, 35, 0.3)",
          borderRadius: 10,
          padding: "14px 18px",
          display: "flex",
          alignItems: "flex-start",
          gap: 12,
        }}
      >
        <Info size={18} color="#ffa502" style={{ flexShrink: 0, marginTop: 2 }} />
        <div style={{ fontSize: "0.78rem", color: "#d8c4a0", lineHeight: 1.55 }}>
          <strong style={{ color: "#ffa502" }}>
            Academic Integrity &amp; Model Methodology Disclaimer:{" "}
          </strong>
          This module uses an explainable rule-based risk scoring algorithm (calibrated for
          Nagpur locations) as a baseline model because full historical ML training sets are
          unavailable. Risk scores represent relative probability based on rainfall intensity
          and drainage parameters — they are decision-support estimates and do not guarantee
          flooding.
        </div>
      </div>

      {/* 2-Column Section: Chart on Left | Model Parameters on Right (Image 3) */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1.6fr 1fr",
          gap: 18,
        }}
      >
        {/* Left Card: Chart */}
        <div className="glass-card" style={{ padding: "20px 22px" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              marginBottom: 16,
            }}
          >
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <TrendingUp size={16} color="#00d4ff" />
                <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#fff" }}>
                  Nagpur Rainfall vs. Average Risk Score Trend
                </h3>
              </div>
              <p style={{ fontSize: "0.72rem", color: "#8b95a8", marginTop: 2 }}>
                Hourly progression &amp; 1-hour forecast
              </p>
            </div>
            <span
              style={{
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 6,
                padding: "3px 8px",
                fontSize: "10px",
                color: "#8b95a8",
                fontFamily: "monospace",
              }}
            >
              Model: rule-based-v1
            </span>
          </div>

          {/* SVG Trend Wave Chart matching Image 3 */}
          <div style={{ position: "relative", width: "100%", height: 200, marginTop: 10 }}>
            <svg
              viewBox="0 0 600 200"
              style={{ width: "100%", height: "100%", overflow: "visible" }}
            >
              <defs>
                {/* Red Risk Gradient */}
                <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ff4757" stopOpacity="0.45" />
                  <stop offset="100%" stopColor="#ff4757" stopOpacity="0.0" />
                </linearGradient>
                {/* Cyan Rain Gradient */}
                <linearGradient id="rainGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00d4ff" stopOpacity="0.4" />
                  <stop offset="100%" stopColor="#00d4ff" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Horizontal grid lines */}
              <line x1="40" y1="20" x2="580" y2="20" stroke="rgba(255,255,255,0.06)" strokeDasharray="3,3" />
              <line x1="40" y1="65" x2="580" y2="65" stroke="rgba(255,255,255,0.06)" strokeDasharray="3,3" />
              <line x1="40" y1="110" x2="580" y2="110" stroke="rgba(255,255,255,0.06)" strokeDasharray="3,3" />
              <line x1="40" y1="155" x2="580" y2="155" stroke="rgba(255,255,255,0.06)" strokeDasharray="3,3" />

              {/* Y Axis Labels */}
              <text x="25" y="24" fill="#5a6478" fontSize="10" textAnchor="end">100</text>
              <text x="25" y="69" fill="#5a6478" fontSize="10" textAnchor="end">75</text>
              <text x="25" y="114" fill="#5a6478" fontSize="10" textAnchor="end">50</text>
              <text x="25" y="159" fill="#5a6478" fontSize="10" textAnchor="end">25</text>

              {/* Average Risk Wave (Red/Pink Area) */}
              <path
                d="M 40 160 Q 120 150, 180 135 T 300 80 T 420 85 T 500 70 T 580 60 L 580 170 L 40 170 Z"
                fill="url(#riskGrad)"
              />
              <path
                d="M 40 160 Q 120 150, 180 135 T 300 80 T 420 85 T 500 70 T 580 60"
                fill="none"
                stroke="#ff4757"
                strokeWidth="2.5"
              />

              {/* Rainfall Intensity Wave (Cyan Area) */}
              <path
                d="M 40 170 Q 120 165, 180 150 T 300 110 T 420 130 T 500 160 T 580 120 L 580 170 L 40 170 Z"
                fill="url(#rainGrad)"
              />
              <path
                d="M 40 170 Q 120 165, 180 150 T 300 110 T 420 130 T 500 160 T 580 120"
                fill="none"
                stroke="#00d4ff"
                strokeWidth="2"
              />

              {/* X Axis Ticks and Labels matching Image 3 */}
              <text x="40" y="188" fill="#5a6478" fontSize="9" textAnchor="middle">08:00</text>
              <text x="130" y="188" fill="#5a6478" fontSize="9" textAnchor="middle">09:00</text>
              <text x="220" y="188" fill="#5a6478" fontSize="9" textAnchor="middle">10:00</text>
              <text x="310" y="188" fill="#5a6478" fontSize="9" textAnchor="middle">11:00</text>
              <text x="400" y="188" fill="#5a6478" fontSize="9" textAnchor="middle">12:00</text>
              <text x="490" y="188" fill="#00d4ff" fontSize="9" textAnchor="middle" fontWeight="bold">13:00 (Now)</text>
              <text x="570" y="188" fill="#ff6b35" fontSize="9" textAnchor="middle" fontWeight="bold">14:00 (Pred)</text>
            </svg>
          </div>
        </div>

        {/* Right Card: Model Parameters matching Image 3 */}
        <div className="glass-card" style={{ padding: "20px 22px", display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 18 }}>
            <Sliders size={16} color="#00d4ff" />
            <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#fff" }}>
              Model Parameters
            </h3>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 12, flex: 1 }}>
            {/* Current Rainfall Intensity */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "10px 14px",
                background: "rgba(255,255,255,0.02)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 8,
              }}
            >
              <span style={{ fontSize: "11px", color: "#8b95a8" }}>Current Rainfall Intensity</span>
              <span style={{ fontSize: "12px", fontWeight: 700, color: "#00d4ff" }}>LIGHT</span>
            </div>

            {/* Accumulated 3h Rain */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "10px 14px",
                background: "rgba(255,255,255,0.02)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 8,
              }}
            >
              <span style={{ fontSize: "11px", color: "#8b95a8" }}>Accumulated 3h Rain</span>
              <span style={{ fontSize: "12px", fontWeight: 700, color: "#fff" }}>5.6 mm</span>
            </div>

            {/* Primary Feature Weights */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "10px 14px",
                background: "rgba(255,255,255,0.02)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 8,
              }}
            >
              <span style={{ fontSize: "11px", color: "#8b95a8" }}>Primary Feature Weights</span>
              <span style={{ fontSize: "11px", fontWeight: 600, color: "#c0c9d8" }}>
                Rainfall (35%), Freq (25%)
              </span>
            </div>

            {/* Data Source Provenance */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "10px 14px",
                background: "rgba(255,255,255,0.02)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 8,
              }}
            >
              <span style={{ fontSize: "11px", color: "#8b95a8" }}>Data Source Provenance</span>
              <span style={{ fontSize: "11px", fontWeight: 700, color: "#ffa502" }}>
                SIMULATED / DEMO
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Section: Location Risk Forecasts & Contributing Factors matching Image 3 */}
      <div>
        <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "#fff", marginBottom: 14 }}>
          Location Risk Forecasts &amp; Contributing Factors
        </h3>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 14 }}>
          {locationForecasts.map((loc) => (
            <div
              key={loc.name}
              className="glass-card"
              style={{
                padding: "16px 18px",
                borderTop: `3px solid ${loc.riskColor}`,
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                <h4 style={{ fontSize: "13px", fontWeight: 700, color: "#fff" }}>{loc.name}</h4>
                <span
                  style={{
                    fontSize: "10px",
                    fontWeight: 700,
                    color: loc.riskColor,
                    background: `${loc.riskColor}18`,
                    border: `1px solid ${loc.riskColor}44`,
                    padding: "2px 8px",
                    borderRadius: 4,
                  }}
                >
                  {loc.riskCategory} ({loc.riskScore}%)
                </span>
              </div>

              <div style={{ fontSize: "11px", color: "#8b95a8", lineHeight: 1.5, marginBottom: 8 }}>
                <div><strong>Drainage:</strong> {loc.drainageCapacity}</div>
                <div><strong>Impact:</strong> {loc.rainfallImpact}</div>
              </div>

              <div
                style={{
                  fontSize: "10px",
                  color: "#00d4ff",
                  background: "rgba(0, 212, 255, 0.05)",
                  padding: "6px 8px",
                  borderRadius: 6,
                  border: "1px solid rgba(0, 212, 255, 0.15)",
                }}
              >
                {loc.advice}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
