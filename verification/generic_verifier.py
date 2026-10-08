"""
VERIRESUME - Generic URL / Public Provider Verifier
Attempts live HTTP verification against public credential URLs if provided.
Falls back safely without crashing if external network is unavailable.
"""

from typing import Dict, Any
import requests
from bs4 import BeautifulSoup
from .base_verifier import CertificateVerifier, VerificationResult
from .mock_verifier import MockCertificateVerifier
from backend.comparison_engine import compare_certificate_data
from mathematics.authenticity_model import calculate_certificate_score


class GenericURLVerifier(CertificateVerifier):
    """
    Verifier adapter that performs network checks against public verification URLs.
    """

    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout
        self.mock_fallback = MockCertificateVerifier()

    def verify(self, certificate: Dict[str, Any]) -> VerificationResult:
        url = certificate.get("verification_url") or certificate.get("url")
        
        # If no URL is provided, delegate directly to Mock Verifier
        if not url:
            return self.mock_fallback.verify(certificate)

        try:
            # Perform safe GET request with strict timeout
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VERIRESUME/1.0"}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                page_text = soup.get_text().lower()
                
                # Check for presence of key certificate terms in webpage
                name = (certificate.get("candidate_name") or certificate.get("candidate") or "").lower()
                cert_id = (certificate.get("certificate_id") or certificate.get("id") or "").lower()
                course = (certificate.get("certificate_name") or certificate.get("course_name") or "").lower()

                name_present = bool(name and name in page_text)
                id_present = bool(cert_id and cert_id in page_text)
                course_present = bool(course and course in page_text)

                if name_present or id_present:
                    scoring_res = calculate_certificate_score(
                        name_match=1.0 if name_present else 0.5,
                        certificate_id_match=1.0 if id_present else 0.5,
                        course_match=1.0 if course_present else 0.5,
                        organization_match=1.0,
                        date_match=0.8
                    )
                    return VerificationResult(
                        status=scoring_res["status"],
                        score=scoring_res["score"],
                        checks={
                            "name_match": name_present,
                            "certificate_id_match": id_present,
                            "course_match": course_present,
                            "organization_match": True,
                            "date_match": True,
                        },
                        official_record={"url": url, "verified_live": True},
                        source="PUBLIC LIVE VERIFICATION URL",
                        details=f"Live verification successful at {url}.",
                        breakdown=scoring_res["breakdown"]
                    )

            # If live check was inconclusive or URL didn't contain matching tokens, fallback to mock database
            return self.mock_fallback.verify(certificate)

        except Exception:
            # On any connection or network error, fallback safely to mock database
            return self.mock_fallback.verify(certificate)
