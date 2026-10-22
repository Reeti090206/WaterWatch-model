"use client";

import React, { useEffect, useState, useCallback } from "react";
import Navbar from "../components/Navbar";
import GoogleMapComponent from "../components/GoogleMapComponent";
import DashboardSummaryView from "../components/DashboardSummaryView";
import RouteRecommendationView from "../components/RouteRecommendationView";
import RainfallPredictionView from "../components/RainfallPredictionView";
import ImageDetectionView from "../components/ImageDetectionView";
import CitizenReportView from "../components/CitizenReportView";
import HotspotsAnalyticsView from "../components/HotspotsAnalyticsView";
import ModelStatusView from "../components/ModelStatusView";
import AdminReviewModal from "../components/AdminReviewModal";
import {
  DashboardSummary,
  Incident,
  HistoricalHotspot,
  RoadClosure,
  CitizenReport,
  RouteSegment,
} from "../types";
import { api } from "../services/api";

export default function HomePage() {
  const [activeTab, setActiveTab] = useState("overview");

  // Global State
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [hotspots, setHotspots] = useState<HistoricalHotspot[]>([]);
  const [closures, setClosures] = useState<RoadClosure[]>([]);
  const [reports, setReports] = useState<CitizenReport[]>([]);
  const [activeRoute, setActiveRoute] = useState<RouteSegment | null>(null);
  const [reviewReport, setReviewReport] = useState<CitizenReport | null>(null);

  const [loading, setLoading] = useState(true);

  // Load all initial data from backend
  const loadInitialData = useCallback(async () => {
    try {
      const [sumData, incData, hotData, closeData, repData] = await Promise.allSettled([
        api.getDashboardSummary(),
        api.getIncidents(),
        api.getHotspots(),
        api.getRoadClosures(),
        api.getCitizenReports(),
      ]);

      if (sumData.status === "fulfilled") setSummary(sumData.value);
      if (incData.status === "fulfilled") setIncidents(incData.value);
      if (hotData.status === "fulfilled") setHotspots(hotData.value);
      if (closeData.status === "fulfilled") setClosures(closeData.value);
      if (repData.status === "fulfilled") setReports(repData.value);
    } catch (e) {
      console.error("Data loading error", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  const refreshReports = async () => {
    try {
      const rep = await api.getCitizenReports();
      setReports(rep);
      const inc = await api.getIncidents();
      setIncidents(inc);
    } catch (e) {
      console.error("Refresh error", e);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        weather={summary?.live_weather}
      />

      <main style={{ flex: 1, maxWidth: "1440px", width: "100%", margin: "0 auto", padding: "20px 24px" }}>
        {/* Top Split View: Map is pinned for overview and routing */}
        {(activeTab === "overview" || activeTab === "routing") && (
          <div style={{ marginBottom: "24px" }}>
            <div className="glass-panel" style={{ padding: "8px" }}>
              <GoogleMapComponent
                incidents={incidents}
                hotspots={hotspots}
                closures={closures}
                reports={reports}
                activeRoute={activeRoute}
              />
            </div>
          </div>
        )}

        {/* Tab Modules */}
        {activeTab === "overview" && (
          <DashboardSummaryView
            summary={summary}
            incidents={incidents}
            onNavigateTab={(tab) => setActiveTab(tab)}
          />
        )}

        {activeTab === "routing" && (
          <RouteRecommendationView
            onSelectRouteForMap={(route) => setActiveRoute(route)}
            activeRoute={activeRoute}
          />
        )}

        {activeTab === "rainfall" && <RainfallPredictionView />}

        {activeTab === "detection" && <ImageDetectionView />}

        {activeTab === "citizen" && (
          <CitizenReportView
            reports={reports}
            onRefreshReports={refreshReports}
            onOpenReview={(r) => setReviewReport(r)}
          />
        )}

        {activeTab === "hotspots" && <HotspotsAnalyticsView hotspots={hotspots} />}

        {activeTab === "models" && <ModelStatusView />}
      </main>

      {/* Admin Moderation Modal */}
      {reviewReport && (
        <AdminReviewModal
          report={reviewReport}
          onClose={() => setReviewReport(null)}
          onSuccess={refreshReports}
        />
      )}

      {/* Footer */}
      <footer
        style={{
          borderTop: "1px solid rgba(255, 255, 255, 0.08)",
          padding: "16px 24px",
          textAlign: "center",
          fontSize: "12px",
          color: "#64748b",
          marginTop: "40px",
          background: "#080c14",
        }}
      >
        WaterWatch AI — Nagpur Smart City Municipal & Research Prototype • Model Integrity Preserved
      </footer>
    </div>
  );
}
