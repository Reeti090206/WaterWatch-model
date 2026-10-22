/**
 * WaterWatch AI - Typed API Client
 * Interfaces with FastAPI endpoints at /api/v1
 */

import {
  DashboardSummary,
  Incident,
  CitizenReport,
  HistoricalHotspot,
  RoadClosure,
  RainfallPredictionRequest,
  RainfallPredictionResponse,
  ImageDetectionResponse,
  RouteRecommendationResponse,
  MapsConfig
} from "./types";

const BASE_URL = "/api/v1";

class ApiService {
  private async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${BASE_URL}${endpoint}`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `HTTP Error ${response.status}`);
    }
    return response.json();
  }

  private async post<T>(endpoint: string, body: any): Promise<T> {
    const isFormData = body instanceof FormData;
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: "POST",
      headers: isFormData ? undefined : { "Content-Type": "application/json" },
      body: isFormData ? body : JSON.stringify(body)
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `HTTP Error ${response.status}`);
    }
    return response.json();
  }

  private async patch<T>(endpoint: string, body: any): Promise<T> {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `HTTP Error ${response.status}`);
    }
    return response.json();
  }

  public async getMapsConfig(): Promise<MapsConfig> {
    return this.get<MapsConfig>("/config/maps");
  }

  public async getDashboardSummary(): Promise<DashboardSummary> {
    return this.get<DashboardSummary>("/dashboard/summary");
  }

  public async getIncidents(): Promise<Incident[]> {
    return this.get<Incident[]>("/incidents");
  }

  public async getHotspots(): Promise<HistoricalHotspot[]> {
    return this.get<HistoricalHotspot[]>("/hotspots");
  }

  public async getRoadClosures(): Promise<RoadClosure[]> {
    return this.get<RoadClosure[]>("/road-closures");
  }

  public async getCitizenReports(status?: string): Promise<CitizenReport[]> {
    const query = status ? `?status=${encodeURIComponent(status)}` : "";
    return this.get<CitizenReport[]>(`/reports${query}`);
  }

  public async submitCitizenReport(formData: FormData): Promise<any> {
    return this.post<any>("/reports", formData);
  }

  public async reviewCitizenReport(
    reportId: number,
    action: "VERIFY" | "REJECT" | "REQUEST_INFO",
    notes: string,
    adminToken: string
  ): Promise<any> {
    return this.patch<any>(`/reports/${reportId}/review`, {
      action,
      reviewer_notes: notes,
      admin_token: adminToken
    });
  }

  public async predictRainfallRisk(payload: RainfallPredictionRequest): Promise<RainfallPredictionResponse> {
    return this.post<RainfallPredictionResponse>("/predictions/rainfall", payload);
  }

  public async detectWaterloggingInImage(formData: FormData): Promise<ImageDetectionResponse> {
    return this.post<ImageDetectionResponse>("/detection/image", formData);
  }

  public async recommendRoutes(payload: any): Promise<RouteRecommendationResponse> {
    return this.post<RouteRecommendationResponse>("/routes/recommend", payload);
  }

  public async getModelsStatus(): Promise<any> {
    return this.get<any>("/models/status");
  }
}

export const api = new ApiService();
