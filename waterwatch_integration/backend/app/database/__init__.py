"""Database package for WaterWatch Integration"""
from .connection import Base, engine, SessionLocal, get_db
from .models import Incident, CitizenReport, HistoricalHotspot, RoadClosure, PredictionAudit, init_db
