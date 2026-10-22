"""
WaterWatch AI Integration - SQLAlchemy Database Models
Isolated schemas for Incidents, Citizen Reports, Hotspots, Road Closures, and Prediction Records.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from waterwatch_integration.backend.app.database.connection import Base, engine, SessionLocal


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_code = Column(String(50), unique=True, index=True)
    title = Column(String(200), nullable=False)
    location_name = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    severity = Column(String(50), default="Moderate")  # Low, Moderate, High, Critical
    water_depth_cm = Column(Float, nullable=True)
    is_verified = Column(Boolean, default=True)
    source = Column(String(100), default="NMC Control Room")
    status = Column(String(50), default="Active")  # Active, Receding, Resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CitizenReport(Base):
    __tablename__ = "citizen_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_code = Column(String(50), unique=True, index=True)
    location_name = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    estimated_severity = Column(String(50), default="Moderate")
    water_depth_cm = Column(Float, nullable=True)
    image_filename = Column(String(255), nullable=True)
    reporter_name = Column(String(100), default="Anonymous Citizen")
    reporter_contact = Column(String(100), nullable=True)
    verification_status = Column(String(50), default="UNVERIFIED")  # UNVERIFIED, VERIFIED, REJECTED
    reviewer_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class HistoricalHotspot(Base):
    __tablename__ = "historical_hotspots"

    id = Column(Integer, primary_key=True, index=True)
    hotspot_code = Column(String(50), unique=True, index=True)
    name = Column(String(200), nullable=False)
    locality = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    incident_count_last_5yr = Column(Integer, default=10)
    chronic_cause = Column(String(255), nullable=False)
    average_depth_cm = Column(Float, default=25.0)
    drainage_capacity_proxy = Column(Float, default=0.45)
    typical_critical_threshold_mm = Column(Float, default=30.0)


class RoadClosure(Base):
    __tablename__ = "road_closures"

    id = Column(Integer, primary_key=True, index=True)
    closure_code = Column(String(50), unique=True, index=True)
    road_name = Column(String(200), nullable=False)
    locality = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    reason = Column(String(255), default="Severe Waterlogging Hazard")
    status = Column(String(50), default="Active")  # Active, Lifted
    reported_at = Column(DateTime, default=datetime.utcnow)


class PredictionAudit(Base):
    __tablename__ = "prediction_audits"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100), default="Nagpur")
    rainfall_1h_mm = Column(Float, nullable=False)
    rainfall_24h_mm = Column(Float, nullable=False)
    predicted_class = Column(Integer, nullable=False)
    predicted_probability = Column(Float, nullable=False)
    risk_category = Column(String(50), nullable=False)
    model_name = Column(String(100), default="LogisticRegression")
    training_data_status = Column(String(50), default="SYNTHETIC_EXPERIMENTAL")
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Initializes schema and pre-populates Nagpur landmark reference hotspots."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Pre-populate historical chronic hotspots in Nagpur if empty
    if db.query(HistoricalHotspot).count() == 0:
        seed_hotspots = [
            HistoricalHotspot(
                hotspot_code="HOT-NGP-001",
                name="Narendra Nagar Railway Underbridge (RUB)",
                locality="Manish Nagar / Narendra Nagar",
                latitude=21.1078,
                longitude=79.0765,
                incident_count_last_5yr=48,
                chronic_cause="Depressed topography beneath railway track with severe stormwater runoff collection",
                average_depth_cm=55.0,
                drainage_capacity_proxy=0.25,
                typical_critical_threshold_mm=20.0
            ),
            HistoricalHotspot(
                hotspot_code="HOT-NGP-002",
                name="Mor Bhavan Bus Stand Square",
                locality="Sitabuldi",
                latitude=21.1442,
                longitude=79.0831,
                incident_count_last_5yr=32,
                chronic_cause="High impervious commercial density and Nag River runoff backflow",
                average_depth_cm=35.0,
                drainage_capacity_proxy=0.40,
                typical_critical_threshold_mm=25.0
            ),
            HistoricalHotspot(
                hotspot_code="HOT-NGP-003",
                name="Law College Square - Amravati Road",
                locality="Dharampeth",
                latitude=21.1487,
                longitude=79.0624,
                incident_count_last_5yr=26,
                chronic_cause="Inadequate storm pipe diameters and slope convergence from West Nagpur hills",
                average_depth_cm=28.0,
                drainage_capacity_proxy=0.55,
                typical_critical_threshold_mm=30.0
            ),
            HistoricalHotspot(
                hotspot_code="HOT-NGP-004",
                name="Sadar Residency Road - Mount Road Junction",
                locality="Sadar",
                latitude=21.1601,
                longitude=79.0818,
                incident_count_last_5yr=21,
                chronic_cause="Clogged masonry culverts and commercial runoff pooling",
                average_depth_cm=22.0,
                drainage_capacity_proxy=0.50,
                typical_critical_threshold_mm=35.0
            ),
            HistoricalHotspot(
                hotspot_code="HOT-NGP-005",
                name="Mankapur Ring Road Flyover Base",
                locality="Mankapur",
                latitude=21.1925,
                longitude=79.0792,
                incident_count_last_5yr=19,
                chronic_cause="Flyover pier catchment discharge pooling on outer ring road surface",
                average_depth_cm=30.0,
                drainage_capacity_proxy=0.48,
                typical_critical_threshold_mm=30.0
            ),
            HistoricalHotspot(
                hotspot_code="HOT-NGP-006",
                name="Dhantoli Panchsheel Square Subway",
                locality="Dhantoli",
                latitude=21.1378,
                longitude=79.0838,
                incident_count_last_5yr=35,
                chronic_cause="Nag River bank proximity and low-lying arterial transit junction",
                average_depth_cm=42.0,
                drainage_capacity_proxy=0.35,
                typical_critical_threshold_mm=22.0
            )
        ]
        db.add_all(seed_hotspots)

    # Pre-populate sample verified incidents
    if db.query(Incident).count() == 0:
        seed_incidents = [
            Incident(
                incident_code="INC-NGP-2026-001",
                title="Severe Water Accumulation at Narendra Nagar RUB",
                location_name="Narendra Nagar Railway Underbridge",
                latitude=21.1078,
                longitude=79.0765,
                severity="Critical",
                water_depth_cm=48.0,
                is_verified=True,
                source="Traffic Police Advisory",
                status="Active"
            ),
            Incident(
                incident_code="INC-NGP-2026-002",
                title="Moderate Roadway Flooding near Panchsheel Cinema",
                location_name="Wardha Road - Dhantoli Junction",
                latitude=21.1375,
                longitude=79.0832,
                severity="Moderate",
                water_depth_cm=20.0,
                is_verified=True,
                source="NMC Field Inspection",
                status="Active"
            )
        ]
        db.add_all(seed_incidents)

    # Pre-populate active road closure
    if db.query(RoadClosure).count() == 0:
        seed_closures = [
            RoadClosure(
                closure_code="CLS-NGP-001",
                road_name="Narendra Nagar Underpass Arterial Link",
                locality="Manish Nagar",
                latitude=21.1078,
                longitude=79.0765,
                reason="Submerged railway underbridge (48 cm standing water)",
                status="Active"
            )
        ]
        db.add_all(seed_closures)

    db.commit()
    db.close()
