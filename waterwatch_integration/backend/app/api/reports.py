"""
WaterWatch AI Integration - Citizen Reporting & Administrative Review API Router
"""

import os
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Header
from sqlalchemy.orm import Session
from waterwatch_integration.backend.app.config import settings, UPLOADS_DIR
from waterwatch_integration.backend.app.database.connection import get_db
from waterwatch_integration.backend.app.database.models import CitizenReport, Incident
from waterwatch_integration.backend.app.schemas.reports import CitizenReportCreate, CitizenReportReview, CitizenReportResponse

router = APIRouter(tags=["Citizen Reports & Review"])


@router.post("/reports")
async def submit_citizen_report(
    location_name: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    description: str = Form(...),
    estimated_severity: str = Form("Moderate"),
    water_depth_cm: Optional[float] = Form(None),
    reporter_name: Optional[str] = Form("Anonymous Citizen"),
    reporter_contact: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Submits a new citizen waterlogging incident report.
    Defaults to UNVERIFIED status.
    """
    if not (15.0 <= latitude <= 25.0 and 70.0 <= longitude <= 85.0):
        raise HTTPException(status_code=400, detail="Coordinates must be within Maharashtra bounds")

    image_filename = None
    if image and image.filename:
        # Check extension
        ext = image.filename.split(".")[-1].lower()
        if ext not in ["jpg", "jpeg", "png", "webp"]:
            raise HTTPException(status_code=400, detail="Only JPG, JPEG, PNG, and WEBP images are supported")

        # Save to uploads directory
        unique_name = f"{uuid.uuid4().hex[:12]}_{image.filename}"
        dest_path = UPLOADS_DIR / unique_name
        contents = await image.read()
        with open(dest_path, "wb") as f:
            f.write(contents)
        image_filename = unique_name

    report_code = f"REP-NGP-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    new_report = CitizenReport(
        report_code=report_code,
        location_name=location_name,
        latitude=latitude,
        longitude=longitude,
        description=description,
        estimated_severity=estimated_severity,
        water_depth_cm=water_depth_cm,
        image_filename=image_filename,
        reporter_name=reporter_name or "Anonymous Citizen",
        reporter_contact=reporter_contact,
        verification_status="UNVERIFIED",
        created_at=datetime.utcnow()
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return {
        "success": True,
        "report_code": new_report.report_code,
        "report_id": new_report.id,
        "location_name": new_report.location_name,
        "message": "Citizen incident report submitted successfully. Stored as UNVERIFIED pending authority review.",
        "verification_status": new_report.verification_status,
        "created_at": new_report.created_at.isoformat()
    }



@router.get("/reports")
def list_citizen_reports(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lists citizen reports with optional status filtering."""
    query = db.query(CitizenReport)
    if status:
        query = query.filter(CitizenReport.verification_status == status.upper())
    reports = query.order_by(CitizenReport.created_at.desc()).all()

    return [
        {
            "id": r.id,
            "report_code": r.report_code,
            "location_name": r.location_name,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "description": r.description,
            "estimated_severity": r.estimated_severity,
            "water_depth_cm": r.water_depth_cm,
            "image_filename": r.image_filename,
            "image_url": f"/api/v1/uploads/{r.image_filename}" if r.image_filename else None,
            "verification_status": r.verification_status,
            "reviewer_notes": r.reviewer_notes,
            "reviewed_by": r.reviewed_by,
            "reviewed_at": r.reviewed_at.isoformat() if r.reviewed_at else None,
            "created_at": r.created_at.isoformat()
        }
        for r in reports
    ]


@router.get("/reports/{report_id}")
def get_citizen_report(report_id: int, db: Session = Depends(get_db)):
    """Retrieves a single citizen report by ID."""
    r = db.query(CitizenReport).filter(CitizenReport.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "id": r.id,
        "report_code": r.report_code,
        "location_name": r.location_name,
        "latitude": r.latitude,
        "longitude": r.longitude,
        "description": r.description,
        "estimated_severity": r.estimated_severity,
        "water_depth_cm": r.water_depth_cm,
        "image_filename": r.image_filename,
        "image_url": f"/api/v1/uploads/{r.image_filename}" if r.image_filename else None,
        "verification_status": r.verification_status,
        "reviewer_notes": r.reviewer_notes,
        "reviewed_by": r.reviewed_by,
        "reviewed_at": r.reviewed_at.isoformat() if r.reviewed_at else None,
        "created_at": r.created_at.isoformat()
    }


@router.patch("/reports/{report_id}/review")
def review_citizen_report(
    report_id: int,
    payload: CitizenReportReview,
    db: Session = Depends(get_db)
):
    """
    Administrative review endpoint for verifying or rejecting citizen reports.
    Requires valid admin authentication token.
    """
    # Verify Admin Token
    if payload.admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid administrative credentials")

    report = db.query(CitizenReport).filter(CitizenReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    status_map = {
        "VERIFY": "VERIFIED",
        "REJECT": "REJECTED",
        "REQUEST_INFO": "INFO_REQUESTED"
    }
    new_status = status_map.get(payload.action, "UNVERIFIED")

    report.verification_status = new_status
    report.reviewer_notes = payload.reviewer_notes
    report.reviewed_by = "Authorized Municipal Officer"
    report.reviewed_at = datetime.utcnow()

    # If verified, optionally add to verified Incidents list
    if new_status == "VERIFIED":
        inc_code = f"INC-REP-{report.report_code}"
        existing = db.query(Incident).filter(Incident.incident_code == inc_code).first()
        if not existing:
            verified_inc = Incident(
                incident_code=inc_code,
                title=f"Verified Report: {report.location_name}",
                location_name=report.location_name,
                latitude=report.latitude,
                longitude=report.longitude,
                severity=report.estimated_severity,
                water_depth_cm=report.water_depth_cm,
                is_verified=True,
                source=f"Citizen Verification ({report.report_code})",
                status="Active"
            )
            db.add(verified_inc)

    db.commit()
    db.refresh(report)

    return {
        "success": True,
        "report_id": report.id,
        "report_code": report.report_code,
        "new_status": report.verification_status,
        "verification_status": report.verification_status,
        "reviewed_by": report.reviewed_by,
        "reviewed_at": report.reviewed_at.isoformat(),
        "notes": report.reviewer_notes
    }
