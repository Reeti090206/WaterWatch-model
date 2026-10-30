"use client";

import React from "react";
import {
  BookOpen,
  Navigation,
  AlertTriangle,
  Droplet,
  Zap,
  Activity,
  Map,
  ShieldCheck,
  ChevronRight,
  ArrowDown,
  CheckCircle2,
  Clock,
  Layers,
  Sparkles
} from "lucide-react";

interface HomeHeroViewProps {
  onNavigate: (tab: string) => void;
}

export default function HomeHeroView({ onNavigate }: HomeHeroViewProps) {
  const scrollToOverview = () => {
    document.getElementById("home-overview-section")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="home-container" style={{ width: "100%", display: "flex", flexDirection: "column" }}>
      {/* 1. TOP HERO SECTION WITH BACKGROUND IMAGE */}
      <div className="hero-section" style={{ position: "relative", minHeight: "92vh", display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden" }}>
        {/* Background artwork with rainy dark city, weather telemetry, and risk legend */}
        <div className="hero-bg" />

        {/* Centered Glassmorphic Modal Card */}
        <div className="hero-content">
          <div className="hero-glass">
            <div className="hero-badge">
              <Droplet size={13} fill="currentColor" />
              <span>REAL-TIME WATERLOGGING MONITORING &amp; SMART NAVIGATION</span>
            </div>

            <h1 className="hero-title">Nagpur WaterWatch</h1>

            <div className="hero-tagline">Predict. Detect. Navigate.</div>

            <p className="hero-desc">
              A real-time IoT and predictive waterlogging monitoring system combined
              with intelligent route recommendation to ensure safer citizen travel
              across vulnerable roads in Nagpur.
            </p>

            <div className="hero-actions">
              <button
                className="btn-primary"
                onClick={() => onNavigate("livedemo")}
                style={{
                  background: "linear-gradient(135deg, #0ea5e9, #10b981)",
                  borderColor: "#38bdf8",
                  boxShadow: "0 0 24px rgba(14, 165, 233, 0.45)",
                  fontWeight: 600,
                }}
              >
                <Zap size={17} />
                <span>⚡ Live AI Demo</span>
              </button>

              <button
                className="btn-primary"
                onClick={() => onNavigate("dashboard")}
                style={{
                  boxShadow: "0 0 20px rgba(0, 180, 216, 0.4)",
                }}
              >
                <BookOpen size={17} />
                <span>Live Dashboard &amp; Map</span>
              </button>

              <button
                className="btn-dark"
                onClick={() => onNavigate("routing")}
                style={{
                  background: "#162035",
                  borderColor: "rgba(255, 255, 255, 0.12)",
                }}
              >
                <Navigation size={17} />
                <span>Safe Route Planner</span>
              </button>

              <button
                className="btn-amber"
                onClick={() => onNavigate("report")}
                style={{
                  background: "rgba(245, 166, 35, 0.12)",
                  borderColor: "rgba(245, 166, 35, 0.35)",
                }}
              >
                <AlertTriangle size={17} />
                <span>Report Waterlogging</span>
              </button>
            </div>

            {/* Scroll Down Hint Button */}
            <div style={{ marginTop: 24 }}>
              <button
                onClick={scrollToOverview}
                style={{
                  background: "transparent",
                  border: "none",
                  color: "var(--accent-cyan)",
                  fontSize: "0.8rem",
                  cursor: "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "4px 8px",
                  borderRadius: 6,
                  transition: "all 0.2s ease"
                }}
              >
                <span>Scroll down for operational modules &amp; telemetry</span>
                <ArrowDown size={14} className="bounce-animate" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 2. SCROLLABLE OVERVIEW & CORE SYSTEM MODULES */}
      <div id="home-overview-section" style={{ padding: "40px 32px 60px 32px", display: "flex", flexDirection: "column", gap: 36, background: "var(--bg-dark)" }}>
        
        {/* KPI Strip */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))", gap: 16 }}>
          <div className="glass-card" style={{ padding: "18px 20px", borderLeft: "3px solid #00d4ff" }}>
            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Urban IoT Telemetry</span>
            <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "#fff", marginTop: 4 }}>
              8 Active Sensors
            </div>
            <span style={{ fontSize: "0.72rem", color: "#2ed573" }}>● 24/7 Live Monitoring</span>
          </div>

          <div className="glass-card" style={{ padding: "18px 20px", borderLeft: "3px solid #10b981" }}>
            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>MobileNetV3 Accuracy</span>
            <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "#10b981", marginTop: 4 }}>
              100.0%
            </div>
            <span style={{ fontSize: "0.72rem", color: "var(--text-dim)" }}>Held-Out Test Set (N=79)</span>
          </div>

          <div className="glass-card" style={{ padding: "18px 20px", borderLeft: "3px solid #2ed573" }}>
            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Dry Road False Alarms</span>
            <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "#2ed573", marginTop: 4 }}>
              0 / 48
            </div>
            <span style={{ fontSize: "0.72rem", color: "var(--text-dim)" }}>IndiaScene365 Negative Controls</span>
          </div>

          <div className="glass-card" style={{ padding: "18px 20px", borderLeft: "3px solid #ffa502" }}>
            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Monitored Underpasses</span>
            <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "#ffa502", marginTop: 4 }}>
              10 Critical Hotspots
            </div>
            <span style={{ fontSize: "0.72rem", color: "var(--text-dim)" }}>Nagpur Municipal Corporation</span>
          </div>
        </div>

        {/* Core Modules Grid */}
        <div>
          <div style={{ marginBottom: 16 }}>
            <h2 style={{ fontSize: "1.25rem", fontWeight: 800, color: "#fff", display: "flex", alignItems: "center", gap: 8 }}>
              <Layers size={20} color="#00d4ff" /> Core System Modules &amp; Live Capabilities
            </h2>
            <p style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
              Access direct operational controls, live inference tools, and real-time navigation pipelines:
            </p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
            {/* Card 1: Live AI Demo */}
            <div
              className="glass-card"
              style={{ padding: 22, cursor: "pointer", transition: "all 0.25s ease" }}
              onClick={() => onNavigate("livedemo")}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: "rgba(0, 212, 255, 0.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <Zap size={22} color="#00d4ff" />
                </div>
                <span className="badge badge-normal" style={{ fontSize: "0.7rem" }}>FEATURED</span>
              </div>
              <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#fff", marginBottom: 6 }}>
                ⚡ Live AI Evaluator Demo
              </h3>
              <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", lineHeight: 1.5, marginBottom: 14 }}>
                Run live optical waterlogging detection on sample or custom images (MobileNetV3 + YOLOv11), rainfall simulations, and route recommendations with measured telemetry.
              </p>
              <div style={{ display: "flex", alignItems: "center", gap: 4, color: "#00d4ff", fontSize: "0.82rem", fontWeight: 600 }}>
                <span>Launch Interactive Demo</span>
                <ChevronRight size={15} />
              </div>
            </div>

            {/* Card 2: Live Monitoring Dashboard */}
            <div
              className="glass-card"
              style={{ padding: 22, cursor: "pointer", transition: "all 0.25s ease" }}
              onClick={() => onNavigate("dashboard")}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: "rgba(16, 185, 129, 0.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <Activity size={22} color="#10b981" />
                </div>
                <span className="badge badge-simulated" style={{ fontSize: "0.7rem" }}>TELEMETRY</span>
              </div>
              <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#fff", marginBottom: 6 }}>
                📈 Live Monitoring Dashboard
              </h3>
              <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", lineHeight: 1.5, marginBottom: 14 }}>
                Real-time IoT sensor telemetry, active hazard advisories, weather feeds, and municipal incident verification queues across Nagpur.
              </p>
              <div style={{ display: "flex", alignItems: "center", gap: 4, color: "#10b981", fontSize: "0.82rem", fontWeight: 600 }}>
                <span>Open Live Dashboard</span>
                <ChevronRight size={15} />
              </div>
            </div>

            {/* Card 3: Safe Route Planner */}
            <div
              className="glass-card"
              style={{ padding: 22, cursor: "pointer", transition: "all 0.25s ease" }}
              onClick={() => onNavigate("routing")}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: "rgba(56, 189, 248, 0.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <Navigation size={22} color="#38bdf8" />
                </div>
                <span className="badge badge-low" style={{ fontSize: "0.7rem" }}>NAVIGATION</span>
              </div>
              <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#fff", marginBottom: 6 }}>
                🧭 Safe Route Planner
              </h3>
              <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", lineHeight: 1.5, marginBottom: 14 }}>
                Google Maps-style smart navigation that factors in submerged underpasses, chronic flood hotspots, and active road closures to recommend safe alternative corridors.
              </p>
              <div style={{ display: "flex", alignItems: "center", gap: 4, color: "#38bdf8", fontSize: "0.82rem", fontWeight: 600 }}>
                <span>Calculate Safe Route</span>
                <ChevronRight size={15} />
              </div>
            </div>

            {/* Card 4: Predictive Risk Dashboard */}
            <div
              className="glass-card"
              style={{ padding: 22, cursor: "pointer", transition: "all 0.25s ease" }}
              onClick={() => onNavigate("predictions")}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: "rgba(245, 166, 35, 0.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <AlertTriangle size={22} color="#f5a623" />
                </div>
                <span className="badge badge-amber" style={{ fontSize: "0.7rem" }}>PREDICTIVE</span>
              </div>
              <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#fff", marginBottom: 6 }}>
                ⚠️ Predictive Risk Engine
              </h3>
              <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", lineHeight: 1.5, marginBottom: 14 }}>
                Antecedent rainfall curve analytics, rolling multi-hour storm progression forecasting, and drainage clearance simulation per Nagpur municipal ward.
              </p>
              <div style={{ display: "flex", alignItems: "center", gap: 4, color: "#f5a623", fontSize: "0.82rem", fontWeight: 600 }}>
                <span>Explore Predictions</span>
                <ChevronRight size={15} />
              </div>
            </div>
          </div>
        </div>

        {/* Chronic Hotspots Monitored Section */}
        <div className="glass-card" style={{ padding: 24 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <div>
              <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#fff" }}>
                🌊 Monitored Nagpur Railway Underpasses &amp; Hotspots
              </h3>
              <p style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                Key low-lying depression basins tracked in real-time by municipal sensors:
              </p>
            </div>
            <button className="btn-dark" onClick={() => onNavigate("map")} style={{ padding: "6px 14px", fontSize: "0.8rem" }}>
              <span>View On Map</span>
              <ChevronRight size={14} />
            </button>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 14 }}>
            <div className="glass-panel" style={{ padding: 14, borderLeft: "3px solid #ff4757" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                <strong style={{ color: "#fff", fontSize: "0.88rem" }}>Pardi Naka Underpass</strong>
                <span className="badge badge-severe" style={{ fontSize: "0.65rem" }}>SEVERE RISK</span>
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Depression basin, submersible pumps restricted</div>
            </div>

            <div className="glass-panel" style={{ padding: 14, borderLeft: "3px solid #ff6b35" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                <strong style={{ color: "#fff", fontSize: "0.88rem" }}>Ambazari Lake Road</strong>
                <span className="badge badge-moderate" style={{ fontSize: "0.65rem" }}>MODERATE</span>
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Overflow runoff from lake spillway</div>
            </div>

            <div className="glass-panel" style={{ padding: 14, borderLeft: "3px solid #ff6b35" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                <strong style={{ color: "#fff", fontSize: "0.88rem" }}>Pratap Nagar Square</strong>
                <span className="badge badge-moderate" style={{ fontSize: "0.65rem" }}>MODERATE</span>
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Low grade intersection stormwater ponding</div>
            </div>

            <div className="glass-panel" style={{ padding: 14, borderLeft: "3px solid #2ed573" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                <strong style={{ color: "#fff", fontSize: "0.88rem" }}>Civil Lines VIP Road</strong>
                <span className="badge badge-normal" style={{ fontSize: "0.65rem" }}>NORMAL</span>
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Elevated gradient, rapid stormwater clearance</div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
