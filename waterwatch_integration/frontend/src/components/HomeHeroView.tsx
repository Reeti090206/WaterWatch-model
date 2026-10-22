"use client";

import React from "react";
import { BookOpen, Navigation, AlertTriangle, Droplet } from "lucide-react";

interface HomeHeroViewProps {
  onNavigate: (tab: string) => void;
}

export default function HomeHeroView({ onNavigate }: HomeHeroViewProps) {
  return (
    <div className="hero-section">
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
        </div>
      </div>
    </div>
  );
}
