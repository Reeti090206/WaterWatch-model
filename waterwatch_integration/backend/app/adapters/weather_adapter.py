"""
Live Weather Adapter for Nagpur
Fetches real-time observations and forecasts from Open-Meteo API.
Provides transparent fallback if offline or API is unreachable.
Zero modifications outside waterwatch_integration/.
"""

import requests
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger("waterwatch.weather")

class WeatherAdapter:
    NAGPUR_LAT = 21.1458
    NAGPUR_LON = 79.0882

    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def get_current_nagpur_weather(self) -> Dict[str, Any]:
        """Fetch current weather for Nagpur with offline fallback."""
        params = {
            "latitude": self.NAGPUR_LAT,
            "longitude": self.NAGPUR_LON,
            "current": "temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,wind_speed_10m",
            "hourly": "precipitation,rain",
            "forecast_days": 1,
            "timezone": "Asia/Kolkata",
        }
        try:
            resp = requests.get(self.base_url, params=params, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current", {})
                hourly = data.get("hourly", {})
                
                precip_history = hourly.get("precipitation", [])
                sum_1h = float(current.get("precipitation", 0.0))
                sum_3h = sum(precip_history[:3]) if len(precip_history) >= 3 else sum_1h
                sum_6h = sum(precip_history[:6]) if len(precip_history) >= 6 else sum_3h
                sum_24h = sum(precip_history) if precip_history else sum_6h

                return {
                    "source": "Open-Meteo Live API",
                    "status": "LIVE",
                    "city": "Nagpur",
                    "latitude": self.NAGPUR_LAT,
                    "longitude": self.NAGPUR_LON,
                    "temperature_c": current.get("temperature_2m"),
                    "humidity_percent": current.get("relative_humidity_2m"),
                    "current_precipitation_mm": current.get("precipitation", 0.0),
                    "rainfall_1h_mm": round(sum_1h, 2),
                    "rainfall_3h_mm": round(sum_3h, 2),
                    "rainfall_6h_mm": round(sum_6h, 2),
                    "rainfall_24h_mm": round(sum_24h, 2),
                    "wind_speed_kmh": current.get("wind_speed_10m"),
                    "timestamp": current.get("time") or datetime.utcnow().isoformat(),
                    "disclaimer": "Live meteorological data from Open-Meteo."
                }
        except Exception as e:
            logger.warning(f"Could not reach live weather API: {e}. Falling back to default offline metrics.")

        # Offline fallback
        return {
            "source": "WaterWatch Offline Fallback Engine",
            "status": "NO LIVE DATA AVAILABLE (OFFLINE MODE)",
            "city": "Nagpur",
            "latitude": self.NAGPUR_LAT,
            "longitude": self.NAGPUR_LON,
            "temperature_c": 28.5,
            "humidity_percent": 82,
            "current_precipitation_mm": 5.2,
            "rainfall_1h_mm": 12.0,
            "rainfall_3h_mm": 28.5,
            "rainfall_6h_mm": 45.0,
            "rainfall_24h_mm": 62.0,
            "wind_speed_kmh": 14.2,
            "timestamp": datetime.utcnow().isoformat(),
            "disclaimer": "Simulated monsoon baseline for Nagpur locality risk evaluation."
        }

    def get_live_weather(self) -> Dict[str, Any]:
        """Alias for get_current_nagpur_weather."""
        return self.get_current_nagpur_weather()

weather_adapter = WeatherAdapter()

