"""
VeriHire AI – Database & ORM Layer
===================================
Production-quality database module for candidate verification,
resume analysis, certificates, interview scheduling, and enterprise audit logs.
"""

from datetime import datetime
from typing import Generator, List, Dict, Any, Optional
import json
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

import config

engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """Recruiter / HR account user."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(50), default="Senior Technical Recruiter")
    company_name = Column(String(255), default="Enterprise Talent Corp")
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Candidate(Base):
    """Candidate profile with overall scores, verification, and recruitment state."""
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(100), default="San Francisco, CA")
    position = Column(String(255), default="Software Engineer")
    avatar = Column(String(500), nullable=True)

    # AI Scores (0 to 100)
    overall_resume_score = Column(Float, default=85.0)
    skills_match_score = Column(Float, default=88.0)
    experience_match_score = Column(Float, default=82.0)
    education_match_score = Column(Float, default=90.0)
    consistency_score = Column(Float, default=95.0)

    # Risk Assessment
    risk_score = Column(Float, default=15.0)  # 0 to 100
    risk_level = Column(String(20), default="LOW")  # LOW, MEDIUM, HIGH
    risk_factors_json = Column(Text, nullable=True)

    # Verification Status
    # VERIFIED, NEEDS MANUAL VERIFICATION, SUSPICIOUS, INVALID / FAKE
    verification_status = Column(String(50), default="VERIFIED", index=True)

    # Recruiter Pipeline Decision
    # NONE, SHORTLISTED, VERIFICATION_REQUESTED, REJECTED, SAVED
    recruiter_decision = Column(String(50), default="NONE", index=True)
    recruiter_notes = Column(Text, nullable=True)

    # Interview State
    # NOT_SCHEDULED, SCHEDULED, PENDING, COMPLETED, CANCELLED
    interview_status = Column(String(50), default="NOT_SCHEDULED", index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")
    audit_logs = relationship("VerificationLog", back_populates="candidate", cascade="all, delete-orphan")


class Resume(Base):
    """Uploaded candidate resume document with structured AI extractions."""
    __tablename__ = "resumes"

    id = Column(String(64), primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    raw_text = Column(Text, nullable=True)

    # Structured extractions
    extracted_skills = Column(Text, nullable=True)      # JSON serialized list of skills
    extracted_education = Column(Text, nullable=True)   # JSON serialized list of dicts/strings
    extracted_experience = Column(Text, nullable=True)  # JSON serialized list of dicts/strings
    extracted_projects = Column(Text, nullable=True)    # JSON serialized list of dicts/strings
    summary = Column(Text, nullable=True)

    uploaded_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="resumes")
    certificates = relationship("Certificate", back_populates="resume", cascade="all, delete-orphan")


class Certificate(Base):
    """Certificate claim extracted from resume or uploaded separately."""
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(String(64), ForeignKey("resumes.id"), nullable=True, index=True)
    candidate_name = Column(String(255), nullable=True)
    certificate_name = Column(String(255), nullable=False)
    certificate_id = Column(String(100), nullable=True, index=True)
    issuing_organization = Column(String(255), nullable=True)
    issue_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    verification_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="certificates")
    verification_result = relationship("VerificationResult", back_populates="certificate", uselist=False, cascade="all, delete-orphan")


class VerificationResult(Base):
    """Detailed verification audit result and explainable AI insights."""
    __tablename__ = "verification_results"

    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(Integer, ForeignKey("certificates.id"), unique=True, index=True)

    # Status: VERIFIED, NEEDS MANUAL VERIFICATION, SUSPICIOUS, INVALID / FAKE
    status = Column(String(50), nullable=False, index=True)
    authenticity_score = Column(Float, default=0.0)  # 0 to 100
    ai_confidence = Column(Float, default=95.0)      # 0 to 100

    # Verification checklist
    id_format_valid = Column(Boolean, default=True)
    issuing_org_verified = Column(Boolean, default=True)
    name_match = Column(Boolean, default=True)
    date_consistency = Column(Boolean, default=True)
    qr_url_verified = Column(Boolean, default=True)
    digital_signature_valid = Column(Boolean, default=True)
    metadata_consistent = Column(Boolean, default=True)
    tampering_detected = Column(Boolean, default=False)

    verification_source = Column(String(255), default="Official Issuer Credential Registry")
    details = Column(Text, nullable=True)
    ai_explanation = Column(Text, nullable=True)  # Explainable "Why was this flagged?"

    # JSON fields
    detected_issues_json = Column(Text, nullable=True)    # List of issues
    official_record_json = Column(Text, nullable=True)    # Issuer authoritative snapshot
    evidence_diff_json = Column(Text, nullable=True)      # Side-by-side comparison
    breakdown_json = Column(Text, nullable=True)

    verified_at = Column(DateTime, default=datetime.utcnow)

    certificate = relationship("Certificate", back_populates="verification_result")


class Interview(Base):
    """Interview scheduling record."""
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    interview_type = Column(String(100), default="Technical Screen")  # Screening, Technical Round, System Design, HR, Final
    interviewer_name = Column(String(255), default="Sarah Jenkins (Principal Engineer)")
    interviewer_email = Column(String(255), default="sjenkins@verihire.ai")
    scheduled_at = Column(DateTime, nullable=False)
    # Status: SCHEDULED, PENDING, COMPLETED, CANCELLED
    status = Column(String(50), default="SCHEDULED", index=True)
    meeting_link = Column(String(500), default="https://meet.google.com/abc-veri-hire")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="interviews")


class VerificationLog(Base):
    """Enterprise audit trail logging all actions and security checks."""
    __tablename__ = "verification_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=True, index=True)
    recruiter_name = Column(String(255), default="System AI Engine")
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="audit_logs")


class Notification(Base):
    """Recruiter notification alert."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info")  # success, warning, danger, info
    is_read = Column(Boolean, default=False)
    link = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Initializes tables and seeds initial demo data if empty."""
    Base.metadata.create_all(bind=engine)
    seed_demo_data()


def get_db() -> Generator:
    """FastAPI Dependency for database session injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def log_event(event_type: str, description: str, metadata: dict = None, candidate_id: int = None, recruiter_name: str = "Recruiter Admin"):
    """Persists verification and operational events into SQLite audit log."""
    try:
        db = SessionLocal()
        entry = VerificationLog(
            event_type=event_type,
            description=description,
            candidate_id=candidate_id,
            recruiter_name=recruiter_name,
            metadata_json=json.dumps(metadata or {}, default=str)
        )
        db.add(entry)
        db.commit()
        db.close()
    except Exception:
        pass


def seed_demo_data():
    """Seeds the 4 realistic demo candidates required by the specification."""
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Candidate).count() >= 4:
            return

        # 1. Sarah Chen - Senior Cloud Architect (VERIFIED)
        c1 = Candidate(
            name="Sarah Chen",
            email="sarah.chen@cloudarch.io",
            phone="+1 (206) 555-0192",
            location="Seattle, WA",
            position="Senior Cloud Solutions Architect",
            avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
            overall_resume_score=94.0,
            skills_match_score=96.0,
            experience_match_score=92.0,
            education_match_score=95.0,
            consistency_score=98.0,
            risk_score=8.0,
            risk_level="LOW",
            risk_factors_json=json.dumps({
                "resume_inconsistencies": "None detected",
                "certificate_risk": "Low (0.02)",
                "experience_mismatch": "None",
                "education_mismatch": "None"
            }),
            verification_status="VERIFIED",
            recruiter_decision="SHORTLISTED",
            interview_status="SCHEDULED",
            recruiter_notes="Top tier cloud architecture candidate. Verified AWS Solutions Architect Pro and CNCF CKA credentials."
        )
        db.add(c1)
        db.flush()

        r1 = Resume(
            id="res-sarah-chen-001",
            candidate_id=c1.id,
            filename="Sarah_Chen_Principal_Cloud_Architect.pdf",
            file_type=".pdf",
            file_size_bytes=245800,
            raw_text="Sarah Chen - Principal Cloud Solutions Architect with 8+ years experience designing resilient multi-cloud infrastructures...",
            extracted_skills=json.dumps(["AWS", "Kubernetes", "Terraform", "Distributed Systems", "Go", "Python", "Microservices", "Docker"]),
            extracted_education=json.dumps([{"degree": "B.S. in Computer Science", "school": "University of Washington", "year": "2016"}]),
            extracted_experience=json.dumps([
                {"title": "Lead Cloud Infrastructure Engineer", "company": "Stripe", "period": "2020 - Present"},
                {"title": "Senior DevOps Engineer", "company": "Nordstrom Tech", "period": "2016 - 2020"}
            ]),
            extracted_projects=json.dumps([{"name": "Multi-Region Zero-Downtime AWS Migration", "tech": "Terraform, EKS, DynamoDB"}]),
            summary="Extensive background in scalable cloud native systems and zero-trust security postures."
        )
        db.add(r1)

        cert1_1 = Certificate(
            resume_id=r1.id,
            candidate_name="Sarah Chen",
            certificate_name="AWS Certified Solutions Architect - Professional",
            certificate_id="AWS-SAP-9941",
            issuing_organization="Amazon Web Services",
            issue_date="2024-02-10",
            expiry_date="2027-02-10",
            verification_url="https://aws.amazon.com/verification/AWS-SAP-9941"
        )
        cert1_2 = Certificate(
            resume_id=r1.id,
            candidate_name="Sarah Chen",
            certificate_name="Certified Kubernetes Administrator (CKA)",
            certificate_id="CKA-2023-884",
            issuing_organization="Cloud Native Computing Foundation",
            issue_date="2023-08-14",
            expiry_date="2026-08-14",
            verification_url="https://www.cncf.io/certification/verify/CKA-2023-884"
        )
        db.add_all([cert1_1, cert1_2])
        db.flush()

        vr1_1 = VerificationResult(
            certificate_id=cert1_1.id,
            status="VERIFIED",
            authenticity_score=98.5,
            ai_confidence=98.0,
            id_format_valid=True,
            issuing_org_verified=True,
            name_match=True,
            date_consistency=True,
            qr_url_verified=True,
            digital_signature_valid=True,
            metadata_consistent=True,
            tampering_detected=False,
            verification_source="AWS Official Certification Registry API",
            details="Cryptographic credential token matches AWS authority directory. Name, issue date, and validation hash are 100% congruent.",
            ai_explanation="Certificate information matches authoritative verification records directly with Amazon Web Services credential registry.",
            detected_issues_json=json.dumps([]),
            official_record_json=json.dumps({
                "credential_id": "AWS-SAP-9941",
                "recipient": "Sarah Chen",
                "issuer": "Amazon Web Services Training & Certification",
                "badge_status": "Active / Good Standing",
                "issued_on": "2024-02-10",
                "expires_on": "2027-02-10"
            }),
            evidence_diff_json=json.dumps({
                "field_matches": [
                    {"field": "Candidate Name", "claim": "Sarah Chen", "official": "Sarah Chen", "match": True},
                    {"field": "Certificate ID", "claim": "AWS-SAP-9941", "official": "AWS-SAP-9941", "match": True},
                    {"field": "Issuing Authority", "claim": "Amazon Web Services", "official": "Amazon Web Services", "match": True},
                    {"field": "Issue Date", "claim": "2024-02-10", "official": "2024-02-10", "match": True}
                ]
            })
        )
        vr1_2 = VerificationResult(
            certificate_id=cert1_2.id,
            status="VERIFIED",
            authenticity_score=96.0,
            ai_confidence=95.0,
            id_format_valid=True,
            issuing_org_verified=True,
            name_match=True,
            date_consistency=True,
            qr_url_verified=True,
            digital_signature_valid=True,
            metadata_consistent=True,
            tampering_detected=False,
            verification_source="Linux Foundation / CNCF Verification Network",
            details="CNCF signature verified on Linux Foundation certificate registry. No tampering indicators found.",
            ai_explanation="Authorized record retrieved from CNCF official certificate registry with valid cryptographic token.",
            detected_issues_json=json.dumps([]),
            official_record_json=json.dumps({
                "credential_id": "CKA-2023-884",
                "recipient": "Sarah Chen",
                "issuer": "Cloud Native Computing Foundation",
                "status": "Active"
            })
        )
        db.add_all([vr1_1, vr1_2])

        # Interview for Sarah
        inv1 = Interview(
            candidate_id=c1.id,
            interview_type="System Design Architecture",
            interviewer_name="Alex Rivera (Head of Infrastructure)",
            interviewer_email="arivera@company.com",
            scheduled_at=datetime.utcnow(),
            status="SCHEDULED",
            notes="Focus on multi-region failover and distributed consensus architectures."
        )
        db.add(inv1)

        # 2. Marcus Vance - Lead Data Scientist (SUSPICIOUS)
        c2 = Candidate(
            name="Marcus Vance",
            email="marcus.vance@datascience.net",
            phone="+1 (512) 555-0814",
            location="Austin, TX",
            position="Lead Data Scientist & ML Engineer",
            avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
            overall_resume_score=78.0,
            skills_match_score=85.0,
            experience_match_score=80.0,
            education_match_score=75.0,
            consistency_score=70.0,
            risk_score=58.0,
            risk_level="MEDIUM",
            risk_factors_json=json.dumps({
                "resume_inconsistencies": "Certificate ID formatting mismatch",
                "certificate_risk": "Moderate-High (0.58)",
                "experience_mismatch": "Low",
                "education_mismatch": "None"
            }),
            verification_status="SUSPICIOUS",
            recruiter_decision="VERIFICATION_REQUESTED",
            interview_status="PENDING",
            recruiter_notes="Flagged due to suspicious Stanford credential ID format. DeepLearning.AI cert passed. Hold interview until verified."
        )
        db.add(c2)
        db.flush()

        r2 = Resume(
            id="res-marcus-vance-002",
            candidate_id=c2.id,
            filename="Marcus_Vance_Resume_ML_2026.pdf",
            file_type=".pdf",
            file_size_bytes=312400,
            raw_text="Marcus Vance - Lead Machine Learning Engineer specializing in LLMs, PyTorch, Transformer fine-tuning...",
            extracted_skills=json.dumps(["PyTorch", "Python", "Transformers", "MLOps", "CUDA", "TensorFlow", "Scikit-Learn"]),
            extracted_education=json.dumps([{"degree": "M.S. in Computer Science", "school": "UT Austin", "year": "2019"}]),
            extracted_experience=json.dumps([
                {"title": "Senior Data Scientist", "company": "Applied AI Labs", "period": "2021 - Present"},
                {"title": "Machine Learning Engineer", "company": "Dell Technologies", "period": "2019 - 2021"}
            ]),
            extracted_projects=json.dumps([{"name": "Domain-Specific LLM Fine-Tuning Pipeline", "tech": "PyTorch, HuggingFace, vLLM"}]),
            summary="5 years building production recommendation engines and NLP models."
        )
        db.add(r2)

        cert2_1 = Certificate(
            resume_id=r2.id,
            candidate_name="Marcus Vance",
            certificate_name="Stanford Machine Learning Specialization",
            certificate_id="STAN-ML-8291",
            issuing_organization="Stanford Online / edX",
            issue_date="2022-04-18",
            expiry_date="Lifetime",
            verification_url="https://online.stanford.edu/verify/STAN-ML-8291"
        )
        cert2_2 = Certificate(
            resume_id=r2.id,
            candidate_name="Marcus Vance",
            certificate_name="Deep Learning Specialization",
            certificate_id="DEEP-AI-991",
            issuing_organization="DeepLearning.AI",
            issue_date="2023-01-15",
            expiry_date="Lifetime",
            verification_url="https://coursera.org/verify/specialization/DEEP-AI-991"
        )
        db.add_all([cert2_1, cert2_2])
        db.flush()

        vr2_1 = VerificationResult(
            certificate_id=cert2_1.id,
            status="SUSPICIOUS",
            authenticity_score=44.0,
            ai_confidence=87.0,
            id_format_valid=False,
            issuing_org_verified=True,
            name_match=True,
            date_consistency=False,
            qr_url_verified=False,
            digital_signature_valid=False,
            metadata_consistent=False,
            tampering_detected=True,
            verification_source="Stanford Online Registrar & edX Directory",
            details="Certificate ID prefix 'STAN-ML-' is inconsistent with official edX/Stanford format pattern (expected alphanumeric hash 32-chars). Issue date 2022 precedes curriculum revamp.",
            ai_explanation="Certificate ID could not be matched with the issuer's verification record. Potential format tampering and broken verification URL detected.",
            detected_issues_json=json.dumps([
                "Certificate ID format does not match official Stanford credential pattern",
                "Issuer verification link redirects to generic landing page, not a credential record",
                "Document PDF metadata indicates modified creator tool (PDF Editor Pro)",
                "Official registrar database returned 'Record Not Found' for ID STAN-ML-8291"
            ]),
            official_record_json=json.dumps({
                "query_id": "STAN-ML-8291",
                "issuer_queried": "Stanford Center for Professional Development",
                "result": "NO_RECORD_FOUND",
                "status_code": "ERR_NOT_FOUND"
            }),
            evidence_diff_json=json.dumps({
                "field_matches": [
                    {"field": "Certificate ID", "claim": "STAN-ML-8291", "official": "No matching record", "match": False},
                    {"field": "Issuer Format", "claim": "STAN-ML-8291", "official": "Expects: 32-char hex token", "match": False},
                    {"field": "Verification URL", "claim": "online.stanford.edu/verify/...", "official": "URL unverified (HTTP 404)", "match": False}
                ]
            })
        )
        vr2_2 = VerificationResult(
            certificate_id=cert2_2.id,
            status="VERIFIED",
            authenticity_score=92.0,
            ai_confidence=94.0,
            id_format_valid=True,
            issuing_org_verified=True,
            name_match=True,
            date_consistency=True,
            qr_url_verified=True,
            digital_signature_valid=True,
            metadata_consistent=True,
            tampering_detected=False,
            verification_source="DeepLearning.AI Official Verification Service",
            details="Authorized completion record verified on Coursera / DeepLearning.AI registry.",
            ai_explanation="Legitimate certificate found in DeepLearning.AI credential directory.",
            detected_issues_json=json.dumps([])
        )
        db.add_all([vr2_1, vr2_2])

        # 3. Elena Rostova - DevOps Engineer (NEEDS MANUAL VERIFICATION)
        c3 = Candidate(
            name="Elena Rostova",
            email="elena.rostova@berlin-tech.de",
            phone="+49 30 901820",
            location="Berlin, Germany",
            position="DevOps & Site Reliability Engineer",
            avatar="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80",
            overall_resume_score=86.0,
            skills_match_score=89.0,
            experience_match_score=85.0,
            education_match_score=88.0,
            consistency_score=91.0,
            risk_score=24.0,
            risk_level="LOW",
            risk_factors_json=json.dumps({
                "resume_inconsistencies": "None",
                "certificate_risk": "Moderate (Issuer registry automated gateway offline)",
                "experience_mismatch": "None",
                "education_mismatch": "None"
            }),
            verification_status="NEEDS MANUAL VERIFICATION",
            recruiter_decision="VERIFICATION_REQUESTED",
            interview_status="PENDING",
            recruiter_notes="Certificate from European OpenInfra gateway timed out. Mark for recruiter manual review rather than auto-reject."
        )
        db.add(c3)
        db.flush()

        r3 = Resume(
            id="res-elena-rostova-003",
            candidate_id=c3.id,
            filename="Elena_Rostova_DevOps_CV.pdf",
            file_type=".pdf",
            file_size_bytes=219000,
            raw_text="Elena Rostova - SRE and DevOps Engineer with strong Kubernetes, CI/CD, Terraform, and OpenStack background...",
            extracted_skills=json.dumps(["Terraform", "OpenStack", "Kubernetes", "GitLab CI", "Linux", "Prometheus", "Grafana", "Bash"]),
            extracted_education=json.dumps([{"degree": "Dipl.-Ing. Information Systems", "school": "Technical University of Munich", "year": "2018"}]),
            extracted_experience=json.dumps([
                {"title": "Senior SRE", "company": "FinTech Berlin AG", "period": "2021 - Present"},
                {"title": "Systems Engineer", "company": "CloudRail GmbH", "period": "2018 - 2021"}
            ]),
            extracted_projects=json.dumps([{"name": "Hybrid Cloud Zero-Trust Telemetry", "tech": "Prometheus, Grafana, OpenTelemetry"}]),
            summary="Specialist in hybrid cloud infrastructure and automated disaster recovery failover."
        )
        db.add(r3)

        cert3_1 = Certificate(
            resume_id=r3.id,
            candidate_name="Elena Rostova",
            certificate_name="OpenStack Certified Administrator (COA)",
            certificate_id="COA-DE-4401",
            issuing_organization="OpenInfra Foundation",
            issue_date="2023-05-12",
            expiry_date="2026-05-12",
            verification_url="https://openinfra.dev/verify/COA-DE-4401"
        )
        cert3_2 = Certificate(
            resume_id=r3.id,
            candidate_name="Elena Rostova",
            certificate_name="HashiCorp Certified: Terraform Associate",
            certificate_id="HASHI-TA-512",
            issuing_organization="HashiCorp",
            issue_date="2023-11-20",
            expiry_date="2025-11-20",
            verification_url="https://www.credly.com/org/hashicorp/badge/HASHI-TA-512"
        )
        db.add_all([cert3_1, cert3_2])
        db.flush()

        vr3_1 = VerificationResult(
            certificate_id=cert3_1.id,
            status="NEEDS MANUAL VERIFICATION",
            authenticity_score=72.0,
            ai_confidence=68.0,
            id_format_valid=True,
            issuing_org_verified=True,
            name_match=True,
            date_consistency=True,
            qr_url_verified=False,
            digital_signature_valid=False,
            metadata_consistent=True,
            tampering_detected=False,
            verification_source="OpenInfra Foundation Verification Gateway",
            details="Issuer external verification endpoint returned HTTP 504 Gateway Timeout. Automated AI check could neither confirm nor deny authenticity.",
            ai_explanation="The issuing authority's automated credential API is temporarily unreachable. The document contains legitimate metadata, but manual verification with the registrar is recommended.",
            detected_issues_json=json.dumps([
                "Issuing organization API connection timed out after 3 retries",
                "Requires recruiter manual document request or registrar phone/email verification"
            ]),
            official_record_json=json.dumps({
                "status": "GATEWAY_TIMEOUT",
                "message": "Remote verification endpoint unreachable. Retried 3 times."
            })
        )
        vr3_2 = VerificationResult(
            certificate_id=cert3_2.id,
            status="VERIFIED",
            authenticity_score=95.0,
            ai_confidence=97.0,
            id_format_valid=True,
            issuing_org_verified=True,
            name_match=True,
            date_consistency=True,
            qr_url_verified=True,
            digital_signature_valid=True,
            metadata_consistent=True,
            tampering_detected=False,
            verification_source="Credly / HashiCorp Official Badges",
            details="Confirmed active HashiCorp badge on Credly registry.",
            ai_explanation="Cryptographically authentic Credly credential badge."
        )
        db.add_all([vr3_1, vr3_2])

        # 4. David Kim - Full Stack Developer (HIGH RISK / INVALID)
        c4 = Candidate(
            name="David Kim",
            email="david.kim.dev@gmail.com",
            phone="+1 (212) 555-0144",
            location="New York, NY",
            position="Full Stack Web Developer",
            avatar="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80",
            overall_resume_score=62.0,
            skills_match_score=70.0,
            experience_match_score=65.0,
            education_match_score=60.0,
            consistency_score=35.0,
            risk_score=88.0,
            risk_level="HIGH",
            risk_factors_json=json.dumps({
                "resume_inconsistencies": "Significant date discrepancy & altered PDF metadata",
                "certificate_risk": "Critical (0.88) - Duplicate ID assigned to different recipient",
                "experience_mismatch": "Moderate",
                "education_mismatch": "None"
            }),
            verification_status="INVALID / FAKE",
            recruiter_decision="REJECTED",
            interview_status="CANCELLED",
            recruiter_notes="Strong forensic evidence of falsified Google Cloud certificate. ID GCP-PDE-3011 belongs to another candidate in official registry."
        )
        db.add(c4)
        db.flush()

        r4 = Resume(
            id="res-david-kim-004",
            candidate_id=c4.id,
            filename="David_Kim_Developer_Resume.pdf",
            file_type=".pdf",
            file_size_bytes=184000,
            raw_text="David Kim - Full Stack Developer with experience in React, Node.js, and Google Cloud Platform...",
            extracted_skills=json.dumps(["React", "Node.js", "Express", "MongoDB", "GCP", "JavaScript", "HTML/CSS"]),
            extracted_education=json.dumps([{"degree": "B.A. in Economics", "school": "NYU", "year": "2021"}]),
            extracted_experience=json.dumps([
                {"title": "Junior Web Developer", "company": "Agency Nine", "period": "2022 - Present"}
            ]),
            extracted_projects=json.dumps([{"name": "E-Commerce Storefront", "tech": "React, Stripe, Firebase"}]),
            summary="Web developer seeking Senior Cloud Engineer position."
        )
        db.add(r4)

        cert4_1 = Certificate(
            resume_id=r4.id,
            candidate_name="David Kim",
            certificate_name="Google Professional Data Engineer",
            certificate_id="GCP-PDE-3011",
            issuing_organization="Google Cloud",
            issue_date="2024-03-01",
            expiry_date="2026-03-01",
            verification_url="https://cloud.google.com/certification/verify/GCP-PDE-3011"
        )
        db.add(cert4_1)
        db.flush()

        vr4_1 = VerificationResult(
            certificate_id=cert4_1.id,
            status="INVALID / FAKE",
            authenticity_score=18.0,
            ai_confidence=96.0,
            id_format_valid=True,
            issuing_org_verified=True,
            name_match=False,
            date_consistency=False,
            qr_url_verified=False,
            digital_signature_valid=False,
            metadata_consistent=False,
            tampering_detected=True,
            verification_source="Google Cloud Certified Directory Registry",
            details="CRITICAL MISMATCH: Certificate ID GCP-PDE-3011 belongs to registered recipient 'David Miller' (issued 2023-09-05), not 'David Kim'. PDF creation metadata shows Photoshop text manipulation.",
            ai_explanation="Strong forensic evidence indicates the certificate is not authentic. The certificate ID belongs to another individual in the Google Cloud official directory, and document metadata shows visual tampering.",
            detected_issues_json=json.dumps([
                "Recipient name mismatch: ID registered to 'David Miller', claimed by 'David Kim'",
                "Issue date mismatch: Claimed 2024-03-01, official registry record states 2023-09-05",
                "PDF visual layer contains cloned font artifacts around candidate name field",
                "Digital signature hash invalidated"
            ]),
            official_record_json=json.dumps({
                "certificate_id": "GCP-PDE-3011",
                "legitimate_holder": "David Miller",
                "credential": "Google Professional Data Engineer",
                "issuance_date": "2023-09-05",
                "status": "VALID (Assigned to David Miller)"
            }),
            evidence_diff_json=json.dumps({
                "field_matches": [
                    {"field": "Recipient Name", "claim": "David Kim", "official": "David Miller", "match": False},
                    {"field": "Issue Date", "claim": "2024-03-01", "official": "2023-09-05", "match": False},
                    {"field": "Digital Signature", "claim": "Present in visual layout", "official": "Stripped / Invalid hash", "match": False}
                ]
            })
        )
        db.add(vr4_1)

        # Add initial notifications
        n1 = Notification(
            title="Verification Completed",
            message="Sarah Chen's AWS and CNCF certifications were verified successfully (Score: 98%).",
            type="success",
            link="/candidate/1"
        )
        n2 = Notification(
            title="Manual Verification Required",
            message="Elena Rostova's OpenStack certification requires manual recruiter review due to issuer gateway timeout.",
            type="warning",
            link="/verification-queue"
        )
        n3 = Notification(
            title="Potential Fraud Flagged",
            message="Marcus Vance: Stanford Machine Learning certificate ID format mismatch detected.",
            type="danger",
            link="/candidate/2"
        )
        n4 = Notification(
            title="Interview Scheduled",
            message="Technical Screen with Sarah Chen confirmed for this week.",
            type="info",
            link="/interviews"
        )
        db.add_all([n1, n2, n3, n4])

        # Add audit logs
        log1 = VerificationLog(
            event_type="AI_VERIFICATION_COMPLETE",
            description="Automated multi-engine verification completed for candidate Sarah Chen.",
            candidate_id=c1.id,
            recruiter_name="VeriHire AI Pipeline"
        )
        log2 = VerificationLog(
            event_type="SUSPICIOUS_CREDENTIAL_FLAG",
            description="Discrepancy detected in certificate STAN-ML-8291 for Marcus Vance.",
            candidate_id=c2.id,
            recruiter_name="VeriHire AI Pipeline"
        )
        log3 = VerificationLog(
            event_type="MANUAL_QUEUE_ENQUEUE",
            description="OpenStack credential routed to Manual Verification Queue due to remote timeout.",
            candidate_id=c3.id,
            recruiter_name="VeriHire AI Pipeline"
        )
        db.add_all([log1, log2, log3])

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error seeding demo data: {e}")
    finally:
        db.close()
