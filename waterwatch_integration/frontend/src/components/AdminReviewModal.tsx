"use client";

import React, { useState } from "react";
import { CitizenReport } from "../types";
import { api } from "../services/api";

interface AdminModalProps {
  report: CitizenReport | null;
  onClose: () => void;
  onSuccess: () => void;
}

export default function AdminReviewModal({ report, onClose, onSuccess }: AdminModalProps) {
  const [adminToken, setAdminToken] = useState("waterwatch_admin_secret_token_2026");
  const [notes, setNotes] = useState("");
  const [action, setAction] = useState<"VERIFY" | "REJECT" | "REQUEST_INFO">("VERIFY");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!report) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.reviewCitizenReport(report.id, action, notes || "Verified by municipal field unit", adminToken);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to update report status");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 100,
        background: "rgba(0, 0, 0, 0.75)",
        backdropFilter: "blur(6px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "16px",
      }}
    >
      <div
        className="glass-panel"
        style={{
          width: "100%",
          maxWidth: "500px",
          padding: "24px",
          background: "#111827",
          border: "1px solid rgba(255, 255, 255, 0.15)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#f8fafc" }}>
            🛡️ Municipal Review & Verification
          </h3>
          <button
            onClick={onClose}
            style={{ background: "none", border: "none", color: "#94a3b8", fontSize: "18px", cursor: "pointer" }}
          >
            ✕
          </button>
        </div>

        <div style={{ background: "rgba(15, 23, 42, 0.6)", padding: "12px", borderRadius: "8px", marginBottom: "16px", fontSize: "13px" }}>
          <div><strong>Report:</strong> {report.report_code}</div>
          <div><strong>Location:</strong> {report.location_name}</div>
          <div><strong>Reported Severity:</strong> {report.estimated_severity}</div>
          {report.water_depth_cm && <div><strong>Depth:</strong> {report.water_depth_cm} cm</div>}
          <div style={{ color: "#94a3b8", marginTop: "4px" }}>{report.description}</div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <div>
            <label style={{ display: "block", fontSize: "12px", color: "#94a3b8", marginBottom: "4px" }}>
              Action Decision
            </label>
            <select
              className="input-field"
              value={action}
              onChange={(e) => setAction(e.target.value as any)}
            >
              <option value="VERIFY" style={{ background: "#0f172a" }}>
                ✅ Verify & Elevate to Active Municipal Incident
              </option>
              <option value="REJECT" style={{ background: "#0f172a" }}>
                ❌ Reject (Spam / Inaccurate / Resolved)
              </option>
              <option value="REQUEST_INFO" style={{ background: "#0f172a" }}>
                ❓ Request Additional Verification
              </option>
            </select>
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", color: "#94a3b8", marginBottom: "4px" }}>
              Reviewer Notes / Field Action Plan
            </label>
            <textarea
              className="input-field"
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g., Confirmed with Ward 14 traffic warden; drain suction pumps deployed."
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", color: "#94a3b8", marginBottom: "4px" }}>
              Admin Secret Key
            </label>
            <input
              type="password"
              className="input-field"
              value={adminToken}
              onChange={(e) => setAdminToken(e.target.value)}
              required
            />
          </div>

          {error && <div style={{ color: "#f87171", fontSize: "12px" }}>⚠️ {error}</div>}

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "10px" }}>
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? "Submitting Review..." : "Confirm Decision"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
