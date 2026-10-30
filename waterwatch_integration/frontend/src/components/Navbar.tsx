"use client";

import React from "react";
import { LiveWeather } from "../types";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  weather?: LiveWeather | null;
}

export default function Navbar({ activeTab, setActiveTab, weather }: NavbarProps) {
  const navItems = [
    { id: "overview", label: "Overview & Map" },
    { id: "routing", label: "Safe Routing" },
    { id: "rainfall", label: "Rainfall ML" },
    { id: "detection", label: "Image YOLO" },
    { id: "citizen", label: "Citizen Reports" },
    { id: "hotspots", label: "Hotspots" },
    { id: "models", label: "Model Status" },
  ];

  return (
    <header
      style={{
        background: "rgba(11, 15, 25, 0.95)",
        backdropFilter: "blur(12px)",
        borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
        position: "sticky",
        top: 0,
        zIndex: 50,
        padding: "0 24px",
      }}
    >
      <div
        style={{
          maxWidth: "1440px",
          margin: "0 auto",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          height: "68px",
        }}
      >
        {/* Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", cursor: "pointer" }} onClick={() => setActiveTab("overview")}>
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: "linear-gradient(135deg, #06b6d4, #2563eb)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 0 16px rgba(6, 182, 212, 0.4)",
            }}
          >
            <span style={{ fontSize: "18px" }}>🌊</span>
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontWeight: 800, fontSize: "1.15rem", letterSpacing: "-0.02em", color: "#ffffff" }}>
                WaterWatch <span style={{ color: "#38bdf8" }}>AI</span>
              </span>
              <span
                style={{
                  background: "rgba(56, 189, 248, 0.15)",
                  color: "#38bdf8",
                  border: "1px solid rgba(56, 189, 248, 0.3)",
                  fontSize: "10px",
                  fontWeight: 700,
                  padding: "2px 6px",
                  borderRadius: "4px",
                }}
              >
                NAGPUR
              </span>
            </div>
            <div style={{ fontSize: "11px", color: "#94a3b8" }}>Real-Time Flood Monitoring & Safe Route Engine</div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: "flex", gap: "6px" }}>
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  background: isActive ? "rgba(6, 182, 212, 0.15)" : "transparent",
                  color: isActive ? "#38bdf8" : "#94a3b8",
                  border: isActive ? "1px solid rgba(6, 182, 212, 0.35)" : "1px solid transparent",
                  borderRadius: "8px",
                  padding: "8px 14px",
                  fontSize: "0.85rem",
                  fontWeight: isActive ? 600 : 500,
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                }}
              >
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Live Weather Widget */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            background: "rgba(17, 24, 39, 0.8)",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            padding: "6px 14px",
            borderRadius: "20px",
            fontSize: "12px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ fontSize: "14px" }}>🌧️</span>
            <div>
              <span style={{ fontWeight: 600, color: "#f8fafc" }}>
                {weather?.rainfall_1h_mm ?? 0} mm/h
              </span>
              <span style={{ color: "#64748b", marginLeft: "4px" }}>(1h)</span>
            </div>
          </div>
          <div style={{ width: "1px", height: "18px", background: "rgba(255,255,255,0.1)" }} />
          <div style={{ color: "#94a3b8" }}>
            {weather?.temperature_c ?? 28}°C | {weather?.humidity_percent ?? 80}% RH
          </div>
        </div>
      </div>
    </header>
  );
}
