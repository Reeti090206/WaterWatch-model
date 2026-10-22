"""Schemas package for WaterWatch Integration"""
from .common import HealthResponse, IncidentResponse, HistoricalHotspotResponse, RoadClosureResponse, Coordinates
from .reports import CitizenReportCreate, CitizenReportReview, CitizenReportResponse
from .predictions import RainfallPredictionRequest, RainfallPredictionResponse
from .routing import RoutePoint, RouteRecommendationRequest, RouteSegment, RouteRecommendationResponse
