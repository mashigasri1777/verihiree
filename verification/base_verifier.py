"""
VERIRESUME - Base Certificate Verifier Interface
Defines the contract and common data structures for verification adapters.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class VerificationResult:
    status: str  # "VERIFIED", "REVIEW REQUIRED", "SUSPICIOUS", "FAILED", "UNABLE_TO_VERIFY"
    score: float
    checks: Dict[str, Any]
    official_record: Optional[Dict[str, Any]]
    source: str
    details: str
    breakdown: Optional[Dict[str, float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CertificateVerifier(ABC):
    """
    Abstract Base Class for certificate verification providers.
    """

    @abstractmethod
    def verify(self, certificate: Dict[str, Any]) -> VerificationResult:
        """
        Verify a single certificate against the verification source.
        
        :param certificate: Dictionary containing:
            - candidate_name: str
            - certificate_id: str
            - certificate_name / course_name: str
            - issuing_organization: str
            - issue_date: str (optional)
            - verification_url: str (optional)
        :return: VerificationResult
        """
        raise NotImplementedError("Subclasses must implement verify()")
