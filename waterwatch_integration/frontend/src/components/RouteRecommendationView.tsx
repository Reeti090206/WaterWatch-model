"use client";

import React, { useState } from "react";
import {
  Navigation,
  MapPin,
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  Car,
  CheckCircle2,
  Info,
} from "lucide-react";
import LeafletMapComponent from "./LeafletMapComponent";
import { RouteSegment } from "../types";

interface RouteProps {
  onSelectRouteForMap?: (route: RouteSegment) => void;
  activeRoute?: RouteSegment | null;
}

const NAGPUR_QUICK_DESTINATIONS = [
  "Katol Road Square",
  "Sitabuldi Metro Station",
  "Pardi Naka Underpass",
  "Ambazari Lake Road",
  "Wardha Road (Airport)",
  "Sadar Flyover",
  "Pratap Nagar Square",
  "Hingna T-Point",
];

export default function RouteRecommendationView({
  onSelectRouteForMap,
  activeRoute,
}: RouteProps) {
  const [origin, setOrigin] = useState("Katol Road, Nagpur");
  const [destination, setDestination] = useState("Pardi Naka, Nagpur");
  const [selectedRouteIdx, setSelectedRouteIdx] = useState(0);

  // Nagpur coordinates for the 2 routes shown in the screenshots
  const routesData = [
    {
      id: 0,
      title: "Direct Route (Via Main Arterial Underpass)",
      subtitle: "Heavy / Water Accumulation",
      badge: "RECOMMENDED",
      badgeClass: "badge-normal",
      distance_km: 3.8,
      duration_minutes: 12,
      risk_score: 20,
      submerged_segments: [
        { name: "Pardi Naka Underpass", status: "Severe / Road Unsafe" },
      ],
      is_recommended: true,
      google_maps_url: `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(
        origin
      )}&destination=${encodeURIComponent(destination)}&travelmode=driving`,
      coordinates: [
        [21.1645, 79.062],
        [21.155, 79.08],
        [21.1442, 79.1415],
      ] as [number, number][],
    },
    {
      id: 1,
      title: "Safest Recommended Route (Elevated Bypass)",
      subtitle: "Moderate / Normal Flow",
      badge: "MEDIUM RISK",
      badgeClass: "badge-moderate",
      distance_km: 4.3,
      duration_minutes: 12,
      risk_score: 20,
      avoided_hazards: "Bypasses Pardi Naka Underpass",
      submerged_segments: [
        { name: "Pardi Naka Underpass", status: "Severe / Road Unsafe" },
      ],
      is_recommended: false,
      google_maps_url: `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(
        origin
      )}&destination=${encodeURIComponent(destination)}&travelmode=driving`,
      coordinates: [
        [21.1645, 79.062],
        [21.17, 79.09],
        [21.16, 79.12],
        [21.1442, 79.1415],
      ] as [number, number][],
    },
  ];

  const handleSelectRoute = (idx: number) => {
    setSelectedRouteIdx(idx);
    const r = routesData[idx];
    if (onSelectRouteForMap) {
      onSelectRouteForMap({
        preference_type: idx === 0 ? "fastest" : "lowest_risk",
        distance_km: r.distance_km,
        duration_minutes: r.duration_minutes,
        estimated_risk_level: idx === 0 ? "LOW_ESTIMATED_RISK" : "MODERATE_ESTIMATED_RISK",
        risk_score: r.risk_score,
        hazard_factors: ["Waterlogged underpass"],
        coordinates: r.coordinates,
        is_recommended: r.is_recommended,
        recommendation_rationale: r.subtitle,
      });
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* Page Header matching Image 1 */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <Navigation size={22} color="#00d4ff" />
            <h1 style={{ fontSize: "1.45rem", fontWeight: 800, color: "#fff" }}>
              Google Maps–Style Safe Navigation
            </h1>
          </div>
          <p style={{ fontSize: "0.8rem", color: "#8b95a8", marginTop: 4 }}>
            Real-time waterlogging risk evaluation overlaid on Google Maps navigation for Nagpur city
          </p>
        </div>

        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            background: "rgba(0, 212, 255, 0.08)",
            border: "1px solid rgba(0, 212, 255, 0.3)",
            borderRadius: 999,
            padding: "6px 14px",
            fontSize: "11px",
            color: "#00d4ff",
            fontWeight: 600,
          }}
        >
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#00d4ff" }} />
          <span>Live Sensor + Flood Avoidance Engine</span>
        </div>
      </div>

      {/* Blue Informational Banner matching Image 1 */}
      <div
        style={{
          background: "rgba(0, 212, 255, 0.04)",
          border: "1px solid rgba(0, 212, 255, 0.2)",
          borderRadius: 10,
          padding: "12px 16px",
          display: "flex",
          alignItems: "flex-start",
          gap: 12,
        }}
      >
        <Info size={18} color="#00d4ff" style={{ flexShrink: 0, marginTop: 2 }} />
        <div style={{ fontSize: "0.78rem", color: "#c0c9d8", lineHeight: 1.5 }}>
          <strong style={{ color: "#fff" }}>Google Maps Navigation Integration: </strong>
          Standard Google Maps does not report live water depth or submerged underpass risks.
          Nagpur WaterWatch combines IoT sensor telemetry and AI predictions with spatial
          routing, calculating the safest path around flooded areas and launching turn-by-turn
          navigation directly in Google Maps.
        </div>
      </div>

      {/* Split Grid: Left Form & Cards | Right Safe Banner & Map */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "480px 1fr",
          gap: 20,
          alignItems: "start",
        }}
      >
        {/* Left Column */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Trip Origin & Destination Card */}
          <div className="glass-card" style={{ padding: "18px 20px" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 14,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#00d4ff" }} />
                <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#fff" }}>
                  Trip Origin &amp; Destination
                </h3>
              </div>
              <button
                onClick={() => setOrigin("Katol Road, Nagpur")}
                style={{
                  background: "rgba(0, 212, 255, 0.12)",
                  border: "1px solid rgba(0, 212, 255, 0.3)",
                  borderRadius: 6,
                  color: "#00d4ff",
                  fontSize: "11px",
                  padding: "4px 10px",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: 4,
                }}
              >
                <MapPin size={12} /> Your Location
              </button>
            </div>

            {/* Starting Location */}
            <div style={{ marginBottom: 12 }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  fontSize: "11px",
                  color: "#8b95a8",
                  marginBottom: 6,
                }}
              >
                <span>Starting Location (Origin)</span>
                <span style={{ color: "#ff4757", cursor: "pointer", display: "flex", alignItems: "center", gap: 2 }}>
                  📍 Pick on Map
                </span>
              </div>
              <input
                type="text"
                className="input-field"
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
              />
            </div>

            {/* Destination */}
            <div style={{ marginBottom: 16 }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  fontSize: "11px",
                  color: "#8b95a8",
                  marginBottom: 6,
                }}
              >
                <span>Destination</span>
                <span style={{ color: "#ff4757", cursor: "pointer", display: "flex", alignItems: "center", gap: 2 }}>
                  📍 Pick on Map
                </span>
              </div>
              <input
                type="text"
                className="input-field"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
              />
            </div>

            {/* Calculate Button */}
            <button
              className="btn-primary"
              style={{ width: "100%", justifyContent: "center", marginBottom: 16 }}
              onClick={() => handleSelectRoute(0)}
            >
              <Navigation size={15} />
              <span>Calculate Safe Navigation Route</span>
            </button>

            {/* Quick Select Nagpur Destination */}
            <div>
              <div style={{ fontSize: "10px", fontWeight: 700, color: "#8b95a8", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8 }}>
                Quick Select Nagpur Destination:
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {NAGPUR_QUICK_DESTINATIONS.map((dest) => (
                  <button
                    key={dest}
                    onClick={() => {
                      setDestination(dest);
                      handleSelectRoute(0);
                    }}
                    style={{
                      background: "rgba(255, 255, 255, 0.04)",
                      border: "1px solid rgba(255, 255, 255, 0.08)",
                      borderRadius: 6,
                      padding: "5px 10px",
                      fontSize: "11px",
                      color: destination.includes(dest.split(" ")[0]) ? "#00d4ff" : "#8b95a8",
                      cursor: "pointer",
                      transition: "all 0.15s",
                    }}
                  >
                    {dest}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Available Route Options Section */}
          <div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 10,
              }}
            >
              <span style={{ fontSize: "12px", color: "#8b95a8" }}>Available Route Options (2):</span>
              <span style={{ fontSize: "11px", color: "#00d4ff", cursor: "pointer" }}>
                Click card to highlight on map
              </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {/* Route Card 1 (Direct Route) matching Image 1 */}
              <div
                onClick={() => handleSelectRoute(0)}
                className="glass-card"
                style={{
                  padding: "16px",
                  cursor: "pointer",
                  border:
                    selectedRouteIdx === 0
                      ? "1px solid #00d4ff"
                      : "1px solid rgba(255,255,255,0.08)",
                  boxShadow:
                    selectedRouteIdx === 0 ? "0 0 16px rgba(0, 212, 255, 0.2)" : "none",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
                  <div>
                    <h4 style={{ fontSize: "13px", fontWeight: 700, color: "#fff" }}>
                      Direct Route (Via Main Arterial Underpass)
                    </h4>
                    <div style={{ fontSize: "11px", color: "#8b95a8", display: "flex", alignItems: "center", gap: 5, marginTop: 2 }}>
                      <Car size={13} color="#00d4ff" /> Heavy / Water Accumulation
                    </div>
                  </div>
                  <span
                    style={{
                      background: "rgba(46, 213, 115, 0.15)",
                      color: "#2ed573",
                      border: "1px solid rgba(46, 213, 115, 0.35)",
                      fontSize: "10px",
                      fontWeight: 700,
                      padding: "3px 8px",
                      borderRadius: 4,
                    }}
                  >
                    RECOMMENDED
                  </span>
                </div>

                {/* 3 Metrics: Distance, Est. Time, Risk Score */}
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr 1fr",
                    gap: 8,
                    margin: "12px 0",
                    background: "rgba(0,0,0,0.2)",
                    borderRadius: 8,
                    padding: "8px 10px",
                    textAlign: "center",
                  }}
                >
                  <div>
                    <div style={{ fontSize: "10px", color: "#8b95a8" }}>Distance</div>
                    <div style={{ fontSize: "13px", fontWeight: 700, color: "#fff" }}>3.8 km</div>
                  </div>
                  <div>
                    <div style={{ fontSize: "10px", color: "#8b95a8" }}>Est. Time</div>
                    <div style={{ fontSize: "13px", fontWeight: 700, color: "#fff" }}>12 min</div>
                  </div>
                  <div>
                    <div style={{ fontSize: "10px", color: "#8b95a8" }}>Risk Score</div>
                    <div style={{ fontSize: "13px", fontWeight: 700, color: "#2ed573" }}>20%</div>
                  </div>
                </div>

                {/* Submerged Segments */}
                <div style={{ marginBottom: 12 }}>
                  <div style={{ fontSize: "10px", color: "#8b95a8", textTransform: "uppercase", marginBottom: 4 }}>
                    Submerged Segments (1):
                  </div>
                  <div
                    style={{
                      background: "rgba(255, 71, 87, 0.08)",
                      border: "1px solid rgba(255, 71, 87, 0.25)",
                      borderRadius: 6,
                      padding: "6px 10px",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <span style={{ fontSize: "11px", color: "#fff" }}>Pardi Naka Underpass</span>
                    <span style={{ fontSize: "10px", color: "#ff4757", fontWeight: 700 }}>
                      Severe / Road Unsafe
                    </span>
                  </div>
                </div>

                {/* Start Navigation in Google Maps Button */}
                <a
                  href={`https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(
                    origin
                  )}&destination=${encodeURIComponent(destination)}&travelmode=driving`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-primary"
                  style={{
                    width: "100%",
                    justifyContent: "center",
                    fontSize: "12px",
                    padding: "8px 14px",
                  }}
                >
                  <ExternalLink size={14} />
                  <span>Start Navigation in Google Maps</span>
                </a>
              </div>

              {/* Route Card 2 (Safest Recommended Route) matching Image 2 */}
              <div
                onClick={() => handleSelectRoute(1)}
                className="glass-card"
                style={{
                  padding: "16px",
                  cursor: "pointer",
                  border:
                    selectedRouteIdx === 1
                      ? "1px solid #00d4ff"
                      : "1px solid rgba(255,255,255,0.08)",
                  boxShadow:
                    selectedRouteIdx === 1 ? "0 0 16px rgba(0, 212, 255, 0.2)" : "none",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
                  <div>
                    <h4 style={{ fontSize: "13px", fontWeight: 700, color: "#fff" }}>
                      Safest Recommended Route (Elevated Bypass)
                    </h4>
                    <div style={{ fontSize: "11px", color: "#8b95a8", display: "flex", alignItems: "center", gap: 5, marginTop: 2 }}>
                      <Car size={13} color="#00d4ff" /> Moderate / Normal Flow
                    </div>
                  </div>
                  <span
                    style={{
                      background: "rgba(255, 71, 87, 0.15)",
                      color: "#ff4757",
                      border: "1px solid rgba(255, 71, 87, 0.35)",
                      fontSize: "10px",
                      fontWeight: 700,
                      padding: "3px 8px",
                      borderRadius: 4,
                    }}
                  >
                    MEDIUM RISK
                  </span>
                </div>

                {/* 3 Metrics: Distance, Est. Time, Risk Score */}
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr 1fr",
                    gap: 8,
                    margin: "12px 0",
                    background: "rgba(0,0,0,0.2)",
                    borderRadius: 8,
                    padding: "8px 10px",
                    textAlign: "center",
                  }}
                >
                  <div>
                    <div style={{ fontSize: "10px", color: "#8b95a8" }}>Distance</div>
                    <div style={{ fontSize: "13px", fontWeight: 700, color: "#fff" }}>4.3 km</div>
                  </div>
                  <div>
                    <div style={{ fontSize: "10px", color: "#8b95a8" }}>Est. Time</div>
                    <div style={{ fontSize: "13px", fontWeight: 700, color: "#fff" }}>12 min</div>
                  </div>
                  <div>
                    <div style={{ fontSize: "10px", color: "#8b95a8" }}>Risk Score</div>
                    <div style={{ fontSize: "13px", fontWeight: 700, color: "#2ed573" }}>20%</div>
                  </div>
                </div>

                {/* Avoided Hazards Tag matching Image 2 */}
                <div
                  style={{
                    background: "rgba(46, 213, 115, 0.08)",
                    border: "1px solid rgba(46, 213, 115, 0.25)",
                    borderRadius: 6,
                    padding: "6px 10px",
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                    fontSize: "11px",
                    color: "#2ed573",
                    marginBottom: 10,
                  }}
                >
                  <ShieldCheck size={14} />
                  <span>Avoided Hazards: Bypasses Pardi Naka Underpass</span>
                </div>

                {/* Submerged Segments */}
                <div>
                  <div style={{ fontSize: "10px", color: "#8b95a8", textTransform: "uppercase", marginBottom: 4 }}>
                    Submerged Segments (1):
                  </div>
                  <div
                    style={{
                      background: "rgba(255, 71, 87, 0.08)",
                      border: "1px solid rgba(255, 71, 87, 0.25)",
                      borderRadius: 6,
                      padding: "6px 10px",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <span style={{ fontSize: "11px", color: "#fff" }}>Pardi Naka Underpass</span>
                    <span style={{ fontSize: "10px", color: "#ff4757", fontWeight: 700 }}>
                      Severe / Road Unsafe
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Safe Route Recommendation Banner + Leaflet Map matching Image 1 & 2 */}
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {/* Green Top Recommendation Banner matching Image 1 */}
          <div
            style={{
              background: "rgba(46, 213, 115, 0.08)",
              border: "1px solid rgba(46, 213, 115, 0.3)",
              borderRadius: 10,
              padding: "12px 18px",
              display: "flex",
              alignItems: "center",
              gap: 12,
            }}
          >
            <CheckCircle2 size={20} color="#2ed573" style={{ flexShrink: 0 }} />
            <div>
              <div style={{ fontSize: "13px", fontWeight: 700, color: "#2ed573" }}>
                Safe Route Recommendation
              </div>
              <div style={{ fontSize: "11px", color: "#c0c9d8" }}>
                Route 1 is recommended as it has equal or lower waterlogging risk.
              </div>
            </div>
          </div>

          {/* Interactive Map with Routes A to B */}
          <div className="glass-card" style={{ padding: 10, overflow: "hidden" }}>
            <LeafletMapComponent
              mode="embedded"
              activeRoute={{
                preference_type: selectedRouteIdx === 0 ? "fastest" : "lowest_risk",
                distance_km: routesData[selectedRouteIdx].distance_km,
                duration_minutes: routesData[selectedRouteIdx].duration_minutes,
                estimated_risk_level: "LOW_ESTIMATED_RISK",
                risk_score: routesData[selectedRouteIdx].risk_score,
                hazard_factors: ["Pardi Naka Underpass waterlogging"],
                coordinates: routesData[selectedRouteIdx].coordinates,
                is_recommended: routesData[selectedRouteIdx].is_recommended,
                recommendation_rationale: routesData[selectedRouteIdx].subtitle,
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
