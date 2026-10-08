"""
VERIRESUME Backend Module
"""

from .resume_parser import resume_parser, ResumeParser
from .certificate_detector import certificate_detector, CertificateDetector
from .ocr_engine import ocr_engine, OCREngine
from .comparison_engine import compare_certificate_data
from .verification_engine import default_verification_engine, verify_certificate
from .database import init_db, get_db, Candidate, Resume, Certificate, VerificationResult, VerificationLog, log_event

__all__ = [
    "resume_parser",
    "ResumeParser",
    "certificate_detector",
    "CertificateDetector",
    "ocr_engine",
    "OCREngine",
    "compare_certificate_data",
    "default_verification_engine",
    "verify_certificate",
    "init_db",
    "get_db",
    "Candidate",
    "Resume",
    "Certificate",
    "VerificationResult",
    "VerificationLog",
    "log_event",
]
