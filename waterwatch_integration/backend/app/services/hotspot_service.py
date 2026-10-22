"""
WaterWatch AI Integration - Historical Hotspots & Spatial Aggregation Service
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from waterwatch_integration.backend.app.database.models import HistoricalHotspot, Incident


class HotspotAnalyticsService:
    """Summarizes chronic waterlogging hotspots and historical severity."""

    def get_hotspots_summary(self, db: Session) -> Dict[str, Any]:
        hotspots = db.query(HistoricalHotspot).all()
        incidents = db.query(Incident).all()

        total_hotspots = len(hotspots)
        chronic_incidents_recorded = sum(h.incident_count_last_5yr for h in hotspots)

        locality_breakdown = {}
        for h in hotspots:
            locality_breakdown[h.locality] = locality_breakdown.get(h.locality, 0) + h.incident_count_last_5yr

        return {
            "total_chronic_hotspots": total_hotspots,
            "total_recorded_historical_incidents": chronic_incidents_recorded,
            "locality_breakdown": locality_breakdown,
            "chronic_locations": [
                {
                    "hotspot_code": h.hotspot_code,
                    "name": h.name,
                    "locality": h.locality,
                    "coordinates": [h.latitude, h.longitude],
                    "incident_count_last_5yr": h.incident_count_last_5yr,
                    "chronic_cause": h.chronic_cause,
                    "average_depth_cm": h.average_depth_cm,
                    "drainage_capacity_proxy": h.drainage_capacity_proxy
                }
                for h in hotspots
            ],
            "data_provenance": "Nagpur Municipal Corporation Historical Flooding Survey & Field Audit"
        }


hotspot_service = HotspotAnalyticsService()
