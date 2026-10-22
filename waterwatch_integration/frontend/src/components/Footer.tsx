"use client";

import React from "react";
import { Droplet, AlertTriangle } from "lucide-react";

interface FooterProps {
  onNavigate: (tab: string) => void;
}

export default function Footer({ onNavigate }: FooterProps) {
  return (
    <footer className="app-footer">
      <div className="footer-grid">
        {/* Left Column: Brand & Academic Disclaimer */}
        <div className="footer-brand">
          <h3>
            <Droplet size={18} fill="#00d4ff" color="#00d4ff" />
            <span>Nagpur WaterWatch</span>
          </h3>
          <p>
            Real-Time and Predictive Waterlogging Monitoring and Intelligent Route
            Recommendation System for Nagpur.
          </p>
          <div className="footer-disclaimer">
            <AlertTriangle
              size={18}
              color="#ffa502"
              style={{ flexShrink: 0, marginTop: 2 }}
            />
            <div>
              <strong style={{ color: "#ffa502" }}>Academic Disclaimer:</strong> Initial coverage
              focuses on selected vulnerable locations in Nagpur. Simulated sensor data and
              predictions are clearly demarcated for demonstration.
            </div>
          </div>
        </div>

        {/* Center Column: Quick Navigation */}
        <div className="footer-col">
          <h4>Quick Navigation</h4>
          <ul>
            <li onClick={() => onNavigate("dashboard")}>Live Dashboard</li>
            <li onClick={() => onNavigate("map")}>Waterlogging Hotspot Map</li>
            <li onClick={() => onNavigate("routing")}>Safe Route Planner</li>
            <li onClick={() => onNavigate("predictions")}>Waterlogging Risk Predictions</li>
            <li onClick={() => onNavigate("report")}>Submit Citizen Report</li>
          </ul>
        </div>

        {/* Right Column: Project Team */}
        <div className="footer-col">
          <h4>Project Team</h4>
          <ul>
            <li style={{ cursor: "default" }}>Harshita Agrawal (32)</li>
            <li style={{ cursor: "default" }}>Reeti Khandelwal (20)</li>
            <li style={{ cursor: "default" }}>Richa Chandak (37)</li>
            <li style={{ cursor: "default" }}>Ananya Biyani (27)</li>
            <li
              style={{
                marginTop: 10,
                color: "#e8ecf4",
                fontWeight: 600,
                cursor: "default",
              }}
            >
              Guided by: Dr. Avinash Agrawal
            </li>
          </ul>
        </div>
      </div>

      <div className="footer-bottom">
        <div>© 2026–27 Nagpur WaterWatch. All rights reserved.</div>
        <div>Nagpur, MH, India</div>
      </div>
    </footer>
  );
}
