"use client";

import React, { useState } from "react";
import { CitizenReport } from "../types";
import { api } from "../services/api";

interface CitizenReportProps {
  reports: CitizenReport[];
  onRefreshReports: () => void;
  onOpenReview: (report: CitizenReport) => void;
}

export default function CitizenReportView({ reports, onRefreshReports, onOpenReview }: CitizenReportProps) {
  const [locationName, setLocationName] = useState("");
  const [latitude, setLatitude] = useState(21.1458);
  const [longitude, setLongitude] = useState(79.0882);
  const [severity, setSeverity] = useState("Moderate");
  const [depthCm, setDepthCm] = useState<number | "">("");
  const [description, setDescription] = useState("");
  const [reporterName, setReporterName] = useState("");
  const [reporterContact, setReporterContact] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);

  const [submitting, setSubmitting] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ text: string; isError: boolean } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setStatusMsg(null);

    const formData = new FormData();
    formData.append("location_name", locationName);
    formData.append("latitude", latitude.toString());
    formData.append("longitude", longitude.toString());
    formData.append("estimated_severity", severity);
    if (depthCm !== "") formData.append("water_depth_cm", depthCm.toString());
    formData.append("description", description);
    if (reporterName) formData.append("reporter_name", reporterName);
    if (reporterContact) formData.append("reporter_contact", reporterContact);
    if (imageFile) formData.append("image", imageFile);

    try {
      const res = await api.submitCitizenReport(formData);
      setStatusMsg({
        text: `Report submitted successfully! Code: ${res.report_code}. Logged as UNVERIFIED pending review.`,
        isError: false,
      });
      setLocationName("");
      setDescription("");
      setDepthCm("");
      setImageFile(null);
      onRefreshReports();
    } catch (err: any) {
      setStatusMsg({ text: err.message || "Failed to submit citizen report", isError: true });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1.3fr", gap: "20px" }}>
      {/* Submission Form */}
      <div className="glass-panel" style={{ padding: "22px" }}>
        <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#f8fafc", marginBottom: "6px" }}>
          📢 Report Waterlogging Incident
        </h3>
        <p style={{ fontSize: "0.82rem", color: "#94a3b8", marginBottom: "16px" }}>
          Crowdsource waterlogging alerts. Reports appear as unverified advisories until verified by NMC.
        </p>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <div>
            <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "4px" }}>
              Location Name / Landmark *
            </label>
            <input
              type="text"
              className="input-field"
              value={locationName}
              onChange={(e) => setLocationName(e.target.value)}
              placeholder="e.g. Wardha Road Metro Pillar 42"
              required
            />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "4px" }}>
                Latitude *
              </label>
              <input
                type="number"
                step="0.0001"
                className="input-field"
                value={latitude}
                onChange={(e) => setLatitude(Number(e.target.value))}
                required
              />
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "4px" }}>
                Longitude *
              </label>
              <input
                type="number"
                step="0.0001"
                className="input-field"
                value={longitude}
                onChange={(e) => setLongitude(Number(e.target.value))}
                required
              />
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "4px" }}>
                Estimated Severity
              </label>
              <select
                className="input-field"
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
              >
                <option value="Low" style={{ background: "#0f172a" }}>Low (Ankle depth, passable)</option>
                <option value="Moderate" style={{ background: "#0f172a" }}>Moderate (Half-wheel depth)</option>
                <option value="High" style={{ background: "#0f172a" }}>High (Submerged exhaust, risky)</option>
                <option value="Critical" style={{ background: "#0f172a" }}>Critical (Road blocked / Underpass flooded)</option>
              </select>
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "4px" }}>
                Est. Depth in cm (Optional)
              </label>
              <input
                type="number"
                className="input-field"
                value={depthCm}
                onChange={(e) => setDepthCm(e.target.value === "" ? "" : Number(e.target.value))}
                placeholder="e.g. 35"
              />
            </div>
          </div>

          <div>
            <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "4px" }}>
              Incident Description *
            </label>
            <textarea
              className="input-field"
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe road blockage, stranded vehicles, or overflowing storm drains..."
              required
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "4px" }}>
              Attach Photo Proof (Optional)
            </label>
            <input
              type="file"
              accept="image/*"
              className="input-field"
              onChange={(e) => setImageFile(e.target.files ? e.target.files[0] : null)}
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="btn-primary"
            style={{ marginTop: "6px" }}
          >
            {submitting ? "Uploading Report..." : "📤 Submit Incident Report"}
          </button>
        </form>

        {statusMsg && (
          <div
            style={{
              marginTop: "14px",
              padding: "10px",
              borderRadius: "8px",
              fontSize: "12px",
              background: statusMsg.isError ? "rgba(239, 68, 68, 0.15)" : "rgba(16, 185, 129, 0.15)",
              color: statusMsg.isError ? "#f87171" : "#34d399",
              border: `1px solid ${statusMsg.isError ? "rgba(239, 68, 68, 0.3)" : "rgba(16, 185, 129, 0.3)"}`,
            }}
          >
            {statusMsg.text}
          </div>
        )}
      </div>

      {/* Reports List & Moderation */}
      <div className="glass-panel" style={{ padding: "22px", display: "flex", flexDirection: "column" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
          <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#f8fafc" }}>
            📋 Live Citizen Reports Feed ({reports.length})
          </h3>
          <button onClick={onRefreshReports} className="btn-secondary" style={{ padding: "4px 10px", fontSize: "11px" }}>
            🔄 Refresh Feed
          </button>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "10px", overflowY: "auto", maxHeight: "560px" }}>
          {reports.length === 0 ? (
            <div style={{ textAlign: "center", color: "#64748b", padding: "40px" }}>
              No citizen reports recorded yet.
            </div>
          ) : (
            reports.map((r) => {
              const isVerified = r.verification_status === "VERIFIED";
              const isRejected = r.verification_status === "REJECTED";

              return (
                <div
                  key={r.id}
                  style={{
                    background: "rgba(255, 255, 255, 0.03)",
                    border: `1px solid ${isVerified ? "rgba(2, 132, 199, 0.4)" : "rgba(255, 255, 255, 0.08)"}`,
                    borderRadius: "8px",
                    padding: "14px",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: "0.92rem", color: "#f1f5f9" }}>{r.location_name}</div>
                      <div style={{ fontSize: "11px", color: "#94a3b8", marginTop: "2px" }}>
                        Code: {r.report_code} • {new Date(r.created_at).toLocaleTimeString()}
                      </div>
                    </div>
                    <span
                      style={{
                        padding: "3px 8px",
                        borderRadius: "4px",
                        fontSize: "10px",
                        fontWeight: 700,
                        background: isVerified ? "rgba(16, 185, 129, 0.2)" : isRejected ? "rgba(239, 68, 68, 0.2)" : "rgba(245, 158, 11, 0.2)",
                        color: isVerified ? "#34d399" : isRejected ? "#f87171" : "#fbbf24",
                      }}
                    >
                      {r.verification_status}
                    </span>
                  </div>

                  <p style={{ fontSize: "12px", color: "#cbd5e1", marginTop: "8px", lineHeight: 1.4 }}>
                    {r.description}
                  </p>

                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "10px", fontSize: "11px" }}>
                    <div style={{ color: "#64748b" }}>
                      Severity: <strong style={{ color: "#e2e8f0" }}>{r.estimated_severity}</strong>
                      {r.water_depth_cm && ` • Depth: ${r.water_depth_cm} cm`}
                    </div>

                    {!isVerified && !isRejected && (
                      <button
                        onClick={() => onOpenReview(r)}
                        className="btn-secondary"
                        style={{ padding: "3px 10px", fontSize: "11px", borderColor: "#06b6d4" }}
                      >
                        🛡️ Review / Verify
                      </button>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
