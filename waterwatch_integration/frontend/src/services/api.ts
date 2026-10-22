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
  MapsConfig,
} from "../types";

const getBaseUrl = (): string => {
  if (typeof window === "undefined") {
    return process.env.FASTAPI_BACKEND_URL || "http://127.0.0.1:8080/api/v1";
  }
  return process.env.NEXT_PUBLIC_API_URL || "/api/v1";
};

class ApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const baseUrl = getBaseUrl();
    const url = `${baseUrl}${endpoint}`;

    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
    };

    if (!(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorDetail = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errJson = await response.json();
        if (errJson && errJson.detail) {
          errorDetail = errJson.detail;
        }
      } catch {
        // use default error detail
      }
      throw new Error(errorDetail);
    }

    return response.json();
  }

  public async getMapsConfig(): Promise<MapsConfig> {
    return this.request<MapsConfig>("/config/maps");
  }

  public async getDashboardSummary(): Promise<DashboardSummary> {
    return this.request<DashboardSummary>("/dashboard/summary");
  }

  public async getIncidents(): Promise<Incident[]> {
    return this.request<Incident[]>("/incidents");
  }

  public async getHotspots(): Promise<HistoricalHotspot[]> {
    return this.request<HistoricalHotspot[]>("/hotspots");
  }

  public async getRoadClosures(): Promise<RoadClosure[]> {
    return this.request<RoadClosure[]>("/road-closures");
  }

  public async getCitizenReports(status?: string): Promise<CitizenReport[]> {
    const query = status ? `?status=${encodeURIComponent(status)}` : "";
    return this.request<CitizenReport[]>(`/reports${query}`);
  }

  public async submitCitizenReport(formData: FormData): Promise<any> {
    return this.request<any>("/reports", {
      method: "POST",
      body: formData,
    });
  }

  public async reviewCitizenReport(
    reportId: number,
    action: "VERIFY" | "REJECT" | "REQUEST_INFO",
    notes: string,
    adminToken: string
  ): Promise<any> {
    return this.request<any>(`/reports/${reportId}/review`, {
      method: "PATCH",
      body: JSON.stringify({
        action,
        reviewer_notes: notes,
        admin_token: adminToken,
      }),
    });
  }

  public async predictRainfallRisk(payload: RainfallPredictionRequest): Promise<RainfallPredictionResponse> {
    return this.request<RainfallPredictionResponse>("/predictions/rainfall", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  public async detectWaterloggingInImage(formData: FormData): Promise<ImageDetectionResponse> {
    return this.request<ImageDetectionResponse>("/detection/image", {
      method: "POST",
      body: formData,
    });
  }

  public async recommendRoutes(payload: any): Promise<RouteRecommendationResponse> {
    return this.request<RouteRecommendationResponse>("/routes/recommend", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  public async getModelsStatus(): Promise<any> {
    return this.request<any>("/models/status");
  }

  public async getPredictionTable(rainMultiplier: number = 1.0): Promise<any> {
    return this.request<any>(`/predictions/table?rain_multiplier=${rainMultiplier}`);
  }
}

export const api = new ApiService();
