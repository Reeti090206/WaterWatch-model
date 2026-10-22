"use client";

import React, { useEffect, useRef, useState } from "react";
import { Compass, Plus, Minus, Layers, MapPin, X } from "lucide-react";
import { Incident, HistoricalHotspot, CitizenReport, RoadClosure, RouteSegment } from "../types";

export interface LeafletMapProps {
  incidents?: Incident[];
  hotspots?: HistoricalHotspot[];
  closures?: RoadClosure[];
  reports?: CitizenReport[];
  activeRoute?: RouteSegment | null;
  mode?: "embedded" | "fullscreen";
  onSelectHotspot?: (name: string) => void;
}

// Fallback Nagpur sensor hotspots matching the screenshots exactly
const NAGPUR_DEFAULT_HOTSPOTS = [
  {
    name: "Ambazari Lake Road",
    lat: 21.1278,
    lng: 79.0494,
    severity: "MODERATE",
    depth: "9.4 cm",
    drainage: "Low",
    status: "Moderate / Avoid if Possible",
    color: "#ff6b35",
  },
  {
    name: "Pardi Naka Underpass",
    lat: 21.1442,
    lng: 79.1415,
    severity: "SEVERE",
    depth: "12.3 cm",
    drainage: "Low",
    status: "Severe / Road Unsafe",
    color: "#ff4757",
  },
  {
    name: "Pratap Nagar Square",
    lat: 21.1189,
    lng: 79.0628,
    severity: "MODERATE",
    depth: "15.2 cm",
    drainage: "Low",
    status: "Moderate / Avoid if Possible",
    color: "#ff6b35",
  },
  {
    name: "Manewada Road Bridge",
    lat: 21.1075,
    lng: 79.0963,
    severity: "MODERATE",
    depth: "25.5 cm",
    drainage: "Low",
    status: "Moderate / Avoid if Possible",
    color: "#ff6b35",
  },
  {
    name: "Dharampeth Main Road",
    lat: 21.1458,
    lng: 79.0664,
    severity: "LOW",
    depth: "4.8 cm",
    drainage: "Moderate",
    status: "Low / Minor water build-up",
    color: "#ffa502",
  },
  {
    name: "Sitabuldi Interchange",
    lat: 21.1466,
    lng: 79.0882,
    severity: "LOW",
    depth: "3.2 cm",
    drainage: "Moderate",
    status: "Low / Minor water build-up",
    color: "#ffa502",
  },
  {
    name: "Narendra Nagar Flyover",
    lat: 21.1092,
    lng: 79.0815,
    severity: "LOW",
    depth: "5.1 cm",
    drainage: "Moderate",
    status: "Low / Minor water build-up",
    color: "#ffa502",
  },
  {
    name: "Civil Lines VIP Road",
    lat: 21.1595,
    lng: 79.0768,
    severity: "NORMAL",
    depth: "0.5 cm",
    drainage: "High",
    status: "Normal / Road Clear",
    color: "#2ed573",
  },
];

export default function LeafletMapComponent({
  incidents = [],
  hotspots = [],
  closures = [],
  reports = [],
  activeRoute = null,
  mode = "embedded",
  onSelectHotspot,
}: LeafletMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const layerGroupRef = useRef<any>(null);
  const routeLayerRef = useRef<any>(null);

  const [mapType, setMapType] = useState<"streets" | "voyager" | "satellite">("streets");
  const [activeFilter, setActiveFilter] = useState<"ALL" | "SEVERE" | "MODERATE" | "LOW" | "NORMAL">("ALL");
  const [locationsOpen, setLocationsOpen] = useState(false);

  // Initialize Map
  useEffect(() => {
    if (typeof window === "undefined" || !mapContainerRef.current) return;

    let isMounted = true;

    // Dynamically import leaflet to prevent SSR window error
    import("leaflet").then((L) => {
      if (!isMounted || !mapContainerRef.current) return;

      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }

      // Nagpur center
      const nagpurCenter: [number, number] = [21.1458, 79.0882];
      const initialZoom = mode === "fullscreen" ? 13 : 12;

      const map = L.map(mapContainerRef.current, {
        center: nagpurCenter,
        zoom: initialZoom,
        zoomControl: false,
        attributionControl: true,
      });

      // Default OpenStreetMap / CartoDB tile layer
      const getTileUrl = (type: string) => {
        if (type === "voyager") {
          return "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png";
        } else if (type === "satellite") {
          return "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
        }
        return "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
      };

      const tileLayer = L.tileLayer(getTileUrl(mapType), {
        maxZoom: 19,
        attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
      }).addTo(map);

      (map as any)._currentTileLayer = tileLayer;

      const layerGroup = L.layerGroup().addTo(map);
      const routeLayer = L.layerGroup().addTo(map);

      layerGroupRef.current = layerGroup;
      routeLayerRef.current = routeLayer;
      mapInstanceRef.current = map;

      renderMarkers(L, map, layerGroup);
    });

    return () => {
      isMounted = false;
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Handle map type changes
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    import("leaflet").then((L) => {
      const map = mapInstanceRef.current;
      if (!map) return;

      if ((map as any)._currentTileLayer) {
        map.removeLayer((map as any)._currentTileLayer);
      }

      let url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
      let attr = '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a>';

      if (mapType === "voyager") {
        url = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png";
        attr = '&copy; <a href="https://carto.com/">CARTO</a>';
      } else if (mapType === "satellite") {
        url = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
        attr = '&copy; Esri, Maxar, Earthstar';
      }

      const newTile = L.tileLayer(url, { maxZoom: 19, attribution: attr }).addTo(map);
      (map as any)._currentTileLayer = newTile;
    });
  }, [mapType]);

  // Render markers whenever filter or data updates
  const renderMarkers = (L: any, map: any, layerGroup: any) => {
    if (!layerGroup) return;
    layerGroup.clearLayers();

    // Use backend data if available, otherwise NAGPUR_DEFAULT_HOTSPOTS
    const items =
      incidents.length > 0
        ? incidents.map((inc) => ({
            name: inc.location_name,
            lat: inc.latitude,
            lng: inc.longitude,
            severity:
              inc.severity === "Critical"
                ? "SEVERE"
                : inc.severity === "High"
                ? "SEVERE"
                : inc.severity === "Moderate"
                ? "MODERATE"
                : "LOW",
            depth: `${(inc.water_depth_cm || 0).toFixed(1)} cm`,
            drainage: "Monitored",
            status: `${inc.severity} / ${inc.status}`,
            color:
              inc.severity === "Critical" || inc.severity === "High"
                ? "#ff4757"
                : inc.severity === "Moderate"
                ? "#ff6b35"
                : inc.severity === "Low"
                ? "#ffa502"
                : "#2ed573",
          }))
        : NAGPUR_DEFAULT_HOTSPOTS;

    items.forEach((item) => {
      if (activeFilter !== "ALL" && item.severity !== activeFilter) {
        return;
      }

      // Create glowing concentric circle marker
      const customIcon = L.divIcon({
        className: "custom-leaflet-marker",
        html: `
          <div style="
            position: relative;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
          ">
            <div style="
              position: absolute;
              width: 24px;
              height: 24px;
              border-radius: 50%;
              background: ${item.color};
              opacity: 0.3;
              animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;
            "></div>
            <div style="
              position: absolute;
              width: 14px;
              height: 14px;
              border-radius: 50%;
              background: ${item.color};
              border: 2px solid #ffffff;
              box-shadow: 0 0 10px ${item.color};
            "></div>
          </div>
        `,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
      });

      const marker = L.marker([item.lat, item.lng], { icon: customIcon });

      const popupContent = `
        <div style="
          background: #111a2e;
          color: #ffffff;
          padding: 12px;
          border-radius: 8px;
          border: 1px solid rgba(0, 212, 255, 0.3);
          font-family: 'Inter', sans-serif;
          min-width: 180px;
        ">
          <div style="font-size: 13px; font-weight: 700; color: #fff; margin-bottom: 6px;">
            ${item.name}
          </div>
          <div style="
            display: inline-block;
            background: ${item.color}22;
            color: ${item.color};
            border: 1px solid ${item.color}66;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
            margin-bottom: 8px;
          ">
            ${item.status}
          </div>
          <div style="font-size: 11px; color: #8b95a8; display: flex; justify-content: space-between; margin-bottom: 3px;">
            <span>Water Depth:</span>
            <span style="color: #00d4ff; font-weight: 600;">${item.depth}</span>
          </div>
          <div style="font-size: 11px; color: #8b95a8; display: flex; justify-content: space-between;">
            <span>Drainage:</span>
            <span style="color: #fff; font-weight: 500;">${item.drainage}</span>
          </div>
        </div>
      `;

      marker.bindPopup(popupContent, {
        className: "custom-leaflet-popup",
        closeButton: true,
      });

      marker.addTo(layerGroup);
    });
  };

  useEffect(() => {
    if (!mapInstanceRef.current || !layerGroupRef.current) return;
    import("leaflet").then((L) => {
      renderMarkers(L, mapInstanceRef.current, layerGroupRef.current);
    });
  }, [activeFilter, incidents]);

  // Route drawing
  useEffect(() => {
    if (!mapInstanceRef.current || !routeLayerRef.current) return;
    import("leaflet").then((L) => {
      const routeLayer = routeLayerRef.current;
      routeLayer.clearLayers();

      if (activeRoute && activeRoute.coordinates && activeRoute.coordinates.length > 0) {
        const latlngs = activeRoute.coordinates;
        const polyline = L.polyline(latlngs, {
          color: "#00d4ff",
          weight: 5,
          opacity: 0.85,
          dashArray: activeRoute.is_recommended ? undefined : "6, 8",
        }).addTo(routeLayer);

        mapInstanceRef.current.fitBounds(polyline.getBounds(), { padding: [40, 40] });
      }
    });
  }, [activeRoute]);

  const handleZoomIn = () => {
    if (mapInstanceRef.current) mapInstanceRef.current.zoomIn();
  };

  const handleZoomOut = () => {
    if (mapInstanceRef.current) mapInstanceRef.current.zoomOut();
  };

  const handleResetCenter = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.setView([21.1458, 79.0882], mode === "fullscreen" ? 13 : 12);
    }
  };

  const handleFlyToLocation = (lat: number, lng: number) => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([lat, lng], 15, { duration: 1.2 });
    }
  };

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: mode === "fullscreen" ? "calc(100vh - 60px)" : "420px",
        borderRadius: mode === "fullscreen" ? "0" : "12px",
        overflow: "hidden",
        border: mode === "fullscreen" ? "none" : "1px solid var(--border-glass)",
        background: "#0a1628",
      }}
    >
      {/* Actual Map Container */}
      <div ref={mapContainerRef} style={{ width: "100%", height: "100%", zIndex: 1 }} />

      {/* Top Header Overlay (for Fullscreen mode as in Screenshot 5) */}
      {mode === "fullscreen" && (
        <div
          style={{
            position: "absolute",
            top: 18,
            left: 20,
            zIndex: 10,
            background: "rgba(13, 20, 35, 0.9)",
            backdropFilter: "blur(12px)",
            border: "1px solid rgba(0, 212, 255, 0.25)",
            borderRadius: 12,
            padding: "12px 18px",
            boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
            maxWidth: 380,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <MapPin size={17} color="#00d4ff" />
            <span style={{ fontSize: "14px", fontWeight: 700, color: "#fff" }}>
              Nagpur Waterlogging Hotspot Map
            </span>
          </div>
          <div style={{ fontSize: "11px", color: "#8b95a8", marginBottom: 12 }}>
            Real-time sensor data &amp; citizen reports
          </div>

          {/* Filter Pills matching Screenshot 5 */}
          <div className="map-filter-bar">
            {(["ALL", "SEVERE", "MODERATE", "LOW", "NORMAL"] as const).map((filter) => {
              const count =
                filter === "ALL"
                  ? 8
                  : filter === "SEVERE"
                  ? 1
                  : filter === "MODERATE"
                  ? 3
                  : filter === "LOW"
                  ? 3
                  : 1;

              const label =
                filter === "ALL"
                  ? "All"
                  : filter === "SEVERE"
                  ? `Severe (${count})`
                  : filter === "MODERATE"
                  ? `Moderate (${count})`
                  : filter === "LOW"
                  ? `Low (${count})`
                  : `Normal (${count})`;

              return (
                <button
                  key={filter}
                  className={`map-pill ${activeFilter === filter ? "active" : ""}`}
                  onClick={() => setActiveFilter(filter)}
                  style={{
                    padding: "4px 8px",
                    fontSize: "10px",
                  }}
                >
                  {label}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Map Type Switcher (Screenshot 3 style) */}
      <div
        style={{
          position: "absolute",
          top: 14,
          left: mode === "fullscreen" ? "auto" : 14,
          right: mode === "fullscreen" ? 140 : "auto",
          zIndex: 10,
          background: "rgba(10, 16, 28, 0.85)",
          backdropFilter: "blur(10px)",
          border: "1px solid rgba(255, 255, 255, 0.1)",
          borderRadius: 8,
          padding: 4,
          display: "flex",
          alignItems: "center",
          gap: 4,
        }}
      >
        <span
          style={{
            fontSize: "11px",
            color: "#8b95a8",
            padding: "0 8px",
            fontWeight: 500,
            display: "flex",
            alignItems: "center",
            gap: 4,
          }}
        >
          <Layers size={12} /> Map Type:
        </span>
        {(["streets", "voyager", "satellite"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setMapType(t)}
            style={{
              padding: "4px 10px",
              borderRadius: 6,
              fontSize: "11px",
              fontWeight: 600,
              textTransform: "capitalize",
              background: mapType === t ? "var(--accent-cyan)" : "transparent",
              color: mapType === t ? "#000" : "#8b95a8",
              border: "none",
              cursor: "pointer",
              transition: "all 0.15s",
            }}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Locations Drawer Button on Top Right (Screenshot 5) */}
      {mode === "fullscreen" && (
        <button
          onClick={() => setLocationsOpen(!locationsOpen)}
          style={{
            position: "absolute",
            top: 14,
            right: 20,
            zIndex: 10,
            background: "rgba(10, 16, 28, 0.85)",
            backdropFilter: "blur(10px)",
            border: "1px solid rgba(255, 255, 255, 0.15)",
            borderRadius: 8,
            color: "#fff",
            fontSize: "12px",
            fontWeight: 600,
            padding: "8px 14px",
            display: "flex",
            alignItems: "center",
            gap: 6,
            cursor: "pointer",
          }}
        >
          <MapPin size={14} color="#00d4ff" />
          <span>Locations ▾</span>
        </button>
      )}

      {/* Locations Slide-out Panel */}
      {locationsOpen && (
        <div
          style={{
            position: "absolute",
            top: 60,
            right: 20,
            width: 280,
            maxHeight: "75vh",
            zIndex: 20,
            background: "#0d1423",
            border: "1px solid rgba(0, 212, 255, 0.3)",
            borderRadius: 12,
            boxShadow: "0 12px 36px rgba(0,0,0,0.6)",
            padding: 14,
            overflowY: "auto",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: 10,
              borderBottom: "1px solid rgba(255,255,255,0.08)",
              paddingBottom: 6,
            }}
          >
            <span style={{ fontSize: "12px", fontWeight: 700, color: "#fff" }}>
              Nagpur Monitored Areas
            </span>
            <button
              onClick={() => setLocationsOpen(false)}
              style={{ background: "none", border: "none", color: "#8b95a8", cursor: "pointer" }}
            >
              <X size={15} />
            </button>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {NAGPUR_DEFAULT_HOTSPOTS.map((spot) => (
              <div
                key={spot.name}
                onClick={() => {
                  handleFlyToLocation(spot.lat, spot.lng);
                  if (onSelectHotspot) onSelectHotspot(spot.name);
                }}
                style={{
                  padding: "8px 10px",
                  borderRadius: 6,
                  background: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  cursor: "pointer",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <div style={{ fontSize: "12px", color: "#fff", fontWeight: 600 }}>{spot.name}</div>
                  <div style={{ fontSize: "10px", color: "#8b95a8" }}>Depth: {spot.depth}</div>
                </div>
                <span
                  style={{
                    fontSize: "9px",
                    fontWeight: 700,
                    color: spot.color,
                    background: `${spot.color}18`,
                    border: `1px solid ${spot.color}44`,
                    padding: "2px 6px",
                    borderRadius: 4,
                  }}
                >
                  {spot.severity}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Floating Severity Legend at Bottom-Left (matching Screenshots 3, 4 & 5) */}
      <div
        style={{
          position: "absolute",
          bottom: 14,
          left: 14,
          zIndex: 10,
          background: "rgba(10, 16, 28, 0.9)",
          backdropFilter: "blur(10px)",
          border: "1px solid rgba(255, 255, 255, 0.12)",
          borderRadius: 8,
          padding: "6px 14px",
          display: "flex",
          alignItems: "center",
          gap: 12,
          fontSize: "11px",
          color: "#8b95a8",
        }}
      >
        <span style={{ fontWeight: 600, color: "#fff" }}>Severity:</span>
        <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
          <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#2ed573" }} />
          <span>Normal</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
          <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#ffa502" }} />
          <span>Low</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
          <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#ff6b35" }} />
          <span>Moderate</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
          <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#ff4757" }} />
          <span>Severe</span>
        </div>
      </div>

      {/* Map Control Buttons at Bottom-Right (Compass, Zoom +/-) */}
      <div
        style={{
          position: "absolute",
          bottom: 24,
          right: 14,
          zIndex: 10,
          display: "flex",
          flexDirection: "column",
          gap: 6,
        }}
      >
        <button
          onClick={handleResetCenter}
          title="Reset to Nagpur Center"
          style={{
            width: 34,
            height: 34,
            borderRadius: 8,
            background: "rgba(10, 16, 28, 0.9)",
            border: "1px solid rgba(0, 212, 255, 0.3)",
            color: "#00d4ff",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
          }}
        >
          <Compass size={18} />
        </button>

        <button
          onClick={handleZoomIn}
          title="Zoom In"
          style={{
            width: 34,
            height: 34,
            borderRadius: 8,
            background: "rgba(10, 16, 28, 0.9)",
            border: "1px solid rgba(255, 255, 255, 0.15)",
            color: "#fff",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
          }}
        >
          <Plus size={16} />
        </button>

        <button
          onClick={handleZoomOut}
          title="Zoom Out"
          style={{
            width: 34,
            height: 34,
            borderRadius: 8,
            background: "rgba(10, 16, 28, 0.9)",
            border: "1px solid rgba(255, 255, 255, 0.15)",
            color: "#fff",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
          }}
        >
          <Minus size={16} />
        </button>
      </div>
    </div>
  );
}
