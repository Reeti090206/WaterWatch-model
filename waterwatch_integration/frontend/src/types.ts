/**
 * WaterWatch AI - Frontend TypeScript Definitions
 * Strictly defines contracts with FastAPI backend endpoints.
 */

export interface Coordinates {
  lat: number;
  lng: number;
}

export interface Incident {
  id: number;
  incident_code: string;
  title: string;
  location_name: string;
  latitude: number;
  longitude: number;
  severity: "Low" | "Moderate" | "High" | "Critical";
  water_depth_cm?: number;
  is_verified: boolean;
  source: string;
  status: "Active" | "Resolved" | "Monitoring";
  created_at: string;
}

export interface CitizenReport {
  id: number;
  report_code: string;
  location_name: string;
  latitude: number;
  longitude: number;
  description: string;
  estimated_severity: "Low" | "Moderate" | "High" | "Critical";
  water_depth_cm?: number;
  image_filename?: string;
  image_url?: string;
  verification_status: "UNVERIFIED" | "VERIFIED" | "REJECTED" | "INFO_REQUESTED";
  reviewer_notes?: string;
  reviewed_by?: string;
  reviewed_at?: string;
  created_at: string;
}

export interface HistoricalHotspot {
  id: number;
  hotspot_code: string;
  name: string;
  locality: string;
  latitude: number;
  longitude: number;
  incident_count_last_5yr: number;
  chronic_cause: string;
  average_depth_cm: number;
  drainage_capacity_proxy: number;
  typical_critical_threshold_mm: number;
}

export interface RoadClosure {
  id: number;
  closure_code: string;
  road_name: string;
  locality: string;
  latitude: number;
  longitude: number;
  reason: string;
  status: string;
  reported_at: string;
}

export interface RainfallPredictionRequest {
  locality_name: string;
  rainfall_1h_mm: number;
  rainfall_3h_mm: number;
  rainfall_6h_mm: number;
  rainfall_24h_mm: number;
  rainfall_prev_72h_mm: number;
  drainage_capacity_proxy: number;
}

export interface RainfallPredictionResponse {
  location: string;
  predicted_class: number;
  waterlogging_predicted: boolean;
  predicted_probability: number;
  risk_category: "LOW" | "MODERATE" | "HIGH";
  model_name: string;
  model_version: string;
  training_data_status: string;
  validation_warnings: string[];
  input_features: Record<string, number>;
  scientific_disclaimer: string;
}

export interface DetectionBox {
  class_id: number;
  class_name: string;
  confidence: number;
  bbox_pixels: [number, number, number, number];
  bbox_normalized: [number, number, number, number];
}

export interface ImageDetectionResponse {
  image_filename: string;
  image_url: string;
  dimensions: { width: number; height: number };
  waterlogging_detected: boolean;
  detection_count: number;
  detections: DetectionBox[];
  conf_threshold_used: number;
  disclaimer: string;
}

export interface RoutePoint {
  name?: string;
  latitude: number;
  longitude: number;
}

export interface RouteSegment {
  preference_type: "fastest" | "lowest_risk" | "balanced";
  distance_km: number;
  duration_minutes: number;
  estimated_risk_level: "LOW_ESTIMATED_RISK" | "MODERATE_ESTIMATED_RISK" | "HIGH_ESTIMATED_RISK" | "UNKNOWN";
  risk_score: number;
  hazard_factors: string[];
  coordinates: [number, number][]; // [lat, lng]
  is_recommended: boolean;
  recommendation_rationale: string;
  data_freshness_warning?: string;
}

export interface RouteRecommendationResponse {
  origin: RoutePoint;
  destination: RoutePoint;
  requested_preference: string;
  candidates_count: number;
  routes: RouteSegment[];
  disclaimer: string;
}

export interface LiveWeather {
  source: string;
  status: string;
  city: string;
  temperature_c: number;
  humidity_percent: number;
  current_precipitation_mm: number;
  rainfall_1h_mm: number;
  rainfall_3h_mm: number;
  rainfall_6h_mm: number;
  rainfall_24h_mm: number;
  wind_speed_kmh: number;
  timestamp: string;
  disclaimer: string;
}

export interface DashboardSummary {
  metrics: {
    total_incidents: number;
    verified_waterlogging_incidents: number;
    unverified_citizen_reports: number;
    active_road_closures: number;
    chronic_hotspots: number;
    high_risk_locations: number;
    medium_risk_locations: number;
    total_predictions_served: number;
  };
  live_weather: LiveWeather;
  system_status: Record<string, string>;
  last_updated: string;
}

export interface MapsConfig {
  google_maps_api_key: string;
  default_center: Coordinates;
  default_zoom: number;
  provider: string;
}
