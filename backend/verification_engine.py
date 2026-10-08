"""
VERIRESUME - Verification Engine
Central coordinator that verifies certificate claims against official/mock sources,
runs SymPy mathematical scoring, and formats standardized audit reports.
"""

from typing import Dict, Any, Optional
from verification.mock_verifier import MockCertificateVerifier
from verification.generic_verifier import GenericURLVerifier
from functional.functional_processing import normalize_certificate_dict


class VerificationEngine:
    """
    Core verification engine orchestrating adapters, comparison, and scoring.
    """

    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode
        self.mock_verifier = MockCertificateVerifier()
        self.generic_verifier = GenericURLVerifier()

    def verify_single_certificate(self, certificate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifies a single certificate and returns complete audit result dictionary.
        """
        norm_cert = normalize_certificate_dict(certificate)
        
        # Decide which adapter to use
        has_url = bool(certificate.get("verification_url") or certificate.get("url"))
        
        if has_url and not self.demo_mode:
            res = self.generic_verifier.verify(norm_cert)
        else:
            res = self.mock_verifier.verify(norm_cert)

        # Merge input certificate metadata with verification output
        return {
            "certificate_name": certificate.get("certificate_name") or certificate.get("name") or certificate.get("course_name") or "Unnamed Certificate",
            "candidate_name": certificate.get("candidate_name") or certificate.get("candidate") or "Unknown Candidate",
            "certificate_id": certificate.get("certificate_id") or certificate.get("id") or "N/A",
            "issuing_organization": certificate.get("issuing_organization") or certificate.get("organization") or "N/A",
            "issue_date": certificate.get("issue_date") or certificate.get("date") or "N/A",
            "verification_url": certificate.get("verification_url") or certificate.get("url") or "",
            "status": res.status,
            "score": res.score,
            "checks": res.checks,
            "official_record": res.official_record,
            "verification_source": res.source,
            "details": res.details,
            "breakdown": res.breakdown or {}
        }


# Singleton engine instance
default_verification_engine = VerificationEngine()


def verify_certificate(certificate: Dict[str, Any]) -> Dict[str, Any]:
    """Top-level convenience function for single certificate verification."""
    return default_verification_engine.verify_single_certificate(certificate)
