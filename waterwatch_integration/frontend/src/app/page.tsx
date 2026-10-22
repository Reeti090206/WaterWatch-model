"use client";

import React, { useEffect, useState, useCallback } from "react";
import Sidebar from "../components/Sidebar";
import HomeHeroView from "../components/HomeHeroView";
import LiveDashboardView from "../components/LiveDashboardView";
import LeafletMapComponent from "../components/LeafletMapComponent";
import RouteRecommendationView from "../components/RouteRecommendationView";
import PredictiveRiskView from "../components/PredictiveRiskView";
import RainfallPredictionView from "../components/RainfallPredictionView";
import ImageDetectionView from "../components/ImageDetectionView";
import CitizenReportView from "../components/CitizenReportView";
import SignInView from "../components/SignInView";
import HotspotsAnalyticsView from "../components/HotspotsAnalyticsView";
import ModelStatusView from "../components/ModelStatusView";
import MLPredictionTableModal from "../components/MLPredictionTableModal";
import AdminReviewModal from "../components/AdminReviewModal";
import Footer from "../components/Footer";
import {
  DashboardSummary,
  Incident,
  HistoricalHotspot,
  RoadClosure,
  CitizenReport,
  RouteSegment,
} from "../types";
import { api } from "../services/api";
import { ShieldCheck, UserCheck, AlertCircle } from "lucide-react";

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<string>("home");
  const [collapsed, setCollapsed] = useState<boolean>(false);
  const [role, setRole] = useState<"Citizen" | "Auth" | "Admin">("Citizen");

  // Global State
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [hotspots, setHotspots] = useState<HistoricalHotspot[]>([]);
  const [closures, setClosures] = useState<RoadClosure[]>([]);
  const [reports, setReports] = useState<CitizenReport[]>([]);
  const [activeRoute, setActiveRoute] = useState<RouteSegment | null>(null);
  const [reviewReport, setReviewReport] = useState<CitizenReport | null>(null);
  const [showPredictionTable, setShowPredictionTable] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Load all initial data from backend (with safe fallback)
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
      console.warn("Backend not active, using default Nagpur telemetry and sensor dataset", e);
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
    <div className="app-layout">
      {/* Vertical Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        collapsed={collapsed}
        setCollapsed={setCollapsed}
        role={role}
        setRole={setRole}
      />

      {/* Main Content Area offset by sidebar */}
      <main
        className="main-content"
        style={{
          marginLeft: collapsed ? "var(--sidebar-collapsed)" : "var(--sidebar-width)",
          transition: "margin-left 0.25s cubic-bezier(0.4, 0, 0.2, 1)",
          width: `calc(100% - ${collapsed ? "var(--sidebar-collapsed)" : "var(--sidebar-width)"})`,
        }}
      >
        {/* Tab 1: Home (Screenshots 1 & 2) */}
        {activeTab === "home" && <HomeHeroView onNavigate={setActiveTab} />}

        {/* Tab 2: Live Dashboard (Screenshots 3 & 4) */}
        {activeTab === "dashboard" && (
          <>
            <LiveDashboardView
              summary={summary}
              incidents={incidents}
              hotspots={hotspots}
              closures={closures}
              reports={reports}
              onNavigate={setActiveTab}
              onRefresh={loadInitialData}
              onOpenPredictionTable={() => setShowPredictionTable(true)}
            />
            <Footer onNavigate={setActiveTab} />
          </>
        )}

        {/* Tab 3: Waterlogging Map (Screenshot 5) */}
        {activeTab === "map" && (
          <div style={{ height: "100vh", width: "100%", position: "relative" }}>
            <LeafletMapComponent
              incidents={incidents}
              hotspots={hotspots}
              closures={closures}
              reports={reports}
              mode="fullscreen"
            />
          </div>
        )}

        {/* Tab 4: Safe Route Planner (Image 1 & 2) */}
        {activeTab === "routing" && (
          <div style={{ padding: "20px 24px", minHeight: "80vh" }}>
            <RouteRecommendationView
              onSelectRouteForMap={(route) => setActiveRoute(route)}
              activeRoute={activeRoute}
            />
            <Footer onNavigate={setActiveTab} />
          </div>
        )}

        {/* Tab 5: Predictive Waterlogging Risk Dashboard (Image 3) */}
        {activeTab === "predictions" && (
          <div style={{ padding: "24px 28px", display: "flex", flexDirection: "column", gap: 24 }}>
            <PredictiveRiskView
              onOpenPredictionTable={() => setShowPredictionTable(true)}
            />

            {/* Detailed Interactive ML Predictor & Optical Detection */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <RainfallPredictionView />
              <ImageDetectionView />
            </div>

            <Footer onNavigate={setActiveTab} />
          </div>
        )}

        {/* Tab 6: Report Incident (Image 4) */}
        {activeTab === "report" && (
          <div style={{ padding: "24px 28px" }}>
            <CitizenReportView
              reports={reports}
              onRefreshReports={refreshReports}
              onOpenReview={(r) => setReviewReport(r)}
            />
            <Footer onNavigate={setActiveTab} />
          </div>
        )}

        {/* Tab 7: Authority Dashboard */}
        {activeTab === "authority" && (
          <div style={{ padding: "24px 28px", minHeight: "80vh" }}>
            <div className="section-header" style={{ paddingLeft: 0, paddingRight: 0 }}>
              <div>
                <h2 className="section-title">
                  <ShieldCheck size={22} color="#00d4ff" /> Authority Verification &amp; Control
                </h2>
                <p className="section-subtitle">
                  Verify or reject citizen-submitted waterlogging reports before publishing to public maps
                </p>
              </div>
            </div>

            <div className="glass-card" style={{ padding: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#fff" }}>
                  Pending Incident Reports ({reports.length})
                </h3>
                <span className="badge badge-simulated">AUTHORITY LEVEL ACCESS</span>
              </div>

              {reports.length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {reports.map((r) => (
                    <div
                      key={r.id}
                      style={{
                        background: "rgba(255,255,255,0.02)",
                        border: "1px solid rgba(255,255,255,0.06)",
                        borderRadius: 8,
                        padding: "14px 18px",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <div>
                        <div style={{ fontSize: "14px", fontWeight: 700, color: "#fff", marginBottom: 4 }}>
                          {r.location_name}
                        </div>
                        <div style={{ fontSize: "12px", color: "#8b95a8", marginBottom: 4 }}>
                          {r.description}
                        </div>
                        <div style={{ fontSize: "11px", color: "#5a6478" }}>
                          Report #{r.report_code} | Severity: {r.estimated_severity}
                        </div>
                      </div>

                      <div style={{ display: "flex", gap: 8 }}>
                        <button
                          className="btn-outline-cyan"
                          style={{ padding: "6px 14px", fontSize: "11px" }}
                          onClick={() => setReviewReport(r)}
                        >
                          Review &amp; Verify
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ textAlign: "center", padding: "40px 20px", color: "#8b95a8" }}>
                  <AlertCircle size={32} color="#00d4ff" style={{ margin: "0 auto 10px" }} />
                  <p>All citizen incident reports have been reviewed and verified.</p>
                </div>
              )}
            </div>
            <Footer onNavigate={setActiveTab} />
          </div>
        )}

        {/* Tab 8: Admin Panel */}
        {activeTab === "admin" && (
          <div style={{ padding: "24px 28px", display: "flex", flexDirection: "column", gap: 24 }}>
            <ModelStatusView />
            <HotspotsAnalyticsView hotspots={hotspots} />
            <Footer onNavigate={setActiveTab} />
          </div>
        )}

        {/* Tab 9: Account / Sign In (Image 5) */}
        {activeTab === "account" && (
          <div style={{ padding: "20px 24px" }}>
            <SignInView
              onSignInSuccess={(newRole) => {
                setRole(newRole);
                setActiveTab("dashboard");
              }}
            />
            <Footer onNavigate={setActiveTab} />
          </div>
        )}
      </main>

      {/* Admin Review Modal */}
      {reviewReport && (
        <AdminReviewModal
          report={reviewReport}
          onClose={() => setReviewReport(null)}
          onSuccess={() => {
            setReviewReport(null);
            refreshReports();
          }}
        />
      )}

      {/* Strict ML Model Prediction Table Modal */}
      <MLPredictionTableModal
        isOpen={showPredictionTable}
        onClose={() => setShowPredictionTable(false)}
      />
    </div>
  );
}
