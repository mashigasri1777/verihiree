"""
VERIRESUME - Pydantic Request & Response Schemas
Provides strict validation for REST API communication.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class CertificateClaim(BaseModel):
    id: Optional[int] = None
    candidate_name: Optional[str] = Field(None, description="Candidate name as extracted from resume or entered manually")
    certificate_name: str = Field(..., description="Title of the certificate or course")
    certificate_id: Optional[str] = Field(None, description="Unique certificate/credential ID")
    issuing_organization: Optional[str] = Field(None, description="Issuing authority or platform")
    issue_date: Optional[str] = Field(None, description="Date of issuance")
    verification_url: Optional[str] = Field(None, description="Official online verification link")


class CertificateVerificationResponse(BaseModel):
    certificate_name: str
    candidate_name: str
    certificate_id: str
    issuing_organization: str
    issue_date: str
    verification_url: str
    status: str
    score: float
    checks: Dict[str, Any]
    official_record: Optional[Dict[str, Any]] = None
    verification_source: str
    details: str
    breakdown: Optional[Dict[str, float]] = None
    multiprocessing_meta: Optional[Dict[str, Any]] = None


class BatchVerificationRequest(BaseModel):
    resume_id: Optional[str] = None
    certificates: List[CertificateClaim]


class BatchVerificationResponse(BaseModel):
    resume_id: Optional[str] = None
    total_certificates: int
    verified_count: int
    review_count: int
    suspicious_count: int
    failed_count: int
    average_score: float
    overall_status: str
    results: List[CertificateVerificationResponse]
    diagnostics: Dict[str, Any]


class ResumeAnalysisResponse(BaseModel):
    resume_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    education: List[str] = []
    skills: List[str] = []
    experience: List[str] = []
    certificates: List[CertificateClaim] = []
    uploaded_at: datetime


class ReportResponse(BaseModel):
    resume_id: str
    candidate_name: str
    overall_score: float
    overall_status: str
    generated_at: datetime
    summary: Dict[str, Any]
    certificates: List[CertificateVerificationResponse]
    symbolic_math_info: Dict[str, Any]
    functional_pipeline_info: Dict[str, Any]
