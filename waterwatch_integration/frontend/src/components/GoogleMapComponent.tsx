"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import { Incident, HistoricalHotspot, RoadClosure, CitizenReport, RouteSegment } from "../types";

interface GoogleMapProps {
  incidents: Incident[];
  hotspots: HistoricalHotspot[];
  closures: RoadClosure[];
  reports: CitizenReport[];
  activeRoute: RouteSegment | null;
  onSelectIncident?: (incident: Incident) => void;
}

const DARK_MAP_STYLE: google.maps.MapTypeStyle[] = [
  { elementType: "geometry", stylers: [{ color: "#111827" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#111827" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#9ca3af" }] },
  {
    featureType: "administrative.locality",
    elementType: "labels.text.fill",
    stylers: [{ color: "#38bdf8" }],
  },
  {
    featureType: "poi",
    elementType: "labels.text.fill",
    stylers: [{ color: "#6b7280" }],
  },
  {
    featureType: "poi.park",
    elementType: "geometry",
    stylers: [{ color: "#162032" }],
  },
  {
    featureType: "road",
    elementType: "geometry",
    stylers: [{ color: "#1f293d" }],
  },
  {
    featureType: "road",
    elementType: "geometry.stroke",
    stylers: [{ color: "#0f172a" }],
  },
  {
    featureType: "road",
    elementType: "labels.text.fill",
    stylers: [{ color: "#94a3b8" }],
  },
  {
    featureType: "road.highway",
    elementType: "geometry",
    stylers: [{ color: "#334155" }],
  },
  {
    featureType: "road.highway",
    elementType: "labels.text.fill",
    stylers: [{ color: "#cbd5e1" }],
  },
  {
    featureType: "transit",
    elementType: "geometry",
    stylers: [{ color: "#1e293b" }],
  },
  {
    featureType: "water",
    elementType: "geometry",
    stylers: [{ color: "#082f49" }],
  },
  {
    featureType: "water",
    elementType: "labels.text.fill",
    stylers: [{ color: "#38bdf8" }],
  },
];

export default function GoogleMapComponent({
  incidents,
  hotspots,
  closures,
  reports,
  activeRoute,
}: GoogleMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<google.maps.Map | null>(null);
  const markersRef = useRef<google.maps.Marker[]>([]);
  const polylineRef = useRef<google.maps.Polyline | null>(null);
  const infoWindowRef = useRef<google.maps.InfoWindow | null>(null);

  const [mapLoaded, setMapLoaded] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [activeLayers, setActiveLayers] = useState({
    incidents: true,
    hotspots: true,
    closures: true,
    reports: true,
  });

  const apiKey =
    process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ||
    "AIzaSyBFzKz2QQEzTO3h5youhcy67kjcpP9dmPM";

  // Load Google Maps Script
  useEffect(() => {
    if (typeof window === "undefined") return;

    if (window.google && window.google.maps) {
      setMapLoaded(true);
      return;
    }

    const scriptId = "google-maps-script";
    const existing = document.getElementById(scriptId);
    if (!existing) {
      const script = document.createElement("script");
      script.id = scriptId;
      script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=geometry`;
      script.async = true;
      script.defer = true;
      script.onload = () => setMapLoaded(true);
      script.onerror = () => {
        setLoadError("Failed to load Google Maps API script. Please check your network connection or API quota.");
      };
      document.head.appendChild(script);
    } else {
      existing.addEventListener("load", () => setMapLoaded(true));
    }
  }, [apiKey]);

  // Initialize Map
  useEffect(() => {
    if (!mapLoaded || !mapRef.current || mapInstanceRef.current) return;

    try {
      const nagpurCenter = { lat: 21.1458, lng: 79.0882 };
      const map = new google.maps.Map(mapRef.current, {
        center: nagpurCenter,
        zoom: 13,
        styles: DARK_MAP_STYLE,
        disableDefaultUI: false,
        zoomControl: true,
        streetViewControl: false,
        mapTypeControl: false,
        fullscreenControl: true,
      });

      infoWindowRef.current = new google.maps.InfoWindow();
      mapInstanceRef.current = map;
    } catch (e) {
      console.error("Map initialization failed", e);
    }
  }, [mapLoaded]);

  // Render Markers
  const renderMarkers = useCallback(() => {
    if (!mapInstanceRef.current || !window.google) return;

    // Clear old markers
    markersRef.current.forEach((m) => m.setMap(null));
    markersRef.current = [];

    const map = mapInstanceRef.current;
    const infoWindow = infoWindowRef.current;

    // 1. Incidents
    if (activeLayers.incidents) {
      incidents.forEach((inc) => {
        const color =
          inc.severity === "Critical"
            ? "#ef4444"
            : inc.severity === "High"
            ? "#f97316"
            : inc.severity === "Moderate"
            ? "#eab308"
            : "#10b981";

        const marker = new google.maps.Marker({
          position: { lat: inc.latitude, lng: inc.longitude },
          map,
          title: inc.title,
          icon: {
            path: google.maps.SymbolPath.CIRCLE,
            fillColor: color,
            fillOpacity: 0.9,
            strokeColor: "#ffffff",
            strokeWeight: 2,
            scale: 9,
          },
        });

        marker.addListener("click", () => {
          if (!infoWindow) return;
          infoWindow.setContent(`
            <div style="color: #111827; font-family: Inter, sans-serif; padding: 6px; max-width: 250px;">
              <h4 style="margin: 0 0 4px 0; font-size: 14px; font-weight: 700; color: #0f172a;">${inc.title}</h4>
              <p style="margin: 0 0 4px 0; font-size: 12px; color: #475569;"><strong>Location:</strong> ${inc.location_name}</p>
              <p style="margin: 0 0 4px 0; font-size: 12px;"><strong>Severity:</strong> <span style="color: ${color}; font-weight: 700;">${inc.severity}</span></p>
              ${inc.water_depth_cm ? `<p style="margin: 0 0 4px 0; font-size: 12px; color: #0284c7;"><strong>Water Depth:</strong> ${inc.water_depth_cm} cm</p>` : ""}
              <p style="margin: 0; font-size: 11px; color: #64748b;">Source: ${inc.source}</p>
            </div>
          `);
          infoWindow.open(map, marker);
        });

        markersRef.current.push(marker);
      });
    }

    // 2. Hotspots
    if (activeLayers.hotspots) {
      hotspots.forEach((h) => {
        const marker = new google.maps.Marker({
          position: { lat: h.latitude, lng: h.longitude },
          map,
          title: `Hotspot: ${h.name}`,
          icon: {
            path: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z",
            fillColor: "#8b5cf6",
            fillOpacity: 0.9,
            strokeColor: "#ffffff",
            strokeWeight: 1.5,
            scale: 1.3,
            anchor: new google.maps.Point(12, 22),
          },
        });

        marker.addListener("click", () => {
          if (!infoWindow) return;
          infoWindow.setContent(`
            <div style="color: #111827; font-family: Inter, sans-serif; padding: 6px; max-width: 250px;">
              <h4 style="margin: 0 0 4px 0; font-size: 14px; font-weight: 700; color: #6d28d9;">⚠️ Chronic Hotspot</h4>
              <p style="margin: 0 0 4px 0; font-size: 13px; font-weight: 600;">${h.name}</p>
              <p style="margin: 0 0 4px 0; font-size: 12px; color: #475569;"><strong>Locality:</strong> ${h.locality}</p>
              <p style="margin: 0 0 4px 0; font-size: 12px; color: #b91c1c;"><strong>Avg Depth:</strong> ${h.average_depth_cm} cm</p>
              <p style="margin: 0; font-size: 11px; color: #64748b;">Cause: ${h.chronic_cause}</p>
            </div>
          `);
          infoWindow.open(map, marker);
        });

        markersRef.current.push(marker);
      });
    }

    // 3. Road Closures
    if (activeLayers.closures) {
      closures.forEach((c) => {
        const marker = new google.maps.Marker({
          position: { lat: c.latitude, lng: c.longitude },
          map,
          title: `Road Closure: ${c.road_name}`,
          icon: {
            path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
            fillColor: "#dc2626",
            fillOpacity: 1,
            strokeColor: "#ffffff",
            strokeWeight: 2,
            scale: 6,
          },
        });

        marker.addListener("click", () => {
          if (!infoWindow) return;
          infoWindow.setContent(`
            <div style="color: #111827; font-family: Inter, sans-serif; padding: 6px; max-width: 250px;">
              <h4 style="margin: 0 0 4px 0; font-size: 14px; font-weight: 700; color: #dc2626;">🚫 Road Closure</h4>
              <p style="margin: 0 0 4px 0; font-size: 13px; font-weight: 600;">${c.road_name}</p>
              <p style="margin: 0 0 4px 0; font-size: 12px; color: #475569;"><strong>Reason:</strong> ${c.reason}</p>
              <p style="margin: 0; font-size: 11px; color: #dc2626; font-weight: 700;">STATUS: ${c.status.toUpperCase()}</p>
            </div>
          `);
          infoWindow.open(map, marker);
        });

        markersRef.current.push(marker);
      });
    }

    // 4. Citizen Reports
    if (activeLayers.reports) {
      reports.forEach((r) => {
        const marker = new google.maps.Marker({
          position: { lat: r.latitude, lng: r.longitude },
          map,
          title: `Citizen Report: ${r.location_name}`,
          icon: {
            path: google.maps.SymbolPath.CIRCLE,
            fillColor: r.verification_status === "VERIFIED" ? "#0284c7" : "#eab308",
            fillOpacity: 0.85,
            strokeColor: "#ffffff",
            strokeWeight: 1.5,
            scale: 6,
          },
        });

        marker.addListener("click", () => {
          if (!infoWindow) return;
          infoWindow.setContent(`
            <div style="color: #111827; font-family: Inter, sans-serif; padding: 6px; max-width: 250px;">
              <h4 style="margin: 0 0 4px 0; font-size: 13px; font-weight: 700; color: #0284c7;">📢 Citizen Report</h4>
              <p style="margin: 0 0 4px 0; font-size: 12px; font-weight: 600;">${r.location_name}</p>
              <p style="margin: 0 0 4px 0; font-size: 11px; color: #475569;">${r.description}</p>
              <p style="margin: 0; font-size: 11px;">Status: <strong>${r.verification_status}</strong></p>
            </div>
          `);
          infoWindow.open(map, marker);
        });

        markersRef.current.push(marker);
      });
    }
  }, [activeLayers, incidents, hotspots, closures, reports]);

  useEffect(() => {
    renderMarkers();
  }, [renderMarkers]);

  // Render Active Route Polyline
  useEffect(() => {
    if (!mapInstanceRef.current || !window.google) return;

    if (polylineRef.current) {
      polylineRef.current.setMap(null);
      polylineRef.current = null;
    }

    if (activeRoute && activeRoute.coordinates && activeRoute.coordinates.length > 0) {
      const map = mapInstanceRef.current;
      const path = activeRoute.coordinates.map((c) => ({ lat: c[0], lng: c[1] }));

      const strokeColor =
        activeRoute.risk_score < 0.35
          ? "#10b981"
          : activeRoute.risk_score < 0.65
          ? "#f59e0b"
          : "#ef4444";

      const polyline = new google.maps.Polyline({
        path,
        geodesic: true,
        strokeColor,
        strokeOpacity: 0.9,
        strokeWeight: 6,
        map,
      });

      polylineRef.current = polyline;

      // Fit map to bounds
      const bounds = new google.maps.LatLngBounds();
      path.forEach((p) => bounds.extend(p));
      map.fitBounds(bounds, { top: 50, right: 50, bottom: 50, left: 50 });
    }
  }, [activeRoute]);

  return (
    <div style={{ position: "relative", width: "100%", height: "100%", minHeight: "520px", borderRadius: "12px", overflow: "hidden" }}>
      {/* Layer Control Bar */}
      <div
        style={{
          position: "absolute",
          top: "14px",
          left: "14px",
          zIndex: 10,
          background: "rgba(17, 24, 39, 0.9)",
          backdropFilter: "blur(8px)",
          border: "1px solid rgba(255, 255, 255, 0.1)",
          borderRadius: "8px",
          padding: "8px 12px",
          display: "flex",
          gap: "12px",
          alignItems: "center",
          fontSize: "12px",
          color: "#e2e8f0",
        }}
      >
        <span style={{ fontWeight: 600, color: "#38bdf8" }}>Map Layers:</span>
        <label style={{ display: "flex", alignItems: "center", gap: "5px", cursor: "pointer" }}>
          <input
            type="checkbox"
            checked={activeLayers.incidents}
            onChange={(e) => setActiveLayers((p) => ({ ...p, incidents: e.target.checked }))}
          />
          <span style={{ color: "#f87171" }}>● Incidents ({incidents.length})</span>
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: "5px", cursor: "pointer" }}>
          <input
            type="checkbox"
            checked={activeLayers.hotspots}
            onChange={(e) => setActiveLayers((p) => ({ ...p, hotspots: e.target.checked }))}
          />
          <span style={{ color: "#c084fc" }}>▲ Hotspots ({hotspots.length})</span>
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: "5px", cursor: "pointer" }}>
          <input
            type="checkbox"
            checked={activeLayers.closures}
            onChange={(e) => setActiveLayers((p) => ({ ...p, closures: e.target.checked }))}
          />
          <span style={{ color: "#ef4444" }}>🚫 Closures ({closures.length})</span>
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: "5px", cursor: "pointer" }}>
          <input
            type="checkbox"
            checked={activeLayers.reports}
            onChange={(e) => setActiveLayers((p) => ({ ...p, reports: e.target.checked }))}
          />
          <span style={{ color: "#facc15" }}>📢 Reports ({reports.length})</span>
        </label>
      </div>

      {loadError && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            background: "#0f172a",
            color: "#f87171",
            padding: "20px",
            textAlign: "center",
            zIndex: 20,
          }}
        >
          <p style={{ fontWeight: 700, fontSize: "16px", marginBottom: "8px" }}>Map Load Notice</p>
          <p style={{ fontSize: "13px", color: "#94a3b8", maxWidth: "480px" }}>{loadError}</p>
        </div>
      )}

      <div ref={mapRef} style={{ width: "100%", height: "100%", minHeight: "520px" }} />
    </div>
  );
}
