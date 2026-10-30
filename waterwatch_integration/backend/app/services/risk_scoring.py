"""
WaterWatch AI Integration - Route Waterlogging Risk Scoring Algorithm
Computes documented, multi-factor risk scores by spatially intersecting route geometries
with active verified incidents, road closures, chronic hotspots, and citizen reports.
"""

import math
from typing import List, Dict, Any, Tuple


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two GPS coordinates in kilometers."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def min_distance_to_route_km(coord: Tuple[float, float], route_coords: List[List[float]]) -> float:
    """Finds the minimum distance between a hazard point and any point on the route."""
    if not route_coords:
        return float("inf")
    min_dist = float("inf")
    lat, lon = coord
    for pt in route_coords:
        # Check pt format [lat, lon]
        dist = haversine_distance_km(lat, lon, pt[0], pt[1])
        if dist < min_dist:
            min_dist = dist
            if min_dist < 0.05:  # Within 50 meters, immediate intersection
                break
    return min_dist


class RouteRiskScoringEngine:
    """
    Evaluates multi-factor waterlogging risk along route corridors.
    Weights:
    - Active Road Closure (within 200m): +0.90 (immediate detour trigger)
    - Verified Severe Incident (within 300m): +0.65
    - Verified Moderate Incident (within 300m): +0.40
    - Chronic Historical Hotspot (within 250m): +0.30
    - Unverified Citizen Report (within 250m): +0.15 (flagged as unverified signal)
    """

    PROXIMITY_THRESHOLD_KM = 0.35  # 350 meters corridor buffer

    def evaluate_route_risk(
        self,
        route_coords: List[List[float]],
        active_incidents: List[Any],
        road_closures: List[Any],
        historical_hotspots: List[Any],
        citizen_reports: List[Any]
    ) -> Dict[str, Any]:
        """
        Evaluates risk factors along a candidate route.
        """
        if not route_coords or len(route_coords) < 2:
            return {
                "risk_score": 0.0,
                "risk_level": "UNKNOWN",
                "hazard_factors": ["Insufficient route coordinates to evaluate spatial risk"],
                "data_freshness_warning": "Route geometry missing"
            }

        score = 0.0
        hazard_factors = []
        closure_hit = False

        # 1. Check Active Road Closures
        for cls in road_closures:
            dist = min_distance_to_route_km((cls.latitude, cls.longitude), route_coords)
            if dist <= 0.25:
                closure_hit = True
                score += 0.85
                hazard_factors.append(
                    f"ACTIVE ROAD CLOSURE ({round(dist*1000)}m away): '{cls.road_name}' ({cls.reason})"
                )

        # 2. Check Verified Waterlogging Incidents
        for inc in active_incidents:
            dist = min_distance_to_route_km((inc.latitude, inc.longitude), route_coords)
            if dist <= self.PROXIMITY_THRESHOLD_KM:
                weight = 0.60 if inc.severity in ["High", "Critical"] else 0.35
                score += weight
                hazard_factors.append(
                    f"VERIFIED INCIDENT ({round(dist*1000)}m away): '{inc.title}' "
                    f"[Severity: {inc.severity}, Depth: {inc.water_depth_cm or 'Unmeasured'} cm]"
                )

        # 3. Check Chronic Historical Hotspots
        for hot in historical_hotspots:
            dist = min_distance_to_route_km((hot.latitude, hot.longitude), route_coords)
            if dist <= 0.25:
                score += 0.25
                hazard_factors.append(
                    f"CHRONIC HOTSPOT ({round(dist*1000)}m away): '{hot.name}' "
                    f"(Historical: {hot.incident_count_last_5yr} incidents in 5 yrs; Cause: {hot.chronic_cause})"
                )

        # 4. Check Unverified Citizen Reports
        for rep in citizen_reports:
            if rep.verification_status == "UNVERIFIED":
                dist = min_distance_to_route_km((rep.latitude, rep.longitude), route_coords)
                if dist <= 0.25:
                    score += 0.15
                    hazard_factors.append(
                        f"UNVERIFIED CITIZEN REPORT ({round(dist*1000)}m away): '{rep.description[:60]}...' "
                        f"[Reported Severity: {rep.estimated_severity}]"
                    )

        # Bound score to [0.0, 1.0]
        final_score = round(min(score, 1.0), 4)

        # Classify Level
        if final_score < 0.25:
            risk_level = "LOW_ESTIMATED_RISK"
        elif final_score < 0.60:
            risk_level = "MODERATE_ESTIMATED_RISK"
        else:
            risk_level = "HIGH_ESTIMATED_RISK"

        # Determine Rationale
        if closure_hit:
            rationale = "Route traverses or closely bypasses an active physical road closure. Detour strongly recommended."
        elif final_score >= 0.60:
            rationale = "Route corridor encounters multiple severe waterlogging obstacles and chronic runoff points."
        elif final_score >= 0.25:
            rationale = "Route is passable with caution; minor standing water or nearby chronic drainage hotspots detected."
        else:
            rationale = "Route corridor is clear of active closures and severe waterlogging reports."

        return {
            "risk_score": final_score,
            "risk_level": risk_level,
            "hazard_factors": hazard_factors,
            "recommendation_rationale": rationale,
            "data_freshness_warning": None if hazard_factors else "No active municipal waterlogging incidents detected along this corridor."
        }


risk_engine = RouteRiskScoringEngine()
