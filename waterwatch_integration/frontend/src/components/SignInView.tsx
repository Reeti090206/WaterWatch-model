"use client";

import React, { useState } from "react";
import {
  Droplet,
  User,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  Shield,
  CheckCircle2,
} from "lucide-react";

interface SignInProps {
  onSignInSuccess?: (role: "Citizen" | "Auth" | "Admin") => void;
}

export default function SignInView({ onSignInSuccess }: SignInProps) {
  const [activeTab, setActiveTab] = useState<"signin" | "register">("signin");
  const [username, setUsername] = useState("citizen");
  const [password, setPassword] = useState("citizen@123");
  const [showPassword, setShowPassword] = useState(false);
  const [signedInRole, setSignedInRole] = useState<string | null>(null);

  const handleQuickFill = (role: "Citizen" | "Auth" | "Admin") => {
    if (role === "Citizen") {
      setUsername("citizen");
      setPassword("citizen@123");
    } else if (role === "Auth") {
      setUsername("authority");
      setPassword("authority123");
    } else {
      setUsername("admin");
      setPassword("admin123");
    }
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    let detectedRole: "Citizen" | "Auth" | "Admin" = "Citizen";
    if (username.toLowerCase().includes("admin")) {
      detectedRole = "Admin";
    } else if (username.toLowerCase().includes("auth")) {
      detectedRole = "Auth";
    }

    setSignedInRole(detectedRole);
    if (onSignInSuccess) {
      onSignInSuccess(detectedRole);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px 20px",
        minHeight: "75vh",
      }}
    >
      {/* Top Cyan Droplet Icon matching Image 5 */}
      <div
        style={{
          width: 52,
          height: 52,
          borderRadius: 14,
          background: "linear-gradient(135deg, #00d4ff, #0077b6)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: "0 0 24px rgba(0, 212, 255, 0.5)",
          marginBottom: 16,
        }}
      >
        <Droplet size={26} fill="#ffffff" color="#ffffff" />
      </div>

      <h1 style={{ fontSize: "1.6rem", fontWeight: 800, color: "#fff", marginBottom: 6 }}>
        Sign In to Nagpur WaterWatch
      </h1>
      <p style={{ fontSize: "0.85rem", color: "#8b95a8", marginBottom: 24, textAlign: "center" }}>
        Access live sensor telemetry, verified reports, and navigation.
      </p>

      {/* Demo Quick-Fill Credentials Card matching Image 5 */}
      <div
        style={{
          width: "100%",
          maxWidth: 440,
          background: "rgba(255,255,255,0.02)",
          border: "1px solid rgba(255,255,255,0.07)",
          borderRadius: 12,
          padding: "12px 16px",
          marginBottom: 16,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontSize: "11px",
            color: "#8b95a8",
            marginBottom: 10,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 6, color: "#00d4ff", fontWeight: 600 }}>
            <span>🛠 Demo Quick-Fill Credentials:</span>
          </div>
          <span style={{ fontSize: "10px", color: "#5a6478" }}>Click to auto-fill</span>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
          <button
            type="button"
            onClick={() => handleQuickFill("Citizen")}
            style={{
              background: username === "citizen" ? "rgba(0, 212, 255, 0.15)" : "rgba(255,255,255,0.03)",
              border: username === "citizen" ? "1px solid #00d4ff" : "1px solid rgba(255,255,255,0.08)",
              borderRadius: 6,
              padding: "6px 8px",
              textAlign: "center",
              cursor: "pointer",
            }}
          >
            <div style={{ fontSize: "11px", fontWeight: 700, color: "#fff" }}>Citizen</div>
            <div style={{ fontSize: "9px", color: "#8b95a8" }}>citizen@123</div>
          </button>

          <button
            type="button"
            onClick={() => handleQuickFill("Auth")}
            style={{
              background: username === "authority" ? "rgba(0, 212, 255, 0.15)" : "rgba(255,255,255,0.03)",
              border: username === "authority" ? "1px solid #00d4ff" : "1px solid rgba(255,255,255,0.08)",
              borderRadius: 6,
              padding: "6px 8px",
              textAlign: "center",
              cursor: "pointer",
            }}
          >
            <div style={{ fontSize: "11px", fontWeight: 700, color: "#fff" }}>Authority</div>
            <div style={{ fontSize: "9px", color: "#8b95a8" }}>authority123</div>
          </button>

          <button
            type="button"
            onClick={() => handleQuickFill("Admin")}
            style={{
              background: username === "admin" ? "rgba(0, 212, 255, 0.15)" : "rgba(255,255,255,0.03)",
              border: username === "admin" ? "1px solid #00d4ff" : "1px solid rgba(255,255,255,0.08)",
              borderRadius: 6,
              padding: "6px 8px",
              textAlign: "center",
              cursor: "pointer",
            }}
          >
            <div style={{ fontSize: "11px", fontWeight: 700, color: "#fff" }}>Admin</div>
            <div style={{ fontSize: "9px", color: "#8b95a8" }}>admin123</div>
          </button>
        </div>
      </div>

      {/* Main Glass Sign In Form Card matching Image 5 */}
      <div
        className="glass-card"
        style={{
          width: "100%",
          maxWidth: 440,
          padding: "24px",
        }}
      >
        {signedInRole && (
          <div
            style={{
              background: "rgba(46, 213, 115, 0.12)",
              border: "1px solid rgba(46, 213, 115, 0.35)",
              borderRadius: 8,
              padding: "10px 14px",
              display: "flex",
              alignItems: "center",
              gap: 8,
              color: "#2ed573",
              fontSize: "12px",
              fontWeight: 600,
              marginBottom: 16,
            }}
          >
            <CheckCircle2 size={16} />
            <span>Authenticated successfully as {signedInRole}! Session is active.</span>
          </div>
        )}

        {/* Sign In / Register Tabs matching Image 5 */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 4,
            background: "rgba(0,0,0,0.3)",
            padding: 4,
            borderRadius: 8,
            marginBottom: 20,
          }}
        >
          <button
            type="button"
            onClick={() => setActiveTab("signin")}
            style={{
              padding: "8px",
              borderRadius: 6,
              fontSize: "12px",
              fontWeight: 700,
              border: "none",
              cursor: "pointer",
              background: activeTab === "signin" ? "#00b4d8" : "transparent",
              color: activeTab === "signin" ? "#fff" : "#8b95a8",
              transition: "all 0.15s",
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("register")}
            style={{
              padding: "8px",
              borderRadius: 6,
              fontSize: "12px",
              fontWeight: 700,
              border: "none",
              cursor: "pointer",
              background: activeTab === "register" ? "#00b4d8" : "transparent",
              color: activeTab === "register" ? "#fff" : "#8b95a8",
              transition: "all 0.15s",
            }}
          >
            Register
          </button>
        </div>

        <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Username Input */}
          <div>
            <label style={{ fontSize: "11px", color: "#8b95a8", display: "block", marginBottom: 6 }}>
              Username
            </label>
            <div style={{ position: "relative" }}>
              <User
                size={16}
                color="#8b95a8"
                style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)" }}
              />
              <input
                type="text"
                className="input-field"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={{ paddingLeft: 38 }}
                required
              />
            </div>
          </div>

          {/* Password Input */}
          <div>
            <label style={{ fontSize: "11px", color: "#8b95a8", display: "block", marginBottom: 6 }}>
              Password
            </label>
            <div style={{ position: "relative" }}>
              <Lock
                size={16}
                color="#8b95a8"
                style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)" }}
              />
              <input
                type={showPassword ? "text" : "password"}
                className="input-field"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{ paddingLeft: 38, paddingRight: 38 }}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: "absolute",
                  right: 12,
                  top: "50%",
                  transform: "translateY(-50%)",
                  background: "none",
                  border: "none",
                  color: "#8b95a8",
                  cursor: "pointer",
                  display: "flex",
                }}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {/* Sign In Button */}
          <button
            type="submit"
            className="btn-primary"
            style={{
              width: "100%",
              justifyContent: "center",
              padding: "11px",
              fontSize: "13px",
              fontWeight: 700,
              marginTop: 4,
            }}
          >
            <span>Sign In to System</span>
            <ArrowRight size={15} />
          </button>

          {/* Footer Register link matching Image 5 */}
          <div style={{ textAlign: "center", fontSize: "11px", color: "#8b95a8", marginTop: 4 }}>
            <span>Don&apos;t have an account yet? </span>
            <span
              onClick={() => setActiveTab("register")}
              style={{ color: "#00d4ff", cursor: "pointer", textDecoration: "underline" }}
            >
              Register here
            </span>
          </div>
        </form>
      </div>

      {/* Protected Security Framework note matching Image 5 */}
      <div style={{ marginTop: 24, fontSize: "11px", color: "#5a6478", display: "flex", alignItems: "center", gap: 6 }}>
        <Shield size={13} color="#5a6478" />
        <span>Protected under Nagpur WaterWatch municipal security framework.</span>
      </div>
    </div>
  );
}
