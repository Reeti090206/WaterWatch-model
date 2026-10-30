"use client";

import React from "react";
import {
  Droplet,
  Activity,
  Map,
  Navigation,
  AlertTriangle,
  FileText,
  ShieldCheck,
  Settings,
  User,
  PanelLeftClose,
  PanelLeftOpen,
  Wifi,
  Zap,
} from "lucide-react";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
  role: "Citizen" | "Auth" | "Admin";
  setRole: (role: "Citizen" | "Auth" | "Admin") => void;
}

export default function Sidebar({
  activeTab,
  setActiveTab,
  collapsed,
  setCollapsed,
  role,
  setRole,
}: SidebarProps) {
  const navItems = [
    { id: "home", label: "Home", icon: Droplet },
    { id: "livedemo", label: "Live AI Demo", icon: Zap },
    { id: "dashboard", label: "Live Dashboard", icon: Activity },
    { id: "map", label: "Waterlogging Map", icon: Map },
    { id: "routing", label: "Safe Route Planner", icon: Navigation },
    { id: "predictions", label: "Predictions", icon: AlertTriangle },
    { id: "report", label: "Report Incident", icon: FileText },
    { id: "authority", label: "Authority Dashboard", icon: ShieldCheck },
    { id: "admin", label: "Admin Panel", icon: Settings },
    { id: "account", label: "Sign In / Account", icon: User },
  ];

  return (
    <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
      {/* Top Brand */}
      <div
        className="sidebar-brand"
        onClick={() => setCollapsed(!collapsed)}
        title={collapsed ? "Click to expand" : "Click to collapse"}
      >
        <div className="sidebar-brand-icon">
          <Droplet size={18} fill="#ffffff" color="#ffffff" />
        </div>
        {!collapsed && (
          <div className="sidebar-brand-text" style={{ flex: 1, minWidth: 0 }}>
            <h2>Nagpur WaterWatch</h2>
            <span>Smart Water Monitor</span>
          </div>
        )}
        <button
          onClick={(e) => {
            e.stopPropagation();
            setCollapsed(!collapsed);
          }}
          aria-label="Toggle sidebar"
          style={{
            background: "none",
            border: "none",
            color: "#8b95a8",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            padding: 4,
          }}
        >
          {collapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`sidebar-item ${isActive ? "active" : ""}`}
              onClick={() => setActiveTab(item.id)}
              title={collapsed ? item.label : undefined}
            >
              <span className="sidebar-icon">
                <Icon size={18} />
              </span>
              {!collapsed && <span className="sidebar-label">{item.label}</span>}
            </button>
          );
        })}
      </nav>

      {/* Bottom Section */}
      <div className="sidebar-bottom">
        {!collapsed && (
          <div className="sidebar-role-switcher">
            <div className="role-title">
              <User size={12} />
              <span>Role Mode</span>
            </div>
            <div className="role-pills">
              {(["Citizen", "Auth", "Admin"] as const).map((r) => (
                <button
                  key={r}
                  className={`role-pill ${role === r ? "active" : ""}`}
                  onClick={() => setRole(r)}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>
        )}

        <div
          className="sidebar-status"
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: collapsed ? "center" : "space-between",
            paddingTop: 8,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span className="status-dot"></span>
            {!collapsed && <span style={{ fontSize: "11px", color: "#8b95a8" }}>System Live</span>}
          </div>
          {!collapsed && (
            <span
              style={{
                fontSize: "10px",
                color: "#00d4ff",
                background: "rgba(0, 212, 255, 0.1)",
                padding: "2px 6px",
                borderRadius: "4px",
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                gap: 4,
              }}
            >
              <Wifi size={10} /> 24/7 IoT
            </span>
          )}
        </div>

        {!collapsed && (
          <button
            onClick={() => setCollapsed(true)}
            style={{
              width: "100%",
              marginTop: 10,
              padding: "6px 8px",
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.06)",
              borderRadius: 6,
              color: "#8b95a8",
              fontSize: "11px",
              display: "flex",
              alignItems: "center",
              gap: 8,
              cursor: "pointer",
            }}
          >
            <span
              style={{
                width: 18,
                height: 18,
                borderRadius: 4,
                background: "#000",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 800,
                fontSize: 10,
                color: "#fff",
              }}
            >
              N
            </span>
            <span style={{ fontSize: "11px" }}>Contract Panel</span>
          </button>
        )}
      </div>
    </aside>
  );
}
