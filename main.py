"""
VeriHire AI – Resume & Certificate Verification System
======================================================
Modern, enterprise-grade AI recruitment platform with resume parsing,
certificate detection, authenticity verification, explainable AI,
and recruiter interview management.
"""

import os
import sys
import uuid
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Request, Body
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# Ensure project root in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config
from backend.database import (
    init_db,
    get_db,
    User,
    Candidate,
    Resume,
    Certificate,
    VerificationResult,
    Interview,
    VerificationLog,
    Notification,
    log_event
)
from backend.ai_pipeline import ai_pipeline

# Initialize Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [VeriHire AI] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "verihire.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("VeriHireAI")

# FastAPI App Instance
app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_SUBTITLE,
    version="2.0.0"
)

# Static & Templates setup
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"
static_dir.mkdir(parents=True, exist_ok=True)
templates_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# Jinja2 Custom Filters
def filter_from_json(value):
    if not value:
        return []
    try:
        return json.loads(value)
    except Exception:
        return []

def filter_escapejs(val):
    if not val:
        return "{}"
    return str(val).replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")

templates.env.filters["from_json"] = filter_from_json
templates.env.filters["escapejs"] = filter_escapejs


@app.on_event("startup")
def on_startup():
    """Initializes SQLite database and seeds default 4 demo candidates."""
    init_db()
    logger.info("VeriHire AI Database and Demo Candidates initialized successfully.")
    log_event("SYSTEM_STARTUP", "VeriHire AI SaaS Application engine started.", {"demo_mode": config.DEMO_MODE})


# ============================================================================
# WEB PAGES / HTML ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
def page_landing(request: Request, db: Session = Depends(get_db)):
    """Public SaaS Landing Page."""
    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context={
            "app_name": config.APP_NAME,
            "tagline": config.APP_TAGLINE,
            "subtitle": config.APP_SUBTITLE
        }
    )


@app.get("/login", response_class=HTMLResponse)
@app.get("/signup", response_class=HTMLResponse)
def page_auth(request: Request):
    """Recruiter Login and Signup."""
    return templates.TemplateResponse(
        request=request,
        name="auth.html",
        context={}
    )


@app.get("/dashboard", response_class=HTMLResponse)
def page_dashboard(request: Request, db: Session = Depends(get_db)):
    """Enterprise Recruiter Dashboard."""
    candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).all()
    
    total_candidates = len(candidates)
    verified_count = sum(1 for c in candidates if c.verification_status == "VERIFIED")
    manual_count = sum(1 for c in candidates if c.verification_status in ["NEEDS MANUAL VERIFICATION", "SUSPICIOUS"])
    high_risk_count = sum(1 for c in candidates if c.risk_level == "HIGH" or c.verification_status == "INVALID / FAKE")
    
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "candidates": candidates,
            "total_candidates": total_candidates,
            "verified_count": verified_count,
            "manual_count": manual_count,
            "high_risk_count": high_risk_count,
            "manual_queue_count": manual_count
        }
    )


@app.get("/candidates", response_class=HTMLResponse)
def page_candidates(request: Request, db: Session = Depends(get_db)):
    """Candidate Directory & Credential Roster."""
    candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).all()
    manual_count = sum(1 for c in candidates if c.verification_status in ["NEEDS MANUAL VERIFICATION", "SUSPICIOUS"])

    return templates.TemplateResponse(
        request=request,
        name="candidates.html",
        context={
            "candidates": candidates,
            "manual_queue_count": manual_count
        }
    )


@app.get("/upload", response_class=HTMLResponse)
def page_upload(request: Request, db: Session = Depends(get_db)):
    """Resume Upload and AI analysis launcher."""
    manual_count = db.query(Candidate).filter(Candidate.verification_status.in_(["NEEDS MANUAL VERIFICATION", "SUSPICIOUS"])).count()
    return templates.TemplateResponse(
        request=request,
        name="upload.html",
        context={
            "manual_queue_count": manual_count
        }
    )


@app.get("/candidate/{candidate_id}", response_class=HTMLResponse)
def page_candidate_profile(candidate_id: int, request: Request, db: Session = Depends(get_db)):
    """Deep Candidate Profile & Certificate Verification."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        # Fallback to first candidate if not found
        candidate = db.query(Candidate).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found.")

    resume = candidate.resumes[0] if candidate.resumes else None
    certificates = []
    if resume and resume.certificates:
        certificates = resume.certificates
    elif candidate.resumes:
        certificates = candidate.resumes[0].certificates

    skills = json.loads(resume.extracted_skills) if resume and resume.extracted_skills else []
    education = json.loads(resume.extracted_education) if resume and resume.extracted_education else []
    experience = json.loads(resume.extracted_experience) if resume and resume.extracted_experience else []
    risk_factors = json.loads(candidate.risk_factors_json) if candidate.risk_factors_json else {}

    interviews = candidate.interviews or []
    manual_count = db.query(Candidate).filter(Candidate.verification_status.in_(["NEEDS MANUAL VERIFICATION", "SUSPICIOUS"])).count()

    return templates.TemplateResponse(
        request=request,
        name="candidate_profile.html",
        context={
            "candidate": candidate,
            "resume": resume,
            "certificates": certificates,
            "skills": skills,
            "education": education,
            "experience": experience,
            "risk_factors": risk_factors,
            "interviews": interviews,
            "manual_queue_count": manual_count
        }
    )


@app.get("/verification-queue", response_class=HTMLResponse)
def page_verification_queue(request: Request, db: Session = Depends(get_db)):
    """Human-in-the-Loop Recruiter Review Queue."""
    candidates_with_issues = db.query(Candidate).filter(
        Candidate.verification_status.in_(["NEEDS MANUAL VERIFICATION", "SUSPICIOUS", "INVALID / FAKE"])
    ).all()

    queue_items = []
    for cand in candidates_with_issues:
        for r in cand.resumes:
            for cert in r.certificates:
                if cert.verification_result and cert.verification_result.status in ["NEEDS MANUAL VERIFICATION", "SUSPICIOUS", "INVALID / FAKE"]:
                    queue_items.append({
                        "candidate": cand,
                        "certificate": cert,
                        "result": cert.verification_result
                    })

    manual_count = len(queue_items)

    return templates.TemplateResponse(
        request=request,
        name="verification_queue.html",
        context={
            "queue_items": queue_items,
            "manual_queue_count": manual_count
        }
    )


@app.get("/interviews", response_class=HTMLResponse)
def page_interviews(request: Request, db: Session = Depends(get_db)):
    """Interview Management & Scheduling."""
    interviews = db.query(Interview).order_by(Interview.scheduled_at.desc()).all()
    candidates = db.query(Candidate).all()
    scheduled_count = sum(1 for i in interviews if i.status == "SCHEDULED")
    pending_count = sum(1 for i in interviews if i.status == "PENDING")
    manual_count = db.query(Candidate).filter(Candidate.verification_status.in_(["NEEDS MANUAL VERIFICATION", "SUSPICIOUS"])).count()

    return templates.TemplateResponse(
        request=request,
        name="interviews.html",
        context={
            "interviews": interviews,
            "candidates": candidates,
            "scheduled_count": scheduled_count,
            "pending_count": pending_count,
            "manual_queue_count": manual_count
        }
    )


@app.get("/analytics", response_class=HTMLResponse)
def page_analytics(request: Request, db: Session = Depends(get_db)):
    """Recruitment Analytics & Fraud Telemetry."""
    manual_count = db.query(Candidate).filter(Candidate.verification_status.in_(["NEEDS MANUAL VERIFICATION", "SUSPICIOUS"])).count()
    return templates.TemplateResponse(
        request=request,
        name="analytics.html",
        context={
            "manual_queue_count": manual_count
        }
    )


@app.get("/report/{target_id}", response_class=HTMLResponse)
def page_report(target_id: str, request: Request, db: Session = Depends(get_db)):
    """Formal Printable & Downloadable Candidate Verification Report."""
    candidate = None
    resume = None

    # Try matching candidate ID first
    if target_id.isdigit():
        candidate = db.query(Candidate).filter(Candidate.id == int(target_id)).first()
        if candidate and candidate.resumes:
            resume = candidate.resumes[0]
    else:
        # Match by resume UUID
        resume = db.query(Resume).filter(Resume.id == target_id).first()
        if resume:
            candidate = resume.candidate

    if not candidate:
        candidate = db.query(Candidate).first()
        if candidate and candidate.resumes:
            resume = candidate.resumes[0]

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate record not found.")

    certificates = resume.certificates if resume else []
    skills = json.loads(resume.extracted_skills) if resume and resume.extracted_skills else []

    return templates.TemplateResponse(
        request=request,
        name="report.html",
        context={
            "candidate": candidate,
            "resume": resume,
            "certificates": certificates,
            "skills": skills,
            "now": datetime.utcnow()
        }
    )


@app.get("/security", response_class=HTMLResponse)
def page_security(request: Request, db: Session = Depends(get_db)):
    """Security & Privacy Governance."""
    logs = db.query(VerificationLog).order_by(VerificationLog.created_at.desc()).limit(20).all()
    manual_count = db.query(Candidate).filter(Candidate.verification_status.in_(["NEEDS MANUAL VERIFICATION", "SUSPICIOUS"])).count()
    return templates.TemplateResponse(
        request=request,
        name="security.html",
        context={
            "logs": logs,
            "manual_queue_count": manual_count
        }
    )


@app.get("/settings", response_class=HTMLResponse)
def page_settings(request: Request, db: Session = Depends(get_db)):
    """Settings Configuration."""
    manual_count = db.query(Candidate).filter(Candidate.verification_status.in_(["NEEDS MANUAL VERIFICATION", "SUSPICIOUS"])).count()
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "manual_queue_count": manual_count
        }
    )


# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.post("/api/upload-resume")
async def api_upload_resume(
    file: UploadFile = File(...),
    cert_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Receives resume file, executes the 6-stage AI pipeline,
    and returns redirect URL to the candidate's deep profile.
    """
    filename = file.filename or "resume.pdf"
    file_ext = Path(filename).suffix.lower()

    if file_ext not in config.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{file_ext}'. Please upload PDF, DOC, or DOCX.")

    resume_uuid = str(uuid.uuid4())
    save_path = config.UPLOADS_DIR / f"{resume_uuid}_{filename}"

    contents = await file.read()
    with open(save_path, "wb") as f:
        f.write(contents)

    # Execute full AI Pipeline
    pipeline_result = ai_pipeline.process_resume(save_path)

    # Create and persist Candidate
    candidate = Candidate(
        name=pipeline_result["candidate_name"],
        email=pipeline_result["email"],
        phone=pipeline_result["phone"],
        location=pipeline_result["location"],
        position="Senior Software Engineer",
        overall_resume_score=pipeline_result["overall_resume_score"],
        skills_match_score=pipeline_result["skills_match_score"],
        experience_match_score=pipeline_result["experience_match_score"],
        education_match_score=pipeline_result["education_match_score"],
        consistency_score=pipeline_result["consistency_score"],
        risk_score=pipeline_result["risk_score"],
        risk_level=pipeline_result["risk_level"],
        risk_factors_json=json.dumps(pipeline_result["risk_factors"]),
        verification_status=pipeline_result["verification_status"],
        recruiter_decision="NONE",
        interview_status="NOT_SCHEDULED"
    )
    db.add(candidate)
    db.flush()

    # Create and persist Resume
    resume_obj = Resume(
        id=resume_uuid,
        candidate_id=candidate.id,
        filename=filename,
        file_type=file_ext,
        file_size_bytes=len(contents),
        raw_text=pipeline_result["raw_text"],
        extracted_skills=json.dumps(pipeline_result["skills"]),
        extracted_education=json.dumps(pipeline_result["education"]),
        extracted_experience=json.dumps(pipeline_result["experience"]),
        extracted_projects=json.dumps(pipeline_result["projects"]),
        summary="Ingested and verified via VeriHire AI Pipeline."
    )
    db.add(resume_obj)

    # Persist Certificates & Verification Results
    for cert_data in pipeline_result["certificates"]:
        cert_rec = Certificate(
            resume_id=resume_uuid,
            candidate_name=candidate.name,
            certificate_name=cert_data["certificate_name"],
            certificate_id=cert_data["certificate_id"],
            issuing_organization=cert_data["issuing_organization"],
            issue_date=cert_data["issue_date"],
            expiry_date=cert_data.get("expiry_date", "N/A"),
            verification_url=cert_data.get("verification_url", "")
        )
        db.add(cert_rec)
        db.flush()

        vr = VerificationResult(
            certificate_id=cert_rec.id,
            status=cert_data["status"],
            authenticity_score=cert_data["authenticity_score"],
            ai_confidence=cert_data["ai_confidence"],
            id_format_valid=cert_data["id_format_valid"],
            issuing_org_verified=cert_data["issuing_org_verified"],
            name_match=cert_data["name_match"],
            date_consistency=cert_data["date_consistency"],
            qr_url_verified=cert_data["qr_url_verified"],
            digital_signature_valid=cert_data["digital_signature_valid"],
            metadata_consistent=cert_data["metadata_consistent"],
            tampering_detected=cert_data["tampering_detected"],
            verification_source=cert_data["verification_source"],
            details=cert_data["details"],
            ai_explanation=cert_data["ai_explanation"],
            detected_issues_json=json.dumps(cert_data.get("detected_issues", [])),
            official_record_json=json.dumps(cert_data.get("official_record", {})),
            evidence_diff_json=json.dumps(cert_data.get("evidence_diff", {}))
        )
        db.add(vr)

    # Create notification and audit log
    notif = Notification(
        title="Resume Analyzed",
        message=f"{candidate.name}'s resume analyzed: Status {candidate.verification_status} (Score: {candidate.overall_resume_score|round}%)",
        type="success" if candidate.verification_status == "VERIFIED" else "warning",
        link=f"/candidate/{candidate.id}"
    )
    db.add(notif)

    log_event(
        "RESUME_ANALYZED",
        f"Ingested and analyzed {filename} for {candidate.name}.",
        {"candidate_id": candidate.id, "resume_id": resume_uuid},
        candidate_id=candidate.id
    )

    db.commit()

    return {
        "status": "success",
        "candidate_id": candidate.id,
        "resume_id": resume_uuid,
        "candidate_name": candidate.name,
        "redirect_url": f"/candidate/{candidate.id}"
    }


@app.post("/api/candidate/{candidate_id}/decision")
def api_candidate_decision(
    candidate_id: int,
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Sets recruiter decision: SHORTLISTED, VERIFICATION_REQUESTED, REJECTED, SAVED."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    decision = payload.get("decision", "NONE")
    candidate.recruiter_decision = decision

    if decision == "SHORTLISTED":
        if candidate.interview_status == "NOT_SCHEDULED":
            candidate.interview_status = "PENDING"
    elif decision == "REJECTED":
        candidate.interview_status = "CANCELLED"

    log_event("RECRUITER_DECISION", f"Recruiter set decision '{decision}' for {candidate.name}", candidate_id=candidate.id)
    db.commit()

    return {"status": "success", "candidate_id": candidate.id, "decision": decision}


@app.post("/api/candidate/{candidate_id}/verify-manual")
def api_candidate_manual_verify(candidate_id: int, db: Session = Depends(get_db)):
    """Overrides candidate credential status to VERIFIED by human recruiter authority."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    candidate.verification_status = "VERIFIED"
    candidate.risk_level = "LOW"
    candidate.risk_score = 10.0

    # Also update certificates
    for r in candidate.resumes:
        for c in r.certificates:
            if c.verification_result:
                c.verification_result.status = "VERIFIED"
                c.verification_result.authenticity_score = 95.0
                c.verification_result.ai_explanation = "Manually confirmed and approved by recruiter audit override."

    log_event("MANUAL_VERIFY_OVERRIDE", f"Recruiter manually verified all credentials for {candidate.name}", candidate_id=candidate.id)
    db.commit()

    return {"status": "success", "message": "Candidate verified manually."}


@app.post("/api/candidate/{candidate_id}/schedule-interview")
def api_schedule_interview(
    candidate_id: int,
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Schedules an interview round for the candidate."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    interview_type = payload.get("interview_type", "Technical Screening Round")
    interviewer_name = payload.get("interviewer_name", "Sarah Jenkins")
    scheduled_at_str = payload.get("scheduled_at")
    notes = payload.get("notes", "")

    try:
        scheduled_at = datetime.fromisoformat(scheduled_at_str) if scheduled_at_str else datetime.utcnow()
    except Exception:
        scheduled_at = datetime.utcnow()

    inv = Interview(
        candidate_id=candidate.id,
        interview_type=interview_type,
        interviewer_name=interviewer_name,
        scheduled_at=scheduled_at,
        status="SCHEDULED",
        notes=notes,
        meeting_link=f"https://meet.google.com/vh-{uuid.uuid4().hex[:6]}"
    )
    db.add(inv)

    candidate.interview_status = "SCHEDULED"
    candidate.recruiter_decision = "SHORTLISTED"

    notif = Notification(
        title="Interview Scheduled",
        message=f"{interview_type} scheduled with {candidate.name} ({scheduled_at.strftime('%b %d')}).",
        type="info",
        link="/interviews"
    )
    db.add(notif)

    log_event("INTERVIEW_SCHEDULED", f"Scheduled {interview_type} for {candidate.name}", candidate_id=candidate.id)
    db.commit()

    return {"status": "success", "interview_id": inv.id}


@app.get("/health")
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "app": config.APP_NAME,
        "tagline": config.APP_TAGLINE,
        "demo_mode": config.DEMO_MODE,
        "database": "SQLite / SQLAlchemy ORM",
        "timestamp": datetime.utcnow().isoformat()
    }
