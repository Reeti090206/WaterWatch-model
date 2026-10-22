"use client";

import React, { useState, useRef } from "react";
import { ImageDetectionResponse } from "../types";
import { api } from "../services/api";

export default function ImageDetectionView() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [confThreshold, setConfThreshold] = useState(0.25);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detectionResult, setDetectionResult] = useState<ImageDetectionResponse | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setDetectionResult(null);
      setError(null);
    }
  };

  const handleDetect = async () => {
    if (!selectedFile) {
      setError("Please select an image file first");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("image", selectedFile);
    formData.append("conf_threshold", confThreshold.toString());

    try {
      const result = await api.detectWaterloggingInImage(formData);
      setDetectionResult(result);

      // Draw bounding boxes on canvas
      if (previewUrl && canvasRef.current) {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");
        const img = new Image();
        img.src = previewUrl;
        img.onload = () => {
          canvas.width = img.width;
          canvas.height = img.height;
          if (!ctx) return;

          ctx.drawImage(img, 0, 0);

          // Draw boxes
          result.detections.forEach((box) => {
            const [x1, y1, x2, y2] = box.bbox_pixels;
            const width = x2 - x1;
            const height = y2 - y1;

            ctx.strokeStyle = "#06b6d4";
            ctx.lineWidth = Math.max(3, Math.round(img.width / 200));
            ctx.strokeRect(x1, y1, width, height);

            ctx.fillStyle = "rgba(6, 182, 212, 0.25)";
            ctx.fillRect(x1, y1, width, height);

            // Label
            const text = `${box.class_name} (${(box.confidence * 100).toFixed(0)}%)`;
            ctx.font = `bold ${Math.max(14, Math.round(img.width / 40))}px Inter, sans-serif`;
            const textWidth = ctx.measureText(text).width;

            ctx.fillStyle = "#06b6d4";
            ctx.fillRect(x1, Math.max(0, y1 - 24), textWidth + 10, 24);

            ctx.fillStyle = "#ffffff";
            ctx.fillText(text, x1 + 5, Math.max(18, y1 - 6));
          });
        };
      }
    } catch (err: any) {
      setError(err.message || "Image detection failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "20px" }}>
      {/* Upload and Controls */}
      <div className="glass-panel" style={{ padding: "22px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
          <div>
            <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#f8fafc" }}>
              📷 Computer Vision Waterlogging Detector
            </h3>
            <p style={{ fontSize: "0.82rem", color: "#94a3b8", marginTop: "2px" }}>
              Optical surface detection powered by Ultralytics YOLOv11 (best.pt).
            </p>
          </div>
          <span style={{ background: "rgba(56, 189, 248, 0.15)", color: "#38bdf8", border: "1px solid rgba(56, 189, 248, 0.3)", padding: "3px 8px", borderRadius: "6px", fontSize: "0.7rem", fontWeight: 600 }}>
            YOLOv11 NANO
          </span>
        </div>

        {/* Upload Dropzone */}
        <div
          onClick={() => fileInputRef.current?.click()}
          style={{
            border: "2px dashed rgba(255, 255, 255, 0.15)",
            borderRadius: "10px",
            padding: "30px 20px",
            textAlign: "center",
            cursor: "pointer",
            background: "rgba(15, 23, 42, 0.4)",
            transition: "all 0.2s",
            marginBottom: "16px",
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            style={{ display: "none" }}
            onChange={handleFileChange}
          />
          <div style={{ fontSize: "2rem", marginBottom: "8px" }}>📸</div>
          <div style={{ fontWeight: 600, fontSize: "0.9rem", color: "#e2e8f0" }}>
            {selectedFile ? selectedFile.name : "Click to select a road photo or drop file here"}
          </div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>
            Supports JPG, JPEG, PNG, WEBP (Max 10MB)
          </div>
        </div>

        {/* Confidence Threshold */}
        <div style={{ marginBottom: "18px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", color: "#94a3b8", marginBottom: "6px" }}>
            <span>Confidence Threshold</span>
            <span style={{ fontWeight: 700, color: "#38bdf8" }}>{(confThreshold * 100).toFixed(0)}%</span>
          </div>
          <input
            type="range"
            min="0.1"
            max="0.9"
            step="0.05"
            value={confThreshold}
            onChange={(e) => setConfThreshold(Number(e.target.value))}
            style={{ width: "100%", accentColor: "#06b6d4" }}
          />
        </div>

        <button
          onClick={handleDetect}
          disabled={!selectedFile || loading}
          className="btn-primary"
          style={{ width: "100%", opacity: !selectedFile ? 0.6 : 1 }}
        >
          {loading ? "Running YOLOv11 Inference..." : "🔍 Run Optical Flood Detection"}
        </button>

        {error && (
          <div style={{ marginTop: "14px", color: "#f87171", fontSize: "0.85rem" }}>
            ⚠️ {error}
          </div>
        )}

        <div style={{ marginTop: "18px", fontSize: "11px", color: "#64748b", lineHeight: 1.4, borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: "12px" }}>
          * <strong>CV Scope:</strong> Detects visible water puddle and ponding surfaces. 2D optical bounding boxes cannot calculate flood depth in centimeters.
        </div>
      </div>

      {/* Detection Visualizer */}
      <div className="glass-panel" style={{ padding: "22px", display: "flex", flexDirection: "column" }}>
        <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#f8fafc", marginBottom: "16px" }}>
          Detection Visualization
        </h3>

        {!previewUrl ? (
          <div
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              color: "#64748b",
              textAlign: "center",
              padding: "40px 20px",
            }}
          >
            <div style={{ fontSize: "3rem", marginBottom: "10px" }}>🖼️</div>
            <p style={{ fontSize: "0.9rem" }}>Upload a roadway photo to inspect bounding boxes</p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
            <div
              style={{
                borderRadius: "8px",
                overflow: "hidden",
                border: "1px solid rgba(255,255,255,0.1)",
                maxHeight: "360px",
                display: "flex",
                justifyContent: "center",
                background: "#0a0e17",
              }}
            >
              <canvas
                ref={canvasRef}
                style={{
                  maxWidth: "100%",
                  maxHeight: "360px",
                  objectFit: "contain",
                }}
              />
            </div>

            {detectionResult && (
              <div style={{ background: "rgba(15, 23, 42, 0.8)", padding: "14px", borderRadius: "8px", border: "1px solid rgba(255,255,255,0.08)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <span style={{ fontWeight: 700, color: detectionResult.waterlogging_detected ? "#f87171" : "#34d399", fontSize: "0.95rem" }}>
                    {detectionResult.waterlogging_detected ? "⚠️ WATERLOGGING DETECTED" : "✅ CLEAR ROAD SURFACE"}
                  </span>
                  <span style={{ fontSize: "12px", color: "#94a3b8" }}>
                    {detectionResult.detection_count} bounding box(es)
                  </span>
                </div>

                {detectionResult.detections.map((d, i) => (
                  <div key={i} style={{ fontSize: "12px", color: "#cbd5e1", display: "flex", justifyContent: "space-between", borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: "4px", marginTop: "4px" }}>
                    <span>Target: <strong>{d.class_name}</strong></span>
                    <span style={{ color: "#38bdf8", fontWeight: 600 }}>Confidence: {(d.confidence * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
